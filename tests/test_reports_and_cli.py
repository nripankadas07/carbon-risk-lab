import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from carbon_risk_lab.engine import run_monte_carlo
from carbon_risk_lab.model import build_demo_portfolio
from carbon_risk_lab.reporting import write_reports


class ReportingTests(unittest.TestCase):
    def test_reports_share_versioned_result(self):
        result = run_monte_carlo(build_demo_portfolio(), 300, 6)
        with tempfile.TemporaryDirectory() as directory:
            paths = write_reports(result, Path(directory))
            self.assertTrue(all(path.exists() for path in paths.values()))
            self.assertEqual(json.loads(paths["json"].read_text())["schema_version"], "1.0.0")
            self.assertIn("Synthetic only", paths["html"].read_text())

    def test_cli_demo(self):
        with tempfile.TemporaryDirectory() as directory:
            env = dict(os.environ)
            env["PYTHONPATH"] = str(ROOT / "src")
            completed = subprocess.run(
                [sys.executable, "-m", "carbon_risk_lab", "demo", "--seed", "5", "--simulations", "250", "--output-dir", directory],
                cwd=str(ROOT), env=env, text=True, capture_output=True, check=False
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertTrue((Path(directory) / "carbon_risk_report.html").exists())

    def test_golden_demo_matches(self):
        result = run_monte_carlo(build_demo_portfolio(), 1000, 2026)
        with tempfile.TemporaryDirectory() as directory:
            paths = write_reports(result, Path(directory))
            golden = ROOT / "artifacts" / "demo"
            for path in paths.values():
                self.assertEqual(path.read_bytes(), (golden / path.name).read_bytes())

    def test_markdown_neutralizes_untrusted_portfolio_id(self):
        portfolio = build_demo_portfolio()
        portfolio.portfolio_id = (
            "safe`\n\n## FORGED RISK FREE ![pixel](https://attacker.invalid/p) "
            "[link](https://attacker.invalid) <https://attacker.invalid>"
        )
        result = run_monte_carlo(portfolio, 100, 1, False)
        with tempfile.TemporaryDirectory() as directory:
            markdown = write_reports(result, Path(directory))["markdown"].read_text(
                encoding="utf-8"
            )
        self.assertNotIn("\n## FORGED RISK FREE", markdown)
        self.assertIn("&#96;", markdown)
        self.assertNotIn("![pixel]", markdown)
        self.assertNotIn("](https://", markdown)
        self.assertNotIn("<https://", markdown)

    def test_cli_rejects_derived_overflow_without_traceback(self):
        artifact = build_demo_portfolio().to_artifact()
        artifact["positions"] = artifact["positions"][:1]
        artifact["positions"][0]["units"] = 1e308
        artifact["positions"][0]["base_price"] = 1e308
        with tempfile.TemporaryDirectory() as directory:
            portfolio_path = Path(directory) / "invalid.json"
            portfolio_path.write_text(json.dumps(artifact), encoding="utf-8")
            env = dict(os.environ)
            env["PYTHONPATH"] = str(ROOT / "src")
            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "carbon_risk_lab",
                    "run",
                    "--portfolio",
                    str(portfolio_path),
                    "--simulations",
                    "100",
                    "--output-dir",
                    str(Path(directory) / "out"),
                ],
                cwd=str(ROOT),
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertEqual(completed.returncode, 2)
        self.assertIn("carbon-risk-lab: error:", completed.stderr)
        self.assertNotIn("Traceback", completed.stderr)

    def test_cli_rejects_non_object_artifact_without_traceback(self):
        with tempfile.TemporaryDirectory() as directory:
            portfolio_path = Path(directory) / "invalid.json"
            portfolio_path.write_text("[]", encoding="utf-8")
            env = dict(os.environ)
            env["PYTHONPATH"] = str(ROOT / "src")
            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "carbon_risk_lab",
                    "run",
                    "--portfolio",
                    str(portfolio_path),
                    "--simulations",
                    "100",
                    "--output-dir",
                    str(Path(directory) / "out"),
                ],
                cwd=str(ROOT),
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertEqual(completed.returncode, 2)
        self.assertIn("portfolio artifact must be an object", completed.stderr)
        self.assertNotIn("Traceback", completed.stderr)


if __name__ == "__main__":
    unittest.main()
