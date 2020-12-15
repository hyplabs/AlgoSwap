const developmentConfig = require('./config/development');
const productionConfig = require('./config/production');

const isProduction = process.env.ALGORAND_IS_PRODUCTION || false;

module.exports = {
  config: isProduction ? productionConfig : developmentConfig,
  isProduction,
};
