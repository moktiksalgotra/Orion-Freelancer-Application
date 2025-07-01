import React, { useState, useEffect } from 'react';
import { profilesAPI, jobsAPI, proposalsAPI, scrapeJobs } from '../services/api';
import {
  CheckCircleIcon,
  XCircleIcon,
  LightBulbIcon,
  SparklesIcon,
  ClipboardDocumentIcon,
  MagnifyingGlassIcon,
  PencilIcon,
  ArrowLeftIcon,
  ChevronDownIcon,
  ChevronUpIcon,
  ChartBarIcon,
  DocumentTextIcon
} from '@heroicons/react/24/outline';
import analysisImage from '../assets/analysis.png';

const JobAnalysis = () => {
  // Move ALL hooks to the top of the component, before any conditional returns
  const [profiles, setProfiles] = useState([]);
  const [selectedProfile, setSelectedProfile] = useState('');
  const [jobData, setJobData] = useState({
    job_title: '',
    job_description: '',
    required_skills: '',
    client_rating: '',
    avg_pay_rate: '',
    job_url: ''
  });
  const [analysisResult, setAnalysisResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [proposalLoading, setProposalLoading] = useState(false);
  const [generatedProposal, setGeneratedProposal] = useState(null);
  const [proposalError, setProposalError] = useState('');
  const [scrapeKeywords, setScrapeKeywords] = useState('');
  const [scrapeMaxJobs, setScrapeMaxJobs] = useState(5);
  const [currentView, setCurrentView] = useState('landing');
  const [showAnalysis, setShowAnalysis] = useState(false);
  const [showDetails, setShowDetails] = useState(false);
  const [showProposal, setShowProposal] = useState(false);
  const [expandedSections, setExpandedSections] = useState({
    analysis: true,
    details: true,
    proposal: true
  });
  const [scrapedJobs, setScrapedJobs] = useState([]);
  const [scrapeLoading, setScrapeLoading] = useState(false);
  const [scrapeError, setScrapeError] = useState('');
  const [scrapeStep, setScrapeStep] = useState(0);
  const [scrapeProposalLoading, setScrapeProposalLoading] = useState(false);
  const [scrapeProposal, setScrapeProposal] = useState(null);
  const [scrapeProposalError, setScrapeProposalError] = useState('');
  const [scrapeSelectedProfile, setScrapeSelectedProfile] = useState('');
  const [scrapeAnalysisResult, setScrapeAnalysisResult] = useState(null);
  const [scrapeAnalysisLoading, setScrapeAnalysisLoading] = useState(false);
  const [scrapeAnalysisError, setScrapeAnalysisError] = useState('');
  const [jobStates, setJobStates] = useState([]);
  const [manualProposalView, setManualProposalView] = useState({ open: false, proposal: null });
  const [isEditingProposal, setIsEditingProposal] = useState(false);
  const [editedProposalText, setEditedProposalText] = useState("");
  const [scrapeProposalView, setScrapeProposalView] = useState({ open: false, proposal: null, job: null });

  useEffect(() => {
    setJobStates(scrapedJobs.map(() => ({
      selectedProfile: '',
      analysis: null,
      proposal: null,
      loading: false,
      error: '',
      proposalLoading: false,
      proposalError: '',
    })));
  }, [scrapedJobs]);

  useEffect(() => {
    loadProfiles();
  }, []);

  useEffect(() => {
    if (analysisResult) {
      setShowAnalysis(true);
      setTimeout(() => setShowDetails(true), 300);
    }
  }, [analysisResult]);

  useEffect(() => {
    if (generatedProposal) {
      setShowProposal(true);
    }
  }, [generatedProposal]);

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
    setAnalysisResult(null);
    setGeneratedProposal(null);
    setProposalError('');
    setShowAnalysis(false);
    setShowDetails(false);
    setShowProposal(false);

    try {
      // Parse skills from comma-separated string
      const skills = jobData.required_skills
        .split(',')
        .map(skill => skill.trim())
        .filter(skill => skill.length > 0);

      const analysisData = {
        job_title: jobData.job_title,
        job_description: jobData.job_description,
        required_skills: skills,
        client_rating: jobData.client_rating ? parseFloat(jobData.client_rating) : null,
        avg_pay_rate: jobData.avg_pay_rate ? parseFloat(jobData.avg_pay_rate) : null,
        job_url: jobData.job_url || null,
        freelancer_id: parseInt(selectedProfile)
      };

      const response = await jobsAPI.analyze(analysisData);
      setAnalysisResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to analyze job');
      console.error('Error analyzing job:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateProposal = async () => {
    if (!analysisResult) return;
    setProposalLoading(true);
    setProposalError('');
    setGeneratedProposal(null);
    try {
      const response = await proposalsAPI.generate({
        job_title: jobData.job_title,
        job_description: jobData.job_description,
        required_skills: jobData.required_skills.split(',').map(s => s.trim()),
        client_rating: jobData.client_rating ? parseFloat(jobData.client_rating) : null,
        job_budget: jobData.avg_pay_rate ? parseFloat(jobData.avg_pay_rate) : null,
        job_url: jobData.job_url || null,
        freelancer_id: parseInt(selectedProfile),
        use_ai: true
      });
      console.log('Proposal API response:', response.data);
      setGeneratedProposal(response.data);
      setManualProposalView({ open: true, proposal: response.data }); // Always open focused view
    } catch (err) {
      setProposalError('Failed to generate proposal. Please try again.');
    } finally {
      setProposalLoading(false);
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

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const getMatchLevelDisplay = (matchLevel, overallScore) => {
    const matchConfigs = {
      'EXCELLENT': {
        title: 'Excellent Match!',
        subtitle: 'This job is a perfect fit for your profile. Apply with confidence.',
        bgColor: 'bg-gradient-to-br from-emerald-50 to-green-100',
        borderColor: 'border-emerald-200',
        iconColor: 'text-emerald-600',
        icon: '⭐',
        buttonText: 'Generate Proposal',
        buttonColor: 'bg-emerald-600 hover:bg-emerald-700',
        scoreColor: 'text-emerald-600',
        shadowColor: 'shadow-emerald-100/40'
      },
      'GREAT': {
        title: 'Great Match!',
        subtitle: 'This job is a strong fit for your profile. You can now generate a personalized proposal using AI.',
        bgColor: 'bg-gradient-to-br from-green-50 to-emerald-100',
        borderColor: 'border-green-200',
        iconColor: 'text-green-600',
        icon: '✅',
        buttonText: 'Generate Proposal',
        buttonColor: 'bg-green-600 hover:bg-green-700',
        scoreColor: 'text-green-600',
        shadowColor: 'shadow-green-100/40'
      },
      'MODERATE': {
        title: 'Moderate Match',
        subtitle: 'Consider applying but highlight relevant experience and transferable skills.',
        bgColor: 'bg-gradient-to-br from-yellow-50 to-orange-100',
        borderColor: 'border-yellow-200',
        iconColor: 'text-yellow-600',
        icon: '⚠️',
        buttonText: 'Generate Proposal',
        buttonColor: 'bg-yellow-600 hover:bg-yellow-700',
        scoreColor: 'text-yellow-600',
        shadowColor: 'shadow-yellow-100/40'
      },
      'LOW': {
        title: 'Low Match',
        subtitle: 'This job may not be the best fit, but you can still apply if interested.',
        bgColor: 'bg-gradient-to-br from-red-50 to-pink-100',
        borderColor: 'border-red-200',
        iconColor: 'text-red-600',
        icon: '❌',
        buttonText: 'Generate Proposal Anyway',
        buttonColor: 'bg-red-600 hover:bg-red-700',
        scoreColor: 'text-red-600',
        shadowColor: 'shadow-red-100/40'
      }
    };

    return matchConfigs[matchLevel] || matchConfigs['LOW'];
  };

  const getResultBgColor = (result) => {
    return result === 'PASS' ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200';
  };

  const handleScrapeSubmit = async (e) => {
    e.preventDefault();
    setScrapeLoading(true);
    setScrapeError('');
    setScrapedJobs([]);
    setScrapeStep(0);
    setScrapeProposal(null);
    setScrapeProposalError('');

    // Ensure a profile is selected
    if (!selectedProfile) {
      setScrapeError('Please select a profile before scraping jobs.');
      setScrapeLoading(false);
      return;
    }

    try {
      const keywords = scrapeKeywords
        .split('\n')
        .map(k => k.trim())
        .filter(k => k.length > 0);
      
      if (keywords.length === 0) {
        setScrapeError('Please enter at least one keyword.');
        setScrapeLoading(false);
        return;
      }
      
      // Use the jobsAPI service to scrape real-time jobs
      const response = await jobsAPI.scrape({
        keywords,
        max_jobs_per_keyword: Math.min(scrapeMaxJobs || 5, 5),
      });
      
      if (response && response.jobs && response.jobs.length > 0) {
        setScrapedJobs(response.jobs);
        setScrapeStep(0);
        // Show success message
        console.log(`Successfully scraped ${response.jobs.length} real-time jobs from Upwork`);
      } else {
        setScrapeError('No jobs found for your requests. This could be due to:\n• No active jobs returned by the API\n• RapidAPI rate limits or service issues\n• Network connectivity problems\n\nPlease try again later.');
      }
    } catch (err) {
      console.error('Scraping error:', err);
      const errorMessage = err.response?.data?.detail || 'Failed to scrape jobs.';
      
      if (errorMessage.includes('Failed to fetch jobs') || errorMessage.includes('RapidAPI')) {
        setScrapeError(`RapidAPI Error: ${errorMessage}\n\nThis could be due to:\n• Invalid or expired RapidAPI key\n• Rate limit exceeded (100 requests/month free tier)\n• RapidAPI service temporarily unavailable\n\nPlease check your RapidAPI configuration or try again later.`);
      } else {
        setScrapeError(`Scraping Error: ${errorMessage}\n\nPlease check your internet connection and try again.`);
      }
    } finally {
      setScrapeLoading(false);
    }
  };

  const handleScrapeAnalyze = async () => {
    setScrapeAnalysisLoading(true);
    setScrapeAnalysisError('');
    setScrapeAnalysisResult(null);
    setScrapeProposal(null);
    setScrapeProposalError('');
    try {
      const job = scrapedJobs[scrapeStep];
      const analysisData = {
        job_title: job.job_title || job.title || '',
        job_description: job.job_description || job.description || '',
        required_skills: job.required_skills || job.skills || [],
        client_rating: job.client_rating || null,
        avg_pay_rate: job.avg_pay_rate || null,
        job_url: job.job_url || job.url || '',
        freelancer_id: parseInt(scrapeSelectedProfile)
      };
      const response = await jobsAPI.analyze(analysisData);
      setScrapeAnalysisResult(response.data);
    } catch (err) {
      setScrapeAnalysisError('Failed to analyze job/profile match.');
    } finally {
      setScrapeAnalysisLoading(false);
    }
  };

  const handleScrapeGenerateProposal = async () => {
    if (!scrapeAnalysisResult) return;
    setScrapeProposalLoading(true);
    setScrapeProposalError('');
    setScrapeProposal(null);
    try {
      const job = scrapedJobs[scrapeStep];
      const response = await proposalsAPI.generate({
        job_title: job.job_title || job.title || '',
        job_description: job.job_description || job.description || '',
        required_skills: job.required_skills || job.skills || [],
        client_rating: job.client_rating || null,
        job_budget: job.avg_pay_rate || null,
        job_url: job.job_url || job.url || '',
        freelancer_id: parseInt(scrapeSelectedProfile),
        use_ai: true
      });
      setScrapeProposal(response.data);
    } catch (err) {
      setScrapeProposalError('Failed to generate proposal. Please try again.');
    } finally {
      setScrapeProposalLoading(false);
    }
  };

  const resetToLanding = () => {
    setCurrentView('landing');
    setAnalysisResult(null);
    setGeneratedProposal(null);
    setShowAnalysis(false);
    setShowDetails(false);
    setShowProposal(false);
    setError('');
    setProposalError('');
  };

  // Scrape jobs handler
  const handleScrapeCardSimpleScrape = async () => {
    setScrapeLoading(true);
    setScrapeError('');
    setScrapedJobs([]);
    try {
      const response = await scrapeJobs({
        keywords: [], // Let backend handle default logic
        max_jobs_per_keyword: 5,
      });
      console.log('SCRAPE RESPONSE:', response); // Debug log
      const jobs = response.jobs || response; // Accept both {jobs: [...]} and [...] formats
      if (jobs && Array.isArray(jobs) && jobs.length > 0) {
        setScrapedJobs(jobs);
      } else {
        setScrapeError('No jobs found.');
      }
    } catch (err) {
      setScrapeError('Failed to scrape jobs.');
    } finally {
      setScrapeLoading(false);
    }
  };

  // Handle profile selection and analysis for a job
  const handleScrapeCardProfileSelect = async (jobIdx, profileId) => {
    setJobStates(prev => prev.map((state, idx) => idx === jobIdx ? { ...state, selectedProfile: profileId, loading: true, error: '', analysis: null, proposal: null } : state));
    try {
      const job = scrapedJobs[jobIdx];
      const analysisData = {
        job_title: job.job_title || job.title || '',
        job_description: job.job_description || job.description || '',
        required_skills: job.required_skills || job.skills || [],
        client_rating: job.client_rating || null,
        avg_pay_rate: job.avg_pay_rate || null,
        job_url: job.job_url || job.url || '',
        freelancer_id: parseInt(profileId)
      };
      const response = await jobsAPI.analyze(analysisData);
      setJobStates(prev => prev.map((state, idx) => idx === jobIdx ? { ...state, analysis: response.data, loading: false } : state));
    } catch (err) {
      setJobStates(prev => prev.map((state, idx) => idx === jobIdx ? { ...state, error: 'Failed to analyze match.', loading: false } : state));
    }
  };

  // Handle proposal generation for a job
  const handleScrapeCardGenerateProposal = async (jobIdx) => {
    setJobStates(prev => prev.map((state, idx) => idx === jobIdx ? { ...state, proposalLoading: true, proposalError: '', proposal: null } : state));
    try {
      const job = scrapedJobs[jobIdx];
      const state = jobStates[jobIdx];
      const response = await proposalsAPI.generate({
        job_title: job.job_title || job.title || '',
        job_description: job.job_description || job.description || '',
        required_skills: job.required_skills || job.skills || [],
        client_rating: job.client_rating || null,
        job_budget: job.avg_pay_rate || null,
        job_url: job.job_url || job.url || '',
        freelancer_id: parseInt(state.selectedProfile),
        use_ai: true
      });
      setJobStates(prev => prev.map((state, idx) => idx === jobIdx ? { ...state, proposal: response.data, proposalLoading: false } : state));
      // Show proposal in separate view
      setScrapeProposalView({ open: true, proposal: response.data, job });
    } catch (err) {
      setJobStates(prev => prev.map((state, idx) => idx === jobIdx ? { ...state, proposalError: 'Failed to generate proposal.', proposalLoading: false } : state));
    }
  };

  // Scrape Jobs View (full-page proposal view takes priority)
  if (scrapeProposalView.open && scrapeProposalView.proposal) {
    const proposal = scrapeProposalView.proposal;
    // If editing, show textarea and save/cancel
    if (isEditingProposal) {
      return (
        <div className="min-h-screen w-full flex flex-col items-center justify-center bg-gradient-to-br from-blue-50 via-white to-indigo-50 px-4 py-10">
          <div className="w-full max-w-4xl bg-white rounded-2xl shadow-xl border border-gray-200 p-12 flex flex-col gap-8">
            <button
              onClick={() => { setScrapeProposalView({ open: false, proposal: null, job: null }); setIsEditingProposal(false); }}
              className="self-start mb-2 px-4 py-1.5 rounded-full bg-gray-100 text-gray-700 font-medium hover:bg-gray-200 transition"
            >
              ← Back to Jobs
            </button>
            <h2 className="text-3xl font-bold text-emerald-700 mb-2 flex items-center gap-2">
              <svg className="h-7 w-7 text-emerald-600" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M9 7V6a3 3 0 016 0v1m-9 4h12M4 7h16a2 2 0 012 2v8a2 2 0 01-2 2H4a2 2 0 01-2-2V9a2 2 0 012-2z" /></svg>
              Edit Proposal
            </h2>
            <textarea
              className="w-full min-h-[350px] rounded-lg border border-gray-300 px-4 py-3 text-base focus:ring-2 focus:ring-green-400 focus:outline-none bg-gray-50 font-mono"
              value={editedProposalText}
              onChange={e => setEditedProposalText(e.target.value)}
            />
            <div className="flex gap-4 mt-2">
              <button
                onClick={() => {
                  setScrapeProposalView({ open: true, proposal: { ...proposal, proposal_text: editedProposalText }, job: scrapeProposalView.job });
                  setIsEditingProposal(false);
                }}
                className="px-8 py-3 rounded-full bg-emerald-600 text-white text-lg font-semibold hover:bg-emerald-700 transition"
              >
                Save
              </button>
              <button
                onClick={() => setIsEditingProposal(false)}
                className="px-8 py-3 rounded-full bg-gray-200 text-gray-700 text-lg font-semibold hover:bg-gray-300 transition"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      );
    }
    // Normal proposal view
    return (
      <div className="min-h-screen w-full flex flex-col items-center justify-center bg-gradient-to-br from-blue-50 via-white to-indigo-50">
        {/* Back Button aligned left, slightly below top */}
        <div className="w-full">
          <button
            onClick={() => setScrapeProposalView({ open: false, proposal: null, job: null })}
            className="inline-flex items-center rounded-full bg-gray-100 px-5 py-2 text-gray-700 font-medium hover:bg-gray-200 transition-colors mt-6 ml-4"
          >
            <ArrowLeftIcon className="h-5 w-5 mr-1 text-gray-600" />
            Back
          </button>
        </div>
        <div className="max-w-4xl w-full bg-white p-10 rounded-2xl shadow-lg border border-gray-200 flex flex-col mt-2">
          {/* Page Header OUTSIDE the card */}
          <div className="flex flex-col items-center mb-8">
            <div className="flex items-center gap-3 mb-2">
              <span className="inline-flex items-center justify-center rounded-full bg-green-100 p-2">
                <SparklesIcon className="h-6 w-6 text-green-600" />
              </span>
              <h1 className="text-3xl font-semibold text-gray-900 tracking-tight">Scraped Job Proposal</h1>
            </div>
            <p className="mt-1 text-base text-gray-600 text-center">
              This is your generated proposal for the scraped job. You can edit it as needed.
            </p>
          </div>
          {/* Proposal Output */}
          <div className="flex flex-col gap-4">
            <h2 className="text-2xl font-bold text-emerald-700 mb-2 flex items-center gap-2">
              <SparklesIcon className="h-6 w-6 text-emerald-600" />
              Generated Proposal
            </h2>
            <pre className="whitespace-pre-wrap text-base text-gray-800 font-sans leading-relaxed bg-gray-50 rounded-lg p-6 border border-gray-200">
              {proposal.proposal_text}
            </pre>
            {/* Add Edit Proposal button here */}
            <button
              onClick={() => {
                setIsEditingProposal(true);
                setEditedProposalText(proposal.proposal_text);
              }}
              className="px-6 py-2 rounded-full bg-blue-500 text-white font-semibold hover:bg-blue-600 transition mt-4 self-start"
            >
              Edit Proposal
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Landing Page View
  if (currentView === 'landing') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
        <div className="max-w-6xl mx-auto px-6 py-12">
          {/* Header */}
          <div className="text-center mb-16">
            <div className="inline-flex items-center justify-center rounded-full bg-primary-100 p-3 mb-6">
              <DocumentTextIcon className="h-8 w-8 text-primary-600" />
            </div>
            <h1 className="text-4xl font-bold text-gray-900 mb-4 tracking-tight">
              Job Analysis
            </h1>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto leading-relaxed">
              Choose how you'd like to analyze job opportunities. Enter details manually or scrape jobs automatically.
            </p>
          </div>

          {/* Hero Section with Image */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center mb-16">
            <div className="text-left">
              <h2 className="text-3xl font-bold text-gray-900 mb-6">
                Smart Job Analysis for Better Opportunities
              </h2>
              <p className="text-lg text-gray-600 mb-8 leading-relaxed">
                Our AI-powered platform helps you find the perfect job matches and generate compelling proposals that increase your chances of landing great projects.
              </p>
              <div className="space-y-4">
                <div className="flex items-center gap-3">
                  <CheckCircleIcon className="h-6 w-6 text-green-500 flex-shrink-0" />
                  <span className="text-gray-700">AI-powered job matching</span>
                </div>
                <div className="flex items-center gap-3">
                  <CheckCircleIcon className="h-6 w-6 text-green-500 flex-shrink-0" />
                  <span className="text-gray-700">Personalized proposal generation</span>
                </div>
                <div className="flex items-center gap-3">
                  <CheckCircleIcon className="h-6 w-6 text-green-500 flex-shrink-0" />
                  <span className="text-gray-700">Automated job discovery</span>
                </div>
              </div>
            </div>
            <div className="flex justify-center lg:justify-end">
              <div className="relative max-w-md">
                <div className="absolute inset-0 bg-gradient-to-r from-blue-400 to-purple-500 rounded-2xl transform rotate-3 opacity-10"></div>
                <img 
                  src={analysisImage} 
                  alt="Job Analysis Illustration" 
                  className="relative rounded-2xl shadow-2xl w-full h-auto max-w-xs"
                />
              </div>
            </div>
          </div>

          {/* Option Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-3xl mx-auto relative">
            {/* Manual Analysis Card */}
            <div 
              onClick={() => setCurrentView('manual')}
              className="group cursor-pointer relative"
            >
              {/* Hand-drawn Arrow (left, blue) */}
              <svg
                className="hidden md:block absolute -left-24 top-1/2 -translate-y-1/2 w-24 h-16 z-10"
                viewBox="0 0 100 50"
                fill="none"
                stroke="currentColor"
                strokeWidth="3"
                style={{ color: '#3b82f6' }}
              >
                <path d="M5,25 Q60,10 95,25" strokeLinecap="round" strokeLinejoin="round" />
                <polyline points="85,20 95,25 85,30" fill="none" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
              <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-8 hover:shadow-lg hover:border-primary-300 transition-all duration-300 transform hover:-translate-y-1">
                <div className="text-center">
                  <div className="inline-flex items-center justify-center rounded-full bg-blue-100 p-4 mb-6 group-hover:bg-blue-200 transition-colors">
                    <PencilIcon className="h-8 w-8 text-blue-600" />
                  </div>
                  <h3 className="text-2xl font-semibold text-gray-900 mb-3">
                    Manual Analysis
                  </h3>
                  <p className="text-gray-600 leading-relaxed mb-6">
                    Enter job details manually for personalized analysis and AI-powered proposal generation.
                  </p>
                  <div className="inline-flex items-center text-blue-600 font-medium group-hover:text-blue-700 transition-colors">
                    <span>
                      <button
                        className="inline-flex items-center px-6 py-2 bg-gradient-to-r from-blue-500 to-blue-600 text-white font-semibold rounded-full shadow-md hover:from-blue-600 hover:to-blue-700 hover:scale-105 transition-transform duration-200 focus:outline-none focus:ring-2 focus:ring-blue-400"
                        type="button"
                      >
                    Get Started
                        <svg className="ml-2 h-5 w-5" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
                    </svg>
                      </button>
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Scrape Jobs Card */}
            <div 
              onClick={() => setCurrentView('scrape')}
              className="group cursor-pointer relative"
            >
              {/* Hand-drawn Arrow (right, green) */}
              <svg
                className="hidden md:block absolute -right-24 top-1/2 -translate-y-1/2 w-24 h-16 z-10"
                viewBox="0 0 100 50"
                fill="none"
                stroke="currentColor"
                strokeWidth="3"
                style={{ color: '#22c55e' }}
              >
                <path d="M95,25 Q40,10 5,25" strokeLinecap="round" strokeLinejoin="round" />
                <polyline points="15,20 5,25 15,30" fill="none" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
              <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-8 hover:shadow-lg hover:border-primary-300 transition-all duration-300 transform hover:-translate-y-1">
                <div className="text-center">
                  <div className="inline-flex items-center justify-center rounded-full bg-green-100 p-4 mb-6 group-hover:bg-green-200 transition-colors">
                    <MagnifyingGlassIcon className="h-8 w-8 text-green-600" />
                  </div>
                  <h3 className="text-2xl font-semibold text-gray-900 mb-3">
                    Scrape Jobs
                  </h3>
                  <p className="text-gray-600 leading-relaxed mb-6">
                    Automatically discover and analyze job opportunities based on your keywords and criteria.
                  </p>
                  <div className="inline-flex items-center text-green-600 font-medium group-hover:text-green-700 transition-colors">
                    <span>
                      <button
                        className="inline-flex items-center px-6 py-2 bg-gradient-to-r from-green-500 to-green-600 text-white font-semibold rounded-full shadow-md hover:from-green-600 hover:to-green-700 hover:scale-105 transition-transform duration-200 focus:outline-none focus:ring-2 focus:ring-green-400"
                        type="button"
                      >
                    Start Scraping
                        <svg className="ml-2 h-5 w-5" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
                    </svg>
                      </button>
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Manual Analysis View
  if (currentView === 'manual') {
    // Focused proposal view (like scrape)
    if (manualProposalView.open && manualProposalView.proposal) {
      const proposal = manualProposalView.proposal;
      // If editing, show textarea and save/cancel
      if (isEditingProposal) {
        return (
          <div className="min-h-screen w-full flex flex-col items-center justify-center bg-gradient-to-br from-blue-50 via-white to-indigo-50 px-4 py-10">
            <div className="w-full max-w-4xl bg-white rounded-2xl shadow-xl border border-gray-200 p-12 flex flex-col gap-8">
              <button
                onClick={() => { setManualProposalView({ open: false, proposal: null }); setIsEditingProposal(false); }}
                className="self-start mb-2 px-4 py-1.5 rounded-full bg-gray-100 text-gray-700 font-medium hover:bg-gray-200 transition"
              >
                ← Back to Analysis
              </button>
              <h2 className="text-3xl font-bold text-emerald-700 mb-2 flex items-center gap-2">
                <svg className="h-7 w-7 text-emerald-600" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M9 7V6a3 3 0 016 0v1m-9 4h12M4 7h16a2 2 0 012 2v8a2 2 0 01-2 2H4a2 2 0 01-2-2V9a2 2 0 012-2z" /></svg>
                Edit Proposal
              </h2>
              <textarea
                className="w-full min-h-[350px] rounded-lg border border-gray-300 px-4 py-3 text-base focus:ring-2 focus:ring-green-400 focus:outline-none bg-gray-50 font-mono"
                value={editedProposalText}
                onChange={e => setEditedProposalText(e.target.value)}
              />
              <div className="flex gap-4 mt-2">
                <button
                  onClick={() => {
                    setManualProposalView({ open: true, proposal: { ...proposal, proposal_text: editedProposalText } });
                    setIsEditingProposal(false);
                  }}
                  className="px-8 py-3 rounded-full bg-emerald-600 text-white text-lg font-semibold hover:bg-emerald-700 transition"
                >
                  Save
                </button>
                <button
                  onClick={() => setIsEditingProposal(false)}
                  className="px-8 py-3 rounded-full bg-gray-200 text-gray-700 text-lg font-semibold hover:bg-gray-300 transition"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        );
      }
      // Normal proposal view
      return (
        <div className="min-h-screen w-full flex flex-col items-center justify-center bg-gradient-to-br from-blue-50 via-white to-indigo-50">
          {/* Back Button aligned left, slightly below top */}
          <div className="w-full">
            <button
              onClick={resetToLanding}
              className="inline-flex items-center rounded-full bg-gray-100 px-5 py-2 text-gray-700 font-medium hover:bg-gray-200 transition-colors mt-6 ml-4"
            >
              <ArrowLeftIcon className="h-5 w-5 mr-1 text-gray-600" />
              Back
            </button>
          </div>
          <div className="max-w-4xl w-full bg-white p-10 rounded-2xl shadow-lg border border-gray-200 flex flex-col mt-2">
            {/* Page Header OUTSIDE the card */}
            <div className="flex flex-col items-center mb-8">
              <div className="flex items-center gap-3 mb-2">
                <span className="inline-flex items-center justify-center rounded-full bg-blue-100 p-2">
                  <PencilIcon className="h-6 w-6 text-blue-600" />
                </span>
                <h1 className="text-3xl font-semibold text-gray-900 tracking-tight">Manual Job Analysis</h1>
              </div>
              <p className="mt-1 text-base text-gray-600 text-center">
                Enter job details for personalized analysis and AI proposal generation.
              </p>
            </div>
            {/* Proposal Output */}
            <div className="flex flex-col gap-4">
              <h2 className="text-2xl font-bold text-emerald-700 mb-2 flex items-center gap-2">
                <SparklesIcon className="h-6 w-6 text-emerald-600" />
                Generated Proposal
              </h2>
              <pre className="whitespace-pre-wrap text-base text-gray-800 font-sans leading-relaxed bg-gray-50 rounded-lg p-6 border border-gray-200">
                {proposal.proposal_text}
              </pre>
              {/* Add Edit Proposal button here */}
              <button
                onClick={() => {
                  setIsEditingProposal(true);
                  setEditedProposalText(proposal.proposal_text);
                }}
                className="px-6 py-2 rounded-full bg-blue-500 text-white font-semibold hover:bg-blue-600 transition mt-4 self-start"
              >
                Edit Proposal
              </button>
            </div>
          </div>
        </div>
      );
    }
    return (
      <div className="min-h-screen w-full flex flex-col items-center justify-center bg-gradient-to-br from-blue-50 via-white to-indigo-50">
        {/* Back Button aligned left, slightly below top */}
        <div className="w-full">
          <button
            onClick={resetToLanding}
            className="inline-flex items-center rounded-full bg-gray-100 px-5 py-2 text-gray-700 font-medium hover:bg-gray-200 transition-colors mt-6 ml-4"
          >
            <ArrowLeftIcon className="h-5 w-5 mr-1 text-gray-600" />
            Back
          </button>
        </div>
        <div className="max-w-4xl w-full bg-white p-10 rounded-2xl shadow-lg border border-gray-200 flex flex-col mt-2">
          {/* Page Header OUTSIDE the card */}
          <div className="flex flex-col items-center mb-8">
            <div className="flex items-center gap-3 mb-2">
              <span className="inline-flex items-center justify-center rounded-full bg-blue-100 p-2">
                <PencilIcon className="h-6 w-6 text-blue-600" />
              </span>
              <h1 className="text-3xl font-semibold text-gray-900 tracking-tight">Manual Job Analysis</h1>
            </div>
            <p className="mt-1 text-base text-gray-600 text-center">
              Enter job details for personalized analysis and AI proposal generation.
            </p>
          </div>

          {/* Input Form */}
          {(!loading && !analysisResult) && (
            <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-x-10 gap-y-8 w-full">
              <div className="flex flex-col col-span-1">
                <label className="block text-sm font-medium text-gray-800 mb-2">Select Your Profile *</label>
                <select
                  required
                  value={selectedProfile}
                  onChange={(e) => setSelectedProfile(e.target.value)}
                  className="rounded-lg border border-gray-300 px-4 py-3 text-base focus:ring-2 focus:ring-blue-400 focus:outline-none bg-gray-50"
                >
                  <option value="">Select a profile</option>
                  {profiles.map(profile => (
                    <option key={profile.id} value={profile.id}>
                      {profile.name} - ${profile.hourly_rate}/hr
                    </option>
                  ))}
                </select>
              </div>
              <div className="flex flex-col col-span-1">
                <label className="block text-sm font-medium text-gray-800 mb-2">Job Title *</label>
                <input
                  type="text"
                  required
                  value={jobData.job_title}
                  onChange={(e) => setJobData({...jobData, job_title: e.target.value})}
                  className="rounded-lg border border-gray-300 px-4 py-3 text-base focus:ring-2 focus:ring-blue-400 focus:outline-none bg-gray-50"
                  placeholder="e.g., React Developer Needed"
                />
              </div>
              <div className="flex flex-col col-span-1 md:col-span-2">
                <label className="block text-sm font-medium text-gray-800 mb-2">Job Description *</label>
                <textarea
                  required
                  value={jobData.job_description}
                  onChange={(e) => setJobData({...jobData, job_description: e.target.value})}
                  className="rounded-lg border border-gray-300 px-4 py-3 text-base focus:ring-2 focus:ring-blue-400 focus:outline-none bg-gray-50 min-h-[100px]"
                  rows="4"
                  placeholder="Paste the job description here..."
                />
              </div>
              <div className="flex flex-col col-span-1 md:col-span-2">
                <label className="block text-sm font-medium text-gray-800 mb-2">Required Skills (comma-separated) *</label>
                <input
                  type="text"
                  required
                  value={jobData.required_skills}
                  onChange={(e) => setJobData({...jobData, required_skills: e.target.value})}
                  className="rounded-lg border border-gray-300 px-4 py-3 text-base focus:ring-2 focus:ring-blue-400 focus:outline-none bg-gray-50"
                  placeholder="e.g., React, JavaScript, Node.js"
                />
              </div>
              <div className="flex flex-col col-span-1">
                <label className="block text-sm font-medium text-gray-800 mb-2">Client Rating (0-5)</label>
                <input
                  type="number"
                  min="0"
                  max="5"
                  step="0.1"
                  value={jobData.client_rating || ''}
                  onChange={(e) => {
                    const value = e.target.value;
                    setJobData({...jobData, client_rating: value === '' ? '' : value});
                  }}
                  className="rounded-lg border border-gray-300 px-4 py-3 text-base focus:ring-2 focus:ring-blue-400 focus:outline-none bg-gray-50"
                  placeholder="4.5"
                />
              </div>
              <div className="flex flex-col col-span-1">
                <label className="block text-sm font-medium text-gray-800 mb-2">Average Pay Rate ($/hr)</label>
                <input
                  type="number"
                  min="0"
                  step="0.01"
                  value={jobData.avg_pay_rate || ''}
                  onChange={(e) => {
                    const value = e.target.value;
                    setJobData({...jobData, avg_pay_rate: value === '' ? '' : value});
                  }}
                  className="rounded-lg border border-gray-300 px-4 py-3 text-base focus:ring-2 focus:ring-blue-400 focus:outline-none bg-gray-50"
                  placeholder="25.00"
                />
              </div>
              <div className="flex flex-col col-span-1 md:col-span-2">
                <label className="block text-sm font-medium text-gray-800 mb-2">Job URL (optional)</label>
                <input
                  type="url"
                  value={jobData.job_url}
                  onChange={(e) => setJobData({...jobData, job_url: e.target.value})}
                  className="rounded-lg border border-gray-300 px-4 py-3 text-base focus:ring-2 focus:ring-blue-400 focus:outline-none bg-gray-50"
                  placeholder="https://www.upwork.com/jobs/~..."
                />
              </div>
              <div className="col-span-1 md:col-span-2 flex flex-col mt-2 items-center">
                <button 
                  type="submit" 
                  className="px-8 py-2 text-base font-semibold rounded-lg bg-gradient-to-r from-blue-500 to-blue-600 text-white shadow-md hover:from-blue-600 hover:to-blue-700 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-400"
                  disabled={loading}
                >
                  Analyze Job
                </button>
              </div>
            </form>
          )}

          {/* Analysis Results & Proposal */}
          <div className="flex-1 space-y-4 w-full">
            {error && (
              <div className="card bg-red-50 border-red-200">
                <div className="text-red-800">
                  <h4 className="font-medium">Error</h4>
                  <p className="text-sm">{error}</p>
                </div>
              </div>
            )}
            {/* Loader Animation while analyzing */}
            {loading && (
              <div className="w-full flex flex-col items-center justify-center py-24 animate-fade-in">
                <svg className="animate-spin h-12 w-12 text-blue-500 mb-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"></path>
                </svg>
                <div className="text-2xl text-blue-500 font-bold tracking-wide animate-pulse mt-2">Analyzing your job match…</div>
              </div>
            )}
            {/* Show analysis result only if not loading and analysisResult exists */}
            {!loading && analysisResult && (
              <div className="bg-white rounded-2xl shadow-material hover:shadow-material-hover border border-gray-100 overflow-hidden hover-lift p-8 mb-4">
                {/* Match Summary */}
                <div className={`flex items-center justify-between rounded-xl p-6 mb-6 ${getMatchLevelDisplay(analysisResult.analysis.match_level, analysisResult.analysis.overall_match_score).bgColor}`}
                     style={{ border: `1.5px solid`, borderColor: getMatchLevelDisplay(analysisResult.analysis.match_level, analysisResult.analysis.overall_match_score).borderColor }}>
                  <div className="flex items-center gap-4">
                    <span className={`text-3xl ${getMatchLevelDisplay(analysisResult.analysis.match_level, analysisResult.analysis.overall_match_score).iconColor}`}>{getMatchLevelDisplay(analysisResult.analysis.match_level, analysisResult.analysis.overall_match_score).icon}</span>
                    <div>
                      <h3 className={`text-2xl font-bold ${getMatchLevelDisplay(analysisResult.analysis.match_level, analysisResult.analysis.overall_match_score).iconColor} mb-1`}>{getMatchLevelDisplay(analysisResult.analysis.match_level, analysisResult.analysis.overall_match_score).title}</h3>
                      <p className="text-gray-700 text-base">{getMatchLevelDisplay(analysisResult.analysis.match_level, analysisResult.analysis.overall_match_score).subtitle}</p>
                    </div>
                  </div>
                  <span className={`text-2xl font-bold ${getMatchLevelDisplay(analysisResult.analysis.match_level, analysisResult.analysis.overall_match_score).scoreColor}`}>{Math.round(analysisResult.analysis.overall_match_score * 100)}%</span>
                </div>
                {/* Analysis Details */}
                <div className="p-4">
                  {/* Match Level Badge */}
                  <div className="flex justify-center mb-4">
                    <span className="inline-flex items-center px-4 py-2 rounded-full text-sm font-medium bg-gray-100 text-gray-800 shadow-sm hover-lift">
                      Match Level: <span className={`ml-2 font-bold ${getMatchLevelDisplay(analysisResult.analysis.match_level, analysisResult.analysis.overall_match_score).scoreColor}`}>{analysisResult.analysis.match_level}</span>
                    </span>
                  </div>
                  {/* Match Score Cards */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                    <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-4 border border-blue-100 hover-lift">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-blue-700">Overall Match</span>
                        <span className={`text-xl font-bold ${getMatchLevelDisplay(analysisResult.analysis.match_level, analysisResult.analysis.overall_match_score).scoreColor}`}>{Math.round(analysisResult.analysis.overall_match_score * 100)}%</span>
                      </div>
                      <div className="w-full bg-blue-200 rounded-full h-2">
                        <div className={`h-2 rounded-full transition-all duration-1000 ease-out ${getMatchLevelDisplay(analysisResult.analysis.match_level, analysisResult.analysis.overall_match_score).scoreColor.replace('text-', 'bg-')}`}
                             style={{ width: `${analysisResult.analysis.overall_match_score * 100}%` }}></div>
                      </div>
                    </div>
                    <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl p-4 border border-purple-100 hover-lift">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-purple-700">Skill Match</span>
                        <span className="text-xl font-bold text-purple-600">{Math.round(analysisResult.analysis.skill_match_score * 100)}%</span>
                      </div>
                      <div className="w-full bg-purple-200 rounded-full h-2">
                        <div className="bg-purple-600 h-2 rounded-full transition-all duration-1000 ease-out" style={{ width: `${analysisResult.analysis.skill_match_score * 100}%` }}></div>
                      </div>
                    </div>
                  </div>
                  {/* Matched Skills */}
                  {analysisResult.analysis.matched_skills?.length > 0 && (
                    <div className="bg-gray-50 rounded-xl p-4 hover-lift mb-4">
                      <h4 className="text-sm font-medium text-gray-700 mb-3">Matched Skills</h4>
                      <div className="flex flex-wrap gap-2">
                        {analysisResult.analysis.matched_skills.map((skill, index) => (
                          <span key={index} className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800 animate-scale-in hover:bg-green-200 transition-colors">{skill}</span>
                        ))}
                      </div>
                    </div>
                  )}
                  {/* Analysis Reasons */}
                  <div className="bg-gray-50 rounded-xl p-4 hover-lift mb-4">
                    <h4 className="font-semibold text-gray-800 mb-4 flex items-center gap-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse-slow"></div>
                      Analysis Results
                    </h4>
                    <div className="space-y-3">
                      {analysisResult.analysis.reasons.map((reason, index) => (
                        <div key={index} className="flex items-start gap-3 p-3 bg-white rounded-lg border border-gray-200 animate-fade-in hover-lift">
                          <div className="w-2 h-2 bg-green-500 rounded-full mt-2 flex-shrink-0"></div>
                          <span className="text-gray-700 text-sm">{reason}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                  {/* Skill Match Visualization */}
                  {analysisResult.analysis.skill_match_score !== undefined && (
                    <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-4 border border-blue-100 hover-lift">
                      <h4 className="font-semibold text-gray-800 mb-4">Skill Match Breakdown</h4>
                      <div className="space-y-4">
                        <div className="flex items-center justify-between">
                          <span className="text-sm font-medium text-gray-700">Skill Compatibility</span>
                          <span className="font-bold text-lg text-blue-600">{Math.round(analysisResult.analysis.skill_match_score * 100)}%</span>
                        </div>
                        <div className="w-full bg-blue-200 rounded-full h-3">
                          <div className="bg-gradient-to-r from-blue-500 to-indigo-600 h-3 rounded-full transition-all duration-1000 ease-out" style={{ width: `${analysisResult.analysis.skill_match_score * 100}%` }}></div>
                        </div>
                        {analysisResult.analysis.matched_skills?.length > 0 && (
                          <p className="text-sm text-gray-600"><strong>Matched skills:</strong> {analysisResult.analysis.matched_skills.join(', ')}</p>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
        {/* Move Generate Proposal button OUTSIDE the card */}
        {!loading && analysisResult && (
          <div className="flex justify-center mt-8 animate-fade-in w-full">
            <button
              onClick={handleGenerateProposal}
              disabled={proposalLoading}
              className={`${getMatchLevelDisplay(analysisResult.analysis.match_level, analysisResult.analysis.overall_match_score).buttonColor} text-white font-medium rounded-full px-8 py-3 shadow-lg hover:shadow-xl transition-all duration-300 flex items-center gap-3 transform hover:scale-105 active:scale-95`}
            >
              {proposalLoading ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  Generating...
                </>
              ) : (
                <>
                  <SparklesIcon className="h-5 w-5" />
                  {getMatchLevelDisplay(analysisResult.analysis.match_level, analysisResult.analysis.overall_match_score).buttonText}
                </>
              )}
            </button>
          </div>
        )}
      </div>
    );
  }

  // Scrape Jobs View
  if (currentView === 'scrape') {
    return (
      <div className="min-h-screen w-full flex flex-col items-center justify-center bg-gradient-to-br from-blue-50 via-white to-indigo-50">
        {/* Back Button styled like manual view */}
        {/* Back Button above the Scrape Jobs card */}
        <div className="w-full max-w-5xl flex items-start mb-6">
          <button
            onClick={resetToLanding}
            className="px-4 py-2 rounded-full bg-gray-100 text-gray-700 font-medium hover:bg-gray-200 transition"
          >
            ← Back
          </button>
        </div>
        <div className="w-full max-w-5xl space-y-8">
          {/* Enhanced Scrape Jobs Card Header */}
          <div className="flex flex-col items-center justify-center">
            <div className="bg-white rounded-2xl shadow-lg border border-green-200 px-10 py-8 flex flex-col items-center w-full max-w-2xl mx-auto mb-8 relative overflow-hidden">
              {/* Decorative Accent */}
              <div className="absolute -top-8 -right-8 w-32 h-32 bg-gradient-to-br from-green-100 to-green-200 rounded-full opacity-30 z-0"></div>
              <div className="relative z-10 flex flex-col items-center">
                <span className="inline-flex items-center justify-center rounded-full bg-green-100 p-4 mb-4">
                  <MagnifyingGlassIcon className="h-8 w-8 text-green-600" />
                </span>
                <h1 className="text-3xl font-bold text-gray-900 mb-2 tracking-tight flex items-center gap-2">
                  Scrape Jobs
                </h1>
                <p className="text-base text-gray-600 text-center max-w-lg mb-6">
                  <span className="font-medium text-green-700">Automatically discover and analyze job opportunities</span> from Upwork in real-time. Use this feature to quickly find jobs that match your skills and generate AI-powered proposals with just a few clicks.
                </p>
            <button
              onClick={handleScrapeCardSimpleScrape}
              className="px-8 py-3 text-lg font-semibold rounded-lg bg-gradient-to-r from-green-500 to-green-600 text-white shadow-md hover:from-green-600 hover:to-green-700 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-green-400"
              disabled={scrapeLoading}
            >
              {scrapeLoading ? 'Scraping…' : 'Scrape Jobs'}
            </button>
              </div>
            </div>
          </div>
          {/* Error */}
          {scrapeError && (
            <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg p-4 text-center mb-6">{scrapeError}</div>
          )}
          {/* Jobs Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {scrapeLoading && Array.from({ length: 4 }).map((_, i) => <CardSkeleton key={i} />)}
            {!scrapeLoading && scrapedJobs.map((job, idx) => {
              const state = jobStates[idx] || {};
              const analysis = state.analysis?.analysis;
              // Extract skills for chips
              const skills = job.required_skills || job.skills || [];
              return (
                <div
                  key={idx}
                  className="relative bg-white rounded-2xl shadow-lg border border-gray-200 p-4 flex flex-col gap-2 transition-shadow duration-300 hover:shadow-2xl group overflow-hidden"
                >
                  {/* Colored Accent Bar */}
                  <div className="absolute left-0 top-0 h-full w-2 bg-gradient-to-b from-green-400 to-emerald-500 rounded-l-2xl" />
                  {/* Icon */}
                  <div className="flex items-center gap-2 mb-1">
                    <span className="inline-flex items-center justify-center rounded-full bg-green-100 p-1">
                      <svg className="h-5 w-5 text-green-600" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M9 7V6a3 3 0 016 0v1m-9 4h12M4 7h16a2 2 0 012 2v8a2 2 0 01-2 2H4a2 2 0 01-2-2V9a2 2 0 012-2z" /></svg>
                    </span>
                    <h2 className="text-lg font-bold text-gray-900 mb-0 leading-tight group-hover:text-green-700 transition-colors">{job.job_title || job.title}</h2>
                  </div>
                  <div className="text-gray-600 text-sm mb-1 line-clamp-2">{job.job_description || job.description}</div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs text-gray-500">Pay Rate:</span>
                    <span className="text-base font-bold text-emerald-600">${job.avg_pay_rate || 'N/A'}</span>
                  </div>
                  {/* Skills Chips */}
                  {skills.length > 0 && (
                    <div className="flex flex-wrap gap-1 mb-1">
                      {skills.map((skill, i) => (
                        <span key={i} className="bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded-full text-xs font-medium shadow-sm hover:bg-emerald-200 transition-colors">{skill}</span>
                      ))}
                    </div>
                  )}
                  {/* View Job Link */}
                  {job.job_url && (
                    <a
                      href={job.job_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center text-green-600 hover:underline hover:text-green-800 text-xs font-medium gap-1 mb-1 transition-colors"
                    >
                      <svg className="h-3 w-3" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M17 8V7a5 5 0 00-10 0v1m12 4v5a2 2 0 01-2 2H7a2 2 0 01-2-2v-5m16-4h-4m0 0V7a7 7 0 10-14 0v1m14 0h-4" /></svg>
                      View Job
                    </a>
                  )}
                  {/* Profile selection */}
                  <div className="flex flex-col gap-1 mt-1">
                    <label className="text-xs font-medium text-gray-700">Select Profile</label>
                    <select
                      value={state.selectedProfile || ''}
                      onChange={e => handleScrapeCardProfileSelect(idx, e.target.value)}
                      className="rounded-lg border border-gray-300 px-2 py-1 text-sm focus:ring-2 focus:ring-green-400 focus:outline-none bg-gray-50"
                    >
                      <option value="">Select a profile</option>
                      {profiles.map(profile => (
                        <option key={profile.id} value={profile.id}>{profile.name} - ${profile.hourly_rate}/hr</option>
                      ))}
                    </select>
                  </div>
                  {/* Analysis result */}
                  {state.loading && <div className="text-green-600 text-xs">Analyzing match…</div>}
                  {state.error && <div className="text-red-600 text-xs">{state.error}</div>}
                  {analysis && (
                    <div className="mt-1 p-2 rounded-lg border text-xs"
                      style={{ borderColor: analysis.match_level === 'EXCELLENT' || analysis.match_level === 'GREAT' ? '#22c55e' : '#f59e42', background: analysis.match_level === 'EXCELLENT' || analysis.match_level === 'GREAT' ? '#f0fdf4' : '#fff7ed' }}
                    >
                      <div className="font-semibold mb-0 flex items-center gap-1">
                        Match: {analysis.match_level} (
                        <AnimatedScore score={analysis.overall_match_score} colorClass={analysis.match_level === 'EXCELLENT' || analysis.match_level === 'GREAT' ? 'text-emerald-600' : 'text-yellow-600'} />
                        )
                      </div>
                      <div className="text-xs text-gray-700 mb-0">{analysis.reasons?.[0]}</div>
                      {analysis.matched_skills?.length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-0.5">
                          {analysis.matched_skills.map((skill, i) => (
                            <span key={i} className="bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded-full text-xs">{skill}</span>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                  {/* Proposal generation */}
                  {analysis && !state.proposal && (
                    <button
                      onClick={() => handleScrapeCardGenerateProposal(idx)}
                      className="mt-1 px-4 py-1.5 rounded-full bg-gradient-to-r from-emerald-500 to-green-600 text-white font-semibold shadow hover:from-emerald-600 hover:to-green-700 transition-all text-xs"
                      disabled={state.proposalLoading}
                    >
                      {state.proposalLoading ? 'Generating…' : 'Generate Proposal'}
                    </button>
                  )}
                  {state.proposalError && <div className="text-red-600 text-xs mt-1">{state.proposalError}</div>}
                  {state.proposal && (
                    <div className="mt-2">
                      <button
                        className="px-4 py-1.5 rounded-full bg-blue-500 text-white font-semibold hover:bg-blue-600 transition text-xs"
                        onClick={() => setScrapeProposalView({ open: true, proposal: state.proposal, job })}
                      >
                        View Proposal
                      </button>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    );
  }

  return null;
};

// 1. Add Google-style animated loader component
const GoogleDotsLoader = () => (
  <div className="flex items-center justify-center gap-1 mt-4 mb-2">
    {[0, 1, 2, 3].map((i) => (
      <span
        key={i}
        className={`inline-block w-3 h-3 rounded-full animate-google-bounce bg-gradient-to-br from-blue-500 to-green-400`}
        style={{ animationDelay: `${i * 0.15}s` }}
      ></span>
    ))}
    <style>{`
      @keyframes google-bounce {
        0%, 80%, 100% { transform: scale(0.8); opacity: 0.7; }
        40% { transform: scale(1.2); opacity: 1; }
      }
      .animate-google-bounce {
        animation: google-bounce 1s infinite both;
      }
    `}</style>
  </div>
);

// 2. Add skeleton loader for cards
const CardSkeleton = () => (
  <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6 animate-pulse flex flex-col gap-4 min-h-[220px]">
    <div className="h-6 w-1/3 bg-gray-200 rounded mb-2"></div>
    <div className="h-4 w-2/3 bg-gray-100 rounded mb-2"></div>
    <div className="h-4 w-1/2 bg-gray-100 rounded mb-2"></div>
    <div className="flex gap-2 mt-2">
      <div className="h-6 w-20 bg-gray-200 rounded-full"></div>
      <div className="h-6 w-16 bg-gray-100 rounded-full"></div>
    </div>
    <div className="h-8 w-1/4 bg-gray-200 rounded-full mt-4"></div>
  </div>
);

// 3. Animated match score (count up)
const AnimatedScore = ({ score, colorClass }) => {
  const [displayScore, setDisplayScore] = useState(0);
  useEffect(() => {
    let start = 0;
    const end = Math.round(score * 100);
    if (end === 0) return;
    const duration = 800;
    const step = Math.max(1, Math.round(end / (duration / 16)));
    const interval = setInterval(() => {
      start += step;
      if (start >= end) {
        setDisplayScore(end);
        clearInterval(interval);
      } else {
        setDisplayScore(start);
      }
    }, 16);
    return () => clearInterval(interval);
  }, [score]);
  return <span className={`text-lg font-bold ${colorClass}`}>{displayScore}%</span>;
};

export default JobAnalysis; 