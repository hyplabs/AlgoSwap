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


if __name__ == "__main__":
    print("Compiling exchange manager application...")
    manager_approve_teal_code = compileTeal(
        manager.approval_program(), Mode.Application)
    compile_response = algod_client.compile(manager_approve_teal_code)
    manager_approve_code = base64.b64decode(compile_response['result'])
    MANAGER_APPROVE_BYTECODE_LEN = len(manager_approve_code)
    MANAGER_APPROVE_ADDRESS = compile_response['hash']

    manager_clear_teal_code = compileTeal(
        manager.clear_program(), Mode.Application)
    compile_response = algod_client.compile(manager_clear_teal_code)
    manager_clear_code = base64.b64decode(compile_response['result'])
    MANAGER_CLEAR_BYTECODE_LEN = len(manager_clear_code)
    MANAGER_CLEAR_ADDRESS = compile_response['hash']
    print(
        f"Exchange Manager | Approval: {MANAGER_APPROVE_BYTECODE_LEN}/1000 bytes ({MANAGER_APPROVE_ADDRESS}) | Clear: {MANAGER_CLEAR_BYTECODE_LEN}/1000 bytes ({MANAGER_CLEAR_ADDRESS})")

    with open('manager_approval.teal', 'w') as f:
        f.write(manager_approve_teal_code)
    
    with open('manager_clear.teal', 'w') as f:
        f.write(manager_clear_teal_code)

    print()

    print("Compiling exchange validator application...")
    validator_approve_teal_code = compileTeal(
        validator.approval_program(), Mode.Application)
    compile_response = algod_client.compile(validator_approve_teal_code)
    validator_approve_code = base64.b64decode(compile_response['result'])
    VALIDATOR_APPROVE_BYTECODE_LEN = len(validator_approve_code)
    VALIDATOR_APPROVE_ADDRESS = compile_response['hash']

    validator_clear_teal_code = compileTeal(
        validator.clear_program(), Mode.Application)
    compile_response = algod_client.compile(validator_clear_teal_code)
    validator_clear_code = base64.b64decode(compile_response['result'])
    VALIDATOR_CLEAR_BYTECODE_LEN = len(validator_clear_code)
    VALIDATOR_CLEAR_ADDRESS = compile_response['hash']
    print(
        f"Exchange Validator | Approval: {VALIDATOR_APPROVE_BYTECODE_LEN}/1000 bytes ({VALIDATOR_APPROVE_ADDRESS}) | Clear: {VALIDATOR_CLEAR_BYTECODE_LEN}/1000 bytes ({VALIDATOR_CLEAR_ADDRESS})")

    with open('validator_approval.teal', 'w') as f:
        f.write(validator_approve_teal_code)
    
    with open('validator_clear.teal', 'w') as f:
        f.write(validator_clear_teal_code)

    print()

    print("Compiling exchange escrow logicsig...")
    escrow_logicsig_code = compileTeal(escrow.logicsig(), Mode.Application)
    compile_response = algod_client.compile(escrow_logicsig_code)
    escrow_compiled_code = base64.b64decode(compile_response['result'])
    ESCROW_BYTECODE_LEN = len(escrow_compiled_code)
    ESCROW_ADDRESS = compile_response['hash']
    print(
        f"Exchange Escrow | {ESCROW_BYTECODE_LEN}/1000 bytes ({ESCROW_ADDRESS})")

    with open('escrow.teal', 'w') as f:
        f.write(escrow_logicsig_code)
    

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
