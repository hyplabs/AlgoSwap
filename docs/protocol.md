---
title: AlgoSwap Protocol Specification
authors: Anthony Zhang (@uberi), Haardik Haardik (@haardikk21)
last_edited: 11 November 2020
---

# AlgoSwap Protocol

## Components

### User

Refers to the AlgoSwap end user, interacting via [Frontend](#frontend) and [Wallet](#wallet). Capable of 4 distinct operations:

- Opt in to AlgoSwap
- Swap between a `TOKEN1`/`TOKEN2` pair
- Add liquidity for `TOKEN1`/`TOKEN2` pair
- Withdraw liquidity for `TOKEN1`/`TOKEN2` pair

### Frontend

Refers to the AlgoSwap frontend, which will be hosted on the open internet and be the convenient and standard way for [User](#user) to interact with Algoswap.

Optionally, [User](#user) may choose to host [Frontend](#frontend) themselves, or write their own clients should they wish to.

[Frontend](#frontend) interacts with the Algorand blockchain via the [Wallet's](#wallet) Algorand API.

### Wallet

Refers to a browser extension that manages Algorand transaction signing. At the time of writing, the best and only option for this is [PureStake's AlgoSigner](https://www.purestake.com/technology/algosigner/), written for Chrome/Chromium browsers.

### Validator

Refers to a logicsig Algorand smart contract that validates the transaction fields of every possible transaction for Algoswap.

### Manager

Refers to a stateful application Algorand smart contract that manages global and local state, and approves transactions to the escrow contracts for each liquidity pair.

### Escrow Contract

Refers to a logicsig Algorand smart contract for a specific liquidity pair (`TOKEN1` and `TOKEN2`), where `TOKEN1` and `TOKEN2` refer to distinct Algorand Standard Assets. All withdrawals from this smart contract account require approval from [Validator](#validator) and [Manager](#manager) within the same atomic transaction group.

We denote the 58-byte Algorand address of `ESCROW(TOKEN1, TOKEN2)` as `ADDRESS_OF(ESCROW(TOKEN1, TOKEN2))`

### Liquidity Token

Refers to an Algorand Standard Asset representing shares of the liquidity stored in a specific [Escrow Contract](#escrow-contract).

This token is minted when liquidity providers deposit liquidity, and then burned by its holder to recover the amounts of `TOKEN1` and `TOKEN2` represented by the liquidity represented by this token.

The reserve address for the liquidity token is represented as `RESERVE_ADDR(LIQUIDITY_TOKEN(ESCROW(TOKEN1, TOKEN2)))`

### Developer

Refers to an AlgoSwap developer deploying, upgrading, and maintaining AlgoSwap. Has the special privelege to be able to withdraw [Protocol Fees](#protocol-fees) (`PROTOCOL_UNUSED_TOKEN1` and `PROTOCOL_UNUSED_TOKEN2` balances in each `ESCROW(TOKEN1, TOKEN2)`)

---

## Application State (for Manager)

Actual keys in TEAL use shorter names than the ones specified here for readability.

### Global Storage

- `DEVELOPER_ADDRESS`: address of the account that created the [Manager](#manager) contract.

### Local Storage for Escrow Contracts

Manager also needs to store some information about each [Escrow Contract](#escrow-contract). To do this, each Escrow Contract opts into the Manager, and we store fields in Manager's local storage for the Escrow Contract.

- `TOKEN1` and `TOKEN2`: The asset ID's of Token 1 and Token 2 respectively.

- `LIQUIDITY_TOKEN`: The asset ID of the liquidity token for this escrow contract.

- `TOTAL_TOKEN1_BALANCE` and `TOTAL_TOKEN2_BALANCE`: Total amounts of TOKEN1 and TOKEN2 currently in the liquidity pool, respectively.

  - Different from getting the Escrow contract's balance for `TOKEN1` and `TOKEN2` because the real balances also include the values of `USER_TOKEN1_UNUSED` and `USER_TOKEN2_UNUSED` for [User](#user) and the [Protocol Fees](#protocol-fees).
  - These values are initialized to 0.

- `TOTAL_LIQUIDITY_TOKEN_DISTRIBUTED`: Total amount of `LIQUIDITY_TOKEN` distributed to users.

  - Different from calculating (total supply of `LIQUIDITY_TOKEN(ESCROW(TOKEN1, TOKEN2))`) minus (current balance of `RESERVE_ADDR(LIQUIDITY_TOKEN(ESCROW(TOKEN1, TOKEN2)))`), because the real amount of `LIQUIDITY_TOKEN` distributed to users should also include the values of `USER_UNUSED_LIQUIDITY` for [User](#user).

- `PROTOCOL_UNUSED_TOKEN1` and `PROTOCOL_UNUSED_TOKEN2`: Total amounts of Token 1 and Token 2 currently allocated towards protocol fees. These are withdrawable by the [Developer](#developer)

### Local Storage for Users

- `USER_UNUSED_TOKEN1(ADDRESS_OF(ESCROW(TOKEN1, TOKEN2)))` and `USER_UNUSED_TOKEN2(ADDRESS_OF(ESCROW(TOKEN1, TOKEN2)))`: Amounts of Token 1 and Token 2 for `ESCROW(TOKEN1, TOKEN2)` that are immediately refundable to the User with a withdrawal transaction.

  - Acts as a holding area for funds that are "refunded" by AlgoSwap
  - Due to slippage, it is impossible to know with certainty at transaction creation time exactly how much of Token 2 the User will be able to withdraw afterwards. Instead, the swap updates the refundable balance for the user, that they can then withdraw at their leisure.
  - These values are initialized to 0

- `USER_UNUSED_LIQUIDITY(ADDRESS_OF(ESCROW(TOKEN1, TOKEN2)))`: Amount of liquidity token for this escrow contract that are immediately refundable to the User with a withdrawal transaction.
  - Acts as a holding area for liquidity owed to the user by AlgoSwap.
  - Since the ratio of Token1/Token2 can change between transaction creation and finalization time, the amount of liquidity the user should receive can change as well. AlgoSwap thus computes the maximum possible liquidity given User's Token1/Token2 deposit, issues a refund for any remaining Token1/Token2, and updated the refundable balances for the user. User can then withdraw them at their leisure.
  - This value is initialized to 0.

### Assets

- `LIQUIDITY_TOKEN(ESCROW(TOKEN1, TOKEN2))` is the liquidity token associated with `ESCROW(TOKEN1, TOKEN2)`. This represents a share of the liquidity pool, and is gained by adding liquidity to AlgoSwap. The User may withdraw their liquidity from AlgoSwap, burning `LIQUIDITY_TOKEN(ESCROW(TOKEN1, TOKEN2))` in the process and receiving their share of Token 1 and Token 2.

---

## Constants

### Swap Fees

The swap fee intended to be paid to liquidity providers, and is taken out of the Token 2 balance for every swap. This fee is added to the liquidity pool. Sincce the liquidity providers each own shares of the liquidity pool, the fee is distributed to liquidity providers weighted by how much liquidity they provide. Currently set to 0.45%.

### Protocol Fees

The fee intended by to paid to the AlgoSwap developers to cover costs of ongoing maintainence and development. Currently set to be 0.05%.

## Transactions

### Swap Token 1 for Token 2

AlgoSwap enforces the `xy=k` invariant, i.e. `TOTAL_TOKEN1_BALANCE * TOTAL_TOKEN2_BALANCE = k` where `k` is a constant.

Therefore, `TOTAL_TOKEN1_BALANCE * TOTAL_TOKEN2_BALANCE = (TOTAL_TOKEN1_BALANCE + token1_input) * (TOTAL_TOKEN2_BALANCE - token2_output)`

We can solve this to get `token2_output = TOTAL_TOKEN2_BALANCE - ((TOTAL_TOKEN1_BALANCE * TOTAL_TOKEN2_BALANCE) / (TOTAL_TOKEN1_BALANCE + token1_input))`

As per Martin Koppelmann's price formula in [On Path Independence](https://vitalik.ca/general/2017/06/22/marketmakers.html), we'll define `instantaneous_exchange_rate = TOTAL_TOKEN1_BALANCE / TOTAL_TOKEN2_BALANCE` to be the instantaneous exchange rate - the amount of TOKEN2 you receive, divided by the amount of TOKEN1 you sent, if you sent a really really small amount of TOKEN1.

Therefore, we can now define a swap operation as follows:

1. [Frontend](#frontend) asks [User](#user) for their account address, the desired liquidity pair, and the amount of Token 1 to swap.
2. Frontend asks [Wallet](#wallet) to sign an atomic transaction group consisting of 3 transactions:

   1. An `ApplicationCall` transaction from User to [Validator](#validator):

      - `FirstValid` is the current round (no verification needed)
      - `LastValid` is set to be a few rounds in the future (no verification needed)
      - `Application ID` is Validator's application ID (no verification needed)
      - `OnComplete` is `NoOp`
      - `Accounts` is a one-element array consisting of `ADDRESS_OF(ESCROW(TOKEN1, TOKEN2))`
      - `App Arguments` is a two-element array consisting of:
        - The string `"s1"` which identifies this transaction group as a swap for Token 1 to Token 2.
        - `min_token2_received_from_algoswap`: The minimum amount of Token 2 that the user should receive. If the exchange rate rises such that the User would receive less than this amount of Token 2, the swap fails.
      - All other ApplicationCall-specific transaction fields MUST not be present.

   2. An `ApplicationCall` transaction from User to [Manager](#manager):
      - `FirstValid` is the current round (no verification needed)
      - `LastValid` is set to be a few rounds in the future (no verification needed)
      - `Application ID` is Validator's application ID (no verification needed)
      - `OnComplete` is `NoOp`
      - `Accounts` is a one-element array consisting of `ADDRESS_OF(ESCROW(TOKEN1, TOKEN2))`
      - `App Arguments` is a two-element array consisting of:
        - The string `"s1"` which identifies this transaction group as a swap for Token 1 to Token 2.
        - `min_token2_received_from_algoswap`: The minimum amount of Token 2 that the user should receive. If the exchange rate rises such that the User would receive less than this amount of Token 2, the swap fails.
      - All other ApplicationCall-specific transaction fields MUST not be present.
   3. An `AssetTransfer` transaction from User to the [Escrow Contract](#escrow-contract) for Token1/Token2
      - `XferAsset` is Token 1
      - `AssetAmount` is amount specified in the frontend (no verification needed). Call this `token1_input`
      - `AssetSender` is Global zero address (should be the case for regular transfers between accounts)
      - `AssetReceiver` is `ADDRESS_OF(ESCROW(TOKEN1, TOKEN2))`
      - All other AssetTransfer-specific transaction fields MUST not be present

3. Validator runs its approval program for validating the fields of the transaction group
4. Manager runs its approval program for updating the [Application State](#application-state) for this transaction group
   1. Retrieve `TOTAL_TOKEN1_BALANCE` and `TOTAL_TOKEN2_BALANCE` from `MANAGER`'s local storage for `ESCROW(TOKEN1, TOKEN2)`.
   2. Set `TOTAL_TOKEN1_BALANCE += token1_input * SWAP_FEE` in `MANAGER`'s local storage for `ESCROW(TOKEN1, TOKEN2)`. This adds the swap fee amount to the liquidity pool, to be shared by all liquidity providers
   3. Set `PROTOCOL_UNUSED_TOKEN1 += token1_input * PROTOCOL_FEE` in `MANAGER`'s local storage for `ESCROW(TOKEN1, TOKEN2)`. This adds the protocol fee to the protocol fee account.
   4. Compute `token1_input_minus_fees = token1_input_amount * (1 - SWAP_FEE - PROTOCOL_FEE)`.
   5. Compute `token2_output = TOTAL_TOKEN2_BALANCE - (TOTAL_TOKEN1_BALANCE * TOTAL_TOKEN2_BALANCE) / (TOTAL_TOKEN1_BALANCE + token1_input_minus_fees)`.
   6. Assert that `token2_output >= min_token2_received_from_algoswap`.
   7. Set `USER_UNUSED_TOKEN2(ADDRESS_OF(ESCROW(TOKEN1, TOKEN2))) += token2_output` in `MANAGER`'s local storage for `USER`.
   8. Set `TOTAL_TOKEN1_BALANCE += token1_input_minus_fees` in `MANAGER`'s local storage for `ESCROW(TOKEN1, TOKEN2)`.
   9. Set `TOTAL_TOKEN2_BALANCE -= token2_output` in `MANAGER`'s local storage for `ESCROW(TOKEN1, TOKEN2)`.
   10. At this point, we approve the transaction. Since we're depositing, `ESCROW(TOKEN1, TOKEN2)` does not need to run its logicsig.
5. Frontend reads the value of `unused_token2 = USER_UNUSED_TOKEN2(ADDRESS_OF(ESCROW(TOKEN1, TOKEN2)))` from Manager's local storage for the User.
6. Frontend asks Wallet to sign an atomic transaction group consisting of 3 transactions:
   1. An `ApplicationCall` transaction from User to Validator
      - `Application ID` is Validator's application ID (must be verified by `ESCROW(TOKEN1, TOKEN2)`).
      - `OnComplete` is `NoOp`.
      - `Accounts` is a one-element array consisting of `ADDRESS_OF(ESCROW(TOKEN1, TOKEN2))`.
      - `App Arguments` is a one-element array consisting of the string `"r"`, which identifies this transaction group as a "refund".
      - All other ApplicationCall-specific transaction fields must not be present.
   2. An `ApplicationCall` transaction from User to Manager
      - `Application ID` is `MANAGER`'s application ID (must be verified by `ESCROW(TOKEN1, TOKEN2)`).
      - `OnComplete` is `NoOp`.
      - `Accounts` is a one-element array consisting of `ADDRESS_OF(ESCROW(TOKEN1, TOKEN2))`.
      - `App Arguments` is a one-element array consisting of the string `"r"`, which identifies this transaction group as a "refund".
      - All other ApplicationCall-specific transaction fields must not be present.
   3. An `AssetTransfer` transaction from the Escrow Contract that sends the User's refundable Token 2 back to User.
      - `Sender` is `ESCROW(TOKEN1, TOKEN2)`.
      - `XferAsset` is TOKEN1.
      - `AssetAmount` is any amount up to and including `unused_token2`.
      - `AssetSender` is zero (this should always be the case for regular transfers between accounts).
      - `AssetReceiver` is the Algorand address for `USER` (no verification needed).
      - All other AssetTransfer-specific transaction fields must not be present.
7. Validator runs its approval program for validating the fields of the transaction group.
8. Manager runs its approval program for updating the Application State for this transaction group and escrow runs its logicsig:
   - Sets `USER_UNUSED_TOKEN2(ADDRESS_OF(TOKEN1, TOKEN2)) -= unused_token2` in local storage for User.
   - `ESCROW(TOKEN1, TOKEN2)` checks that the transaction group matches up to the required format.
9. Frontend clears Manager's local state for the User, then shows User how much of Token 2 they have received.

### Swap Token 2 for Token 1

Mostly the same as [Swap Token 1 for Token 2](#swap-token-1-for-token-2) except Token 1 and Token 2 switch places.

Solve `TOTAL_TOKEN1_BALANCE * TOTAL_TOKEN2_BALANCE = (TOTAL_TOKEN1_BALANCE - token1_output) * (TOTAL_TOKEN2_BALANCE + token2_input)` to get `token1_output = TOTAL_TOKEN1_BALANCE - ((TOTAL_TOKEN1_BALANCE * TOTAL_TOKEN2_BALANCE) / (TOTAL_TOKEN2_BALANCE + token2_input))`

### Add Liquidity for Token 1 and Token 2

During liquidity addition, AlgoSwap enforces that the instantaneous exchange rate (`TOTAL_TOKEN1_BALANCE / TOTAL_TOKEN2_BALANCE`) stays constant. This prevents liquidity providers from being able to control the exchange rate by changing the amount of liquidity they make available.

Therefore, liquidity providers must deposit an amount such that `(TOTAL_TOKEN1_BALANCE + token1_deposit) / (TOTAL_TOKEN2_BALANCE + token2_deposit) = TOTAL_TOKEN1_BALANCE / TOTAL_TOKEN2_BALANCE`.

We can solve to get `token2_deposit = token1_deposit * TOTAL_TOKEN2_BALANCE / TOTAL_TOKEN1_BALANCE`. Likewise `token1_deposit = token2_deposit * TOTAL_TOKEN1_BALANCE / TOTAL_TOKEN2_BALANCE`.

When `TOTAL_LIQUIDITY_TOKEN_DISTRIBUTED` is 0 (which also implies that one or more of `TOTAL_TOKEN1_BALANCE` or `TOTAL_TOKEN2_BALANCE` are 0), this means that the user adding liquidity is the very first liquidity provider. In this special case, User is able to control the exchange rate, but this can only happen when User is the very first liquidity provider. User would be advised to deposit amounts of TOKEN1 and TOKEN2 that are equal in value on other exchanges, or else arbitrageurs will quickly skim off the difference.

So, if User is sending `x` of Token 1, they need to send `x * TOTAL_TOKEN2_BALANCE / TOTAL_TOKEN1_BALANCE` of Token 2 as well, in order to keep the instantaneous exchange rate the same.

Due to slippage, Users cannot be expected to send exact amounts for each deposit as they might never be able to send the right amount on time before the rate changes. Instead

- `min(token1_deposit, (token2_deposit * TOTAL_TOKEN1_BALANCE / TOTAL_TOKEN2_BALANCE))` of Token 1, and
- `min(token2_deposit, token1_deposit * (TOTAL_TOKEN2_BALANCE / TOTAL_TOKEN1_BALANCE))` of Token 2

are made available in the liquidity pool, and the rest is all refundable to the sender.

To split liquidity fees, we need to measure how much liquidity each liquidity provider is providing. To do this, we define a unitless measure of liquidity where the first liquidity provider on AlgoSwap sets it initially to the amount of TOKEN1 they've provided, and after that liquidity providers gain liquidity as a factor of how much they've increased the amount of TOKEN1 in the liquidity pool. For example, if `TOTAL_TOKEN1_BALANCE` is 1000 and someone adds 1000 of TOKEN1, they doubled the amount of liquidity in the system, therefore they should gain an amount of liquidity equal to whatever amount of liquidity currently exists.

Therefore, we can now define an add liquidity operation as follows:

1. [Frontend](#frontend) asks [User](#user) for their account address, the desired liquidity pair, and the amount of each token to add to the liquidity pool.
2. Frontend asks [Wallet](#wallet) to sign an atomic transaction group consisting of 4 transactions:

   1. An `ApplicationCall` transaction from User to [Validator](#validator):

      - `FirstValid` is the current round (no verification needed)
      - `LastValid` is set to be a few rounds in the future (no verification needed)
      - `Application ID` is Validator's application ID (no verification needed)
      - `OnComplete` is `NoOp`
      - `Accounts` is a one-element array consisting of `ADDRESS_OF(ESCROW(TOKEN1, TOKEN2))`.
      - `App Arguments` is a two-element array consisting of:
        - The string `"a"` which identifies this transaction group as an add liquidity transaction.
        - `min_liquidity_received_from_algoswap`: The minimum amount of liquidity token that the user should receive. If the exchange rate rises such that the User would receive less than this amount of liqudity token, the swap fails.
      - `Foreign Assets` is a one-element array consisting of `LIQUIDITY_TOKEN(ESCROW(TOKEN1, TOKEN2))`.
      - All other ApplicationCall-specific transaction fields MUST not be present.

   2. An `ApplicationCall` transaction from User to [Manager](#manager):
      - `FirstValid` is the current round (no verification needed)
      - `LastValid` is set to be a few rounds in the future (no verification needed)
      - `Application ID` is Validator's application ID (no verification needed)
      - `OnComplete` is `NoOp`
      - `Accounts` is a one-element array consisting of `ADDRESS_OF(ESCROW(TOKEN1, TOKEN2))`.
      - `App Arguments` is a two-element array consisting of:
        - The string `"a"` which identifies this transaction group as an add liquidity transaction.
        - `min_liquidity_received_from_algoswap`: The minimum amount of liquidity token that the user should receive. If the exchange rate rises such that the User would receive less than this amount of liqudity token, the swap fails.
      - `Foreign Assets` is a one-element array consisting of `LIQUIDITY_TOKEN(ESCROW(TOKEN1, TOKEN2))`.
      - All other ApplicationCall-specific transaction fields MUST not be present.
   3. An AssetTransfer transaction from User that sends the specified amount of TOKEN1 to `ESCROW(TOKEN1, TOKEN2)`:
      - `XferAsset` is TOKEN1.
      - `AssetAmount` is anything (no verification needed).
      - `AssetSender` is zero (this should always be the case for regular transfers between accounts).
      - `AssetReceiver` is `ESCROW(TOKEN1, TOKEN2)`.
      - All other AssetTransfer-specific transaction fields MUST not be present.
   4. An AssetTransfer transaction from User that sends the specified amount of TOKEN2 to `ESCROW(TOKEN1, TOKEN2)`:
      - `XferAsset` is TOKEN2.
      - `AssetAmount` is anything (no verification needed).
      - `AssetSender` is zero (this should always be the case for regular transfers between accounts).
      - `AssetReceiver` is `ESCROW(TOKEN1, TOKEN2)`.
      - All other AssetTransfer-specific transaction fields MUST not be present.

3. Validator runs its approval program for validating the fields of the transaction group
4. Manager runs its approval program for updating the [Application State](#application-state) for this transaction group
   1. Retrieve `TOTAL_TOKEN1_BALANCE`, `TOTAL_TOKEN2_BALANCE`, and `TOTAL_LIQUIDITY_TOKEN_DISTRIBUTED` from `MANAGER`'s local storage for `ESCROW(TOKEN1, TOKEN2)`.
   2. If `TOTAL_LIQUIDITY_TOKEN_DISTRIBUTED` is 0:
      1. Compute `token1_used = token1_deposit` and `token2_used = token2_deposit`, where `token1_deposit` and `token2_deposit` are the TOKEN1 and TOKEN2 `AssetAmount` values from the transaction group.
      2. Compute `new_liquidity = token1_deposit`.
   3. Otherwise (if `TOTAL_LIQUIDITY_TOKEN_DISTRIBUTED` is not 0):
      1. Compute `token1_used = min(token1_deposit, token2_deposit * TOTAL_TOKEN1_BALANCE / TOTAL_TOKEN2_BALANCE)`, where `token1_deposit` and `token2_deposit` are the TOKEN1 and TOKEN2 `AssetAmount` values from the transaction group.
      2. Compute `token2_used = min(token2_deposit, token1_deposit * TOTAL_TOKEN2_BALANCE / TOTAL_TOKEN1_BALANCE)`.
      3. Compute `new_liquidity = TOTAL_LIQUIDITY_TOKEN_DISTRIBUTED * token1_deposit / TOTAL_TOKEN1_BALANCE`.
   4. Set `USER_UNUSED_TOKEN1(ADDRESS_OF(ESCROW(TOKEN1, TOKEN2))) += token1_deposit - token1_used` in `MANAGER`'s local storage for `USER`.
   5. Set `USER_UNUSED_TOKEN2(ADDRESS_OF(ESCROW(TOKEN1, TOKEN2))) += token2_deposit - token2_used` in `MANAGER`'s local storage for `USER`.
   6. Set `USER_UNUSED_LIQUIDITY(ADDRESS_OF(ESCROW(TOKEN1, TOKEN2))) += new_liquidity` in `MANAGER`'s local storage for `USER`.
   7. Set `TOTAL_TOKEN1_BALANCE += token1_used` and `TOTAL_TOKEN2_BALANCE += token2_used` and `TOTAL_LIQUIDITY_TOKEN_DISTRIBUTED += new_liquidity` in `MANAGER`'s local storage for `ESCROW(TOKEN1, TOKEN2)`. These amounts are now part of the liquidity pool and can only be retrieved with a liquidity withdrawal operation. The unused remainder of `USER`'s tokens in `MANAGER` can now be refunded to `USER` in the following steps.
5. Frontend reads the value of `unused_token1 = USER_UNUSED_TOKEN1(ADDRESS_OF(ESCROW(TOKEN1, TOKEN2)))`, `unused_token2 = USER_UNUSED_TOKEN2(ADDRESS_OF(ESCROW(TOKEN1, TOKEN2)))`, and `unused_liquidity = USER_UNUSED_LIQUIDITY(ADDRESS_OF(ESCROW(TOKEN1, TOKEN2)))` from Manager's local storage for the User.
6. Frontend asks Wallet to sign an atomic transaction group consisting of 3 transactions:
   1. An `ApplicationCall` transaction from User to Validator
      - `Application ID` is Validator's application ID (must be verified by `ESCROW(TOKEN1, TOKEN2)`).
      - `OnComplete` is `NoOp`.
      - `Accounts` is a one-element array consisting of `ADDRESS_OF(ESCROW(TOKEN1, TOKEN2))`.
      - `App Arguments` is a one-element array consisting of the string `"r"`, which identifies this transaction group as a "refund".
      - All other ApplicationCall-specific transaction fields must not be present.
   2. An `ApplicationCall` transaction from User to Manager
      - `Application ID` is Manager's application ID (must be verified by `ESCROW(TOKEN1, TOKEN2)`).
      - `OnComplete` is `NoOp`.
      - `Accounts` is a one-element array consisting of `ADDRESS_OF(ESCROW(TOKEN1, TOKEN2))`.
      - `App Arguments` is a one-element array consisting of the string `"r"`, which identifies this transaction group as a "refund".
      - All other ApplicationCall-specific transaction fields must not be present.
   3. An `AssetTransfer` transaction from `ESCROW(TOKEN1, TOKEN2)` that sends `USER`'s refundable TOKEN1 back to `USER`.
      - `Sender` is `ESCROW(TOKEN1, TOKEN2)`.
      - `XferAsset` is TOKEN1.
      - `AssetAmount` is any amount up to and including `unused_token1`.
      - `AssetSender` is zero (this should always be the case for regular transfers between accounts).
      - `AssetReceiver` is the Algorand address for `USER` (no verification needed).
      - All other AssetTransfer-specific transaction fields must not be present.
7. Validator runs its approval program for validating the fields of the transaction group.
8. Manager runs its approval program for updating the [Application State](#application-state) for this transaction group and escrow runs its logicsig:
   - Sets `USER_UNUSED_TOKEN1(ADDRESS_OF(ESCROW(TOKEN1, TOKEN2))) -= unused_token1` in local storage for User.
   - `ESCROW(TOKEN1, TOKEN2)` checks that the transaction group matches up to the required format.
9. Same as steps 6 and 7, but for Token 2 rather than Token 1
10. Same as steps 6 and 7, but for `LIQUIDITY_TOKEN(ESCROW(TOKEN1, TOKEN2))` rather than Token 1
11. Frontend clears Manager's local state for the User, then shows User how much of Token 1 and Token 2 they've successfully added to the liquidity pool.

### Withdraw Liquididity for Token 1 and Token 2

We can define a withdraw liquidity operation as follows:

1. [Frontend](#frontend) asks [User](#user) for their account address, the desired liquidity pair, and the amount of liquidity to withdraw from the liquidity pool.
2. Frontend asks [Wallet](#wallet) to sign an atomic transaction group consisting of 3 transactions:

   1. An `ApplicationCall` transaction from User to [Validator](#validator):

      - `FirstValid` is the current round (no verification needed).
      - `LastValid` is set to be a few rounds in the future, perhaps around 30 seconds (no verification needed). This is intended to limit frontrunning techniques that delay the transaction for many rounds.
      - `Application ID` is `MANAGER`'s application ID (no verification needed).
      - `OnComplete` is `NoOp`.
      - `Accounts` is a two-element array consisting of `ADDRESS_OF(ESCROW(TOKEN1, TOKEN2))`.
      - `App Arguments` is a three-element array consisting of:
        - The string "w": identifies this transaction as a "withdraw liquidity".
        - `min_token1_received_from_algoswap`: the swap fails if the exchange rate rises such that `USER` would receive less than this amount of TOKEN1. This is intended to limit frontrunning techniques that manipulate the liquidity pool distribution.
        - `min_token2_received_from_algoswap`: the swap fails if the exchange rate rises such that `USER` would receive less than this amount of TOKEN2. This is intended to limit frontrunning techniques that manipulate the liquidity pool distribution.
      - `Foreign Assets` is a one-element array consisting of `LIQUIDITY_TOKEN(ESCROW(TOKEN1, TOKEN2))`.
      - All other ApplicationCall-specific transaction fields MUST not be present.

   2. An `ApplicationCall` transaction from User to [Manager](#manager):
      - `FirstValid` is the current round (no verification needed).
      - `LastValid` is set to be a few rounds in the future, perhaps around 30 seconds (no verification needed). This is intended to limit frontrunning techniques that delay the transaction for many rounds.
      - `Application ID` is `MANAGER`'s application ID (no verification needed).
      - `OnComplete` is `NoOp`.
      - `Accounts` is a one-element array consisting of `ADDRESS_OF(ESCROW(TOKEN1, TOKEN2))`.
      - `App Arguments` is a three-element array consisting of:
        - The string "w": identifies this transaction as a "withdraw liquidity".
        - `min_token1_received_from_algoswap`: the swap fails if the exchange rate rises such that `USER` would receive less than this amount of TOKEN1. This is intended to limit frontrunning techniques that manipulate the liquidity pool distribution.
        - `min_token2_received_from_algoswap`: the swap fails if the exchange rate rises such that `USER` would receive less than this amount of TOKEN2. This is intended to limit frontrunning techniques that manipulate the liquidity pool distribution.
      - `Foreign Assets` is a one-element array consisting of `LIQUIDITY_TOKEN(ESCROW(TOKEN1, TOKEN2))`.
      - All other ApplicationCall-specific transaction fields MUST not be present.
   3. An AssetTransfer transaction from User that sends the specified amount of `LIQUIDITY_TOKEN(ESCROW(TOKEN1, TOKEN2))` to `ESCROW(TOKEN1, TOKEN2)`:
      - `XferAsset` is `LIQUIDITY_TOKEN(ESCROW(TOKEN1, TOKEN2))`.
      - `AssetAmount` is anything (no verification needed).
      - `AssetSender` is zero (this should always be the case for regular transfers between accounts).
      - `AssetReceiver` is `ESCROW(TOKEN1, TOKEN2)`.
      - All other AssetTransfer-specific transaction fields MUST not be present.

3. Validator runs its approval program for validating the fields of the transaction group.
4. Manager runs its approval program for updating the [Application State](#application-state) for this transaction group
   1. Retrieve `TOTAL_TOKEN1_BALANCE`, `TOTAL_TOKEN2_BALANCE`, and `TOTAL_LIQUIDITY_TOKEN_DISTRIBUTED` from `MANAGER`'s local storage for `ESCROW(TOKEN1, TOKEN2)`.
   2. Compute `token1_available = TOTAL_TOKEN1_BALANCE * user_liquidity / TOTAL_LIQUIDITY_TOKEN_DISTRIBUTED` and `token2_available = TOTAL_TOKEN2_BALANCE * user_liquidity / TOTAL_LIQUIDITY_TOKEN_DISTRIBUTED`, where `user_liquidity` is the `AssetAmount` value in the transaction group. This is the fraction of the liquidity pool provided by `USER`. As the liquidity pool grows from liquidity provider fees, `USER` still owns the same slice of the pie, but the whole pie grew larger, so `USER`'s liquidity tokens are worth more than before.
   3. Set `USER_UNUSED_TOKEN1(ADDRESS_OF(ESCROW(TOKEN1, TOKEN2))) += token1_available` in `MANAGER`'s local storage for `USER`.
   4. Set `USER_UNUSED_TOKEN2(ADDRESS_OF(ESCROW(TOKEN1, TOKEN2))) += token2_available` in `MANAGER`'s local storage for `USER`.
   5. Set `TOTAL_TOKEN1_BALANCE -= token1_available`, `TOTAL_TOKEN2_BALANCE -= token2_available`, and `TOTAL_LIQUIDITY_TOKEN_DISTRIBUTED -= user_liquidity` in `MANAGER`'s local storage for `ESCROW(TOKEN1, TOKEN2)`.
5. Frontend reads the value of `unused_token1 = USER_UNUSED_TOKEN1(ADDRESS_OF(ESCROW(TOKEN1, TOKEN2)))` and `unused_token2 = USER_UNUSED_TOKEN2(ADDRESS_OF(ESCROW(TOKEN1, TOKEN2)))` from Manager's local storage for the User.
6. Frontend asks Wallet to sign an atomic transaction group consisting of 3 transactions:
   1. An `ApplicationCall` transaction from User to Validator
      - `Application ID` is Validator's application ID (must be verified by `ESCROW(TOKEN1, TOKEN2)`).
      - `OnComplete` is `NoOp`.
      - `Accounts` is a one-element array consisting of `ADDRESS_OF(ESCROW(TOKEN1, TOKEN2))`.
      - `App Arguments` is a one-element array consisting of the string `"r"`, which identifies this transaction group as a "refund".
      - All other ApplicationCall-specific transaction fields must not be present.
   2. An `ApplicationCall` transaction from User to Manager
      - `Application ID` is Manager's application ID (must be verified by `ESCROW(TOKEN1, TOKEN2)`).
      - `OnComplete` is `NoOp`.
      - `Accounts` is a one-element array consisting of `ADDRESS_OF(ESCROW(TOKEN1, TOKEN2))`.
      - `App Arguments` is a one-element array consisting of the string `"r"`, which identifies this transaction group as a "refund".
      - All other ApplicationCall-specific transaction fields must not be present.
   3. An `AssetTransfer` transaction from `ESCROW(TOKEN1, TOKEN2)` that sends `USER`'s refundable TOKEN1 back to `USER`.
      - `Sender` is `ESCROW(TOKEN1, TOKEN2)`.
      - `XferAsset` is TOKEN1.
      - `AssetAmount` is any amount up to and including `unused_token1`.
      - `AssetSender` is zero (this should always be the case for regular transfers between accounts).
      - `AssetReceiver` is the Algorand address for `USER` (no verification needed).
      - All other AssetTransfer-specific transaction fields must not be present.
7. Validator runs its approval program for validating the fields of the transaction group.
8. Manager runs its approval program for updating the [Application State](#application-state) for this transaction group and escrow runs its logicsig:
   - Sets `USER_UNUSED_TOKEN1(ADDRESS_OF(ESCROW(TOKEN1, TOKEN2))) -= unused_token1` in local storage for User.
   - `ESCROW(TOKEN1, TOKEN2)` checks that the transaction group matches up to the required format.
9. Same as steps 6 and 7, but for Token 2 rather than Token 1
10. Frontend clears Manager's local state for the User, then shows User how much of Token 1 and Token 2 they've successfully withdrawn from the AlgoSwap liquidity pool.

### Withdrawing Protocol Fees

1. [Developer](#developer) reads the current values of `PROTOCOL_UNUSED_TOKEN1` and `PROTOCOL_UNUSED_TOKEN2` from Manager's local state for some Escrow Contract.
2. Developer creates and signs an atomic transaction group consisting of 4 transactions:
   1. An `ApplicationCall` transaction from Developer to [Validator](#validator)
      - `Sender` is `DEVELOPER_ADDRESS`
      - `Application ID` is Validator's application ID (must be verified by `ESCROW(TOKEN1, TOKEN2)`)
      - `OnComplete` is `NoOp`
      - `Accounts` is a one-element array consisting of `ADDRESS_OF(ESCROW(TOKEN1, TOKEN2))`
      - `App Arguments` is a one-element array consisting of the string `"p"` which identifies this transaction group as a protocol fee refund.
      - All other ApplicationCall-specific transaction fields MUST not be present.
   2. An `AppliationCall` transaction from Developer to [Manager](#manager)
      - `Sender` is `DEVELOPER_ADDRESS`
      - `Application ID` is Validator's application ID (must be verified by `ESCROW(TOKEN1, TOKEN2)`)
      - `OnComplete` is `NoOp`
      - `Accounts` is a one-element array consisting of `ADDRESS_OF(ESCROW(TOKEN1, TOKEN2))`
      - `App Arguments` is a one-element array consisting of the string `"p"` which identifies this transaction group as a protocol fee refund.
      - All other ApplicationCall-specific transaction fields MUST not be present.
   3. An `AssetTransfer` transaction from `ESCROW(TOKEN1, TOKEN2)` that sends unclaimed Token 1 protocol fees to `DEVELOPER_ADDRESS`
      - `Sender` is `ESCROW(TOKEN1, TOKEN2)`.
      - `XferAsset` is TOKEN1.
      - `AssetAmount` is any amount `withdrawn_token1` up to and including the current value of `PROTOCOL_UNUSED_TOKEN1`.
      - `AssetSender` is zero (this should always be the case for regular transfers between accounts).
      - `AssetReceiver` is `DEVELOPER_ADDRESS` (no verification needed).
      - All other AssetTransfer-specific transaction fields MUST not be present.
   4. An `AssetTransfer` transaction from `ESCROW(TOKEN1, TOKEN2)` that sends unclaimed Token 2 protocol fees to `DEVELOPER_ADDRESS`
      - `Sender` is `ESCROW(TOKEN1, TOKEN2)`.
      - `XferAsset` is TOKEN2.
      - `AssetAmount` is any amount `withdrawn_token2` up to and including the current value of `PROTOCOL_UNUSED_TOKEN2`.
      - `AssetSender` is zero (this should always be the case for regular transfers between accounts).
      - `AssetReceiver` is `DEVELOPER_ADDRESS` (no verification needed).
      - All other AssetTransfer-specific transaction fields must not be present.
3. Validator runs its approval program to validate the transaction fields for this transaction group
4. Manager runs its approval program for updating the [Application State](#application-state) for this transaction group and escrow runs its logicsig
   - Sets `PROTOCOL_UNUSED_TOKEN1(ADDRESS_OF(ESCROW(TOKEN1, TOKEN2))) -= withdrawn_token1` and `PROTOCOL_UNUSED_TOKEN2(ADDRESS_OF(ESCROW(TOKEN1, TOKEN2))) -= withdrawn_token2` in local storage for User (Developer)
   - `ESCROW(TOKEN1, TOKEN2)` checks that the transaction group matches up to the required format.
