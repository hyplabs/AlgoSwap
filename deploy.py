import os
import base64
import time

from algosdk.v2client import algod, indexer
from algosdk.future import transaction
from algosdk import encoding, account, mnemonic, error
from pyteal import compileTeal, Mode

from contracts import manager
from contracts import validator

ALGOD_ENDPOINT = os.environ['ALGOD_ENDPOINT']
ALGOD_TOKEN = os.environ['ALGOD_TOKEN']
INDEXER_ENDPOINT = os.environ['INDEXER_ENDPOINT']
INDEXER_TOKEN = os.environ['INDEXER_TOKEN']

DEVELOPER_ACCOUNT_PRIVATE_KEY = mnemonic.to_private_key(
    os.environ['DEVELOPER_ACCOUNT_PRIVATE_KEY'])
DEVELOPER_ACCOUNT_ADDRESS = account.address_from_private_key(
    DEVELOPER_ACCOUNT_PRIVATE_KEY)
ZERO_ADDRESS = encoding.encode_address(bytes(32))

TEST_ACCOUNT_PRIVATE_KEY = mnemonic.to_private_key(
    os.environ['TEST_ACCOUNT_PRIVATE_KEY'])
TEST_ACCOUNT_ADDRESS = account.address_from_private_key(
    TEST_ACCOUNT_PRIVATE_KEY)

TOKEN1_UNIT_NAME = "TOKEN1"
TOKEN1_ASSET_NAME = "AlgoSwap Token 1 Test Asset"
TOKEN1_AMOUNT = 1000
TOKEN1_DECIMALS = 0
TOKEN2_UNIT_NAME = "TOKEN2"
TOKEN2_ASSET_NAME = "AlgoSwap Token 2 Test Asset"
TOKEN2_AMOUNT = 1000
TOKEN2_DECIMALS = 0
LIQUIDITY_TOKEN_UNIT_NAME = "T1T2"
LIQUIDITY_TOKEN_ASSET_NAME = "AlgoSwap Token1/Token2"
LIQUIDITY_TOKEN_AMOUNT = 1000
LIQUIDITY_TOKEN_DECIMALS = 0


algod_client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ENDPOINT, headers={
    "x-api-key": ALGOD_TOKEN})
indexer_client = indexer.IndexerClient(INDEXER_TOKEN, INDEXER_ENDPOINT, headers={
    "x-api-key": INDEXER_TOKEN})


def wait_for_transaction(transaction_id):
    suggested_params = algod_client.suggested_params()
    algod_client.status_after_block(suggested_params.first + 2)
    result = indexer_client.search_transactions(txid=transaction_id)
    assert len(result['transactions']) == 1, result
    return result['transactions'][0]


def compile_exchange_validator():
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

    with open('./build/validator_approval.teal', 'w') as f:
        f.write(validator_approve_teal_code)
    with open('./build/validator_clear.teal', 'w') as f:
        f.write(validator_clear_teal_code)

    print()

    return validator_approve_code, validator_clear_code


def compile_exchange_manager():
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

    with open('./build/manager_approval.teal', 'w') as f:
        f.write(manager_approve_teal_code)
    with open('./build/manager_clear.teal', 'w') as f:
        f.write(manager_clear_teal_code)

    print()

    return manager_approve_code, manager_clear_code


def compile_exchange_escrow():
    from contracts import escrow

    print("Compiling exchange escrow logicsig...")
    escrow_logicsig_teal_code = compileTeal(
        escrow.logicsig(), Mode.Application)
    compile_response = algod_client.compile(escrow_logicsig_teal_code)
    escrow_logicsig = compile_response['result']
    escrow_logicsig_bytes = base64.b64decode(escrow_logicsig)
    ESCROW_BYTECODE_LEN = len(escrow_logicsig_bytes)
    ESCROW_ADDRESS = compile_response['hash']
    print(
        f"Exchange Escrow | {ESCROW_BYTECODE_LEN}/1000 bytes ({ESCROW_ADDRESS})")

    with open('./build/escrow.teal', 'w') as f:
        f.write(escrow_logicsig_teal_code)

    with open("./build/escrow_logicsig", "w") as f:
        f.write(escrow_logicsig)

    print(f"Escrow logicsig compiled with address {ESCROW_ADDRESS}")

    print()

    return escrow_logicsig


