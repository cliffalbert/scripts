#!/usr/bin/env python3
"""Dump AWX inventories as an Ansible YAML inventory.

Each AWX inventory becomes a child of the parent group. Host and group
variables and group membership come from the inventory script endpoint.
Hosts marked disabled in AWX are left out. The host ``description`` is
the AWX host description. When that field is empty, a description already
stored in host variables is kept. Otherwise the host is marked as auto-added.
"""

import argparse
import os
import sys
from collections import Counter
from typing import Optional
from urllib.parse import urljoin

import requests
import yaml
from requests.auth import HTTPBasicAuth

AUTO_DESCRIPTION = "Auto Added by AWX Inventory"
TIMEOUT = 60


class AwxError(Exception):
    def __init__(self, message: str, status: Optional[int] = None):
        super().__init__(message)
        self.status = status


def host_record(variables: object, description: Optional[str]) -> dict:
    """Build one Ansible host mapping, description first."""
    record = {}
    variable_description = None
    if isinstance(variables, dict):
        for key, value in variables.items():
            if key == "description":
                variable_description = value
            else:
                record[key] = value

    text = (description or "").strip()
    if not text and isinstance(variable_description, str):
        text = variable_description.strip()
    if not text:
        text = AUTO_DESCRIPTION
    return {"description": text, **record}


def parse_variables(raw: object, host_name: str) -> dict:
    if isinstance(raw, dict):
        return raw
    if not isinstance(raw, str) or not raw.strip():
        return {}
    try:
        parsed = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        print(f"warning: {host_name}: could not parse variables: {exc}", file=sys.stderr)
        return {}
    if parsed in (None, {}):
        return {}
    if not isinstance(parsed, dict):
        print(f"warning: {host_name}: variables are not a mapping; left them out", file=sys.stderr)
        return {}
    return parsed


def _host_names(hosts_field: object) -> list:
    if isinstance(hosts_field, list):
        return [name for name in hosts_field if isinstance(name, str)]
    if isinstance(hosts_field, dict):
        return [name for name in hosts_field if isinstance(name, str)]
    return []


def _child_names(children_field: object) -> list:
    if isinstance(children_field, list):
        return [name for name in children_field if isinstance(name, str)]
    if isinstance(children_field, dict):
        return [name for name in children_field if isinstance(name, str)]
    return []


def host_is_enabled(host: dict) -> bool:
    """AWX hosts stay in the export unless ``enabled`` is explicitly false."""
    return host.get("enabled") is not False


def script_to_group(
    script: dict,
    descriptions: dict,
    raw_variables: Optional[dict] = None,
    disabled: Optional[set] = None,
) -> dict:
    """Convert AWX dynamic-inventory JSON into an Ansible YAML group body.

    AWX lists every group as a top-level key and again in ``all.children``.
    Nested groups are emitted only under their parent so the YAML is a tree.
    Host variables prefer the script hostvars. Hosts missing from the script
    keep the variables stored on the AWX host. Disabled hosts are omitted
    even when the script still lists them.
    """
    if not isinstance(script, dict):
        raise AwxError("inventory script response was not an object")

    disabled = set(disabled or ())
    meta = script.get("_meta") if isinstance(script.get("_meta"), dict) else {}
    hostvars = meta.get("hostvars") if isinstance(meta.get("hostvars"), dict) else {}
    raw_variables = raw_variables or {}
    records = {}
    for name in (set(descriptions) | set(hostvars) | set(raw_variables)) - disabled:
        variables = hostvars.get(name)
        if not isinstance(variables, dict):
            variables = parse_variables(raw_variables.get(name), name)
        records[name] = host_record(variables, descriptions.get(name))

    groups = {
        name: content
        for name, content in script.items()
        if name not in ("_meta", "all") and isinstance(content, dict)
    }
    all_group = script.get("all") if isinstance(script.get("all"), dict) else {}
    nested = _nested_children(groups)

    def render(name: str, stack: tuple) -> dict:
        if name in stack:
            print(
                f"warning: group cycle involving {name}; stopped nesting there",
                file=sys.stderr,
            )
            return {}
        content = groups.get(name) or {}
        node = {}
        group_vars = content.get("vars") or {}
        if isinstance(group_vars, dict) and group_vars:
            node["vars"] = group_vars
        hosts = _host_map(_host_names(content.get("hosts")), records, descriptions, disabled)
        if hosts:
            node["hosts"] = hosts
        children = {}
        for child in _child_names(content.get("children")):
            if child in ("_meta", "all"):
                continue
            children[child] = render(child, stack + (name,))
        if children:
            node["children"] = children
        return node

    inventory_vars = all_group.get("vars") or {}
    hosts = _host_map(_host_names(all_group.get("hosts")), records, descriptions, disabled)

    roots = []
    seen = set()
    for name in list(_child_names(all_group.get("children"))) + list(groups):
        if name in ("_meta", "all") or name in nested or name in seen:
            continue
        roots.append(name)
        seen.add(name)

    children = {name: render(name, ()) for name in roots}
    rendered = set()
    _collect_group_names(children, rendered)
    for name in groups:
        if name in rendered:
            continue
        print(
            f"warning: group {name} was not reachable from the inventory root; attaching it directly",
            file=sys.stderr,
        )
        children[name] = render(name, ())

    listed = set(hosts)
    _collect_hosts({"hosts": hosts, "children": children}, listed)
    for hostname in sorted(set(records) - listed):
        hosts[hostname] = records[hostname]

    node = {}
    if isinstance(inventory_vars, dict) and inventory_vars:
        node["vars"] = inventory_vars
    if hosts:
        node["hosts"] = hosts
    if children:
        node["children"] = children
    return node


