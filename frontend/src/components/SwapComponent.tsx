// @ts-nocheck
import React, {useEffect, useState} from 'react';
import TokenAmount from './TokenAmount';
import {connect} from 'react-redux';
import {SetAccountAddress} from '../redux/actions/user';

/* eslint-disable */
import Rodal from 'rodal';
import 'rodal/lib/rodal.css';

import './SwapComponent.scss';

interface Props {}

const SwapComponent: React.FC<Props> = (props: any) => {
  const [walletAddr, setWalletAddr] = useState<string>('');

  // To-Dos: Fetch the tokens from the backend
  const [tokenList, setTokenList] = useState<Array<Array<string>>>([]);
  const [fromAmount, setFromAmount] = useState<string>('');
  const [fromToken, setFromToken] = useState<string>('');
  const [toAmount, setToAmount] = useState<string>('');
  const [toToken, setToToken] = useState<string>('');

  const [fromTabSelected, setFromTabSelected] = useState<boolean>(false);
  const [toTabSelected, setToTabSelected] = useState<boolean>(false);

  const [openModal, setOpenModal] = useState<boolean>(false);
  const [openSwapModal, setOpenSwapModal] = useState<boolean>(false);

  useEffect(() => {
    setTokenList([
      ['ETH', '0'],
      ['BTC', '1'],
      ['ALGO', '2'],
      ['USDC', '3'],
    ]);

    setWalletAddr(props.user.accountAddress);
    setFromAmount('');
    setFromToken('ETH');
    setToAmount('');
    setToToken('USD');

    setFromTabSelected(false);
    setToTabSelected(false);
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

        setWalletAddr(testnetAccounts[0].address);
        props.SetAccountAddress(testnetAccounts[0].address);
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

  return (
    <div className="SwapComponent">
      <div className="SwapComponent-header">Swap</div>
      <div className="SwapComponent-content">
        <TokenAmount
          title="From"
          amount={fromAmount}
          updateAmount={amount => setFromAmount(amount)}
          tokenList={tokenList}
          token={fromToken}
          updateToken={token => setFromToken(token)}
          active={fromTabSelected}
          onClick={() => setActiveTab('From')}
        />
        <p className="SwapComponent-arrow">↓</p>
        <TokenAmount
          title="To"
          amount={toAmount}
          updateAmount={amount => setToAmount(amount)}
          tokenList={tokenList}
          token={toToken}
          updateToken={token => setToToken(token)}
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

const mapStateToProps = (state: any) => {
  return {
    user: state.user,
  };
};

const mapDispatchToProps = {SetAccountAddress};

export default connect(mapStateToProps, mapDispatchToProps)(SwapComponent);
