import os
import base64

from algosdk.v2client import algod, indexer
from algosdk import mnemonic, account, encoding
from algosdk.future import transaction

ALGOD_ENDPOINT = os.environ['ALGOD_ENDPOINT']
ALGOD_TOKEN = os.environ['ALGOD_TOKEN']
INDEXER_ENDPOINT = os.environ['INDEXER_ENDPOINT']
INDEXER_TOKEN = os.environ['INDEXER_TOKEN']
TEST_ACCOUNT_PRIVATE_KEY = mnemonic.to_private_key(os.environ['TEST_ACCOUNT_PRIVATE_KEY'])
TEST_ACCOUNT_ADDRESS = account.address_from_private_key(TEST_ACCOUNT_PRIVATE_KEY)

ESCROW_LOGICSIG = os.environ['ESCROW_LOGICSIG']
ESCROW_ADDRESS = os.environ['ESCROW_ADDRESS']

VALIDATOR_INDEX = int(os.environ['VALIDATOR_INDEX'])
MANAGER_INDEX = int(os.environ['MANAGER_INDEX'])
TOKEN1_INDEX = int(os.environ['TOKEN1_INDEX'])
TOKEN2_INDEX = int(os.environ['TOKEN2_INDEX'])
LIQUIDITY_TOKEN_INDEX = int(os.environ['LIQUIDITY_TOKEN_INDEX'])

algod_client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ENDPOINT, headers={
  "x-api-key": ALGOD_TOKEN
})
indexer_client = indexer.IndexerClient(INDEXER_TOKEN, INDEXER_ENDPOINT, headers={
  "x-api-key": INDEXER_TOKEN
})

def get_token1_refund():
  print("Attempting to get refund of Token 1 from Escrow...")

  encoded_app_args = [
    bytes("r", "utf-8")
  ]

  # Calculate unused_token1
  unused_token1 = 0
  account_info = algod_client.account_info(TEST_ACCOUNT_ADDRESS)
  local_state = account_info['apps-local-state']
  for block in local_state:
    if block['id'] == MANAGER_INDEX:
      for kvs in block['key-value']:
        decoded_key = base64.b64decode(kvs['key'])
        prefix_bytes = decoded_key[:2]
        prefix_key = prefix_bytes.decode('utf-8')
        addr_bytes = decoded_key[2:]
        b32_encoded_addr = base64.b32encode(addr_bytes).decode('utf-8')
        escrow_addr = encoding.encode_address(base64.b32decode(b32_encoded_addr))

        if (prefix_key == "U1" and ESCROW_ADDRESS == escrow_addr):
          unused_token1 = int(kvs['value']['uint'])

  print(f"User unused Token 1 is {unused_token1}")

  if unused_token1 != 0:
    # Transaction to Validator
    txn_1 = transaction.ApplicationCallTxn(
      sender=TEST_ACCOUNT_ADDRESS,
      sp=algod_client.suggested_params(),
      index=VALIDATOR_INDEX,
      on_complete=transaction.OnComplete.NoOpOC,
      accounts=[ESCROW_ADDRESS],
      app_args=encoded_app_args
    )

    # Transaction to Manager
    txn_2 = transaction.ApplicationCallTxn(
      sender=TEST_ACCOUNT_ADDRESS,
      sp=algod_client.suggested_params(),
      index=MANAGER_INDEX,
      on_complete=transaction.OnComplete.NoOpOC,
      accounts=[ESCROW_ADDRESS],
      app_args=encoded_app_args
    )

    # Make LogicSig
    program = base64.b64decode(ESCROW_LOGICSIG)
    lsig = transaction.LogicSig(program)

    # Transaction to get refund of Token 1 from Escrow
    txn_3 = transaction.AssetTransferTxn(
      sender=ESCROW_ADDRESS,
      sp=algod_client.suggested_params(),
      receiver=TEST_ACCOUNT_ADDRESS,
      amt=unused_token1,
      index=TOKEN1_INDEX
    )

    # Get group ID and assign to transactions
    gid = transaction.calculate_group_id([txn_1, txn_2, txn_3])
    txn_1.group = gid
    txn_2.group = gid
    txn_3.group = gid

    # Sign transactions
    stxn_1 = txn_1.sign(TEST_ACCOUNT_PRIVATE_KEY)
    stxn_2 = txn_2.sign(TEST_ACCOUNT_PRIVATE_KEY)
    stxn_3 = transaction.LogicSigTransaction(txn_3, lsig)

    # Broadcast the transactions
    signed_txns = [stxn_1, stxn_2, stxn_3]
    tx_id = algod_client.send_transactions(signed_txns)

    print(f"Got refund of Token 1 from AlgoSwap to User successfully! Tx ID: https://testnet.algoexplorer.io/tx/{tx_id}")

  print()

