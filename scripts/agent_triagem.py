"""Agente autônomo de atendimento (TP4) — HealthAssist.

Constrói um ``Agent`` com o OpenAI Agents SDK cuja única ferramenta
(``@function_tool``) chama o endpoint ``POST /classify`` da própria API (protegido por
JWT) para descobrir a intenção da mensagem do paciente. O ciclo do agente é executado
com ``Runner.run`` e a conversa tem pelo menos 3 turnos.

Backend do LLM: por padrão aponta para um **Ollama local** (API compatível com OpenAI em
``http://127.0.0.1:11434/v1``), de modo que não é preciso chave externa nem há custo.
Para usar a OpenAI de verdade, defina ``OPENAI_API_KEY`` e ``AGENT_MODEL`` (ex.: gpt-4o-mini)
e ``AGENT_OPENAI=1``.

Pré-requisitos:
  1. API HealthAssist rodando (com modelo treinado e /classify ativo).
  2. Um usuário válido para o agente autenticar (AGENT_USER / AGENT_PASSWORD).
  3. Ollama com um modelo que suporte tools (ex.: qwen2.5:7b) OU uma OPENAI_API_KEY.

Uso:
    python -m scripts.agent_triagem
"""
import asyncio
import json
import os

import httpx
from agents import (
    Agent,
    OpenAIChatCompletionsModel,
    Runner,
    function_tool,
    set_tracing_disabled,
)
from openai import AsyncOpenAI

API_URL = os.getenv("HEALTHASSIST_URL", "http://127.0.0.1:8710")
AGENT_USER = os.getenv("AGENT_USER", "alice")
AGENT_PASSWORD = os.getenv("AGENT_PASSWORD", "")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434/v1")
AGENT_MODEL = os.getenv("AGENT_MODEL", "qwen2.5:7b")
USE_OPENAI = os.getenv("AGENT_OPENAI", "0") == "1"

# Tracing do SDK exige chave da OpenAI; desligamos para rodar 100% local.
set_tracing_disabled(True)

# Token JWT obtido uma vez e reutilizado pela ferramenta.
_TOKEN: str = ""


def _login() -> str:
    """Autentica na HealthAssist API e devolve um Bearer JWT."""
    resp = httpx.post(
        f"{API_URL}/auth/token",
        json={"username": AGENT_USER, "password": AGENT_PASSWORD},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


@function_tool
def classificar_intencao(texto: str) -> str:
    """Classifica a intenção de uma mensagem de paciente usando o modelo da HealthAssist API.

    Args:
        texto: a mensagem do paciente, em português.

    Returns:
        JSON com a intenção prevista (``intent``), a probabilidade e a versão do modelo.
    """
    resp = httpx.post(
        f"{API_URL}/classify",
        headers={"Authorization": f"Bearer {_TOKEN}"},
        json={"text": texto},
        timeout=30,
    )
    if resp.status_code != 200:
        return json.dumps({"erro": f"status {resp.status_code}", "corpo": resp.text[:200]})
    return json.dumps(resp.json(), ensure_ascii=False)


INSTRUCTIONS = (
    "Você é o assistente de triagem da HealthAssist, um serviço de atendimento a pacientes. "
    "Para cada mensagem do paciente, use SEMPRE a ferramenta `classificar_intencao` para "
    "descobrir a intenção (ex.: Tratamento, Diagnóstico, Escolha de profissionais de saúde, "
    "Epidemiologia, Estilo de vida saudável, Anatomia e fisiologia, Outros). "
    "Depois, responda em português de forma acolhedora e objetiva, citando a intenção "
    "detectada e orientando o próximo passo da triagem. Você NÃO dá diagnóstico médico nem "
    "prescreve tratamento: apenas direciona. Se a probabilidade for baixa, diga que vai "
    "confirmar com um atendente humano."
)


def _build_agent() -> Agent:
    """Monta o Agent com o backend de LLM (Ollama local por padrão)."""
    if USE_OPENAI:
        # Usa a OpenAI padrão (requer OPENAI_API_KEY no ambiente).
        return Agent(name="Triagem HealthAssist", instructions=INSTRUCTIONS,
                     model=os.getenv("AGENT_MODEL", "gpt-4o-mini"),
                     tools=[classificar_intencao])
    client = AsyncOpenAI(base_url=OLLAMA_URL, api_key="ollama")
    model = OpenAIChatCompletionsModel(model=AGENT_MODEL, openai_client=client)
    return Agent(name="Triagem HealthAssist", instructions=INSTRUCTIONS,
                 model=model, tools=[classificar_intencao])


async def main() -> None:
    """Executa uma conversa de 3 turnos com o agente, mantendo o histórico entre turnos."""
    global _TOKEN
    _TOKEN = _login()
    agent = _build_agent()

    turnos = [
        "Oi, fiz uma cirurgia no joelho mês passado. Qual fisioterapia ajuda na recuperação?",
        "E qual especialista eu procuro para acompanhar essa recuperação?",
        "Entendi. Isso que eu tenho é contagioso para outras pessoas?",
    ]

    historico: list = []
    for i, fala in enumerate(turnos, start=1):
        entrada = historico + [{"role": "user", "content": fala}]
        resultado = await Runner.run(agent, entrada)
        print(f"\n===== TURNO {i} =====")
        print(f"[Paciente] {fala}")
        print(f"[Agente]   {resultado.final_output}")
        historico = resultado.to_input_list()

    print("\nConversa concluída (3 turnos).")


if __name__ == "__main__":
    asyncio.run(main())
