export interface CurrentUser {
  readonly accountAddress: string | null;
}

export interface CurrentTokenInfo {
  readonly tokenList: Array<Array<string>> | [];
  readonly fromToken: string;
  readonly toToken: string;
  readonly firstToken: string;
  readonly secondToken: string;
}

export default interface CurrentAlgoSwapContext {
  user: CurrentUser;
  tokens: CurrentTokenInfo;
}
