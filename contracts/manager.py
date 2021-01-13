#!/usr/bin/env python3

from pyteal import compileTeal, Seq, App, Assert, Txn, Gtxn, TxnType, Btoi, Bytes, Int, Return, If, Cond, And, Or, Not, Global, Mode, OnComplete, Concat, AssetHolding, AssetParam

# Validator contract application ID
validator_application_id = Int(123)
# 45 parts out of 10000 from each swap goes to liquidity providers
swap_fee = Int(45)
# 5 parts out of 10000 from each swap goes to the developers
protocol_fee = Int(5)

# TODO: validate escrow contracts are valid from the smart contract - verify hash of the escrow program is the escrow address
# Checking the escrow account: https://github.com/algorand/stateful-teal-auction-demo/blob/master/src/sovauc_approve.teal#L500
# TODO: ensure other fields are not present in field validation for manager contract
# TODO: consider moving some validation to the escrow

KEY_CREATOR = Bytes("C")
KEY_TOTAL_TOKEN1_BALANCE = Bytes("B1")
KEY_TOTAL_TOKEN2_BALANCE = Bytes("B2")
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


def approval_program(tmpl_swap_fee=swap_fee, tmpl_protocol_fee=protocol_fee, tmpl_validator_application_id=validator_application_id):
    get_liquidity_token = App.localGetEx(
        Int(1), Global.current_application_id(), KEY_LIQUIDITY_TOKEN)

    get_token1 = App.localGetEx(
        Int(1), Global.current_application_id(), KEY_TOKEN1)

    get_token2 = App.localGetEx(
        Int(1), Global.current_application_id(), KEY_TOKEN2)

    get_total_token1_balance = App.localGetEx(
        Int(1), Global.current_application_id(), KEY_TOTAL_TOKEN1_BALANCE)

    get_total_token2_balance = App.localGetEx(
        Int(1), Global.current_application_id(), KEY_TOTAL_TOKEN2_BALANCE)

    def set_total_token1_balance(b): return App.localPut(
        Int(1), KEY_TOTAL_TOKEN1_BALANCE, b)

    def set_total_token2_balance(b): return App.localPut(
        Int(1), KEY_TOTAL_TOKEN2_BALANCE, b)

    def get_protocol_unused_token1(addr): return App.localGetEx(
        Int(1), Global.current_application_id(), Concat(KEY_PROTOCOL_UNUSED_TOKEN1, addr))

    def get_protocol_unused_token2(addr): return App.localGetEx(
        Int(1), Global.current_application_id(), Concat(KEY_PROTOCOL_UNUSED_TOKEN2, addr))

    def set_protocol_unused_token1(addr, amount): return App.localPut(
        Int(1), Concat(KEY_PROTOCOL_UNUSED_TOKEN1, addr), amount)

    def set_protocol_unused_token2(addr, amount): return App.localPut(
        Int(1), Concat(KEY_PROTOCOL_UNUSED_TOKEN2, addr), amount)

    def get_user_unused_token1(addr): return App.localGetEx(
        Int(0), Global.current_application_id(), Concat(KEY_USER_UNUSED_TOKEN1, addr))

    def get_user_unused_token2(addr): return App.localGetEx(
        Int(0), Global.current_application_id(), Concat(KEY_USER_UNUSED_TOKEN2, addr))

    def set_user_unused_token1(addr, amount): return App.localPut(
        Int(0), Concat(KEY_USER_UNUSED_TOKEN1, addr), amount)

    def set_user_unused_token2(addr, amount): return App.localPut(
        Int(0), Concat(KEY_USER_UNUSED_TOKEN2, addr), amount)

    def get_user_unused_liquidity(addr): return App.localGetEx(
        Int(0), Global.current_application_id(), Concat
        (KEY_USER_UNUSED_LIQUIDITY, addr))

    def set_user_unused_liquidity(addr, amount): return App.localPut(
        Int(0), Concat(KEY_USER_UNUSED_LIQUIDITY, addr), amount)

    on_create = Seq([
        App.globalPut(KEY_CREATOR, Txn.sender()),
        Int(1),
    ])

    # allow closeout if the user has no remaining balances owed to them
    on_closeout = And(
        App.localGet(Int(0), KEY_USER_UNUSED_TOKEN1) == Int(0),
        App.localGet(Int(0), KEY_USER_UNUSED_TOKEN2) == Int(0),
        App.localGet(Int(0), KEY_USER_UNUSED_LIQUIDITY) == Int(0),
    )

    on_opt_in = Cond([Txn.application_args.length() == Int(0), Seq([
        # initialize sender's local state as a user
        App.localPut(Int(0), KEY_LIQUIDITY_TOKEN,
                     Btoi(Txn.application_args[0])),
        App.localPut(Int(0), KEY_TOTAL_TOKEN1_BALANCE, Int(0)),
        App.localPut(Int(0), KEY_USER_UNUSED_LIQUIDITY, Int(0)),
        Int(1),
    ])], [Txn.application_args.length() == Int(3), Seq([
        # initialize sender's local state as an escrow
        App.localPut(Int(0), KEY_LIQUIDITY_TOKEN, Txn.application_args[0]),
        App.localPut(Int(0), KEY_TOKEN1, Txn.application_args[1]),
        App.localPut(Int(0), KEY_TOKEN2, Txn.application_args[2]),
        App.localPut(Int(0), KEY_TOTAL_TOKEN1_BALANCE, Int(0)),
        App.localPut(Int(0), KEY_TOTAL_TOKEN2_BALANCE, Int(0)),
        Int(1),
    ])])

    def swap_token_input_minus_fees(asset_amount):
        return asset_amount * (Int(1) - tmpl_protocol_fee - tmpl_swap_fee)

    def swap_token2_output(token1_input_minus_fees):
        return get_total_token2_balance.value() - (get_total_token1_balance.value() * get_total_token2_balance.value()) / (get_total_token1_balance.value() + token1_input_minus_fees)

    on_swap_deposit = Seq([
        Assert(And(
            Global.group_size() == Int(3),  # three transactions in this group
            Gtxn[0].application_id() == tmpl_validator_application_id,
            Txn.group_index() == Int(1),  # this ApplicationCall is the second one
            # the additional account is an escrow with token1
            get_token1.hasValue(),
            # the additional account is an escrow with token2
            get_token2.hasValue(),
            Gtxn[1].xfer_asset() == get_token1.value(),
        )),
        # add swap fee amount to liquidity pool
        set_total_token1_balance(
            get_total_token1_balance.value() + (Gtxn[1].asset_amount() * tmpl_swap_fee)),
        # add protocol fee to protocol fee account
        set_protocol_unused_token1(Txn.accounts[1],
                                   get_protocol_unused_token1(Txn.accounts[1]).value() + (Gtxn[1].asset_amount() * tmpl_protocol_fee)),
        # assert token 2 output >= min_token2_received_from_algoswap
        Assert(swap_token2_output(swap_token_input_minus_fees(
            Gtxn[1].asset_amount())) >= Btoi(Txn.application_args[1])),
        # set user unused token 2 += token2_output
        set_user_unused_token2(Txn.accounts[1], get_user_unused_token2(Txn.accounts[1]).value(
        ) + swap_token2_output(swap_token_input_minus_fees(Gtxn[1].asset_amount()))),
        # update total token1 balance
        set_total_token1_balance(get_total_token1_balance.value(
        ) + swap_token_input_minus_fees(Gtxn[1].asset_amount())),
        # update total token2 balance
        set_total_token2_balance(get_total_token2_balance.value(
        ) - swap_token2_output(swap_token_input_minus_fees(Gtxn[1].asset_amount()))),
        # successful approval
        Int(1)
    ])

    def swap_token1_output(token2_input_minus_fees):
        return get_total_token1_balance.value() - (get_total_token1_balance.value() * get_total_token2_balance.value()) / (get_total_token2_balance.value() + token2_input_minus_fees)

    on_swap_deposit_2 = Seq([
        Assert(And(
            Global.group_size() == Int(2),  # two transactions in this group
            Txn.group_index() == Int(0),  # this ApplicationCall is the first one
            Txn.on_completion() == OnComplete.NoOp,  # no additional actions needed
            Txn.accounts.length() == Int(1),  # has one additional account attached
            # the additional account is an escrow with token1
            get_token1.hasValue(),
            # the additional account is an escrow with token2
            get_token2.hasValue(),
            Txn.application_args.length() == Int(2),  # has two application arguments
            # the second transaction is of type AssetTransfer
            Gtxn[1].type_enum() == TxnType.AssetTransfer,
            # asset sender is zero address
            Gtxn[1].sender() == Global.zero_address(),
            # transfer asset is Token2
            Gtxn[1].xfer_asset() == get_token2.value(),
            # asset receiver is the escrow account
            Gtxn[1].asset_receiver() == Txn.accounts[1],
        )),
        # add swap fee amount to liquidity pool
        set_total_token2_balance(get_total_token2_balance.value(
        ) + (Gtxn[1].asset_amount() * tmpl_swap_fee)),
        # add protocol fee to protocol fees account
        set_protocol_unused_token2(Txn.accounts[1], get_protocol_unused_token2(Txn.accounts[1]).value(
        ) + (Gtxn[1].asset_amount() * tmpl_protocol_fee)),
        # assert token 1 output >= min_token1_received_from_algoswap
        Assert(swap_token1_output(swap_token_input_minus_fees(
            Gtxn[1].asset_amount())) >= Btoi(Txn.application_args[1])),
        # set user unused token1 += token1_output
        set_user_unused_token1(Txn.accounts[1], get_user_unused_token1(Txn.accounts[1]).value(
        ) + swap_token1_output(swap_token_input_minus_fees(Gtxn[1].asset_amount()))),
        # update total token2 balance
        set_total_token2_balance(get_total_token2_balance.value(
        ) + swap_token_input_minus_fees(Gtxn[1].asset_amount())),
        # update total token1 balance
        set_total_token1_balance(get_total_token1_balance.value(
        ) - swap_token1_output(swap_token_input_minus_fees(Gtxn[1].asset_amount()))),
        # successful approval
        Int(1),
    ])

    def total_liquidity(total_supply, reserve_balance):
        return total_supply - reserve_balance

    on_add_liquidity_deposit = Seq([
        Assert(And(
            get_token1.hasValue(),  # the first additional account is an escrow with token1
            get_token2.hasValue(),  # the first additional account is an escrow with token2
            # the transfer asset is TOKEN1
            Gtxn[2].xfer_asset() == get_token1.value(),
            # the transfer asset is TOKEN2
            Gtxn[3].xfer_asset() == get_token2.value(),
        )),
        # set user unused token1 += token1_deposit - token1_used
        If(Gtxn[1].asset_amount() > Gtxn[2].asset_amount() * get_total_token1_balance.value() / get_total_token2_balance.value(),
           # token1_deposit > matched_token
           set_user_unused_token1(Txn.accounts[1], get_user_unused_token1(Txn.accounts[1]).value() + Gtxn[1].asset_amount(
           ) - (Gtxn[2].asset_amount() * get_total_token1_balance.value() / get_total_token2_balance.value()))),
        # set user unused token2 += token2_deposit - token2_used
        If(Gtxn[2].asset_amount() > Gtxn[1].asset_amount() * get_total_token2_balance.value() / get_total_token1_balance.value(),
           # token2_deposit > matched_token
           set_user_unused_token2(Txn.accounts[1], get_user_unused_token2(Txn.accounts[1]).value() + Gtxn[2].asset_amount(
           ) - (Gtxn[2].asset_amount() * get_total_token2_balance.value() / get_total_token1_balance.value()))),
        # set user unused liquidity += total_liquidity * token1_deposit / TOTAL_TOKEN1_BALANCE
        set_user_unused_liquidity(Txn.accounts[1], get_user_unused_liquidity(
            Txn.accounts[1]).value() + AssetParam.total(Int(0)).value() - AssetHolding.balance(Int(2), get_liquidity_token.value()).value()),
        # set TOTAL_TOKEN1_BALANCE += token1_used
        If(Gtxn[1].asset_amount() > Gtxn[2].asset_amount() * get_total_token1_balance.value() / get_total_token2_balance.value(),
           set_total_token1_balance(get_total_token1_balance.value() + Gtxn[2].asset_amount(
           ) * get_total_token1_balance.value() / get_total_token2_balance.value()),
           set_total_token1_balance(get_total_token1_balance.value() + Gtxn[1].asset_amount())),
        # set TOTAL_TOKEN2_BALANCE += token2_used
        If(Gtxn[2].asset_amount() > Gtxn[1].asset_amount() * get_total_token2_balance.value() / get_total_token1_balance.value(),
           set_total_token2_balance(get_total_token2_balance.value() + Gtxn[1].asset_amount() * get_total_token2_balance.value() / get_total_token1_balance.value()), set_total_token2_balance(get_total_token2_balance.value() + Gtxn[2].asset_amount())),
        Int(1)
    ])

    on_withdraw_liquidity = Seq([
        Assert(And(
            # this ApplicationCall's first additional account is an escrow and has key of token 1
            get_token1.hasValue(),
            get_token2.hasValue(),  # has key of token 2 as well

            # the AssetTransfer is for liquidity token
            Gtxn[2].xfer_asset() == get_liquidity_token.value(),
        )),
        # set user unused token1 += token1_available
        set_user_unused_token1(Txn.accounts[1], get_user_unused_token1(Txn.accounts[1]).value() + get_total_token1_balance.value(
        ) * Gtxn[1].asset_amount() / (AssetParam.total(Int(0)).value() - AssetHolding.balance(Int(2), get_liquidity_token.value()).value())),
        # set user unused token2 += token2_available
        set_user_unused_token2(Txn.accounts[1], get_user_unused_token2(Txn.accounts[1]).value() + get_total_token2_balance.value(
        ) * Gtxn[1].asset_amount() / (AssetParam.total(Int(0)).value() - AssetHolding.balance(Int(2), get_liquidity_token.value()).value())),
        # set TOTAL_TOKEN1_BALANCE -= token1_available
        set_total_token1_balance(get_total_token1_balance.value() - get_total_token1_balance.value(
        ) * Gtxn[1].asset_amount() / (AssetParam.total(Int(0)).value() - AssetHolding.balance(Int(2), get_liquidity_token.value()).value())),
        # set TOTAL_TOKEN2_BALANCE -= token2_available
        set_total_token2_balance(get_total_token2_balance.value() - get_total_token2_balance.value(
        ) * Gtxn[1].asset_amount() / (AssetParam.total(Int(0)).value() - AssetHolding.balance(Int(2), get_liquidity_token.value()).value())),
        Int(1)
    ])

    on_refund = Seq([
        Assert(And(
            # this ApplicationCall's additional account is an escrow account with token1
            get_token1.hasValue(),
            # this ApplicationCall's additional account is an escrow account with token2
            get_token2.hasValue(),
        )),
        Cond([
            # this AssetTransfer is for an available amount of TOKEN1
            And(Gtxn[1].xfer_asset() == get_token1.value(), Gtxn[1].asset_amount(
            ) <= get_user_unused_token1(Txn.accounts[1]).value()),
            set_user_unused_token1(Txn.accounts[1], get_user_unused_token1(
                Txn.accounts[1]).value() - Gtxn[1].asset_amount()),
        ], [
            # this AssetTransfer is for an available amount of TOKEN2
            And(Gtxn[1].xfer_asset() == get_token2.value(), Gtxn[1].asset_amount(
            ) <= get_user_unused_token2(Txn.accounts[1]).value()),
            set_user_unused_token2(Txn.accounts[1], get_user_unused_token2(
                Txn.accounts[1]).value() - Gtxn[1].asset_amount()),
        ], [
            # this AssetTransfer is for an available amount of LIQUIDITY_TOKEN
            And(Gtxn[1].xfer_asset() == get_liquidity_token.value(
            ), Gtxn[1].asset_amount() <= get_user_unused_liquidity(Txn.accounts[1]).value()),
            set_user_unused_liquidity(Txn.accounts[1], get_user_unused_liquidity(
                Txn.accounts[1]).value() - Gtxn[1].asset_amount())
        ]),
        Int(1),
    ])

    on_withdraw_protocol_fees = Seq([
        Assert(And(


            # this ApplicationCall's additional account is an escrow account with token1
            get_token1.hasValue(),
            # this ApplicationCall's additional account is an escrow account with token2
            get_token2.hasValue(),

            # this TOKEN1 AssetTransfer is for TOKEN1
            Gtxn[1].xfer_asset() == get_token1.value(),
            # this TOKEN1 AssetTransfer is for an available amount of TOKEN1
            Gtxn[1].asset_amount() <= get_protocol_unused_token1(
                Txn.accounts[1]).value(),

            # this TOKEN2 AssetTransfer is for TOKEN2
            Gtxn[2].xfer_asset() == get_token2.value(),
            # this TOKEN2 AssetTransfer is for an available amount of TOKEN2
            Gtxn[2].asset_amount() <= get_protocol_unused_token2(
                Txn.accounts[1]).value(),
            # this TOKEN2 AssetTransfer is not a clawback transaction
        )),
        set_protocol_unused_token1(Txn.accounts[1], get_protocol_unused_token1(
            Txn.accounts[1]).value() - Gtxn[1].asset_amount()),
        set_protocol_unused_token2(Txn.accounts[1], get_protocol_unused_token2(
            Txn.accounts[1]).value() - Gtxn[2].asset_amount()),
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
    # TODO
    return Int(1)


if __name__ == "__main__":
    with open('manager_approval.teal', 'w') as f:
        compiled = compileTeal(approval_program(), Mode.Application)
        f.write(compiled)

    with open('manager_clear.teal', 'w') as f:
        compiled = compileTeal(clear_program(), Mode.Application)
        f.write(compiled)
