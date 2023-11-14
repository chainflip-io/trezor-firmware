# Chainflip Trezor tools

This repository is forked from the Trezor monorepo. It adds functionality for signing
extrinsics using the Trezor Model One. It consists of three parts:
- The Firmware, which is installed onto the Trezor to add support for signing extrinsics
- The CLI (trezorctl), which is a tool to interface with the trezor. Functions for exporting
  the public key and signing extrinsics were added
- A script `sign_with_trezor.py` which makes creating, signing and submitting extrinsics easier.

## Build the firmware
To make the build deterministic and reproducible, the firmware is built inside a Docker container. For security reasons, the Trezor will not accept "production" builds that haven't been signed by Trezor themselves, but "non-production" builds work fine. The build script expects a tag name and will build the code in the corresponding commit. If you want to make changes to the code, you need to commit them and tag the last commit. For convenience, the latest commit on this repo is tagged as "chainflip". To build it, run:
```
PRODUCTION=0 ./build-docker.sh --skip-bitcoinonly --skip-core chainflip
```

## Build the cli tool
Run these commands:
```
brew install protobuf
python3 -m venv .venv
source .venv/bin/activate
pip install pillow mako munch pyyaml substrate-interface click trezor google protobuf
git submodule update --init --recursive
make gen
cd python
python setup.py build
python setup.py install
pip uninstall trezor
```
Now you should be able to run `trezorctl`. Check that the "chainflip" command is available.

## Installing the firmware
Hold both buttons on the Trezor and then plug it in. It should start in "bootloader" mode. Now you can install the firmware by running
```
trezorctl firmware update -f ./build/legacy/firmware/firmware.bin
```
Follow the instructions on the device.
Installing the firmware will completely wipe your Trezor! Make sure you have your recovery phrase if you used it before!
You need to set-up your Trezor after installing the new firmware. This works just like with a normal Trezor.

## Signing and submitting an extrinsic
In polkadot.js, create an extrinsic, but instead of submitting it, copy the "encoded call data".
Then run
```
python sign_with_trezor.py
```
and provide the requested data. For example
- Endpoint: ws://127.0.0.1:9944
- Calldata: 0x2002 (this is the "encoded call data" copied from polkadot.js)
- Pubkey: (run `trezorctl chainflip pubkey` and use the reported value)

You will now receive a "Payload" that needs to be signed with the trezor.
- Signature: (run `trezorctl chainflip sign <Payload>` and use the reported value here)

You will now receive the signed extrinsic.
You can press "y" to submit it directly, or submit it manually through polkadot.js

If the extrinsic is very large, you can copy the calldata into a file and call
```
python sign_with_trezor.py calldata.txt
```
The signed extrinsic will then be stored in a separate file "extrinsic.txt"
