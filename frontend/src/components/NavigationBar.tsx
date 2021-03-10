import React from 'react';
import {useDispatch, useSelector} from 'react-redux';

import {selectUserAccountAddress} from '../redux/reducers/user';
import {setAccountAddress} from '../redux/actions';
import {Link, useLocation} from 'react-router-dom';

import {connectToAlgoSigner} from '../utils/connectToAlgoSigner';
import './NavigationBar.scss';

const NavigationBar: React.FC = () => {
  const {pathname} = useLocation();
  const accountAddr = useSelector(selectUserAccountAddress);
  const dispatch = useDispatch();

  async function connectToAlgoSignerWallet() {
    const fetchedAddress = await connectToAlgoSigner();
    dispatch(setAccountAddress(fetchedAddress));
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
          <span>{accountAddr}</span>
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
