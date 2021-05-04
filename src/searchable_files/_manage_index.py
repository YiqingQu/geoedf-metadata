import json

import click

from ._common import common_options, search_client, token_storage_adapter


@click.command(
    "create-index",
    short_help="Create the Index for Searchable Files",
    help="Create the Index for Searchable Files. It will be owned "
    "by the current user.",
)
@common_options
def create_index():
    adapter = token_storage_adapter()
    client = search_client()

    res = client.post(
        "/beta/index",
        {
            "display_name": "Searchable Files Demo Index",
            "description": "An index created for use with the Searchable Files Demo App",
        },
    )
    index_id = res["id"]

    adapter.store_config("index_info", {"index_id": index_id})

    click.echo(f"successfully created index, id='{index_id}'")


@click.command(
    "show-index",
    short_help="Show index info",
    help="Show detailed info about the Searchable Files index. "
    "Must run after create-index",
)
@common_options
def show_index():
    adapter = token_storage_adapter()
    client = search_client()

    index_info = adapter.read_config("index_info")
    if not index_info:
        raise click.UsageError("You must create an index with `create-index` first!")
    index_id = index_info["index_id"]

    res = client.get(f"/v1/index/{index_id}")
    click.echo(json.dumps(res.data, indent=2, separators=(",", ": ")))