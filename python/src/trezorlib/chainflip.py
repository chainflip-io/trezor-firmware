import struct
import xdrlib

from . import messages
from .tools import expect

@expect(messages.ChainflipPubkey, field="pubkey")
def request_pubkey(client):
    return client.call(
        messages.ChainflipRequestPubkey()
    )

@expect(messages.ChainflipSignature, field="signature")
def request_signature(client, payload):
    return client.call(
        messages.ChainflipRequestSignature(payload=payload)
    )
