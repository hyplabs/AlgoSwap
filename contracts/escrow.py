from pyteal import compileTeal, Mode, And, Int, Global, Txn, Gtxn, TxnType

validator_application_id = Int(13377480)
manager_application_id = Int(13377481)

def logicsig(tmpl_validator_application_id=validator_application_id, tmpl_manager_application_id=manager_application_id):
    """
    This smart contract implements the Escrow part of the AlgoSwap DEX.
    It is a logicsig smart contract for a specific liquidity pair (Token 1/Token 2)
    where Token 1 and Token 2 are distinct Algorand Standard Assets (ASAs).
    All withdrawals from this smart contract account require approval from the
    Validator and Manager contracts first within the same atomic transaction group.
    """
    program = And(
        Global.group_size() == Int(3),  # 3 transactions in this group
        # first one is an ApplicationCall
        Gtxn[0].type_enum() == TxnType.ApplicationCall,
        # the ApplicationCall must be approved by the validator application
        Gtxn[0].application_id() == tmpl_validator_application_id,

        # second one is an ApplicationCall
        Gtxn[1].type_enum() == TxnType.ApplicationCall,
        # Must be approved by the manager application
        Gtxn[1].application_id() == tmpl_manager_application_id,
        
        Txn.group_index() == Int(2),  # this AssetTransfer is the third one
        Txn.close_remainder_to() == Global.zero_address(), # Is not a close transaction
        Txn.asset_close_to() == Global.zero_address(), # Is not an asset close transaction
    )
    return program


if __name__ == "__main__":
    print(compileTeal(logicsig, Mode.Signature))
