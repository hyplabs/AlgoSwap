import React, {useEffect, useState} from 'react';
import TokenModal from './TokenModal';

import './TokenAmount.scss';

interface Props {
  title: string;
  amount: string;
  tokenList?: Array<Array<string>>;
  token: string;
  updateAmount: (amount: string) => void;
  updateToken: (token: string) => void;
  active: boolean;
  onClick: () => void;
}

const TokenAmount: React.FC<Props> = ({
  title,
  amount,
  updateAmount,
  tokenList,
  token,
  updateToken,
  active,
  onClick,
}) => {
  const [selectedToken, setSelectedToken] = useState<string>(token);
  const [openTokenModal, setOpenTokenModal] = useState<boolean>(false);

  useEffect(() => {
    setSelectedToken(token);
  }, [token]);

  const toggleTokenModal = () => {
    setOpenTokenModal(!openTokenModal);
    token !== selectedToken && updateToken(selectedToken);
  };

  return (
    <div
      className={active ? ['TokenAmount-active', 'TokenAmount'].join(' ') : 'TokenAmount'}
      onClick={onClick}
    >
      <p className="TokenAmount-title">{title}</p>
      <div className="TokenAmount-content">
        <input
          className="TokenAmount-amount"
          placeholder="0.0"
          type="number"
          onChange={evt => updateAmount(evt.target.value)}
          value={amount}
        />
        <button className="TokenAmount-token-select" onClick={toggleTokenModal}>
          {token === '' ? 'Select' : token}
        </button>
      </div>
      <TokenModal
        selectedToken={selectedToken}
        tokenList={tokenList}
        updateSelectedToken={token => setSelectedToken(token)}
        openTokenModal={openTokenModal}
        toggleTokenModal={toggleTokenModal}
      />
    </div>
  );
};

export default TokenAmount;
