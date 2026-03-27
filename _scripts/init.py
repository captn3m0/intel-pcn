#!/usr/bin/env python3
"""
Intel PCN fetcher and database updater.
Fetches PCNs from Intel's search API for the last 7 days and updates the SQLite database.
"""

import sqlite3
import requests
import json
import datetime
import curl_cffi
from pathlib import Path
from typing import Dict, Any, List


def open_database() -> sqlite3.Connection:
    """Open (or create) the PCN database."""
    db_path = Path("pcn.db")
    conn = sqlite3.connect(db_path)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS pcns (
            contentid INTEGER PRIMARY KEY,
            systitle TEXT,
            sysurihash TEXT,
            createddate INTEGER,
            urihash TEXT,
            binaryfilesize TEXT,
            lastmodifieddt INTEGER,
            sysuri TEXT,
            docexpiredate INTEGER,
            description TEXT,
            permanentid TEXT,
            metadataclassification TEXT,
            title TEXT,
            sourcetype TEXT,
            docuniqueid TEXT,
            clickableuri TEXT,
            type TEXT,
            emtcontenttype_en TEXT,
            syssourcetype TEXT,
            version TEXT,
            filetype TEXT,
            downloadtype TEXT,
            sysclickableuri TEXT,
            sysfiletype TEXT,
            secondaryurl TEXT,
            uri TEXT,
            issoftware TEXT
        )
    """)

    conn.commit()
    return conn


def normalize_value(value: Any) -> str:
    """Normalize a value - if it's a single-item array, return the first item."""
    if isinstance(value, list) and len(value) == 1:
        return str(value[0])
    return str(value) if value is not None else ""


def insert_pcn(conn: sqlite3.Connection, raw_pcn: Dict[str, Any]) -> None:
    """Insert a PCN record into the database."""
    normalized = {key: normalize_value(value) for key, value in raw_pcn.items()}

    conn.execute("""
        INSERT OR REPLACE INTO pcns (
            systitle, sysurihash, createddate, urihash, binaryfilesize,
            lastmodifieddt, sysuri, docexpiredate, contentid, description,
            permanentid, metadataclassification, title, sourcetype, docuniqueid,
            clickableuri, type, emtcontenttype_en, syssourcetype, version,
            filetype, downloadtype, sysclickableuri, sysfiletype, secondaryurl,
            uri, issoftware
        ) VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
    """, (
        normalized.get("systitle", ""),
        normalized.get("sysurihash", ""),
        normalized.get("createddate", 0),
        normalized.get("urihash", ""),
        normalized.get("binaryfilesize", ""),
        normalized.get("lastmodifieddt", 0),
        normalized.get("sysuri", ""),
        normalized.get("docexpiredate", 0),
        normalized.get("contentid", 0),
        normalized.get("description", ""),
        normalized.get("permanentid", ""),
        normalized.get("metadataclassification", ""),
        normalized.get("title", ""),
        normalized.get("sourcetype", ""),
        normalized.get("docuniqueid", ""),
        normalized.get("clickableuri", ""),
        normalized.get("type", ""),
        normalized.get("emtcontenttype_en", ""),
        normalized.get("syssourcetype", ""),
        normalized.get("version", ""),
        normalized.get("filetype", ""),
        normalized.get("downloadtype", ""),
        normalized.get("sysclickableuri", ""),
        normalized.get("sysfiletype", ""),
        normalized.get("secondaryurl", ""),
        normalized.get("uri", ""),
        normalized.get("issoftware", "")
    ))


def fetch_pcns(token: str, start_date: str) -> List[Dict[str, Any]]:
    """Fetch all PCNs from Intel's API since start_date using pagination."""
    url = "https://intelcorporationproductione78n25s6.org.coveo.com/rest/search"

    headers = {
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {token}",
    }

    all_pcns = []
    first_result = 0
    results_per_page = 100

    while True:
        payload = {
            "aq": f"(@localecode==en_US) (@synapticaguid==(\"etm-b6e7ce4fd9e144048c526ca9c64587d8\",\"etm-fb506128738d478fbd7c7c7992367c48\",\"etm-432664f7da684e6fb3347b2fc528a3c7\",\"etm-53e34c9049b54c69aec7931e09591a7d\")) (@lastmodifieddt>={start_date})",
            "firstResult": first_result,
            "numberOfResults": results_per_page,
            "locale": "en",
            "sortCriteria": "@lastmodifieddt descending",
            "fieldsToInclude": ["title", "description", "clickableuri", "docuniqueid", "lastmodifieddt", "filetype", "binaryfilesize", "contenttype", "keywords", "version", "secondaryurl", "issoftware", "docexpiredate", "softwarearchivaldate", "createddate", "metadataclassification", "includes", "emtcontenttype_en", "allVersions", "downloadtype", "sysuri", "type", "contentid"],
            "facets": [],
            "pipeline": "rdc-technicallibrary",
            "searchHub": "rdc-technicallibrary",
            "queryFunctions": []
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()

            data = response.json()
            results = data.get("results", [])

            if not results:
                break

            for result in results:
                if "raw" in result:
                    all_pcns.append(result["raw"])

            if len(results) < results_per_page:
                break

            first_result += results_per_page

        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            break
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            break

    return all_pcns

def get_token() -> str:
    BROWSER_CODE = "safari18_4_ios"
    TOKEN_URL = "https://www.intel.com/libs/intel/services/replatform?searchHub=rdc-technicallibrary"
    body = curl_cffi.get(TOKEN_URL, impersonate=BROWSER_CODE).json()
    return body['token']

def main():
    """Main function to fetch recent PCNs and update database."""
    print("Updating Intel PCN database...")

    conn = open_database()
    auth_token = get_token()

    start_date = (datetime.date.today() - datetime.timedelta(days=30)).strftime("%Y/%m/%d")
    print(f"Fetching PCNs since {start_date}...")

    try:
        cursor = conn.execute("SELECT COUNT(*) FROM pcns")
        count_before = cursor.fetchone()[0]

        pcns = fetch_pcns(auth_token, start_date)
        print(f"Fetched {len(pcns)} PCNs from the last 30 days")

        for i, pcn in enumerate(pcns, 1):
            insert_pcn(conn, pcn)
            if i % 50 == 0:
                conn.commit()

        conn.commit()

        cursor = conn.execute("SELECT COUNT(*) FROM pcns")
        count_after = cursor.fetchone()[0]
        print(f"Database updated: {count_before} → {count_after} PCNs ({count_after - count_before} new)")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
