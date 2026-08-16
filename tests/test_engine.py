import json
import copy
import sys
import unittest
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from carbon_risk_lab.engine import percentile, run_monte_carlo
from carbon_risk_lab.model import Portfolio, Position, build_demo_portfolio


class EngineTests(unittest.TestCase):
    def test_percentile_interpolates(self):
        self.assertEqual(percentile([0.0, 10.0], 0.5), 5.0)

    def test_seeded_run_is_deterministic(self):
        portfolio = build_demo_portfolio()
        first = run_monte_carlo(portfolio, 600, 77)
        second = run_monte_carlo(portfolio, 600, 77)
        self.assertEqual(first, second)

    def test_tail_metrics_are_ordered(self):
        metrics = run_monte_carlo(build_demo_portfolio(), 800, 12)["metrics"]
        self.assertGreaterEqual(metrics["loss_cvar_95"], metrics["loss_var_95"])
        self.assertGreaterEqual(metrics["loss_cvar_99"], metrics["loss_var_99"])
        self.assertLessEqual(metrics["value_p05"], metrics["value_p50"])
        self.assertLessEqual(metrics["value_p50"], metrics["value_p95"])

    def test_reversal_stress_reduces_expected_value(self):
        result = run_monte_carlo(build_demo_portfolio(), 800, 31)
        row = next(item for item in result["sensitivities"] if item["stress"].startswith("reversal"))
        self.assertLess(row["expected_value_change"], 0.0)

    def test_adverse_haircut_tail_loss_uses_original_baseline(self):
        result = run_monte_carlo(build_demo_portfolio(), 800, 31)
        row = next(
            item
            for item in result["sensitivities"]
            if item["stress"] == "policy_haircut_plus_5pp"
        )
        self.assertEqual(
            result["run"]["sensitivity_loss_reference"],
            "unstressed_baseline_value",
        )
        self.assertGreaterEqual(row["loss_cvar_95_change"], 0.0)

    def test_portfolio_round_trip(self):
        original = build_demo_portfolio()
        restored = Portfolio.from_artifact(json.loads(json.dumps(original.to_artifact())))
        self.assertEqual(original.to_artifact(), restored.to_artifact())

    def test_non_finite_assumptions_are_rejected(self):
        original = build_demo_portfolio()
        artifact = original.to_artifact()
        artifact["positions"][0]["price_volatility"] = float("nan")
        with self.assertRaises(ValueError):
            Portfolio.from_artifact(artifact)

    def test_full_policy_haircut_remains_zero_value(self):
        portfolio = Portfolio(
            "full-haircut",
            "SYN",
            [
                Position(
                    "p",
                    "synthetic",
                    "synthetic",
                    100.0,
                    10.0,
                    1.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                )
            ],
        )
        result = run_monte_carlo(portfolio, 300, 7)
        self.assertEqual(result["metrics"]["baseline_value"], 0.0)
        self.assertEqual(result["metrics"]["expected_value"], 0.0)
        self.assertEqual(result["event_rates"]["average_policy_haircut"], 1.0)
        stress = next(
            item
            for item in result["sensitivities"]
            if item["stress"] == "policy_haircut_plus_5pp"
        )
        self.assertEqual(stress["expected_value"], 0.0)
        self.assertEqual(stress["expected_value_change"], 0.0)

    def test_haircut_stress_is_monotone_near_full_boundary(self):
        portfolio = Portfolio(
            "near-full-haircut",
            "SYN",
            [
                Position(
                    "p",
                    "synthetic",
                    "synthetic",
                    100.0,
                    10.0,
                    1.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.98,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                )
            ],
        )
        result = run_monte_carlo(portfolio, 500, 19)
        stress = next(
            item
            for item in result["sensitivities"]
            if item["stress"] == "policy_haircut_plus_5pp"
        )
        self.assertLessEqual(stress["expected_value_change"], 0.0)

    def test_derived_notional_overflow_is_rejected_before_simulation(self):
        artifact = build_demo_portfolio().to_artifact()
        artifact["positions"] = artifact["positions"][:1]
        artifact["positions"][0]["units"] = 1e308
        artifact["positions"][0]["base_price"] = 1e308
        with self.assertRaisesRegex(ValueError, "units multiplied by base_price"):
            Portfolio.from_artifact(artifact)

    def test_price_variance_overflow_is_rejected(self):
        artifact = build_demo_portfolio().to_artifact()
        artifact["positions"][0]["price_volatility"] = 1e308
        with self.assertRaisesRegex(ValueError, "price_volatility squared"):
            Portfolio.from_artifact(artifact)

    def test_artifact_schema_is_exact_and_types_are_not_coerced(self):
        base = build_demo_portfolio().to_artifact()
        mutations = []

        artifact = copy.deepcopy(base)
        artifact["unexpected_root"] = True
        mutations.append((artifact, "portfolio artifact fields"))

        artifact = copy.deepcopy(base)
        artifact.pop("currency")
        mutations.append((artifact, "portfolio artifact fields"))

        artifact = copy.deepcopy(base)
        artifact["positions"][0]["unexpected_position"] = 1
        mutations.append((artifact, "position fields"))

        artifact = copy.deepcopy(base)
        artifact["positions"][0].pop("market_correlation")
        mutations.append((artifact, "position fields"))

        artifact = copy.deepcopy(base)
        artifact["portfolio_id"] = {}
        mutations.append((artifact, "portfolio_id must be a non-empty string"))

        artifact = copy.deepcopy(base)
        artifact["currency"] = []
        mutations.append((artifact, "currency must be a non-empty string"))

        artifact = copy.deepcopy(base)
        artifact["synthetic_notice"] = "  "
        mutations.append((artifact, "synthetic_notice must be a non-empty string"))

        artifact = copy.deepcopy(base)
        artifact["annual_delivery_discount_rate"] = True
        mutations.append((artifact, "must be a JSON number"))

        artifact = copy.deepcopy(base)
        artifact["positions"][0]["units"] = "18000"
        mutations.append((artifact, "units must be a JSON number"))

        artifact = copy.deepcopy(base)
        artifact["positions"][0]["issuance_probability"] = True
        mutations.append((artifact, "issuance_probability must be a JSON number"))

        artifact = copy.deepcopy(base)
        artifact["positions"][0]["position_id"] = ""
        mutations.append((artifact, "position_id must be a non-empty string"))

        artifact = copy.deepcopy(base)
        artifact["positions"][0]["project_type"] = []
        mutations.append((artifact, "project_type must be a non-empty string"))

        artifact = copy.deepcopy(base)
        artifact["positions"][0]["synthetic_geography"] = None
        mutations.append((artifact, "synthetic_geography must be a non-empty string"))

        for artifact, message in mutations:
            with self.subTest(message=message):
                with self.assertRaisesRegex(ValueError, message):
                    Portfolio.from_artifact(artifact)

    def test_artifact_root_and_positions_have_controlled_shape_errors(self):
        with self.assertRaisesRegex(ValueError, "portfolio artifact must be an object"):
            Portfolio.from_artifact([])
        artifact = build_demo_portfolio().to_artifact()
        artifact["positions"] = "not-an-array"
        with self.assertRaisesRegex(ValueError, "positions must be an array"):
            Portfolio.from_artifact(artifact)


if __name__ == "__main__":
    unittest.main()
