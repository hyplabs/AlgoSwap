#!/usr/bin/env python3

from pyteal import *

def test():
    on_opt_in = Seq([
        App.localPut(Int(0), Bytes("T1"), Int(0)),
        Int(1)
    ])

    t1_val = App.localGet(Int(1), Bytes("T1"))

    on_function = Seq(
        [Assert(
            And(
                Txn.accounts.length() == Int(1),
                t1_val == Btoi(Txn.application_args[0])
            )
        ),
        Int(1)
    ])
    
    program = Cond(
        [Txn.on_completion() == OnComplete.OptIn,on_opt_in],
        [Txn.on_completion() == OnComplete.NoOp, on_function]
    )
    return program


if __name__ == "__main__":
    print(compileTeal(test(), Mode.Application))
