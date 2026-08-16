"""Command-line interface for Carbon Risk Lab."""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

from .engine import run_monte_carlo
from .model import Portfolio, build_demo_portfolio
from .reporting import write_reports


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="carbon-risk-lab", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    demo = sub.add_parser("demo", help="run the seeded synthetic portfolio")
    demo.add_argument("--seed", type=int, default=2026)
    demo.add_argument("--simulations", type=int, default=5000)
    demo.add_argument("--output-dir", type=Path, default=Path("reports"))
    run = sub.add_parser("run", help="run a versioned portfolio JSON file")
    run.add_argument("--portfolio", type=Path, required=True)
    run.add_argument("--seed", type=int, default=2026)
    run.add_argument("--simulations", type=int, default=5000)
    run.add_argument("--output-dir", type=Path, default=Path("reports"))
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "demo":
            portfolio = build_demo_portfolio()
        else:
            portfolio = Portfolio.from_artifact(json.loads(args.portfolio.read_text(encoding="utf-8")))
        result = run_monte_carlo(portfolio, args.simulations, args.seed)
        paths = write_reports(result, args.output_dir)
        print("Synthetic demonstration only; not current market data or investment advice.")
        print("Expected value: {0:,.2f} {1}".format(result["metrics"]["expected_value"], portfolio.currency))
        for kind, path in paths.items():
            print("{0}: {1}".format(kind, path.resolve()))
        return 0
    except (OSError, ValueError, TypeError, OverflowError, json.JSONDecodeError) as exc:
        print("carbon-risk-lab: error: {0}".format(exc), file=sys.stderr)
        return 2
