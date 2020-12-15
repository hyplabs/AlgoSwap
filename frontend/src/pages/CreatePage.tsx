import React from 'react';
import { useHistory, useParams } from 'react-router-dom';

import CreatePair from '../components/CreatePair';
import './CreatePage.css'

const CreatePage: React.FC = () => {
  const { first, second } = useParams<ParamTypes>();
  const history = useHistory();
  return (
    <div className="AddPage">
      <CreatePair
        firstToken={first || ''}
        secondToken={second || ''}
        updateTokens={(first, second) => history.push(`/create/${first || 'ETH'}/${second}`)}
      />
    </div>
  );
};

interface ParamTypes {
  first: string | undefined;
  second: string | undefined;
}

export default CreatePage;
