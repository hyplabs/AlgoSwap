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
    on_closeout = Int(1)

    # Opt in on validator does nothing
    on_opt_in = Int(1)

    on_swap_deposit = Seq([
        Assert(
            And(
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
                # Asset sender is zero address
                Gtxn[2].sender() == Global.zero_address(),
                # Asset receiver is attached account
                Gtxn[2].asset_receiver() == Txn.accounts[1],
            )
        ),
        Int(1)
    ])

    on_swap_deposit_2 = Seq([
        Assert(
            And(
                # Group has 3 transactions
                Global.group_size() == Int(3),
                # This ApplicationCall is the first transaction
                Txn.group_index() == Int(0),
                # No additional actions are needed from this transaction
                Txn.on_completion() == OnComplete.NoOp,
                # Has one additional account attached
                Txn.accounts.length() == Int(1),
                # Has two application arguments attached
                Txn.application_args.length() == Int(2),

                # Second txn to Manager

                # Is of type ApplicationCall
                Gtxn[1].type_enum() == TxnType.ApplicationCall,
                # No additional actions needed
                Gtxn[1].on_completion() == OnComplete.NoOp,
                # Has one additional account attached
                Gtxn[1].accounts.length() == Int(1),
                # Has two application arguments attached
                Gtxn[1].application_args.length() == Int(2),
                # Additional account is same as first txn
                Txn.accounts[1] == Gtxn[1].accounts[1],
                # Application arguments are same as first txn
                Txn.application_args[0] == Gtxn[1].application_args[0],
                Txn.application_args[1] == Gtxn[1].application_args[1],

                # Third txn to escrow

                # Is of type AssetTransfer
                Gtxn[2].type_enum() == TxnType.AssetTransfer,
                # Sender is zero address
                Gtxn[2].sender() == Global.zero_address(),
                # Asset receiver is attached account
                Gtxn[2].asset_receiver() == Txn.accounts[1],
            )
        ),
        Int(1)
    ])

    on_add_liquidity_deposit = Seq([
        Assert(
            And(
                # Group has 4 transactions
                Global.group_size() == Int(4),
                # This ApplicationCall is the first transaction
                Txn.group_index() == Int(0),
                # No additional actions needed from this transaction
                Txn.on_completion() == OnComplete.NoOp,
                # Has two additional accounts attached
                Txn.accounts.length() == Int(2),
                # Has two application arguments attached
                Txn.application_args.length() == Int(2),

                # NOTE: No way to check length of foreign assets in PyTeal

                # Second txn to Manager

                # is of type ApplicationCall
                Gtxn[1].type_enum() == TxnType.ApplicationCall,
                # No additional actions needed
                Gtxn[1].on_completion() == OnComplete.NoOp,
                # Has two additional accounts attached
                Gtxn[1].application_args.length() == Int(2),
                # Has two application arguments attached
                Gtxn[1].application_args.length() == Int(2),
                # Additional accounts are same as first txn
                Txn.accounts[1] == Gtxn[1].accounts[1],
                Txn.accounts[2] == Gtxn[1].accounts[2],
                # Application arguments are same as first txn
                Txn.application_args[0] == Gtxn[1].application_args[0],
                Txn.application_args[1] == Gtxn[1].application_args[1],

                # Third txn to Escrow

                # Is of type AssetTransfer
                Gtxn[2].type_enum() == TxnType.AssetTransfer,
                # Asset sender is zero address
                Gtxn[2].sender() == Global.zero_address(),
                # Asset receiver is the escrow account
                Gtxn[2].asset_receiver() == Txn.accounts[1],

                # Fourth txn to Escrow

                # Is of type AssetTransfer
                Gtxn[2].type_enum() == TxnType.AssetTransfer,
                # Asset sender is zero address
                Gtxn[2].sender() == Global.zero_address(),
                # Asset receiver is the escrow account
                Gtxn[2].asset_receiver() == Txn.accounts[1],
            )
        ),
        Int(1)
    ])

    on_withdraw_liquidity = Seq([
        Assert(
            And(
                # Group has 3 transactions
                Global.group_size() == Int(3),
                # This ApplicationCall is the first transaction
                Txn.group_index() == Int(0),
                # No additional actions are needed from this transaction
                Txn.on_completion() == OnComplete.NoOp,
                # Has two additional accounts attached
                Txn.accounts.length() == Int(2),
                # Has three application arguments attached
                Txn.application_args.length() == Int(3),

                # NOTE: No way to check length of foreign assets in PyTeal

                # Second txn to Manager

                # is of type ApplicationCall
                Gtxn[1].type_enum() == TxnType.ApplicationCall,
                # No additional actions needed
                Gtxn[1].on_completion() == OnComplete.NoOp,
                # Has two additional accounts attached
                Gtxn[1].application_args.length() == Int(2),
                # Has three application arguments attached
                Gtxn[1].application_args.length() == Int(3),
                # Additional accounts are same as first txn
                Txn.accounts[1] == Gtxn[1].accounts[1],
                Txn.accounts[2] == Gtxn[1].accounts[2],
                # Application arguments are same as first txn
                Txn.application_args[0] == Gtxn[1].application_args[0],
                Txn.application_args[1] == Gtxn[1].application_args[1],

                # Third txn to Escrow

                # is of type AssetTransfer
                Gtxn[2].type_enum() == TxnType.AssetTransfer,
                # Asset sender is zero address
                Gtxn[2].sender() == Global.zero_address(),
                # Asset receiver is the escrow account
                Gtxn[2].asset_receiver() == Txn.accounts[1],
            )
        ),
        Int(1),
    ])

    on_withdraw_protocol_fees = Seq([
        Assert(
            And(
                # Group has 4 transactions
                Global.group_size() == Int(4),
                # This ApplicationCall is the first transaction
                Txn.group_index() == Int(0),
                # No additional actions needed from this transaction
                Txn.on_completion() == OnComplete.NoOp,
                # Has one additional account attached
                Txn.accounts.length() == Int(1),
                # Has one application argument attached
                Txn.application_args.length() == Int(1),
                # Sender is developer
                Txn.sender() == App.globalGet(KEY_CREATOR),

                # Second txn to Manager

                # is of type ApplicationCall
                Gtxn[1].type_enum() == TxnType.ApplicationCall,
                # No additional actions needed
                Gtxn[1].on_completion() == OnComplete.NoOp,
                # Has one additional account attached
                Gtxn[1].accounts.length() == Int(1),
                # Has one application argument attached
                Gtxn[1].application_args.length() == Int(1),
                # Additional account is same as first txn
                Txn.accounts[1] == Gtxn[1].accounts[1],
                # Application argument is same as first txn
                Txn.application_args[0] == Gtxn[1].application_args[0],
                # Sender is developer
                Gtxn[1].sender() == App.globalGet(KEY_CREATOR),

                # Third txn from Escrow to Developer

                # is of type AssetTransfer
                Gtxn[2].type_enum() == TxnType.AssetTransfer,
                # sender is escrow
                Gtxn[2].sender() == Txn.accounts[1],
                # is not a clawback transaction
                Gtxn[1].asset_sender() == Global.zero_address(),

                # Fourth txn from Escrow to Developer

                # is of type AssetTransfer
                Gtxn[3].type_enum() == TxnType.AssetTransfer,
                # sender is escrow
                Gtxn[2].sender() == Txn.accounts[1],
                # is not a clawback transaction
                Gtxn[2].asset_sender() == Global.zero_address()
            )
        ),
        Int(1)
    ])

    on_refund = Seq([
        Assert(
            And(
                # Group has 3 transactions
                Global.group_size() == Int(3),
                # This ApplicationCall is the first transaction
                Txn.group_index() == Int(0),
                # No additional actions needed from this transaction
                Txn.on_completion() == OnComplete.NoOp,
                # Has one additional account attached
                Txn.accounts.length() == Int(1),
                # Has one application argument attached
                Txn.application_args.length() == Int(1),

                # Second txn to Manager

                # is of type ApplicationCall
                Gtxn[1].type_enum() == TxnType.ApplicationCall,
                # No additional actions needed
                Gtxn[1].on_completion() == OnComplete.NoOp,
                # Has one additional account attached
                Gtxn[1].accounts.length() == Int(1),
                # Has one application argument attached
                Gtxn[1].application_args.length() == Int(1),
                # Additional account is same as first txn
                Txn.accounts[1] == Gtxn[1].accounts[1],
                # Application argument is same as first txn
                Txn.application_args[0] == Gtxn[1].application_args[0],

                # Third txn from Escrow

                # is of type AssetTransfer
                Gtxn[2].type_enum() == TxnType.AssetTransfer,
                # sender is escrow
                Gtxn[2].sender() == Txn.accounts[1],
                # is not a clawback transaction
                Gtxn[2].asset_sender() == Global.zero_address(),
            )
        ),
        Int(1)
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


if __name__ == "__main__":
    with open('validator_approval.teal', 'w') as f:
        compiled = compileTeal(approval_program(), Mode.Application)
        f.write(compiled)

    with open('validator_clear.teal', 'w') as f:
        compiled = compileTeal(clear_program(), Mode.Application)
        f.write(compiled)
