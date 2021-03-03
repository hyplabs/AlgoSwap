import ActionType from './types';

export type CurrentAccountAddress = {type: ActionType.SetAccountAddress; accountAddress: string};

export type CurrentTokenList = {type: ActionType.SetTokenList; tokenList: Array<Array<string>>};
export type CurrentFromToken = {type: ActionType.SetFromToken; fromToken: string};
export type CurrentToToken = {type: ActionType.SetToToken; toToken: string};
export type CurrentFirstToken = {type: ActionType.SetFirstToken; firstToken: string};
export type CurrentSecondToken = {type: ActionType.SetSecondToken; secondToken: string};

export function setAccountAddress(accountAddress: string): CurrentAccountAddress {
  return {
    accountAddress,
    type: ActionType.SetAccountAddress,
  };
}

export function setTokenList(tokenList: Array<Array<string>>): CurrentTokenList {
  return {
    tokenList,
    type: ActionType.SetTokenList,
  };
}

export function setFromToken(fromToken: string): CurrentFromToken {
  return {
    fromToken,
    type: ActionType.SetFromToken,
  };
}

export function setToToken(toToken: string): CurrentToToken {
  return {
    toToken,
    type: ActionType.SetToToken,
  };
}

export function setFirstToken(firstToken: string): CurrentFirstToken {
  return {
    firstToken,
    type: ActionType.SetFirstToken,
  };
}

export function setSecondToken(secondToken: string): CurrentSecondToken {
  return {
    secondToken,
    type: ActionType.SetSecondToken,
  };
}
