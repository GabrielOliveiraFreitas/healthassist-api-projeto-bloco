"""Cria o banco e usuários de teste (admin, alice, bob) para uso/pentest.

Uso: as senhas vêm do ambiente (SEED_ADMIN_PASSWORD, SEED_ALICE_PASSWORD,
SEED_BOB_PASSWORD) ou do `.env`; nada é hardcoded no repositório.
    python -m scripts.seed
"""
import os
import sys

from sqlmodel import Session, select

from app.db import engine, init_db
from app.models.entities import Triagem, User
from app.security.passwords import hash_password

SEED_USERS = ("admin", "alice", "bob")


def main() -> int:
    """Insere usuários (idempotente) e uma triagem de exemplo para alice e bob."""
    senhas = {u: os.getenv(f"SEED_{u.upper()}_PASSWORD", "") for u in SEED_USERS}
    faltando = [f"SEED_{u.upper()}_PASSWORD" for u, p in senhas.items() if len(p) < 8]
    if faltando:
        print(f"Defina (mín. 8 caracteres): {', '.join(faltando)}", file=sys.stderr)
        return 1

    init_db()
    with Session(engine) as session:
        for username, senha in senhas.items():
            if session.exec(select(User).where(User.username == username)).first() is None:
                session.add(User(username=username, password_hash=hash_password(senha)))
        session.commit()
        for owner, sintomas in (("alice", ["febre", "tosse"]), ("bob", ["dor de cabeça"])):
            if session.exec(select(Triagem).where(Triagem.owner == owner)).first() is None:
                session.add(
                    Triagem(
                        owner=owner,
                        symptoms=sintomas,
                        prediction="placeholder",
                        confidence=0.0,
                        recommendation="Aguarde integração com modelo de EDA",
                    )
                )
        session.commit()
    print("Seed concluído: usuários admin, alice e bob; 1 triagem para alice e 1 para bob.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
