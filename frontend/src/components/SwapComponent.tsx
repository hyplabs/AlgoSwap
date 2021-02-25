import React, {useEffect, useState} from 'react';
import TokenAmount from './TokenAmount';

/* eslint-dsiable */
// @ts-ignore
import Rodal from 'rodal';
import 'rodal/lib/rodal.css';

import './SwapComponent.scss';

interface Props {}

export const SwapComponent: React.FC<Props> = () => {
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

  useEffect(() => {
    setTokenList([
      ['ETH', '0'],
      ['BTC', '1'],
      ['ALG', '2'],
      ['USD', '3'],
    ]);

    setWalletAddr('');
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

  const modalStyle = {
    position: 'relative',
    'border-radius': '30px',
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
          <button className="SwapComponent-button">Swap</button>
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
          <button className="SwapComponent-wallet-modal-select">
            <div className="SwapComponent-wallet-modal-item">
              AlgoSigner
              <img className="Wallet-logo-modal" src="/algosigner.png" alt="AlgoSigner" />
            </div>
          </button>
        </div>
      </Rodal>
    </div>
  );
};
