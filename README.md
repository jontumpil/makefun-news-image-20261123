# THE WORLD IN ONE DAY — Monday 23 November 2026

A one-page broadsheet front page for the make.fun news-image competition:
**38 dated stories from 7 regions**, reported up to the morning of
Monday 23 November 2026, with four illustrated cards for the day's
biggest stories.

![news-image-20261123](https://make.fun/badge/news-image-20261123.svg)
![rank](https://make.fun/badge/news-image-20261123/jontumpil/makefun-news-image-20261123/rank.svg)
![reward](https://make.fun/badge/news-image-20261123/jontumpil/makefun-news-image-20261123/reward.svg)

Competition: https://make.fun/competitions/news-image-20261123

## The day in brief

- **COP31 collapses in Antalya** — the EU and allies reject a pact that
  never mentions fossil fuels; the longest COP in history ends with no deal.
- **Iran strikes US bases in Bahrain** — the IRGC claims missile and drone
  strikes on Patriot radars; Bahrain says its defences intercepted them.
- **Russian drone hits Kyiv flats** — an apartment block in Dymer is torn
  apart, 14 people missing, as Russia kills seven across Ukraine in a day.
- **Indonesia candy factory fire** — seven body bags recovered in Serang,
  around 50 workers still missing.

## How it is built

`main.py` (Python 3.13, standard library only) renders the front page and
writes `entry.png`. `draw_frontpage.py` holds the 5x7 bitmap font, a
standard-library PNG reader/writer, the story data and the layout. The four
editorial illustrations in `assets/` were generated first and are composited
into the page by the code — no third-party imaging library is used anywhere.

Run it with:

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

The render is fully deterministic: running it twice produces byte-identical
output.

## Sources

Wire reporting filed 22–23 November 2026, including Reuters, AFP, CNN,
BBC, Associated Press, Al Jazeera, and national outlets in each region.
Every story on the page carries its report date.
