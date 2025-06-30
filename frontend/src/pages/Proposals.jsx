import { useState, useEffect } from 'react';
import { profilesAPI, proposalsAPI } from '../services/api';

const Proposals = () => {
  const [profiles, setProfiles] = useState([]);
  const [selectedProfile, setSelectedProfile] = useState('');
  const [jobData, setJobData] = useState({
    job_title: '',
    job_description: '',
    required_skills: '',
    client_rating: '',
    job_budget: '',
    job_url: '',
    use_ai: true
  });
  const [generatedProposal, setGeneratedProposal] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    loadProfiles();
  }, []);

  const loadProfiles = async () => {
    try {
      const response = await profilesAPI.getAll();
      setProfiles(response.data);
      if (response.data.length > 0) {
        setSelectedProfile(response.data[0].id.toString());
      }
    } catch (err) {
      setError('Failed to load profiles');
      console.error('Error loading profiles:', err);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setGeneratedProposal(null);

    try {
      // Parse skills from comma-separated string
      const skills = jobData.required_skills
        .split(',')
        .map(skill => skill.trim())
        .filter(skill => skill.length > 0);

      const proposalData = {
        freelancer_id: parseInt(selectedProfile),
        job_title: jobData.job_title,
        job_description: jobData.job_description,
        required_skills: skills,
        client_rating: jobData.client_rating ? parseFloat(jobData.client_rating) : null,
        job_budget: jobData.job_budget ? parseFloat(jobData.job_budget) : null,
        job_url: jobData.job_url || null,
        use_ai: jobData.use_ai
      };

      const response = await proposalsAPI.generate(proposalData);
      setGeneratedProposal(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate proposal');
      console.error('Error generating proposal:', err);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = async (text) => {
    try {
      await navigator.clipboard.writeText(text);
      alert('Proposal copied to clipboard!');
    } catch (err) {
      console.error('Failed to copy to clipboard:', err);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Proposal Generation</h1>
        <p className="mt-1 text-sm text-gray-500">
          Generate AI-powered proposals for jobs using LLaMA 3.3
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input Form */}
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Generate Proposal</h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Select Your Profile *
              </label>
              <select
                required
                value={selectedProfile}
                onChange={(e) => setSelectedProfile(e.target.value)}
                className="input-field"
              >
                <option value="">Select a profile</option>
                {profiles.map(profile => (
                  <option key={profile.id} value={profile.id}>
                    {profile.name} - ${profile.hourly_rate}/hr
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Job Title *
              </label>
              <input
                type="text"
                required
                value={jobData.job_title}
                onChange={(e) => setJobData({...jobData, job_title: e.target.value})}
                className="input-field"
                placeholder="e.g., React Developer Needed"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Job Description *
              </label>
              <textarea
                required
                value={jobData.job_description}
                onChange={(e) => setJobData({...jobData, job_description: e.target.value})}
                className="textarea-field"
                rows="4"
                placeholder="Paste the job description here..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Required Skills (comma-separated) *
              </label>
              <input
                type="text"
                required
                value={jobData.required_skills}
                onChange={(e) => setJobData({...jobData, required_skills: e.target.value})}
                className="input-field"
                placeholder="e.g., React, JavaScript, Node.js"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Client Rating (0-5)
                </label>
                <input
                  type="number"
                  min="0"
                  max="5"
                  step="0.1"
                  value={jobData.client_rating}
                  onChange={(e) => setJobData({...jobData, client_rating: e.target.value})}
                  className="input-field"
                  placeholder="4.5"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Job Budget ($)
                </label>
                <input
                  type="number"
                  min="0"
                  step="0.01"
                  value={jobData.job_budget}
                  onChange={(e) => setJobData({...jobData, job_budget: e.target.value})}
                  className="input-field"
                  placeholder="1000.00"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Job URL (optional)
              </label>
              <input
                type="url"
                value={jobData.job_url}
                onChange={(e) => setJobData({...jobData, job_url: e.target.value})}
                className="input-field"
                placeholder="https://www.upwork.com/jobs/~..."
              />
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="useAI"
                checked={jobData.use_ai}
                onChange={(e) => setJobData({...jobData, use_ai: e.target.checked})}
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
              <label htmlFor="useAI" className="ml-2 block text-sm text-gray-900">
                Use AI (LLaMA 3.3) for proposal generation
              </label>
            </div>

            <button 
              type="submit" 
              className="btn-primary w-full"
              disabled={loading}
            >
              {loading ? 'Generating...' : 'Generate Proposal'}
            </button>
          </form>
        </div>

        {/* Generated Proposal */}
        <div className="space-y-4">
          {error && (
            <div className="card bg-red-50 border-red-200">
              <div className="text-red-800">
                <h4 className="font-medium">Error</h4>
                <p className="text-sm">{error}</p>
              </div>
            </div>
          )}

          {generatedProposal && (
            <div className="card">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">Generated Proposal</h3>
                <button
                  onClick={() => copyToClipboard(generatedProposal.proposal_text)}
                  className="btn-secondary text-sm"
                >
                  Copy to Clipboard
                </button>
              </div>

              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="prose prose-sm max-w-none">
                  <pre className="whitespace-pre-wrap text-sm text-gray-800 font-sans">
                    {generatedProposal.proposal_text}
                  </pre>
                </div>
              </div>

              <div className="mt-4 pt-4 border-t border-gray-200">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-500">Proposal ID:</span>
                    <span className="ml-2 font-medium">{generatedProposal.id}</span>
                  </div>
                  <div>
                    <span className="text-gray-500">Status:</span>
                    <span className="ml-2 font-medium">{generatedProposal.proposal_status}</span>
                  </div>
                  <div>
                    <span className="text-gray-500">Generated:</span>
                    <span className="ml-2 font-medium">
                      {new Date(generatedProposal.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-500">Method:</span>
                    <span className="ml-2 font-medium">
                      {generatedProposal.proposal_text.includes('Dear Client') ? 'AI Generated' : 'Template'}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Proposals; 