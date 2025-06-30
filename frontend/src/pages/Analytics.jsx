import { useState, useEffect } from 'react';
import { analyticsAPI } from '../services/api';

const Analytics = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await analyticsAPI.getDashboard();
        setDashboardData(response.data);
      } catch (error) {
        console.error('Failed to fetch analytics:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Analytics & Insights</h1>
        <p className="mt-1 text-sm text-gray-500">
          View your performance metrics and job market insights
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900">Total Profiles</h3>
          <p className="text-3xl font-bold text-primary-600">
            {dashboardData?.total_profiles || 0}
          </p>
        </div>
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900">Jobs Scraped</h3>
          <p className="text-3xl font-bold text-green-600">
            {dashboardData?.total_jobs_scraped || 0}
          </p>
        </div>
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900">Jobs Analyzed</h3>
          <p className="text-3xl font-bold text-yellow-600">
            {dashboardData?.total_jobs_analyzed || 0}
          </p>
        </div>
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900">Proposals Generated</h3>
          <p className="text-3xl font-bold text-purple-600">
            {dashboardData?.total_proposals_generated || 0}
          </p>
        </div>
      </div>

      <div className="card">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Activity</h3>
        <p className="text-gray-500">Analytics features coming soon...</p>
      </div>
    </div>
  );
};

export default Analytics; 