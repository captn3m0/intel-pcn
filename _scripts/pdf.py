#!/usr/bin/env python3
"""
Resolve PCN URIs to direct PDF URLs.

Used as a one-off script to fix existing rows in pcn.db, and imported by init.py
to resolve URIs before inserting new PCNs.
"""

import sqlite3
import sys
from pathlib import Path
from urllib.parse import urlsplit

import requests

ALTERA_VIEWER_PREFIX = "https://docs.altera.com/v/u/"
ALTERA_PRETTY_URL_API = "https://docs.altera.com/internal/api/webapp/pretty-url/viewer"
ALTERA_DOC_URL_TEMPLATE = "https://docs.altera.com/api/khub/documents/{}/content"
TIMEOUT = 30


def _is_resolved(uri: str) -> bool:
    """True if uri already points at a direct PDF or anywhere on docs.altera.com."""
    if not uri:
        return False
    parts = urlsplit(uri)
    if parts.netloc == "docs.altera.com":
        return True
    if parts.path.lower().endswith(".pdf"):
        return True
    return False


def _final_response(uri: str, session: requests.Session) -> requests.Response | None:
    """Follow redirects via HEAD; fall back to streaming GET if HEAD isn't supported."""
    try:
        resp = session.head(uri, allow_redirects=True, timeout=TIMEOUT)
        if resp.status_code < 400:
            return resp
    except requests.RequestException as e:
        print(f"  HEAD failed for {uri}: {e}", file=sys.stderr)

    try:
        resp = session.get(uri, allow_redirects=True, timeout=TIMEOUT, stream=True)
        resp.close()
        return resp
    except requests.RequestException as e:
        print(f"  GET failed for {uri}: {e}", file=sys.stderr)
        return None


def _altera_document_id(pretty_url: str, session: requests.Session) -> str | None:
    try:
        resp = session.post(
            ALTERA_PRETTY_URL_API,
            json={"prettyUrl": pretty_url},
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
        return resp.json().get("documentId")
    except (requests.RequestException, ValueError) as e:
        print(f"  pretty-url API failed for {pretty_url}: {e}", file=sys.stderr)
        return None


def resolve_uri(uri: str, session: requests.Session) -> str:
    """Resolve a URI to a direct PDF URL. Returns the original URI if it can't resolve."""
    if not uri or _is_resolved(uri):
        return uri

    resp = _final_response(uri, session)
    if resp is None:
        return uri

    final_url = resp.url
    content_type = resp.headers.get("Content-Type", "").lower()

    if "application/pdf" in content_type:
        return final_url

    if final_url.startswith(ALTERA_VIEWER_PREFIX):
        path = urlsplit(final_url).path
        pretty_url = path[len("/v/u/"):]
        document_id = _altera_document_id(pretty_url, session)
        if document_id:
            return ALTERA_DOC_URL_TEMPLATE.format(document_id)

    print(f"  unresolved: {uri} → {final_url} (content-type: {content_type})", file=sys.stderr)
    return uri


def main():
    db_path = Path("pcn.db")
    if not db_path.exists():
        print(f"Error: {db_path} not found", file=sys.stderr)
        sys.exit(1)

    conn = sqlite3.connect(db_path)
    session = requests.Session()

    try:
        cursor = conn.execute(
            "SELECT contentid, clickableuri FROM pcns WHERE clickableuri != ''"
        )
        rows = [(cid, uri) for cid, uri in cursor.fetchall() if not _is_resolved(uri)]
        total = len(rows)
        print(f"Resolving {total} URIs...")

        changed = 0
        warnings = 0

        for i, (contentid, current_uri) in enumerate(rows, 1):
            resolved = resolve_uri(current_uri, session)
            if resolved != current_uri:
                conn.execute(
                    "UPDATE pcns SET clickableuri = ? WHERE contentid = ?",
                    (resolved, contentid),
                )
                changed += 1
            else:
                warnings += 1

            if i % 50 == 0:
                conn.commit()
                print(f"  {i}/{total} processed ({changed} changed, {warnings} unchanged)")

        conn.commit()
        print(f"Done: {changed}/{total} URIs resolved, {warnings} left unchanged")

    finally:
        conn.close()
        session.close()


if __name__ == "__main__":
    main()
