from micropython import const
from typing import TYPE_CHECKING

from .. import common

if TYPE_CHECKING:
    from trezor.messages import TxInput, TxOutput

# The chain id used for change.
_BIP32_CHANGE_CHAIN = const(1)

# The maximum allowed change address. This should be large enough for normal
# use and still allow to quickly brute-force the correct BIP32 path.
_BIP32_MAX_LAST_ELEMENT = const(1_000_000)


class ChangeDetector:
    def __init__(self) -> None:
        from .matchcheck import (
            MultisigFingerprintChecker,
            ScriptTypeChecker,
            WalletPathChecker,
        )

        # Checksum of multisig inputs, used to validate change-output.
        self.multisig_fingerprint = MultisigFingerprintChecker()

        # Common prefix of input paths, used to validate change-output.
        self.wallet_path = WalletPathChecker()

        # Common script type, used to validate change-output.
        self.script_type = ScriptTypeChecker()

    def add_input(self, txi: TxInput) -> None:
        if not common.input_is_external(txi):
            self.wallet_path.add_input(txi)
            self.script_type.add_input(txi)
            self.multisig_fingerprint.add_input(txi)

    def check_input(self, txi: TxInput) -> None:
        self.wallet_path.check_input(txi)
        self.script_type.check_input(txi)
        self.multisig_fingerprint.check_input(txi)

    def output_is_change(self, txo: TxOutput) -> bool:
        if txo.script_type not in common.CHANGE_OUTPUT_SCRIPT_TYPES:
            return False

        # Check the multisig fingerprint only for multisig outputs. This means
        # that a transfer from a multisig account to a singlesig account is
        # treated as a change-output as long as all other change-output
        # conditions are satisfied. This goes a bit against the concept of a
        # multisig account but the other cosigners will notice that they are
        # relinquishing control of the funds, so there is no security risk.
        if txo.multisig and not self.multisig_fingerprint.output_matches(txo):
            return False

        return (
            self.wallet_path.output_matches(txo)
            and self.script_type.output_matches(txo)
            and len(txo.address_n) >= common.BIP32_WALLET_DEPTH
            and txo.address_n[-2] <= _BIP32_CHANGE_CHAIN
            and txo.address_n[-1] <= _BIP32_MAX_LAST_ELEMENT
            and txo.amount > 0
        )