def deploy_exchange_validator(validator_approve_code, validator_clear_code):
    print("Deploying exchange validator application...")

    create_validator_transaction = transaction.ApplicationCreateTxn(
        sender=DEVELOPER_ACCOUNT_ADDRESS,
        sp=algod_client.suggested_params(),
        on_complete=transaction.OnComplete.NoOpOC,
        approval_program=validator_approve_code,
        clear_program=validator_clear_code,
        global_schema=transaction.StateSchema(num_uints=0, num_byte_slices=1),
        local_schema=None,
    ).sign(DEVELOPER_ACCOUNT_PRIVATE_KEY)

    tx_id = algod_client.send_transaction(create_validator_transaction)
    validator_app_id = wait_for_transaction(tx_id)['created-application-index']
    print(
        f"Exchange Validator deployed with Application ID: {validator_app_id} (Txn ID: https://testnet.algoexplorer.io/tx/{tx_id})"
    )

    print()

    return validator_app_id


def deploy_exchange_manager(manager_approve_code, manager_clear_code):
    print("Deploying exchange manager application...")

    create_manager_transaction = transaction.ApplicationCreateTxn(
        sender=DEVELOPER_ACCOUNT_ADDRESS,
        sp=algod_client.suggested_params(),
        on_complete=transaction.OnComplete.NoOpOC,
        approval_program=manager_approve_code,
        clear_program=manager_clear_code,
        global_schema=transaction.StateSchema(num_uints=0, num_byte_slices=1),
        local_schema=transaction.StateSchema(num_uints=10, num_byte_slices=0),
    ).sign(DEVELOPER_ACCOUNT_PRIVATE_KEY)
    tx_id = algod_client.send_transaction(create_manager_transaction)
    manager_app_id = wait_for_transaction(tx_id)['created-application-index']
    print(
        f"Exchange Manager deployed with Application ID: {manager_app_id} (Txn ID: https://testnet.algoexplorer.io/tx/{tx_id})"
    )

    print()

    return manager_app_id


def deploy_token1_token2():
    print(
        f"Deploying tokens {TOKEN1_ASSET_NAME} ({TOKEN1_UNIT_NAME}) and {TOKEN2_ASSET_NAME} ({TOKEN2_UNIT_NAME})..."
    )

    txn_1 = transaction.AssetConfigTxn(
        sender=DEVELOPER_ACCOUNT_ADDRESS,
        sp=algod_client.suggested_params(),
        total=TOKEN1_AMOUNT,
        default_frozen=False,
        unit_name=TOKEN1_UNIT_NAME,
        asset_name=TOKEN1_ASSET_NAME,
        manager=DEVELOPER_ACCOUNT_ADDRESS,
        reserve=DEVELOPER_ACCOUNT_ADDRESS,
        freeze=DEVELOPER_ACCOUNT_ADDRESS,
        clawback=DEVELOPER_ACCOUNT_ADDRESS,
        url=f"https://algoswap.io/{TOKEN1_UNIT_NAME}",
        decimals=TOKEN1_DECIMALS
    ).sign(DEVELOPER_ACCOUNT_PRIVATE_KEY)

    txn_2 = transaction.AssetConfigTxn(
        sender=DEVELOPER_ACCOUNT_ADDRESS,
        sp=algod_client.suggested_params(),
        total=TOKEN2_AMOUNT,
        default_frozen=False,
        unit_name=TOKEN2_UNIT_NAME,
        asset_name=TOKEN2_ASSET_NAME,
        manager=DEVELOPER_ACCOUNT_ADDRESS,
        reserve=DEVELOPER_ACCOUNT_ADDRESS,
        freeze=DEVELOPER_ACCOUNT_ADDRESS,
        clawback=DEVELOPER_ACCOUNT_ADDRESS,
        url=f"https://algoswap.io/{TOKEN2_UNIT_NAME}",
        decimals=TOKEN2_DECIMALS
    ).sign(DEVELOPER_ACCOUNT_PRIVATE_KEY)

    tx_id_1 = algod_client.send_transaction(txn_1)
    tx_id_2 = algod_client.send_transaction(txn_2)

    token_1_asset_id = wait_for_transaction(tx_id_1)['created-asset-index']
    token_2_asset_id = wait_for_transaction(tx_id_2)['created-asset-index']

    print(
        f"Deployed {TOKEN1_ASSET_NAME} ({TOKEN1_UNIT_NAME}) with Asset ID: {token_1_asset_id} | Tx ID: https://testnet.algoexplorer.io/tx/{tx_id_1}"
    )
    print(
        f"Deployed {TOKEN2_ASSET_NAME} ({TOKEN2_UNIT_NAME}) with Asset ID: {token_2_asset_id} | Tx ID: https://testnet.algoexplorer.io/tx/{tx_id_2}"
    )

    print()

    return token_1_asset_id, token_2_asset_id


