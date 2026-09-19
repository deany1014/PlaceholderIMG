# Placeholder Image Generator

`So uhm claude made this entire project cause im lazy, i commanded claude to make this cause im building a website and needed some placeholders. Use it how you like or implement it into your own apps/software`

A tiny command-line tool that generates clean placeholder images for websites and mockups, for when you're building a site but don't have the real photos yet.

Each image has your own **custom label**, the **dimensions**, the **file type**, and a thin **cross** across the background so you can instantly see where the center of the photo is.

<p align="center">
  <img src="examples/hero-image.jpg" alt="Example: Hero Image, 1920x1080" width="640">
</p>

## Features

- Custom label instead of a fixed text (`Hero Image`, `Team Photo`, `Logo`, ...)
- Cross drawn corner to corner (anti-aliased) to mark the center
- Any size, and text scales along automatically
- Long labels shrink automatically so they always fit
- Generate many placeholders in one command, each with its own size
- Output as `jpg`, `png` or `webp`
- Custom colors and a custom font if you want them
- Interactive mode if you'd rather not remember any options

## Download (Windows)

Don't want to install Python? Download `placeholder.exe` from the [latest release](../../releases/latest) and run it from a terminal:

```powershell
.\placeholder.exe "Hero Image" "Team Photo:800x600"
```

Double-clicking the exe starts the interactive mode. The font is bundled inside the exe, so no internet connection is needed.

> Windows SmartScreen or your antivirus may warn about the exe, because it's an unsigned PyInstaller build. If you'd rather not trust it, run the Python script directly instead (see below).

## Installation

Requires Python 3.8+.

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>
pip install -r requirements.txt
```

The font ([Poppins Black](https://fonts.google.com/specimen/Poppins), SIL Open Font License) is downloaded automatically the first time you run the script and cached in a `fonts/` folder next to it.

## Usage

```bash
# Interactive mode: asks for a name and size
python placeholder.py

# One placeholder (default size 1920x1080, jpg)
python placeholder.py "Hero Image"

# Custom size
python placeholder.py "Hero Image" -s 1600x900

# Several at once, each with its own size (NAME:WIDTHxHEIGHT)
python placeholder.py "Hero Image" "Team Photo:800x600" "Logo:400x400"

# PNG in a custom folder
python placeholder.py "Banner:1200x300" -f png -o ./img
```

Files are saved to `./placeholders/` by default, named after the label (`Team Photo` becomes `team-photo.jpg`). If you generate two placeholders with the same label, the second one overwrites the first.

<p align="center">
  <img src="examples/team-photo.jpg" alt="Example: Team Photo, 800x600" width="400">
</p>

## Options

| Option | Description | Default |
| --- | --- | --- |
| `NAME[:WxH]` | One or more labels, optionally with their own size | interactive mode |
| `-s`, `--size` | Default size for all placeholders | `1920x1080` |
| `-f`, `--format` | File type: `jpg`, `png`, `webp` | `jpg` |
| `-o`, `--output` | Output folder | `./placeholders` |
| `--bg` | Background color | `#000000` |
| `--fg` | Text color | `#ffffff` |
| `--line-color` | Color of the cross | `#808080` |
| `--no-cross` | Don't draw the cross | off |
| `--quality` | Quality for jpg/webp (1-100) | `92` |
| `--font` | Path to your own `.ttf` font | Poppins Black |

Colors accept anything Pillow understands: hex (`#1a1a2e`), names (`navy`), or `rgb(20, 20, 40)`.

Example with custom colors:

```bash
python placeholder.py "Product Photo:1000x1000" --bg "#1a1a2e" --fg "#eaeaea" --line-color "#444"
```

## Notes

- Sizes must be between 16 and 10,000 px.
- Labels are always rendered in uppercase.
- If the font can't be downloaded (no internet), the script falls back to Arial Black / Arial Bold / DejaVu Bold if available. You can also download `Poppins-Black.ttf` yourself and put it in `fonts/`, or point to any font with `--font`.
- Layout is tuned for 1920x1080 and scaled proportionally for other sizes.

## Releasing a new version

A GitHub Action (`.github/workflows/release.yml`) builds `placeholder.exe` with PyInstaller and attaches it to a GitHub release whenever you push a version tag:

```bash
git tag v1.0.0
git push origin v1.0.0
```

You can also run the workflow manually from the **Actions** tab to test the build. In that case the exe is available as a build artifact, and no release is created.

## Credits

Font: [Poppins](https://github.com/itfoundry/Poppins) by Indian Type Foundry, licensed under the [SIL Open Font License 1.1](https://openfontlicense.org/).

## License
`This is free and unencumbered software released into the public domain.`

`Anyone is free to copy, modify, publish, use, compile, sell, or distribute this software, either in source code form or as a compiled binary, for any purpose, commercial or non-commercial, and by any means.`

`In jurisdictions that recognize copyright laws, the author or authors of this software dedicate any and all copyright interest in the software to the public domain. We make this dedication for the benefit of the public at large and to the detriment of our heirs and successors. We intend this dedication to be an overt act of relinquishment in perpetuity of all present and future rights to this software under copyright law.`

`THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.`

[`For more information, please refer to https://unlicense.org`](https://unlicense.org)