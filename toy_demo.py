"""Standalone CPU illustration of order-dependent local motion."""

from __future__ import annotations

import argparse
from pathlib import Path

FORMAL_METRICS_USED = False
FORMAL_PIPELINE_REPRODUCED = False

STEP = 0.75
SHEAR = 0.80
START = (-0.65, -0.35)


def horizontal(point: tuple[float, float]) -> tuple[float, float]:
    """Apply a closed-form horizontal translation."""
    x, y = point
    return x + STEP, y


def vertical_shear(point: tuple[float, float]) -> tuple[float, float]:
    """Apply a closed-form vertical flow whose speed depends on x."""
    x, y = point
    return x, y + SHEAR * x * STEP


def compose(
    first,
    second,
    point: tuple[float, float] = START,
) -> tuple[float, float]:
    return second(first(point))


def endpoints() -> tuple[tuple[float, float], tuple[float, float]]:
    horizontal_then_shear = compose(horizontal, vertical_shear)
    shear_then_horizontal = compose(vertical_shear, horizontal)
    return horizontal_then_shear, shear_then_horizontal


def analytic_check() -> None:
    horizontal_then_shear, shear_then_horizontal = endpoints()
    observed = (
        horizontal_then_shear[0] - shear_then_horizontal[0],
        horizontal_then_shear[1] - shear_then_horizontal[1],
    )
    expected = (0.0, SHEAR * STEP * STEP)
    if any(abs(left - right) > 1e-12 for left, right in zip(observed, expected)):
        raise RuntimeError("order-dependent endpoint check failed")
    if abs(observed[1]) < 0.1:
        raise RuntimeError("order-dependent endpoint difference is not visible")


def _map(point: tuple[float, float]) -> tuple[float, float]:
    x, y = point
    return 360.0 + 230.0 * x, 280.0 - 230.0 * y


def render_svg() -> str:
    """Return one deterministic, self-contained SVG illustration."""
    analytic_check()
    hs = compose(horizontal, vertical_shear)
    sh = compose(vertical_shear, horizontal)
    h_mid = horizontal(START)
    s_mid = vertical_shear(START)
    points = {
        "start": _map(START),
        "h_mid": _map(h_mid),
        "s_mid": _map(s_mid),
        "hs": _map(hs),
        "sh": _map(sh),
    }

    def line(first: str, second: str, color: str) -> str:
        x1, y1 = points[first]
        x2, y2 = points[second]
        return (
            f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" '
            f'y2="{y2:.2f}" stroke="{color}" stroke-width="5" '
            'stroke-linecap="round" marker-end="url(#arrow)"/>'
        )

    sx, sy = points["start"]
    hsx, hsy = points["hs"]
    shx, shy = points["sh"]
    order_gap = abs(hs[1] - sh[1])
    return "\n".join(
        [
            '<svg xmlns="http://www.w3.org/2000/svg" width="760" height="500" '
            'viewBox="0 0 760 500">',
            "<defs>",
            '<marker id="arrow" markerWidth="8" markerHeight="8" refX="7" '
            'refY="4" orient="auto">',
            '<path d="M0,0 L8,4 L0,8 z" fill="context-stroke"/>',
            "</marker>",
            "</defs>",
            '<rect width="760" height="500" rx="24" fill="#f4f1e9"/>',
            '<text x="44" y="58" font-family="sans-serif" font-size="25" '
            'font-weight="700" fill="#17212b">Order changes the endpoint</text>',
            '<text x="44" y="91" font-family="sans-serif" font-size="16" '
            'fill="#52606d">A horizontal flow changes the state seen by a '
            "vertical shear.</text>",
            '<line x1="80" y1="320" x2="690" y2="320" stroke="#c8c2b5"/>',
            '<line x1="360" y1="120" x2="360" y2="430" stroke="#c8c2b5"/>',
            line("start", "h_mid", "#157f86"),
            line("h_mid", "hs", "#157f86"),
            line("start", "s_mid", "#b3543d"),
            line("s_mid", "sh", "#b3543d"),
            f'<circle cx="{sx:.2f}" cy="{sy:.2f}" r="8" fill="#17212b"/>',
            f'<circle cx="{hsx:.2f}" cy="{hsy:.2f}" r="10" fill="#157f86"/>',
            f'<circle cx="{shx:.2f}" cy="{shy:.2f}" r="10" fill="#b3543d"/>',
            f'<line x1="{hsx + 18:.2f}" y1="{hsy:.2f}" x2="{shx + 18:.2f}" '
            f'y2="{shy:.2f}" stroke="#6c5ce7" stroke-width="3" '
            'stroke-dasharray="6 5"/>',
            f'<text x="{hsx + 30:.2f}" y="{(hsy + shy) / 2:.2f}" '
            'font-family="sans-serif" font-size="15" fill="#5147b8">'
            f"order gap = {order_gap:.3f}</text>",
            '<rect x="44" y="405" width="672" height="56" rx="12" '
            'fill="#ffffff" opacity="0.82"/>',
            '<circle cx="72" cy="433" r="7" fill="#157f86"/>',
            '<text x="88" y="439" font-family="sans-serif" font-size="15" '
            'fill="#263746">horizontal → shear</text>',
            '<circle cx="290" cy="433" r="7" fill="#b3543d"/>',
            '<text x="306" y="439" font-family="sans-serif" font-size="15" '
            'fill="#263746">shear → horizontal</text>',
            '<text x="526" y="439" font-family="sans-serif" font-size="14" '
            'fill="#52606d">standalone CPU toy</text>',
            "</svg>",
            "",
        ]
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Render a standalone non-commutative flow illustration."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Run the analytic check without writing a file.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("toy-output.svg"),
        help="SVG destination used outside check mode.",
    )
    return parser


def main() -> int:
    arguments = _parser().parse_args()
    analytic_check()
    if arguments.check:
        print("status=toy_validated")
        print("formal_metrics_used=false")
        print("formal_pipeline_reproduced=false")
        return 0
    arguments.output.write_text(render_svg(), encoding="utf-8", newline="\n")
    print(f"wrote={arguments.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
