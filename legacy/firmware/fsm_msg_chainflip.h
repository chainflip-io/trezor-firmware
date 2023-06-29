
/*
Takes no arguments and provides the Ed25519 Pubkey as a hex string
*/
void fsm_msgChainflipRequestPubkey(const ChainflipRequestPubkey *msg) {
  (void)msg;
  RESP_INIT(ChainflipPubkey);

  CHECK_INITIALIZED

  CHECK_PIN
  layoutDialogSwipe(&bmp_chainflip, _("Cancel"), _("Export"), NULL,
                        _("Do you want to export"), _("your Chainflip"),
                        _("Governance Pubkey?"), NULL, NULL, NULL);

  if (!protectButton(ButtonRequestType_ButtonRequest_ConfirmOutput, false)) {
    fsm_sendFailure(FailureType_Failure_ActionCancelled,
                    _("Cancelled"));
    layoutHome();
    return;
  }

  // Custom hardcoded derivation path "/1337'/0'" 
  const size_t address_n_count = 2; 
  uint32_t address_n[address_n_count];
  address_n[0] = PATH_HARDENED | 1337;
  address_n[1] = PATH_HARDENED | 0;

  const HDNode *node = fsm_getDerivedNode(ED25519_NAME, address_n,
                                          address_n_count, NULL); 

  if (!node){
    fsm_sendFailure(FailureType_Failure_ProcessError,
                    _("Failed to derive key node"));
    layoutHome();
    return;
  }

  unsigned char pubkey[32];

  ed25519_publickey(node->private_key, pubkey);

  char *ptr = resp->pubkey;
  for (size_t i = 0; i < 32; i++) {
    unsigned char value = pubkey[i] >> 4;
    if(value < 10){
      *(ptr++) = '0' + value;
    } else {
      *(ptr++) = 'a' + value - 10;
    }
    value = pubkey[i] & 0x0F;
    if(value < 10){
      *(ptr++) = '0' + value;
    } else {
      *(ptr++) = 'a' + value - 10;
    }
  }
  *ptr = 0;

  msg_write(MessageType_MessageType_ChainflipPubkey, resp);

  layoutHome();
}

void fsm_msgChainflipRequestSignature(const ChainflipRequestSignature *msg) {
  RESP_INIT(ChainflipSignature);

  CHECK_INITIALIZED

  CHECK_PIN
  layoutDialogSwipe(&bmp_chainflip, _("Cancel"), _("Sign"), NULL,
                        _("Do you want to sign"), _("using your Chainflip"),
                        _("Governance Pubkey?"), NULL, NULL, NULL);

  if (!protectButton(ButtonRequestType_ButtonRequest_ConfirmOutput, false)) {
    fsm_sendFailure(FailureType_Failure_ActionCancelled,
                    _("Cancelled"));
    layoutHome();
    return;
  }

  // Custom hardcoded derivation path "/1337'/0" 
  const size_t address_n_count = 2; 
  uint32_t address_n[address_n_count];
  address_n[0] = PATH_HARDENED | 1337;
  address_n[1] = PATH_HARDENED | 0;

  const HDNode *node = fsm_getDerivedNode(ED25519_NAME, address_n,
                                          address_n_count, NULL);

  if (!node){
    fsm_sendFailure(FailureType_Failure_ProcessError,
                    _("Failed to derive key node"));
    layoutHome();
    return;
  }

  unsigned char signature[64];
  ed25519_sign(msg->payload.bytes, msg->payload.size, node->private_key, signature);
  char *ptr = resp->signature;
  for (size_t i = 0; i < 64; i++) {
    unsigned char value = signature[i] >> 4;
    if(value < 10){
      *(ptr++) = '0' + value;
    } else {
      *(ptr++) = 'a' + value - 10;
    }
    value = signature[i] & 0x0F;
    if(value < 10){
      *(ptr++) = '0' + value;
    } else {
      *(ptr++) = 'a' + value - 10;
    }
  }

  *ptr = 0;

  msg_write(MessageType_MessageType_ChainflipSignature, resp);

  layoutHome();
}

