import React from 'react';

import TokenAmount from './TokenAmount';
import './AddLiquidity.css';

export default class AddLiquidity extends React.PureComponent<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      firstAmount: '',
      secondAmount: '',
    };
  }

  add = () => {
    // TODO
    console.log(this.state.firstAmount + ' ' + this.props.firstToken);
    console.log(this.state.secondAmount + ' ' + this.props.secondToken);
  };

  render() {
    return (
      <div className="AddLiquidity">
        <TokenAmount
          title="From"
          amount={this.state.firstAmount}
          updateAmount={amount => this.setState({firstAmount: amount})}
          token={this.props.firstToken}
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
        <button className="AddLiquidity-add" onClick={this.add}>
          Add Liquidity
        </button>
      </div>
    );
  }
}

interface Props {
  firstToken: string;
  secondToken: string;
  updateTokens: (first: string, second: string) => void;
}
interface State {
  firstAmount: string;
  secondAmount: string;
}
