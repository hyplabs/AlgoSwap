import React from 'react';
import {connect} from 'react-redux';
import {Link, useLocation} from 'react-router-dom';

import './Navbar.scss';

interface Props {}

const AlgoSwapNavbar: React.FC<Props> = (props: any) => {
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
      <div className="Navbar-right">
        <p>{props.user.accountAddress}</p>
      </div>
    </nav>
  );
};

const mapStateToProps = (state: any) => {
  return {
    user: state.user,
  };
};

export default connect(mapStateToProps, undefined)(AlgoSwapNavbar);
