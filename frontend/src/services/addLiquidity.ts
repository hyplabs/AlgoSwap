// @ts-nocheck
import * as constants from './constants';
import algosdk from 'algosdk';

export default async function addLiquidity(
  from: string,
  escrowAddr: string,
  token1Amount: number,
  token1Index: number,
  token2Amount: number,
  token2Index: number,
  minLiquidityTokenReceived: number
) {
  // TODO: encode these and send with txns
  const args = ['a', minLiquidityTokenReceived];

  const txParams = await AlgoSigner.algod({
    ledger: constants.LEDGER_NAME,
    path: '/v2/transactions/params',
  });

  // Call to validator
  let txn1 = {
    type: 'appl',
    from: from,
    suggestedParams: txParams,
    appIndex: constants.VALIDATOR_APP_ID,
    appOnComplete: 0, // 0 == NoOp
    appArgs: '',
    appAccounts: [escrowAddr],
  };

  // Transaction to manager
  let txn2 = {
    type: 'appl',
    from: from,
    suggestedParams: txParams,
    appIndex: constants.MANAGER_APP_ID,
    appOnComplete: 0, // 0 == NoOp
    appArgs: '', // TODO: figure this out
    appAccounts: [escrowAddr],
  };

  // Send Token1 to Escrow
  let txn3 = {
    type: 'axfer',
    from: from,
    to: escrowAddr,
    amount: token1Amount,
    suggestedParams: txParams,
    assetIndex: token1Index,
  };

  // Send Token2 to Escrow
  let txn4 = {
    type: 'axfer',
    from: from,
    to: escrowAddr,
    amount: token2Amount,
    suggestedParams: txParams,
    assetIndex: token2Index,
  };

  let txnGroup = await algosdk.assignGroupID([txn1, txn2, txn3, txn4]);

  // Modify the group fields in original transactions to be base64 encoded strings
  txn1.group = txnGroup[0].group.toString('base64');
  txn2.group = txnGroup[1].group.toString('base64');
  txn3.group = txnGroup[2].group.toString('base64');
  txn4.group = txnGroup[3].group.toString('base64');

  let signedTxn1 = await AlgoSigner.sign(txn1);
  let signedTxn2 = await AlgoSigner.sign(txn2);
  let signedTxn3 = await AlgoSigner.sign(txn3);
  let signedTxn4 = await AlgoSigner.sign(txn4);

  if (!(signedTxn1 && signedTxn2 && signedTxn3 && signedTxn4)) {
    return console.error('User rejected signatures');
  }

  // Get the decoded binary Uint8Array values from the blobs
  const decoded_1 = new Uint8Array(
    atob(signed1.blob)
      .split('')
      .map(x => x.charCodeAt(0))
  );
  const decoded_2 = new Uint8Array(
    atob(signed2.blob)
      .split('')
      .map(x => x.charCodeAt(0))
  );
  const decoded_3 = new Uint8Array(
    atob(signed3.blob)
      .split('')
      .map(x => x.charCodeAt(0))
  );

  // Use their combined length to create a 3rd array
  let combined_decoded_txns = new Uint8Array(
    decoded_1.byteLength + decoded_2.byteLength + decoded_3.byteLength
  );

  // Starting at the 0 position, fill in the binary for the first object
  combined_decoded_txns.set(new Uint8Array(decoded_1), 0);
  // Starting at the first object byte length, fill in the 2nd binary value
  combined_decoded_txns.set(new Uint8Array(decoded_2), decoded_1.byteLength);
  // Starting at the first+second object byte length, fill in the 3rd binary value
  combined_decoded_txns.set(new Uint8Array(decoded_3), decoded_1.byteLength + decoded_2.byteLength);

  // Modify our combined array values back to an encoded 64bit string
  const grouped_txns = btoa(String.fromCharCode.apply(null, combined_decoded_txns));

  const res = await AlgoSigner.send({
    ledger: constants.LEDGER_NAME,
    tx: grouped_txns,
  });
}
