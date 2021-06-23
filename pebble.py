#!/usr/bin/env python3

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, List, Optional, Tuple, Union

import click
import requests
from click.core import Option
from dateutil.parser import parse as parse_time_str
from dotenv import load_dotenv

load_dotenv(dotenv_path=f"{Path.home()}/.config/pebble-cms/config")
load_dotenv(override=True)

PEBBLE_API_ENDPOINT = os.getenv("PEBBLE_API_ENDPOINT", "https://pebble.ggicci.me")
PEBBLE_TOKEN = os.getenv("PEBBLE_TOKEN")
PEBBLE_NAMESPACE = os.getenv("PEBBLE_NAMESPACE")

CLIENT = requests.Session()
CLIENT.headers["Authorization"] = f"Bearer {PEBBLE_TOKEN}"


def api_url(path: str) -> str:
    return f"{PEBBLE_API_ENDPOINT}{path}"


def json_serializable(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: json_serializable(obj[k]) for k in obj.keys()}
    if isinstance(obj, (list, tuple)):
        return [json_serializable(x) for x in obj]
    if isinstance(obj, datetime):
        return obj.isoformat()
    if hasattr(obj, "__dict__"):
        return json_serializable(obj.__dict__)
    return obj


def __display_key_values(kvs: dict) -> None:
    max_length = max(len(x) for x in kvs.keys())
    for (k, v) in kvs.items():
        click.echo(f"{k.ljust(max_length + 1)}: {v}")


def exit_on_api_error(resp) -> None:
    if 200 <= resp.status_code < 300:
        return

    kvs = {"Status": resp.status_code}
    kvs.update(resp.headers.items())
    __display_key_values(kvs)
    click.secho(resp.text, fg="red")
    sys.exit(1)


class State:
    def __init__(self):
        self.id: str = None
        self.created_at: datetime = None
        self.updated_at: datetime = None
        self.name: str = None
        self.display: str = None
        self.remark: str = None
        self.upstream: List[str] = None
        self.namespace_id: str = None
        self.upstream_details: List[dict] = None

    def from_json(self, json_data: dict):
        for k, v in json_data.items():
            if hasattr(self, k):
                setattr(self, k, v)

    def to_json(self, compact=True) -> str:
        """Returns a JSON representation of the state."""
        if compact is True:
            return json.dumps(json_serializable(self.__dict__))
        return json.dumps(json_serializable(self.__dict__), indent=4)

    @classmethod
    def from_json(cls, json_data: dict):
        if json_data is None:
            return None

        state = cls()
        for k, v in json_data.items():
            if hasattr(state, k):
                setattr(state, k, v)

        state.created_at = parse_time_str(json_data["created_at"])
        state.updated_at = parse_time_str(json_data["updated_at"])
        return state

    @classmethod
    def list(cls) -> List["State"]:
        resp = CLIENT.get(api_url(f"/v1/namespaces/{PEBBLE_NAMESPACE}/states"))
        exit_on_api_error(resp)
        state_list = []
        for item in resp.json():
            state_list.append(cls.from_json(item))
        return state_list


class Pagination:
    pass


class Pebble:
    PATCHABLE_FIELDS = ("title", "state_id", "tags", "content", "kind", "nuid")

    def __init__(self):
        self.id: str = None
        self.created_at: datetime = None
        self.updated_at: datetime = None
        self.uuid: str = None
        self.namespace_id: str = None
        self.nuid: str = None
        self.owner_id: str = None
        self.state_id: str = None
        self.title: str = None
        self.filesize: int = None
        self.content_type: str = None
        self.kind: str = None
        self.tags: List[str] = None
        self.revision: str = None
        self.permalink: str = None
        self.content: str = None
        self.storage_provider: str = None
        self.owner = None
        self.state: "State" = None

    def __str__(self):
        return f"Pebble#{self.id}"

    def to_json(self, compact=True) -> str:
        """Returns a JSON representation of the pebble."""
        if compact is True:
            return json.dumps(json_serializable(self.__dict__))
        return json.dumps(json_serializable(self.__dict__), indent=4)

    @classmethod
    def create(cls, title: str, **kwargs) -> "Pebble":
        payload = {"title": title}
        payload.update(kwargs)
        resp = CLIENT.post(
            api_url(f"/v1/namespaces/{PEBBLE_NAMESPACE}/pebbles"), json=payload
        )
        exit_on_api_error(resp)
        new_resp = CLIENT.get(api_url(resp.headers.get("Location")))
        new_exit_on_api_error(resp)
        return cls.from_json(new_resp.json())

    @classmethod
    def fetch(
        cls,
        pid: str,
        nuid: Optional[str] = None,
        meta_only: bool = False,
        content_only: bool = False,
    ) -> Union["Pebble", str]:
        """Fetch a pebble from remote by pebble's id or nuid.

        Args:
            pid: The id of the pebble
            nuid: The custom unique id of the pebble
            meta_only: Fetch meta info only
            content_only: Fetch content only

        Returns:
            A Pebble instance or just content of the Pebble when content_only is True
        """
        url = (
            api_url(f"/v1/namespaces/{PEBBLE_NAMESPACE}/pebbles/by-nuid/{nuid}")
            if nuid
            else api_url(f"/v1/pebbles/{pid}")
        )
        resp = CLIENT.get(
            url, params={"meta_only": meta_only, "content_only": content_only}
        )
        exit_on_api_error(resp)
        if content_only:
            return resp.text
        return cls.from_json(resp.json())

    @classmethod
    def list(cls) -> Tuple[List["Pebble"], Pagination]:
        """List pebbles."""
        resp = CLIENT.get(api_url(f"/v1/namespaces/{PEBBLE_NAMESPACE}/pebbles"))
        exit_on_api_error(resp)
        # TODO(ggicci): pagination
        pebbles = [cls.from_json(x) for x in resp.json()]
        return pebbles, None

    @classmethod
    def update(cls, pid: str, by_nuid: Optional[str], **kwargs) -> "Pebble":
        payload = {
            k: v
            for k, v in kwargs.items()
            if k in cls.PATCHABLE_FIELDS and v is not None
        }
        resp = CLIENT.patch(
            api_url(f"/v1/namespaces/{PEBBLE_NAMESPACE}/pebbles/{pid}")
            if pid
            else api_url(
                f"/v1/namespaces/{PEBBLE_NAMESPACE}/pebbles/by-nuid/{by_nuid}"
            ),
            json=payload,
        )
        exit_on_api_error(resp)
        return cls.fetch(pid, by_nuid, meta_only=False)

    @classmethod
    def from_json(cls, json_data: dict):
        if json_data is None:
            return None

        pebble = cls()
        for k, v in json_data.items():
            if hasattr(pebble, k):
                setattr(pebble, k, v)

        pebble.created_at = parse_time_str(json_data["created_at"])
        pebble.updated_at = parse_time_str(json_data["updated_at"])
        pebble.state = State.from_json(json_data.get("state"))
        return pebble


