import argparse
import json
import os
import subprocess
import sys
from typing import Dict, List, Tuple, Literal, cast

# Ensure repo root is on sys.path so we import local code, not site-packages.
REPO_ROOT = os.path.dirname(os.path.dirname(__file__))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from materialyoucolor.dynamiccolor.color_spec import COLOR_NAMES
from materialyoucolor.dynamiccolor.dynamic_scheme import DynamicScheme
from materialyoucolor.dynamiccolor.material_dynamic_colors import MaterialDynamicColors
from materialyoucolor.dynamiccolor.variant import Variant
from materialyoucolor.scheme.scheme_cmf import SchemeCmf
from materialyoucolor.hct.hct import Hct
from materialyoucolor.utils.color_utils import argb_from_rgb

try:
    from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn

    _HAS_RICH = True
except Exception:
    _HAS_RICH = False


TS_SCRIPT = os.path.join(REPO_ROOT, "tests", "compare_ts_py.ts")
DENO = "deno"


def parse_hex_rgb(hex_str: str) -> int:
    s = hex_str.strip().lstrip("#")
    if len(s) != 6:
        raise ValueError(f"Expected 6-digit hex RGB, got: {hex_str}")
    r = int(s[0:2], 16)
    g = int(s[2:4], 16)
    b = int(s[4:6], 16)
    return argb_from_rgb(r, g, b)


SpecVersion = Literal["2021", "2025", "2026"]
Platform = Literal["phone", "watch"]


def python_colors(
    seed_argb: int,
    variant: Variant,
    is_dark: bool,
    contrast: float,
    spec: SpecVersion,
    platform: Platform,
) -> Dict[str, int | None]:
    if variant == Variant.CMF:
        if spec != "2026":
            return {}
        scheme = SchemeCmf(
            Hct.from_int(seed_argb),
            is_dark=is_dark,
            contrast_level=contrast,
            spec_version=spec,
            platform=platform,
        )
    else:
        scheme = DynamicScheme(
            source_color_hct=Hct.from_int(seed_argb),
            variant=variant,
            contrast_level=contrast,
            is_dark=is_dark,
            platform=platform,
            spec_version=spec,
        )
    mdc = MaterialDynamicColors()
    out: Dict[str, int | None] = {}
    for name in COLOR_NAMES:
        dc = getattr(mdc, name)
        if dc is None:
            out[name] = None
        else:
            out[name] = scheme.get_argb(dc)
    return out


def run_ts_bulk(
    seed_argb: int,
    variants: List[str],
    specs: List[SpecVersion],
    platforms: List[Platform],
    contrasts: List[float],
) -> Dict[str, Dict[str, int | None]]:
    contrasts_norm = [format(c, "g") for c in contrasts]
    cmd = [
        DENO,
        "run",
        "--sloppy-imports",
        "--allow-env",
        "--allow-read",
        TS_SCRIPT,
        str(seed_argb),
        ",".join(variants),
        ",".join(specs),
        ",".join(platforms),
        ",".join(contrasts_norm),
    ]
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    return cast(Dict[str, Dict[str, int | None]], json.loads(result.stdout))


def diff_maps(
    py_map: Dict[str, int | None], ts_map: Dict[str, int | None]
) -> List[str]:
    diffs = []
    for name in COLOR_NAMES:
        py_val = py_map.get(name)
        ts_val = ts_map.get(name)
        if py_val != ts_val:
            diffs.append(
                f"{name}: py={hex(py_val) if py_val is not None else None} "
                f"ts={hex(ts_val) if ts_val is not None else None}"
            )
    return diffs


