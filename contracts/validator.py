#!/usr/bin/env python3

from pyteal import *

# Manager App ID
MANAGER_INDEX = Int(13795367) # TODO: Update

# Keys
KEY_CREATOR = Bytes("C")
KEY_TOKEN1 = Bytes("T1")
KEY_TOKEN2 = Bytes("T2")
KEY_LIQUIDITY_TOKEN = Bytes("LT")

# Transaction Types
TRANSACTION_TYPE_SWAP_DEPOSIT_TOKEN1_TO_TOKEN2 = Bytes("s1")
TRANSACTION_TYPE_SWAP_DEPOSIT_TOKEN2_TO_TOKEN1 = Bytes("s2")
TRANSACTION_TYPE_ADD_LIQUIDITY_DEPOSIT = Bytes("a")
TRANSACTION_TYPE_WITHDRAW_LIQUIDITY = Bytes("w")
TRANSACTION_TYPE_REFUND = Bytes("r")
TRANSACTION_TYPE_WITHDRAW_PROTOCOL_FEES = Bytes("p")

def approval_program():
    """
    This smart contract implements the Validator part of the AlgoSwap DEX.
    It asserts the existence of all required transaction fields in every
    transaction part of every possible atomic transaction group that AlgoSwap
    supports (Swap Token 1 for Token 2, Swap Token 2 for Token 1, Add Liquidity,
    Withdraw Liquidity, Withdraw Protocol Fees, and Refund).

    Any atomic transaction group MUST have a transaction to the validator
    smart contract as the first transaction of the group to proceed.

    Commands:
        s1  Swap Token 1 for Token 2 in a liquidity pair
        s2  Swap Token 2 for Token 1 in a liquidity pair
        a   Add liquidity to a liquidity pool
        w   Withdraw liquidity from a liquidity pool
        r   Get a refund of unused tokens
        p   Withdraw protocol fees (Developer only)
    """

    key_token1 = App.localGetEx(Int(1), MANAGER_INDEX, KEY_TOKEN1)
    key_token2 = App.localGetEx(Int(1), MANAGER_INDEX, KEY_TOKEN2)
    key_liquidity_token = App.localGetEx(Int(1), MANAGER_INDEX, KEY_LIQUIDITY_TOKEN)

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
        key_token1,
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
                # Transfer asset is TOKEN1
                Gtxn[2].xfer_asset() == key_token1.value(),
                # Asset sender is zero address
                Gtxn[2].asset_sender() == Global.zero_address(),
                # Asset receiver is attached account
                Gtxn[2].asset_receiver() == Txn.accounts[1],
                # Is not a close transaction
                Gtxn[2].close_remainder_to() == Global.zero_address(),
                # Is not a close asset transaction
                Gtxn[2].asset_close_to() == Global.zero_address(),
            )
        ),
        Int(1)
    ])

    on_swap_deposit_2 = Seq([
        key_token2,
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
                # Transfer asset is Token 2
                Gtxn[2].xfer_asset() == key_token2.value(),
                # Sender is zero address
                Gtxn[2].asset_sender() == Global.zero_address(),
                # Asset receiver is attached account
                Gtxn[2].asset_receiver() == Txn.accounts[1],
                # Is not a close transaction
                Gtxn[2].close_remainder_to() == Global.zero_address(),
                # Is not a close asset transaction
                Gtxn[2].asset_close_to() == Global.zero_address(),
            )
        ),
        Int(1)
    ])

    on_add_liquidity_deposit = Seq([
        key_token1,
        key_token2,
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
                # Has two application arguments attached
                Txn.application_args.length() == Int(2),

                # NOTE: No way to check length of foreign assets in PyTeal

                # Second txn to Manager

                # is of type ApplicationCall
                Gtxn[1].type_enum() == TxnType.ApplicationCall,
                # No additional actions needed
                Gtxn[1].on_completion() == OnComplete.NoOp,
                # Has one additional account attached
                Gtxn[1].accounts.length() == Int(1),
                # Has two application arguments attached
                Gtxn[1].application_args.length() == Int(2),
                # Additional accounts are same as first txn
                Txn.accounts[1] == Gtxn[1].accounts[1],
                # Application arguments are same as first txn
                Txn.application_args[0] == Gtxn[1].application_args[0],
                Txn.application_args[1] == Gtxn[1].application_args[1],

                # Third txn to Escrow

                # Is of type AssetTransfer
                Gtxn[2].type_enum() == TxnType.AssetTransfer,
                # Transfer asset is Token 1
                Gtxn[2].xfer_asset() == key_token1.value(),
                # Asset sender is zero address
                Gtxn[2].asset_sender() == Global.zero_address(),
                # Asset receiver is the escrow account
                Gtxn[2].asset_receiver() == Txn.accounts[1],
                # Is not a close transaction
                Gtxn[2].close_remainder_to() == Global.zero_address(),
                # Is not a close asset transaction
                Gtxn[2].asset_close_to() == Global.zero_address(),

                # Fourth txn to Escrow

                # Is of type AssetTransfer
                Gtxn[3].type_enum() == TxnType.AssetTransfer,
                # Transfer asset is Token 2
                Gtxn[3].xfer_asset() == key_token2.value(),
                # Asset sender is zero address
                Gtxn[3].asset_sender() == Global.zero_address(),
                # Asset receiver is the escrow account
                Gtxn[3].asset_receiver() == Txn.accounts[1],
                # Is not a close transaction
                Gtxn[3].close_remainder_to() == Global.zero_address(),
                # Is not a close asset transaction
                Gtxn[3].asset_close_to() == Global.zero_address(),
            )
        ),
        Int(1)
    ])

    on_withdraw_liquidity = Seq([
        key_liquidity_token,
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
                # Has three application arguments attached
                Txn.application_args.length() == Int(3),

                # NOTE: No way to check length of foreign assets in PyTeal

                # Second txn to Manager

                # is of type ApplicationCall
                Gtxn[1].type_enum() == TxnType.ApplicationCall,
                # No additional actions needed
                Gtxn[1].on_completion() == OnComplete.NoOp,
                # Has two additional accounts attached
                Gtxn[1].accounts.length() == Int(1),
                # Has three application arguments attached
                Gtxn[1].application_args.length() == Int(3),
                # Additional accounts are same as first txn
                Txn.accounts[1] == Gtxn[1].accounts[1],
                # Application arguments are same as first txn
                Txn.application_args[0] == Gtxn[1].application_args[0],
                Txn.application_args[1] == Gtxn[1].application_args[1],
                Txn.application_args[2] == Gtxn[1].application_args[2],

                # Third txn to Escrow

                # is of type AssetTransfer
                Gtxn[2].type_enum() == TxnType.AssetTransfer,
                # Transfer asset is liquidity token
                Gtxn[2].xfer_asset() == key_liquidity_token.value(),
                # Asset sender is zero address
                Gtxn[2].asset_sender() == Global.zero_address(),
                # Asset receiver is the escrow account
                Gtxn[2].asset_receiver() == Txn.accounts[1],
                # Is not a close transaction
                Gtxn[2].close_remainder_to() == Global.zero_address(),
                # Is not a close asset transaction
                Gtxn[2].asset_close_to() == Global.zero_address(),
            )
        ),
        Int(1),
    ])

    on_withdraw_protocol_fees = Seq([
        key_token1,
        key_token2,
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
                # Transfer asset is Token 1
                Gtxn[2].xfer_asset() == key_token1.value(),
                # sender is escrow
                Gtxn[2].sender() == Txn.accounts[1],
                # is not a clawback transaction
                Gtxn[2].asset_sender() == Global.zero_address(),

                # Fourth txn from Escrow to Developer

                # is of type AssetTransfer
                Gtxn[3].type_enum() == TxnType.AssetTransfer,
                # Transfer asset is Token 2
                Gtxn[3].xfer_asset() == key_token2.value(),
                # sender is escrow
                Gtxn[3].sender() == Txn.accounts[1],
                # is not a clawback transaction
                Gtxn[3].asset_sender() == Global.zero_address(),
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