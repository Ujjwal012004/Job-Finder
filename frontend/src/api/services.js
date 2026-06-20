import apiClient from './client';

export const authService = {
  login: async (email, password) => {
    const response = await apiClient.post('/auth/login', { email, password });
    return response.data;
  },
  register: async (userData) => {
    const response = await apiClient.post('/auth/register', userData);
    return response.data;
  },
};

export const userService = {
  getProfile: async () => {
    const response = await apiClient.get('/users/me');
    return response.data;
  },
};

export const jobService = {
  searchJobs: async (params) => {
    // We use the advanced search endpoint which handles relevance, pagination, etc.
    const response = await apiClient.get('/search/jobs', { params });
    return response.data;
  },
  getJob: async (jobId) => {
    const response = await apiClient.get(`/jobs/${jobId}`);
    return response.data;
  },
  getRecommendations: async () => {
    const response = await apiClient.get('/search/recommendations');
    return response.data;
  },
};

export const applicationService = {
  apply: async (jobId, coverLetter) => {
    const response = await apiClient.post('/applications', {
      job_id: jobId,
      cover_letter: coverLetter,
    });
    return response.data;
  },
  getMyApplications: async () => {
    const response = await apiClient.get('/applications');
    return response.data;
  },
};

export const dashboardService = {
  getDashboard: async () => {
    const response = await apiClient.get('/dashboard/');
    return response.data;
  },
};
