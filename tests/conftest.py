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

VALIDATOR_ADDRESS = "XRLYLAQKSCOW36TXJVKS2OB2ZUATZTOXI5XCVH4FYSSAQJJB4S3TPI7LWY"
MANAGER_ADDRESS = "OAXWLSC5IGC3S5HNTGUD7B3SZWDBD6WX3AJAXAQ2UKOWXTQCMCQ5PWOAFE"
ESCROW_ADDRESS = "POXWP2YDBS33LH7KOH6VNZOAKAFTGDCFMI5B6WAZZPEU7L27UXLDIMSZU4"

ESCROW_LOGICSIG = ""
VALIDATOR_INDEX = 13377480
MANAGER_INDEX = 13377481

algod_client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ENDPOINT, headers={
  "x-api-key": ALGOD_TOKEN
})
indexer_client = indexer.IndexerClient(INDEXER_TOKEN, INDEXER_ENDPOINT, headers={
  "x-api-key": INDEXER_TOKEN
})

token_1 = {
  "unit_name": "ABC",
  "asset_name": "AlgoSwap ABC Test Asset"
}

token_2 = {
  "unit_name": "DEF",
  "asset_name": "AlgoSwap DEF Test Asset"
}

def wait_for_transaction(transaction_id):
    suggested_params = algod_client.suggested_params()
    algod_client.status_after_block(suggested_params.first + 2)
    result = indexer_client.search_transactions(txid=transaction_id)
    assert len(result['transactions']) == 1, result
    return result['transactions'][0]

def deploy_tokens():
  print(f"Deploying tokens {token_1['unit_name']} and {token_2['unit_name']}...")

  txn_1 = transaction.AssetConfigTxn(
    sender=TEST_ACCOUNT_ADDRESS,
    sp=algod_client.suggested_params(),
    total=10000000000000000000,
    default_frozen=False,
    unit_name=token_1['unit_name'],
    asset_name=token_1['asset_name'],
    manager=TEST_ACCOUNT_ADDRESS,
    reserve=TEST_ACCOUNT_ADDRESS,
    freeze=TEST_ACCOUNT_ADDRESS,
    clawback=TEST_ACCOUNT_ADDRESS,
    url="https://example.com/abc",
    decimals=8
  ).sign(TEST_ACCOUNT_PRIVATE_KEY)

  txn_2 = transaction.AssetConfigTxn(
    sender=TEST_ACCOUNT_ADDRESS,
    sp=algod_client.suggested_params(),
    total=10000000000000000000,
    default_frozen=False,
    unit_name=token_2['unit_name'],
    asset_name=token_2['asset_name'],
    manager=TEST_ACCOUNT_ADDRESS,
    reserve=TEST_ACCOUNT_ADDRESS,
    freeze=TEST_ACCOUNT_ADDRESS,
    clawback=TEST_ACCOUNT_ADDRESS,
    url="https://example.com/def",
    decimals=8
  ).sign(TEST_ACCOUNT_PRIVATE_KEY)

  tx_id_1 = algod_client.send_transaction(txn_1)
  tx_id_2 = algod_client.send_transaction(txn_2)

  token_1_asset_id = wait_for_transaction(tx_id_1)['created-asset-index']
  token_2_asset_id = wait_for_transaction(tx_id_2)['created-asset-index']


  print(
    f"Deployed {token_1['asset_name']} ({token_1['unit_name']}) with Asset ID: {token_1_asset_id} | Tx ID: {tx_id_1}"
  )
  print(
    f"Deployed {token_2['asset_name']} ({token_2['unit_name']}) with Asset ID: {token_2_asset_id} | Tx ID: {tx_id_2}"
  )

def user_opt_in():
  print("Opting user into Validator and Manager contracts...")
  # Opt into Validator
  txn_1 = transaction.ApplicationOptInTxn(
    sender=TEST_ACCOUNT_ADDRESS,
    sp=algod_client.suggested_params(),
    index=VALIDATOR_ADDRESS
  ).sign(TEST_ACCOUNT_PRIVATE_KEY)

  # Opt into Manager
  txn_2 = transaction.ApplicationOptInTxn(
    sender=TEST_ACCOUNT_ADDRESS,
    sp=algod_client.suggested_params(),
    index=MANAGER_ADDRESS
  ).sign(TEST_ACCOUNT_PRIVATE_KEY)

  tx_id_1 = algod_client.send_transaction(txn_1)
  tx_id_2 = algod_client.send_transaction(txn_2)

  print(
    f"Opted user into Validator contract with Tx ID: {tx_id_1}"
  )

  print(
    f"Opted user into Manager contract with Tx ID: {tx_id_2}"
  )

def escrow_opt_in():
  # TODO: How to sign transaction from escrow account to opt in to manager?
  # Escrow account does not have a private key - only a logic signature
  pass

def pytest_sessionstart(session):
  deploy_tokens()
