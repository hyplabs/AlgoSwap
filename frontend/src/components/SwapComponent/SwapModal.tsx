/*
  Need to disable typescript check to outsmart Rodal package issue.
  If you are making any changes to the code, remove this line temporarily
  as we want to pass typecheck testing as much as possible.
*/
// @ts-nocheck
import React from 'react';

/* eslint-disable */
import Rodal from 'rodal';
import 'rodal/lib/rodal.css';

import './SwapModal.scss';

interface Props {
  fromAmount: string;
  toAmount: string;
  fromToken: string;
  toToken: string;

  openSwapModal: boolean;
  toggleSwapModal: () => void;
}

const SwapModal: React.FC<Props> = ({
  fromAmount,
  toAmount,
  fromToken,
  toToken,
  openSwapModal,
  toggleSwapModal,
}) => {
  const modalStyle = {
    position: 'relative',
    borderRadius: '30px',
    top: '210px',
  };

  return (
    <Rodal
      width={420}
      customStyles={modalStyle}
      visible={openSwapModal}
      onClose={toggleSwapModal}
      height={400}
      showCloseButton={true}
    >
      <div className="SwapComponent-swap-modal">
        <div className="SwapComponent-swap-modal-header">
          <div className="SwapComponent-swap-modal-header-image">
            <img className="App-logo-modal" src="/logo.png" alt="AlgoSwap" />
          </div>
          Confirm Swap
        </div>
        <div className="SwapComponent-swap-modal-txdetails">
          <div className="SwapComponent-swap-modal-txdetail">
            <span>
              <img className="App-logo-modal" src="/logo.png" alt="AlgoSwap" />
              {fromAmount}
            </span>
            <span>{fromToken}</span>
          </div>
          <p className="SwapComponent-arrow">↓</p>
          <div className="SwapComponent-swap-modal-txdetail">
            <span>
              <img className="App-logo-modal" src="/logo.png" alt="AlgoSwap" />
              {toAmount}
            </span>
            <span>{toToken}</span>
          </div>
          <div className="SwapComponent-swap-modal-subtitle">
            Output is estimated. You will receive at least {toAmount} {toToken} or the transaction
            will revert.
          </div>
          <div className="SwapComponent-swap-modal-txinfo">
            <span>Price:</span>
            <span>
              {parseFloat(toAmount) / parseFloat(fromAmount)} {toToken}/{fromToken}
            </span>
          </div>
        </div>
        <div className="SwapComponent-swap-modal-bottom">
          <button className="SwapComponent-swap-modal-button" onClick={toggleSwapModal}>
            Swap tokens
          </button>
        </div>
      </div>
    </Rodal>
  );
};

export default SwapModal;
