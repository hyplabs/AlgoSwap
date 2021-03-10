/*
  Need to disable typescript check to outsmart Rodal package issue.
  If you are making any changes to the code, remove this line temporarily
  as we want to pass typecheck testing as much as possible.
*/
// @ts-nocheck
import React from 'react';
import {useSelector} from 'react-redux';

import {selectSlippageTolerance} from '../../redux/reducers/transaction';

/* eslint-disable */
import Rodal from 'rodal';
import 'rodal/lib/rodal.css';

import './CreatePairModal.scss';

interface Props {
  firstAmount: string;
  firstToken: string;
  secondAmount: string;
  secondToken: string;

  openSupplyModal: boolean;
  toggleSupplyModal: () => void;
}

const CreatePairModal: React.FC<Props> = ({
  firstAmount,
  firstToken,
  secondAmount,
  secondToken,
  openSupplyModal,
  toggleSupplyModal,
}) => {
  const slippageTolerance = useSelector(selectSlippageTolerance);

  const modalStyle = {
    position: 'relative',
    borderRadius: '30px',
    top: '210px',
  };

  return (
    <Rodal
      width={420}
      customStyles={modalStyle}
      visible={openSupplyModal}
      onClose={toggleSupplyModal}
      height={430}
      showCloseButton={true}
    >
      <div className="CreatePair-modal">
        <div className="CreatePair-modal-header">
          <div className="CreatePair-modal-header-image">
            <img className="App-logo-modal" src="/logo.png" alt="AlgoSwap" />
          </div>
          Confirm Supply
        </div>
        <div className="CreatePair-modal-supply-summary">
          <span className="CreatePair-modal-supply-summary-info">Supply Summary</span>
          <span>{parseFloat(firstAmount) / parseFloat(secondAmount)}</span>
          <span className="CreatePair-modal-supply-summary-info">
            {firstToken}/{secondToken} Pool Tokens
          </span>
        </div>
        <div className="CreatePair-modal-subtitle">
          Output is estimated. If the price changes by more than {slippageTolerance}%, your
          transaction will revert.
        </div>
        <div className="CreatePair-modal-supply-details">
          <div className="CreatePair-modal-supply-details-info">
            <span>{firstToken} Deposited</span>
            <span>{firstAmount}</span>
          </div>
          <div className="CreatePair-modal-supply-details-info">
            <span>{secondToken} Deposited</span>
            <span>{secondAmount}</span>
          </div>
        </div>
        <div className="CreatePair-modal-bottom">
          <button className="CreatePair-modal-button" onClick={toggleSupplyModal}>
            Supply Liquidity
          </button>
        </div>
      </div>
    </Rodal>
  );
};

export default CreatePairModal;
