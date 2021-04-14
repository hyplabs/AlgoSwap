import React, {useEffect, useState} from 'react';
import {useSelector, useDispatch} from 'react-redux';
import {useHistory} from 'react-router-dom';

import {selectUserAccountAddress} from '../../redux/reducers/user';
import {selectTokenList} from '../../redux/reducers/tokens';
import {setTokenList, setFirstToken, setSecondToken} from '../../redux/actions';

import TokenAmount from '../TokenAmount/TokenAmount';

import SettingsModal from '../common/SettingsModal';
import WalletModal from '../common/WalletModal';

import './AddLiquidity.scss';

interface Props {
  firstToken: string;
  secondToken: string;
  updateTokens: (first: string, second: string) => void;
}

const AddLiquidity: React.FC<Props> = ({firstToken, secondToken, updateTokens}) => {
  const history = useHistory();
  // Local state
  const [firstAmount, setFirstAmount] = useState<string>('');
  const [secondAmount, setSecondAmount] = useState<string>('');

  const [firstTabSelected, setFirstTabSelected] = useState<boolean>(false);
  const [secondTabSelected, setSecondTabSelected] = useState<boolean>(false);

  // Modals
  const [openWalletModal, setOpenWalletModal] = useState<boolean>(false);
  const [openSettingsModal, setOpenSettingsModal] = useState<boolean>(false);

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
  };

  const toggleWalletModal = () => {
    setOpenWalletModal(!openWalletModal);
  };

  const toggleSettingsModal = () => {
    setOpenSettingsModal(!openSettingsModal);
  };

  const bothTokensNotSet = () => {
    if (firstToken === '' || secondToken === '') {
      return true;
    }
    /*
    TODO:
    If one of the input panels are given the value, the other
    one should be automatically calculated using the conversion rate.

    For now, the swap button is clickable only when both inputs
    are filled manually
    */
    if (firstAmount === '' || secondAmount === '') {
      return true;
    }
    return false;
  };

  useEffect(() => {
    onFirstRender();
  }, []);

  const toggleModal = () => {
    setOpenWalletModal(!openWalletModal);
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

  return (
    <div className="AddLiquidity">
      <div className="AddLiquidity-header">
        <div className="AddLiquidity-header-title-section">
          <button className="AddLiquidity-header-button" onClick={() => history.goBack()}>
            <img className="Back-logo" src="/back.png" alt="Back" />
          </button>
          <span className="AddLiquidity-header-title">Add Liquidity</span>
        </div>
        <span>
          <button className="AddLiquidity-header-button" onClick={toggleSettingsModal}>
            <img className="Settings-logo" src="/settings.png" alt="Settings" />
          </button>
        </span>
      </div>
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
          <button
            className={
              bothTokensNotSet()
                ? ['AddLiquidity-button-disabled', 'AddLiquidity-button'].join(' ')
                : 'AddLiquidity-button'
            }
            disabled={bothTokensNotSet()}
          >
            Add Liquidity
          </button>
        ) : (
          <button className="AddLiquidity-button" onClick={toggleModal}>
            Connect to a wallet
          </button>
        )}
      </div>
      <WalletModal openWalletModal={openWalletModal} toggleWalletModal={toggleWalletModal} />
      <SettingsModal
        openSettingsModal={openSettingsModal}
        toggleSettingsModal={toggleSettingsModal}
      />
    </div>
  );
};

export default AddLiquidity;
