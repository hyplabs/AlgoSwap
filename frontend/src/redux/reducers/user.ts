import ActionType from '../actions/types';
import {CurrentAccountAddress, CurrentAccountNet} from '../actions';
import CurrentAlgoSwapContext, {CurrentUser} from './types';

const initUser: CurrentUser = {
  accountAddress: null,
  accountNet: null,
};

type CurrentUserInfoAction = CurrentAccountAddress | CurrentAccountNet;

export const selectUserAccountAddress = (state: CurrentAlgoSwapContext) => {
  return state.user.accountAddress;
};

export const selectUserAccountNet = (state: CurrentAlgoSwapContext) => {
  return state.user.accountNet;
};

export default function user(state = initUser, action: CurrentUserInfoAction): CurrentUser {
  switch (action.type) {
    case ActionType.SetAccountAddress:
      return {...state, accountAddress: action.accountAddress};
    case ActionType.SetAccountNet:
      return {...state, accountNet: action.accountNet};
    default:
      return state;
  }
}
