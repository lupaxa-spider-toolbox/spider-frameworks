<p align="center">
  <a href="https://github.com/lupaxa-spider-toolbox">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/organisations/spider-toolbox/readme-logo.png" alt="Spider Toolbox" />
  </a>
</p>

<h1 align="center">Spider Frameworks</h1>

A collection of web-spider templates. Clone the repository, pick one folder
under `spiders/`, and use that script as a starting point. This is not an
installable crawler library. There is no unified `--backend` CLI. Requires
Python 3.10+.

Each `spiders/<name>/` folder is one `spider.py` and its own
`requirements.txt`. Copy that folder out if you want to leave the rest of
the repo behind. All four templates start at one URL, stay on that host,
collect off-domain links without crawling them, and print a short summary.
They differ in how they fetch pages.

## Pick a template

Start with `threadpool` unless the pages need a browser.

| Folder              | Fetch            | Concurrency          | Use when                                             |
| ------------------- | ---------------- | -------------------- | ---------------------------------------------------- |
| `threadpool`        | `httpx`          | `ThreadPoolExecutor` | Static HTML, you want threads and a simple script    |
| `asyncio`           | `httpx`          | asyncio + semaphore  | Static HTML, you prefer `async` / `await`            |
| `selenium`          | one Chrome       | sequential queue     | Pages need a real browser; keep one driver           |
| `selenium-threaded` | new Chrome / URL | `ThreadPoolExecutor` | Pages need a browser and you accept a driver per URL |

The HTTP templates do not run JavaScript. Selenium templates need Chrome
installed. `webdriver-manager` fetches a matching ChromeDriver on first run.

## Run a template

```bash
cd spiders/threadpool
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python spider.py https://example.com
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1`.

A host without a scheme is treated as `https://`. A leading `//` plus a
host becomes `https:` plus that host. Anything else exits `2` with
`START_URL must be a host or an http(s) URL`.

> **Note:** These commands use `example.com`. Crawl only hosts you are
> allowed to fetch.

`--concurrency` defaults to `10` on `threadpool`, `asyncio`, and
`selenium-threaded`. After a page is parsed, up to that many newly
discovered same-host links are fetched at once. It is not a cap on the
whole site. A value below `1` exits `2` with `concurrency must be >= 1`.
Sequential `selenium` has no `--concurrency` flag. On `selenium-threaded`,
start at `2` or `3`: each in-flight URL opens its own Chrome.
`threadpool` opens a short-lived `httpx` client per fetch. `asyncio` uses
one client for the run.

`--user-agent` defaults to `Lupaxa-Spider-<Type>`:
`Lupaxa-Spider-Threadpool`, `Lupaxa-Spider-Asyncio`,
`Lupaxa-Spider-Selenium`, or `Lupaxa-Spider-Selenium-Threaded`.

Cyan lines mark the start and the summary. Green is a visit, yellow is a
non-HTML skip, and red is a fetch error that does not stop the crawl.
External URLs are listed at the end and are not fetched.

These skeletons do not implement `robots.txt`, rate limits, politeness
delays, stealth, or writing results to a file.

## How a crawl works

The host is the start URL’s netloc, including the port. `www.example.com`
and `example.com` are different hosts. Off-domain links are recorded and
not fetched.

Only `<a href>` links are followed. The script skips `#`, `javascript:`,
and `mailto:`, drops fragments, and skips paths ending in `.css`, `.js`,
`.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`, `.pdf`, `.docx`, or `.xlsx`.
Query strings stay, so `/page?a=1` and `/page?a=2` are different pages.

HTTP templates treat a response as HTML only when `Content-Type` contains
`text/html`. The timeout is 10 seconds, and redirects are followed.
Selenium waits up to 10 seconds for `body` in headless Chrome. A failed
URL prints in red and the crawl continues. That URL still counts as
visited.

Ctrl-C prints `Keyboard interrupt detected. Shutting down...`, closes
clients and Chrome, and exits `130`. A `kill -9` skips that cleanup, so
check for leftover Chrome or `chromedriver` processes.

| Exit  | Meaning                                          |
| ----- | ------------------------------------------------ |
| `0`   | Finished, including when no further links remain |
| `2`   | Bad arguments, or a start value with no host     |
| `130` | Ctrl-C                                           |

## If the first run fails

| Symptom                                      | What to check                                                         |
| -------------------------------------------- | --------------------------------------------------------------------- |
| `START_URL must be a host or an http(s) URL` | The argument was empty, or still had no host after `https://`         |
| `concurrency must be >= 1`                   | Pass `--concurrency` of 1 or more (not on sequential Selenium)        |
| `Failed to start Chrome`                     | Chrome is installed; retry so `webdriver-manager` can fetch a driver  |
| Yellow `Skipping: … (Not HTML)`              | The start URL did not return HTML                                     |
| Import errors for `httpx` or `selenium`      | That folder’s `requirements.txt` was not the one you installed        |

<a href="https://github.com/the-lupaxa-project">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/components/footer-for-child-orgs.svg" alt="The Lupaxa Project Footer" width="100%" />
</a>
