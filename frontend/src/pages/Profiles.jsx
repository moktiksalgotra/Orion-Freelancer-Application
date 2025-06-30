import { useState, useEffect } from 'react';
import { PlusIcon, PencilIcon, TrashIcon, UserIcon, SparklesIcon, GlobeAltIcon, BriefcaseIcon, PlusCircleIcon, LinkIcon } from '@heroicons/react/24/outline';
import { profilesAPI } from '../services/api';
import profileImage from '../assets/profile.png';

const Profiles = () => {
  const [profiles, setProfiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingProfile, setEditingProfile] = useState(null);
  const [showRelevantExperience, setShowRelevantExperience] = useState(false);
  const [selectedProfileId, setSelectedProfileId] = useState(null);
  const [relevantExperienceProjects, setRelevantExperienceProjects] = useState([]);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    hourly_rate: '',
    skills: '',
    experience_years: '',
    bio: '',
    portfolio_url: '',
    github_url: '',
    linkedin_url: '',
    relevant_experience: '',
    timezone: ''
  });

  // Relevant Experience Form Data
  const [relevantExperienceForm, setRelevantExperienceForm] = useState({
    project_title: '',
    project_description: '',
    project_url: '',
    company_name: '',
    project_type: '',
    technologies_used: '',
    key_achievements: '',
    project_duration: '',
    completion_date: ''
  });
  const [editingProject, setEditingProject] = useState(null);

  useEffect(() => {
    fetchProfiles();
  }, []);

  const fetchProfiles = async () => {
    try {
      setLoading(true);
      const response = await profilesAPI.getAll();
      setProfiles(response.data);
    } catch (error) {
      console.error('Failed to fetch profiles:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchRelevantExperienceProjects = async (profileId) => {
    try {
      const response = await profilesAPI.getRelevantExperienceProjects(profileId);
      setRelevantExperienceProjects(response.data);
    } catch (error) {
      console.error('Failed to fetch relevant experience projects:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const profileData = {
        name: formData.name,
        email: formData.email,
        hourly_rate: parseFloat(formData.hourly_rate),
        experience_years: parseInt(formData.experience_years),
        skills: formData.skills.split(',').map(skill => skill.trim()).filter(Boolean),
        bio: formData.bio,
        portfolio_url: formData.portfolio_url,
        github_url: formData.github_url,
        linkedin_url: formData.linkedin_url,
        relevant_experience: formData.relevant_experience,
        timezone: formData.timezone
      };

      if (editingProfile) {
        await profilesAPI.update(editingProfile.id, profileData);
      } else {
        await profilesAPI.create(profileData);
      }

      setShowForm(false);
      setEditingProfile(null);
      resetForm();
      fetchProfiles();
    } catch (error) {
      console.error('Failed to save profile:', error);
    }
  };

  const handleRelevantExperienceSubmit = async (e) => {
    e.preventDefault();
    try {
      const projectData = {
        project_title: relevantExperienceForm.project_title,
        project_description: relevantExperienceForm.project_description,
        project_url: relevantExperienceForm.project_url,
        company_name: relevantExperienceForm.company_name,
        project_type: relevantExperienceForm.project_type,
        technologies_used: relevantExperienceForm.technologies_used.split(',').map(tech => tech.trim()).filter(Boolean),
        key_achievements: relevantExperienceForm.key_achievements,
        project_duration: relevantExperienceForm.project_duration,
        completion_date: relevantExperienceForm.completion_date
      };

      if (editingProject) {
        await profilesAPI.updateRelevantExperienceProject(selectedProfileId, editingProject.id, projectData);
      } else {
        await profilesAPI.addRelevantExperienceProject(selectedProfileId, projectData);
      }

      setShowRelevantExperience(false);
      setEditingProject(null);
      resetRelevantExperienceForm();
      fetchRelevantExperienceProjects(selectedProfileId);
    } catch (error) {
      console.error('Failed to save relevant experience project:', error);
    }
  };

  const handleEdit = (profile) => {
    setEditingProfile(profile);
    setFormData({
      name: profile.name,
      email: profile.email || '',
      hourly_rate: profile.hourly_rate.toString(),
      skills: Array.isArray(profile.skills) ? profile.skills.join(', ') : '',
      experience_years: profile.experience_years.toString(),
      bio: profile.bio || '',
      portfolio_url: profile.portfolio_url || '',
      github_url: profile.github_url || '',
      linkedin_url: profile.linkedin_url || '',
      relevant_experience: profile.relevant_experience || '',
      timezone: profile.timezone || ''
    });
    setShowForm(true);
  };

  const handleEditRelevantExperience = (project) => {
    setEditingProject(project);
    setRelevantExperienceForm({
      project_title: project.project_title,
      project_description: project.project_description,
      project_url: project.project_url || '',
      company_name: project.company_name || '',
      project_type: project.project_type || '',
      technologies_used: Array.isArray(project.technologies_used) ? project.technologies_used.join(', ') : '',
      key_achievements: project.key_achievements || '',
      project_duration: project.project_duration || '',
      completion_date: project.completion_date || ''
    });
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this profile?')) {
      try {
        await profilesAPI.delete(id);
        fetchProfiles();
      } catch (error) {
        console.error('Failed to delete profile:', error);
      }
    }
  };

  const handleDeleteRelevantExperience = async (projectId) => {
    if (window.confirm('Are you sure you want to delete this project?')) {
      try {
        await profilesAPI.deleteRelevantExperienceProject(selectedProfileId, projectId);
        fetchRelevantExperienceProjects(selectedProfileId);
      } catch (error) {
        console.error('Failed to delete relevant experience project:', error);
      }
    }
  };

  const openRelevantExperience = (profileId) => {
    setSelectedProfileId(profileId);
    setShowRelevantExperience(true);
    fetchRelevantExperienceProjects(profileId);
  };

  const resetForm = () => {
    setFormData({
      name: '',
      email: '',
      hourly_rate: '',
      skills: '',
      experience_years: '',
      bio: '',
      portfolio_url: '',
      github_url: '',
      linkedin_url: '',
      relevant_experience: '',
      timezone: ''
    });
  };

  const resetRelevantExperienceForm = () => {
    setRelevantExperienceForm({
      project_title: '',
      project_description: '',
      project_url: '',
      company_name: '',
      project_type: '',
      technologies_used: '',
      key_achievements: '',
      project_duration: '',
      completion_date: ''
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto space-y-12">
      {/* Hero Header */}
      <div className="text-center mb-8">
        <div className="inline-flex items-center justify-center rounded-full bg-primary-100 p-3 mb-4">
          <UserIcon className="h-8 w-8 text-primary-600" />
        </div>
        <h1 className="text-4xl font-bold text-gray-900 tracking-tight">Freelancer Profiles</h1>
        <p className="mt-3 text-xl text-gray-600 max-w-3xl mx-auto">
          Manage your freelance identity, showcase your skills, and optimize your Upwork presence with structured project experience.
        </p>
      </div>

      {/* Features Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center mb-12 bg-white rounded-2xl shadow-lg p-8">
        {/* Feature cards left */}
        <div className="flex flex-col gap-6">
          <div className="flex items-start gap-4">
            <div className="p-2 rounded-full bg-blue-100">
              <SparklesIcon className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <h3 className="font-medium text-gray-900 text-lg mb-1">Structured Project Experience</h3>
              <p className="text-gray-600">Add detailed project experience with links, technologies, and achievements for better proposal generation.</p>
            </div>
          </div>
          <div className="flex items-start gap-4">
            <div className="p-2 rounded-full bg-green-100">
              <LinkIcon className="h-6 w-6 text-green-600" />
            </div>
            <div>
              <h3 className="font-medium text-gray-900 text-lg mb-1">Professional Project Links</h3>
              <p className="text-gray-600">Include project URLs, GitHub repositories, and live demos to showcase your work professionally.</p>
            </div>
          </div>
          <div className="flex items-start gap-4">
            <div className="p-2 rounded-full bg-purple-100">
              <BriefcaseIcon className="h-6 w-6 text-purple-600" />
            </div>
            <div>
              <h3 className="font-medium text-gray-900 text-lg mb-1">AI-Enhanced Proposals</h3>
              <p className="text-gray-600">Generate proposals that automatically include your relevant project experience with professional formatting.</p>
            </div>
          </div>
        </div>
        {/* Profile image right */}
        <div className="flex justify-center md:justify-end items-center">
          <img src={profileImage} alt="Profile Illustration" className="w-80 h-auto rounded-xl shadow-lg" />
        </div>
      </div>

      {/* Header + Add Button */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-2xl font-semibold text-gray-900">Your Profiles</h2>
          <p className="mt-1 text-base text-gray-600">All your freelancer profiles at a glance</p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="flex items-center gap-2 px-6 py-3 bg-primary-600 text-white font-medium rounded-full shadow-md hover:bg-primary-700 transition-colors"
        >
          <PlusCircleIcon className="h-5 w-5" />
          Add Profile
        </button>
      </div>

      {/* Profile Form */}
      {showForm && (
        <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
          <h3 className="text-xl font-medium text-gray-900 mb-6">
            {editingProfile ? 'Edit Profile' : 'Add New Profile'}
          </h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Name *
                </label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  className="input-field"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email
                </label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                  className="input-field"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Hourly Rate ($) *
                </label>
                <input
                  type="number"
                  required
                  min="0"
                  step="0.01"
                  value={formData.hourly_rate}
                  onChange={(e) => setFormData({...formData, hourly_rate: e.target.value})}
                  className="input-field"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Experience (Years) *
                </label>
                <input
                  type="number"
                  required
                  min="0"
                  value={formData.experience_years}
                  onChange={(e) => setFormData({...formData, experience_years: e.target.value})}
                  className="input-field"
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Skills (comma-separated) *
              </label>
              <input
                type="text"
                required
                value={formData.skills}
                onChange={(e) => setFormData({...formData, skills: e.target.value})}
                className="input-field"
                placeholder="React, Node.js, Python, etc."
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Bio
              </label>
              <textarea
                value={formData.bio}
                onChange={(e) => setFormData({...formData, bio: e.target.value})}
                className="textarea-field"
                rows="3"
              />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Portfolio URL
                </label>
                <input
                  type="url"
                  value={formData.portfolio_url}
                  onChange={(e) => setFormData({...formData, portfolio_url: e.target.value})}
                  className="input-field"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  GitHub URL
                </label>
                <input
                  type="url"
                  value={formData.github_url}
                  onChange={(e) => setFormData({...formData, github_url: e.target.value})}
                  className="input-field"
                  placeholder="https://github.com/username"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  LinkedIn URL
                </label>
                <input
                  type="url"
                  value={formData.linkedin_url}
                  onChange={(e) => setFormData({...formData, linkedin_url: e.target.value})}
                  className="input-field"
                  placeholder="https://linkedin.com/in/username"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Timezone
                </label>
                <input
                  type="text"
                  value={formData.timezone}
                  onChange={(e) => setFormData({...formData, timezone: e.target.value})}
                  className="input-field"
                  placeholder="UTC-5, EST, etc."
                />
              </div>
            </div>
            <div className="flex justify-end space-x-3">
              <button
                type="button"
                onClick={() => {
                  setShowForm(false);
                  setEditingProfile(null);
                  resetForm();
                }}
                className="btn-secondary"
              >
                Cancel
              </button>
              <button type="submit" className="btn-primary">
                {editingProfile ? 'Update Profile' : 'Create Profile'}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Relevant Experience Modal */}
      {showRelevantExperience && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-lg p-8 max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-medium text-gray-900">
                Manage Relevant Experience Projects
              </h3>
              <button
                onClick={() => {
                  setShowRelevantExperience(false);
                  setSelectedProfileId(null);
                  setEditingProject(null);
                  resetRelevantExperienceForm();
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Add/Edit Project Form */}
            <form onSubmit={handleRelevantExperienceSubmit} className="mb-8 bg-gray-50 rounded-lg p-6">
              <h4 className="text-lg font-medium text-gray-900 mb-4">
                {editingProject ? 'Edit Project' : 'Add New Project'}
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Project Title *
                  </label>
                  <input
                    type="text"
                    required
                    value={relevantExperienceForm.project_title}
                    onChange={(e) => setRelevantExperienceForm({...relevantExperienceForm, project_title: e.target.value})}
                    className="input-field"
                    placeholder="e.g., E-commerce Platform"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Company Name
                  </label>
                  <input
                    type="text"
                    value={relevantExperienceForm.company_name}
                    onChange={(e) => setRelevantExperienceForm({...relevantExperienceForm, company_name: e.target.value})}
                    className="input-field"
                    placeholder="e.g., TechCorp Inc."
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Project URL
                  </label>
                  <input
                    type="url"
                    value={relevantExperienceForm.project_url}
                    onChange={(e) => setRelevantExperienceForm({...relevantExperienceForm, project_url: e.target.value})}
                    className="input-field"
                    placeholder="https://project-demo.com"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Project Type
                  </label>
                  <input
                    type="text"
                    value={relevantExperienceForm.project_type}
                    onChange={(e) => setRelevantExperienceForm({...relevantExperienceForm, project_type: e.target.value})}
                    className="input-field"
                    placeholder="e.g., Web Application, Mobile App"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Technologies Used
                  </label>
                  <input
                    type="text"
                    value={relevantExperienceForm.technologies_used}
                    onChange={(e) => setRelevantExperienceForm({...relevantExperienceForm, technologies_used: e.target.value})}
                    className="input-field"
                    placeholder="React, Node.js, MongoDB (comma-separated)"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Project Duration
                  </label>
                  <input
                    type="text"
                    value={relevantExperienceForm.project_duration}
                    onChange={(e) => setRelevantExperienceForm({...relevantExperienceForm, project_duration: e.target.value})}
                    className="input-field"
                    placeholder="e.g., 3 months, 6 weeks"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Completion Date
                  </label>
                  <input
                    type="date"
                    value={relevantExperienceForm.completion_date}
                    onChange={(e) => setRelevantExperienceForm({...relevantExperienceForm, completion_date: e.target.value})}
                    className="input-field"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Project Description *
                </label>
                <textarea
                  required
                  value={relevantExperienceForm.project_description}
                  onChange={(e) => setRelevantExperienceForm({...relevantExperienceForm, project_description: e.target.value})}
                  className="textarea-field"
                  rows="4"
                  placeholder="Describe the project, your role, and key features implemented..."
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Key Achievements
                </label>
                <textarea
                  value={relevantExperienceForm.key_achievements}
                  onChange={(e) => setRelevantExperienceForm({...relevantExperienceForm, key_achievements: e.target.value})}
                  className="textarea-field"
                  rows="3"
                  placeholder="Highlight specific achievements, metrics, or outcomes..."
                />
              </div>
              <div className="flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => {
                    setEditingProject(null);
                    resetRelevantExperienceForm();
                  }}
                  className="btn-secondary"
                >
                  Cancel
                </button>
                <button type="submit" className="btn-primary">
                  {editingProject ? 'Update Project' : 'Add Project'}
                </button>
              </div>
            </form>

            {/* Projects List */}
            <div>
              <h4 className="text-lg font-medium text-gray-900 mb-4">Your Projects</h4>
              {relevantExperienceProjects.length === 0 ? (
                <div className="text-center py-8 bg-gray-50 rounded-lg">
                  <p className="text-gray-600">No projects added yet. Add your first project to showcase your experience.</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {relevantExperienceProjects.map((project) => (
                    <div key={project.id} className="bg-white border border-gray-200 rounded-lg p-4">
                      <div className="flex justify-between items-start mb-3">
                        <div className="flex-1">
                          <h5 className="font-medium text-gray-900">{project.project_title}</h5>
                          {project.company_name && (
                            <p className="text-sm text-gray-600">{project.company_name}</p>
                          )}
                        </div>
                        <div className="flex space-x-2">
                          <button
                            onClick={() => handleEditRelevantExperience(project)}
                            className="p-1 text-gray-400 hover:text-primary-600"
                          >
                            <PencilIcon className="h-4 w-4" />
                          </button>
                          <button
                            onClick={() => handleDeleteRelevantExperience(project.id)}
                            className="p-1 text-gray-400 hover:text-red-600"
                          >
                            <TrashIcon className="h-4 w-4" />
                          </button>
                        </div>
                      </div>
                      <p className="text-sm text-gray-700 mb-3">{project.project_description}</p>
                      <div className="flex flex-wrap gap-2 mb-3">
                        {project.technologies_used && project.technologies_used.map((tech, index) => (
                          <span
                            key={index}
                            className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-50 text-blue-700"
                          >
                            {tech}
                          </span>
                        ))}
                      </div>
                      {project.project_url && (
                        <a
                          href={project.project_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-1 text-sm text-primary-600 hover:text-primary-700"
                        >
                          <LinkIcon className="h-4 w-4" />
                          View Project
                        </a>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Profiles List */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-8">
        {profiles.map((profile) => (
          <div key={profile.id} className="bg-white rounded-xl p-6 flex flex-col gap-4 shadow-lg hover:shadow-xl transition-all duration-300 border border-gray-100">
            <div className="flex justify-between items-start">
              <div className="flex-1">
                <h3 className="text-lg font-medium text-gray-900">{profile.name}</h3>
                <p className="text-sm text-gray-500 mt-0.5">{profile.email}</p>
              </div>
              <div className="flex space-x-1">
                <button
                  onClick={() => handleEdit(profile)}
                  className="p-2 text-gray-400 hover:text-primary-600 rounded-full hover:bg-gray-100"
                >
                  <PencilIcon className="h-4 w-4" />
                </button>
                <button
                  onClick={() => handleDelete(profile.id)}
                  className="p-2 text-gray-400 hover:text-danger-600 rounded-full hover:bg-gray-100"
                >
                  <TrashIcon className="h-4 w-4" />
                </button>
              </div>
            </div>
            <div className="mt-2 pt-4 border-t border-gray-100 space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Hourly Rate</span>
                <span className="text-base font-medium text-primary-700">${profile.hourly_rate}/hr</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Experience</span>
                <span className="text-base font-medium">{profile.experience_years} years</span>
              </div>
            </div>
            <div className="mt-3">
              <span className="text-sm text-gray-600 block mb-2">Skills</span>
              <div className="flex flex-wrap gap-2">
                {Array.isArray(profile.skills) && profile.skills.map((skill, index) => (
                  <span
                    key={index}
                    className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-50 text-blue-700"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>
            {profile.bio && (
              <div className="mt-3">
                <span className="text-sm text-gray-600 block mb-1">Bio</span>
                <p className="text-sm text-gray-700 line-clamp-2">{profile.bio}</p>
              </div>
            )}
            {(profile.github_url || profile.linkedin_url) && (
              <div className="mt-3">
                <span className="text-sm text-gray-600 block mb-1">Links</span>
                <div className="flex flex-wrap gap-2">
                  {profile.github_url && (
                    <a
                      href={profile.github_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-gray-100 text-gray-700 hover:bg-gray-200"
                    >
                      GitHub
                    </a>
                  )}
                  {profile.linkedin_url && (
                    <a
                      href={profile.linkedin_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-blue-100 text-blue-700 hover:bg-blue-200"
                    >
                      LinkedIn
                    </a>
                  )}
                </div>
              </div>
            )}
            <div className="mt-4 pt-4 border-t border-gray-100">
              <button
                onClick={() => openRelevantExperience(profile.id)}
                className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-primary-50 text-primary-700 font-medium rounded-lg hover:bg-primary-100 transition-colors"
              >
                <LinkIcon className="h-4 w-4" />
                Manage Projects
              </button>
              </div>
          </div>
        ))}
      </div>

      {profiles.length === 0 && (
        <div className="text-center py-16 bg-gray-50 rounded-xl border border-gray-200">
          <UserIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600 text-lg">No profiles found. Create your first profile to get started.</p>
          <button 
            onClick={() => setShowForm(true)}
            className="mt-4 inline-flex items-center gap-2 px-6 py-2 bg-primary-600 text-white font-medium rounded-full shadow-md hover:bg-primary-700 transition-colors"
          >
            <PlusCircleIcon className="h-5 w-5" />
            Create Profile
          </button>
        </div>
      )}
    </div>
  );
};

export default Profiles; 