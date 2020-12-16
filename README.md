# AlgoSwap

# WARNING: THIS CODE HAS NOT BEEN AUDITED AND SHOULD NOT BE USED ON THE ALGORAND MAINNET - USE AT YOUR OWN RISK!

## Overview

AlgoSwap is an automated market maker like UniSwap built on the Pure Proof of Stake Algorand Blockchain. It relies on the `xy = k` function to maintain exchange rates for liquidity pairs in the market.

---

## Protocol

See the [AlgoSwap Protocol](./docs/protocol.md) documentation.

---

## Setup and Initialization

TODO

---

## TODO

- Test cases
- Anti-frontrunning using hashed commitments: in one block you must commit to making a trade by putting down a deposit (the amount needs to be thought out to properly align incentives), in a later block you would follow through on the commitment by actually making a trade, you can't make a trade unless you've committed to it in a previous block, this should entirely prevent frontrunning bots

## Credits

AlgoSwap was made possible by a [generous grant from the Algorand Foundation](https://algorand.foundation/grants-program/2020-grant-recipients), and the hard work of the following individuals:

- [calvinchan1](https://github.com/calvinchan1)
- [ehliang](https://github.com/ehliang)
- [haardikk21](https://github.com/haardikk21)
- [luoyang9](https://github.com/luoyang9)
- [mattreyes](https://github.com/mattreyes)
- [tiger-hao](https://github.com/tiger-hao)
- [uberi](https://github.com/uberi)
- [windforcer](https://github.com/windforcer)

## License

AlgoSwap is made available under the [MIT license](./LICENSE.txt).
