"""Registra saídas reais dos testes e exemplos. Não fabrica transcrições de chat."""

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT / "evidence"


def main():
    DESTINATION.mkdir(exist_ok=True)
    log = DESTINATION / "execucao.txt"
    log.write_text(f"GuardAI — evidência de execução real\nUTC: {datetime.now(timezone.utc).isoformat()}\n"
                   f"Python: {platform.python_version()}\nSistema: {platform.system()}\n", encoding="utf-8")
    failed = False
    environment = dict(os.environ, PYTHONIOENCODING="utf-8")
    commands = [
        (["lab/vulnerable/app.py"], 0, None),
        (["lab/hardened/app.py"], 0, None),
        (["-m", "unittest", "discover", "-s", "tests", "-v"], 0, None),
        (["scripts/security_review.py", "--paths", "lab/vulnerable/app.py", "lab/vulnerable/config.json", "lab/vulnerable/infra.json"], 1, "vulnerable.json"),
        (["scripts/security_review.py", "--paths", "lab/hardened/app.py", "lab/hardened/config.json", "lab/hardened/infra.json"], 0, "hardened.json"),
        (["scripts/security_review.py", "--tracked"], 0, None),
        (["scripts/validate_project.py"], 0, None),
    ]
    inputs = sorted([*ROOT.glob("lab/**/*.py"), *ROOT.glob("lab/**/*.json"),
                     *ROOT.glob("scripts/*.py"), *ROOT.glob("tests/*.py"),
                     *ROOT.glob(".agents/skills/*/SKILL.md")])
    hashes = {str(path.relative_to(ROOT).as_posix()): hashlib.sha256(path.read_bytes()).hexdigest() for path in inputs}
    (DESTINATION / "sha256.json").write_text(json.dumps(hashes, indent=2) + "\n", encoding="utf-8")
    for args, expected, output in commands:
        process = subprocess.run([sys.executable, *args], cwd=ROOT, env=environment,
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf-8")
        if output:
            json.loads(process.stdout)
            (DESTINATION / output).write_text(process.stdout, encoding="utf-8")
        with log.open("a", encoding="utf-8") as stream:
            stream.write(f"\n$ python {' '.join(args)}\n{process.stdout}\n"
                         f"Saída: {process.returncode}; esperada: {expected}\n")
        failed |= process.returncode != expected
        print(f"{'OK' if process.returncode == expected else 'FALHOU'}: python {' '.join(args)}")
    return int(failed)


if __name__ == "__main__":
    sys.exit(main())
