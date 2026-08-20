#!/usr/bin/env python3
"""
Extract all AWX/AAP Job Templates and their configured 'limit' values.
"""

import argparse
import os
import sys
from typing import Optional

import requests
from requests.auth import HTTPBasicAuth

# Disable SSL warnings if you use self-signed certs (optional)
# import urllib3
# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_all_job_templates(
    base_url: str,
    token: Optional[str] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
    verify_ssl: bool = True,
    page_size: int = 100,
) -> list[dict]:
    """
    Fetch all job templates from AWX, handling pagination.
    Returns a list of dicts with the relevant fields.
    """
    url = f"{base_url.rstrip('/')}/api/v2/job_templates/"
    headers = {"Content-Type": "application/json"}
    auth = None

    if token:
        headers["Authorization"] = f"Bearer {token}"
    elif username and password:
        auth = HTTPBasicAuth(username, password)
    else:
        raise ValueError("Provide either a token or username + password")

    results = []
    params = {"page_size": page_size}

    while url:
        resp = requests.get(
            url,
            headers=headers,
            auth=auth,
            params=params if "?" not in url else None,  # params only on first request
            verify=verify_ssl,
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()

        for jt in data.get("results", []):
            results.append(
                {
                    "id": jt.get("id"),
                    "name": jt.get("name"),
                    "limit": jt.get("limit") or "",          # empty string if not set
                    "ask_limit_on_launch": jt.get("ask_limit_on_launch", False),
                    "inventory": jt.get("inventory"),
                    "project": jt.get("project"),
                    "playbook": jt.get("playbook"),
                    "organization": jt.get("summary_fields", {})
                    .get("organization", {})
                    .get("name"),
                }
            )

        url = data.get("next")  # next page URL (already includes page_size)
        params = None           # don't re-apply page_size on subsequent pages

    return results

def main():
    parser = argparse.ArgumentParser(
        description="List all AWX/AAP job templates and their limit settings"
    )
    parser.add_argument(
        "--url",
        default=os.getenv("AWX_URL", "https://awx.example.com"),
        help="AWX base URL (or set AWX_URL env var)",
    )
    parser.add_argument(
        "--token",
        default=os.getenv("AWX_TOKEN"),
        help="OAuth2 / Personal Access Token (preferred). Or set AWX_TOKEN",
    )
    parser.add_argument(
        "--username",
        default=os.getenv("AWX_USERNAME"),
        help="Username (if not using token)",
    )
    parser.add_argument(
        "--password",
        default=os.getenv("AWX_PASSWORD"),
        help="Password (if not using token)",
    )
    parser.add_argument(
        "--insecure",
        action="store_true",
        help="Disable SSL certificate verification",
    )
    parser.add_argument(
        "--csv",
        action="store_true",
        help="Output as CSV instead of table",
    )
    parser.add_argument(
        "--only-with-limit",
        action="store_true",
        help="Show only templates that have a limit set",
    )

    args = parser.parse_args()

    try:
        templates = get_all_job_templates(
            base_url=args.url,
            token=args.token,
            username=args.username,
            password=args.password,
            verify_ssl=not args.insecure,
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.only_with_limit:
        templates = [t for t in templates if t["limit"]]

    if not templates:
        print("No job templates found.")
        return

    if args.csv:
        import csv
        writer = csv.DictWriter(
            sys.stdout,
            fieldnames=["id", "name", "limit", "ask_limit_on_launch", "playbook", "organization"],
        )
        writer.writeheader()
        for t in templates:
            writer.writerow(
                {
                    "id": t["id"],
                    "name": t["name"],
                    "limit": t["limit"],
                    "ask_limit_on_launch": t["ask_limit_on_launch"],
                    "playbook": t["playbook"],
                    "organization": t["organization"] or "",
                }
            )
    else:
        # Pretty table
        print(f"{'ID':<6} {'Name':<45} {'Limit':<30} {'Ask on Launch':<14} {'Playbook'}")
        print("-" * 120)
        for t in templates:
            limit_display = t["limit"] if t["limit"] else "(none)"
            ask = "Yes" if t["ask_limit_on_launch"] else "No"
            print(
                f"{t['id']:<6} {t['name'][:44]:<45} {limit_display[:29]:<30} "
                f"{ask:<14} {t['playbook'] or ''}"
            )

        print(f"\nTotal: {len(templates)} job template(s)")

if __name__ == "__main__":
    main()
