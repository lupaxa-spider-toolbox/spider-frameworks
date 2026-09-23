# Usage

Run the script from the template folder you picked. There is no unified
`--backend` CLI and no console script on the root package.

```bash
cd spiders/threadpool
python spider.py START_URL [--concurrency N] [--user-agent UA]
```

## HTTP and threaded Selenium

`threadpool`, `asyncio`, and `selenium-threaded` accept both optional flags:

```bash
python spider.py START_URL [--concurrency N] [--user-agent UA]
```

## Sequential Selenium

`selenium` uses one headless Chrome driver. It omits `--concurrency`:

```bash
python spider.py START_URL [--user-agent UA]
```

## START_URL

The first argument is required. A bare host or a scheme-less path gets an
`https://` prefix. A leading `//` plus a host gets an `https:` prefix.
After that, the value must be `http` or `https` with a host. Anything else
exits `2` with `START_URL must be a host or an http(s) URL`.

There is no hardcoded start URL in the scripts. `--help` prints the
parser help. The spider scripts do not take `--version` (that would collide
with the repo package version).

## --concurrency

Default is `10`. The value is the **per-page** fan-out: after a page is
parsed, up to that many newly discovered same-host links are fetched at
once (thread pool size, or the asyncio semaphore). It is not a global
cap on every in-flight request across the whole site.

`--concurrency` must be `>= 1` or the process prints
`concurrency must be >= 1` to stderr and exits `2`. Sequential Selenium
has no such flag: it walks a queue one URL at a time on one driver.

On `selenium-threaded`, each in-flight URL starts its own Chrome. A value
of `10` can mean ten browsers. Start at `2` or `3` on a laptop.

The threadpool template must not share one `httpx.Client` across workers.
Each fetch opens a short-lived client (or equivalent). The asyncio
template uses one `AsyncClient` for the run.

## --user-agent

Sent as the HTTP `User-Agent` header, or as Chrome’s `--user-agent=`
flag on the Selenium templates. Defaults are `Lupaxa-Spider-<Type>` with
title-cased folder words:

| Folder              | Default user-agent                |
| ------------------- | --------------------------------- |
| `threadpool`        | `Lupaxa-Spider-Threadpool`        |
| `asyncio`           | `Lupaxa-Spider-Asyncio`           |
| `selenium`          | `Lupaxa-Spider-Selenium`          |
| `selenium-threaded` | `Lupaxa-Spider-Selenium-Threaded` |

Override when a site expects a named research bot, or when you want logs
to show which experiment you ran.

## What the output means

Lines use `colored` (`Fore.green` / `yellow` / `cyan` / `red`).

| Colour | Typical text                      | Meaning                                                |
| ------ | --------------------------------- | ------------------------------------------------------ |
| Cyan   | `Starting with: …`                | Crawl is about to begin                                |
| Green  | `Visiting: …`                     | This URL was claimed and is being fetched              |
| Yellow | `Skipping: … (Not HTML)`          | Response was not HTML; links are not parsed            |
| Red    | `Error while crawling …`          | Timeout, HTTP error, or fetch exception; crawl goes on |
| Cyan   | `Crawling completed.` plus counts | Finished (or ran out of same-host links)               |

External URLs are listed after `External: N`, one per line, without colour.
They were recorded and not crawled.

Ctrl-C prints `Keyboard interrupt detected. Shutting down...`, closes
clients and Chrome drivers, and exits `130`.
