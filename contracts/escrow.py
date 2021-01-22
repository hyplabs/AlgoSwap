from pyteal import *

manager_application_id = Int(13649731) # TODO: Update
validator_application_id = Int(13649738) # TODO: Update
token1_asset_id = Int(13649742) # TODO: Update
token2_asset_id = Int(13649743) # TODO: Update
liquidity_token_asset_id = Int(13649749) # TODO: Update
optin_last_valid = Int(11885898) # TODO: Update

def logicsig():
    """
    This smart contract implements the Escrow part of the AlgoSwap DEX.
    It is a logicsig smart contract for a specific liquidity pair (Token 1/Token 2)
    where Token 1 and Token 2 are distinct Algorand Standard Assets (ASAs).
    All withdrawals from this smart contract account require approval from the
    Validator and Manager contracts first within the same atomic transaction group.
    """
    program = Cond(
        [
            # If there is a single transaction within the group
            Global.group_size() == Int(1),
            # Then either this is an opt-in to a contract, or to an asset
            Or(
                And(
                    # This is a contract opt-in transaction
                    Txn.on_completion() == OnComplete.OptIn,
                    # Transaction's last valid round is lte specified last valid round
                    Txn.last_valid() <= optin_last_valid,
                    Or(
                        # Is an opt in to the validator contract
                        Txn.application_id() == validator_application_id,
                        # Is an opt in to the manager contract
                        Txn.application_id() == manager_application_id
                    )
                ),
                And(
                    # This is an asset opt-in
                    Txn.type_enum() == TxnType.AssetTransfer,
                    # Sender and asset receiver are both Escrow
                    Txn.sender() == Txn.asset_receiver(),
                    # Transaction's last valid round is lte specified last valid round
                    Txn.last_valid() <= optin_last_valid,
                    # Is an opt-in to one of the expected assets
                    Or(
                        # Is an opt in to Token 1 Asset
                        Txn.xfer_asset() == token1_asset_id,
                        # Is an opt in to Token 2 Asset
                        Txn.xfer_asset() == token2_asset_id,
                        # Is an opt in to Liquidity Pair Token Asset
                        Txn.xfer_asset() == liquidity_token_asset_id
                    )
                )
            )
        ],
        [
            # If there are three transactions within the group
            Global.group_size() == Int(3),
            # Then this is a refund transaction
            And(
                # first one is an ApplicationCall
                Gtxn[0].type_enum() == TxnType.ApplicationCall,
                # the ApplicationCall must be approved by the validator application
                Gtxn[0].application_id() == validator_application_id,

                # second one is an ApplicationCall
                Gtxn[1].type_enum() == TxnType.ApplicationCall,
                # Must be approved by the manager application
                Gtxn[1].application_id() == manager_application_id,

                # this transaction is the third one
                Txn.group_index() == Int(2),
                # this transaction is an AssetTransfer
                Txn.type_enum() == TxnType.AssetTransfer,
                # this transaction is not a close transaction
                Txn.close_remainder_to() == Global.zero_address(),
                # this transaction is not an asset close transaction
                Txn.asset_close_to() == Global.zero_address()
            )
        ],
        [
            # If there are four transactions within the group
            Global.group_size() == Int(4),
            # Then this is a withdraw protocol fees transaction
            And(
                # first one is an ApplicationCall
                # first one is an ApplicationCall
                Gtxn[0].type_enum() == TxnType.ApplicationCall,
                # the ApplicationCall must be approved by the validator application
                Gtxn[0].application_id() == validator_application_id,

                # second one is an ApplicationCall
                Gtxn[1].type_enum() == TxnType.ApplicationCall,
                # Must be approved by the manager application
                Gtxn[1].application_id() == manager_application_id,

                # this transaction is the third or fourth one
                Or(
                    Txn.group_index() == Int(2),
                    Txn.group_index() == Int(3),
                ),
                # this transaction is an AssetTransfer
                Txn.type_enum() == TxnType.AssetTransfer,
                # this transaction is not a close transaction
                Txn.close_remainder_to() == Global.zero_address(),
                # this transaction is not an asset close transaction
                Txn.asset_close_to() == Global.zero_address(),
            )
        ]
    )
    return program


if __name__ == "__main__":
    print(compileTeal(logicsig, Mode.Signature))
