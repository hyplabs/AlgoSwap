// @ts-nocheck
import * as constants from './constants';
import algosdk from 'algosdk';

export default async function withdrawLiquidity(
  from: string,
  escrowAddr: string,
  liquidityTokenAmount: number,
  liquidityTokenIndex: number,
  minToken1Received: number,
  minToken2Received: number
) {
  try {
    // TODO: encode these and send with txns
    const args = ['w', minToken1Received, minToken2Received];

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

    // Call to manager
    let txn2 = {
      type: 'appl',
      from: from,
      suggestedParams: txParams,
      appIndex: constants.MANAGER_APP_ID,
      appOnComplete: 0, // 0 == NoOp
      appArgs: '',
      appAccounts: [escrowAddr],
    };

    // Send liquidity token to Escrow
    let txn3 = {
      type: 'axfer',
      from: from,
      to: escrowAddr,
      amount: liquidityTokenAmount,
      suggestedParams: txParams,
      assetIndex: liquidityTokenIndex,
    };

    let txnGroup = await algosdk.assignGroupID([txn1, txn2, txn3]);

    // Modify the group fields in orginal transactions to be base64 encoded strings
    txn1.group = txnGroup[0].group.toString('base64');
    txn2.group = txnGroup[1].group.toString('base64');
    txn3.group = txnGroup[2].group.toString('base64');

    let signedTxn1 = await AlgoSigner.sign(txn1);
    let signedTxn2 = await AlgoSigner.sign(txn2);
    let signedTxn3 = await AlgoSigner.sign(txn3);

    if (!(signedTxn1 && signedTxn2 && signedTxn3)) {
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
    combined_decoded_txns.set(
      new Uint8Array(decoded_3),
      decoded_1.byteLength + decoded_2.byteLength
    );

    // Modify our combined array values back to an encoded 64bit string
    const grouped_txns = btoa(String.fromCharCode.apply(null, combined_decoded_txns));

    const res = await AlgoSigner.send({
      ledger: constants.LEDGER_NAME,
      tx: grouped_txns,
    });
    console.log(res);
  } catch (e) {
    console.error(e);
  }
}
