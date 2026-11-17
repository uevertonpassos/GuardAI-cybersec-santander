"""Verificações didáticas estáticas; não executa os arquivos analisados."""

import argparse
import ast
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
LAB_FIXTURES = frozenset({
    "lab/vulnerable/app.py",
    "lab/vulnerable/config.json",
    "lab/vulnerable/infra.json",
})


def severity(impact, likelihood):
    if type(impact) is not int or type(likelihood) is not int:
        raise ValueError("As notas devem ser inteiros de 1 a 3")
    if impact not in (1, 2, 3) or likelihood not in (1, 2, 3):
        raise ValueError("As notas devem ser inteiros de 1 a 3")
    score = impact * likelihood
    return score, "baixa" if score <= 2 else "média" if score <= 4 else "alta" if score == 6 else "crítica"


def finding(rule, path, location, evidence, correction):
    return {
        "id": rule,
        "arquivo": path,
        "localizacao": location,
        "evidencia": evidence,
        "impacto": None,
        "probabilidade": None,
        "pontuacao": None,
        "severidade": "não determinada",
        "confianca": "média — padrão estático, sem análise de fluxo completa",
        "cenario_de_risco": "Validar uso, exposição, dados e controles antes de classificar.",
        "correcao": correction,
        "validacao": "Detecção estática; confirmar com revisão e teste autorizado.",
    }


def scan_text(path, content):
    findings = []
    if path.endswith(".py"):
        tree = ast.parse(content, filename=path)
        for node in ast.walk(tree):
            if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                    and node.func.attr in {"execute", "executemany", "executescript"} and node.args):
                continue
            query = node.args[0]
            interpolated = isinstance(query, ast.JoinedStr) or (
                isinstance(query, ast.BinOp) and isinstance(query.op, (ast.Add, ast.Mod))
            ) or (isinstance(query, ast.Call) and isinstance(query.func, ast.Attribute)
                  and query.func.attr == "format")
            if interpolated:
                findings.append(finding(
                    "SQL001", path, f"linha {node.lineno}",
                    "Construção dinâmica diretamente no argumento de execute; confirmar origem da entrada.",
                    "Separar SQL e valores com parâmetros do driver.",
                ))
    elif path.endswith(".json"):
        data = json.loads(content)
        if not isinstance(data, dict):
            return findings
        rules = [
            (data.get("debug") is True, "CFG001", "debug", "Debug habilitado.", "Desabilitar debug fora do desenvolvimento."),
            (data.get("bind") in ("0.0.0.0", "::") and data.get("tls") is False,
             "CFG002", "bind, tls", "Escuta pública com TLS declarado desabilitado.", "Restringir a escuta e confirmar TLS no serviço ou proxy."),
            (isinstance(data.get("ssh_sources"), list) and any(
                source in ("0.0.0.0/0", "::/0") for source in data["ssh_sources"]),
             "INF001", "ssh_sources", "Origem SSH irrestrita em IPv4 ou IPv6.", "Restringir origem a rede administrativa autorizada."),
            (data.get("storage_encrypted") is False, "INF002", "storage_encrypted",
             "Criptografia de armazenamento declarada desabilitada.", "Habilitar criptografia e definir gestão de chaves."),
        ]
        for condition, rule, location, evidence, correction in rules:
            if condition:
                findings.append(finding(rule, path, location, evidence, correction))
    return sorted(findings, key=lambda item: (item["arquivo"], item["id"], item["localizacao"]))


def git(root, *args):
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True, check=True)
    return result.stdout.decode("utf-8")


def resolve_revision(root, revision):
    return git(root, "rev-parse", "--verify", "--end-of-options", revision + "^{commit}").strip()


def changed_paths(root, base, head):
    base_sha = resolve_revision(root, base)
    head_sha = resolve_revision(root, head)
    ancestor = git(root, "merge-base", base_sha, head_sha).strip()
    names = git(root, "diff", "--name-only", "--diff-filter=ACMR", "-z", ancestor, head_sha)
    return [name for name in names.split("\0") if name], head_sha


def review(root, paths, exclude_fixtures=False, revision=None):
    root = root.resolve()
    report = {"formato": "guardai-estatico-v1", "revisao": revision,
              "arquivos_analisados": [], "arquivos_excluidos": [],
              "arquivos_sem_regra": [], "achados": [], "erros": []}
    for name in sorted(set(paths)):
        path = Path(name)
        if path.is_absolute() or ".." in path.parts:
            report["erros"].append(f"Caminho fora do escopo: {name}")
            continue
        name = path.as_posix()
        if exclude_fixtures and name in LAB_FIXTURES:
            report["arquivos_excluidos"].append(name)
            continue
        if path.suffix not in (".py", ".json"):
            report["arquivos_sem_regra"].append(name)
            continue
        try:
            if revision:
                mode = git(root, "ls-tree", revision, "--", name).split(" ", 1)[0]
                if mode not in ("100644", "100755"):
                    raise ValueError("A revisão aceita somente arquivos regulares")
                content = git(root, "show", f"{revision}:{name}")
            else:
                target = (root / path).resolve()
                if not target.is_relative_to(root) or (root / path).is_symlink():
                    raise ValueError("Link ou caminho fora do escopo")
                content = target.read_text(encoding="utf-8")
            report["achados"].extend(scan_text(name, content))
            report["arquivos_analisados"].append(name)
        except (OSError, ValueError, SyntaxError, subprocess.CalledProcessError) as exc:
            report["erros"].append(f"{name}: {type(exc).__name__}; revisão incompleta")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--paths", nargs="+", help="Arquivos locais, incluindo fixtures se explícitas")
    mode.add_argument("--tracked", action="store_true", help="Arquivos Git do working tree, exceto as três fixtures")
    mode.add_argument("--base", help="Revisar arquivos alterados desde o ancestral comum com a base")
    parser.add_argument("--head", default="HEAD", help="Revisão final, usada com --base")
    args = parser.parse_args()
    try:
        revision = None
        if args.base:
            paths, revision = changed_paths(ROOT, args.base, args.head)
        elif args.tracked:
            paths = [p for p in git(ROOT, "ls-files", "-z").split("\0") if p]
            if not paths:
                raise ValueError("Nenhum arquivo no índice; prepare o repositório antes de usar --tracked")
        else:
            paths = args.paths
        report = review(ROOT, paths, not bool(args.paths), revision)
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        print(json.dumps({"erros": [str(exc)]}, ensure_ascii=False, indent=2))
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 2 if report["erros"] else 1 if report["achados"] else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
