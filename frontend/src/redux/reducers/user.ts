import ActionType from '../actions/types';
import {CurrentAccountAddress} from '../actions';
import CurrentAlgoSwapContext, {CurrentUser} from './types';

const initUser: CurrentUser = {
  accountAddress: null,
};

export const selectUserAccountAddress = (state: CurrentAlgoSwapContext) => {
  return state.user.accountAddress;
};

export default function user(state = initUser, action: CurrentAccountAddress): CurrentUser {
  switch (action.type) {
    case ActionType.SetAccountAddress:
      return {...state, accountAddress: action.accountAddress};
    default:
      return state;
  }
}
