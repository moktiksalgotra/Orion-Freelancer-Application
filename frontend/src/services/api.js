import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Profiles API
export const profilesAPI = {
  // Get all profiles
  getAll: () => api.get('/profiles/'),
  
  // Get single profile
  getById: (id) => api.get(`/profiles/${id}`),
  
  // Create new profile
  create: (profileData) => api.post('/profiles/', profileData),
  
  // Update profile
  update: (id, profileData) => api.put(`/profiles/${id}`, profileData),
  
  // Delete profile
  delete: (id) => api.delete(`/profiles/${id}`),
  
  // Relevant Experience Projects
  getRelevantExperienceProjects: (profileId) => api.get(`/profiles/${profileId}/relevant-experience`),
  
  addRelevantExperienceProject: (profileId, projectData) => 
    api.post(`/profiles/${profileId}/relevant-experience`, projectData),
  
  updateRelevantExperienceProject: (profileId, projectId, projectData) => 
    api.put(`/profiles/${profileId}/relevant-experience/${projectId}`, projectData),
  
  deleteRelevantExperienceProject: (profileId, projectId) => 
    api.delete(`/profiles/${profileId}/relevant-experience/${projectId}`),
};

// Jobs API
export const jobsAPI = {
  // Scrape jobs
  scrape: (scrapingData) => api.post('/jobs/scrape', scrapingData),
  
  // Get scraped jobs
  getScraped: (limit = 50) => api.get(`/jobs/scraped?limit=${limit}`),
  
  // Clear scraped jobs
  clearScraped: () => api.delete('/jobs/scraped'),
  
  // Analyze job
  analyze: (analysisData) => api.post('/jobs/analyze', analysisData),
  
  // Scrape job from URL
  scrapeFromUrl: (url) => api.get(`/jobs/scrape-url?url=${encodeURIComponent(url)}`),
};

// Convenience functions for job scraping
export const scrapeJobs = (scrapingData) => jobsAPI.scrape(scrapingData).then(response => response.data);
export const getScrapedJobs = (limit = 50) => jobsAPI.getScraped(limit).then(response => response.data);
export const clearScrapedJobs = () => jobsAPI.clearScraped().then(response => response.data);

// Proposals API
export const proposalsAPI = {
  // Generate proposal
  generate: (proposalData) => api.post('/proposals/generate', proposalData),
  
  // Get all proposals for a freelancer
  getAll: (freelancerId) => api.get(`/proposals/?freelancer_id=${freelancerId}`),
  
  // Get single proposal
  getById: (id) => api.get(`/proposals/${id}`),
  
  // Update proposal status
  updateStatus: (id, status, clientResponse) => 
    api.put(`/proposals/${id}`, { status, client_response: clientResponse }),
};

// Analytics API
export const analyticsAPI = {
  // Get dashboard stats
  getDashboard: () => api.get('/analytics/dashboard'),
  
  // Get profile stats
  getProfileStats: (profileId) => api.get(`/analytics/profiles/${profileId}/stats`),
  
  // Get job trends
  getJobTrends: () => api.get('/analytics/jobs/trends'),
  
  // Export profile data
  exportProfile: (profileId) => api.get(`/analytics/export/${profileId}`),
};

// Health check
export const healthAPI = {
  check: () => axios.get('http://localhost:8000/health'),
};

export default api; 