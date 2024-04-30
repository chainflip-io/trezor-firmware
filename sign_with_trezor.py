from substrateinterface import SubstrateInterface, Keypair, KeypairType
from scalecodec.base import ScaleBytes
import sys

# This prints the decoded call in a human readable form so that the user can confirm
# that the extrinsic matches their expectation
def print_call(call, indent=0):
    print("    "*indent + call['call_module'] + " -> " + call['call_function'] + "(")
    for x in call['call_args']:
        if type(x) is dict and x['type'] == 'RuntimeCall':
            print_call(x['value'], indent+1)
        else:
            arg = str(x['value'])
            if len(arg) > 128:
                arg = arg[:128] + "..."
            print("    "*(indent+1) + x['name'] + ": " + arg + "  (" + x['type'] + ")")
    print("    "*indent + ")")

# The substrate libraries decode into arrays for arguments, but expect dicts when encoding...
# So we have to fix this manually
def fix_args(module, function, args):
    result = {
        'call_module': module,
        'call_function': function
    }
    new_args = {}
    for a in args:
        if a['type'] == 'RuntimeCall':
            temp_module = a['value']['call_module']
            temp_function = a['value']['call_function']
            temp_args = a['value']['call_args']
            new_args[a['name']] = fix_args(temp_module, temp_function, temp_args)
        elif a['type'] == 'Price':
            new_args[a['name']] = [a['value']]
        elif a['type'] == 'BoundedVec<PalletConfigUpdate<T, I>, ConstU32<10>>':
            new_args[a['name']] = [a['value']]
        elif a['type'] == 'Vec<RuntimeCall>':
            new_args[a['name']] = [fix_args(c['call_module'], c['call_function'], c['call_args']) for c in a['value']]
        else:
            new_args[a['name']] = a['value']
    result['call_args'] = new_args
    return result

endpoint = input("Enter Endpoint URL: (defaults to wss://mainnet-rpc.chainflip.io) ")
if endpoint == "":
    endpoint = "wss://mainnet-rpc.chainflip.io"
api = SubstrateInterface(url=endpoint)
calldata = open(sys.argv[1], "r").read() if len(sys.argv) == 2 else input("Enter Calldata: ")
call = api.create_scale_object(type_string='Call', data=ScaleBytes(calldata)).decode()
print_call(call)
call = fix_args(call['call_module'], call['call_function'], call['call_args'])
call = api.compose_call(
    call_module=call['call_module'],
    call_function=call['call_function'],
    call_params=call['call_args'])

pubkey = input("Enter Pubkey: ")
if pubkey[:2] == "0x":
    pubkey = pubkey[2:]
keypair = Keypair(public_key=bytes.fromhex(pubkey), crypto_type=KeypairType.ED25519, ss58_format=2112)
print("Address:", keypair.ss58_address)
current_block = api.get_block_number(None)
print("Current Block:", current_block)
era = {'period': 64, 'current': current_block}
nonce = api.get_account_nonce(keypair.ss58_address)
print("Nonce:", nonce)
payload = api.generate_signature_payload(call=call, era=era, nonce=nonce)
print("Payload:", payload)
signature = input("Enter Signature: ")
if signature[:2] == "0x":
    signature = signature[2:]
raw_signature = bytes.fromhex(signature)
tx = api.create_signed_extrinsic(call=call, keypair=keypair, era=era, nonce=nonce, signature=raw_signature)

if keypair.verify(data=payload, signature=raw_signature):
    extrinsic = str(tx.data)
    if len(extrinsic) < 1025:
        print("Extrinsic:", str(tx.data))
    else:
        open("extrinsic.txt", "w").write(extrinsic)
        print("Extrinsic was written to extrinsic.txt")
    confirmation = input("Submit extrinsic? (Y/N) ")
    if confirmation == "Y" or confirmation == "y":
        receipt = api.submit_extrinsic(tx, wait_for_inclusion=True)
        print('Extrinsic "{}" included in block "{}"'.format(
            receipt.extrinsic_hash, receipt.block_hash
        ))
        if receipt.is_success:
            print("Extrinsic was successful!")
        else:
            print("Extrinsic failed on chain!")
    else:
        print("Not sent")
else:
    print("Signature invalid!")