# Monday 23 November 2026 — The World in One Day: 40 dated stories, 7 regions: Huang returns to Nvidia; Ukraine hits Russian ships off Libya; COP31 ends with no deal

[![make.fun · news-image-20261123](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![rank](https://make.fun/badge/news-image-20261123/jontumpil/makefun-news-image-20261123/rank.svg)](https://make.fun/bounty/news-image-20261123/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![reward](https://make.fun/badge/news-image-20261123/jontumpil/makefun-news-image-20261123/reward.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)

Competition: https://make.fun/bounty/news-image-20261123

One newspaper front page summing up the full day of Monday 23 November
2026: 40 dated stories from 7 regions, four of them illustrated, and a
DATE CHECK box stating that every story is dated 23 November 2026.

## The day in brief

- **Huang returns to Nvidia.** Eleven days after resigning, Jensen Huang
  is reinstated as chief executive; Nvidia shares jump 33% and Wall
  Street posts one of its best days in months.
- **Ukraine hits Russian ships off Libya.** Zelenskyy says Ukrainian sea
  drones struck two Russian ships in the port of Benghazi, taking the
  war far beyond Europe's borders.
- **COP31 ends with no deal.** The longest UN climate talks in history
  close in Antalya without agreement, split over fossil fuels and money.
- **Mexico captures "El Chapo Isidro".** Special forces seize the FBI
  most-wanted fugitive Fausto Isidro Meza Flores in Sinaloa; 16
  suspected cartel gunmen are killed.

## How it is built

- `main.py` — standard library only. Reads `MAKEFUN_OUTPUT_DIR`
  (default `/output`), calls `draw_frontpage.build`, writes `entry.png`.
- `draw_frontpage.py` — standard library only (struct, zlib, os). Holds
  a hand-drawn 5x7 bitmap font, an RGB canvas, a PNG reader and writer,
  all 40 stories as literals, and the front-page layout. Deterministic:
  fixed iteration order, fixed zlib level, no clock, no randomness.
- `assets/` — four editorial illustrations (`nvidia.png`,
  `benghazi.png`, `cop31.png`, `sinaloa.png`) composited by the renderer
  into the four top-story cards. No third-party library is used by the
  code that is graded.

## Run it

```
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Two runs write byte-identical `entry.png` files (1024x1024, under 1 MiB).

## Sources

Every story is dated Monday 23 November 2026. Stories tagged CONFIRMED
happened on 23 November; stories tagged REPORTED were first widely
reported on 23 November. Main sources: Reuters, AP, CBS, Al Jazeera,
BBC, UNRWA, NEMA, Meduza, EU Commission, Just Security.

Date discipline: stories whose original date could not be verified as
23 November 2026 were left out, even when they sounded like that day's
news — for example the Trump–Putin–Xi summit in Shenzhen, which took
place on 19 November, and the Miley Cyrus wedding of 21 November.
