import React from 'react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { BrandingProvider } from './contexts/BrandingContext';
import { Navbar, Footer } from './components/layout';
import AppRoutes from './routes/AppRoutes';

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <BrandingProvider>
          <div className="app-shell d-flex flex-column min-vh-100">
            <Navbar />
            <main className="main-content flex-grow-1">
              <AppRoutes />
            </main>
            <Footer />
          </div>
        </BrandingProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
