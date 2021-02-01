import os
import base64

from algosdk.v2client import algod, indexer
from algosdk import mnemonic, account, encoding
from algosdk.future import transaction

from helpers import *

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

TOKEN2_AMOUNT = 10000000

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

def swap_token2_for_token1():
  print("Building swap Token 2 for Token 1 atomic transaction group...")

  encoded_app_args = [
    bytes("s2", "utf-8"),
    (8088850).to_bytes(8, 'big')
  ]

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

  # Transaction to send Token 2 to Escrow
  txn_3 = transaction.AssetTransferTxn(
    sender=TEST_ACCOUNT_ADDRESS,
    sp=algod_client.suggested_params(),
    receiver=ESCROW_ADDRESS,
    amt=TOKEN2_AMOUNT,
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
  stxn_3 = txn_3.sign(TEST_ACCOUNT_PRIVATE_KEY)

  # Broadcast the transactions
  signed_txns = [stxn_1, stxn_2, stxn_3]
  tx_id = algod_client.send_transactions(signed_txns)

  # Wait for transaction
  wait_for_transaction(tx_id)

  print(f"Swap Token 2 for Token 1 transaction sent from User to AlgoSwap successfully! Tx ID: https://testnet.algoexplorer.io/tx/{tx_id}")

  print()

if __name__ == "__main__":
  swap_token2_for_token1()

  get_token1_refund()