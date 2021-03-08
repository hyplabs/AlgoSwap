import React from 'react';
import {Link} from 'react-router-dom';

import './LiquidityList.css';

export default class LiquidityList extends React.PureComponent<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      liquidities: [],
    };
  }

  renderLiquidities = () => {
    return this.state.liquidities.map(liquidity => (
      <div className="LiquidityList-liquidity">{liquidity}</div>
    ));
  };

  render() {
    return (
      <div className="LiquidityList">
        <div className="LiquidityList-header">
          <p className="LiquidityList-title">Your liquidity</p>
          <div className="LiquidityList-buttons">
            <Link to="/create">
              <button type="button" className="LiquidityList-create-pair">
                Create a pair
              </button>
            </Link>
            <Link to="/add">
              <button type="button" className="LiquidityList-add-liquidity">
                Add liquidity
              </button>
            </Link>
          </div>
        </div>
        <div className="LiquidityList-content">
          {this.state.liquidities.length > 0 ? (
            this.renderLiquidities()
          ) : (
            <p className="LiquidityList-nullstate">No liquidity found.</p>
          )}
        </div>
      </div>
    );
  }
}

interface Props {}
interface State {
  liquidities: string[];
}
