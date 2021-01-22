import os
import base64

from algosdk.v2client import algod, indexer
from algosdk import mnemonic, account, encoding
from algosdk.future import transaction

ALGOD_ENDPOINT = os.environ['ALGOD_ENDPOINT']
ALGOD_TOKEN = os.environ['ALGOD_TOKEN']
INDEXER_ENDPOINT = os.environ['INDEXER_ENDPOINT']
INDEXER_TOKEN = os.environ['INDEXER_TOKEN']
DEVELOPER_ACCOUNT_PRIVATE_KEY = mnemonic.to_private_key(os.environ['DEVELOPER_ACCOUNT_PRIVATE_KEY'])
DEVELOPER_ACCOUNT_ADDRESS = mnemonic.to_private_key(DEVELOPER_ACCOUNT_PRIVATE_KEY)


ESCROW_LOGICSIG = os.environ['ESCROW_LOGICSIG']
ESCROW_ADDRESS = os.environ['ESCROW_ADDRESS']

VALIDATOR_INDEX = int(os.environ['VALIDATOR_INDEX'])
MANAGER_INDEX = int(os.environ['MANAGER_INDEX'])
TOKEN1_INDEX = int(os.environ['TOKEN1_INDEX'])
TOKEN2_INDEX = int(os.environ['TOKEN2_INDEX'])

algod_client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ENDPOINT, headers={
  "x-api-key": ALGOD_TOKEN
})
indexer_client = indexer.IndexerClient(INDEXER_TOKEN, INDEXER_ENDPOINT, headers={
  "x-api-key": INDEXER_TOKEN
})

def wait_for_transaction(transaction_id):
  suggested_params = algod_client.suggested_params()
  algod_client.status_after_block(suggested_params.first + 4)
  result = indexer_client.search_transactions(txid=transaction_id)
  assert len(result['transactions']) == 1, result
  return result['transactions'][0]

def withdraw_protocol_fees():
  print("Building withdraw protocol fees atomic transaction group...")

  encoded_app_args = [
    bytes("p", "utf-8")
  ]

  # Get unclaimed TOKEN1 and TOKEN2 protocol fees
  protocol_unused_token1 = protocol_unused_token2 = 0
  account_info = algod_client.account_info(ESCROW_ADDRESS)
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

        if (prefix_key == "P1" and ESCROW_ADDRESS == escrow_addr):
          protocol_unused_token1 = kvs['value']['uint']
        elif (prefix_key == "P2" and ESCROW_ADDRESS == escrow_addr):
          protocol_unused_token2 = kvs['value']['uint']
  
  print(f"Unused Protocol Fees is Token 1 = {protocol_unused_token1} and Token 2 = {protocol_unused_token2}")

  # Transaction to Validator
  txn_1 = transaction.ApplicationCallTxn(
    sender=DEVELOPER_ACCOUNT_ADDRESS,
    sp=algod_client.suggested_params(),
    index=VALIDATOR_INDEX,
    on_complete=transaction.OnComplete.NoOpOC,
    accounts=[ESCROW_ADDRESS],
    app_args=encoded_app_args
  )

  # Transaction to Manager
  txn_2 = transaction.ApplicationCallTxn(
    sender=DEVELOPER_ACCOUNT_ADDRESS,
    sp=algod_client.suggested_params(),
    index=MANAGER_INDEX,
    on_complete=transaction.OnComplete.NoOpOC,
    accounts=[ESCROW_ADDRESS],
    app_args=encoded_app_args
  )

  # Transaction to send Token 1 from Escrow to Developer
  txn_3 = transaction.AssetTransferTxn(
    sender=ESCROW_ADDRESS,
    sp=algod_client.suggested_params(),
    receiver=DEVELOPER_ACCOUNT_ADDRESS,
    amt=protocol_unused_token1,
    index=TOKEN1_INDEX
  )

  # Transaction to send Token 2 from Escrow to Developer
  txn_4 = transaction.AssetTransferTxn(
    sender=ESCROW_ADDRESS,
    sp=algod_client.suggested_params(),
    receiver=DEVELOPER_ACCOUNT_ADDRESS,
    amt=protocol_unused_token2,
    index=TOKEN2_INDEX
  )

  # Make Logicsig
  program = base64.b64decode(ESCROW_LOGICSIG)
  lsig = transaction.LogicSig(program)

  # Get group ID and assign to transactions
  gid = transaction.calculate_group_id([txn_1, txn_2, txn_3, txn_4])
  txn_1.group = gid
  txn_2.group = gid
  txn_3.group = gid
  txn_4.group = gid

  # Sign transactions
  stxn_1 = txn_1.sign(DEVELOPER_ACCOUNT_PRIVATE_KEY)
  stxn_2 = txn_2.sign(DEVELOPER_ACCOUNT_PRIVATE_KEY)
  stxn_3 = transaction.LogicSigTransaction(txn_3, lsig)
  stxn_4 = transaction.LogicSigTransaction(txn_4, lsig)

  # Broadcast the transactions
  signed_txns = [stxn_1, stxn_2, stxn_3, stxn_4]
  tx_id = algod_client.send_transactions(signed_txns)

  # Wait for transaction
  wait_for_transaction(tx_id)

  print(f"Withdrew protocol fees for Token 1 and Token 2 from AlgoSwap to Developer successfully! Tx ID: https://testnet.algoexplorer.io/tx/{tx_id}")

if __name__ == "__main__":
  withdraw_protocol_fees()