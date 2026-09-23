# Getting started

## Requirements

- Python 3.10 or newer
- A start host or URL you are allowed to crawl
- A virtual environment is recommended (`python3 -m venv .venv`)
- Chrome, for `selenium` and `selenium-threaded`

The Selenium templates pull a matching ChromeDriver through
`webdriver-manager` on first run. You do not download a driver by hand, but
Chrome itself must already be installed.

## Choose a template

Start with `threadpool` unless you already know you need something else.

-   **`threadpool`** — default for static HTML. Each fetch uses a short-lived
    `httpx` client (one `Client` is not shared across threads).
-   **`asyncio`** — same HTTP stack, one `AsyncClient` for the run, a
    semaphore for `--concurrency`.
-   **`selenium`** — one headless Chrome, one URL at a time. Lowest load on
    the machine; slowest crawl.
-   **`selenium-threaded`** — a new headless Chrome per URL. Faster on JS
    sites, heavier on RAM and CPU. Keep `--concurrency` low until you see
    how many browsers your machine can hold.

## Pick a folder

Clone the repository, then work in one folder only:

```bash
git clone git@github.com:lupaxa-spider-toolbox/spider-frameworks.git
cd spider-frameworks/spiders/threadpool
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1`.

Each `spiders/<name>/` directory is self-contained (`spider.py` plus
`requirements.txt`). Copy that folder out if you want to delete the rest
of the repo. Do not import crawl helpers from another template folder.

## First run

```bash
python spider.py https://example.com
```

A host without a scheme is treated as `https://`:

```bash
python spider.py example.com
```

You should see a cyan `Starting with:` line, green `Visiting:` lines as
pages are fetched, then a cyan summary (`Crawling completed.`, visited
count, external count, then the external URL list). Yellow means a
non-HTML response was skipped. Red means that URL failed; the crawl
continues.

!!! note "example.com"
    Docs commands use `example.com`. They are not run in CI. Crawl only
    hosts you are allowed to fetch.

## If the first run fails

| Symptom                                         | What to check                                                      |
| ----------------------------------------------- | ------------------------------------------------------------------ |
| `START_URL must be a host or an http(s) URL`    | Empty string or a value that still has no host after `https://`    |
| `concurrency must be >= 1`                      | Pass `--concurrency` 1 or more (not on sequential Selenium)        |
| `Failed to start Chrome` / driver errors        | Chrome installed; retry so `webdriver-manager` can fetch a driver  |
| Immediate yellow `Skipping: … (Not HTML)`       | The start URL did not return `text/html`                           |
| Import errors for `httpx` / `selenium`          | You installed a different folder’s `requirements.txt`              |

See [Usage](usage.md) for flags and [Examples](examples.md) for recipes.

## Local documentation site

Site Markdown lives in `mkdocs/` (not GitHub’s special `docs/` directory).
From the repository root:

```bash
make init
make python-install-dev
make mkdocs-serve
```

Published docs: <https://spider-frameworks.thelupaxaproject.org/>.
