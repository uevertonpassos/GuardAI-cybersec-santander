"""Testes locais: nenhuma rede, nenhum servidor e nenhum dado real."""

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from security_review import changed_paths, review, scan_text, severity


def load_app(variant):
    spec = importlib.util.spec_from_file_location(variant, ROOT / "lab" / variant / "app.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SQLRegressionTests(unittest.TestCase):
    def search(self, variant, name):
        app = load_app(variant)
        db = app.create_database()
        try:
            return app.find_user(db, name)
        finally:
            db.close()

    def test_normal_input_still_works(self):
        for variant in ("vulnerable", "hardened"):
            with self.subTest(variant=variant):
                self.assertEqual(self.search(variant, "Ana Demo"), [(1, "Ana Demo")])

    def test_injection_reproduced_only_in_vulnerable(self):
        payload = "' OR '1'='1"
        self.assertEqual(len(self.search("vulnerable", payload)), 2)
        self.assertEqual(self.search("hardened", payload), [])

    def test_legitimate_apostrophe_is_data(self):
        app = load_app("hardened")
        db = app.create_database()
        try:
            db.execute("INSERT INTO users (name) VALUES (?)", ("D'Avila Demo",))
            self.assertEqual(app.find_user(db, "D'Avila Demo"), [(3, "D'Avila Demo")])
        finally:
            db.close()


class StaticReviewTests(unittest.TestCase):
    def test_three_insecure_scenarios_and_corrections(self):
        paths = [f"lab/vulnerable/{file}" for file in ("app.py", "config.json", "infra.json")]
        before = review(ROOT, paths)
        self.assertEqual({item["id"] for item in before["achados"]},
                         {"SQL001", "CFG001", "CFG002", "INF001", "INF002"})
        self.assertFalse(before["erros"])
        after = review(ROOT, [path.replace("vulnerable", "hardened") for path in paths])
        self.assertEqual(after["achados"], [])
        self.assertEqual(after["erros"], [])

    def test_unknown_context_not_assigned_severity(self):
        result = scan_text("config.json", '{"debug": true}')
        self.assertIsNone(result[0]["impacto"])
        self.assertEqual(result[0]["severidade"], "não determinada")

    def test_public_binding_with_tls_not_flagged(self):
        self.assertEqual(scan_text("config.json", '{"bind":"0.0.0.0", "tls":true}'), [])

    def test_sql_word_in_comment_not_flagged(self):
        self.assertEqual(scan_text("app.py", '# execute(f"SELECT {name}")\n'), [])

    def test_ipv6_worldwide_access_detected(self):
        self.assertEqual(scan_text("infra.json", '{"ssh_sources":["::/0"]}')[0]["id"], "INF001")

    def test_broken_json_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "config.json").write_text('{"debug":', encoding="utf-8")
            self.assertTrue(review(root, ["config.json"])["erros"])

    def test_external_path_rejected(self):
        self.assertTrue(review(ROOT, ["../outside.py"])["erros"])

    def test_only_named_fixtures_are_excluded(self):
        result = review(ROOT, ["lab/vulnerable/app.py", "lab/vulnerable/new.py"], exclude_fixtures=True)
        self.assertEqual(result["arquivos_excluidos"], ["lab/vulnerable/app.py"])
        self.assertTrue(result["erros"])

    def test_cli_expected_exit_codes(self):
        for path, expected in (("lab/vulnerable/app.py", 1), ("lab/hardened/app.py", 0), ("absent.py", 2)):
            with self.subTest(path=path):
                result = subprocess.run([sys.executable, str(ROOT / "scripts/security_review.py"), "--paths", path],
                                        capture_output=True, encoding="utf-8")
                self.assertEqual(result.returncode, expected)
                json.loads(result.stdout)


class RiskTests(unittest.TestCase):
    def test_all_matrix_cells(self):
        expected = {(1, 1): "baixa", (1, 2): "baixa", (1, 3): "média",
                    (2, 1): "baixa", (2, 2): "média", (2, 3): "alta",
                    (3, 1): "média", (3, 2): "alta", (3, 3): "crítica"}
        for notes, label in expected.items():
            self.assertEqual(severity(*notes), (notes[0] * notes[1], label))

    def test_invalid_scores_rejected(self):
        for value in (0, 4, None, "3", True, 1.5):
            with self.assertRaises(ValueError):
                severity(value, 1)


class GitReviewTests(unittest.TestCase):
    def test_review_uses_committed_head_and_reports_unsupported_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)

            def git(*args):
                return subprocess.run(["git", "-C", str(root), *args], check=True,
                                      capture_output=True, encoding="utf-8").stdout.strip()

            git("init", "-b", "main")
            git("config", "user.name", "Teste Local")
            git("config", "user.email", "test@example.invalid")
            (root / "config.json").write_text('{"debug":false}', encoding="utf-8")
            git("add", ".")
            git("commit", "-m", "base")
            base = git("rev-parse", "HEAD")
            (root / "config.json").write_text('{"debug":true}', encoding="utf-8")
            (root / "policy.md").write_text("Revisão humana necessária", encoding="utf-8")
            git("add", ".")
            git("commit", "-m", "change")
            paths, head = changed_paths(root, base, "HEAD")
            (root / "config.json").write_text('{"debug":false}', encoding="utf-8")
            result = review(root, paths, revision=head)
            self.assertEqual(result["achados"][0]["id"], "CFG001")
            self.assertEqual(result["arquivos_sem_regra"], ["policy.md"])
            self.assertEqual(result["erros"], [])


if __name__ == "__main__":
    unittest.main()
