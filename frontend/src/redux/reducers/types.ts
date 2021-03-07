export interface CurrentUser {
  readonly accountAddress: string | null;
}

export interface CurrentTransaction {
  readonly slippageTolerance: number;
}

export interface CurrentTokenInfo {
  readonly tokenList: Array<Array<string>> | [];
  readonly fromToken: string | undefined;
  readonly toToken: string | undefined;
  readonly firstToken: string | undefined;
  readonly secondToken: string | undefined;
}

export default interface CurrentAlgoSwapContext {
  user: CurrentUser;
  transaction: CurrentTransaction;
  tokens: CurrentTokenInfo;
}
