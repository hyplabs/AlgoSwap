#!/usr/bin/env python3

from pyteal import *

# 45 parts out of 10000 from each swap goes to liquidity providers
swap_fee = Int(45)
# 5 parts out of 10000 from each swap goes to the developers
protocol_fee = Int(5)


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


def approval_program(tmpl_swap_fee=swap_fee, tmpl_protocol_fee=protocol_fee):
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
    get_liquidity_token = App.localGetEx(Int(1), Global.current_application_id(), KEY_LIQUIDITY_TOKEN)

    get_token1 = App.localGetEx(Int(1), Global.current_application_id(), KEY_TOKEN1)

    get_token2 = App.localGetEx(Int(1), Global.current_application_id(), KEY_TOKEN2)

    get_total_token1_balance = App.localGetEx(Int(1), Global.current_application_id(), KEY_TOTAL_TOKEN1_BALANCE)

    get_total_token2_balance = App.localGetEx(Int(1), Global.current_application_id(), KEY_TOTAL_TOKEN2_BALANCE)

    def set_total_token1_balance(b): return App.localPut(Int(1), KEY_TOTAL_TOKEN1_BALANCE, b)

    def set_total_token2_balance(b): return App.localPut(Int(1), KEY_TOTAL_TOKEN2_BALANCE, b)

    def get_protocol_unused_token1(addr): return App.localGetEx(Int(1), Global.current_application_id(), Concat(KEY_PROTOCOL_UNUSED_TOKEN1, addr))

    def get_protocol_unused_token2(addr): return App.localGetEx(Int(1), Global.current_application_id(), Concat(KEY_PROTOCOL_UNUSED_TOKEN2, addr))

    def set_protocol_unused_token1(addr, amount): return App.localPut(Int(1), Concat(KEY_PROTOCOL_UNUSED_TOKEN1, addr), amount)

    def set_protocol_unused_token2(addr, amount): return App.localPut(Int(1), Concat(KEY_PROTOCOL_UNUSED_TOKEN2, addr), amount)

    def get_user_unused_token1(addr): return App.localGetEx(Int(0), Global.current_application_id(), Concat(KEY_USER_UNUSED_TOKEN1, addr))

    def get_user_unused_token2(addr): return App.localGetEx(Int(0), Global.current_application_id(), Concat(KEY_USER_UNUSED_TOKEN2, addr))

    def set_user_unused_token1(addr, amount): return App.localPut(Int(0), Concat(KEY_USER_UNUSED_TOKEN1, addr), amount)

    def set_user_unused_token2(addr, amount): return App.localPut(Int(0), Concat(KEY_USER_UNUSED_TOKEN2, addr), amount)

    def get_user_unused_liquidity(addr): return App.localGetEx(Int(0), Global.current_application_id(), Concat(KEY_USER_UNUSED_LIQUIDITY, addr))

    def set_user_unused_liquidity(addr, amount): return App.localPut(Int(0), Concat(KEY_USER_UNUSED_LIQUIDITY, addr), amount)

    on_create = Int(1)

    # allow closeout if the user has no remaining balances owed to them
    on_closeout = And(
        App.localGet(Int(0), KEY_USER_UNUSED_TOKEN1) == Int(0),
        App.localGet(Int(0), KEY_USER_UNUSED_TOKEN2) == Int(0),
        App.localGet(Int(0), KEY_USER_UNUSED_LIQUIDITY) == Int(0),
    )

    on_opt_in = Cond(
        # User
        [Txn.application_args.length() == Int(0),
            Seq([
                # initialize sender's local state as a user
                App.localPut(Int(0), KEY_LIQUIDITY_TOKEN, Btoi(Txn.application_args[0])),
                App.localPut(Int(0), KEY_TOTAL_TOKEN1_BALANCE, Int(0)),
                App.localPut(Int(0), KEY_USER_UNUSED_LIQUIDITY, Int(0)),
                Int(1),
            ])
        ],
        # Escrow
        [Txn.application_args.length() == Int(3),
        Seq([
            # initialize sender's local state as an escrow
            App.localPut(Int(0), KEY_LIQUIDITY_TOKEN, Txn.application_args[0]),
            App.localPut(Int(0), KEY_TOKEN1, Txn.application_args[1]),
            App.localPut(Int(0), KEY_TOKEN2, Txn.application_args[2]),
            App.localPut(Int(0), KEY_TOTAL_TOKEN1_BALANCE, Int(0)),
            App.localPut(Int(0), KEY_TOTAL_TOKEN2_BALANCE, Int(0)),
            Int(1),
        ])]
    )

    def swap_token_input_minus_fees(asset_amount): return asset_amount * (Int(1) - tmpl_protocol_fee - tmpl_swap_fee)

    def swap_token2_output(token1_input_minus_fees):
        return get_total_token2_balance.value() - (get_total_token1_balance.value() * get_total_token2_balance.value()) / (get_total_token1_balance.value() + token1_input_minus_fees)

    scratchvar_swap_token2_output = ScratchVar(TealType.uint64)

    on_swap_deposit = Seq([
        Assert(And(
            # the additional account is an escrow with token1
            get_token1.hasValue(),
            # transfer asset is TOKEN1
            Gtxn[2].xfer_asset() == get_token1.value(),
        )),
        scratchvar_swap_token2_output.store(swap_token2_output(swap_token_input_minus_fees(Gtxn[2].asset_amount()))),
        # Add swap fee amount to the liquidity pool
        # TOTAL_TOKEN1_BALANCE = TOTAL_TOKEN1_BALANCE + token1_input * swap_fee
        set_total_token1_balance(
            get_total_token1_balance.value() + (Gtxn[2].asset_amount() * tmpl_swap_fee)
        ),
        # Add protocol fee to the protocol fees account
        # PROTOCOL_UNUSED_TOKEN1 = PROTOCOL_UNUSED_TOKEN1 + token1_input * protocol_fee
        set_protocol_unused_token1(
            Txn.accounts[1],
            get_protocol_unused_token1(Txn.accounts[1]).value() + (Gtxn[2].asset_amount() * tmpl_protocol_fee)
        ),
        # Assert token2_output >= min_token2_received_from_algoswap
        Assert(
            scratchvar_swap_token2_output.load() >= Btoi(Txn.application_args[1])
        ),
        # USER_UNUSED_TOKEN2 = USER_UNUSED_TOKEN2 + token2_output
        set_user_unused_token2(
            Txn.accounts[1],
            get_user_unused_token2(Txn.accounts[1]).value() + scratchvar_swap_token2_output.load()
        ),
        # TOTAL_TOKEN1_BALANCE = TOTAL_TOKEN1_BALANCE + token1_input_minus_fees
        set_total_token1_balance(
            get_total_token1_balance.value() + swap_token_input_minus_fees(Gtxn[2].asset_amount())
        ),
        # TOTAL_TOKEN2_BALANCE = TOTAL_TOKEN2_BALANCE - token2_output
        set_total_token2_balance(
            get_total_token2_balance.value() - scratchvar_swap_token2_output.load()
        ),
        # successful approval
        Int(1)
    ])

    def swap_token1_output(token2_input_minus_fees):
        return get_total_token1_balance.value() - (get_total_token1_balance.value() * get_total_token2_balance.value()) / (get_total_token2_balance.value() + token2_input_minus_fees)

    scratchvar_swap_token1_output = ScratchVar(TealType.uint64)

    on_swap_deposit_2 = Seq([
        Assert(And(
            # the additional account is an escrow with token1
            get_token1.hasValue(),
            # transfer asset is Token2
            Gtxn[1].xfer_asset() == get_token2.value(),
        )),
        scratchvar_swap_token1_output.store(swap_token1_output(swap_token_input_minus_fees(Gtxn[1].asset_amount()))),
        # add swap fee amount to liquidity pool
        set_total_token2_balance(
            get_total_token2_balance.value() + (Gtxn[1].asset_amount() * tmpl_swap_fee)
        ),
        # add protocol fee to protocol fees account
        set_protocol_unused_token2(
            Txn.accounts[1],
            get_protocol_unused_token2(Txn.accounts[1]).value() + (Gtxn[1].asset_amount() * tmpl_protocol_fee)
        ),
        # assert token 1 output >= min_token1_received_from_algoswap
        Assert(
            scratchvar_swap_token1_output.load() >= Btoi(Txn.application_args[1])
        ),
        # set user unused token1 += token1_output
        set_user_unused_token1(
            Txn.accounts[1],
            get_user_unused_token1(Txn.accounts[1]).value() + scratchvar_swap_token1_output.load()
        ),
        # update total token2 balance
        set_total_token2_balance(get_total_token2_balance.value() + swap_token_input_minus_fees(Gtxn[1].asset_amount())),
        # update total token1 balance
        set_total_token1_balance(get_total_token1_balance.value() - scratchvar_swap_token1_output.load()),
        # successful approval
        Int(1),
    ])

    def total_liquidity(total_supply, reserve_balance): return total_supply - reserve_balance

    on_add_liquidity_deposit = Seq([
        Assert(And(
            get_token1.hasValue(),  # the first additional account is an escrow with token1
            # the transfer asset is TOKEN1
            Gtxn[2].xfer_asset() == get_token1.value(),
            # the transfer asset is TOKEN2
            Gtxn[3].xfer_asset() == get_token2.value(),
        )),
        # token1_used = min(token1_deposit, (token2_deposit * TOTAL_TOKEN1_BALANCE / TOTAL_TOKEN2_BALANCE))
        # If token1_deposit > (token2_deposit * TOTAL_TOKEN1_BALANCE / TOTAL_TOKEN2_BALANCE)
        If(Gtxn[2].asset_amount() > Gtxn[3].asset_amount() * get_total_token1_balance.value() / get_total_token2_balance.value(),
            # USER_UNUSED_TOKEN1 = USER_UNUSED_TOKEN1 + token1_deposit - token1_used
            # USER_UNUSED_TOKEN1 = USER_UNUSED_TOKEN1 + token1_deposit - (token2_deposit * TOTAL_TOKEN1_BALANCE / TOTAL_TOKEN2_BALANCE)
            set_user_unused_token1(
               Txn.accounts[1], 
               get_user_unused_token1(Txn.accounts[1]).value() + Gtxn[2].asset_amount() - 
               (Gtxn[3].asset_amount() * get_total_token1_balance.value() / get_total_token2_balance.value())
            )
            # Else:
            # USER_UNUSED_TOKEN1 = USER_UNUSED_TOKEN1 + token1_deposit - token1_used
            # USER_UNUSED_TOKEN1 = USER_UNUSED_TOKEN1 + token1_deposit - token1_deposit
            # Nothing required
        ),
        # token2_used = min(token2_deposit, (token1_deposit * TOTAL_TOKEN2_BALANCE / TOTAL_TOKEN1_BALANCE))
        # If token2_deposit > (token1_deposit * TOTAL_TOKEN2_BALANCE / TOTAL_TOKEN1_BALANCE)
        If(Gtxn[3].asset_amount() > Gtxn[2].asset_amount() * get_total_token2_balance.value() / get_total_token1_balance.value(),
           # USER_UNUSED_TOKEN2 = USER_UNUSED_TOKEN2 + token2_deposit - token2_used
           # USER_UNUSED_TOKEN2 = USER_UNUSED_TOKEN2 + token2_deposit - (token1_deposit * TOTAL_TOKEN2_BALANCE / TOTAL_TOKEN1_BALANCE)
           set_user_unused_token2(
               Txn.accounts[1],
               get_user_unused_token2(Txn.accounts[1]).value() + Gtxn[3].asset_amount() - 
               (Gtxn[2].asset_amount() * get_total_token2_balance.value() / get_total_token1_balance.value())
            )
            # Else:
            # USER_UNUSED_TOKEN2 = USER_UNUSED_TOKEN2 + token2_deposit - token2_used
            # USER_UNUSED_TOKEN2 = USER_UNUSED_TOKEN2 + token2_deposit - token2_deposit
            # Nothing required
        ),
        # total_liquidity = Total Supply (LIQUIDITY_TOKEN(ESCROW(TOKEN1, TOKEN2))) - Balance (RESERVE_ADDR(LIQUIDITY_TOKEN(ESCROW(TOKEN1, TOKEN2))))
        # USER_UNUSED_LIQUIDITY = USER_UNUSED_LIQUIDITY + total_liquidity * token1_deposit / TOTAL_TOKEN1_BALANCE
        set_user_unused_liquidity(
            Txn.accounts[1],
            get_user_unused_liquidity(Txn.accounts[1]).value() + 
            AssetParam.total(Int(0)).value() - 
            AssetHolding.balance(Int(2), get_liquidity_token.value()).value()
        ),
        # TOTAL_TOKEN1_BALANCE = TOTAL_TOKEN1_BALANCE + token1_used
        If(Gtxn[2].asset_amount() > Gtxn[3].asset_amount() * get_total_token1_balance.value() / get_total_token2_balance.value(),
            # If token1_deposit > (token2_deposit * TOTAL_TOKEN1_BALANCE / TOTAL_TOKEN2_BALANCE)
            # TOTAL_TOKEN1_BALANCE = TOTAL_TOKEN1_BALANCE + (token2_deposit * TOTAL_TOKEN1_BALANCE / TOTAL_TOKEN2_BALANCE)
            set_total_token1_balance(get_total_token1_balance.value() + Gtxn[3].asset_amount() * get_total_token1_balance.value() / get_total_token2_balance.value()),
            # Else:
            # TOTAL_TOKEN1_BALANCE = TOTAL_TOKEN1_BALANCE + token1_deposit
            set_total_token1_balance(get_total_token1_balance.value() + Gtxn[2].asset_amount())
        ),
        # TOTAL_TOKEN2_BALANCE = TOTAL_TOKEN2_BALANCE + token2_used
        If(Gtxn[3].asset_amount() > Gtxn[2].asset_amount() * get_total_token2_balance.value() / get_total_token1_balance.value(),
            # If token2_deposit > (token1_deposit * TOTAL_TOKEN2_BALANCE / TOTAL_TOKEN1_BALANCE)
            # TOTAL_TOKEN2_BALANCE = TOTAL_TOKEN2_BALANCE + (token1_deposit * TOTAL_TOKEN2_BALANCE / TOTAL_TOKEN1_BALANCE)
            set_total_token2_balance(get_total_token2_balance.value() + Gtxn[2].asset_amount() * get_total_token2_balance.value() / get_total_token1_balance.value()),
            # Else:
            # TOTAL_TOKEN2_BALANCE = TOTAL_TOKEN2_BALANCE + token2_deposit
            set_total_token2_balance(get_total_token2_balance.value() + Gtxn[3].asset_amount())
        ),
        Int(1)
    ])

    scratchvar_token1_available = ScratchVar(TealType.uint64)
    scratchvar_token2_available = ScratchVar(TealType.uint64)

    on_withdraw_liquidity = Seq([
        Assert(And(
            # this ApplicationCall's first additional account is an escrow and has key of token 1
            get_token1.hasValue(),
            # the AssetTransfer is for liquidity token
            Gtxn[2].xfer_asset() == get_liquidity_token.value(),
        )),

        # total_liquidity = Total Supply (LIQUIDITY_TOKEN(ESCROW(TOKEN1, TOKEN2))) - Balance (RESERVE_ADDR(LIQUIDITY_TOKEN(ESCROW(TOKEN1, TOKEN2))))
        # user_liquidity = Asset Amount (Txn)

        # token1_available = TOTAL_TOKEN1_BALANCE * user_liquidity / total_liquidity
        scratchvar_token1_available.store(get_total_token1_balance.value() * Gtxn[2].asset_amount() / (AssetParam.total(Int(0)).value() - AssetHolding.balance(Int(2), get_liquidity_token.value()).value())),

        # USER_UNUSED_TOKEN1 = USER_UNUSED_TOKEN1 + token1_available
        set_user_unused_token1(
            Txn.accounts[1],
            get_user_unused_token1(Txn.accounts[1]).value() + scratchvar_token1_available.load()
        ),
        # token2_available = TOTAL_TOKEN2_BALANCE * user_liquidity / total_liquidity
        scratchvar_token2_available.store(get_total_token2_balance.value() * Gtxn[2].asset_amount() / (AssetParam.total(Int(0)).value() - AssetHolding.balance(Int(2), get_liquidity_token.value()).value())),

        # USER_UNUSED_TOKEN2 = USER_UNUSED_TOKEN2 + token2_available
        set_user_unused_token2(
            Txn.accounts[1],
            get_user_unused_token2(Txn.accounts[1]).value() + scratchvar_token2_available.load()
        ),
        # TOTAL_TOKEN1_BALANCE = TOTAL_TOKEN1_BALANCE - token1_available
        set_total_token1_balance(
            get_total_token1_balance.value() - scratchvar_token1_available.load()
        ),
        # TOTAL_TOKEN2_BALANCE = TOTAL_TOKEN2_BALANCE - token2_available
        set_total_token2_balance(
            get_total_token2_balance.value() - scratchvar_token2_available.load()
        ),
        Int(1)
    ])

    on_refund = Seq([
        Assert(
            # this ApplicationCall's additional account is an escrow account with token1
            get_token1.hasValue(),
        ),
        Cond([
            # this AssetTransfer is for an available amount of TOKEN1
            And(
                Gtxn[2].xfer_asset() == get_token1.value(),
                Gtxn[2].asset_amount() <= get_user_unused_token1(Txn.accounts[1]).value()
            ),
            # unused_token1 = Gtxn[2].asset_amount()
            # USER_UNUSED_TOKEN1 = USER_UNUSED_TOKEN1 - unused_token1
            set_user_unused_token1(
                Txn.accounts[1],
                get_user_unused_token1(Txn.accounts[1]).value() - Gtxn[2].asset_amount()
            ),
        ], [
            # this AssetTransfer is for an available amount of TOKEN2
            And(
                Gtxn[2].xfer_asset() == get_token2.value(),
                Gtxn[2].asset_amount() <= get_user_unused_token2(Txn.accounts[1]).value()
            ),
            # unused_token2 = Gtxn[2].asset_amount()
            # USER_UNUSED_TOKEN2 = USER_UNUSED_TOKEN2 - unused_token2
            set_user_unused_token2(
                Txn.accounts[1],
                get_user_unused_token2(Txn.accounts[1]).value() - Gtxn[2].asset_amount()
            ),
        ], [
            # this AssetTransfer is for an available amount of LIQUIDITY_TOKEN
            And(
                Gtxn[2].xfer_asset() == get_liquidity_token.value(),
                Gtxn[2].asset_amount() <= get_user_unused_liquidity(Txn.accounts[1]).value()
            ),
            # unused_liquidity = Gtxn[2].asset_amount()
            # USER_UNUSED_LIQUIDITY = USER_UNUSED_LIQUIDITY - unused_liquidity
            set_user_unused_liquidity(
                Txn.accounts[1], 
                get_user_unused_liquidity(Txn.accounts[1]).value() - Gtxn[2].asset_amount()
            )
        ]),
        Int(1),
    ])

    on_withdraw_protocol_fees = Seq([
        Assert(And(
            # this ApplicationCall's additional account is an escrow account with token1
            get_token1.hasValue(),

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
        )),
        set_protocol_unused_token1(Txn.accounts[1], get_protocol_unused_token1(Txn.accounts[1]).value() - Gtxn[1].asset_amount()),
        set_protocol_unused_token2(Txn.accounts[1], get_protocol_unused_token2(Txn.accounts[1]).value() - Gtxn[2].asset_amount()),
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


if __name__ == "__main__":
    with open('manager_approval.teal', 'w') as f:
        compiled = compileTeal(approval_program(), Mode.Application)
        f.write(compiled)
