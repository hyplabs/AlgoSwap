import React from 'react';

import TokenAmount from './TokenAmount';
import './CreatePair.css';

export default class CreatePair extends React.PureComponent<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      firstAmount: '',
      secondAmount: '',
    };
  }

  create = () => {
    // TODO
    console.log(this.state.firstAmount + ' ' + this.props.firstToken);
    console.log(this.state.secondAmount + ' ' + this.props.secondToken);
  };

  render() {
    return (
      <div className="CreatePair">
        <TokenAmount
          title="Token 1"
          amount={this.state.firstAmount}
          updateAmount={(amount) => this.setState({ firstAmount: amount})} 
          token={this.props.firstToken}
          updateToken={(token) => this.props.updateTokens(token, this.props.secondToken)} 
        />
        <p className="CreatePair-plus">+</p>
        <TokenAmount
          title="Token 2"
          amount={this.state.secondAmount}
          updateAmount={(amount) => this.setState({ secondAmount: amount})} 
          token={this.props.secondToken}
          updateToken={(token) => this.props.updateTokens(this.props.firstToken, token)} 
        />
        <button className="CreatePair-create" onClick={this.create}>Create Pair</button>
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
