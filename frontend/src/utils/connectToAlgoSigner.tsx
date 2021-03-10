//@ts-nocheck
import {calculateUnused} from '../services/helpers';

export async function connectToAlgoSigner() {
  if (typeof AlgoSigner !== 'undefined') {
    try {
      await AlgoSigner.connect();
      let testnetAccounts = await AlgoSigner.accounts({
        ledger: 'TestNet',
      });
      await calculateUnused(
        testnetAccounts[0].address,
        'SDJ5WZSZXRQK6YQUXDTKUXWGWX23DNQM62TCB2Z2WDAISGPUQZG6LB6TJM',
        'U1'
      );
      await calculateUnused(
        testnetAccounts[0].address,
        'SDJ5WZSZXRQK6YQUXDTKUXWGWX23DNQM62TCB2Z2WDAISGPUQZG6LB6TJM',
        'U2'
      );
      await calculateUnused(
        testnetAccounts[0].address,
        'SDJ5WZSZXRQK6YQUXDTKUXWGWX23DNQM62TCB2Z2WDAISGPUQZG6LB6TJM',
        'UL'
      );

      return testnetAccounts[0].address;
    } catch (e) {
      console.error(e);
    }
  }
}
