import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import App from './App';
import { Router } from 'react-router-dom'
import { createBrowserHistory } from 'history'

import Main from './Main';

const history = createBrowserHistory();

ReactDOM.render((
  <Router history={history}>
    <Main history={history} />
  </Router>
), document.getElementById('root'))