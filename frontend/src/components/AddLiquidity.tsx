import React, {useEffect, useState} from 'react';
import {useSelector, useDispatch} from 'react-redux';

import {selectUserAccountAddress} from '../redux/reducers/user';
import {selectFromToken, selectToToken, selectTokenList} from '../redux/reducers/tokens';
import {setAccountAddress, setTokenList, setFirstToken, setSecondToken} from '../redux/actions';

import TokenAmount from './TokenAmount';
import './AddLiquidity.scss';

export const AddLiquidity: React.FC = () => {
  // Local state
  const [firstAmount, setFirstAmount] = useState<string>('');
  const [secondAmount, setSecondAmount] = useState<string>('');

  const [firstTabSelected, setFirstTabSelected] = useState<boolean>(false);
  const [secondTabSelected, setSecondTabSelected] = useState<boolean>(false);
  const [openModal, setOpenModal] = useState<boolean>(false);

  // Redux state
  const walletAddr = useSelector(selectUserAccountAddress);
  const tokenList = useSelector(selectTokenList);
  const firstToken = useSelector(selectFromToken);
  const secondToken = useSelector(selectToToken);

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

    setFirstTabSelected(false);
    setSecondTabSelected(false);
  });

  const toggleModal = () => {
    setOpenModal(!openModal);
  };

  return (
    <div className="AddLiquidity">
      <div className="AddLiquidity-header">Add Liquidity</div>
      <div className="AddLiquidity-content">
        <TokenAmount
          title="From"
          amount={firstAmount}
          updateAmount={amount => dispatch(setFirstAmount(amount))}
          tokenList={tokenList}
          token={fromToken}
          updateToken={token => this.props.updateTokens(token, this.props.secondToken)}
          active={false}
          onClick={() => console.log('clicked')}
        />
        <p className="AddLiquidity-plus">+</p>
        <TokenAmount
          title="To"
          amount={this.state.secondAmount}
          updateAmount={amount => this.setState({secondAmount: amount})}
          token={this.props.secondToken}
          updateToken={token => this.props.updateTokens(this.props.firstToken, token)}
          active={false}
          onClick={() => console.log('clicked')}
        />
      </div>
      <button className="AddLiquidity-add" onClick={this.add}>
        Add Liquidity
      </button>
    </div>
  );
};
