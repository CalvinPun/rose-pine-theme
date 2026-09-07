# Rosé Pine — Afterglow

A modern Chrome theme built around the [Rosé Pine](https://rosepinetheme.com/palette/) palette. Afterglow pairs a deep plum tab strip with a dark omnibox and `surface` toolbar, crisp neutral text, and playful linework in rose, iris, gold, pine, and foam.

## Install locally

1. Open `chrome://extensions` in Chrome.
2. Turn on **Developer mode**.
3. Choose **Load unpacked**.
4. Select this project folder.

Chrome applies the theme immediately. Use **Reset to default** in Chrome's appearance settings to remove it.

If Chrome has already loaded an earlier development build, remove its existing entry from `chrome://extensions` before choosing **Load unpacked** again. Always select the project folder—not the zip file or the `images` folder.

## Package for the Chrome Web Store

Build a clean release archive from the project directory:

```sh
python3 tools/build_theme.py
```

Chrome themes are Manifest V3 packages and contain no scripts or permissions.

## Regenerate the artwork

The seam-safe new-tab background and simplified icon artwork are reproducible and use only Python's standard library:

```sh
python3 tools/generate_assets.py
```

The generated PNGs are committed, so installing the theme does not require Python. Chrome's generated `Cached Theme.pak` is intentionally ignored.

## Palette

The theme uses Rosé Pine's base, surface, overlay, text, love, gold, rose, pine, foam, and iris colors. Rosé Pine is created by [Rosé Pine](https://github.com/rose-pine/rose-pine-theme).
