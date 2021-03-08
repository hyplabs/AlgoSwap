import React from 'react';
import {useSelector} from 'react-redux';

import {selectUserAccountAddress} from '../redux/reducers/user';
import {Link, useLocation} from 'react-router-dom';

import './NavigationBar.scss';

const NavigationBar: React.FC = () => {
  const {pathname} = useLocation();
  const accountAddr = useSelector(selectUserAccountAddress);

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
            pathname === '/pool' || pathname === '/create'
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
        <p>{accountAddr}</p>
      </div>
    </nav>
  );
};

export default NavigationBar;
