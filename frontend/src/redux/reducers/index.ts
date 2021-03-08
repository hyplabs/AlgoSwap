import {combineReducers} from 'redux';

import user from './user';
import transaction from './transaction';
import tokens from './tokens';

export default combineReducers({
  user,
  transaction,
  tokens,
});
