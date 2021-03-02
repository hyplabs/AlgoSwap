import React from 'react';
import {BrowserRouter as Router, Switch, Route, Redirect} from 'react-router-dom';
import AlgoSwapNavbar from './components/Navbar';
import {Provider} from 'react-redux';
import {createStore} from 'redux';

import rootReducer from './redux/reducers';
import SwapPage from './pages/SwapPage';
import PoolPage from './pages/PoolPage';
import AddPage from './pages/AddPage';

import './App.scss';
import CreatePage from './pages/CreatePage';

const store = createStore(rootReducer);

function App() {
  return (
    <Provider store={store}>
      <Router>
        <div className="App">
          <div style={{background: 'red', color: 'white', padding: '1em', fontSize: '1em'}}>
            WARNING: THIS CODE HAS NOT BEEN AUDITED AND SHOULD NOT BE USED ON THE ALGORAND MAINNET -
            USE AT YOUR OWN RISK!
          </div>
          <AlgoSwapNavbar />
          <div className="App-container">
            <Switch>
              <Route exact path="/">
                <Redirect to="/swap" />
              </Route>
              <Route path="/swap">
                <SwapPage />
              </Route>
              <Route path="/pool">
                <PoolPage />
              </Route>
              <Route path="/add/:first?/:second?" children={<AddPage />} />
              <Route path="/create/:first?/:second?" children={<CreatePage />} />
            </Switch>
          </div>
        </div>
      </Router>
    </Provider>
  );
}

export default App;
