import { useState, useEffect } from 'react';
import { scrapeJobs, getScrapedJobs, clearScrapedJobs } from '../services/api';

const JobScraping = () => {
  const [keywords, setKeywords] = useState('');
  const [maxJobs, setMaxJobs] = useState(10);
  const [isLoading, setIsLoading] = useState(false);
  const [scrapedJobs, setScrapedJobs] = useState([]);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    setSuccess('');

    try {
      const keywordList = keywords.split('\n').filter(k => k.trim());
      if (keywordList.length === 0) {
        setError('Please enter at least one keyword');
        return;
      }

      const response = await scrapeJobs({
        keywords: keywordList,
        max_jobs_per_keyword: maxJobs
      });

      // Simplified message: jobs are not filtered by keyword anymore
      const message = `Scraped ${response.total_count} jobs (no keyword filtering applied).`;
      setSuccess(message);
      setScrapedJobs(response.jobs);
      
      // Refresh the scraped jobs list
      loadScrapedJobs();
    } catch (err) {
      setError(err.message || 'Failed to scrape jobs');
    } finally {
      setIsLoading(false);
    }
  };

  const loadScrapedJobs = async () => {
    try {
      const jobs = await getScrapedJobs();
      setScrapedJobs(jobs);
    } catch (err) {
      console.error('Failed to load scraped jobs:', err);
    }
  };

  const handleClearJobs = async () => {
    if (window.confirm('Are you sure you want to clear all scraped jobs? This action cannot be undone.')) {
      try {
        await clearScrapedJobs();
        setScrapedJobs([]);
        setSuccess('All scraped jobs cleared successfully');
      } catch (err) {
        setError('Failed to clear scraped jobs');
      }
    }
  };

  // Load existing jobs on component mount
  useEffect(() => {
    loadScrapedJobs();
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Job Scraping</h1>
        <p className="mt-1 text-sm text-gray-500">
          Scrape jobs from Upwork (no keyword filtering; all jobs shown as returned by the API)
        </p>
      </div>

      <div className="card">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Scrape Jobs</h3>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Requests (one per line) *
            </label>
            <textarea
              required
              value={keywords}
              onChange={(e) => setKeywords(e.target.value)}
              className="textarea-field"
              rows="4"
              placeholder="React\nNode.js\nPython\nUI/UX Design"
            />
            <p className="text-xs text-gray-500 mt-1">
              Each line will trigger a separate API call, but jobs are not filtered by keyword. All jobs returned by the API will be shown.
            </p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Max Jobs per Request
            </label>
            <input
              type="number"
              min="1"
              max="50"
              value={maxJobs}
              onChange={(e) => setMaxJobs(parseInt(e.target.value))}
              className="input-field"
            />
            <p className="text-xs text-gray-500 mt-1">
              Maximum number of jobs to scrape for each request (1-50). No keyword filtering is applied.
            </p>
          </div>
          <button 
            type="submit" 
            className="btn-primary"
            disabled={isLoading}
          >
            {isLoading ? 'Scraping...' : 'Start Scraping'}
          </button>
        </form>

        {error && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
            <p className="text-red-700 text-sm">{error}</p>
          </div>
        )}

        {success && (
          <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-md">
            <p className="text-green-700 text-sm">{success}</p>
          </div>
        )}
      </div>

      <div className="card">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-medium text-gray-900">Scraped Jobs</h3>
          <div className="flex gap-2">
            <button 
              onClick={loadScrapedJobs}
              className="btn-secondary text-sm"
            >
              Refresh
            </button>
            {scrapedJobs.length > 0 && (
              <button 
                onClick={handleClearJobs}
                className="btn-secondary text-sm text-red-600 hover:text-red-800"
              >
                Clear All
              </button>
            )}
          </div>
        </div>
        
        {scrapedJobs.length === 0 ? (
          <p className="text-gray-500">No jobs scraped yet. Start scraping to see results.</p>
        ) : (
          <div className="space-y-4">
            {scrapedJobs.map((job, index) => (
              <div key={job.id || index} className="border border-gray-200 rounded-lg p-4">
                <div className="flex justify-between items-start mb-2">
                  <h4 className="text-lg font-medium text-gray-900">{job.job_title}</h4>
                  <span className="text-sm text-gray-500">{job.job_category}</span>
                </div>
                
                <p className="text-gray-600 mb-3 line-clamp-2">{job.job_description}</p>
                
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <span className="text-gray-500">Client:</span>
                    <p className="font-medium">{job.client_name}</p>
                  </div>
                  <div>
                    <span className="text-gray-500">Rating:</span>
                    <p className="font-medium">{job.client_rating}/5</p>
                  </div>
                  <div>
                    <span className="text-gray-500">Budget:</span>
                    <p className="font-medium">{job.budget_range}</p>
                  </div>
                  <div>
                    <span className="text-gray-500">Duration:</span>
                    <p className="font-medium">{job.project_duration}</p>
                  </div>
                </div>
                
                {job.required_skills && job.required_skills.length > 0 && (
                  <div className="mt-3">
                    <span className="text-gray-500 text-sm">Skills:</span>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {job.required_skills.map((skill, skillIndex) => (
                        <span 
                          key={skillIndex}
                          className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full"
                        >
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                
                {job.job_url && (
                  <div className="mt-3">
                    <a 
                      href={job.job_url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:text-blue-800 text-sm"
                    >
                      View Job on Upwork →
                    </a>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default JobScraping; 