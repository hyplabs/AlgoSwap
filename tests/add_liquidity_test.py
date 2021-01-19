import os
import pytest

from algosdk.v2client import algod, indexer
from algosdk import mnemonic, account
from algosdk.future import transaction

ALGOD_ENDPOINT = os.environ['ALGOD_ENDPOINT']
ALGOD_TOKEN = os.environ['ALGOD_TOKEN']
INDEXER_ENDPOINT = os.environ['INDEXER_ENDPOINT']
INDEXER_TOKEN = os.environ['INDEXER_TOKEN']
TEST_ACCOUNT_PRIVATE_KEY = mnemonic.to_private_key(os.environ['TEST_ACCOUNT_PRIVATE_KEY'])
TEST_ACCOUNT_ADDRESS = account.address_from_private_key(TEST_ACCOUNT_PRIVATE_KEY)

VALIDATOR_ADDRESS = os.environ['VALIDATOR_ADDRESS']
MANAGER_ADDRESS = os.environ['MANAGER_ADDRESS']
ESCROW_ADDRESS = os.environ['ESCROW_ADDRESS']

ESCROW_LOGICSIG = os.environ['ESCROW_LOGICSIG']
VALIDATOR_INDEX = int(os.environ['VALIDATOR_INDEX'])
MANAGER_INDEX = int(os.environ['MANAGER_INDEX'])

algod_client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ENDPOINT, headers={
  "x-api-key": ALGOD_TOKEN
})
indexer_client = indexer.IndexerClient(INDEXER_TOKEN, INDEXER_ENDPOINT, headers={
  "x-api-key": INDEXER_TOKEN
})

def wait_for_transaction(transaction_id):
  suggested_params = algod_client.suggested_params()
  algod_client.status_after_block(suggested_params.first + 2)
  result = indexer_client.search_transactions(txid=transaction_id)
  assert len(result['transactions']) == 1, result
  return result['transactions'][0]

