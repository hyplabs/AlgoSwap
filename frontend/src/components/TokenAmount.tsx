import React from 'react';

import './TokenAmount.css';

const TokenAmount: React.FC<Props> = ({title, amount, updateAmount, token, updateToken}) => {
  return (
    <div className="TokenAmount">
      <p className="TokenAmount-title">{title}</p>
      <div className="TokenAmount-content">
        <input
          className="TokenAmount-amount"
          placeholder="0.0"
          type="text"
          onChange={(evt) => updateAmount(evt.target.value)}
          value={amount}
        />
        <select
          className="TokenAmount-token"
          onChange={(evt) => updateToken(evt.target.value)}
          value={token}
        >
          <option value="" selected>Select a token</option>
          <option value="ETH">ETH</option>
          <option value="BTC">BTC</option>
          <option value="ALG">ALG</option>
        </select>
      </div>
    </div>
  );
};

interface Props {
  title: string;
  amount: string;
  token: string;
  updateAmount: (amount: string) => void;
  updateToken: (token: string) => void;
}

export default TokenAmount;
