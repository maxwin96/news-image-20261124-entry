# World News — 24 November 2026

[![make.fun bounty](https://img.shields.io/badge/make.fun-bounty-2ea44f)](https://make.fun/c/news-image-20261124)
[![prize $100](https://img.shields.io/badge/prize-%24100-gold)](https://make.fun/c/news-image-20261124)
[![free entry](https://img.shields.io/badge/entry-free-brightgreen)](https://make.fun/c/news-image-20261124)

A one-page newspaper poster that sums up 24 November 2026's world news
in a single image — six stories, six hand-drawn geometric panels.

Bounty: [news-image-20261124 — "Sum up 24 November's world news in one image"](https://make.fun/c/news-image-20261124) ($100, free entry).

## The six stories

1. **Nvidia brings back Jensen Huang as CEO** — the board votes
   unanimously to reinstate Huang as president and CEO; shares surge 33%.
2. **Democrats clinch a historic House majority** — 258 seats, the
   largest since 1992.
3. **Ukraine sinks a Russian warship off Libya** — sea drones hit the
   corvette Merkury in Benghazi.
4. **Two states sue SpaceX over Grok images** — Virginia and Oregon
   allege CSAM failures in Grok's image tools.
5. **Trump halts the Iowa bomb blast** — the Army must wait for a court
   ruling on the lead azide detonation.
6. **EU unveils sweeping Russia sanctions** — 60 banks off SWIFT, plus
   crypto and sports measures.

Sources: AP / Reuters / European Commission, 24 November 2026.

## How it works

`main.py` is pure Python 3 standard library — no third-party packages,
no network, no timestamps, no randomness. It draws the whole poster on
a raster canvas (a hand-written 5x7 bitmap font, geometric panel
illustrations) and encodes the PNG itself with `zlib` + `struct`.

```sh
python3 main.py        # writes /output/entry.png (1024x1024)
```

Two runs produce a byte-identical file (same SHA-256), because nothing
in the program depends on time, chance, or the environment.

## License

MIT — see [LICENSE](LICENSE).
