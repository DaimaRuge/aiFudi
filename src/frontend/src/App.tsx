// App Component
//应用入口

import React from 'react';
import { App as AntApp } from 'antd';
import { AppRoutes } from './routes';

function App() {
  return (
    <AntApp>
      <AppRoutes />
    </AntApp>
  );
}

export default App;