@click.command()
def list_states():
    """List states"""
    states = State.list()
    from prettytable import PrettyTable

    table = PrettyTable()
    table.field_names = [
        "#",
        "ID",
        "Created At",
        "Name",
        "Display",
        "Upstream",
        "Remark",
    ]
    for i, state in enumerate(states):
        table.add_row(
            [
                i + 1,
                state.id,
                state.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                state.name,
                state.display,
                ", ".join([x.get("name") for x in state.upstream_details or []]),
                state.remark,
            ]
        )
    print(table)


@click.command()
@click.argument("title")
@click.option("--content", help="Content of the pebble")
@click.option("--kind", help="Kind of the pebble, e.g. python, image, receipt, etc.")
@click.option("--state-id", type=int, help="State ID")
@click.option("--tags", help='Tags separated by comma, e.g. "docker,k8s"')
@click.option("--nuid", help="Custom unique ID")
def create_pebble(title, kind, content, tags, state_id, nuid):
    """Create a pebble"""
    ntags = (
        tags
        if tags is None
        else [x.strip() for x in tags.split(",") if x.strip() != ""]
    )
    pebble = Pebble.create(
        title, content=content, kind=kind, tags=ntags, state_id=state_id, nuid=nuid
    )
    click.echo(pebble.to_json(compact=False))


@click.command()
@click.argument("pid", required=False)
@click.option("--by-nuid", help="Custom unique ID")
@click.option("--meta-only", type=bool, is_flag=True, help="Fetch without content")
@click.option("--content-only", type=bool, is_flag=True, help="Fetch content only")
def get_pebble(pid: str, by_nuid: str, meta_only: bool, content_only: bool) -> None:
    """Get a pebble"""
    if not pid and not by_nuid:
        click.echo("ERROR: empty PID and NUID\n")
        click.echo(click.get_current_context().get_help())
        return 1

    content_only = not meta_only and content_only
    pebble = Pebble.fetch(
        pid,
        by_nuid,
        meta_only=meta_only,
        content_only=content_only,
    )

    if content_only:
        click.echo(pebble)
        return

    click.echo(pebble.to_json(compact=False))


@click.command()
def list_pebbles():
    """List pebbles"""
    pebbles, pagination = Pebble.list()

    from prettytable import PrettyTable

    table = PrettyTable()
    table.field_names = [
        "#",
        "ID",
        "Created At",
        "NUID",
        "Title",
        "State",
        "Tags",
    ]
    for i, pebble in enumerate(pebbles):
        table.add_row(
            [
                i + 1,
                pebble.id,
                pebble.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                pebble.nuid,
                pebble.title,
                "-" if pebble.state is None else pebble.state.display,
                ",".join(pebble.tags),
            ]
        )
    print(table)


@click.command()
@click.argument("pid", required=False)
@click.option("--by-nuid", help="Use custom unique ID to locate the pebble")
@click.option("--content", help="Content of the pebble")
@click.option("--kind", help="Kind of the pebble, e.g. python, image, receipt, etc.")
@click.option("--state-id", type=int, help="State ID")
@click.option("--tags", help='Tags separated by comma, e.g. "docker,k8s"')
@click.option("--nuid", help="Custom unique ID")
def update_pebble(pid, by_nuid, content, kind, state_id, tags, nuid):
    """Update a pebble"""
    ntags = (
        tags
        if tags is None
        else [x.strip() for x in tags.split(",") if x.strip() != ""]
    )
    pebble = Pebble.update(
        pid,
        by_nuid,
        content=content,
        kind=kind,
        state_id=state_id,
        tags=ntags,
        nuid=nuid,
    )
    click.echo(pebble.to_json(compact=False))


@click.command()
@click.argument("pid", required=False)
@click.option("--by-nuid", type=str, help="Custom unique ID")
def delete_pebble(pid: str, nuid: str):
    """Delete a pebble"""
    pass


@click.group()
def cli():
    pass


# TODO(ggicci): add command "add-state"
cli.add_command(list_states, "states")
cli.add_command(create_pebble, "create")
cli.add_command(get_pebble, "get")
cli.add_command(list_pebbles, "list")
cli.add_command(update_pebble, "update")
cli.add_command(delete_pebble, "delete")


def main():
    cli()


if __name__ == "__main__":
    main()
