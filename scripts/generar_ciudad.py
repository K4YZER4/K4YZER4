"""Generate the static contribution city used by the profile README."""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from datetime import date, timedelta
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "code-city.svg"
API_URL = "https://github-contributions-api.jogruber.de/v4/K4YZER4?y=last"
USER_AGENT = "K4YZER4-code-city-generator/1.0"

CELL_WEEK_X = 23
CELL_WEEK_Y = 4
CELL_DAY_X = -23
CELL_DAY_Y = 13
ORIGIN_X = 195
ORIGIN_Y = 160
BUILDING_WIDTH = 16
BUILDING_DEPTH = 9
MAX_HEIGHT = 105
MAX_COUNT = 12
MARGIN = 18

COLORS = {
    "background": "#101010",
    "front": "#202020",
    "side": "#131313",
    "roof": "#303030",
    "off_windows": "#3A3A3A",
    "shadow": "#050505",
    "accent_low": "#534C3D",
    "accent_mid": "#897859",
    "accent_high": "#BDA478",
    "accent_max": "#EAD6AF",
}


def fetch_contributions() -> list[dict[str, object]]:
    request = urllib.request.Request(API_URL, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            if response.status != 200:
                raise RuntimeError(f"la API respondió con HTTP {response.status}")
            payload = json.load(response)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
        raise RuntimeError(f"no se pudieron consultar las contribuciones: {error}") from error

    raw_days = payload.get("contributions") if isinstance(payload, dict) else None
    if not isinstance(raw_days, list) or not raw_days:
        raise RuntimeError("la respuesta no contiene una lista de contribuciones")

    days: list[dict[str, object]] = []
    for item in raw_days:
        if not isinstance(item, dict):
            raise RuntimeError("la respuesta contiene un día con formato inválido")
        raw_date = item.get("date")
        count = item.get("count")
        level = item.get("level")
        if not isinstance(raw_date, str) or not isinstance(count, int) or isinstance(count, bool):
            raise RuntimeError("cada día debe tener fecha y cantidad numérica")
        if count < 0 or not isinstance(level, int) or level < 0 or level > 4:
            raise RuntimeError(f"datos inválidos para {raw_date}")
        try:
            parsed_date = date.fromisoformat(raw_date)
        except ValueError as error:
            raise RuntimeError(f"fecha inválida: {raw_date}") from error
        days.append({"date": parsed_date, "count": count, "level": level})

    days.sort(key=lambda item: item["date"])
    expected = days[0]["date"]
    for item in days:
        if item["date"] != expected:
            raise RuntimeError(f"faltan días en la respuesta antes de {item['date'].isoformat()}")
        expected += timedelta(days=1)
    return days


def iso_day(value: object) -> str:
    if not isinstance(value, date):
        raise TypeError("expected a date")
    return value.isoformat()


def accent_for(level: int, count: int) -> str:
    if count == 0:
        return COLORS["off_windows"]
    return {
        1: COLORS["accent_low"],
        2: COLORS["accent_mid"],
        3: COLORS["accent_high"],
        4: COLORS["accent_max"],
    }[max(1, min(level, 4))]


def polygon(points: list[tuple[float, float]], fill: str, stroke: str | None = None) -> str:
    coordinates = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    outline = f' stroke="{stroke}" stroke-width=".7"' if stroke else ""
    return f'<polygon points="{coordinates}" fill="{fill}"{outline}/>'


def building(
    day: dict[str, object], week: int, weekday: int
) -> tuple[str, tuple[float, float, float, float]]:
    count = int(day["count"])
    level = int(day["level"])
    x = ORIGIN_X + week * CELL_WEEK_X + weekday * CELL_DAY_X
    y = ORIGIN_Y + week * CELL_WEEK_Y + weekday * CELL_DAY_Y
    height = 12 + round(MAX_HEIGHT * min(count, MAX_COUNT) / MAX_COUNT)
    base_y = y
    top_y = base_y - height
    width = BUILDING_WIDTH
    depth = BUILDING_DEPTH
    fill = accent_for(level, count)
    side = "#35312B" if count else COLORS["side"]
    face = "#625746" if count else COLORS["front"]
    roof = COLORS["accent_mid"] if count else COLORS["roof"]
    date_text = f"{iso_day(day['date'])}: {count} contribuciones"
    parts = [
        f'<g aria-label="{escape(date_text)}"><title>{escape(date_text)}</title>',
        polygon([(x - 3, base_y + 2), (x + width + 4, base_y + 7), (x + width + depth + 9, base_y - 1), (x + 10, base_y - 6)], COLORS["shadow"]),
        polygon([(x, top_y), (x + width, top_y + 4), (x + width, base_y + 4), (x, base_y)], face, "#080808"),
        polygon([(x + width, top_y + 4), (x + width + depth, top_y - 1), (x + width + depth, base_y - 1), (x + width, base_y + 4)], side, "#080808"),
        polygon([(x, top_y), (x + depth, top_y - 5), (x + width + depth, top_y - 1), (x + width, top_y + 4)], roof, "#383838"),
    ]

    for window_offset in range(8, height - 3, 9):
        window_y = top_y + window_offset
        for column in range(2):
            window_x = x + 3 + column * 7
            parts.append(
                f'<path d="M {window_x:.1f} {window_y:.1f} l 3 .75 v 3 l -3 -.75 z" '
                f'fill="{fill if count else COLORS["off_windows"]}" opacity="{".95" if count else ".5"}"/>'
            )
        parts.append(
            f'<path d="M {x + 19:.1f} {window_y + 1:.1f} l 3 -1.65 v 3 l -3 1.65 z" '
            f'fill="{fill if count else COLORS["roof"]}" opacity=".65"/>'
        )
    if count > MAX_COUNT // 2:
        parts.append(f'<path d="M {x + 18:.1f} {top_y - 2:.1f} V {top_y - 13:.1f}" stroke="#D6C19A" stroke-width=".8"/>')
        parts.append(f'<circle cx="{x + 18:.1f}" cy="{top_y - 14:.1f}" r="1.3" fill="{COLORS["accent_max"]}"/>')
    parts.append("</g>")
    bounds = (x - 4, top_y - (16 if count > MAX_COUNT // 2 else 5), x + width + depth + 10, base_y + 8)
    return "".join(parts), bounds


def generate(days: list[dict[str, object]]) -> str:
    first_date = days[0]["date"]
    if not isinstance(first_date, date):
        raise RuntimeError("fecha inicial inválida")

    # Keep one column per calendar week; weekday zero is Sunday for this grid.
    by_day = {day["date"]: day for day in days}
    first_sunday = first_date - timedelta(days=(first_date.weekday() + 1) % 7)
    last_date = days[-1]["date"]
    week_count = ((last_date - first_sunday).days // 7) + 1

    buildings: list[str] = []
    bounds: list[tuple[float, float, float, float]] = []
    for weekday in range(7):
        for week in range(week_count):
            current = first_sunday + timedelta(days=week * 7 + weekday)
            if current in by_day:
                rendered, building_bounds = building(by_day[current], week, weekday)
                buildings.append(rendered)
                bounds.append(building_bounds)

    min_x = min(bound[0] for bound in bounds)
    min_y = min(bound[1] for bound in bounds)
    max_x = max(bound[2] for bound in bounds)
    max_y = max(bound[3] for bound in bounds)
    view_min_x = min_x - MARGIN
    view_min_y = min_y - MARGIN
    view_width = max_x - min_x + MARGIN * 2
    view_height = max_y - min_y + MARGIN * 2

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{view_min_x:.1f} {view_min_y:.1f} {view_width:.1f} {view_height:.1f}" width="100%" role="img"',
        ' aria-labelledby="city-title city-description">',
        '<title id="city-title">Ciudad del código</title>',
        '<desc id="city-description">Ciudad isométrica formada por un edificio por cada día del calendario público de contribuciones de K4YZER4 durante el último año. La altura representa la actividad diaria y la escala se limita visualmente a 12 contribuciones.</desc>',
        f'<rect x="{view_min_x:.1f}" y="{view_min_y:.1f}" width="{view_width:.1f}" height="{view_height:.1f}" fill="{COLORS["background"]}"/>',
        '<g aria-label="Edificios del calendario de contribuciones">',
    ]
    parts.extend(buildings)
    parts.extend(["</g>", "</svg>"])
    return "\n".join(parts) + "\n"


def main() -> int:
    try:
        svg = generate(fetch_contributions())
        OUTPUT.write_text(svg, encoding="utf-8", newline="\n")
    except RuntimeError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    print(f"Generado {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
