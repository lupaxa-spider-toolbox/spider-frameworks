# Spider Frameworks

A collection of web-spider templates. Clone the repository, pick one folder
under `spiders/`, and use that script as a starting point.

This is not an installable crawler library. Nobody is expected to
`pip install` a crawler API or run a unified `--backend` CLI.

Requires Python 3.10+.

## What you get

Each `spiders/<name>/` folder is a complete skeleton: one `spider.py` and a
`requirements.txt` for that template only. Helpers (URL normalisation, link
filtering, coloured printing) are copied on purpose so you can take one
folder and delete the rest of the repo.

All four templates share the same crawl contract: start at one URL, stay
on that host, collect off-domain links, and print a short summary. They
differ only in how they fetch pages and how they fan out work.

## Templates

| Folder              | Fetch            | Concurrency                          | Use when                                              |
| ------------------- | ---------------- | ------------------------------------ | ----------------------------------------------------- |
| `threadpool`        | `httpx`          | `ThreadPoolExecutor`                 | Static HTML, you want threads and a simple script     |
| `asyncio`           | `httpx`          | asyncio + semaphore                  | Static HTML, you prefer `async` / `await`             |
| `selenium`          | one Chrome       | sequential queue                     | Pages need a real browser; keep one driver            |
| `selenium-threaded` | new Chrome / URL | `ThreadPoolExecutor`                 | Pages need a browser and you accept a driver per URL  |

The HTTP templates do not run JavaScript. If the links you care about appear
only after client-side rendering, use a Selenium template.

## What this collection does not do

These skeletons are starting points, not a production crawler. They do not
implement `robots.txt`, rate limits, politeness delays, stealth, or writing
results to a file. CI does not crawl the network or start Chrome.

The root `pyproject.toml` exists so makefile-skills CI and version bumps
have a project. It does not export crawl helpers or install console scripts.
