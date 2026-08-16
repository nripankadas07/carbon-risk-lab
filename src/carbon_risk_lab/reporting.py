"""Report rendering for Carbon Risk Lab."""

import html
import json
import re
from pathlib import Path
from typing import Any, Dict


def _markdown_text(value: Any) -> str:
    """Render untrusted values as one inert Markdown line."""
    text = re.sub(r"\s+", " ", str(value)).strip()
    return "".join(
        character
        if character.isalnum() or character == " "
        else "&#{0};".format(ord(character))
        for character in text
    )


def _markdown(result: Dict[str, Any]) -> str:
    m = result["metrics"]
    lines = [
        "# Carbon Risk Lab report",
        "",
        "> **Synthetic only:** {0}".format(_markdown_text(result["synthetic_notice"])),
        "",
        "- Portfolio: `{0}`".format(_markdown_text(result["portfolio"]["portfolio_id"])),
        "- Seed: `{0}`".format(result["run"]["seed"]),
        "- Simulations: `{0:,}`".format(result["run"]["simulations"]),
        "- Artifact schema: `{0}`".format(result["schema_version"]),
        "",
        "## Distribution and tail risk",
        "",
        "| Metric | Synthetic value |",
        "|---|---:|",
        "| Baseline | {0:,.2f} |".format(m["baseline_value"]),
        "| Expected value | {0:,.2f} |".format(m["expected_value"]),
        "| P05 / P50 / P95 | {0:,.2f} / {1:,.2f} / {2:,.2f} |".format(m["value_p05"], m["value_p50"], m["value_p95"]),
        "| Loss VaR 95 | {0:,.2f} |".format(m["loss_var_95"]),
        "| Loss CVaR 95 | {0:,.2f} |".format(m["loss_cvar_95"]),
        "| Loss VaR 99 | {0:,.2f} |".format(m["loss_var_99"]),
        "| Loss CVaR 99 | {0:,.2f} |".format(m["loss_cvar_99"]),
        "| Probability of loss | {0:.2%} |".format(m["probability_of_loss"]),
        "",
        "## Sensitivities",
        "",
        "| Stress | Expected value change | Change % | CVaR95 change vs original baseline |",
        "|---|---:|---:|---:|",
    ]
    for row in result["sensitivities"]:
        lines.append(
            "| `{0}` | {1:,.2f} | {2:.2%} | {3:,.2f} |".format(
                _markdown_text(row["stress"]),
                row["expected_value_change"],
                row["expected_value_change_fraction"],
                row["loss_cvar_95_change"],
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation boundary",
            "",
            "These outputs validate software behavior under explicitly synthetic assumptions. They are not prices, forecasts, ratings, verification outcomes, or investment advice.",
            "",
        ]
    )
    return "\n".join(lines)


def _html(result: Dict[str, Any]) -> str:
    m = result["metrics"]
    sensitivity_rows = "".join(
        "<tr><td>{0}</td><td>{1:,.2f}</td><td>{2:.2%}</td><td>{3:,.2f}</td></tr>".format(
            html.escape(row["stress"]),
            row["expected_value_change"],
            row["expected_value_change_fraction"],
            row["loss_cvar_95_change"],
        )
        for row in result["sensitivities"]
    )
    embedded = html.escape(json.dumps(result, sort_keys=True, allow_nan=False))
    return """<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Carbon Risk Lab</title>
<style>body{{font:16px system-ui;max-width:1050px;margin:2rem auto;padding:0 1rem;color:#14231d}}.notice{{padding:1rem;background:#fff3cd;border-left:4px solid #d49a00}}.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:1rem;margin:1.5rem 0}}.card{{border:1px solid #cedbd4;border-radius:10px;padding:1rem}}.value{{font-size:1.45rem;font-weight:700}}table{{border-collapse:collapse;width:100%}}th,td{{border-bottom:1px solid #dce4df;padding:.55rem;text-align:right}}th:first-child,td:first-child{{text-align:left}}code{{word-break:break-all}}</style>
<body><h1>Carbon Risk Lab</h1><p>{portfolio} · seed {seed} · {simulations:,} simulations</p><p class="notice"><strong>Synthetic only.</strong> {notice}</p>
<div class="cards"><div class="card"><div>Expected value</div><div class="value">{expected:,.0f}</div></div><div class="card"><div>VaR 95</div><div class="value">{var95:,.0f}</div></div><div class="card"><div>CVaR 95</div><div class="value">{cvar95:,.0f}</div></div><div class="card"><div>Loss probability</div><div class="value">{loss_probability:.1%}</div></div></div>
<h2>Sensitivities</h2><p>Stress loss CVaR uses the original, unstressed baseline.</p><table><thead><tr><th>Stress</th><th>Expected change</th><th>Change %</th><th>CVaR95 change vs original baseline</th></tr></thead><tbody>{rows}</tbody></table>
<details><summary>Embedded versioned JSON artifact</summary><code>{embedded}</code></details></body></html>""".format(
        portfolio=html.escape(result["portfolio"]["portfolio_id"]),
        seed=result["run"]["seed"],
        simulations=result["run"]["simulations"],
        notice=html.escape(result["synthetic_notice"]),
        expected=m["expected_value"],
        var95=m["loss_var_95"],
        cvar95=m["loss_cvar_95"],
        loss_probability=m["probability_of_loss"],
        rows=sensitivity_rows,
        embedded=embedded,
    )


def write_reports(result: Dict[str, Any], output_dir: Path) -> Dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "json": output_dir / "carbon_risk_report.json",
        "markdown": output_dir / "carbon_risk_report.md",
        "html": output_dir / "carbon_risk_report.html",
    }
    paths["json"].write_text(
        json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    paths["markdown"].write_text(_markdown(result), encoding="utf-8")
    paths["html"].write_text(_html(result), encoding="utf-8")
    return paths
