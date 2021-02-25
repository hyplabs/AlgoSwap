import React from 'react';
import {Link, useLocation} from 'react-router-dom';

import './Navbar.scss';

interface Props {}

export const AlgoSwapNavbar: React.FC<Props> = () => {
  const {pathname} = useLocation();

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
    </nav>
  );
};
