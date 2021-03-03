import {combineReducers} from 'redux';

import user from './user';
import tokens from './tokens';

export default combineReducers({
  user,
  tokens,
});
