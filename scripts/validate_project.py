"""Valida arquivos, links locais e registro das skills sem dependências externas."""

from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ("analise-vulnerabilidades", "testes-seguranca", "trilha-ciberseguranca")
REQUIRED = (
    "README.md", "AGENTS.md", "persona/guardai.md", "knowledge/metodologia.md",
    "knowledge/referencias.md", "templates/relatorio.md", "docs/harness.md",
    "docs/avaliacao-manual.md", "docs/devsecops.md", "examples/trilha-iniciante.md",
    "evidence/analise-laboratorio.md", "evidence/contexto.md", "evidence/execucao.txt",
    "evidence/vulnerable.json", "evidence/hardened.json",
    ".github/workflows/security.yml", ".github/pull_request_template.md",
    "scripts/security_review.py", "scripts/capture_evidence.py", "tests/test_security.py",
    "lab/vulnerable/app.py", "lab/hardened/app.py",
    "lab/vulnerable/config.json", "lab/hardened/config.json",
    "lab/vulnerable/infra.json", "lab/hardened/infra.json", "LICENSE",
)


def validate(root=ROOT):
    errors = []
    for name in REQUIRED:
        path = root / name
        if not path.is_file() or not path.stat().st_size:
            errors.append(f"Arquivo ausente ou vazio: {name}")
    agents_path = root / "AGENTS.md"
    agents = agents_path.read_text(encoding="utf-8") if agents_path.exists() else ""
    for name in SKILLS:
        relative = f".agents/skills/{name}/SKILL.md"
        path = root / relative
        if not path.is_file():
            errors.append(f"Skill ausente: {relative}")
            continue
        content = path.read_text(encoding="utf-8")
        match = re.match(r"\A---\nname: ([a-z0-9-]+)\ndescription: ([^\n]+)\n---\n(.+)", content, re.S)
        if not match or match[1] != name or len(match[2]) < 20 or not match[3].strip():
            errors.append(f"Frontmatter ou corpo inválido: {relative}")
        if not any(line.startswith("|") and name in line and relative in line for line in agents.splitlines()):
            errors.append(f"Skill não registrada na tabela: {name}")
    for path in root.rglob("*.md"):
        if any(part in {".git", ".venv", "node_modules", "artifacts"} for part in path.relative_to(root).parts):
            continue
        content = path.read_text(encoding="utf-8")
        for raw in re.findall(r"\[[^\]]*\]\(([^\s)]+)\)", content):
            url = urlsplit(raw)
            if url.scheme or raw.startswith("#"):
                continue
            target = (path.parent / unquote(url.path)).resolve()
            if not target.is_relative_to(root.resolve()) or not target.exists():
                errors.append(f"Link local inválido em {path.relative_to(root)}: {raw}")
            elif target.is_file() and target.stat().st_size == 0:
                errors.append(f"Destino vazio: {raw}")
        for raw in re.findall(r"`([^`\n]+)`", content if path.name == "README.md" else ""):
            if " " not in raw and "/" in raw and not raw.startswith(("http", "$")):
                target = root / raw
                if not target.exists():
                    errors.append(f"Caminho citado no README não existe: {raw}")
    return errors


if __name__ == "__main__":
    problems = validate()
    for problem in problems:
        print("ERRO:", problem)
    print(f"Integridade: {'FALHOU' if problems else 'OK'}; 3 skills, arquivos obrigatórios e links locais verificados.")
    sys.exit(bool(problems))
