/*
  Need to disable typescript check to outsmart Rodal package issue.
  If you are making any changes to the code, remove this line temporarily
  as we want to pass typecheck testing as much as possible.
*/
// @ts-nocheck
import React from 'react';
import {useSelector, useDispatch} from 'react-redux';

import {selectSlippageTolerance} from '../../redux/reducers/transaction';
import {setSlippageTolerance} from '../../redux/actions';

/* eslint-disable */
import Rodal from 'rodal';
import 'rodal/lib/rodal.css';

import './SettingsModal.scss';

interface Props {
  openSettingsModal: boolean;
  toggleSettingsModal: () => void;
}

const SettingsModal: React.FC<Props> = ({openSettingsModal, toggleSettingsModal}) => {
  const slippageTolerance = useSelector(selectSlippageTolerance);
  const dispatch = useDispatch();

  const modalStyle = {
    position: 'relative',
    borderRadius: '30px',
    top: '290px',
  };

  const updateSlippageTolerance = (value: string) => {
    const converted = parseFloat(value);
    !isNaN(converted)
      ? dispatch(setSlippageTolerance(converted))
      : dispatch(setSlippageTolerance(1));
  };

  return (
    <Rodal
      width={400}
      customStyles={modalStyle}
      visible={openSettingsModal}
      onClose={toggleSettingsModal}
      height={200}
      showCloseButton={true}
    >
      <div className="Settings-modal">
        <div className="Settings-modal-header">Transaction Settings</div>
        <div className="Settings-modal-slippage">
          <span>Slippage Tolerance</span>
          <div className="Settings-modal-slippage-content">
            <input
              className="Settings-modal-slippage-input"
              placeholder={slippageTolerance.toFixed(2)}
              type="number"
              onChange={evt => updateSlippageTolerance(evt.target.value)}
            />
            %
          </div>
        </div>
        <div className="Settings-modal-info">
          The transaction will revert if the price changes by more than this percentage.
        </div>
      </div>
    </Rodal>
  );
};

export default SettingsModal;
