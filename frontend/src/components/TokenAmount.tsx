import React, {useEffect, useState} from 'react';

/* eslint-dsiable */
// @ts-ignore
import Rodal from 'rodal';
import 'rodal/lib/rodal.css';

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
  const [openModal, setOpenModal] = useState<boolean>(false);

  useEffect(() => {
    setSelectedToken(token);
  }, [token]);

  // console.log(title + ' ' + active + ' ' + openModal);
  const toggleModal = () => {
    setOpenModal(!openModal);
    updateToken(selectedToken);
  };

  const modalStyle = {
    position: 'relative',
    'border-radius': '30px',
    top: '210px',
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
        <button className="TokenAmount-token-select" onClick={toggleModal}>
          {token}
        </button>
      </div>
      <Rodal
        width={420}
        customStyles={modalStyle}
        visible={openModal}
        height={500}
        showCloseButton={false}
      >
        <div className="TokenAmount-token-modal">
          <div className="TokenAmount-token-modal-header">
            <div className="TokenAmount-token-modal-header-image">
              <img className="App-logo-modal" src="/logo.png" alt="AlgoSwap" />
            </div>
            Select a token
          </div>
          <div className="TokenAmount-token-modal-list">
            {tokenList &&
              tokenList.map(token => {
                if (token[0] === selectedToken) {
                  return (
                    <div
                      className={['TokenAmount-token', 'TokenAmount-token-active'].join(' ')}
                      key={token[1]}
                      onClick={() => setSelectedToken(token[0])}
                    >
                      {token[0]}
                    </div>
                  );
                }
                return (
                  <div
                    className="TokenAmount-token"
                    key={token[1]}
                    onClick={() => setSelectedToken(token[0])}
                  >
                    {token[0]}
                  </div>
                );
              })}
          </div>
          <div className="TokenAmount-token-modal-footer">
            <button className="TokenAmount-token-modal-button" onClick={toggleModal}>
              Close
            </button>
          </div>
        </div>
      </Rodal>
    </div>
  );
};

export default TokenAmount;
