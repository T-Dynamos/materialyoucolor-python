const resolveMcuDir = (): string => {
  const envDir = Deno.env.get("MCU_TYPESCRIPT_DIR");
  if (envDir) return envDir;

  const candidates = [
    Deno.cwd() + "/material-color-utilities/typescript",
    "/home/tdynamos/Downloads/material-color-utilities/typescript",
    new URL("../material-color-utilities/typescript", import.meta.url).pathname,
  ];
  for (const c of candidates) {
    try {
      if (Deno.statSync(`${c}/scheme/scheme_cmf.ts`).isFile) return c;
    } catch (_) {}
  }
  return candidates[0];
};

const MCU_DIR = resolveMcuDir();
const {Hct} = await import(`${MCU_DIR}/hct/hct.ts`);
const {DynamicScheme} = await import(`${MCU_DIR}/dynamiccolor/dynamic_scheme.ts`);
const {MaterialDynamicColors} = await import(`${MCU_DIR}/dynamiccolor/material_dynamic_colors.ts`);
const {Variant} = await import(`${MCU_DIR}/dynamiccolor/variant.ts`);
const {SchemeCmf} = await import(`${MCU_DIR}/scheme/scheme_cmf.ts`);

const COLOR_NAMES = [
  "background",
  "onBackground",
  "surface",
  "surfaceDim",
  "surfaceBright",
  "surfaceContainerLowest",
  "surfaceContainerLow",
  "surfaceContainer",
  "surfaceContainerHigh",
  "surfaceContainerHighest",
  "onSurface",
  "surfaceVariant",
  "onSurfaceVariant",
  "outline",
  "outlineVariant",
  "inverseSurface",
  "inverseOnSurface",
  "shadow",
  "scrim",
  "surfaceTint",
  "primary",
  "primaryDim",
  "onPrimary",
  "primaryContainer",
  "onPrimaryContainer",
  "inversePrimary",
  "primaryFixed",
  "primaryFixedDim",
  "onPrimaryFixed",
  "onPrimaryFixedVariant",
  "secondary",
  "secondaryDim",
  "onSecondary",
  "secondaryContainer",
  "onSecondaryContainer",
  "secondaryFixed",
  "secondaryFixedDim",
  "onSecondaryFixed",
  "onSecondaryFixedVariant",
  "tertiary",
  "tertiaryDim",
  "onTertiary",
  "tertiaryContainer",
  "onTertiaryContainer",
  "tertiaryFixed",
  "tertiaryFixedDim",
  "onTertiaryFixed",
  "onTertiaryFixedVariant",
  "error",
  "errorDim",
  "onError",
  "errorContainer",
  "onErrorContainer",
  "primaryPaletteKeyColor",
  "secondaryPaletteKeyColor",
  "tertiaryPaletteKeyColor",
  "neutralPaletteKeyColor",
  "neutralVariantPaletteKeyColor",
  "errorPaletteKeyColor",
];

function main() {
  const [seedArgbStr, variantsStr, specsStr, platformsStr, contrastsStr] = Deno.args;
  if (!seedArgbStr || !variantsStr || !specsStr || !platformsStr || !contrastsStr) {
    console.error(
      "Usage: compare_ts_py.ts <seed_argb> <variants_csv> <specs_csv> <platforms_csv> <contrasts_csv>",
    );
    Deno.exit(2);
  }

  const seedArgb = Number(seedArgbStr);
  const variants = variantsStr.split(",").map((v) => v.trim()).filter(Boolean);
  const specs = specsStr.split(",").map((s) => s.trim()).filter(Boolean);
  const platforms = platformsStr.split(",").map((p) => p.trim()).filter(Boolean);
  const contrasts = contrastsStr.split(",").map((c) => Number(c.trim())).filter((c) => !Number.isNaN(c));

  const mdc = new MaterialDynamicColors();
  const out: Record<string, Record<string, number | null>> = {};

  for (const specVersion of specs) {
    for (const platform of platforms) {
      for (const contrast of contrasts) {
        for (const variantName of variants) {
          const variant = (Variant as any)[variantName];
          if (variant === Variant.CMF && specVersion !== "2026") {
            continue;
          }
          for (const isDark of [false, true]) {
            let scheme: DynamicScheme;
            if (variant === Variant.CMF) {
              scheme = new SchemeCmf(
                Hct.fromInt(seedArgb),
                isDark,
                contrast,
                specVersion as "2026",
                platform as "phone" | "watch",
              );
            } else {
              scheme = new DynamicScheme({
                sourceColorHct: Hct.fromInt(seedArgb),
                variant,
                contrastLevel: contrast,
                isDark,
                platform: platform as "phone" | "watch",
                specVersion: specVersion as "2021" | "2025" | "2026",
              });
            }

            const result: Record<string, number | null> = {};
            for (const name of COLOR_NAMES) {
              const fn = (mdc as any)[name];
              if (typeof fn !== "function") {
                result[name] = null;
                continue;
              }
              const dc = fn.call(mdc);
              if (dc === undefined) {
                result[name] = null;
              } else {
                result[name] = scheme.getArgb(dc);
              }
            }

            const mode = isDark ? "dark" : "light";
            const key = `${specVersion}|${platform}|${contrast}|${variantName}|${mode}`;
            out[key] = result;
          }
        }
      }
    }
  }

  console.log(JSON.stringify(out));
}

main();
