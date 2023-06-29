import json
from typing import TYPE_CHECKING, TextIO

import click

from .. import chainflip, tools
from . import with_client

if TYPE_CHECKING:
    from ..client import TrezorClient

@click.group(name="chainflip")
def cli() -> None:
    """Chainflip commands."""

@cli.command(help="Report the governance public key")
@with_client
def pubkey(client: "TrezorClient"):
    """Get Chainflip Pubkey"""
    return chainflip.request_pubkey(client)

@cli.command(help="Sign the provided payload with the governance public key")
@click.argument("payload")
@with_client
def sign(client: "TrezorClient", payload):
    """Sign data"""
    data = payload[2:] if payload[:2] == "0x" else payload
    return chainflip.request_signature(client, bytes.fromhex(data))