def _host_map(hostnames: list, records: dict, descriptions: dict, disabled: set) -> dict:
    hosts = {}
    for hostname in hostnames:
        if hostname in disabled:
            continue
        hosts[hostname] = records.get(hostname) or host_record({}, descriptions.get(hostname))
    return hosts


def _nested_children(groups: dict) -> set:
    names = set()
    for content in groups.values():
        names.update(_child_names(content.get("children")))
    return names


def _collect_hosts(node: dict, found: set) -> None:
    found.update((node.get("hosts") or {}).keys())
    for child in (node.get("children") or {}).values():
        if isinstance(child, dict):
            _collect_hosts(child, found)


def _collect_group_names(children: dict, found: set) -> None:
    for name, body in children.items():
        found.add(name)
        if isinstance(body, dict):
            _collect_group_names(body.get("children") or {}, found)


def flat_group(raw_hosts: list) -> dict:
    hosts = {}
    for host in raw_hosts:
        name = host.get("name")
        if not name or not host_is_enabled(host):
            continue
        variables = parse_variables(host.get("variables"), name)
        hosts[name] = host_record(variables, host.get("description"))
    return {"hosts": hosts} if hosts else {}


def _error_from_response(response: requests.Response, url: str) -> AwxError:
    detail = ""
    try:
        body = response.json()
    except ValueError:
        body = None
    if isinstance(body, dict):
        detail = str(body.get("detail") or body.get("error") or "")
    elif response.text:
        detail = response.text.strip().splitlines()[0][:200]
    message = f"AWX returned HTTP {response.status_code} for {url}"
    if detail:
        message = f"{message}: {detail}"
    return AwxError(message, status=response.status_code)


def request_json(session: requests.Session, url: str, params: Optional[dict] = None) -> dict:
    try:
        response = session.get(url, params=params, timeout=TIMEOUT)
    except requests.Timeout as exc:
        raise AwxError(f"timed out requesting {url}") from exc
    except requests.RequestException as exc:
        raise AwxError(f"request failed for {url}: {exc}") from exc
    if response.status_code >= 400:
        raise _error_from_response(response, url)
    try:
        data = response.json()
    except ValueError as exc:
        raise AwxError(f"AWX response from {url} was not JSON") from exc
    if not isinstance(data, dict):
        raise AwxError(f"AWX response from {url} was not an object")
    return data


def get_all(session: requests.Session, url: str) -> list:
    results = []
    params = {"page_size": 200, "order_by": "name"}
    while url:
        data = request_json(session, url, params=params)
        if "results" not in data:
            detail = data.get("detail") or "response had no results list"
            raise AwxError(f"unexpected AWX response from {url}: {detail}")
        page = data["results"]
        if not isinstance(page, list):
            raise AwxError(f"unexpected AWX response from {url}: results was not a list")
        results.extend(page)
        # AWX often returns ``next`` as a root-relative path. requests will
        # not add the scheme or host unless we join it to the page we just fetched.
        next_url = data.get("next")
        url = urljoin(url, next_url) if next_url else None
        params = None
    return results


def fetch_script(session: requests.Session, url: str) -> Optional[dict]:
    """Return inventory script JSON, or None when this AWX has no script endpoint.

    ``all`` is left unset so AWX omits hosts that are disabled on the inventory.
    """
    try:
        response = session.get(url, params={"hostvars": "1"}, timeout=TIMEOUT)
    except requests.Timeout as exc:
        raise AwxError(f"timed out requesting {url}") from exc
    except requests.RequestException as exc:
        raise AwxError(f"request failed for {url}: {exc}") from exc

    if response.status_code == 404:
        return None
    if response.status_code >= 400:
        raise _error_from_response(response, url)
    try:
        data = response.json()
    except ValueError as exc:
        raise AwxError(f"AWX response from {url} was not JSON") from exc
    if not isinstance(data, dict):
        raise AwxError(f"AWX response from {url} was not an object")
    return data


