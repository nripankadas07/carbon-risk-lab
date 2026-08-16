"""Seeded correlated Monte Carlo portfolio engine."""

import math
import random
from dataclasses import replace
from statistics import NormalDist, StatisticsError, fmean, pstdev
from typing import Any, Callable, Dict, List, Optional, Tuple

from . import SCHEMA_VERSION, __version__
from .model import Portfolio, Position


NORMAL = NormalDist()


def _round(value: float) -> float:
    return round(float(value), 6)


def _finite(value: float, label: str) -> float:
    normalized = float(value)
    if not math.isfinite(normalized):
        raise ValueError("non-finite derived value: {0}".format(label))
    return normalized


def percentile(values: List[float], probability: float) -> float:
    if not values:
        raise ValueError("percentile requires values")
    if isinstance(probability, bool) or not isinstance(probability, (int, float)):
        raise ValueError("probability must be between zero and one")
    try:
        normalized_probability = float(probability)
    except OverflowError as exc:
        raise ValueError("probability must be between zero and one") from exc
    if not math.isfinite(normalized_probability) or not 0.0 <= normalized_probability <= 1.0:
        raise ValueError("probability must be between zero and one")
    ordered: List[float] = []
    for value in values:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError("percentile values must be finite numbers")
        try:
            normalized = float(value)
        except OverflowError as exc:
            raise ValueError("percentile values must be finite numbers") from exc
        if not math.isfinite(normalized):
            raise ValueError("percentile values must be finite numbers")
        ordered.append(normalized)
    ordered.sort()
    index = (len(ordered) - 1) * normalized_probability
    lower = int(math.floor(index))
    upper = int(math.ceil(index))
    if lower == upper:
        return ordered[lower]
    weight = index - lower
    lower_value = ordered[lower]
    upper_value = ordered[upper]
    if lower_value == upper_value:
        return lower_value
    if lower_value < 0.0 < upper_value:
        # Avoid overflowing ``upper - lower`` for opposite-sign finite
        # endpoints while retaining a convex interpolation.
        interpolated = lower_value * (1.0 - weight) + upper_value * weight
    else:
        interpolated = lower_value + (upper_value - lower_value) * weight
    return _finite(
        interpolated,
        "percentile interpolation",
    )


def _correlated_normal(rng: random.Random, common: float, correlation: float) -> float:
    return math.sqrt(correlation) * common + math.sqrt(1.0 - correlation) * rng.gauss(0.0, 1.0)


def _event(rng: random.Random, probability: float, common: float, correlation: float) -> bool:
    latent = _correlated_normal(rng, common, correlation)
    return NORMAL.cdf(latent) < probability


def _baseline_value(position: Position) -> float:
    return _finite(
        position.units * position.base_price * (1.0 - position.policy_haircut_mean),
        "baseline value for {0}".format(position.position_id),
    )


