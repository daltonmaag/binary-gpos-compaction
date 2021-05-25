import argparse
import csv
import sys
from io import BytesIO
from pathlib import Path
from typing import Any, List, Optional, Tuple

from fontTools.ttLib import TTFont

from .compact_kern_feature_writer import compact

# TODO: check performance with harfbuzz with broken up subtables


def main(args: Optional[List[str]] = None):
    parser = argparse.ArgumentParser()
    parser.add_argument("fonts", type=Path, nargs="+", help="Path to TTFs.")
    parsed_args = parser.parse_args()

    rows = []
    font_path: Path
    for font_path in parsed_args.fonts:
        font = TTFont(font_path)
        if "GPOS" not in font:
            print(f"No GPOS in {font_path.name}, skipping.", file=sys.stderr)
            continue
        size_orig = len(font.getTableData("GPOS")) / 1024
        print(f"Measuring {font_path.name}...", file=sys.stderr)

        font_one = TTFont(font_path)
        compact(font_one, mode="one")
        font_one_path = font_path.with_name(font_path.stem + "_one" + font_path.suffix)
        font_one.save(font_one_path)
        font_one = TTFont(font_one_path)
        size_one = len(font_one.getTableData("GPOS")) / 1024

        font_max = TTFont(font_path)
        compact(font_max, mode="max")
        font_max_path = font_path.with_name(font_path.stem + "_max" + font_path.suffix)
        font_max.save(font_max_path)
        font_max = TTFont(font_max_path)
        size_max = len(font_max.getTableData("GPOS")) / 1024

        font_auto = TTFont(font_path)
        compact(font_auto, mode="auto")
        font_auto_path = font_path.with_name(
            font_path.stem + "_auto" + font_path.suffix
        )
        font_auto.save(font_auto_path)
        font_auto = TTFont(font_auto_path)
        size_auto = len(font_auto.getTableData("GPOS")) / 1024

        # Bonus: measure WOFF2 file sizes.
        size_woff_orig = woff_size(font, font_path)
        size_woff_one = woff_size(font_one, font_one_path)
        size_woff_auto = woff_size(font_auto, font_auto_path)
        size_woff_max = woff_size(font_max, font_max_path)

        rows.append(
            (
                font_path.name,
                size_orig,
                size_woff_orig,
                size_one,
                pct(size_one, size_orig),
                size_woff_one,
                pct(size_woff_one, size_woff_orig),
                size_auto,
                pct(size_auto, size_orig),
                size_woff_auto,
                pct(size_woff_auto, size_woff_orig),
                size_max,
                pct(size_max, size_orig),
                size_woff_max,
                pct(size_woff_max, size_woff_orig),
            )
        )

    write_csv(rows)


def woff_size(font: TTFont, path: Path) -> int:
    font.flavor = "woff2"
    woff_path = path.with_suffix(".woff2")
    font.save(woff_path)
    return woff_path.stat().st_size


def write_csv(rows: List[Tuple[Any]]) -> None:
    sys.stdout.write("\uFEFF")
    writer = csv.writer(sys.stdout, lineterminator="\n")
    writer.writerow(
        [
            "File",
            "Original GPOS Size",
            "Original WOFF2 Size",
            "mode=one",
            "Change one",
            "mode=one WOFF2 Size",
            "Change one WOFF2 Size",
            "mode=auto",
            "Change auto",
            "mode=auto WOFF2 Size",
            "Change auto WOFF2 Size",
            "mode=max",
            "Change max",
            "mode=max WOFF2 Size",
            "Change max WOFF2 Size",
        ]
    )
    for row in rows:
        writer.writerow(row)


def pct(new: float, old: float) -> float:
    return -(1 - (new / old))


if __name__ == "__main__":
    main()
