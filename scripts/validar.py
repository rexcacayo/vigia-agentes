"""Validación local y en CI, sin credenciales: estructura de skills y agentes.

    python scripts/validar.py
"""
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
errores = []


def fm(ruta: Path) -> str:
    m = re.match(r"^---\n(.*?)\n---\n(.+)", ruta.read_text(encoding="utf-8"), re.S)
    if not m:
        errores.append(f"{ruta}: falta frontmatter o cuerpo")
        return ""
    return m.group(1)


for skill in sorted((RAIZ / "skills").iterdir()):
    md = skill / "SKILL.md"
    if not md.exists():
        errores.append(f"{skill}: falta SKILL.md")
        continue
    cab = fm(md)
    nombre = re.search(r"^name:\s*(\S+)", cab, re.M)
    desc = re.search(r"^description:\s*(.+)", cab, re.M)
    if not nombre or nombre.group(1) != skill.name:
        errores.append(f"{md}: «name» debe ser «{skill.name}»")
    if not desc or len(desc.group(1)) > 1024:
        errores.append(f"{md}: «description» obligatoria (≤ 1024 caracteres)")

for agente in sorted((RAIZ / "agents").glob("*.md")):
    cab = fm(agente)
    for clave in ("name:", "model:"):
        if clave not in cab:
            errores.append(f"{agente}: falta «{clave}»")
    for ref in re.findall(r"^\s*-\s*(\.\./\S+)", cab, re.M):
        if not (agente.parent / ref).resolve().exists():
            errores.append(f"{agente}: la referencia {ref} no existe")

if errores:
    print("\n".join("❌ " + e for e in errores))
    sys.exit(1)
print("✅ skills y agentes válidos")
