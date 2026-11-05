"""Crea (una vez) el vault con el token de GitHub que usan los agentes para abrir PRs.

El token NUNCA va al repo ni al chat: se lee de la variable de entorno.

    export GITHUB_TOKEN_AGENTES=...   # token de grano fino: solo vigia-agentes,
                                       # permisos Contents (RW) y Pull requests (RW)
    python scripts/crear_vault.py
Imprime el ID del vault (vlt_...), que no es secreto: ponlo en el .env del vigía como
VAULT_AGENTES.
"""
import os
import sys

import anthropic

MCP_GITHUB = "https://api.githubcopilot.com/mcp/"


def main() -> int:
    token = os.environ.get("GITHUB_TOKEN_AGENTES", "").strip()
    if not token:
        print("Falta GITHUB_TOKEN_AGENTES en el entorno", file=sys.stderr)
        return 1
    c = anthropic.Anthropic()
    vault = c.beta.vaults.create(display_name="vigia-3d", metadata={"proyecto": "vigia-3d"})
    c.beta.vaults.credentials.create(
        vault_id=vault.id, display_name="GitHub (vigia-agentes)",
        auth={"type": "static_bearer", "mcp_server_url": MCP_GITHUB, "token": token})
    print(vault.id)
    return 0


if __name__ == "__main__":
    sys.exit(main())
