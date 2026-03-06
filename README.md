# InaVsTheme — Ancient One Dark for Visual Studio

Ninomae Ina'nis color themes for Visual Studio 2022/2026, ported from the beloved [Ancient One Dark](https://github.com/sigvt/ancient-one-dark) VS Code theme.

## Theme Variants

- **Ancient One Dark** — Deep purple editor with gold accents
- **Ancient One Dark Violet** — Deeper indigo-purple with warm gold accents
- **Ancient One Dark Slate** — Neutral dark with indigo accents

## Installation

1. Download the latest `.vsix` from [Releases](https://github.com/BlackSiroGhost/InaVsTheme/releases)
2. Double-click the `.vsix` file to install
3. Restart Visual Studio
4. Go to **Tools > Theme** and select one of the Ancient One Dark variants

## Building from Source

Requires Visual Studio 2022 17.9+ with the **Visual Studio extension development** workload.

```
msbuild src\InaVsTheme.csproj /p:Configuration=Release
```

The `.vsix` will be in `src\bin\Release\`.

## Credits

These themes are Visual Studio ports of [**Ancient One Dark**](https://github.com/sigvt/ancient-one-dark) by [sigvt](https://github.com/sigvt).
All color palettes originate from that project. Full credit to the original authors for their beautiful theme design.

Extension structure inspired by [VantaBlack](https://github.com/madskristensen/VantaBlack) by Mads Kristensen.

## License

[MIT](LICENSE.txt)