def get_token2_refund():
  print("Attempting to get refund of Token 2 from Escrow...")

  encoded_app_args = [
    bytes("r", "utf-8")
  ]

  # Calculate unused_token2
  unused_token2 = 0
  account_info = algod_client.account_info(TEST_ACCOUNT_ADDRESS)
  local_state = account_info['apps-local-state']
  for block in local_state:
    if block['id'] == MANAGER_INDEX:
      for kvs in block['key-value']:
        decoded_key = base64.b64decode(kvs['key'])
        prefix_bytes = decoded_key[:2]
        prefix_key = prefix_bytes.decode('utf-8')
        addr_bytes = decoded_key[2:]
        b32_encoded_addr = base64.b32encode(addr_bytes).decode('utf-8')
        escrow_addr = encoding.encode_address(base64.b32decode(b32_encoded_addr))

        if (prefix_key == "U2" and ESCROW_ADDRESS == escrow_addr):
          unused_token2 = int(kvs['value']['uint'])

  print(f"User unused Token 2 is {unused_token2}")

  if unused_token2 != 0:
    # Transaction to Validator
    txn_1 = transaction.ApplicationCallTxn(
      sender=TEST_ACCOUNT_ADDRESS,
      sp=algod_client.suggested_params(),
      index=VALIDATOR_INDEX,
      on_complete=transaction.OnComplete.NoOpOC,
      accounts=[ESCROW_ADDRESS],
      app_args=encoded_app_args
    )

    # Transaction to Manager
    txn_2 = transaction.ApplicationCallTxn(
      sender=TEST_ACCOUNT_ADDRESS,
      sp=algod_client.suggested_params(),
      index=MANAGER_INDEX,
      on_complete=transaction.OnComplete.NoOpOC,
      accounts=[ESCROW_ADDRESS],
      app_args=encoded_app_args
    )

    # Make LogicSig
    program = base64.b64decode(ESCROW_LOGICSIG)
    lsig = transaction.LogicSig(program)

    # Transaction to get refund of Token 2 from Escrow
    txn_3 = transaction.AssetTransferTxn(
      sender=ESCROW_ADDRESS,
      sp=algod_client.suggested_params(),
      receiver=TEST_ACCOUNT_ADDRESS,
      amt=unused_token2,
      index=TOKEN2_INDEX
    )

    # Get group ID and assign to transactions
    gid = transaction.calculate_group_id([txn_1, txn_2, txn_3])
    txn_1.group = gid
    txn_2.group = gid
    txn_3.group = gid

    # Sign transactions
    stxn_1 = txn_1.sign(TEST_ACCOUNT_PRIVATE_KEY)
    stxn_2 = txn_2.sign(TEST_ACCOUNT_PRIVATE_KEY)
    stxn_3 = transaction.LogicSigTransaction(txn_3, lsig)

    # Broadcast the transactions
    signed_txns = [stxn_1, stxn_2, stxn_3]
    tx_id = algod_client.send_transactions(signed_txns)

    print(f"Got refund of Token 2 from AlgoSwap to User successfully! Tx ID: https://testnet.algoexplorer.io/tx/{tx_id}")

  print()

def get_liquidity_token_refund():
  print("Attempting to get refund of liquidity tokens from Escrow...")

  encoded_app_args = [
    bytes("r", "utf-8")
  ]

  # Calculate unused_liquidity
  unused_liquidity = 0
  results = algod_client.account_info(TEST_ACCOUNT_ADDRESS)
  local_state = results['apps-local-state']
  for block in local_state:
    if block['id'] == MANAGER_INDEX:
      for kvs in block['key-value']:
        decoded_key = base64.b64decode(kvs['key'])
        prefix_bytes = decoded_key[:2]
        prefix_key = prefix_bytes.decode('utf-8')
        addr_bytes = decoded_key[2:]
        b32_encoded_addr = base64.b32encode(addr_bytes).decode('utf-8')
        escrow_addr = encoding.encode_address(base64.b32decode(b32_encoded_addr))

        if (prefix_key == "UL" and ESCROW_ADDRESS == escrow_addr):
          unused_liquidity = int(kvs['value']['uint'])
  
  print(f"User unused liquidity is {unused_liquidity}")

  if unused_liquidity != 0:
    # Transaction to Validator
    txn_1 = transaction.ApplicationCallTxn(
      sender=TEST_ACCOUNT_ADDRESS,
      sp=algod_client.suggested_params(),
      index=VALIDATOR_INDEX,
      on_complete=transaction.OnComplete.NoOpOC,
      accounts=[ESCROW_ADDRESS],
      app_args=encoded_app_args
    )

    # Transaction to Manager
    txn_2 = transaction.ApplicationCallTxn(
      sender=TEST_ACCOUNT_ADDRESS,
      sp=algod_client.suggested_params(),
      index=MANAGER_INDEX,
      on_complete=transaction.OnComplete.NoOpOC,
      accounts=[ESCROW_ADDRESS],
      app_args=encoded_app_args
    )

    # Make LogicSig
    program = base64.b64decode(ESCROW_LOGICSIG)
    lsig = transaction.LogicSig(program)

    # Transaction to get Liquidity Token refund
    txn_3 = transaction.AssetTransferTxn(
      sender=ESCROW_ADDRESS,
      sp=algod_client.suggested_params(),
      receiver=TEST_ACCOUNT_ADDRESS,
      amt=unused_liquidity,
      index=LIQUIDITY_TOKEN_INDEX
    )

    # Get group ID and assign to transactions
    gid = transaction.calculate_group_id([txn_1, txn_2, txn_3])
    txn_1.group = gid
    txn_2.group = gid
    txn_3.group = gid

    # Sign transactions
    stxn_1 = txn_1.sign(TEST_ACCOUNT_PRIVATE_KEY)
    stxn_2 = txn_2.sign(TEST_ACCOUNT_PRIVATE_KEY)
    stxn_3 = transaction.LogicSigTransaction(txn_3, lsig)

    # Broadcast the transactions
    signed_txns = [stxn_1, stxn_2, stxn_3]
    tx_id = algod_client.send_transactions(signed_txns)

    print(f"Got refund of liquidity tokens from AlgoSwap to User successfully! Tx ID: https://testnet.algoexplorer.io/tx/{tx_id}")

  print()