def inventory_group(session: requests.Session, base_url: str, inventory_id: int, label: str) -> dict:
    raw_hosts = get_all(session, f"{base_url}/api/v2/inventories/{inventory_id}/hosts/")
    descriptions = {}
    raw_variables = {}
    disabled = set()
    enabled_hosts = []
    for host in raw_hosts:
        name = host.get("name")
        if not name:
            continue
        if not host_is_enabled(host):
            disabled.add(name)
            continue
        enabled_hosts.append(host)
        descriptions[name] = host.get("description") or ""
        raw_variables[name] = host.get("variables")

    script = fetch_script(session, f"{base_url}/api/v2/inventories/{inventory_id}/script/")
    if script is None:
        print(
            f"warning: {label}: inventory script endpoint not available; writing a flat host list",
            file=sys.stderr,
        )
        return flat_group(enabled_hosts)
    return script_to_group(script, descriptions, raw_variables, disabled)


def selected_inventories(inventories: list, skip_name: Optional[str]) -> list:
    chosen = []
    for inventory in inventories:
        name = inventory.get("name")
        if not name:
            continue
        if skip_name and name == skip_name:
            continue
        if inventory.get("pending_deletion"):
            print(f"warning: skipping {name}: deletion in progress", file=sys.stderr)
            continue
        chosen.append(inventory)

    counts = Counter(inventory["name"] for inventory in chosen)
    labeled = []
    for inventory in chosen:
        name = inventory["name"]
        if counts[name] > 1:
            org = (
                (inventory.get("summary_fields") or {}).get("organization") or {}
            ).get("name") or "unknown-org"
            labeled.append((inventory, f"{org}/{name}"))
        else:
            labeled.append((inventory, name))
    return labeled


def build_inventory(session: requests.Session, base_url: str, parent: str, skip_name: Optional[str]) -> dict:
    inventories = get_all(session, f"{base_url}/api/v2/inventories/")
    children = {}
    for inventory, label in selected_inventories(inventories, skip_name):
        children[label] = inventory_group(session, base_url, inventory["id"], label)
    return {parent: {"children": children}}


def parse_args(argv: Optional[list] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert AWX inventories to an Ansible YAML inventory"
    )
    parser.add_argument(
        "--url",
        default=os.getenv("AWX_URL"),
        help="AWX base URL (or set AWX_URL)",
    )
    parser.add_argument(
        "--token",
        default=os.getenv("AWX_TOKEN"),
        help="OAuth2 or personal access token (or set AWX_TOKEN)",
    )
    parser.add_argument(
        "-u",
        "--username",
        default=os.getenv("AWX_USERNAME"),
        help="Username, used when no token is set (or set AWX_USERNAME)",
    )
    parser.add_argument(
        "-p",
        "--password",
        default=os.getenv("AWX_PASSWORD"),
        help="Password, used when no token is set (or set AWX_PASSWORD)",
    )
    parser.add_argument(
        "-i",
        "--inventory",
        help=(
            "Name of the generated parent group. AWX inventories are nested under it. "
            "When you pass this, an AWX inventory of the same name is left out. "
            "Defaults to 'all'."
        ),
    )
    parser.add_argument(
        "--insecure",
        action="store_true",
        help="Disable SSL certificate verification",
    )
    args = parser.parse_args(argv)
    if not args.url:
        parser.error("AWX URL is required (--url or AWX_URL)")
    if not args.token and not (args.username and args.password):
        if args.username or args.password:
            parser.error("provide both username and password, or a token")
        parser.error("provide a token (--token or AWX_TOKEN) or username and password")
    return args


def make_session(args: argparse.Namespace) -> requests.Session:
    session = requests.Session()
    session.verify = not args.insecure
    session.headers["Accept"] = "application/json"
    if args.token:
        session.headers["Authorization"] = f"Bearer {args.token}"
    else:
        session.auth = HTTPBasicAuth(args.username, args.password)
    return session


class InventoryDumper(yaml.SafeDumper):
    """Dump every host in full.

    A host listed in several groups is one dict object. The default dumper
    turns the later copies into aliases such as ``*id007``.
    """

    def ignore_aliases(self, data):
        return True


def dump_inventory(document: dict) -> None:
    yaml.dump(
        document,
        sys.stdout,
        Dumper=InventoryDumper,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
        width=4096,
    )


def main(argv: Optional[list] = None) -> int:
    args = parse_args(argv)
    parent = args.inventory or "all"
    # Skipping is tied to an explicit name so the default parent "all" does
    # not drop an AWX inventory that happens to be named all.
    skip_name = args.inventory
    try:
        document = build_inventory(
            make_session(args),
            args.url.rstrip("/"),
            parent,
            skip_name,
        )
    except AwxError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    dump_inventory(document)
    return 0


if __name__ == "__main__":
    sys.exit(main())
