// @ts-nocheck
import React, {useEffect, useState} from 'react';
import {useSelector, useDispatch} from 'react-redux';

import {selectUserAccountAddress} from '../redux/reducers/user';
import {selectFromToken, selectToToken, selectTokenList} from '../redux/reducers/tokens';
import {setAccountAddress, setTokenList, setFromToken, setToToken} from '../redux/actions';

import TokenAmount from './TokenAmount';

/* eslint-disable */
import Rodal from 'rodal';
import 'rodal/lib/rodal.css';

import './SwapComponent.scss';

const SwapComponent: React.FC = () => {
  // Local state
  const [fromAmount, setFromAmount] = useState<float>('');
  const [toAmount, setToAmount] = useState<float>('');

  const [fromTabSelected, setFromTabSelected] = useState<boolean>(false);
  const [toTabSelected, setToTabSelected] = useState<boolean>(false);
  const [openModal, setOpenModal] = useState<boolean>(false);
  const [openSwapModal, setOpenSwapModal] = useState<boolean>(false);

  // Redux state
  const walletAddr = useSelector(selectUserAccountAddress);
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
    dispatch(setAccountAddress(''));
  };

  useEffect(() => {
    onFirstRender();
  }, []);

  const toggleWalletModal = () => {
    setOpenModal(!openModal);
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

  async function connectToAlgoSigner() {
    if (typeof AlgoSigner !== 'undefined') {
      try {
        await AlgoSigner.connect();
        let testnetAccounts = await AlgoSigner.accounts({
          ledger: 'TestNet',
        });

        dispatch(setAccountAddress(testnetAccounts[0].address));
        setOpenModal(!openModal);
      } catch (e) {
        console.error(e);
      }
    }
  }

  const modalStyle = {
    position: 'relative',
    borderRadius: '30px',
    top: '210px',
  };

  function swap() {
    // TODO
    console.log(fromAmount + ' ' + fromToken);
    console.log(toAmount + ' ' + toToken);
  }

  return (
    <div className="SwapComponent">
      <div className="SwapComponent-header">Swap</div>
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
      <Rodal
        width={420}
        customStyles={modalStyle}
        visible={openModal}
        onClose={toggleWalletModal}
        height={200}
        showCloseButton={true}
      >
        <div className="SwapComponent-modal">
          <div className="SwapComponent-modal-header">
            <div className="SwapComponent-modal-header-image">
              <img className="App-logo-modal" src="/logo.png" alt="AlgoSwap" />
            </div>
            Connect to a wallet
          </div>
          <button className="SwapComponent-wallet-modal-select" onClick={connectToAlgoSigner}>
            <div className="SwapComponent-wallet-modal-item">
              AlgoSigner
              <img className="Wallet-logo-modal" src="/algosigner.png" alt="AlgoSigner" />
            </div>
          </button>
        </div>
      </Rodal>

      <Rodal
        width={420}
        customStyles={modalStyle}
        visible={openSwapModal}
        onClose={toggleSwapModal}
        height={400}
        showCloseButton={true}
      >
        <div className="SwapComponent-modal">
          <div className="SwapComponent-modal-header">
            <div className="SwapComponent-modal-header-image">
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
          <div className="SwapComponent-modal-bottom">
            <button className="SwapComponent-modal-button" onClick={toggleSwapModal}>
              Swap tokens
            </button>
          </div>
        </div>
      </Rodal>
    </div>
  );
};

export default SwapComponent;
