import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { useState, useEffect } from 'react';
import Header from './components/layout/Header';
import MobileSidebar from './components/layout/MobileSidebar';
import Dashboard from './pages/Dashboard';
import Profiles from './pages/Profiles';
import JobAnalysis from './pages/JobAnalysis';
import Proposals from './pages/Proposals';
import Analytics from './pages/Analytics';
import { healthAPI } from './services/api';
import Footer from './components/layout/Footer';

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [backendStatus, setBackendStatus] = useState('checking');

  useEffect(() => {
    // Check backend health on app start
    const checkBackendHealth = async () => {
      try {
        await healthAPI.check();
        setBackendStatus('connected');
      } catch (error) {
        console.error('Backend connection failed:', error);
        setBackendStatus('disconnected');
      }
    };

    checkBackendHealth();
  }, []);

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        {/* Backend Status Banner */}
        {backendStatus === 'disconnected' && (
          <div className="bg-red-600 text-white px-4 py-2 text-center">
            <p className="text-sm">
              ⚠️ Backend server is not running. Please check the backend service status.
            </p>
          </div>
        )}

        {/* Header with Navigation */}
        <Header 
          sidebarOpen={sidebarOpen} 
          setSidebarOpen={setSidebarOpen}
          backendStatus={backendStatus}
        />

        {/* Mobile Sidebar */}
        <MobileSidebar 
          sidebarOpen={sidebarOpen} 
          setSidebarOpen={setSidebarOpen}
        />

        {/* Main Content */}
        <main className="py-6">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/profiles" element={<Profiles />} />
              <Route path="/job-scraping" element={<JobAnalysis />} />
              <Route path="/job-analysis" element={<JobAnalysis />} />
              <Route path="/proposals" element={<Proposals />} />
              <Route path="/analytics" element={<Analytics />} />
            </Routes>
          </div>
        </main>
      </div>
      <Footer />
    </Router>
  );
}

export default App;
