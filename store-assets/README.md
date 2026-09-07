# Chrome Web Store artwork

Final upload-ready files are in `final/`:

- `store-icon-128.png` — required 128×128 icon
- `promo-small-440x280.png` — required small promo tile
- `promo-marquee-1400x560.png` — optional marquee tile
- `screenshot-01-new-tab-1280x800.png` — new-tab experience
- `screenshot-02-browser-chrome-1280x800.png` — browser chrome and palette overview

The text-free generated master is preserved in `source/`. To rebuild the final layouts, install Pillow and run:

```sh
python3 -m pip install -r requirements-store.txt
python3 tools/generate_store_assets.py
```

The generated master was created with the built-in image generation workflow; final dimensions, typography, and UI framing are deterministic.