def deploy_liquidity_pair_token():
    print(
        f"Deploying token {LIQUIDITY_TOKEN_ASSET_NAME} ({LIQUIDITY_TOKEN_UNIT_NAME})..."
    )

    txn = transaction.AssetConfigTxn(
        sender=DEVELOPER_ACCOUNT_ADDRESS,
        sp=algod_client.suggested_params(),
        total=LIQUIDITY_TOKEN_AMOUNT,
        default_frozen=False,
        unit_name=LIQUIDITY_TOKEN_UNIT_NAME,
        asset_name=LIQUIDITY_TOKEN_ASSET_NAME,
        manager=DEVELOPER_ACCOUNT_ADDRESS,
        reserve=DEVELOPER_ACCOUNT_ADDRESS,
        freeze=DEVELOPER_ACCOUNT_ADDRESS,
        clawback=DEVELOPER_ACCOUNT_ADDRESS,
        url=f"https://algoswap.io/{LIQUIDITY_TOKEN_UNIT_NAME}",
        decimals=LIQUIDITY_TOKEN_DECIMALS
    ).sign(DEVELOPER_ACCOUNT_PRIVATE_KEY)

    tx_id = algod_client.send_transaction(txn)

    liquidity_token_asset_id = int(
        wait_for_transaction(tx_id)['created-asset-index'])

    print(
        f"Deployed {LIQUIDITY_TOKEN_ASSET_NAME} ({LIQUIDITY_TOKEN_UNIT_NAME}) with Asset ID: {liquidity_token_asset_id} | Tx ID: https://testnet.algoexplorer.io/tx/{tx_id}"
    )

    print()

    return liquidity_token_asset_id


def opt_escrow_into_token(escrow_logicsig, token_idx):
    print(
        f"Opting Escrow into Token with Asset ID: {token_idx}..."
    )
    program = base64.b64decode(escrow_logicsig)

    lsig = transaction.LogicSig(program)

    txn = transaction.AssetTransferTxn(
        sender=lsig.address(),
        sp=algod_client.suggested_params(),
        receiver=lsig.address(),
        amt=0,
        index=token_idx,
    )

    lsig_txn = transaction.LogicSigTransaction(txn, lsig)

    tx_id = algod_client.send_transaction(lsig_txn)

    wait_for_transaction(tx_id)

    print(
        f"Opted Escrow into Token with Asset ID: {token_idx} successfully! Tx ID: https://testnet.algoexplorer.io/tx/{tx_id}"
    )

    print()