def _run_core(
    portfolio: Portfolio,
    simulations: int,
    seed: int,
    loss_reference_baseline: Optional[float] = None,
) -> Dict[str, Any]:
    if isinstance(simulations, bool) or not isinstance(simulations, int):
        raise ValueError("simulations must be an integer")
    if simulations < 100:
        raise ValueError("simulations must be at least 100")
    portfolio.validate()
    rng = random.Random(seed)
    baseline = _finite(
        sum(_baseline_value(position) for position in portfolio.positions),
        "portfolio baseline value",
    )
    loss_reference = (
        baseline
        if loss_reference_baseline is None
        else _finite(loss_reference_baseline, "loss reference baseline")
    )
    values: List[float] = []
    position_sums = {position.position_id: 0.0 for position in portfolio.positions}
    event_counts = {"issuance_failure": 0, "reversal": 0, "counterparty_default": 0}
    haircut_sum = 0.0
    delay_sum = 0.0
    exposure_count = simulations * len(portfolio.positions)

    for _ in range(simulations):
        market_common = rng.gauss(0.0, 1.0)
        physical_common = rng.gauss(0.0, 1.0)
        counterparty_common = rng.gauss(0.0, 1.0)
        policy_common = rng.gauss(0.0, 1.0)
        total = 0.0
        for position in portfolio.positions:
            issued = _event(
                rng,
                position.issuance_probability,
                -counterparty_common,
                position.counterparty_correlation * 0.5,
            )
            reversed_credit = _event(
                rng,
                position.reversal_probability,
                physical_common,
                position.physical_correlation,
            )
            defaulted = _event(
                rng,
                position.counterparty_default_probability,
                counterparty_common,
                position.counterparty_correlation,
            )
            event_counts["issuance_failure"] += int(not issued)
            event_counts["reversal"] += int(reversed_credit)
            event_counts["counterparty_default"] += int(defaulted)

            delay_normal = _correlated_normal(
                rng, counterparty_common, position.counterparty_correlation * 0.5
            )
            delay_adjustment = _finite(
                position.delivery_delay_volatility_months * delay_normal,
                "delivery delay shock for {0}".format(position.position_id),
            )
            delay_months = max(
                0.0,
                _finite(
                    position.delivery_delay_mean_months + delay_adjustment,
                    "delivery delay for {0}".format(position.position_id),
                ),
            )
            delay_sum = _finite(delay_sum + delay_months, "delivery delay sum")
            delivery_discount = _finite(
                (1.0 + portfolio.annual_delivery_discount_rate) ** (-delay_months / 12.0),
                "delivery discount for {0}".format(position.position_id),
            )

            policy_shock = _finite(
                0.055 * policy_common + 0.025 * rng.gauss(0.0, 1.0),
                "policy haircut shock for {0}".format(position.position_id),
            )
            if position.policy_haircut_mean == 1.0:
                policy_haircut = 1.0
            else:
                policy_haircut = min(
                    1.0,
                    max(
                        0.0,
                        _finite(
                            position.policy_haircut_mean + policy_shock,
                            "policy haircut for {0}".format(position.position_id),
                        ),
                    ),
                )
            haircut_sum += policy_haircut
            price_normal = _correlated_normal(
                rng, market_common, position.market_correlation
            )
            price_exponent = _finite(
                position.price_volatility * price_normal
                - 0.5 * position.price_volatility * position.price_volatility,
                "price exponent for {0}".format(position.position_id),
            )
            try:
                price_multiplier = _finite(
                    math.exp(price_exponent),
                    "price multiplier for {0}".format(position.position_id),
                )
            except OverflowError as exc:
                raise ValueError(
                    "non-finite derived value: price multiplier for {0}".format(
                        position.position_id
                    )
                ) from exc
            survival = 1.0 if issued and not reversed_credit and not defaulted else 0.0
            value = _finite(
                position.units
                * position.base_price
                * price_multiplier
                * (1.0 - policy_haircut)
                * delivery_discount
                * survival,
                "scenario value for {0}".format(position.position_id),
            )
            position_sums[position.position_id] = _finite(
                position_sums[position.position_id] + value,
                "position value sum for {0}".format(position.position_id),
            )
            total = _finite(total + value, "scenario portfolio value")
        values.append(total)

    losses = [
        _finite(loss_reference - value, "scenario loss against reference baseline")
        for value in values
    ]
    var95 = percentile(losses, 0.95)
    var99 = percentile(losses, 0.99)
    cvar95_tail = [loss for loss in losses if loss >= var95]
    cvar99_tail = [loss for loss in losses if loss >= var99]
    try:
        summary = {
            "expected_value": _finite(fmean(values), "expected value"),
            "value_standard_deviation": _finite(pstdev(values), "value standard deviation"),
            "value_p01": _finite(percentile(values, 0.01), "value p01"),
            "value_p05": _finite(percentile(values, 0.05), "value p05"),
            "value_p50": _finite(percentile(values, 0.50), "value p50"),
            "value_p95": _finite(percentile(values, 0.95), "value p95"),
            "value_p99": _finite(percentile(values, 0.99), "value p99"),
            "loss_var_95": _finite(var95, "loss VaR 95"),
            "loss_cvar_95": _finite(fmean(cvar95_tail), "loss CVaR 95"),
            "loss_var_99": _finite(var99, "loss VaR 99"),
            "loss_cvar_99": _finite(fmean(cvar99_tail), "loss CVaR 99"),
            "probability_of_loss": sum(loss > 0 for loss in losses) / simulations,
            "probability_below_half_baseline": sum(
                value < loss_reference * 0.5 for value in values
            )
            / simulations,
        }
    except (OverflowError, StatisticsError) as exc:
        raise ValueError("non-finite derived distribution statistic") from exc

    return {
        "baseline_value": baseline,
        "loss_reference_baseline": loss_reference,
        "values": values,
        "losses": losses,
        "summary": summary,
        "event_rates": {
            key + "_rate": count / exposure_count for key, count in event_counts.items()
        },
        "average_policy_haircut": haircut_sum / exposure_count,
        "average_delivery_delay_months": _finite(
            delay_sum / exposure_count, "average delivery delay"
        ),
        "position_expected_values": {
            key: value / simulations for key, value in position_sums.items()
        },
    }


