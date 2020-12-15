import React from 'react';

import ActionType from './types';

export type CurrentUserAction = {type: ActionType.SetAccountAddress; accountAddress: string};

export function SetAccountAddress(accountAddress: string): CurrentUserAction {
  return {
    accountAddress,
    type: ActionType.SetAccountAddress,
  };
}