def opt_escrow_into_manager(escrow_logicsig, manager_app_id, liquidity_token_asset_id, token1_asset_id, token2_asset_id):
    print("Opting Escrow into Manager contract...")

    program = base64.b64decode(escrow_logicsig)

    lsig = transaction.LogicSig(program)

    args = [
        liquidity_token_asset_id.to_bytes(8, 'big'),
        token1_asset_id.to_bytes(8, 'big'),
        token2_asset_id.to_bytes(8, 'big')
    ]

    txn = transaction.ApplicationOptInTxn(
        sender=lsig.address(),
        sp=algod_client.suggested_params(),
        index=manager_app_id,
        app_args=args
    )

    lsig_txn = transaction.LogicSigTransaction(txn, lsig)

    tx_id = algod_client.send_transaction(lsig_txn)

    wait_for_transaction(tx_id)

    print(
        f"Opted Escrow into Manager contract successfully! Tx ID: https://testnet.algoexplorer.io/tx/{tx_id}"
    )

    print()


def opt_user_into_contract(app_id):
    print(
        f"Opting user into contract with App ID: {app_id}..."
    )

    txn = transaction.ApplicationOptInTxn(
        sender=TEST_ACCOUNT_ADDRESS,
        sp=algod_client.suggested_params(),
        index=app_id
    ).sign(TEST_ACCOUNT_PRIVATE_KEY)

    tx_id = algod_client.send_transaction(txn)

    wait_for_transaction(tx_id)

    print(
        f"Opted user into contract with App ID: {app_id} successfully! Tx ID: https://testnet.algoexplorer.io/tx/{tx_id}"
    )

    print()


def opt_user_into_token(asset_id):
    print(
        f"Opting user into token with Asset ID: {asset_id}..."
    )

    txn = transaction.AssetTransferTxn(
        sender=TEST_ACCOUNT_ADDRESS,
        sp=algod_client.suggested_params(),
        receiver=TEST_ACCOUNT_ADDRESS,
        amt=0,
        index=asset_id
    ).sign(TEST_ACCOUNT_PRIVATE_KEY)

    tx_id = algod_client.send_transaction(txn)

    wait_for_transaction(tx_id)

    print(
        f"Opted user into token with Asset ID: {asset_id} successfully! Tx ID: https://testnet.algoexplorer.io/tx/{tx_id}"
    )

    print()


def transfer_liquidity_token_to_escrow(liquidity_token_asset_id, escrow_logicsig):
    print(
        f"Transferring {LIQUIDITY_TOKEN_AMOUNT} liquidity token with Asset ID: {liquidity_token_asset_id} to Escrow..."
    )

    program = base64.b64decode(escrow_logicsig)

    lsig = transaction.LogicSig(program)

    txn = transaction.AssetTransferTxn(
        sender=DEVELOPER_ACCOUNT_ADDRESS,
        sp=algod_client.suggested_params(),
        receiver=lsig.address(),
        amt=LIQUIDITY_TOKEN_AMOUNT,
        index=liquidity_token_asset_id
    ).sign(DEVELOPER_ACCOUNT_PRIVATE_KEY)

    tx_id = algod_client.send_transaction(txn)

    wait_for_transaction(tx_id)

    print(
        f"Transferred {LIQUIDITY_TOKEN_AMOUNT} liquidity token with Asset ID: {liquidity_token_asset_id} to Escrow successfully! Tx ID: https://testnet.algoexplorer.io/tx/{tx_id}"
    )

    print()


