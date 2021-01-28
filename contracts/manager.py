#!/usr/bin/env python3

from pyteal import *

# 45 parts out of 10000 from each swap goes to liquidity providers
# 5 parts out of 10000 from each swap goes to the developers

KEY_TOTAL_TOKEN1_BALANCE = Bytes("B1")
KEY_TOTAL_TOKEN2_BALANCE = Bytes("B2")
KEY_TOTAL_LIQUIDITY_TOKEN_DISTRIBUTED = Bytes("LD")
KEY_PROTOCOL_UNUSED_TOKEN1 = Bytes("P1")
KEY_PROTOCOL_UNUSED_TOKEN2 = Bytes("P2")
KEY_TOKEN1 = Bytes("T1")
KEY_TOKEN2 = Bytes("T2")
KEY_LIQUIDITY_TOKEN = Bytes("LT")
KEY_USER_UNUSED_TOKEN1 = Bytes("U1")
KEY_USER_UNUSED_TOKEN2 = Bytes("U2")
KEY_USER_UNUSED_LIQUIDITY = Bytes("UL")
TRANSACTION_TYPE_SWAP_DEPOSIT_TOKEN1_TO_TOKEN2 = Bytes("s1")
TRANSACTION_TYPE_SWAP_DEPOSIT_TOKEN2_TO_TOKEN1 = Bytes("s2")
TRANSACTION_TYPE_ADD_LIQUIDITY_DEPOSIT = Bytes("a")
TRANSACTION_TYPE_WITHDRAW_LIQUIDITY = Bytes("w")
TRANSACTION_TYPE_REFUND = Bytes("r")
TRANSACTION_TYPE_WITHDRAW_PROTOCOL_FEES = Bytes("p")


