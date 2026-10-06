import React from 'react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { BrandingProvider } from './contexts/BrandingContext';
import { ToastProvider } from './contexts/ToastContext';
import { Navbar, Footer } from './components/layout';
import AppRoutes from './routes/AppRoutes';
import ErrorBoundary from './components/common/ErrorBoundary';

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <BrandingProvider>
          <ToastProvider>
            <div className="app-shell d-flex flex-column min-vh-100">
            <Navbar />
            <main className="main-content flex-grow-1">
              <ErrorBoundary>
                <AppRoutes />
              </ErrorBoundary>
            </main>
              <Footer />
            </div>
          </ToastProvider>
        </BrandingProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
