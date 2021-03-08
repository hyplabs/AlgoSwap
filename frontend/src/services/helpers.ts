// @ts-nocheck
import * as constants from './constants';
import PairDetails from '../models/PairDetails';
import algosdk from 'algosdk';

export async function calculateUnused(
  user: string,
  escrow: string,
  prefix: string
): Promise<number> {
  const accountInfo = await AlgoSigner.algod({
    ledger: constants.LEDGER_NAME,
    path: `/v2/accounts/${user}`,
  });
  const localState = accountInfo['apps-local-state'];

  for (let block of localState) {
    if (block.id === constants.MANAGER_APP_ID) {
      for (let kvs of block['key-value']) {
        let decodedKey = Buffer.from(kvs.key, 'base64');
        let prefixKey = decodedKey.slice(0, 2).toString('utf-8');
        let addrBytes = decodedKey.slice(2);
        let resultantEscrowAddress = algosdk.encodeAddress(addrBytes);

        if (prefixKey === prefix && resultantEscrowAddress === escrow) {
          console.log(prefixKey);
          console.log(resultantEscrowAddress);
          console.log(kvs.value.uint);
          return parseInt(kvs.value.uint);
        }
      }
    }
  }

  return 0;
}

export async function getToken1Refund(user: string, details: PairDetails) {
  const encodedAppArgs = [Buffer.from('r').toString('base64')];

  const unusedToken1 = await calculateUnused(user, details.escrowAddress, 'U1');
  if (unusedToken1 !== 0) {
    try {
      const txParams = await AlgoSigner.algod({
        ledger: constants.LEDGER_NAME,
        path: '/v2/transactions/params',
      });

      // Call to validator
      let txn1 = {
        type: 'appl',
        from: user,
        appIndex: constants.VALIDATOR_APP_ID,
        appOnComplete: 0, // 0 == NoOp
        appArgs: encodedAppArgs,
        appAccounts: [details.escrowAddress],
        fee: txParams['fee'],
        firstRound: txParams['last-round'],
        lastRound: txParams['last-round'] + 1000,
        genesisID: txParams['genesis-id'],
        genesisHash: txParams['genesis-hash'],
      };

      // Call to manager
      let txn2 = {
        type: 'appl',
        from: user,
        appIndex: constants.MANAGER_APP_ID,
        appOnComplete: 0, // 0 == NoOp
        appArgs: encodedAppArgs,
        appAccounts: [details.escrowAddress],
        fee: txParams['fee'],
        firstRound: txParams['last-round'],
        lastRound: txParams['last-round'] + 1000,
        genesisID: txParams['genesis-id'],
        genesisHash: txParams['genesis-hash'],
      };

      // Make logicsig
      let program = Uint8Array.from(Buffer.from(details.escrowLogicSig, 'base64'));
      let lsig = algosdk.makeLogicSig(program);

      let txn3 = {
        type: 'axfer',
        from: details.escrowAddress,
        to: user,
        amount: unusedToken1,
        assetIndex: details.token1Index,
        fee: txParams['fee'],
        firstRound: txParams['last-round'],
        lastRound: txParams['last-round'] + 1000,
        genesisID: txParams['genesis-id'],
        genesisHash: txParams['genesis-hash'],
      };

      let txnGroup = await algosdk.assignGroupID([txn1, txn2, txn3]);

      // Modify the group fields in original transactions to be base64 encoded strings
      txn1.group = txnGroup[0].group.toString('base64');
      txn2.group = txnGroup[1].group.toString('base64');
      txn3.group = txnGroup[2].group.toString('base64');

      let signedTxn1 = await AlgoSigner.sign(txn1);
      let signedTxn2 = await AlgoSigner.sign(txn2);
      let signedTxn3 = algosdk.signLogicSigTransaction(txn3, lsig);

      if (!(signedTxn1 && signedTxn2 && signedTxn3)) {
        return console.error('User rejected signatures');
      }

      // Get the decoded binary UInt8Array values from the blobs
      const decoded_1 = new Uint8Array(
        atob(signedTxn1.blob)
          .split('')
          .map(x => x.charCodeAt(0))
      );

      const decoded_2 = new Uint8Array(
        atob(signedTxn2.blob)
          .split('')
          .map(x => x.charCodeAt(0))
      );

      const decoded_3 = new Uint8Array(
        atob(signedTxn3.blob)
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

      await AlgoSigner.send({
        ledger: constants.LEDGER_NAME,
        tx: grouped_txns,
      });
    } catch (e) {
      console.error(e);
    }
  } else {
    console.log('No unused token 1');
  }
}

export async function getToken2Refund(user: string, details: PairDetails) {
  const encodedAppArgs = [Buffer.from('r').toString('base64')];

  const unusedToken2 = await calculateUnused(user, details.escrowAddress, 'U2');

  if (unusedToken2 !== 0) {
    try {
      const txParams = await AlgoSigner.algod({
        ledger: constants.LEDGER_NAME,
        path: '/v2/transactions/params',
      });

      // Call to validator
      let txn1 = {
        type: 'appl',
        from: user,
        appIndex: constants.VALIDATOR_APP_ID,
        appOnComplete: 0, // 0 == NoOp
        appArgs: encodedAppArgs,
        appAccounts: [details.escrowAddress],
        fee: txParams['fee'],
        firstRound: txParams['last-round'],
        lastRound: txParams['last-round'] + 1000,
        genesisID: txParams['genesis-id'],
        genesisHash: txParams['genesis-hash'],
      };

      // Call to manager
      let txn2 = {
        type: 'appl',
        from: user,
        appIndex: constants.MANAGER_APP_ID,
        appOnComplete: 0, // 0 == NoOp
        appArgs: encodedAppArgs,
        appAccounts: [details.escrowAddress],
        fee: txParams['fee'],
        firstRound: txParams['last-round'],
        lastRound: txParams['last-round'] + 1000,
        genesisID: txParams['genesis-id'],
        genesisHash: txParams['genesis-hash'],
      };

      // Make logicsig
      let program = Uint8Array.from(Buffer.from(details.escrowLogicSig, 'base64'));
      let lsig = algosdk.makeLogicSig(program);

      let txn3 = {
        type: 'axfer',
        from: details.escrowAddress,
        to: user,
        amount: unusedToken2,
        assetIndex: details.token2Index,
        fee: txParams['fee'],
        firstRound: txParams['last-round'],
        lastRound: txParams['last-round'] + 1000,
        genesisID: txParams['genesis-id'],
        genesisHash: txParams['genesis-hash'],
      };

      let txnGroup = await algosdk.assignGroupID([txn1, txn2, txn3]);

      // Modify the group fields in original transactions to be base64 encoded strings
      txn1.group = txnGroup[0].group.toString('base64');
      txn2.group = txnGroup[1].group.toString('base64');
      txn3.group = txnGroup[2].group.toString('base64');

      let signedTxn1 = await AlgoSigner.sign(txn1);
      let signedTxn2 = await AlgoSigner.sign(txn2);
      let signedTxn3 = algosdk.signLogicSigTransaction(txn3, lsig);

      if (!(signedTxn1 && signedTxn2 && signedTxn3)) {
        return console.error('User rejected signatures');
      }

      // Get the decoded binary UInt8Array values from the blobs
      const decoded_1 = new Uint8Array(
        atob(signedTxn1.blob)
          .split('')
          .map(x => x.charCodeAt(0))
      );

      const decoded_2 = new Uint8Array(
        atob(signedTxn2.blob)
          .split('')
          .map(x => x.charCodeAt(0))
      );

      const decoded_3 = new Uint8Array(
        atob(signedTxn3.blob)
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

      await AlgoSigner.send({
        ledger: constants.LEDGER_NAME,
        tx: grouped_txns,
      });
    } catch (e) {
      console.error(e);
    }
  } else {
    console.log('No unused token 2');
  }
}

export async function getLiquidityTokenRefund(user: string, details: PairDetails) {
  const encodedAppArgs = [Buffer.from('r').toString('base64')];

  const unusedLiquidityToken = await calculateUnused(user, details.escrowAddress, 'UL');

  if (unusedLiquidityToken !== 0) {
    try {
      const txParams = await AlgoSigner.algod({
        ledger: constants.LEDGER_NAME,
        path: '/v2/transactions/params',
      });

      // Call to validator
      let txn1 = {
        type: 'appl',
        from: user,
        appIndex: constants.VALIDATOR_APP_ID,
        appOnComplete: 0, // 0 == NoOp
        appArgs: encodedAppArgs,
        appAccounts: [details.escrowAddress],
        fee: txParams['fee'],
        firstRound: txParams['last-round'],
        lastRound: txParams['last-round'] + 1000,
        genesisID: txParams['genesis-id'],
        genesisHash: txParams['genesis-hash'],
      };

      // Call to manager
      let txn2 = {
        type: 'appl',
        from: user,
        appIndex: constants.MANAGER_APP_ID,
        appOnComplete: 0, // 0 == NoOp
        appArgs: encodedAppArgs,
        appAccounts: [details.escrowAddress],
        fee: txParams['fee'],
        firstRound: txParams['last-round'],
        lastRound: txParams['last-round'] + 1000,
        genesisID: txParams['genesis-id'],
        genesisHash: txParams['genesis-hash'],
      };

      // Make logicsig
      let program = Uint8Array.from(Buffer.from(details.escrowLogicSig, 'base64'));
      let lsig = algosdk.makeLogicSig(program);

      let txn3 = {
        type: 'axfer',
        from: details.escrowAddress,
        to: user,
        amount: unusedLiquidityToken,
        assetIndex: details.liquidityTokenIndex,
        fee: txParams['fee'],
        firstRound: txParams['last-round'],
        lastRound: txParams['last-round'] + 1000,
        genesisID: txParams['genesis-id'],
        genesisHash: txParams['genesis-hash'],
      };

      let txnGroup = await algosdk.assignGroupID([txn1, txn2, txn3]);

      // Modify the group fields in original transactions to be base64 encoded strings
      txn1.group = txnGroup[0].group.toString('base64');
      txn2.group = txnGroup[1].group.toString('base64');
      txn3.group = txnGroup[2].group.toString('base64');

      let signedTxn1 = await AlgoSigner.sign(txn1);
      let signedTxn2 = await AlgoSigner.sign(txn2);
      let signedTxn3 = algosdk.signLogicSigTransaction(txn3, lsig);

      if (!(signedTxn1 && signedTxn2 && signedTxn3)) {
        return console.error('User rejected signatures');
      }

      // Get the decoded binary UInt8Array values from the blobs
      const decoded_1 = new Uint8Array(
        atob(signedTxn1.blob)
          .split('')
          .map(x => x.charCodeAt(0))
      );

      const decoded_2 = new Uint8Array(
        atob(signedTxn2.blob)
          .split('')
          .map(x => x.charCodeAt(0))
      );

      const decoded_3 = new Uint8Array(
        atob(signedTxn3.blob)
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

      await AlgoSigner.send({
        ledger: constants.LEDGER_NAME,
        tx: grouped_txns,
      });
    } catch (e) {
      console.error(e);
    }
  } else {
    console.log('No unused liquidity token');
  }
}
