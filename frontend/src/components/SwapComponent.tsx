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

export const SwapComponent: React.FC = () => {
  // Local state
  const [fromAmount, setFromAmount] = useState<string>('');
  const [toAmount, setToAmount] = useState<string>('');

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

  const toggleModal = () => {
    setOpenModal(!openModal);
  };

  const toggleSwapModal = () => {
    setOpenSwapModal(!openSwapModal);
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

  function setActiveTab(type: string) {
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
  }

  const modalStyle = {
    position: 'relative',
    'border-radius': '30px',
    top: '210px',
  };

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
          <button className="SwapComponent-button" onClick={toggleSwapModal}>
            Swap
          </button>
        ) : (
          <button className="SwapComponent-button" onClick={toggleModal}>
            Connect to a wallet
          </button>
        )}
      </div>
      <Rodal
        width={420}
        customStyles={modalStyle}
        visible={openModal}
        onClose={toggleModal}
        height={200}
        showCloseButton={true}
      >
        <div className="SwapComponent-wallet-modal">
          <div className="SwapComponent-wallet-modal-header">
            <div className="SwapComponent-wallet-modal-header-image">
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
        customStyles={modalStyle}
        visible={openSwapModal}
        onClose={toggleSwapModal}
        showCloseButton={true}
      >
        <div className="SwapComponent-swap-modal">
          <div className="SwapComponent-swap-modal-header">Confirm Swap</div>
          <div className="SwapComponent-swap-modal-txdetails">
            <div className="SwapComponent-swap-modal-txdetail_1">
              <span>
                <img className="App-logo-modal" src="/logo.png" alt="AlgoSwap" />1
              </span>
              <span>ETH</span>
            </div>
            <p className="SwapComponent-arrow">↓</p>
            <div className="SwapComponent-swap-modal-txdetail_2">
              <span>
                <img className="App-logo-modal" src="/logo.png" alt="AlgoSwap" />1
              </span>
              <span>ALGO</span>
            </div>
            <div className="SwapComponent-swap-modal-subtitle">
              Output is estimated. You will receive at least <strong>0.5 ALGO</strong> or the
              transaction will revert.
            </div>
          </div>
          <div className="SwapComponent-swap-modal-txinfo">
            <div className="SwapComponent-swap-modal-txinfo-item">
              <span>Price: </span>
              <span>1 ALGO/ETH</span>
            </div>
          </div>
        </div>
      </Rodal>
    </div>
  );
};
