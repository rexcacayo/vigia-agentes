"""Empaqueta cada skill como artefacto OCI según la especificación de la comunidad
«Agent Skills as OCI Artifacts» (https://github.com/ThomasVitale/agents-skills-oci-artifacts-spec).

Genera en dist/<skill>/ el contenido (tar.gz determinista) y el config.json; la subida al
registro la hace `oras` (ver .github/workflows/publicar-oci.yml).

    python scripts/oci_empaquetar.py 1.2.0
"""
import gzip
import io
import json
import re
import sys
import tarfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
NOMBRE_OK = re.compile(r"^[a-z0-9][a-z0-9-]{0,62}[a-z0-9]$")


def frontmatter(skill_md: Path) -> dict:
    texto = skill_md.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", texto, re.S)
    if not m:
        raise SystemExit(f"{skill_md}: falta el frontmatter YAML")
    datos = {}
    for linea in m.group(1).splitlines():
        if ":" in linea and not linea.startswith(" "):
            k, v = linea.split(":", 1)
            datos[k.strip()] = v.strip()
    return datos


def tar_determinista(carpeta: Path, nombre: str) -> bytes:
    """tar.gz con mtime fijo y entradas ordenadas: el mismo contenido da el mismo digest."""
    crudo = io.BytesIO()
    with tarfile.open(fileobj=crudo, mode="w", format=tarfile.PAX_FORMAT) as tar:
        for f in sorted(p for p in carpeta.rglob("*")):
            info = tar.gettarinfo(str(f), arcname=f"{nombre}/{f.relative_to(carpeta).as_posix()}")
            info.mtime, info.uid, info.gid, info.uname, info.gname = 0, 0, 0, "", ""
            if f.is_file():
                with f.open("rb") as fh:
                    tar.addfile(info, fh)
            else:
                tar.addfile(info)
    salida = io.BytesIO()
    with gzip.GzipFile(fileobj=salida, mode="wb", mtime=0) as gz:
        gz.write(crudo.getvalue())
    return salida.getvalue()


def main(version: str) -> None:
    catalogo = []
    for carpeta in sorted((RAIZ / "skills").iterdir()):
        skill_md = carpeta / "SKILL.md"
        if not skill_md.exists():
            continue
        fm = frontmatter(skill_md)
        nombre = fm.get("name", "")
        if not NOMBRE_OK.match(nombre) or nombre != carpeta.name:
            raise SystemExit(f"{carpeta.name}: el name del SKILL.md debe coincidir con la carpeta "
                             "y ser minúsculas, dígitos y guiones")
        destino = RAIZ / "dist" / nombre
        destino.mkdir(parents=True, exist_ok=True)
        (destino / "skill-content.tar.gz").write_bytes(tar_determinista(carpeta, nombre))
        config = {"schemaVersion": "1", "name": nombre, "version": version,
                  "description": fm.get("description", "")[:1024], "license": "GPL-3.0-only",
                  "metadata": {"author": "rexcacayo", "category": "3d-printing"}}
        (destino / "config.json").write_text(json.dumps(config, ensure_ascii=False, indent=2))
        catalogo.append({"name": nombre, "version": version, "description": config["description"]})
        print(f"✅ {nombre} {version}")
    (RAIZ / "dist" / "catalogo.json").write_text(json.dumps(catalogo, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "0.0.0-dev")
