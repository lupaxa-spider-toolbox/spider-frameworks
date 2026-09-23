<p align="center">
  <a href="https://github.com/lupaxa-spider-toolbox">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/organisations/spider-toolbox/readme-logo.png" alt="Spider Toolbox" />
  </a>
</p>

<h1 align="center">Spider Frameworks</h1>

A collection of web-spider templates. Clone the repository, pick one folder
under `spiders/`, and use that script as a starting point. This is not an
installable crawler library.

Requires Python 3.10+.

## Pick a template

- `threadpool` — `httpx` plus a thread pool
- `asyncio` — `httpx` plus asyncio
- `selenium` — one headless Chrome, sequential
- `selenium-threaded` — a new Chrome driver per URL

## Run a template

```bash
cd spiders/threadpool
python -m pip install -r requirements.txt
python spider.py https://example.com
```

A host without a scheme is treated as `https://`. Optional flags:
`--concurrency` (not on sequential Selenium) and `--user-agent`
(default `Lupaxa-Spider-<Type>`, e.g. `Lupaxa-Spider-Threadpool`).

## Documentation

Site pages live in `mkdocs/` and publish to
<https://spider-frameworks.thelupaxaproject.org/>.

```bash
make init
make python-install-dev
make mkdocs-serve
```

Recipes:

- [Start With a Host](https://spider-frameworks.thelupaxaproject.org/examples/#start-with-a-host)
- [Set a User-Agent](https://spider-frameworks.thelupaxaproject.org/examples/#set-a-user-agent)
- [Limit Concurrency](https://spider-frameworks.thelupaxaproject.org/examples/#limit-concurrency)
- [Stop With Ctrl-C](https://spider-frameworks.thelupaxaproject.org/examples/#stop-with-ctrl-c)
