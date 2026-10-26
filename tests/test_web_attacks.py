"""Testes de ataques web clássicos (XSS, injeção, enumeração, headers) — o que o Burp/ZAP tentariam."""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.entities import Triagem
from app.security.jwt_handler import create_access_token

XSS_PAYLOADS = [
    "<script>alert(1)</script>",
    "<img src=x onerror=alert(1)>",
    "\"><svg/onload=alert(1)>",
    "javascript:alert(1)",
]


def _auth(user: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token({'sub': user})}"}


@pytest.mark.parametrize("payload", XSS_PAYLOADS)
def test_xss_armazenado_e_devolvido_como_json_inerte(client: TestClient, payload: str) -> None:
    """Payload XSS vira dado: resposta é JSON (nunca HTML), com nosniff e CSP restritivo."""
    criado = client.post("/predict", json={"symptoms": [payload]}, headers=_auth("alice"))
    assert criado.status_code == 200
    resp = client.get(f"/triagens/{criado.json()['id']}", headers=_auth("alice"))

    assert resp.headers["content-type"].startswith("application/json")
    assert resp.headers["x-content-type-options"] == "nosniff"
    assert resp.headers["content-security-policy"] == "default-src 'none'; frame-ancestors 'none'"
    assert resp.json()["symptoms"] == [payload]


@pytest.mark.parametrize("payload", XSS_PAYLOADS)
def test_xss_refletido_em_url_e_erros_nao_vira_html(client: TestClient, payload: str) -> None:
    """Rotas inexistentes, ids inválidos e bodies inválidos respondem JSON, sem refletir HTML."""
    for resp in (
        client.get(f"/{payload}"),
        client.get(f"/triagens/{payload}", headers=_auth("alice")),
        client.post("/auth/token", json={"username": payload}),
    ):
        assert resp.headers["content-type"].startswith("application/json")
        assert resp.headers["x-content-type-options"] == "nosniff"


@pytest.mark.parametrize(
    "payload",
    ["' OR '1'='1", "'; DROP TABLE user; --", "admin'--", "\" OR \"\"=\"", "1; SELECT * FROM user"],
)
def test_sqli_no_login_nao_autentica(client: TestClient, payload: str) -> None:
    resp = client.post("/auth/token", json={"username": payload, "password": payload})
    assert resp.status_code == 401


@pytest.mark.parametrize("triagem_id", ["1 OR 1=1", "1;DROP TABLE triagem", "-1", "abc", "1.5"])
def test_id_malicioso_em_triagens_nao_vaza_dados(
    client: TestClient, session: Session, triagem_id: str
) -> None:
    session.add(
        Triagem(owner="alice", symptoms=["x"], prediction="p", confidence=0.0, recommendation="r")
    )
    session.commit()
    resp = client.get(f"/triagens/{triagem_id}", headers=_auth("bob"))
    assert resp.status_code in (404, 422)
    assert "alice" not in resp.text


def test_bola_por_enumeracao_de_ids_nunca_retorna_dados_alheios(
    client: TestClient, session: Session
) -> None:
    """Bob varre ids sequenciais: nenhum resultado pode pertencer à alice."""
    for _ in range(5):
        session.add(
            Triagem(owner="alice", symptoms=["s"], prediction="p", confidence=0.0, recommendation="r")
        )
    session.commit()
    for i in range(1, 12):
        assert client.get(f"/triagens/{i}", headers=_auth("bob")).status_code == 404


def test_mass_assignment_owner_no_predict_e_rejeitado(client: TestClient) -> None:
    """Cliente não pode definir `owner`/`id` no body (extra="forbid")."""
    resp = client.post(
        "/predict", json={"symptoms": ["febre"], "owner": "alice", "id": 1}, headers=_auth("bob")
    )
    assert resp.status_code == 422


def test_resposta_de_erro_nao_vaza_stack_trace_nem_segredo(client: TestClient) -> None:
    from app.config import SECRET_KEY

    headers = {**_auth("a"), "Content-Type": "application/json"}
    resp = client.post("/predict", content=b"{nao-e-json", headers=headers)
    assert resp.status_code == 422
    assert "Traceback" not in resp.text
    assert SECRET_KEY not in resp.text


def test_cors_preflight_de_origem_maliciosa_nao_e_liberado(client: TestClient) -> None:
    resp = client.options(
        "/predict",
        headers={"Origin": "https://evil.example", "Access-Control-Request-Method": "POST"},
    )
    assert resp.headers.get("access-control-allow-origin") != "https://evil.example"


def test_cors_origem_permitida_recebe_header(client: TestClient) -> None:
    from app.config import CORS_ORIGINS

    resp = client.get("/health", headers={"Origin": CORS_ORIGINS[0]})
    assert resp.headers["access-control-allow-origin"] == CORS_ORIGINS[0]


def test_headers_de_seguranca_em_respostas_de_erro(client: TestClient) -> None:
    """Headers também valem para 401/404/422, não só para respostas 200."""
    respostas = (
        client.get("/nao-existe"),
        client.post("/predict", json={}),
        client.post("/auth/token", json={}),
    )
    for resp in respostas:
        assert resp.headers["x-frame-options"] == "DENY"
        assert "max-age" in resp.headers["strict-transport-security"]
        assert resp.headers["cross-origin-resource-policy"] == "same-origin"


def test_nao_expoe_header_server_com_versao_de_framework(client: TestClient) -> None:
    assert "fastapi" not in client.get("/health").headers.get("x-powered-by", "").lower()


def test_rate_limit_nao_e_burlado_trocando_username(client: TestClient) -> None:
    """O limite é por IP: variar o username não reinicia o contador (brute force/spraying)."""
    for i in range(5):
        client.post("/auth/token", json={"username": f"user{i}", "password": "x"})
    assert client.post("/auth/token", json={"username": "outro", "password": "x"}).status_code == 429


def test_login_nao_enumera_usuarios_por_mensagem(client: TestClient) -> None:
    a = client.post("/auth/token", json={"username": "admin", "password": "x"})
    b = client.post("/auth/token", json={"username": "naoexiste", "password": "x"})
    assert a.status_code == b.status_code == 401
    assert a.json() == b.json()
