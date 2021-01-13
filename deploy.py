import os
import base64

from algosdk.v2client import algod, indexer
from algosdk.future import transaction
from algosdk import encoding, account, mnemonic, error
from pyteal import compileTeal, Mode

from contracts import manager
from contracts import validator
from contracts import escrow

ALGOD_ENDPOINT = os.environ['ALGOD_ENDPOINT']
ALGOD_TOKEN = os.environ['ALGOD_TOKEN']
INDEXER_ENDPOINT = os.environ['INDEXER_ENDPOINT']
INDEXER_TOKEN = os.environ['INDEXER_TOKEN']
DEVELOPER_ACCOUNT_PRIVATE_KEY = mnemonic.to_private_key(
    os.environ['DEVELOPER_ACCOUNT_PRIVATE_KEY'])
DEVELOPER_ACCOUNT_ADDRESS = account.address_from_private_key(
    DEVELOPER_ACCOUNT_PRIVATE_KEY)
ZERO_ADDRESS = encoding.encode_address(bytes(32))

algod_client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ENDPOINT, headers={
                                 "x-api-key": ALGOD_TOKEN})
indexer_client = indexer.IndexerClient(
    INDEXER_TOKEN, INDEXER_ENDPOINT, headers={"x-api-key": INDEXER_TOKEN})


def wait_for_transaction(transaction_id):
    suggested_params = algod_client.suggested_params()
    algod_client.status_after_block(suggested_params.first + 2)
    result = indexer_client.search_transactions(txid=transaction_id)
    assert len(result['transactions']) == 1, result
    return result['transactions'][0]
    # {
    #     'application-transaction': {'accounts': [], 'application-args': [], 'application-id': 0, 'approval-program': 'AiAFAAIBAwQmEAFzAWEBdwFyAXABQwJVMQJVMgJVTAJMVAJCMQJUMQJUMgJCMgJQMQJQMjEYIhJAADgxGSMSQAA6MRkkEkAASjYaACgSQACKNhoAKRJAAIY2GgAqEkAAgjYaACsSQAB+NhoAJwQSQADwACcFMQBnJEIBeiInBmIiEiInB2IiEhAiJwhiIhIQQgFjMRsiEkAACDEbJRJAABcAIicJNhoAF2YiJwoiZiInCCJmJEIAICInCTYaAGYiJws2GgFmIicMNhoCZiInCiJmIicNImYkQgEbJEIBFyRCARMkQgEPMgQjEjEWIhIQMRkiEhAxHSQSEDQAEDMBECEEEhAzAQA2HAASEDMBEzIDEhAzARUyAxIQQAABADMBETQBEjMBEiInBmIOEEAAEzMBETQCEjMBEiInB2IOEEAAEAAkJwYiJwZiMwESCWZCAAwkJwciJwdiMwESCWYkQgCUMgQlEjEWIhIQMQAnBWQSEDEZIhIQMR0kEhA0ABAzARAhBBIQMwEANhwAEhAzARE0ARIQMwESJCcOYg4QMwETMgMSEDMBFTIDEhAzAhAhBBIQMwIANhwAEhAzAhE0AhIQMwISJCcPYg4QMwITMgMSEDMCFTIDEhBAAAEAJCcOJCcOYjMBEglmJCcPJCcPYjMCEglmJA==', 'clear-state-program': 'AiABASI=', 'foreign-apps': [], 'foreign-assets': [], 'global-state-schema': {'num-byte-slice': 1, 'num-uint': 0}, 'local-state-schema': {'num-byte-slice': 1, 'num-uint': 5}, 'on-completion': 'noop'},
    #     'close-rewards': 0,
    #     'closing-amount': 0,
    #     'confirmed-round': 9439716,
    #     'created-application-index': 12284334,
    #     'fee': 1000,
    #     'first-valid': 9439714,
    #     'genesis-hash': 'SGO1GKSzyE7IEPItTxCByw9x8FmnrCDexi9/cOUJOiI=',
    #     'genesis-id': 'testnet-v1.0',
    #     'global-state-delta': [{'key': 'Qw==', 'value': {'action': 1, 'bytes': 'ItRhv40mcIYSmNgwLCxKOdWj7Fea+LuqZygf2OW7lJ4=', 'uint': 0}}],
    #     'id': 'OXUCAGHYIHEBOBGT6LQV77QDYBJU4YWSLJEXJEBWQ6RNDC4HAJHQ',
    #     'intra-round-offset': 0,
    #     'last-valid': 9440714,
    #     'receiver-rewards': 0,
    #     'round-time': 1600932628,
    #     'sender': 'ELKGDP4NEZYIMEUY3AYCYLCKHHK2H3CXTL4LXKTHFAP5RZN3SSPMW7CLVQ',
    #     'sender-rewards': 0,
    #     'signature': {'sig': 'wnwF16tQd5zgbuVVWf3Ih43Xa8ljfhp/lT/BIH5tJVEOHQSokxXvkDPqKLj83sPp97sUeGhzaFnWj0Wb0oACAA=='},
    #     'tx-type': 'appl'
    # }


