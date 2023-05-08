import os

import click
import globus_sdk
from globus_sdk_tokenstorage import SQLiteAdapter

AUTH_RESOURCE_SERVER = "auth.globus.org"

CLIENT_ID = "c1bd6f26-7d46-4ccf-a7af-ddc7dfec2bfe"


def internal_auth_client():
    return globus_sdk.NativeAppAuthClient(CLIENT_ID, app_name="searchable-files")


def token_storage_adapter():
    if not hasattr(token_storage_adapter, "_instance"):
        # namespace is equal to the current environment
        token_storage_adapter._instance = SQLiteAdapter(
            os.path.expanduser("~/.globus_searchable_files.db"), namespace="DEFAULT"
        )
    return token_storage_adapter._instance


def auth_client():
    storage_adapter = token_storage_adapter()
    as_dict = storage_adapter.read_as_dict()

    if as_dict is None or AUTH_RESOURCE_SERVER not in as_dict:
        raise click.UsageError("Cannot load Auth credentials. Probably not logged in.")

    authdata = as_dict[AUTH_RESOURCE_SERVER]
    access_token = authdata["access_token"]
    print(f'[auth_client] access_token={access_token}')
    refresh_token = authdata["refresh_token"]
    access_token_expires = authdata["expires_at_seconds"]

    authorizer = globus_sdk.RefreshTokenAuthorizer(
        refresh_token,
        internal_auth_client(),
        access_token,
        int(access_token_expires),
        on_refresh=storage_adapter.on_refresh,
    )

    return globus_sdk.AuthClient(authorizer=authorizer, app_name="searchable-files")