def approval_program():
    """
    This smart contract implements the Manager part of the AlgoSwap DEX.
    It maintains the global and local storage for users and escrow contracts
    that are opted into the AlgoSwap protocol for every possible atomic
    transaction group that AlgoSwap supports (Swap Token 1 for Token 2,
    Swap Token 2 for Token 1, Add Liquidity, Withdraw Liquidity, Withdraw 
    Protocol Fees, and Refund).

    Any atomic transaction group MUST have a transaction to the manager
    smart contract as the second transaction of the group to proceed.

    Commands:
        s1  Swap Token 1 for Token 2 in a liquidity pair
        s2  Swap Token 2 for Token 1 in a liquidity pair
        a   Add liquidity to a liquidity pool
        w   Withdraw liquidity from a liquidity pool
        r   Get a refund of unused tokens
        p   Withdraw protocol fees (Developer only)
    """

    # Read from additional account
    read_key_token1 = App.localGet(Int(1), KEY_TOKEN1)
    read_key_token2 = App.localGet(Int(1), KEY_TOKEN2)
    read_key_liquidity_token = App.localGet(Int(1), KEY_LIQUIDITY_TOKEN)

    read_key_total_token1_bal = App.localGet(Int(1), KEY_TOTAL_TOKEN1_BALANCE)
    read_key_total_token2_bal = App.localGet(Int(1), KEY_TOTAL_TOKEN2_BALANCE)
    read_key_total_liquidity_token_distributed = App.localGet(Int(1), KEY_TOTAL_LIQUIDITY_TOKEN_DISTRIBUTED)

    read_protocol_unused_token1 = App.localGet(Int(1), KEY_PROTOCOL_UNUSED_TOKEN1)
    read_protocol_unused_token2 = App.localGet(Int(1), KEY_PROTOCOL_UNUSED_TOKEN2)

    # Write to additional account
    def write_key_total_token1_bal(bal: Int): return App.localPut(Int(1), KEY_TOTAL_TOKEN1_BALANCE, bal)
    def write_key_total_token2_bal(bal: Int): return App.localPut(Int(1), KEY_TOTAL_TOKEN2_BALANCE, bal)

    def write_key_total_liquidity_token_distributed(bal: Int): return App.localPut(Int(1), KEY_TOTAL_LIQUIDITY_TOKEN_DISTRIBUTED, bal)

    def write_protocol_unused_token1(amount: Int): return App.localPut(Int(1), KEY_PROTOCOL_UNUSED_TOKEN1, amount)
    def write_protocol_unused_token2(amount: Int): return App.localPut(Int(1), KEY_PROTOCOL_UNUSED_TOKEN2, amount)

    # Read from sender account
    def read_user_unused_token1(address: Bytes): return App.localGet(Int(0), Concat(KEY_USER_UNUSED_TOKEN1, address))
    def read_user_unused_token2(address: Bytes): return App.localGet(Int(0), Concat(KEY_USER_UNUSED_TOKEN2, address))
    def read_user_unused_liquidity(address: Bytes): return App.localGet(Int(0), Concat(KEY_USER_UNUSED_LIQUIDITY, address))

    # Write to sender account
    def write_user_unused_token1(address: Bytes, amount: Int): return App.localPut(Int(0), Concat(KEY_USER_UNUSED_TOKEN1, address), amount)
    def write_user_unused_token2(address: Bytes, amount: Int): return App.localPut(Int(0), Concat(KEY_USER_UNUSED_TOKEN2, address), amount)
    def write_user_unused_liquidity(address: Bytes, amount: Int): return App.localPut(Int(0), Concat(KEY_USER_UNUSED_LIQUIDITY, address), amount)

    # Scratch Vars
    scratchvar_token1_used = ScratchVar(TealType.uint64)
    scratchvar_token2_used = ScratchVar(TealType.uint64)
    scratchvar_total_token1_bal = ScratchVar(TealType.uint64)
    scratchvar_total_token2_bal = ScratchVar(TealType.uint64)
    scratchvar_total_liquidity_token_distributed = ScratchVar(TealType.uint64)
    scratchvar_swap_token2_output = ScratchVar(TealType.uint64)
    scratchvar_swap_token1_output = ScratchVar(TealType.uint64)
    scratchvar_token1_available = ScratchVar(TealType.uint64)
    scratchvar_token2_available = ScratchVar(TealType.uint64)
    scratchvar_new_liquidity = ScratchVar(TealType.uint64)
    scratchvar_temp = ScratchVar(TealType.uint64)

    on_create = Int(1)

    on_closeout = Int(1)

    on_opt_in = If(Txn.application_args.length() == Int(3), 
        Seq([
            # initialize sender's local state as an escrow
            App.localPut(Int(0), KEY_LIQUIDITY_TOKEN, Btoi(Txn.application_args[0])),
            App.localPut(Int(0), KEY_TOKEN1, Btoi(Txn.application_args[1])),
            App.localPut(Int(0), KEY_TOKEN2, Btoi(Txn.application_args[2])),
            App.localPut(Int(0), KEY_TOTAL_TOKEN1_BALANCE, Int(1)),
            App.localPut(Int(0), KEY_TOTAL_TOKEN2_BALANCE, Int(1)),
            Int(1),
        ]),
        Int(1)
    )

    # 199/200 = 9950/10000 = 0.45% (45/10000) swap fee and 0.05% (5/10000) protocol fee
    def swap_token_input_minus_fees(asset_amount: Int): return (asset_amount * Int(199)) / Int(200)

    def swap_token2_output(token1_input_minus_fees: Int):
        return read_key_total_token2_bal - (read_key_total_token1_bal * read_key_total_token2_bal) / (read_key_total_token1_bal + token1_input_minus_fees)

    on_swap_deposit = Seq([
        scratchvar_swap_token2_output.store(swap_token2_output(swap_token_input_minus_fees(Gtxn[2].asset_amount()))),
        
        # Add protocol fee to the protocol fees account
        # PROTOCOL_UNUSED_TOKEN1 = PROTOCOL_UNUSED_TOKEN1 + token1_input * protocol_fee
        write_protocol_unused_token1(
            read_protocol_unused_token1 + (Gtxn[2].asset_amount() / Int(2000))
        ),
        # Assert token2_output >= min_token2_received_from_algoswap
        Assert(
            scratchvar_swap_token2_output.load() >= Btoi(Txn.application_args[1])
        ),
        # USER_UNUSED_TOKEN2 = USER_UNUSED_TOKEN2 + token2_output
        write_user_unused_token2(
            Txn.accounts[1],
            read_user_unused_token2(Txn.accounts[1]) + scratchvar_swap_token2_output.load()
        ),
        # Update total balance
        # TOTAL_TOKEN1_BALANCE = TOTAL_TOKEN1_BALANCE + (token1_input * swap_fee) + token1_input_minus_fees
        write_key_total_token1_bal(
            read_key_total_token1_bal + ((Gtxn[2].asset_amount() * Int(9)) / Int(10000)) + swap_token_input_minus_fees(Gtxn[2].asset_amount())
        ),
        # TOTAL_TOKEN2_BALANCE = TOTAL_TOKEN2_BALANCE - token2_output
        write_key_total_token2_bal(
            read_key_total_token2_bal - scratchvar_swap_token2_output.load()
        ),
        # successful approval
        Int(1)
    ])

    def swap_token1_output(token2_input_minus_fees: Int):
        return read_key_total_token1_bal - (read_key_total_token1_bal * read_key_total_token2_bal) / (read_key_total_token2_bal + token2_input_minus_fees)


    on_swap_deposit_2 = Seq([
        scratchvar_swap_token1_output.store(swap_token1_output(swap_token_input_minus_fees(Gtxn[1].asset_amount()))),
        # add protocol fee to protocol fees account
        write_protocol_unused_token2(
            read_protocol_unused_token2 + (Gtxn[1].asset_amount() / Int(2000))
        ),
        # assert token 1 output >= min_token1_received_from_algoswap
        Assert(
            scratchvar_swap_token1_output.load() >= Btoi(Txn.application_args[1])
        ),
        # set user unused token1 += token1_output
        write_user_unused_token1(
            Txn.accounts[1],
            read_user_unused_token1(Txn.accounts[1]) + scratchvar_swap_token1_output.load()
        ),
        # update total token2 balance = total_token2_balance + swap fees + swap_token_input_minus_fees
        write_key_total_token2_bal(read_key_total_token2_bal + ((Gtxn[1].asset_amount() * Int(9)) / Int(2000)) + swap_token_input_minus_fees(Gtxn[1].asset_amount())),
        # update total token1 balance
        write_key_total_token1_bal(read_key_total_token1_bal - scratchvar_swap_token1_output.load()),
        # successful approval
        Int(1),
    ])

    def total_liquidity(total_supply: Int, reserve_balance: Int): return total_supply - reserve_balance

    on_add_liquidity_deposit = Seq([
        scratchvar_total_token1_bal.store(read_key_total_token1_bal),
        scratchvar_total_token2_bal.store(read_key_total_token2_bal),
        scratchvar_total_liquidity_token_distributed.store(read_key_total_liquidity_token_distributed),
        If(
            # If TOTAL_LIQUIDITY_TOKEN_DISTRIBUTED = 0
            scratchvar_total_liquidity_token_distributed.load() == Int(0),
            # Then, token1_used = token1_deposit
            # token2_used = token2_deposit
            # new_liquidity = token1_deposit
            Seq([
                scratchvar_token1_used.store(Gtxn[2].asset_amount()),
                scratchvar_token2_used.store(Gtxn[3].asset_amount()),
                scratchvar_new_liquidity.store(Gtxn[2].asset_amount()),
            ]),
            # Else, token1_used = min(token1_deposit, (token2_deposit * TOTAL_TOKEN1_BALANCE / TOTAL_TOKEN2_BALANCE))
            # token2_used = min(token2_deposit, token1_deposit * TOTAL_TOKEN2_BALANCE / TOTAL_TOKEN1_BALANCE)
            Seq([
                scratchvar_temp.store(Gtxn[3].asset_amount() * scratchvar_total_token1_bal.load() / scratchvar_total_token2_bal.load()),
                If(
                    # If token1_deposit is min
                    Gtxn[2].asset_amount() < scratchvar_temp.load(),
                    # token1_used = token1_deposit
                    scratchvar_token1_used.store(Gtxn[2].asset_amount()),
                    # Else, token1_used = (token2_deposit * TOTAL_TOKEN1_BALANCE / TOTAL_TOKEN2_BALANCE))
                    scratchvar_token1_used.store(scratchvar_temp.load()),
                ),
                scratchvar_temp.store(Gtxn[2].asset_amount() * scratchvar_total_token2_bal.load() / scratchvar_total_token1_bal.load()),
                If(
                    # If token2_deposit is min
                    Gtxn[3].asset_amount() < scratchvar_temp.load(),
                    # token2_used = token2_deposit
                    scratchvar_token2_used.store(Gtxn[3].asset_amount()),
                    # Else, token2_used = token1_deposit * TOTAL_TOKEN2_BALANCE / TOTAL_TOKEN1_BALANCE)
                    scratchvar_token2_used.store(scratchvar_temp.load()),
                ),
                scratchvar_new_liquidity.store(scratchvar_total_liquidity_token_distributed.load() * Gtxn[2].asset_amount() / scratchvar_total_token1_bal.load()),
            ])
        ),
        # Assert new_liquidity >= min_liquidity_received_from_algoswap
        Assert(
            scratchvar_new_liquidity.load() >= Btoi(Txn.application_args[1]),
        ),
        # USER_UNUSED_TOKEN1 = USER_UNUSED_TOKEN1 + token1_deposit - token1_used
        # USER_UNUSED_TOKEN1 = USER_UNUSED_TOKEN1 + token1_deposit - (token2_deposit * TOTAL_TOKEN1_BALANCE / TOTAL_TOKEN2_BALANCE)
        write_user_unused_token1(
            Txn.accounts[1],
            read_user_unused_token1(Txn.accounts[1]) + Gtxn[2].asset_amount() - scratchvar_token1_used.load()
        ),
        # token2_used = min(token2_deposit, (token1_deposit * TOTAL_TOKEN2_BALANCE / TOTAL_TOKEN1_BALANCE))
        # If token2_deposit > (token1_deposit * TOTAL_TOKEN2_BALANCE / TOTAL_TOKEN1_BALANCE)
        # USER_UNUSED_TOKEN2 = USER_UNUSED_TOKEN2 + token2_deposit - token2_used
        # USER_UNUSED_TOKEN2 = USER_UNUSED_TOKEN2 + token2_deposit - (token1_deposit * TOTAL_TOKEN2_BALANCE / TOTAL_TOKEN1_BALANCE)
        write_user_unused_token2(
            Txn.accounts[1],
            read_user_unused_token2(Txn.accounts[1]) + Gtxn[3].asset_amount() - scratchvar_token2_used.load()
        ),
        # total_liquidity = Total Supply (LIQUIDITY_TOKEN(ESCROW(TOKEN1, TOKEN2))) - Balance (RESERVE_ADDR(LIQUIDITY_TOKEN(ESCROW(TOKEN1, TOKEN2))))
        # USER_UNUSED_LIQUIDITY = USER_UNUSED_LIQUIDITY + total_liquidity * token1_deposit / TOTAL_TOKEN1_BALANCE
        write_user_unused_liquidity(
            Txn.accounts[1],
            read_user_unused_liquidity(Txn.accounts[1]) + scratchvar_new_liquidity.load()
        ),
        # TOTAL_TOKEN1_BALANCE = TOTAL_TOKEN1_BALANCE + token1_used
        write_key_total_token1_bal(scratchvar_total_token1_bal.load() + scratchvar_token1_used.load()),

        # TOTAL_TOKEN2_BALANCE = TOTAL_TOKEN2_BALANCE + token2_used
        write_key_total_token2_bal(scratchvar_total_token2_bal.load() + scratchvar_token2_used.load()),
        
        # TOTAL_LIQUIDITY_TOKEN_DISTRIBUTED += new_liquidity
        write_key_total_liquidity_token_distributed(scratchvar_total_liquidity_token_distributed.load() + scratchvar_new_liquidity.load()),
        Int(1)
    ])

    on_withdraw_liquidity = Seq([
        # total_liquidity = TOTAL_LIQUIDITY_TOKEN_DISTRIBUTED
        # user_liquidity = Asset Amount (Txn)

        # token1_available = TOTAL_TOKEN1_BALANCE * user_liquidity / total_liquidity
        scratchvar_token1_available.store(read_key_total_token1_bal * Gtxn[2].asset_amount() / read_key_total_liquidity_token_distributed),

        # USER_UNUSED_TOKEN1 = USER_UNUSED_TOKEN1 + token1_available
        write_user_unused_token1(
            Txn.accounts[1],
            read_user_unused_token1(Txn.accounts[1]) + scratchvar_token1_available.load()
        ),
        # token2_available = TOTAL_TOKEN2_BALANCE * user_liquidity / total_liquidity
        scratchvar_token2_available.store(read_key_total_token2_bal * Gtxn[2].asset_amount() / read_key_total_liquidity_token_distributed),

        # USER_UNUSED_TOKEN2 = USER_UNUSED_TOKEN2 + token2_available
        write_user_unused_token2(
            Txn.accounts[1],
            read_user_unused_token2(Txn.accounts[1]) + scratchvar_token2_available.load()
        ),
        # Assert token1_available >= min_token1_received_from_algoswap
        # Assert token2_available >= min_token2_received_from_algoswap
        Assert(
            And(
                scratchvar_token1_available.load() >= Btoi(Txn.application_args[1]),
                scratchvar_token2_available.load() >= Btoi(Txn.application_args[2]),
            )
        ),
        # TOTAL_TOKEN1_BALANCE = TOTAL_TOKEN1_BALANCE - token1_available
        write_key_total_token1_bal(
            read_key_total_token1_bal - scratchvar_token1_available.load()
        ),
        # TOTAL_TOKEN2_BALANCE = TOTAL_TOKEN2_BALANCE - token2_available
        write_key_total_token2_bal(
            read_key_total_token2_bal - scratchvar_token2_available.load()
        ),
        # TOTAL_LIQUIDITY_TOKEN_DISTRIBUTED = TOTAL_LIQUIDITY_TOKEN_DISTRIBUTED - user_liquidity
        write_key_total_liquidity_token_distributed(
            read_key_total_liquidity_token_distributed - Gtxn[2].asset_amount()
        ),
        Int(1)
    ])

    on_refund = Seq([
        Cond([
            # this AssetTransfer is for an available amount of TOKEN1
            And(
                Gtxn[2].xfer_asset() == read_key_token1,
                Gtxn[2].asset_amount() <= read_user_unused_token1(Txn.accounts[1])
            ),
            # unused_token1 = Gtxn[2].asset_amount()
            # USER_UNUSED_TOKEN1 = USER_UNUSED_TOKEN1 - unused_token1
            write_user_unused_token1(
                Txn.accounts[1],
                read_user_unused_token1(Txn.accounts[1]) - Gtxn[2].asset_amount()
            ),
        ], [
            # this AssetTransfer is for an available amount of TOKEN2
            And(
                Gtxn[2].xfer_asset() == read_key_token2,
                Gtxn[2].asset_amount() <= read_user_unused_token2(Txn.accounts[1])
            ),
            # unused_token2 = Gtxn[2].asset_amount()
            # USER_UNUSED_TOKEN2 = USER_UNUSED_TOKEN2 - unused_token2
            write_user_unused_token2(
                Txn.accounts[1],
                read_user_unused_token2(Txn.accounts[1]) - Gtxn[2].asset_amount()
            ),
        ], [
            # this AssetTransfer is for an available amount of LIQUIDITY_TOKEN
            And(
                Gtxn[2].xfer_asset() == read_key_liquidity_token,
                Gtxn[2].asset_amount() <= read_user_unused_liquidity(Txn.accounts[1])
            ),
            # unused_liquidity = Gtxn[2].asset_amount()
            # USER_UNUSED_LIQUIDITY = USER_UNUSED_LIQUIDITY - unused_liquidity
            write_user_unused_liquidity(
                Txn.accounts[1], 
                read_user_unused_liquidity(Txn.accounts[1]) - Gtxn[2].asset_amount()
            ),
        ]),
        Int(1),
    ])

    on_withdraw_protocol_fees = Seq([
        Assert(And(
            # this TOKEN1 AssetTransfer is for an available amount of TOKEN1
            Gtxn[2].asset_amount() <= read_protocol_unused_token1,

            # this TOKEN2 AssetTransfer is for an available amount of TOKEN2
            Gtxn[3].asset_amount() <= read_protocol_unused_token2,
        )),
        # withdraw_token1 = Gtxn[2].asset_amount()
        # PROTOCOL_UNUSED_TOKEN1 = PROTOCOL_UNUSED_TOKEN1 - withdraw_token1
        write_protocol_unused_token1(
            read_protocol_unused_token1 - Gtxn[2].asset_amount()
        ),
        # withdraw_token2 = Gtxn[2].asset_amount()
        # PROTOCOL_UNUSED_TOKEN2 = PROTOCOL_UNUSED_TOKEN2 - withdraw_token2
        write_protocol_unused_token2(
            read_protocol_unused_token2 - Gtxn[3].asset_amount()
        ),
        Int(1),
    ])

    program = Cond(
        [Txn.application_id() == Int(0),
            on_create],
        [Txn.on_completion() == OnComplete.CloseOut,
            on_closeout],
        [Txn.on_completion() == OnComplete.OptIn,
            on_opt_in],
        [Txn.application_args[0] == TRANSACTION_TYPE_SWAP_DEPOSIT_TOKEN1_TO_TOKEN2,
            on_swap_deposit],
        [Txn.application_args[0] == TRANSACTION_TYPE_SWAP_DEPOSIT_TOKEN2_TO_TOKEN1,
            on_swap_deposit_2],
        [Txn.application_args[0] == TRANSACTION_TYPE_ADD_LIQUIDITY_DEPOSIT,
            on_add_liquidity_deposit],
        [Txn.application_args[0] == TRANSACTION_TYPE_WITHDRAW_LIQUIDITY,
            on_withdraw_liquidity],
        [Txn.application_args[0] == TRANSACTION_TYPE_REFUND,
            on_refund],
        [Txn.application_args[0] == TRANSACTION_TYPE_WITHDRAW_PROTOCOL_FEES,
            on_withdraw_protocol_fees],
    )
    return program

def clear_program():
    return Int(1)