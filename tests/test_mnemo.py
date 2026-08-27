from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "mnemo.py"
SPEC = importlib.util.spec_from_file_location("mnemo", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MNEMO = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MNEMO
SPEC.loader.exec_module(MNEMO)


class MnemoUnitTests(unittest.TestCase):
    def test_sensitive_paths_are_blocked(self) -> None:
        blocked = [
            ".env",
            "module/.env.local",
            "credentials-prod.json",
            "data/trips.parquet",
            "infra/terraform.tfstate.backup",
            "service/private.key",
        ]
        for path in blocked:
            with self.subTest(path=path):
                self.assertTrue(MNEMO.forbidden_path(path))

    def test_examples_and_source_are_allowed(self) -> None:
        allowed = [
            ".env.example",
            "infra/example.tfvars.example",
            "scripts/load_data.py",
            "docs/credentials-policy.md",
        ]
        for path in allowed:
            with self.subTest(path=path):
                self.assertFalse(MNEMO.forbidden_path(path))

    def test_current_document_has_recovery_contract(self) -> None:
        content = MNEMO.render_current(
            session="S014",
            device="PCrda",
            role="primary-x86",
            done="La prueba pasó.",
            next_goal="Crear la tabla de staging.",
            command="uv run python scripts/load.py",
            expected="La tabla contiene diez filas.",
            notes="Sin bloqueos.",
            sync_state="checkpoint local",
        )
        self.assertIn("**Sesión:** S014", content)
        self.assertIn("uv run python scripts/load.py", content)
        self.assertIn("La tabla contiene diez filas.", content)

    def test_atomic_write_replaces_complete_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "CURRENT.md"
            MNEMO.atomic_write(path, "primero\n")
            MNEMO.atomic_write(path, "segundo\n")
            self.assertEqual(path.read_text(encoding="utf-8"), "segundo\n")


if __name__ == "__main__":
    unittest.main()
