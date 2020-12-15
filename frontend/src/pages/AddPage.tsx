import React from 'react';
import { useHistory, useParams } from 'react-router-dom';

import AddLiquidity from '../components/AddLiquidity';
import './AddPage.css'

const AddPage: React.FC = () => {
  const { first, second } = useParams<ParamTypes>();
  const history = useHistory();
  return (
    <div className="AddPage">
      <AddLiquidity
        firstToken={first || ''}
        secondToken={second || ''}
        updateTokens={(first, second) => history.push(`/add/${first || 'ETH'}/${second}`)}
      />
    </div>
  );
};

interface ParamTypes {
  first: string | undefined;
  second: string | undefined;
}

export default AddPage;
