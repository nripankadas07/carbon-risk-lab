"""Versioned portfolio data models."""

import math
from dataclasses import asdict, dataclass
from typing import Any, Dict, List

from . import SCHEMA_VERSION


SYNTHETIC_NOTICE = (
    "This portfolio and every simulated issuance, reversal, price, delivery, "
    "counterparty, and policy outcome are synthetic demonstration data. They "
    "are not current market facts, forecasts, valuations, or investment advice."
)


def _require_exact_fields(value: Dict[str, Any], expected: set, label: str) -> None:
    actual = set(value)
    if actual == expected:
        return
    missing = sorted(expected - actual)
    unknown = sorted(actual - expected)
    details = []
    if missing:
        details.append("missing: {0}".format(", ".join(missing)))
    if unknown:
        details.append("unknown: {0}".format(", ".join(unknown)))
    raise ValueError("{0} fields do not match schema ({1})".format(label, "; ".join(details)))


def _nonempty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("{0} must be a non-empty string".format(label))
    return value


def _number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("{0} must be a JSON number".format(label))
    try:
        normalized = float(value)
    except OverflowError as exc:
        raise ValueError("{0} must be finite".format(label)) from exc
    if not math.isfinite(normalized):
        raise ValueError("{0} must be finite".format(label))
    return normalized


@dataclass(frozen=True)
class Position:
    position_id: str
    project_type: str
    synthetic_geography: str
    units: float
    base_price: float
    issuance_probability: float
    reversal_probability: float
    counterparty_default_probability: float
    delivery_delay_mean_months: float
    delivery_delay_volatility_months: float
    policy_haircut_mean: float
    price_volatility: float
    market_correlation: float = 0.55
    physical_correlation: float = 0.45
    counterparty_correlation: float = 0.35

    def validate(self) -> None:
        _nonempty_string(self.position_id, "position_id")
        _nonempty_string(self.project_type, "project_type")
        _nonempty_string(self.synthetic_geography, "synthetic_geography")
        for name in (
            "units",
            "base_price",
            "issuance_probability",
            "reversal_probability",
            "counterparty_default_probability",
            "delivery_delay_mean_months",
            "delivery_delay_volatility_months",
            "policy_haircut_mean",
            "price_volatility",
            "market_correlation",
            "physical_correlation",
            "counterparty_correlation",
        ):
            _number(getattr(self, name), name)
        if self.units < 0 or self.base_price < 0:
            raise ValueError("units and base_price must be non-negative")
        for name in (
            "issuance_probability",
            "reversal_probability",
            "counterparty_default_probability",
            "policy_haircut_mean",
            "market_correlation",
            "physical_correlation",
            "counterparty_correlation",
        ):
            value = getattr(self, name)
            if not 0.0 <= value <= 1.0:
                raise ValueError("{0} must be between zero and one".format(name))
        if self.delivery_delay_mean_months < 0 or self.delivery_delay_volatility_months < 0:
            raise ValueError("delivery delay parameters must be non-negative")
        if self.price_volatility < 0:
            raise ValueError("price_volatility must be non-negative")
        notional = self.units * self.base_price
        if not math.isfinite(notional):
            raise ValueError("units multiplied by base_price must be finite")
        volatility_variance = self.price_volatility * self.price_volatility
        if not math.isfinite(volatility_variance):
            raise ValueError("price_volatility squared must be finite")

    @classmethod
    def from_dict(cls, value: Dict[str, Any]) -> "Position":
        if not isinstance(value, dict):
            raise ValueError("portfolio positions must contain objects")
        fields = {item.name for item in cls.__dataclass_fields__.values()}
        _require_exact_fields(value, fields, "position")
        position = cls(
            position_id=_nonempty_string(value["position_id"], "position_id"),
            project_type=_nonempty_string(value["project_type"], "project_type"),
            synthetic_geography=_nonempty_string(
                value["synthetic_geography"], "synthetic_geography"
            ),
            units=_number(value["units"], "units"),
            base_price=_number(value["base_price"], "base_price"),
            issuance_probability=_number(
                value["issuance_probability"], "issuance_probability"
            ),
            reversal_probability=_number(
                value["reversal_probability"], "reversal_probability"
            ),
            counterparty_default_probability=_number(
                value["counterparty_default_probability"],
                "counterparty_default_probability",
            ),
            delivery_delay_mean_months=_number(
                value["delivery_delay_mean_months"], "delivery_delay_mean_months"
            ),
            delivery_delay_volatility_months=_number(
                value["delivery_delay_volatility_months"],
                "delivery_delay_volatility_months",
            ),
            policy_haircut_mean=_number(
                value["policy_haircut_mean"], "policy_haircut_mean"
            ),
            price_volatility=_number(value["price_volatility"], "price_volatility"),
            market_correlation=_number(value["market_correlation"], "market_correlation"),
            physical_correlation=_number(
                value["physical_correlation"], "physical_correlation"
            ),
            counterparty_correlation=_number(
                value["counterparty_correlation"], "counterparty_correlation"
            ),
        )
        position.validate()
        return position


