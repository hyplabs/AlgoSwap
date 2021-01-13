#!/usr/bin/env python3

from pyteal import *


x = ScratchSlot()
y = ScratchSlot()
z = ScratchSlot()


def test():
    program = Seq([
        z.store(),
    ])
    return program


if __name__ == "__main__":
    print(compileTeal(test(), Mode.Application))