def all_variants() -> List[Tuple[str, Variant]]:
    return [(v.name, v) for v in Variant]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare Python vs TS material color outputs across all variants."
    )
    parser.add_argument("--seed", default="#8A7343", help="Seed color hex RGB")
    parser.add_argument(
        "--specs", default="2021,2025,2026", help="Comma-separated specs"
    )
    parser.add_argument(
        "--platforms", default="phone,watch", help="Comma-separated platforms"
    )
    parser.add_argument(
        "--contrasts",
        default="-1,0,0.5,1",
        help="Comma-separated contrast levels",
    )
    parser.add_argument("--fail-fast", action="store_true")
    args = parser.parse_args()

    seed_argb = parse_hex_rgb(args.seed)
    specs = [cast(SpecVersion, s.strip()) for s in args.specs.split(",") if s.strip()]
    platforms = [
        cast(Platform, p.strip()) for p in args.platforms.split(",") if p.strip()
    ]
    contrasts = [float(c.strip()) for c in args.contrasts.split(",") if c.strip()]

    total_failures = 0
    variant_names = [name for name, _ in all_variants()]
    ts_results = run_ts_bulk(seed_argb, variant_names, specs, platforms, contrasts)

    total_checks = 0
    for spec in specs:
        for platform in platforms:
            for contrast in contrasts:
                for variant_name, variant in all_variants():
                    if variant == Variant.CMF and spec != "2026":
                        continue
                    total_checks += 2

    completed = 0

    def _step() -> None:
        nonlocal completed
        completed += 1

    if _HAS_RICH:
        progress = Progress(
            TextColumn("{task.description}"),
            BarColumn(),
            TextColumn("{task.completed}/{task.total}"),
            TimeElapsedColumn(),
        )
        progress.start()
        task_id = progress.add_task("Comparing", total=total_checks)

        try:
            for spec in specs:
                for platform in platforms:
                    for contrast in contrasts:
                        for variant_name, variant in all_variants():
                            if variant == Variant.CMF and spec != "2026":
                                continue
                            for is_dark in (False, True):
                                py_map = python_colors(
                                    seed_argb,
                                    variant,
                                    is_dark,
                                    contrast,
                                    spec,
                                    platform,
                                    )
                                mode = "dark" if is_dark else "light"
                                contrast_key = format(contrast, "g")
                                key = (
                                    f"{spec}|{platform}|{contrast_key}|"
                                    f"{variant_name}|{mode}"
                                )
                                ts_map = ts_results.get(key)
                                if ts_map is None:
                                    raise RuntimeError(f"Missing TS results for {key}")
                                diffs = diff_maps(py_map, ts_map)
                                if diffs:
                                    total_failures += 1
                                    print(
                                        f"Mismatch: spec={spec} platform={platform} "
                                        f"contrast={contrast} variant={variant_name} mode={mode}"
                                    )
                                    for line in diffs:
                                        print(f"  {line}")
                                    if args.fail_fast:
                                        raise SystemExit(1)
                                _step()
                                progress.update(task_id, completed=completed)
        finally:
            progress.stop()
    else:
        for spec in specs:
            for platform in platforms:
                for contrast in contrasts:
                    for variant_name, variant in all_variants():
                        if variant == Variant.CMF and spec != "2026":
                            continue
                        for is_dark in (False, True):
                            py_map = python_colors(
                                seed_argb,
                                variant,
                                is_dark,
                                contrast,
                                spec,
                                platform,
                            )
                            mode = "dark" if is_dark else "light"
                            contrast_key = format(contrast, "g")
                            key = f"{spec}|{platform}|{contrast_key}|{variant_name}|{mode}"
                            ts_map = ts_results.get(key)
                            if ts_map is None:
                                raise RuntimeError(f"Missing TS results for {key}")
                            diffs = diff_maps(py_map, ts_map)
                            if diffs:
                                total_failures += 1
                                print(
                                    f"Mismatch: spec={spec} platform={platform} "
                                    f"contrast={contrast} variant={variant_name} mode={mode}"
                                )
                                for line in diffs:
                                    print(f"  {line}")
                                if args.fail_fast:
                                    raise SystemExit(1)
                            _step()

    if total_failures == 0:
        print("All comparisons matched.")
        raise SystemExit(0)
    else:
        print(f"Total mismatching cases: {total_failures}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
