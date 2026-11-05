import React, { useState, useEffect } from 'react';
import {
  Database,
  Search,
  Plus,
  Upload,
  Layers,
  User,
  Calendar,
  AlertCircle,
  FileSpreadsheet,
  CheckCircle2,
  ExternalLink,
  ChevronRight,
  Filter
} from 'lucide-react';
import { api } from '../services/api';

export default function DatasetsPage({ onSelectDataset, onNavigate }) {
  const [datasets, setDatasets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  
  // Upload modal state
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [users, setUsers] = useState([]);
  const [sources, setSources] = useState([]);
  const [uploadLoading, setUploadLoading] = useState(false);
  const [uploadError, setUploadError] = useState(null);
  const [uploadSuccess, setUploadSuccess] = useState(null);

  // Form fields
  const [formName, setFormName] = useState('');
  const [formDesc, setFormDesc] = useState('');
  const [formSourceId, setFormSourceId] = useState('');
  const [formOwnerId, setFormOwnerId] = useState('');
  const [formVersion, setFormVersion] = useState('1.0');
  const [selectedFile, setSelectedFile] = useState(null);

  useEffect(() => {
    loadDatasets();
    loadMeta();
  }, []);

  const loadDatasets = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.getDatasets();
      setDatasets(res);
    } catch (err) {
      setError(err.message || 'Failed to load datasets.');
    } finally {
      setLoading(false);
    }
  };

  const loadMeta = async () => {
    try {
      const [uRes, sRes] = await Promise.all([api.getUsers(), api.getDataSources()]);
      setUsers(uRes);
      setSources(sRes);
      if (uRes.length > 0) setFormOwnerId(uRes[0].user_id);
      if (sRes.length > 0) setFormSourceId(sRes[0].source_id);
    } catch (e) {
      console.error('Failed to load user or source metadata:', e);
    }
  };

  const handleUploadSubmit = async (e) => {
    e.preventDefault();
    if (!selectedFile) {
      setUploadError('Please select a CSV file.');
      return;
    }

    setUploadLoading(true);
    setUploadError(null);
    setUploadSuccess(null);

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('dataset_name', formName);
    formData.append('description', formDesc);
    formData.append('source_id', formSourceId);
    formData.append('owner_id', formOwnerId);
    formData.append('version_number', formVersion);

    try {
      const res = await api.uploadDataset(formData);
      setUploadSuccess(`Successfully created dataset '${res.dataset_name}' with version ${formVersion} and executed initial quality checks!`);
      // Reset form
      setFormName('');
      setFormDesc('');
      setSelectedFile(null);
      loadDatasets();
      setTimeout(() => {
        setShowUploadModal(false);
        setUploadSuccess(null);
      }, 2000);
    } catch (err) {
      setUploadError(err.message || 'CSV upload failed.');
    } finally {
      setUploadLoading(false);
    }
  };

  const filteredDatasets = datasets.filter((d) =>
    d.dataset_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (d.description && d.description.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header & Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Dataset Catalog</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Registered business datasets, upstream sources, and version snapshots stored in MySQL.
          </p>
        </div>
        <button
          onClick={() => setShowUploadModal(true)}
          className="inline-flex items-center space-x-1.5 px-3.5 py-2 bg-brand-600 hover:bg-brand-700 text-white rounded-lg text-xs font-semibold shadow-xs transition self-start sm:self-auto"
        >
          <Upload className="w-3.5 h-3.5" />
          <span>Upload New Dataset (CSV)</span>
        </button>
      </div>

      {/* Search & Filter Bar */}
      <div className="bg-white p-3.5 rounded-xl border border-slate-200 shadow-xs flex items-center justify-between gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search datasets by name or description..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-4 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs focus:outline-hidden focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition"
          />
        </div>
        <span className="text-xs text-slate-500 font-medium">
          Showing {filteredDatasets.length} of {datasets.length} datasets
        </span>
      </div>

      {/* Dataset Grid */}
      {loading ? (
        <div className="py-20 flex flex-col items-center justify-center space-y-3">
          <div className="w-8 h-8 border-3 border-brand-200 border-t-brand-600 rounded-full animate-spin" />
          <p className="text-xs text-slate-500">Loading datasets from MySQL...</p>
        </div>
      ) : error ? (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-xl text-rose-800 text-xs">
          {error}
        </div>
      ) : filteredDatasets.length === 0 ? (
        <div className="bg-white rounded-xl p-12 border border-slate-200 text-center space-y-3">
          <div className="w-12 h-12 rounded-full bg-slate-100 flex items-center justify-center mx-auto text-slate-400">
            <Database className="w-6 h-6" />
          </div>
          <h3 className="text-sm font-semibold text-slate-800">No datasets found</h3>
          <p className="text-xs text-slate-500 max-w-md mx-auto">
            {searchTerm ? 'No datasets match your search query.' : 'No datasets registered in the database yet. Click below to upload your first CSV file.'}
          </p>
          <button
            onClick={() => setShowUploadModal(true)}
            className="px-3 py-1.5 bg-brand-600 text-white rounded-lg text-xs font-medium hover:bg-brand-700"
          >
            Upload CSV
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filteredDatasets.map((dataset) => (
            <div
              key={dataset.dataset_id}
              className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs hover:border-slate-300 hover:shadow-md transition flex flex-col justify-between"
            >
              <div>
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center space-x-2.5">
                    <div className="p-2 rounded-lg bg-blue-50 text-brand-600">
                      <FileSpreadsheet className="w-5 h-5" />
                    </div>
                    <div>
                      <h3 className="text-sm font-bold text-slate-900 hover:text-brand-600 transition">
                        {dataset.dataset_name}
                      </h3>
                      <span className="text-[10px] text-slate-400 font-mono">ID: #{dataset.dataset_id}</span>
                    </div>
                  </div>
                  {dataset.latest_version && (
                    <span className="px-2 py-0.5 rounded-full bg-slate-100 border border-slate-200 text-slate-700 font-mono text-[10px] font-semibold">
                      v{dataset.latest_version}
                    </span>
                  )}
                </div>

                <p className="text-xs text-slate-600 mt-3 line-clamp-2 leading-relaxed">
                  {dataset.description || 'No description provided.'}
                </p>

                <div className="mt-4 pt-3 border-t border-slate-100 grid grid-cols-2 gap-2 text-[11px] text-slate-500">
                  <div className="flex items-center space-x-1.5">
                    <User className="w-3.5 h-3.5 text-slate-400" />
                    <span className="truncate">{dataset.owner?.name || 'Owner ID ' + dataset.owner_id}</span>
                  </div>
                  <div className="flex items-center space-x-1.5">
                    <Database className="w-3.5 h-3.5 text-slate-400" />
                    <span className="truncate">{dataset.source?.source_name || 'Source ID ' + dataset.source_id}</span>
                  </div>
                  <div className="flex items-center space-x-1.5">
                    <Layers className="w-3.5 h-3.5 text-slate-400" />
                    <span>{dataset.version_count} total {dataset.version_count === 1 ? 'version' : 'versions'}</span>
                  </div>
                  <div className="flex items-center space-x-1.5">
                    <Calendar className="w-3.5 h-3.5 text-slate-400" />
                    <span>{dataset.created_date}</span>
                  </div>
                </div>
              </div>

              <div className="mt-5 pt-3 border-t border-slate-100 flex items-center justify-between">
                <button
                  onClick={() => {
                    if (onSelectDataset) onSelectDataset(dataset.dataset_id);
                    onNavigate('dataset-versions');
                  }}
                  className="text-xs font-semibold text-brand-600 hover:text-brand-800 flex items-center space-x-1"
                >
                  <span>Inspect Versions</span>
                  <ChevronRight className="w-3.5 h-3.5" />
                </button>
                <button
                  onClick={() => {
                    if (onSelectDataset) onSelectDataset(dataset.dataset_id);
                    onNavigate('data-quality');
                  }}
                  className="text-xs font-medium text-slate-500 hover:text-slate-800"
                >
                  Quality Checks
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Upload CSV Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-200">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div className="flex items-center space-x-2">
                <div className="p-1.5 rounded-lg bg-brand-50 text-brand-600">
                  <Upload className="w-4 h-4" />
                </div>
                <h3 className="text-sm font-bold text-slate-900">Register New Dataset with CSV</h3>
              </div>
              <button
                onClick={() => setShowUploadModal(false)}
                className="text-slate-400 hover:text-slate-600 text-lg leading-none"
              >
                &times;
              </button>
            </div>

            <form onSubmit={handleUploadSubmit} className="mt-4 space-y-4 text-xs">
              {uploadError && (
                <div className="p-3 rounded-lg bg-rose-50 border border-rose-200 text-rose-700 flex items-start space-x-2">
                  <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
                  <span>{uploadError}</span>
                </div>
              )}

              {uploadSuccess && (
                <div className="p-3 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-700 flex items-start space-x-2">
                  <CheckCircle2 className="w-4 h-4 shrink-0 mt-0.5" />
                  <span>{uploadSuccess}</span>
                </div>
              )}

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Dataset Name *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Credit Card Fraud Stream 2026"
                  value={formName}
                  onChange={(e) => setFormName(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Description</label>
                <textarea
                  rows={2}
                  placeholder="Briefly describe schema, features, and domain purpose..."
                  value={formDesc}
                  onChange={(e) => setFormDesc(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Data Source *</label>
                  <select
                    value={formSourceId}
                    onChange={(e) => setFormSourceId(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg focus:outline-hidden"
                  >
                    {sources.map((s) => (
                      <option key={s.source_id} value={s.source_id}>
                        {s.source_name} ({s.source_type})
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Owner (User) *</label>
                  <select
                    value={formOwnerId}
                    onChange={(e) => setFormOwnerId(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg focus:outline-hidden"
                  >
                    {users.map((u) => (
                      <option key={u.user_id} value={u.user_id}>
                        {u.name} ({u.role})
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Initial Version Tag</label>
                <input
                  type="text"
                  required
                  placeholder="1.0"
                  value={formVersion}
                  onChange={(e) => setFormVersion(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg font-mono focus:outline-hidden"
                />
              </div>

              {/* File Input */}
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Select CSV File *</label>
                <div className="border-2 border-dashed border-slate-200 rounded-xl p-4 text-center hover:border-brand-500 transition cursor-pointer bg-slate-50/50">
                  <input
                    type="file"
                    accept=".csv"
                    required
                    onChange={(e) => setSelectedFile(e.target.files[0] || null)}
                    className="w-full text-xs text-slate-500 file:mr-4 file:py-1.5 file:px-3 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-brand-50 file:text-brand-700 hover:file:bg-brand-100"
                  />
                  {selectedFile && (
                    <p className="mt-2 text-[11px] text-emerald-600 font-medium">
                      Selected: {selectedFile.name} ({(selectedFile.size / 1024).toFixed(1)} KB)
                    </p>
                  )}
                </div>
                <p className="text-[10px] text-slate-400 mt-1">
                  File will be profiled by Pandas, saved safely outside public directory, and checked against data quality thresholds.
                </p>
              </div>

              <div className="pt-3 border-t border-slate-100 flex items-center justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setShowUploadModal(false)}
                  className="px-3.5 py-1.5 rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50 font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={uploadLoading}
                  className="px-4 py-1.5 bg-brand-600 hover:bg-brand-700 text-white rounded-lg font-semibold shadow-xs disabled:opacity-50"
                >
                  {uploadLoading ? 'Uploading & Profiling...' : 'Upload & Create Version 1.0'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
