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

import {connectToAlgoSigner} from '../../utils/connectToAlgoSigner';
import './WalletModal.scss';

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

  async function connectToAlgoSignerWallet() {
    const accountAddress = await connectToAlgoSigner();
    dispatch(setAccountAddress(accountAddress));
    toggleWalletModal();
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
        <button className="Wallet-modal-select" onClick={connectToAlgoSignerWallet}>
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
