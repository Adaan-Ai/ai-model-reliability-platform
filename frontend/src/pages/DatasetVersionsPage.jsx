import React, { useState, useEffect } from 'react';
import {
  Layers,
  Database,
  Calendar,
  FileSpreadsheet,
  Upload,
  AlertTriangle,
  CheckCircle2,
  Table,
  Hash,
  Copy,
  ChevronRight,
  ArrowRight
} from 'lucide-react';
import { api } from '../services/api';

export default function DatasetVersionsPage({ selectedDatasetId, onNavigate }) {
  const [datasets, setDatasets] = useState([]);
  const [currentDatasetId, setCurrentDatasetId] = useState(selectedDatasetId || null);
  const [versions, setVersions] = useState([]);
  const [selectedVersionId, setSelectedVersionId] = useState(null);
  const [versionDetail, setVersionDetail] = useState(null);
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);
  const [error, setError] = useState(null);

  // New version upload modal
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [newVersionTag, setNewVersionTag] = useState('2.0');
  const [newVersionFile, setNewVersionFile] = useState(null);
  const [uploadLoading, setUploadLoading] = useState(false);
  const [uploadError, setUploadError] = useState(null);

  useEffect(() => {
    loadInitial();
  }, []);

  useEffect(() => {
    if (selectedDatasetId) {
      setCurrentDatasetId(selectedDatasetId);
    }
  }, [selectedDatasetId]);

  useEffect(() => {
    if (currentDatasetId) {
      loadVersions(currentDatasetId);
    }
  }, [currentDatasetId]);

  useEffect(() => {
    if (selectedVersionId) {
      loadVersionDetail(selectedVersionId);
    }
  }, [selectedVersionId]);

  const loadInitial = async () => {
    setLoading(true);
    setError(null);
    try {
      const dList = await api.getDatasets();
      setDatasets(dList);
      if (dList.length > 0) {
        const activeId = selectedDatasetId || dList[0].dataset_id;
        setCurrentDatasetId(activeId);
      }
    } catch (err) {
      setError(err.message || 'Failed to load datasets.');
    } finally {
      setLoading(false);
    }
  };

  const loadVersions = async (datasetId) => {
    try {
      const vList = await api.getDatasetVersions(datasetId);
      setVersions(vList);
      if (vList.length > 0) {
        setSelectedVersionId(vList[0].dataset_version_id);
      } else {
        setSelectedVersionId(null);
        setVersionDetail(null);
      }
    } catch (err) {
      console.error('Failed to load dataset versions:', err);
    }
  };

  const loadVersionDetail = async (versionId) => {
    setDetailLoading(true);
    try {
      const det = await api.getDatasetVersionDetail(versionId);
      setVersionDetail(det);
    } catch (err) {
      console.error('Failed to load version detail:', err);
    } finally {
      setDetailLoading(false);
    }
  };

  const handleUploadNewVersion = async (e) => {
    e.preventDefault();
    if (!newVersionFile) {
      setUploadError('Please select a CSV file.');
      return;
    }

    setUploadLoading(true);
    setUploadError(null);

    const formData = new FormData();
    formData.append('file', newVersionFile);
    formData.append('version_number', newVersionTag);

    try {
      const res = await api.uploadDatasetVersion(currentDatasetId, formData);
      setShowUploadModal(false);
      setNewVersionFile(null);
      await loadVersions(currentDatasetId);
      setSelectedVersionId(res.dataset_version_id);
    } catch (err) {
      setUploadError(err.message || 'Failed to upload version.');
    } finally {
      setUploadLoading(false);
    }
  };

  const currentDataset = datasets.find((d) => d.dataset_id === Number(currentDatasetId));

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Dataset Version Lineage</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Immutable snapshots of dataset versions, column types, record counts, and quality health.
          </p>
        </div>

        {/* Dataset Selector Dropdown */}
        <div className="flex items-center space-x-2">
          <label className="text-xs font-semibold text-slate-600">Select Dataset:</label>
          <select
            value={currentDatasetId || ''}
            onChange={(e) => setCurrentDatasetId(Number(e.target.value))}
            className="px-3 py-1.5 bg-white border border-slate-200 rounded-lg text-xs font-medium shadow-xs focus:outline-hidden"
          >
            {datasets.map((d) => (
              <option key={d.dataset_id} value={d.dataset_id}>
                {d.dataset_name} ({d.version_count} v)
              </option>
            ))}
          </select>
        </div>
      </div>

      {loading ? (
        <div className="py-20 flex flex-col items-center justify-center space-y-3">
          <div className="w-8 h-8 border-3 border-brand-200 border-t-brand-600 rounded-full animate-spin" />
          <p className="text-xs text-slate-500">Loading version history...</p>
        </div>
      ) : versions.length === 0 ? (
        <div className="bg-white rounded-xl p-10 border border-slate-200 text-center space-y-3">
          <Layers className="w-10 h-10 text-slate-300 mx-auto" />
          <h3 className="text-sm font-semibold text-slate-800">No versions available</h3>
          <p className="text-xs text-slate-500">Upload a CSV version for this dataset to inspect columns and stats.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column: Version History List */}
          <div className="space-y-4">
            <div className="bg-white rounded-xl border border-slate-200 shadow-xs p-4">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">Versions</h3>
                <button
                  onClick={() => setShowUploadModal(true)}
                  className="text-xs text-brand-600 hover:text-brand-800 font-semibold flex items-center space-x-1"
                >
                  <Upload className="w-3.5 h-3.5" />
                  <span>Upload Next Version</span>
                </button>
              </div>

              <div className="space-y-2">
                {versions.map((v) => {
                  const isSelected = v.dataset_version_id === selectedVersionId;
                  return (
                    <button
                      key={v.dataset_version_id}
                      onClick={() => setSelectedVersionId(v.dataset_version_id)}
                      className={`w-full text-left p-3.5 rounded-xl border transition flex items-center justify-between ${
                        isSelected
                          ? 'border-brand-500 bg-brand-50/50 shadow-xs ring-1 ring-brand-500/30'
                          : 'border-slate-200 hover:border-slate-300 hover:bg-slate-50/50'
                      }`}
                    >
                      <div>
                        <div className="flex items-center space-x-2">
                          <span className={`text-xs font-bold font-mono px-2 py-0.5 rounded-full ${
                            isSelected ? 'bg-brand-600 text-white' : 'bg-slate-100 text-slate-700'
                          }`}>
                            v{v.version_number}
                          </span>
                          <span className="text-xs font-semibold text-slate-800">
                            {Number(v.record_count).toLocaleString()} rows
                          </span>
                        </div>
                        <p className="text-[11px] text-slate-400 mt-1 flex items-center space-x-1">
                          <Calendar className="w-3 h-3" />
                          <span>Created: {v.created_date}</span>
                        </p>
                      </div>
                      <ChevronRight className={`w-4 h-4 ${isSelected ? 'text-brand-600' : 'text-slate-300'}`} />
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Quality Check Status Card */}
            {versionDetail?.quality_summary && (
              <div className="bg-white rounded-xl border border-slate-200 shadow-xs p-4">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-3">
                  Quality Health (v{versionDetail.version_number})
                </h3>
                <div className="flex items-baseline justify-between">
                  <span className="text-2xl font-bold text-slate-900">
                    {versionDetail.quality_summary.average_score}%
                  </span>
                  <span className="text-xs font-semibold text-emerald-600">
                    {versionDetail.quality_summary.passed}/{versionDetail.quality_summary.total_checks} Passed
                  </span>
                </div>
                <div className="mt-3 flex items-center space-x-2 text-[10px]">
                  <span className="px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 font-bold">
                    {versionDetail.quality_summary.passed} Passed
                  </span>
                  {versionDetail.quality_summary.warning > 0 && (
                    <span className="px-2 py-0.5 rounded bg-amber-100 text-amber-800 font-bold">
                      {versionDetail.quality_summary.warning} Warning
                    </span>
                  )}
                  {versionDetail.quality_summary.failed > 0 && (
                    <span className="px-2 py-0.5 rounded bg-rose-100 text-rose-800 font-bold">
                      {versionDetail.quality_summary.failed} Failed
                    </span>
                  )}
                </div>
                <button
                  onClick={() => onNavigate('data-quality')}
                  className="mt-3 w-full py-1.5 text-center text-xs font-medium text-brand-600 bg-brand-50 hover:bg-brand-100 rounded-lg transition"
                >
                  View Full Quality Report
                </button>
              </div>
            )}
          </div>

          {/* Right Column: Detailed Version Profile & Preview */}
          <div className="lg:col-span-2 space-y-6">
            {detailLoading ? (
              <div className="bg-white rounded-xl border border-slate-200 p-12 text-center">
                <div className="w-8 h-8 border-3 border-brand-200 border-t-brand-600 rounded-full animate-spin mx-auto" />
                <p className="text-xs text-slate-500 mt-2">Profiling dataset version CSV...</p>
              </div>
            ) : versionDetail ? (
              <>
                {/* Overview Header */}
                <div className="bg-white rounded-xl border border-slate-200 shadow-xs p-5">
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="flex items-center space-x-2">
                        <span className="text-base font-bold text-slate-900">
                          {versionDetail.dataset_name}
                        </span>
                        <span className="text-xs font-mono font-bold px-2 py-0.5 bg-brand-50 text-brand-700 border border-brand-200 rounded-md">
                          v{versionDetail.version_number}
                        </span>
                      </div>
                      <p className="text-xs text-slate-500 mt-1">
                        Snapshot created on {versionDetail.created_date} • {Number(versionDetail.record_count).toLocaleString()} total records
                      </p>
                    </div>

                    <button
                      onClick={() => onNavigate('evaluations')}
                      className="px-3 py-1.5 bg-brand-600 hover:bg-brand-700 text-white text-xs font-semibold rounded-lg shadow-xs transition"
                    >
                      Evaluate This Version
                    </button>
                  </div>

                  {/* Column Stats Breakdown */}
                  <div className="mt-5 pt-4 border-t border-slate-100 grid grid-cols-2 sm:grid-cols-3 gap-4 text-xs">
                    <div className="bg-slate-50 p-3 rounded-lg border border-slate-100">
                      <span className="text-[11px] text-slate-500 font-medium">Numerical Features</span>
                      <p className="text-lg font-bold text-slate-800 mt-0.5">
                        {versionDetail.numerical_columns?.length || 0}
                      </p>
                      <span className="text-[10px] text-slate-400 font-mono truncate block">
                        {versionDetail.numerical_columns?.join(', ')}
                      </span>
                    </div>

                    <div className="bg-slate-50 p-3 rounded-lg border border-slate-100">
                      <span className="text-[11px] text-slate-500 font-medium">Categorical Features</span>
                      <p className="text-lg font-bold text-slate-800 mt-0.5">
                        {versionDetail.categorical_columns?.length || 0}
                      </p>
                      <span className="text-[10px] text-slate-400 font-mono truncate block">
                        {versionDetail.categorical_columns?.join(', ')}
                      </span>
                    </div>

                    <div className="bg-slate-50 p-3 rounded-lg border border-slate-100 col-span-2 sm:col-span-1">
                      <span className="text-[11px] text-slate-500 font-medium">Total Columns</span>
                      <p className="text-lg font-bold text-slate-800 mt-0.5">
                        {versionDetail.columns?.length || 0}
                      </p>
                      <span className="text-[10px] text-emerald-600 font-medium">Clean CSV Parsed</span>
                    </div>
                  </div>
                </div>

                {/* CSV Live Preview Table */}
                <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
                  <div className="px-5 py-3.5 border-b border-slate-200 flex items-center justify-between">
                    <div>
                      <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center space-x-1.5">
                        <Table className="w-3.5 h-3.5 text-slate-400" />
                        <span>Data Preview (First 10 Records)</span>
                      </h3>
                      <span className="text-[10px] text-slate-400">Directly read from storage using Pandas</span>
                    </div>
                  </div>

                  <div className="overflow-x-auto max-h-96">
                    {versionDetail.preview && versionDetail.preview.length > 0 ? (
                      <table className="w-full text-left text-[11px]">
                        <thead className="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200 sticky top-0">
                          <tr>
                            {versionDetail.columns.map((col) => (
                              <th key={col} className="py-2.5 px-4 font-mono whitespace-nowrap">
                                {col}
                              </th>
                            ))}
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100 font-mono">
                          {versionDetail.preview.map((row, idx) => (
                            <tr key={idx} className="hover:bg-slate-50/70 transition">
                              {versionDetail.columns.map((col) => (
                                <td key={col} className="py-2 px-4 whitespace-nowrap text-slate-700">
                                  {row[col] === null ? (
                                    <span className="text-rose-500 bg-rose-50 px-1 py-0.5 rounded text-[10px]">null</span>
                                  ) : (
                                    String(row[col])
                                  )}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    ) : (
                      <div className="p-8 text-center text-xs text-slate-400">
                        No preview records available.
                      </div>
                    )}
                  </div>
                </div>
              </>
            ) : null}
          </div>
        </div>
      )}

      {/* Upload New Version Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl border border-slate-200">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <h3 className="text-sm font-bold text-slate-900">Upload New Version for {currentDataset?.dataset_name}</h3>
              <button
                onClick={() => setShowUploadModal(false)}
                className="text-slate-400 hover:text-slate-600 text-lg leading-none"
              >
                &times;
              </button>
            </div>

            <form onSubmit={handleUploadNewVersion} className="mt-4 space-y-4 text-xs">
              {uploadError && (
                <div className="p-3 rounded-lg bg-rose-50 border border-rose-200 text-rose-700">
                  {uploadError}
                </div>
              )}

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Version Number *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. 2.0"
                  value={newVersionTag}
                  onChange={(e) => setNewVersionTag(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg font-mono focus:outline-hidden"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Select New Version CSV *</label>
                <div className="border-2 border-dashed border-slate-200 rounded-xl p-4 text-center bg-slate-50/50">
                  <input
                    type="file"
                    accept=".csv"
                    required
                    onChange={(e) => setNewVersionFile(e.target.files[0] || null)}
                    className="w-full text-xs text-slate-500 file:mr-4 file:py-1.5 file:px-3 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-brand-50 file:text-brand-700 hover:file:bg-brand-100"
                  />
                  {newVersionFile && (
                    <p className="mt-2 text-[11px] text-emerald-600 font-medium">
                      {newVersionFile.name} ({(newVersionFile.size / 1024).toFixed(1)} KB)
                    </p>
                  )}
                </div>
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
                  {uploadLoading ? 'Uploading & Profiling...' : 'Upload Version'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
