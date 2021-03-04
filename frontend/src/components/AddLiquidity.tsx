import React, {useEffect, useState} from 'react';
import {useSelector, useDispatch} from 'react-redux';

import {selectUserAccountAddress} from '../redux/reducers/user';
import {selectTokenList} from '../redux/reducers/tokens';
import {setAccountAddress, setTokenList, setFirstToken, setSecondToken} from '../redux/actions';

import TokenAmount from './TokenAmount';

/* eslint-dsiable */
// @ts-ignore
import Rodal from 'rodal';
import 'rodal/lib/rodal.css';

import './AddLiquidity.scss';

interface Props {
  firstToken: string;
  secondToken: string;
  updateTokens: (first: string, second: string) => void;
}

const AddLiquidity: React.FC<Props> = ({firstToken, secondToken, updateTokens}) => {
  // Local state
  const [firstAmount, setFirstAmount] = useState<string>('');
  const [secondAmount, setSecondAmount] = useState<string>('');

  const [firstTabSelected, setFirstTabSelected] = useState<boolean>(false);
  const [secondTabSelected, setSecondTabSelected] = useState<boolean>(false);
  const [openModal, setOpenModal] = useState<boolean>(false);

  // Redux state
  const walletAddr = useSelector(selectUserAccountAddress);
  const tokenList = useSelector(selectTokenList);

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

  function setActiveTab(type: string) {
    if (firstTabSelected === false && secondTabSelected === false) {
      if (type === 'First') {
        setFirstTabSelected(true);
      }
      if (type === 'Second') {
        setSecondTabSelected(true);
      }
    } else if (firstTabSelected === true) {
      if (type === 'Second') {
        setFirstTabSelected(false);
        setSecondTabSelected(true);
      }
    } else {
      if (type === 'First') {
        setFirstTabSelected(true);
        setSecondTabSelected(false);
      }
    }
  }

  const modalStyle = {
    position: 'relative',
    'border-radius': '30px',
    top: '210px',
  };

  return (
    <div className="AddLiquidity">
      <div className="AddLiquidity-header">Add Liquidity</div>
      <div className="AddLiquidity-content">
        <TokenAmount
          title="Amount"
          amount={firstAmount}
          updateAmount={amount => setFirstAmount(amount)}
          tokenList={tokenList}
          token={firstToken}
          updateToken={token => {
            dispatch(setFirstToken(token));
            updateTokens(token, secondToken);
          }}
          active={firstTabSelected}
          onClick={() => setActiveTab('First')}
        />
        <p className="AddLiquidity-plus">+</p>
        <TokenAmount
          title="Amount"
          amount={secondAmount}
          updateAmount={amount => setSecondAmount(amount)}
          tokenList={tokenList}
          token={secondToken}
          updateToken={token => {
            if (firstToken === '') {
              dispatch(setFirstToken(tokenList[0][0]));
              dispatch(setSecondToken(token));
              updateTokens(tokenList[0][0], token);
            } else {
              dispatch(setSecondToken(token));
              updateTokens(firstToken, token);
            }
          }}
          active={secondTabSelected}
          onClick={() => setActiveTab('Second')}
        />
      </div>
      <div className="AddLiquidity-bottom">
        {walletAddr ? (
          <button className="AddLiquidity-button">Add Liquidity</button>
        ) : (
          <button className="AddLiquidity-button" onClick={toggleModal}>
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
        <div className="AddLiquidity-wallet-modal">
          <div className="AddLiquidity-wallet-modal-header">
            <div className="AddLiquidity-wallet-modal-header-image">
              <img className="App-logo-modal" src="/logo.png" alt="AlgoSwap" />
            </div>
            Connect to a wallet
          </div>
          <button className="AddLiquidity-wallet-modal-select">
            <div className="AddLiquidity-wallet-modal-item">
              AlgoSigner
              <img className="Wallet-logo-modal" src="/algosigner.png" alt="AlgoSigner" />
            </div>
          </button>
        </div>
      </Rodal>
    </div>
  );
};

export default AddLiquidity;
