import ActionType from '../actions/types';
import {CurrentUserAction} from '../actions/user';

export interface CurrentUser {
  readonly accountAddress: string | null;
}

export const defaultUser: CurrentUser = {
  accountAddress: null,
};

export default function user(state = defaultUser, action: CurrentUserAction) {
  switch (action.type) {
    case ActionType.SetAccountAddress:
      return {...state, accountAddress: action.accountAddress};
    default:
      return state;
  }
}
