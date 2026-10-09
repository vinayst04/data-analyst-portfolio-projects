import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import FlowPage from './FlowPage';
import './styles.css';

const Page = window.location.pathname === '/flow' ? FlowPage : App;
ReactDOM.createRoot(document.getElementById('root')!).render(<React.StrictMode><Page /></React.StrictMode>);
