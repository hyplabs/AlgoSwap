#!/usr/bin/env python3

from pyteal import compileTeal, Seq, App, Assert, Txn, Gtxn, TxnType, Btoi, Bytes, Int, Return, If, Cond, And, Or, Not, Global, Mode, OnComplete, Concat, AssetHolding, AssetParam

# Tmpl Constants
swap_fee = Int(45)
protocol_fee = Int(5)

# Keys
KEY_CREATOR = Bytes("C")

# Transaction Types
TRANSACTION_TYPE_SWAP_DEPOSIT_TOKEN1_TO_TOKEN2 = Bytes("s1")
TRANSACTION_TYPE_SWAP_DEPOSIT_TOKEN2_TO_TOKEN1 = Bytes("s2")
TRANSACTION_TYPE_ADD_LIQUIDITY_DEPOSIT = Bytes("a")
TRANSACTION_TYPE_WITHDRAW_LIQUIDITY = Bytes("w")
TRANSACTION_TYPE_REFUND = Bytes("r")
TRANSACTION_TYPE_WITHDRAW_PROTOCOL_FEES = Bytes("p")


def approval_program():

    # On application create, put the creator key in global storage
    on_create = Seq([
        App.globalPut(KEY_CREATOR, Txn.sender()),
        Int(1)
    ])

    # Closeout on validator does nothing
    on_closeout = Return(Int(1))

    # Opt in on validator does nothing
    on_opt_in = Return(Int(1))

    on_swap_deposit = Assert(And(
        # Group has 3 transactions
        Global.group_size() == Int(3),
        # This ApplicationCall is the 1st transaction
        Txn.group_index() == Int(0),
        # No additional actions are needed from this transaction
        Txn.on_completion() == OnComplete.NoOp,
        # Has one additional account attached
        Txn.accounts.length() == Int(1),
        # Has two application arguments
        Txn.application_args.length() == Int(2),
        # Second txn to manager
        # Is of type ApplicationCall
        Gtxn[1].type_enum() == TxnType.ApplicationCall,
        # No additional actions needed
        Gtxn[1].on_completion() == OnComplete.NoOp,
        # Has one additional account attached
        Gtxn[1].accounts.length() == Int(1),
        # Has two application arguments
        Gtxn[1].application_args.length() == Int(2),
        # Additional account is same in both calls
        Txn.accounts[1] == Gtxn[1].accounts[1],
        # Application argument is same in both calls
        Txn.application_args[0] == Gtxn[1].application_args[0],
        Txn.application_args[1] == Gtxn[1].application_args[1],
        # Third txn to escrow
        # Is of type AssetTransfer
        Gtxn[2].type_enum() == TxnType.AssetTransfer,
        Gtxn[2].sender() == Global.zero_address(),
        Gtxn[2].asset_receiver() == Txn.accounts[1],
    ))

    program = Cond(
        [Txn.application_id() == Int(0), on_create],
        [Txn.on_completion() == OnComplete.CloseOut, on_closeout],
        [Txn.on_completion() == OnComplete.OptIn, on_opt_in],
        [Txn.application_args[0] ==
            TRANSACTION_TYPE_SWAP_DEPOSIT_TOKEN1_TO_TOKEN2, on_swap_deposit],
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
    return


def clear_program():
    return Int(1)


if __name__ == "__main__":
    with open('validator_approval.teal', 'w') as f:
        compiled = compileTeal(approval_program(), Mode.Application)
        f.write(compiled)

    with open('validator_clear.teal', 'w') as f:
        compiled = compileTeal(clear_program(), Mode.Application)
        f.write(compiled)