@dataclass
class Portfolio:
    portfolio_id: str
    currency: str
    positions: List[Position]
    annual_delivery_discount_rate: float = 0.08
    synthetic_notice: str = SYNTHETIC_NOTICE

    def validate(self) -> None:
        _nonempty_string(self.portfolio_id, "portfolio_id")
        _nonempty_string(self.currency, "currency")
        _nonempty_string(self.synthetic_notice, "synthetic_notice")
        if not isinstance(self.positions, list) or not self.positions:
            raise ValueError("portfolio must contain at least one position")
        _number(self.annual_delivery_discount_rate, "annual_delivery_discount_rate")
        if self.annual_delivery_discount_rate < 0:
            raise ValueError("annual_delivery_discount_rate must be non-negative")
        if any(not isinstance(item, Position) for item in self.positions):
            raise ValueError("portfolio positions must contain Position values")
        identifiers = [item.position_id for item in self.positions]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("position_id values must be unique")
        for position in self.positions:
            position.validate()

    def to_artifact(self) -> Dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "artifact_type": "carbon-risk-lab.portfolio",
            "portfolio_id": self.portfolio_id,
            "currency": self.currency,
            "annual_delivery_discount_rate": self.annual_delivery_discount_rate,
            "synthetic_notice": self.synthetic_notice,
            "positions": [asdict(item) for item in self.positions],
        }

    @classmethod
    def from_artifact(cls, value: Dict[str, Any]) -> "Portfolio":
        if not isinstance(value, dict):
            raise ValueError("portfolio artifact must be an object")
        _require_exact_fields(
            value,
            {
                "schema_version",
                "artifact_type",
                "portfolio_id",
                "currency",
                "annual_delivery_discount_rate",
                "synthetic_notice",
                "positions",
            },
            "portfolio artifact",
        )
        if value.get("schema_version") != SCHEMA_VERSION:
            raise ValueError("unsupported portfolio schema_version")
        if value.get("artifact_type") != "carbon-risk-lab.portfolio":
            raise ValueError("unexpected artifact_type")
        positions = value["positions"]
        if not isinstance(positions, list):
            raise ValueError("positions must be an array")
        portfolio = cls(
            portfolio_id=_nonempty_string(value["portfolio_id"], "portfolio_id"),
            currency=_nonempty_string(value["currency"], "currency"),
            annual_delivery_discount_rate=_number(
                value["annual_delivery_discount_rate"],
                "annual_delivery_discount_rate",
            ),
            synthetic_notice=_nonempty_string(
                value["synthetic_notice"], "synthetic_notice"
            ),
            positions=[Position.from_dict(item) for item in positions],
        )
        portfolio.validate()
        return portfolio


def build_demo_portfolio() -> Portfolio:
    portfolio = Portfolio(
        portfolio_id="synthetic-diversified-carbon-book",
        currency="SYN-USD",
        positions=[
            Position("SYN-FOR-01", "afforestation", "Synthetic Highland North", 18000, 18.0, 0.91, 0.09, 0.035, 4.0, 2.0, 0.08, 0.24, 0.60, 0.66, 0.30),
            Position("SYN-MET-02", "methane capture", "Synthetic Basin East", 13000, 23.0, 0.95, 0.025, 0.055, 2.0, 1.2, 0.06, 0.20, 0.52, 0.28, 0.48),
            Position("SYN-SOL-03", "distributed solar", "Synthetic Coast South", 22000, 14.5, 0.88, 0.015, 0.025, 6.0, 3.5, 0.11, 0.31, 0.72, 0.20, 0.22),
            Position("SYN-SOI-04", "soil carbon", "Synthetic Plains West", 15500, 20.5, 0.84, 0.12, 0.065, 8.0, 4.0, 0.14, 0.27, 0.48, 0.58, 0.42),
        ],
    )
    portfolio.validate()
    return portfolio
