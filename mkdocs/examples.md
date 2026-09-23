# Examples

These commands use `example.com`. They are not run in CI. Crawl only hosts
you are allowed to fetch.

## Start With a Host

Omit the scheme. The script adds `https://`.

```bash
cd spiders/threadpool
python -m pip install -r requirements.txt
python spider.py example.com
```

That is the same as `python spider.py https://example.com`. A typical
successful run looks like:

```text
Starting with: https://example.com
Visiting: https://example.com
Crawling completed.
Visited: 1
External: 1
https://iana.org/domains/example
```

Green visit lines and the cyan summary are the happy path. If the start
page is not HTML you will see a yellow skip and `Visited: 1` with no
further same-host links.

## Set a User-Agent

```bash
python spider.py example.com --user-agent "MyResearchBot/1.0"
```

Use this when you want logs, access logs, or a site policy to show a
stable name. The string is sent on every fetch (HTTP header or Chrome
flag). Defaults when the flag is omitted:

| Folder              | Default user-agent                |
| ------------------- | --------------------------------- |
| `threadpool`        | `Lupaxa-Spider-Threadpool`        |
| `asyncio`           | `Lupaxa-Spider-Asyncio`           |
| `selenium`          | `Lupaxa-Spider-Selenium`          |
| `selenium-threaded` | `Lupaxa-Spider-Selenium-Threaded` |

## Limit Concurrency

`--concurrency` is the per-page fan-out (thread pool or asyncio
semaphore). Sequential Selenium has no such flag.

```bash
python spider.py example.com --concurrency 3
```

`3` is a reasonable laptop starting point for `threadpool` and `asyncio`.
For `selenium-threaded`, `3` means up to three Chrome processes after a
page’s links are discovered. Drop to `1` if you want browser fetches but
no parallel drivers (or use sequential `selenium` instead).

`--concurrency 0` or a negative value exits `2`.

## Stop With Ctrl-C

Ctrl-C stops enqueueing, closes HTTP clients and Chrome drivers, and
exits `130`. You should see `Keyboard interrupt detected. Shutting down...`
and then the process should exit. If a Selenium run is interrupted, check
Activity Monitor / Task Manager for leftover `chromedriver` or Chrome
processes — the templates are written to close drivers on interrupt, but
a killed `-9` will not run that path.

## Start Commands by Template

=== "threadpool"

    Static HTML, threads. Default `--concurrency` is 10.

    ```bash
    cd spiders/threadpool
    python -m pip install -r requirements.txt
    python spider.py example.com
    ```

=== "asyncio"

    Static HTML, asyncio. Same flags as threadpool.

    ```bash
    cd spiders/asyncio
    python -m pip install -r requirements.txt
    python spider.py example.com
    ```

=== "selenium"

    One headless Chrome. No `--concurrency`. First run may download
    ChromeDriver via `webdriver-manager`.

    ```bash
    cd spiders/selenium
    python -m pip install -r requirements.txt
    python spider.py example.com
    ```

=== "selenium-threaded"

    New Chrome per URL. Keep concurrency modest.

    ```bash
    cd spiders/selenium-threaded
    python -m pip install -r requirements.txt
    python spider.py example.com --concurrency 3
    ```