def _stress_portfolio(portfolio: Portfolio, transform: Callable[[Position], Position]) -> Portfolio:
    return Portfolio(
        portfolio_id=portfolio.portfolio_id,
        currency=portfolio.currency,
        positions=[transform(position) for position in portfolio.positions],
        annual_delivery_discount_rate=portfolio.annual_delivery_discount_rate,
        synthetic_notice=portfolio.synthetic_notice,
    )


def run_monte_carlo(
    portfolio: Portfolio, simulations: int = 5000, seed: int = 2026, sensitivities: bool = True
) -> Dict[str, Any]:
    core = _run_core(portfolio, simulations, seed)
    sensitivity_rows: List[Dict[str, Any]] = []
    if sensitivities:
        stresses: List[Tuple[str, Callable[[Position], Position]]] = [
            (
                "reversal_probability_plus_25pct",
                lambda p: replace(p, reversal_probability=min(1.0, p.reversal_probability * 1.25)),
            ),
            (
                "counterparty_default_plus_25pct",
                lambda p: replace(
                    p,
                    counterparty_default_probability=min(
                        1.0, p.counterparty_default_probability * 1.25
                    ),
                ),
            ),
            (
                "policy_haircut_plus_5pp",
                lambda p: replace(p, policy_haircut_mean=min(1.0, p.policy_haircut_mean + 0.05)),
            ),
            (
                "price_volatility_plus_25pct",
                lambda p: replace(p, price_volatility=p.price_volatility * 1.25),
            ),
        ]
        for name, transform in stresses:
            stressed = _run_core(
                _stress_portfolio(portfolio, transform),
                simulations,
                seed,
                loss_reference_baseline=core["baseline_value"],
            )
            sensitivity_rows.append(
                {
                    "stress": name,
                    "expected_value": _round(stressed["summary"]["expected_value"]),
                    "expected_value_change": _round(
                        stressed["summary"]["expected_value"]
                        - core["summary"]["expected_value"]
                    ),
                    "expected_value_change_fraction": _round(
                        (
                            stressed["summary"]["expected_value"]
                            - core["summary"]["expected_value"]
                        )
                        / max(core["summary"]["expected_value"], 1e-9)
                    ),
                    "loss_cvar_95": _round(stressed["summary"]["loss_cvar_95"]),
                    "loss_cvar_95_change": _round(
                        stressed["summary"]["loss_cvar_95"]
                        - core["summary"]["loss_cvar_95"]
                    ),
                }
            )

    summary = {key: _round(value) for key, value in core["summary"].items()}
    result = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "carbon-risk-lab.monte-carlo-report",
        "generator": {"name": "carbon-risk-lab", "version": __version__},
        "synthetic_notice": portfolio.synthetic_notice,
        "portfolio": {
            "portfolio_id": portfolio.portfolio_id,
            "currency": portfolio.currency,
            "position_count": len(portfolio.positions),
            "positions": [position.position_id for position in portfolio.positions],
        },
        "run": {
            "seed": seed,
            "simulations": simulations,
            "correlated_scenarios": True,
            "sensitivity_loss_reference": "unstressed_baseline_value",
        },
        "metrics": {"baseline_value": _round(core["baseline_value"]), **summary},
        "event_rates": {
            **{key: _round(value) for key, value in core["event_rates"].items()},
            "average_policy_haircut": _round(core["average_policy_haircut"]),
            "average_delivery_delay_months": _round(core["average_delivery_delay_months"]),
        },
        "position_expected_values": {
            key: _round(value) for key, value in core["position_expected_values"].items()
        },
        "sensitivities": sensitivity_rows,
        "distribution_sample": [_round(value) for value in core["values"][:100]],
    }
    return result
