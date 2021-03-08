import ActionType from '../actions/types';
import {CurrentSlippageTolerance} from '../actions';
import CurrentAlgoSwapContext, {CurrentTransaction} from './types';

const initTransaction: CurrentTransaction = {
  slippageTolerance: 1,
};

export const selectSlippageTolerance = (state: CurrentAlgoSwapContext) => {
  return state.transaction.slippageTolerance;
};

export default function transaction(
  state = initTransaction,
  action: CurrentSlippageTolerance
): CurrentTransaction {
  switch (action.type) {
    case ActionType.SetSlippageTolerance:
      return {...state, slippageTolerance: action.slippageTolerance};
    default:
      return state;
  }
}