def transfer_token1_token2_to_user(token1_asset_id, token2_asset_id):
    print(
        f"Transferring {int(TOKEN1_AMOUNT/2)} {TOKEN1_ASSET_NAME} ({TOKEN1_UNIT_NAME}) with Asset ID: {token1_asset_id} and {int(TOKEN2_AMOUNT/2)} {TOKEN2_ASSET_NAME} ({TOKEN2_UNIT_NAME}) with Asset ID: {token2_asset_id} to User..."
    )

    txn_1 = transaction.AssetTransferTxn(
        sender=DEVELOPER_ACCOUNT_ADDRESS,
        sp=algod_client.suggested_params(),
        receiver=TEST_ACCOUNT_ADDRESS,
        amt=int(TOKEN1_AMOUNT/2),
        index=token1_asset_id
    ).sign(DEVELOPER_ACCOUNT_PRIVATE_KEY)

    txn_2 = transaction.AssetTransferTxn(
        sender=DEVELOPER_ACCOUNT_ADDRESS,
        sp=algod_client.suggested_params(),
        receiver=TEST_ACCOUNT_ADDRESS,
        amt=int(TOKEN2_AMOUNT/2),
        index=token2_asset_id
    ).sign(DEVELOPER_ACCOUNT_PRIVATE_KEY)

    tx_id_1 = algod_client.send_transaction(txn_1)
    tx_id_2 = algod_client.send_transaction(txn_2)

    wait_for_transaction(tx_id_1)
    wait_for_transaction(tx_id_2)

    print(
        f"Transferred {int(TOKEN1_AMOUNT/2)} {TOKEN1_ASSET_NAME} ({TOKEN1_UNIT_NAME}) with Asset ID: {token1_asset_id} to User successfully! Tx ID: https://testnet.algoexplorer.io/tx/{tx_id_1}"
    )

    print(
        f"Transferred {int(TOKEN2_AMOUNT/2)} {TOKEN2_ASSET_NAME} ({TOKEN2_UNIT_NAME}) with Asset ID: {token2_asset_id} to User successfully! Tx ID: https://testnet.algoexplorer.io/tx/{tx_id_2}"
    )   

    print()

if __name__ == "__main__":
    print("Starting deployment process...")

    validator_approve_code, validator_clear_code = compile_exchange_validator()

    manager_approve_code, manager_clear_code = compile_exchange_manager()

    # validator_app_id = deploy_exchange_validator(
    #     validator_approve_code, validator_clear_code)

    # manager_app_id = deploy_exchange_manager(
    #     manager_approve_code, manager_clear_code)

    # token1_asset_id, token2_asset_id = deploy_token1_token2()

    # liquidity_token_asset_id = deploy_liquidity_pair_token()

    # params = algod_client.suggested_params()

    # print("Please update the Escrow contract with the following:")
    # input(f"Validator App ID = {validator_app_id}")
    # input(f"Manager App ID = {manager_app_id}")
    # input(f"Token 1 Asset ID = {token1_asset_id}")
    # input(f"Token 2 Asset ID = {token2_asset_id}")
    # input(f"Liquidity Token Asset ID = {liquidity_token_asset_id}")
    # input(f"Last Valid Round = {params.last + 100}")

    # escrow_logicsig = compile_exchange_escrow()

    # input("Please fund the Escrow account with $ALGO to continue")

    # opt_escrow_into_token(escrow_logicsig, token1_asset_id)
    # opt_escrow_into_token(escrow_logicsig, token2_asset_id)
    # opt_escrow_into_token(escrow_logicsig, liquidity_token_asset_id)

    # opt_escrow_into_manager(escrow_logicsig, manager_app_id,
    #                         liquidity_token_asset_id, token1_asset_id, token2_asset_id)

    # opt_user_into_contract(validator_app_id)
    # opt_user_into_contract(manager_app_id)

    # opt_user_into_token(token1_asset_id)
    # opt_user_into_token(token2_asset_id)
    # opt_user_into_token(liquidity_token_asset_id)

    # transfer_liquidity_token_to_escrow(liquidity_token_asset_id, escrow_logicsig)
    # transfer_token1_token2_to_user(token1_asset_id, token2_asset_id)

    print("Deployment completed successfully!")
