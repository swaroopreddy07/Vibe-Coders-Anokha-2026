# adk/tools/scraper_tool.py
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from bs4 import BeautifulSoup
import traceback
import requests

# Common selectors to try to close cookie / language / overlay popups
CLOSE_SELECTORS = [
    "button[aria-label*='close']",
    "button[aria-label*='Close']",
    "button:has-text('Accept')",
    "button:has-text('I accept')",
    "button:has-text('Agree')",
    "button:has-text('OK')",
    "button:has-text('Close')",
    "button:has-text('Done')",
    "button:has-text('Got it')",
    "button:has-text('Allow cookies')",
    "button:has-text('Accept all')",
    "button.cookie-accept",
    ".cookie-consent button",
    ".cookie-banner button",
    ".consent-modal button",
    ".language-selector button",
    ".language-chooser button",
    ".close-modal",
    ".overlay-close",
    ".modal-close"
]

# Heuristic selectors where job content often lives (we'll try these in order)
JOB_CONTENT_SELECTORS = [
    "article",                       # many sites wrap job in article
    ".job-description",
    ".jobDescription",
    ".posting-body",
    ".job-posting",
    ".description",
    "#job-description",
    ".job-details",
    ".jd-section",
    "#job-content",
    ".content",
    "main"
]

def _try_close_popups(page):
    for sel in CLOSE_SELECTORS:
        try:
            elems = page.query_selector_all(sel)
            if elems:
                for e in elems:
                    try:
                        e.click(timeout=1000)
                    except Exception:
                        # ignore individual click failures
                        pass
        except Exception:
            pass

def scrape_job_url(url: str, headless: bool = False, timeout_ms: int = 30000) -> dict:
    """
    Try to load page, close common popups, and extract job region text.
    Returns dict:
      { text, html, snippet, source, http_status, error, content_selector_used }
    """
    pw_err = ""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=headless, args=["--disable-blink-features=AutomationControlled"])
            context = browser.new_context(
                user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"),
                viewport={"width": 1280, "height": 800}
            )
            page = context.new_page()
            response = page.goto(url, timeout=timeout_ms, wait_until="domcontentloaded")
            status = None
            if response:
                try:
                    status = response.status
                except Exception:
                    status = None

            # small wait for scripts to run
            page.wait_for_timeout(1000)

            # Attempt to close common popups / cookie banners
            _try_close_popups(page)
            # wait briefly after closing
            page.wait_for_timeout(800)

            # Try to find main job content using common selectors
            content_html = None
            selector_used = None
            for sel in JOB_CONTENT_SELECTORS:
                try:
                    handle = page.query_selector(sel)
                    if handle:
                        content_html = handle.inner_html()
                        selector_used = sel
                        break
                except Exception:
                    pass

            # If not found, try broad fallback: pick main/article or body text
            if content_html is None:
                try:
                    # sometimes content is in a div with "job" in class
                    handle = page.query_selector("div[class*='job']")
                    if handle:
                        content_html = handle.inner_html()
                        selector_used = "div[class*=job]"
                except Exception:
                    pass

            if content_html is None:
                # final fallback: full page html and body text
                html = page.content()
                try:
                    body_text = page.inner_text("body")
                except Exception:
                    # fallback to BeautifulSoup on html
                    soup = BeautifulSoup(html, "html.parser")
                    body_text = soup.get_text("\n")
                snippet = body_text[:1200]
                browser.close()
                return {
                    "text": body_text,
                    "html": html,
                    "snippet": snippet,
                    "source": "playwright",
                    "http_status": status,
                    "error": None,
                    "content_selector": None
                }

            # we have content_html from selector
            # convert to visible text
            soup = BeautifulSoup(content_html, "html.parser")
            content_text = soup.get_text("\n")
            html_full = page.content()
            snippet = content_text[:1200]
            browser.close()
            return {
                "text": content_text,
                "html": html_full,
                "snippet": snippet,
                "source": "playwright",
                "http_status": status,
                "error": None,
                "content_selector": selector_used
            }
    except PlaywrightTimeoutError as e:
        pw_err = f"playwright timeout: {e}"
    except Exception as e:
        pw_err = traceback.format_exc()

    # fallback to requests + BS4
    try:
        headers = {
            "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                           "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"),
            "Accept-Language": "en-US,en;q=0.9"
        }
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # try same content selectors on parsed HTML
        content_text = None
        selector_used = None
        for sel in JOB_CONTENT_SELECTORS:
            el = soup.select_one(sel)
            if el:
                content_text = el.get_text("\n")
                selector_used = sel
                break
        if content_text is None:
            # fallback: look for div with job in class
            el = soup.select_one("div[class*='job']")
            if el:
                content_text = el.get_text("\n")
                selector_used = "div[class*=job]"

        if content_text is None:
            content_text = soup.get_text("\n")[:1200]

        return {
            "text": content_text,
            "html": resp.text,
            "snippet": content_text[:1200],
            "source": "requests",
            "http_status": resp.status_code,
            "error": None,
            "content_selector": selector_used
        }
    except Exception as e2:
        req_err = traceback.format_exc()
        return {
            "text": "",
            "html": "",
            "snippet": "",
            "source": None,
            "http_status": None,
            "error": f"playwright_error:\n{pw_err}\n\nrequests_error:\n{req_err}",
            "content_selector": None
        }
