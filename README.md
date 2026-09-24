<p align="center">
  <a href="https://github.com/lupaxa-spider-toolbox">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/organisations/spider-toolbox/readme-logo.png" alt="Spider Toolbox" />
  </a>
</p>

<h1 align="center">Spider Frameworks</h1>

A collection of web-spider templates. Clone the repository, pick one folder
under `spiders/`, and use that script as a starting point. This is not an
installable crawler library. There is no unified `--backend` CLI.

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

A host without a scheme is treated as `https://`.

> **Note:** These commands use `example.com`. Crawl only hosts you are
> allowed to fetch.

`--concurrency` defaults to `10` on `threadpool`, `asyncio`, and
`selenium-threaded`. After a page is parsed, up to that many newly
discovered same-host links are fetched at once. Sequential `selenium` has
no `--concurrency` flag. On `selenium-threaded`, start at `2` or `3`: each
in-flight URL opens its own Chrome.

`--user-agent` defaults to `Lupaxa-Spider-<Type>`:
`Lupaxa-Spider-Threadpool`, `Lupaxa-Spider-Asyncio`,
`Lupaxa-Spider-Selenium`, or `Lupaxa-Spider-Selenium-Threaded`.

Cyan lines mark the start and the summary. Green is a visit, yellow is a
non-HTML skip, and red is a fetch error that does not stop the crawl.
External URLs are listed at the end and are not fetched.

These skeletons do not implement `robots.txt`, rate limits, politeness
delays, stealth, or writing results to a file.

## Documentation

Online documentation:

[https://spider-frameworks.thelupaxaproject.org/](https://spider-frameworks.thelupaxaproject.org/)

Serve the docs locally:

```bash
make init
make python-install-dev
make mkdocs-serve
```

<a href="https://github.com/the-lupaxa-project">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/components/footer-for-child-orgs.svg" alt="The Lupaxa Project Footer" width="100%" />
</a>
