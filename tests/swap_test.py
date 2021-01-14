import os
import pytest

from algosdk.v2client import algod, indexer
from algosdk import mnemonic, account
from algosdk.future import transaction

ALGOD_ENDPOINT = os.environ['ALGOD_ENDPOINT']
ALGOD_TOKEN = os.environ['ALGOD_TOKEN']
INDEXER_ENDPOINT = os.environ['INDEXER_ENVIRON']
INDEXER_TOKEN = os.environ['INDEXER_TOKEN']
TEST_ACCOUNT_PRIVATE_KEY = mnemonic.to_private_key(os.environ['TEST_ACCOUNT_PRIVATE_KEY'])
TEST_ACCOUNT_ADDRESS = account.address_from_private_key(TEST_ACCOUNT_PRIVATE_KEY)

VALIDATOR_ADDRESS = "XRLYLAQKSCOW36TXJVKS2OB2ZUATZTOXI5XCVH4FYSSAQJJB4S3TPI7LWY"
MANAGER_ADDRESS = "OAXWLSC5IGC3S5HNTGUD7B3SZWDBD6WX3AJAXAQ2UKOWXTQCMCQ5PWOAFE"
ESCROW_ADDRESS = "POXWP2YDBS33LH7KOH6VNZOAKAFTGDCFMI5B6WAZZPEU7L27UXLDIMSZU4"

ESCROW_LOGICSIG = ""
VALIDATOR_INDEX = 13377480
MANAGER_INDEX = 13377481

TOKEN1_INDEX = 123 # TODO: Update
TOKEN2_INDEX = 234 # TODO: Update

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

class TestSwaps:
  def test_swap_token1_for_token2():
    txn_1 = transaction.ApplicationNoOpTxn(
      sender=TEST_ACCOUNT_ADDRESS,
      sp=algod_client.suggested_params(),
      index=VALIDATOR_INDEX,
      app_args=["s1", "5"],
      accounts=[ESCROW_ADDRESS]
    )

    txn_2 = transaction.ApplicationNoOpTxn(
      sender=TEST_ACCOUNT_ADDRESS,
      sp=algod_client.suggested_params(),
      index=MANAGER_INDEX,
      app_args=["s1", "5"],
      accounts=[ESCROW_ADDRESS]
    )

    txn_3 = transaction.AssetTransferTxn(
      sender=TEST_ACCOUNT_ADDRESS,
      sp=algod_client.suggested_params(),
      receiver=ESCROW_ADDRESS,
      amt=5,
      index=TOKEN1_INDEX
    )

    gid = transaction.calculate_group_id([txn_1, txn_2, txn_3])
    txn_1.group = gid
    txn_2.group = gid
    txn_3.group = gid

    stxn_1 = txn_1.sign(TEST_ACCOUNT_PRIVATE_KEY)
    stxn_2 = txn_2.sign(TEST_ACCOUNT_PRIVATE_KEY)
    stxn_3 = txn_3.sign(TEST_ACCOUNT_PRIVATE_KEY)

    signed_txns = [stxn_1, stxn_2, stxn_3]

    tx_id = algod_client.send_transactions(signed_txns)

    txn_response = wait_for_transaction(tx_id)
    print(txn_response)

  def test_swap_token2_for_token1():
    txn_1 = transaction.ApplicationNoOpTxn(
      sender=TEST_ACCOUNT_ADDRESS,
      sp=algod_client.suggested_params(),
      index=VALIDATOR_INDEX,
      app_args=["s2", "5"],
      accounts=[ESCROW_ADDRESS]
    )

    txn_2 = transaction.ApplicationNoOpTxn(
      sender=TEST_ACCOUNT_ADDRESS,
      sp=algod_client.suggested_params(),
      index=MANAGER_INDEX,
      app_args=["s2", "5"],
      accounts=[ESCROW_ADDRESS]
    )

    txn_3 = transaction.AssetTransferTxn(
      sender=TEST_ACCOUNT_ADDRESS,
      sp=algod_client.suggested_params(),
      receiver=ESCROW_ADDRESS,
      amt=5,
      index=TOKEN2_INDEX
    )

    gid = transaction.calculate_group_id([txn_1, txn_2, txn_3])
    txn_1.group = gid
    txn_2.group = gid
    txn_3.group = gid

    stxn_1 = txn_1.sign(TEST_ACCOUNT_PRIVATE_KEY)
    stxn_2 = txn_2.sign(TEST_ACCOUNT_PRIVATE_KEY)
    stxn_3 = txn_3.sign(TEST_ACCOUNT_PRIVATE_KEY)

    signed_txns = [stxn_1, stxn_2, stxn_3]

    tx_id = algod_client.send_transactions(signed_txns)

    txn_response = wait_for_transaction(tx_id)
    print(txn_response)
  