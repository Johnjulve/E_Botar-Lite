import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';

/* Foundation Layer */
import './assets/styles/variables.css';
import './assets/styles/foundation/resets.css';
import './assets/styles/foundation/typography.css';

/* External Libraries */
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-icons/font/bootstrap-icons.css';
import '@fortawesome/fontawesome-free/css/all.min.css';
import 'bootstrap/dist/js/bootstrap.bundle.min.js';

/* Bootstrap Overrides & Globals */
import './assets/styles/vendors/bootstrap-overrides.css';
import './assets/styles/global/components.css';
import './assets/styles/global/layout.css';
import './assets/styles/global/utilities.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
