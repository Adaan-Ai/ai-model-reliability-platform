/**
 * Centralized API Service
 * Interacts with FastAPI backend REST endpoints.
 */

const BASE_URL = '/api';

async function request(endpoint, options = {}) {
  const url = `${BASE_URL}${endpoint}`;
  try {
    const res = await fetch(url, options);
    if (!res.ok) {
      let errorMsg = `HTTP Error ${res.status}`;
      try {
        const errorData = await res.json();
        errorMsg = errorData.detail || errorMsg;
      } catch (e) {
        // fallback to status text
        errorMsg = res.statusText || errorMsg;
      }
      throw new Error(errorMsg);
    }
    // Handle 204 No Content
    if (res.status === 204) return null;
    return await res.json();
  } catch (err) {
    console.error(`API Error on ${endpoint}:`, err);
    throw err;
  }
}

export const api = {
  // System Health
  checkHealth: async () => {
    const response = await fetch('/health');
    if (!response.ok) throw new Error(`Health check failed: HTTP ${response.status}`);
    return response.json();
  },

  // Dashboard
  getDashboardOverview: () => request('/dashboard/overview'),

  // Users & Data Sources
  getUsers: () => request('/users'),
  createUser: (data) => request('/users', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  }),
  getDataSources: () => request('/data-sources'),
  createDataSource: (data) => request('/data-sources', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  }),

  // Datasets
  getDatasets: () => request('/datasets'),
  getDataset: (id) => request(`/datasets/${id}`),
  deleteDataset: (id) => request(`/datasets/${id}`, { method: 'DELETE' }),
  createDataset: (data) => request('/datasets', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  }),
  uploadDataset: (formData) => request('/datasets/upload', {
    method: 'POST',
    body: formData,
  }),
  uploadDatasetVersion: (datasetId, formData) => request(`/datasets/${datasetId}/upload-version`, {
    method: 'POST',
    body: formData,
  }),
  getDatasetVersions: (datasetId) => request(`/datasets/${datasetId}/versions`),
  getDatasetVersionDetail: (versionId) => request(`/dataset-versions/${versionId}`),

  // Data Quality
  getQualityChecks: (datasetId) => request(`/quality-checks${datasetId ? `?dataset_id=${datasetId}` : ''}`),
  createQualityCheck: (data) => request('/quality-checks', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  }),
  runQualityChecksForVersion: (versionId, checkIds = null) => request(`/dataset-versions/${versionId}/run-quality-checks`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ check_ids: checkIds }),
  }),
  getQualityResultsForVersion: (versionId) => request(`/dataset-versions/${versionId}/quality-results`),
  getAllQualityResults: () => request('/quality-results'),

  // AI Models
  getModels: () => request('/models'),
  getModel: (id) => request(`/models/${id}`),
  createModel: (data) => request('/models', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  }),
  createModelVersion: (modelId, data) => request(`/models/${modelId}/versions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  }),
  getModelVersionDetail: (versionId) => request(`/model-versions/${versionId}`),

  // Evaluations
  getEvaluations: (filters = {}) => {
    const params = new URLSearchParams();
    if (filters.modelId) params.append('model_id', filters.modelId);
    if (filters.datasetId) params.append('dataset_id', filters.datasetId);
    if (filters.status) params.append('status_filter', filters.status);
    const query = params.toString() ? `?${params.toString()}` : '';
    return request(`/evaluations${query}`);
  },
  triggerEvaluation: (data) => request('/evaluations', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  }),
  getEvaluationDetail: (id) => request(`/evaluations/${id}`),
  compareEvaluations: (ids) => {
    const params = ids.map(id => `ids=${id}`).join('&');
    return request(`/evaluations/compare?${params}`);
  },

  // Drift
  getDriftRecords: () => request('/drift'),
  getEvaluationDriftDetail: (evaluationId) => request(`/evaluations/${evaluationId}/drift`),

  // Reliability
  getReliabilityScores: () => request('/reliability'),
  getEvaluationReliabilityDetail: (evaluationId) => request(`/evaluations/${evaluationId}/reliability`),
  getReliabilityFormula: () => request('/reliability/formula'),

  // Reports
  getEvaluationReport: (evaluationId) => request(`/reports/evaluations/${evaluationId}`),
  getReportDownloadUrl: (evaluationId, format = 'csv') => `${BASE_URL}/reports/evaluations/${evaluationId}/download?format=${format}`,
};
