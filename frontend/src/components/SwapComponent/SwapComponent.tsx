import React, {useEffect, useState} from 'react';
import {useSelector, useDispatch} from 'react-redux';

import {selectUserAccountAddress} from '../../redux/reducers/user';
import {selectSlippageTolerance} from '../../redux/reducers/transaction';
import {selectFromToken, selectToToken, selectTokenList} from '../../redux/reducers/tokens';
import {setTokenList, setFromToken, setToToken} from '../../redux/actions';

import TokenAmount from '../TokenAmount/TokenAmount';
import SwapModal from './SwapModal';
import SettingsModal from '../common/SettingsModal';
import WalletModal from '../common/WalletModal';

import './SwapComponent.scss';

const SwapComponent: React.FC = () => {
  // Local state
  const [fromAmount, setFromAmount] = useState<string>('');
  const [toAmount, setToAmount] = useState<string>('');

  const [fromTabSelected, setFromTabSelected] = useState<boolean>(false);
  const [toTabSelected, setToTabSelected] = useState<boolean>(false);

  // Modals
  const [openWalletModal, setOpenWalletModal] = useState<boolean>(false);
  const [openSettingsModal, setOpenSettingsModal] = useState<boolean>(false);
  const [openSwapModal, setOpenSwapModal] = useState<boolean>(false);

  // Redux state
  const walletAddr = useSelector(selectUserAccountAddress);
  const slippageTolerance = useSelector(selectSlippageTolerance);
  const tokenList = useSelector(selectTokenList);
  const fromToken = useSelector(selectFromToken);
  const toToken = useSelector(selectToToken);

  const dispatch = useDispatch();

  const onFirstRender = () => {
    dispatch(
      setTokenList([
        ['ETH', '0'],
        ['BTC', '1'],
        ['ALG', '2'],
        ['USD', '3'],
      ])
    );
  };

  useEffect(() => {
    onFirstRender();
  }, []);

  const toggleWalletModal = () => {
    setOpenWalletModal(!openWalletModal);
  };

  const toggleSettingsModal = () => {
    setOpenSettingsModal(!openSettingsModal);
  };

  const toggleSwapModal = () => {
    setOpenSwapModal(!openSwapModal);
  };

  const bothTokensNotSet = () => {
    if (fromToken === undefined || toToken === undefined) {
      return true;
    }
    /*
    TODO:
    If one of the input panels are given the value, the other
    one should be automatically calculated using the conversion rate.

    For now, the swap button is clickable only when both inputs
    are filled manually
    */
    if (fromAmount === '' || toAmount === '') {
      return true;
    }
    return false;
  };

  const setActiveTab = (type: string) => {
    if (fromTabSelected === false && toTabSelected === false) {
      if (type === 'From') {
        setFromTabSelected(true);
      }
      if (type === 'To') {
        setToTabSelected(true);
      }
    } else if (fromTabSelected === true) {
      if (type === 'To') {
        setFromTabSelected(false);
        setToTabSelected(true);
      }
    } else {
      if (type === 'From') {
        setFromTabSelected(true);
        setToTabSelected(false);
      }
    }
  };

  return (
    <div className="SwapComponent">
      <div className="SwapComponent-header">
        <span>Swap</span>
        <span>
          <button className="Settings-button" onClick={toggleSettingsModal}>
            <img className="Settings-logo" src="/settings.png" alt="Settings" />
          </button>
        </span>
      </div>
      <div className="SwapComponent-content">
        <TokenAmount
          title="From"
          amount={fromAmount}
          updateAmount={amount => setFromAmount(amount)}
          tokenList={tokenList}
          token={fromToken || ''}
          updateToken={token => dispatch(setFromToken(token))}
          active={fromTabSelected}
          onClick={() => setActiveTab('From')}
        />
        <p className="SwapComponent-arrow">↓</p>
        <TokenAmount
          title="To"
          amount={toAmount}
          updateAmount={amount => setToAmount(amount)}
          tokenList={tokenList}
          token={toToken || ''}
          updateToken={token => dispatch(setToToken(token))}
          active={toTabSelected}
          onClick={() => setActiveTab('To')}
        />
      </div>
      <div className="SwapComponent-info">
        <span>Slippage Tolerance:</span>
        <span>{slippageTolerance.toFixed(2)}%</span>
      </div>
      <div className="SwapComponent-bottom">
        {walletAddr ? (
          <button
            className={
              bothTokensNotSet()
                ? ['SwapComponent-button-disabled', 'SwapComponent-button'].join(' ')
                : 'SwapComponent-button'
            }
            onClick={toggleSwapModal}
            disabled={bothTokensNotSet()}
          >
            Swap
          </button>
        ) : (
          <button className="SwapComponent-button" onClick={toggleWalletModal}>
            Connect to a wallet
          </button>
        )}
      </div>
      <WalletModal openWalletModal={openWalletModal} toggleWalletModal={toggleWalletModal} />
      <SettingsModal
        openSettingsModal={openSettingsModal}
        toggleSettingsModal={toggleSettingsModal}
      />
      {fromToken && toToken && (
        <SwapModal
          fromAmount={fromAmount}
          toAmount={toAmount}
          fromToken={fromToken}
          toToken={toToken}
          openSwapModal={openSwapModal}
          toggleSwapModal={toggleSwapModal}
        />
      )}
    </div>
  );
};

export default SwapComponent;
