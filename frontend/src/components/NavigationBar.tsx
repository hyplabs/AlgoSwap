import React from 'react';
import {useDispatch, useSelector} from 'react-redux';

import {selectUserAccountAddress, selectUserAccountNet} from '../redux/reducers/user';
import {setAccountAddress, setAccountNet} from '../redux/actions';
import {Link, useLocation} from 'react-router-dom';

import {LEDGER_NAME} from '../services/constants';

import {connectToAlgoSigner} from '../utils/connectToAlgoSigner';
import './NavigationBar.scss';

const NavigationBar: React.FC = () => {
  const {pathname} = useLocation();
  const accountAddr = useSelector(selectUserAccountAddress);
  const accountNet = useSelector(selectUserAccountNet);
  const dispatch = useDispatch();

  async function connectToAlgoSignerWallet() {
    const fetchedAddress = await connectToAlgoSigner();
    dispatch(setAccountAddress(fetchedAddress));
    dispatch(setAccountNet(LEDGER_NAME));
  }

  return (
    <nav className="Navbar">
      <div className="Navbar-left">
        <Link to="/">
          <img className="App-logo-nav" src="/logo.png" alt="AlgoSwap" />
        </Link>
        <div className={pathname === '/swap' ? 'Navbar-container-active' : 'Navbar-container'}>
          <Link to="/swap">
            <p>Swap</p>
          </Link>
        </div>
        <div
          className={
            pathname === '/pool' || pathname === '/create' || pathname === '/add'
              ? 'Navbar-container-active'
              : 'Navbar-container'
          }
        >
          <Link to="/pool">
            <p>Pool</p>
          </Link>
        </div>
      </div>
      <div className="Navbar-right">
        {accountAddr ? (
          <div className="Navbar-user-context">
            <div className="Navbar-account-net">{accountNet}</div>
            <div className="Navbar-account-addr">
              <img className="AlgoSigner-logo-nav" src="/algosigner.png" alt="AlgoSigner" />
              {accountAddr.slice(0, 10)}...{accountAddr.slice(-5)}
            </div>
          </div>
        ) : (
          <button className="Navbar-connect-button" onClick={connectToAlgoSignerWallet}>
            Connect to a wallet
          </button>
        )}
      </div>
    </nav>
  );
};

export default NavigationBar;
