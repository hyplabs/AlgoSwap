/*
  Need to disable typescript check to outsmart Rodal package issue.
  If you are making any changes to the code, remove this line temporarily
  as we want to pass typecheck testing as much as possible.
*/
//@ts-nocheck
import React from 'react';
import {useDispatch} from 'react-redux';

import {setAccountAddress} from '../../redux/actions';

/* eslint-disable */
import Rodal from 'rodal';
import 'rodal/lib/rodal.css';

import './WalletModal.scss';
import {calculateUnused} from '../../services/helpers';

interface Props {
  openWalletModal: boolean;
  toggleWalletModal: () => void;
}

const WalletModal: React.FC<Props> = ({openWalletModal, toggleWalletModal}) => {
  const dispatch = useDispatch();

  const modalStyle = {
    position: 'relative',
    borderRadius: '30px',
    top: '210px',
  };

  async function connectToAlgoSigner() {
    if (typeof AlgoSigner !== 'undefined') {
      try {
        await AlgoSigner.connect();
        let testnetAccounts = await AlgoSigner.accounts({
          ledger: 'TestNet',
        });
        dispatch(setAccountAddress(testnetAccounts[0].address));
        toggleWalletModal();
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
      } catch (e) {
        console.error(e);
      }
    }
  }

  return (
    <Rodal
      width={420}
      customStyles={modalStyle}
      visible={openWalletModal}
      onClose={toggleWalletModal}
      height={200}
      showCloseButton={true}
    >
      <div className="Wallet-modal">
        <div className="Wallet-modal-header">
          <div className="Wallet-modal-header-image">
            <img className="App-logo-modal" src="/logo.png" alt="AlgoSwap" />
          </div>
          Connect to a wallet
        </div>
        <button className="Wallet-modal-select" onClick={connectToAlgoSigner}>
          <div className="Wallet-modal-item">
            AlgoSigner
            <img className="Wallet-logo-modal" src="/algosigner.png" alt="AlgoSigner" />
          </div>
        </button>
      </div>
    </Rodal>
  );
};

export default WalletModal;
