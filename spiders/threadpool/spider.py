"""Thread-pool spider template using httpx."""

from __future__ import annotations

import argparse
import sys
import threading
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from urllib.parse import urljoin, urlparse, urlunparse

import httpx
from bs4 import BeautifulSoup
from colored import Fore, Style

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
DEFAULT_TIMEOUT = 10.0
DEFAULT_USER_AGENT = "Lupaxa-Spider-Threadpool"
DEFAULT_CONCURRENCY = 10


@dataclass
class CrawlState:
    host: str
    user_agent: str
    concurrency: int
    visited: set[str] = field(default_factory=set)
    external: list[str] = field(default_factory=list)
    lock: threading.Lock = field(default_factory=threading.Lock)


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
    parser = argparse.ArgumentParser(description="Crawl a site with httpx and a thread pool.")
    parser.add_argument(
        "start_url",
        type=require_http_url,
        help="Start URL (https:// added if the scheme is omitted)",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=DEFAULT_CONCURRENCY,
        help="Per-page thread pool fan-out (default: 10)",
    )
    parser.add_argument(
        "--user-agent",
        default=DEFAULT_USER_AGENT,
        help=f"User-Agent header (default: {DEFAULT_USER_AGENT})",
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


def claim_url(state: CrawlState, url: str) -> bool:
    with state.lock:
        if url in state.visited:
            return False
        state.visited.add(url)
        return True


def record_external(state: CrawlState, url: str) -> None:
    with state.lock:
        if url not in state.external:
            state.external.append(url)


def fetch_html(url: str, user_agent: str) -> str | None:
    headers = {"User-Agent": user_agent}
    try:
        with httpx.Client(
            timeout=DEFAULT_TIMEOUT, follow_redirects=True, headers=headers
        ) as client:
            response = client.get(url)
            response.raise_for_status()
    except httpx.HTTPError as exc:
        print(f"{RED}Error while crawling {url}: {exc}{RESET}")
        return None
    content_type = response.headers.get("content-type", "")
    if "text/html" not in content_type.lower():
        print(f"{YELLOW}Skipping: {url} (Not HTML){RESET}")
        return None
    return response.text


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


def crawl_from(state: CrawlState, url: str) -> None:
    normalized = normalize_url(url, url)
    if not claim_url(state, normalized):
        return
    print(f"{GREEN}Visiting: {normalized}{RESET}")
    html = fetch_html(normalized, state.user_agent)
    if html is None:
        return
    new_links = [
        link for link in discover_links(state, normalized, html) if link not in state.visited
    ]
    if not new_links:
        return
    with ThreadPoolExecutor(max_workers=state.concurrency) as pool:
        futures = [pool.submit(crawl_from, state, link) for link in new_links]
        for future in futures:
            future.result()


def print_summary(state: CrawlState) -> None:
    print(f"{CYAN}Crawling completed.{RESET}")
    print(f"{CYAN}Visited: {len(state.visited)}{RESET}")
    print(f"{CYAN}External: {len(state.external)}{RESET}")
    for url in state.external:
        print(url)


def crawl_website(start_url: str, concurrency: int, user_agent: str) -> None:
    host = urlparse(start_url).netloc
    state = CrawlState(host=host, user_agent=user_agent, concurrency=concurrency)
    print(f"{CYAN}Starting with: {start_url}{RESET}")
    crawl_from(state, start_url)
    print_summary(state)


def main() -> int:
    args = build_parser().parse_args()
    if args.concurrency < 1:
        print("concurrency must be >= 1", file=sys.stderr)
        return 2
    try:
        crawl_website(args.start_url, args.concurrency, args.user_agent)
    except KeyboardInterrupt:
        print("Keyboard interrupt detected. Shutting down...")
        return 130
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
