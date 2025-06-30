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
    // Check backend health on app start with retry mechanism
    const checkBackendHealth = async (retryCount = 0) => {
      const maxRetries = 3;
      
      try {
        console.log(`Checking backend health... (attempt ${retryCount + 1}/${maxRetries + 1})`);
        const response = await healthAPI.check();
        console.log('Backend health check successful:', response);
        setBackendStatus('connected');
      } catch (error) {
        console.error(`Backend connection failed (attempt ${retryCount + 1}):`, error);
        console.error('Error details:', {
          message: error.message,
          status: error.response?.status,
          statusText: error.response?.statusText,
          data: error.response?.data
        });
        
        if (retryCount < maxRetries) {
          console.log(`Retrying in 2 seconds...`);
          setTimeout(() => checkBackendHealth(retryCount + 1), 2000);
        } else {
          console.error('Max retries reached, marking backend as disconnected');
          setBackendStatus('disconnected');
        }
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
            <div className="flex items-center justify-center gap-4">
              <p className="text-sm">
                ⚠️ Backend server is not running. Please check the backend service status.
              </p>
              <button
                onClick={() => {
                  setBackendStatus('checking');
                  const checkBackendHealth = async () => {
                    try {
                      const response = await healthAPI.check();
                      console.log('Manual retry successful:', response);
                      setBackendStatus('connected');
                    } catch (error) {
                      console.error('Manual retry failed:', error);
                      setBackendStatus('disconnected');
                    }
                  };
                  checkBackendHealth();
                }}
                className="px-3 py-1 bg-white text-red-600 rounded text-xs font-medium hover:bg-gray-100 transition-colors"
              >
                Retry
              </button>
            </div>
          </div>
        )}
        
        {backendStatus === 'checking' && (
          <div className="bg-yellow-600 text-white px-4 py-2 text-center">
            <p className="text-sm">
              🔄 Checking backend connection...
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
