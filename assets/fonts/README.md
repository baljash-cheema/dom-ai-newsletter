# Embedded fonts

Two script fonts give the newsletter its personality. `build.py` inlines them
into every issue as base64 `@font-face` data URIs, so the HTML/PDF stay fully
self-contained.

| File | Family | Used for | Source / copyright |
|------|--------|----------|--------------------|
| `GreatVibes-subset.woff2` | Great Vibes | the "Welcome" wordmark (page 1) | © 2015 The Great Vibes Project Authors — https://github.com/googlefonts/great-vibes |
| `DancingScript-subset.woff2` | Dancing Script | the signature (page 1) | © 2010 The Dancing Script Project Authors — https://github.com/impallari/DancingScript |

**License:** both are licensed under the **SIL Open Font License, Version 1.1**
(full text in [`OFL.txt`](OFL.txt)). The OFL permits bundling and embedding; it
only forbids selling the fonts on their own. This repo's MIT license covers the
*code* — the fonts keep their OFL license.

## Regenerating the subsets
The committed files are subset to printable ASCII and converted to woff2 to keep
them tiny (~28 KB each). To rebuild them from the full fonts:

```bash
.venv/bin/pip install fonttools brotli          # build-time only, not a runtime dep
# download GreatVibes-Regular.ttf and DancingScript[wght].ttf from the sources above, then:
.venv/bin/python - <<'PY'
from fontTools import subset
def sub(src, dst):
    opts = subset.Options(); opts.flavor = "woff2"; opts.desubroutinize = True
    font = subset.load_font(src, opts)
    s = subset.Subsetter(options=opts)
    s.populate(unicodes=list(range(0x20, 0x7F)))   # printable ASCII
    s.subset(font); subset.save_font(font, dst, opts)
sub("GreatVibes-Regular.ttf", "GreatVibes-subset.woff2")
sub("DancingScript[wght].ttf", "DancingScript-subset.woff2")
PY
```
Only `Brotli` is needed at build time (WeasyPrint uses it to decode the woff2).