if __name__ == "__main__":
    print("Compiling exchange manager application...")
    manager_approve_teal_code = compileTeal(
        manager.approval_program(), Mode.Application)
    compile_response = algod_client.compile(manager_approve_teal_code)
    manager_approve_code = base64.b64decode(compile_response['result'])
    print(
        f"Exchange manager approve program currently uses {len(manager_approve_code)} of 1000 bytes")
    manager_clear_teal_code = compileTeal(
        manager.clear_program(), Mode.Application)
    compile_response = algod_client.compile(manager_clear_teal_code)
    manager_clear_code = base64.b64decode(compile_response['result'])
    print(
        f"Exchange manager clear program currently uses {len(manager_clear_code)} of 1000 bytes")

    print("Compiling exchange validator application...")
    validator_approve_teal_code = compileTeal(
        validator.approval_program(), Mode.Application)
    compile_response = algod_client.compile(validator_approve_teal_code)
    validator_approve_code = base64.b64decode(compile_response['result'])
    print(
        f"Exchange validator approve program currently uses {len(validator_approve_code)} of 1000 bytes")
    validator_clear_teal_code = compileTeal(
        validator.clear_program(), Mode.Application)
    compile_response = algod_client.compile(validator_clear_teal_code)
    validator_clear_code = base64.b64decode(compile_response['result'])
    print(
        f"Exchange validator clear program currently uses {len(validator_clear_code)} of 1000 bytes")

    # print("Deploying exchange manager application...")
    # create_application_transaction = transaction.ApplicationCreateTxn(
    #     sender=DEVELOPER_ACCOUNT_ADDRESS,
    #     sp=algod_client.suggested_params(),
    #     on_complete=transaction.OnComplete.NoOpOC,
    #     approval_program=manager_approve_code,
    #     clear_program=manager_clear_code,
    #     global_schema=transaction.StateSchema(num_uints=0, num_byte_slices=1),
    #     local_schema=transaction.StateSchema(num_uints=7, num_byte_slices=1),
    # ).sign(DEVELOPER_ACCOUNT_PRIVATE_KEY)
    # transaction_id = algod_client.send_transaction(
    #     create_application_transaction)
    # exchange_application_id = wait_for_transaction(
    #     transaction_id)['created-application-index']
    # print(
    #     f"Exchange manager deployed with application ID {exchange_application_id} (transaction: {transaction_id})")

    # # deploy escrow
    # escrow_teal_code = compileTeal(escrow.logicsig(), Mode.Application)
    # compile_response = algod_client.compile(escrow_teal_code)
    # ESCROW_ADDRESS = compile_response['hash']
    # print("ESCROW_ADDRESS:", ESCROW_ADDRESS)
    # print(
    #     f"Escrow logicsig currently uses {len(base64.b64decode(compile_response['result']))} of 1000 bytes")

    # token1_name, token2_name = "USDt", "USDC"  # TODO
    # create_asset_transaction = transaction.AssetConfigTxn(
    #     sender=DEVELOPER_ACCOUNT_ADDRESS,
    #     sp=algod_client.suggested_params(),
    #     strict_empty_address_check=False,
    #     total=1000,
    #     default_frozen=False,
    #     unit_name=f'ALGOSWAP',
    #     asset_name=f'AlgoSwap {token1_name}-{token2_name} Liquidity',
    #     # TODO: change this to zero address (note that that change will break something in sig validation)
    #     manager=DEVELOPER_ACCOUNT_ADDRESS,
    #     reserve=ESCROW_ADDRESS,
    #     # TODO: change this to zero address (note that that change will break something in sig validation)
    #     freeze=DEVELOPER_ACCOUNT_ADDRESS,
    #     # TODO: change this to zero address (note that that change will break something in sig validation)
    #     clawback=DEVELOPER_ACCOUNT_ADDRESS,
    #     url="https://git.io/JU232",
    #     metadata_hash=b"12345678901234567890123456789012",
    #     decimals=8,
    # ).sign(DEVELOPER_ACCOUNT_PRIVATE_KEY)
    # print(create_asset_transaction.dictify())
    # transaction_id = algod_client.send_transaction(create_asset_transaction)
    # print(wait_for_transaction(transaction_id))
    # liquidity_asset_id = wait_for_transaction(transaction_id)
    # print(
    #     f"Asset \"AlgoSwap {token1_name}-{token2_name} Liquidity\" deployed with asset ID {liquidity_asset_id} (transaction: {transaction_id})")
