import React from 'react';

import TokenAmount from './TokenAmount';
import './SwapComponent.css';

export default class SwapComponent extends React.PureComponent<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      fromAmount: '',
      fromToken: 'ETH',
      toAmount: '',
      toToken: 'USD',
    };
  }

  swap = () => {
    // TODO
    console.log(this.state.fromAmount + ' ' + this.state.fromToken);
    console.log(this.state.toAmount + ' ' + this.state.toToken);
  };

  render() {
    return (
      <div className="SwapComponent">
        <TokenAmount
          title="From"
          amount={this.state.fromAmount}
          updateAmount={(amount) => this.setState({ fromAmount: amount})} 
          token={this.state.fromToken}
          updateToken={(token) => this.setState({ fromToken: token})} 
        />
        <p className="SwapComponent-arrow">↓</p>
        <TokenAmount
          title="To"
          amount={this.state.toAmount}
          updateAmount={(amount) => this.setState({ toAmount: amount})} 
          token={this.state.toToken}
          updateToken={(token) => this.setState({ toToken: token})} 
        />
        <button className="SwapComponent-swap" onClick={this.swap}>Swap</button>
      </div>
    );
  }
}

interface Props {}
interface State {
  fromAmount: string;
  fromToken: string;
  toAmount: string;
  toToken: string;
}
