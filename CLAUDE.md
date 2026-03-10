# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

InaVsTheme is a Visual Studio theme extension ("Ancient One Dark") with three color variants (Dark, Violet, Slate). It ships as two separate VSIX packages: one for VS 2022 (17.9+) and one for VS 2026 (18.x). There are no tests — validation is manual by installing the VSIX.

## Build

```cmd
build.cmd
```

Outputs:
- `src\bin\Release\InaVsTheme.vsix` (VS 2026)
- `vs22\bin\Release\InaVsTheme-VS2022.vsix` (VS 2022)

Requires Visual Studio with the "Visual Studio extension development" workload installed at the default paths used in `build.cmd`.

To build a single target:
```cmd
"C:\Program Files\Microsoft Visual Studio\18\Community\MSBuild\Current\Bin\amd64\MSBuild.exe" src\InaVsTheme.csproj -p:Configuration=Release -restore
"C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe" vs22\InaVsTheme22.csproj -p:Configuration=Release -restore
```

## Architecture

### Two parallel projects

`src/` (VS 2026) and `vs22/` (VS 2022) mirror each other in structure but target different VS SDK versions. Both have the same files: `AncientOnePackage.cs`, `AncientOneCommandSet.vsct`, `source.extension.vsixmanifest`, and `AncientOneDark.vstheme`.

### Theme definitions

- **VS 2026** (`src/AncientOneDark.vstheme`): ~50 KB, hand-maintained XML defining all three variants in one file.
- **VS 2022** (`vs22/AncientOneDark.vstheme`): ~1.3 MB, **generated** — do not edit by hand. Run `python vs22/generate_theme.py` to regenerate from the color palette defined in that script.

The VS 2022 theme file is large because it enumerates every Shell/ShellInternal WinUI token explicitly.

### Theme switching (C#)

`AncientOnePackage.cs` registers menu commands (one per variant). On command invocation, it directly writes the theme GUID to the VS `settings.json` file and clears font/color caches via `IVsFontAndColorCacheManager`. VS 2026 uses GUID slugs for theme identification; VS 2022 uses name strings — the two `AncientOnePackage.cs` files differ in this regard.

### Color palette / variant GUIDs

Each variant has a stable GUID used in:
- `generate_theme.py` (source of truth for VS 2022)
- `src/AncientOneDark.vstheme` (must match for VS 2026)
- `AncientOnePackage.cs` in both projects (must match for menu commands)

When adding a new variant or changing GUIDs, update all three locations.

### VSIX manifests

`source.extension.vsixmanifest` declares the VS version range and CPU architectures (amd64/arm64). VS 2022 targets `[17.9, 18.0)` and VS 2026 targets `[18.0, 19.0)` — this separation prevents installation conflicts.
