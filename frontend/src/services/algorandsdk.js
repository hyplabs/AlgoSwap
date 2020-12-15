import algorand from 'algosdk';

import {config} from 'config';

const token = {
  'X-API-Key': config.API_KEY,
};
const port = '';

const AlgodClient = new algorand.Algodv2(token, config.BASE_SERVER, port);

export default AlgodClient;
