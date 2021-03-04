import ActionType from '../actions/types';
import {
  CurrentTokenList,
  CurrentFromToken,
  CurrentToToken,
  CurrentFirstToken,
  CurrentSecondToken,
} from '../actions';
import CurrentAlgoSwapContext, {CurrentTokenInfo} from './types';

const initTokenInfo: CurrentTokenInfo = {
  tokenList: [],
  fromToken: undefined,
  toToken: undefined,
  firstToken: undefined,
  secondToken: undefined,
};

type CurrentTokenInfoAction =
  | CurrentTokenList
  | CurrentFromToken
  | CurrentToToken
  | CurrentFirstToken
  | CurrentSecondToken;

export const selectFromToken = (state: CurrentAlgoSwapContext) => {
  return state.tokens.fromToken;
};

export const selectToToken = (state: CurrentAlgoSwapContext) => {
  return state.tokens.toToken;
};

export const selectFirstToken = (state: CurrentAlgoSwapContext) => {
  return state.tokens.firstToken;
};

export const selectSecondToken = (state: CurrentAlgoSwapContext) => {
  return state.tokens.secondToken;
};

export const selectTokenList = (state: CurrentAlgoSwapContext) => {
  return state.tokens.tokenList;
};

export default function tokens(
  state = initTokenInfo,
  action: CurrentTokenInfoAction
): CurrentTokenInfo {
  switch (action.type) {
    case ActionType.SetTokenList:
      return {...state, tokenList: action.tokenList};
    case ActionType.SetFromToken:
      return {...state, fromToken: action.fromToken};
    case ActionType.SetToToken:
      return {...state, toToken: action.toToken};
    case ActionType.SetFirstToken:
      return {...state, firstToken: action.firstToken};
    case ActionType.SetSecondToken:
      return {...state, secondToken: action.secondToken};
    default:
      return state;
  }
}
