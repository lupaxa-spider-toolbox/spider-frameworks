"""Sequential Selenium spider template (one headless Chrome driver)."""

from __future__ import annotations

import argparse
from collections.abc import Iterable
from dataclasses import dataclass, field
from urllib.parse import urljoin, urlparse, urlunparse

from bs4 import BeautifulSoup
from colored import Fore, Style
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

GREEN: str = Fore.green
YELLOW: str = Fore.yellow
CYAN: str = Fore.cyan
RED: str = Fore.red
RESET: str = Style.reset

IGNORED_PREFIXES = ("#", "javascript:", "mailto:")
EXCLUDE_EXTENSIONS = (
    ".css",
    ".js",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".pdf",
    ".docx",
    ".xlsx",
)
DEFAULT_WAIT = 10.0
DEFAULT_USER_AGENT = "Lupaxa-Spider-Selenium"


@dataclass
class CrawlState:
    host: str
    user_agent: str
    visited: set[str] = field(default_factory=set)
    external: list[str] = field(default_factory=list)


def require_http_url(value: str) -> str:
    stripped = value.strip()
    parsed = urlparse(stripped)
    if parsed.scheme not in {"http", "https"}:
        stripped = f"https:{stripped}" if stripped.startswith("//") else f"https://{stripped}"
        parsed = urlparse(stripped)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise argparse.ArgumentTypeError("START_URL must be a host or an http(s) URL")
    return stripped


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Crawl a site with one headless Chrome driver.")
    parser.add_argument(
        "start_url",
        type=require_http_url,
        help="Start URL (https:// added if the scheme is omitted)",
    )
    parser.add_argument(
        "--user-agent",
        default=DEFAULT_USER_AGENT,
        help=f"Chrome user-agent (default: {DEFAULT_USER_AGENT})",
    )
    return parser


def normalize_url(url: str, base_url: str) -> str:
    joined = urljoin(base_url, url)
    parsed = urlparse(joined)
    return urlunparse(parsed._replace(fragment=""))


def is_excluded_path(path: str) -> bool:
    lower = path.lower()
    return any(lower.endswith(ext) for ext in EXCLUDE_EXTENSIONS)


def iter_hrefs(html: str) -> Iterable[str]:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.find_all("a"):
        href = tag.get("href")
        if isinstance(href, str) and href:
            yield href


def record_external(state: CrawlState, url: str) -> None:
    if url not in state.external:
        state.external.append(url)


def make_driver(user_agent: str) -> webdriver.Chrome:
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument(f"--user-agent={user_agent}")
    try:
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)
    except Exception as exc:
        raise WebDriverException(str(exc)) from exc


def fetch_html(driver: webdriver.Chrome, url: str) -> str | None:
    try:
        driver.get(url)
        content_type = driver.execute_script("return document.contentType")
        if not isinstance(content_type, str) or not content_type.startswith("text/html"):
            print(f"{YELLOW}Skipping: {url} (Not HTML){RESET}")
            return None
        wait = WebDriverWait(driver, DEFAULT_WAIT)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    except WebDriverException as exc:
        print(f"{RED}Error while crawling {url}: {exc}{RESET}")
        return None
    return driver.page_source


def discover_links(state: CrawlState, page_url: str, html: str) -> list[str]:
    found: list[str] = []
    for href in iter_hrefs(html):
        if any(href.startswith(prefix) for prefix in IGNORED_PREFIXES):
            continue
        parsed = urlparse(href)
        if parsed.fragment and not parsed.path and not parsed.netloc:
            continue
        if is_excluded_path(parsed.path):
            continue
        absolute = normalize_url(href, page_url)
        abs_parsed = urlparse(absolute)
        if is_excluded_path(abs_parsed.path):
            continue
        if abs_parsed.netloc and abs_parsed.netloc != state.host:
            record_external(state, absolute)
            continue
        found.append(absolute)
    return found


def print_summary(state: CrawlState) -> None:
    print(f"{CYAN}Crawling completed.{RESET}")
    print(f"{CYAN}Visited: {len(state.visited)}{RESET}")
    print(f"{CYAN}External: {len(state.external)}{RESET}")
    for url in state.external:
        print(url)


def crawl_website(start_url: str, user_agent: str) -> int:
    host = urlparse(start_url).netloc
    state = CrawlState(host=host, user_agent=user_agent)
    print(f"{CYAN}Starting with: {start_url}{RESET}")
    try:
        driver = make_driver(user_agent)
    except WebDriverException as exc:
        print(f"{RED}Failed to start Chrome: {exc}{RESET}")
        return 1
    queue = [normalize_url(start_url, start_url)]
    interrupted = False
    try:
        while queue:
            current = queue.pop(0)
            if current in state.visited:
                continue
            state.visited.add(current)
            print(f"{GREEN}Visiting: {current}{RESET}")
            html = fetch_html(driver, current)
            if html is None:
                continue
            for link in discover_links(state, current, html):
                if link not in state.visited and link not in queue:
                    queue.append(link)
    except KeyboardInterrupt:
        print("Keyboard interrupt detected. Shutting down...")
        interrupted = True
    finally:
        driver.quit()
    if interrupted:
        return 130
    print_summary(state)
    return 0


def main() -> int:
    args = build_parser().parse_args()
    try:
        return crawl_website(args.start_url, args.user_agent)
    except KeyboardInterrupt:
        print("Keyboard interrupt detected. Shutting down...")
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
