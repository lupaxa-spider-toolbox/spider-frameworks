# Reference

## Crawl Contract

Every template starts at `START_URL` and stays on that host. The host is
the `netloc` of the start URL (including port if you passed one).
Off-domain links are collected and not crawled. `www.example.com` and
`example.com` are different hosts.

1.   Normalize relative hrefs against the page URL. Skip `#`, `javascript:`,
     and `mailto:`. Drop URL fragments. Skip non-page path extensions:
     `.css`, `.js`, `.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`, `.pdf`,
     `.docx`, `.xlsx`.
2.   Fetch the URL. If the response is not HTML, skip it.
3.   Parse `<a href>` with BeautifulSoup (`html.parser`). Other tags are
     ignored.
4.   If the link’s host is set and differs from the start host, record it as
     external and do not crawl it.
5.   Otherwise enqueue the normalized URL if it has not been visited.
6.   Print visit / skip / error with `colored`. On finish, print visited
     count, external count, and the external URL list.

HTTP templates treat a response as HTML only when `Content-Type` contains
`text/html`. Selenium templates load the page in Chrome and skip when the
document does not look like HTML (same yellow skip line).

Default HTTP timeout is 10 seconds. Redirects are followed. Selenium waits
up to 10 seconds for `body`. Chrome runs headless (`--headless=new`) with
`--no-sandbox`, `--disable-dev-shm-usage`, and `--disable-gpu`.

Fetch failures on individual URLs print in red and do not abort the crawl.
Visited URLs that failed still count toward `Visited` because they were
claimed before the fetch.

Crawl state lives on a small object (visited set, external list, host,
user-agent, concurrency). There are no module-level crawl globals.

## What is Skipped

These hrefs never become same-host queue entries:

-   `#`, `javascript:`, `mailto:` prefixes
-   Fragment-only references
-   Paths ending in the excluded extensions above (checked on the raw href
    path and again after `urljoin`)

Same-host URLs that differ only by fragment collapse to one URL.
Query strings are kept: `/page?a=1` and `/page?a=2` are distinct.

## Timeouts and Browsers

| Template            | Fetch                                      | Timeout / wait       |
| ------------------- | ------------------------------------------ | -------------------- |
| `threadpool`        | Short-lived `httpx.Client` per GET         | 10 s HTTP            |
| `asyncio`           | Shared `httpx.AsyncClient`                 | 10 s HTTP            |
| `selenium`          | One Chrome driver, sequential queue        | 10 s wait for `body` |
| `selenium-threaded` | New Chrome driver per URL                  | 10 s wait for `body` |

If Chrome cannot start, sequential Selenium prints
`Failed to start Chrome: …` and exits non-zero. Threaded Selenium wraps
`ChromeDriverManager` failures the same way and must not leave drivers
running after Ctrl-C.

## Exit Codes

| Exit  | Meaning                                      |
| ----- | -------------------------------------------- |
| `0`   | Run finished (including “no further links”)  |
| `2`   | Bad CLI / missing or unparseable `START_URL` |
| `130` | Ctrl-C: close client / drivers, then exit    |

Selenium driver setup failure prints the error and exits non-zero (not
`2` unless the start URL itself was invalid).

## Template Dependencies

| Folder              | Runtime deps                                                 |
| ------------------- | ------------------------------------------------------------ |
| `threadpool`        | `httpx`, `beautifulsoup4`, `colored`                         |
| `asyncio`           | `httpx`, `beautifulsoup4`, `colored`                         |
| `selenium`          | `selenium`, `webdriver-manager`, `beautifulsoup4`, `colored` |
| `selenium-threaded` | `selenium`, `webdriver-manager`, `beautifulsoup4`, `colored` |

Install only the folder you are running. Root `pyproject.toml` `dev`
extras are for lint, tests, and MkDocs, not for crawling.

## Out of Scope for These Templates

The scripts do not read `robots.txt`, throttle requests, persist results,
render JavaScript on the HTTP templates, or switch Chrome for Firefox.
Those are changes you make after you copy a folder.
