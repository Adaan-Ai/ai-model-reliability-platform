import React, { useState, useEffect } from 'react';
import {
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Play,
  Plus,
  Info,
  Layers,
  Database,
  Calendar,
  ShieldAlert,
  ArrowRight
} from 'lucide-react';
import { api } from '../services/api';

export default function DataQualityPage() {
  const [datasets, setDatasets] = useState([]);
  const [selectedDatasetId, setSelectedDatasetId] = useState(null);
  const [versions, setVersions] = useState([]);
  const [selectedVersionId, setSelectedVersionId] = useState(null);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [executing, setExecuting] = useState(false);
  const [error, setError] = useState(null);

  // New check modal
  const [showAddModal, setShowAddModal] = useState(false);
  const [newCheckName, setNewCheckName] = useState('');
  const [newCheckType, setNewCheckType] = useState('missing_values');
  const [newThreshold, setNewThreshold] = useState(90.0);

  useEffect(() => {
    loadDatasets();
  }, []);

  useEffect(() => {
    if (selectedDatasetId) {
      loadVersions(selectedDatasetId);
    }
  }, [selectedDatasetId]);

  useEffect(() => {
    if (selectedVersionId) {
      loadResults(selectedVersionId);
    }
  }, [selectedVersionId]);

  const loadDatasets = async () => {
    setLoading(true);
    try {
      const dList = await api.getDatasets();
      setDatasets(dList);
      if (dList.length > 0) {
        setSelectedDatasetId(dList[0].dataset_id);
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
        setResults([]);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const loadResults = async (versionId) => {
    try {
      const rList = await api.getQualityResultsForVersion(versionId);
      setResults(rList);
    } catch (err) {
      console.error(err);
    }
  };

  const handleRunChecks = async () => {
    if (!selectedVersionId) return;
    setExecuting(true);
    try {
      const res = await api.runQualityChecksForVersion(selectedVersionId);
      setResults(res);
    } catch (err) {
      alert(`Execution failed: ${err.message}`);
    } finally {
      setExecuting(false);
    }
  };

  const handleCreateCheck = async (e) => {
    e.preventDefault();
    try {
      await api.createQualityCheck({
        dataset_id: selectedDatasetId,
        check_name: newCheckName,
        check_type: newCheckType,
        threshold: Number(newThreshold),
      });
      setShowAddModal(false);
      setNewCheckName('');
      // Run checks to immediately test new check
      handleRunChecks();
    } catch (err) {
      alert(`Failed to add check: ${err.message}`);
    }
  };

  const getStatusBadge = (status) => {
    if (status === 'PASSED') {
      return (
        <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-200">
          <CheckCircle2 className="w-3 h-3 text-emerald-600" />
          <span>PASSED</span>
        </span>
      );
    } else if (status === 'WARNING') {
      return (
        <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-800 border border-amber-200">
          <AlertTriangle className="w-3 h-3 text-amber-600" />
          <span>WARNING</span>
        </span>
      );
    }
    return (
      <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-rose-100 text-rose-800 border border-rose-200">
        <XCircle className="w-3 h-3 text-rose-600" />
        <span>FAILED</span>
      </span>
    );
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Data Quality Monitoring</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Deterministic validation against dataset versions with threshold scoring (Core Entities 5 & 6).
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={() => setShowAddModal(true)}
            className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-semibold border border-slate-200 transition"
          >
            + Add Quality Check
          </button>
          <button
            onClick={handleRunChecks}
            disabled={executing || !selectedVersionId}
            className="inline-flex items-center space-x-1.5 px-3.5 py-1.5 bg-brand-600 hover:bg-brand-700 text-white rounded-lg text-xs font-semibold shadow-xs transition disabled:opacity-50"
          >
            <Play className="w-3 h-3" />
            <span>{executing ? 'Executing Checks...' : 'Run Checks Against Version'}</span>
          </button>
        </div>
      </div>

      {/* Selectors Bar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs flex flex-wrap items-center gap-4">
        <div className="flex items-center space-x-2">
          <label className="text-xs font-semibold text-slate-600">Dataset:</label>
          <select
            value={selectedDatasetId || ''}
            onChange={(e) => setSelectedDatasetId(Number(e.target.value))}
            className="px-3 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs font-medium focus:outline-hidden"
          >
            {datasets.map((d) => (
              <option key={d.dataset_id} value={d.dataset_id}>
                {d.dataset_name}
              </option>
            ))}
          </select>
        </div>

        <div className="flex items-center space-x-2">
          <label className="text-xs font-semibold text-slate-600">Target Version:</label>
          <select
            value={selectedVersionId || ''}
            onChange={(e) => setSelectedVersionId(Number(e.target.value))}
            className="px-3 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs font-mono font-medium focus:outline-hidden"
          >
            {versions.map((v) => (
              <option key={v.dataset_version_id} value={v.dataset_version_id}>
                v{v.version_number} ({Number(v.record_count).toLocaleString()} rows)
              </option>
            ))}
          </select>
        </div>

        {results.length > 0 && (
          <div className="ml-auto flex items-center space-x-3 text-xs">
            <span className="text-slate-500">Average Score:</span>
            <span className="font-bold text-base text-slate-900">
              {(results.reduce((acc, curr) => acc + Number(curr.score), 0) / results.length).toFixed(1)}%
            </span>
          </div>
        )}
      </div>

      {/* Quality Results Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700">
            Quality Check Results ({results.length} checks)
          </h3>
          <span className="text-[11px] text-slate-400 font-mono">
            Table: data_quality_result
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-500 uppercase tracking-wider text-[10px] border-b border-slate-200">
              <tr>
                <th className="py-3 px-6 font-semibold">Check Name</th>
                <th className="py-3 px-6 font-semibold">Type</th>
                <th className="py-3 px-6 font-semibold">Threshold</th>
                <th className="py-3 px-6 font-semibold">Calculated Score</th>
                <th className="py-3 px-6 font-semibold">Status</th>
                <th className="py-3 px-6 font-semibold">Execution Timestamp</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {results.length > 0 ? (
                results.map((r) => (
                  <tr key={r.quality_result_id} className="hover:bg-slate-50/70 transition">
                    <td className="py-3.5 px-6 font-semibold text-slate-800">
                      {r.check_name || 'Standard Check'}
                    </td>
                    <td className="py-3.5 px-6 font-mono text-[11px] text-slate-500">
                      {r.check_type || 'validation'}
                    </td>
                    <td className="py-3.5 px-6 font-mono text-slate-600">
                      {r.threshold ? `${r.threshold}%` : '90.0%'}
                    </td>
                    <td className="py-3.5 px-6">
                      <div className="flex items-center space-x-3 max-w-xs">
                        <span className="font-bold font-mono text-slate-900 w-12">{r.score}%</span>
                        <div className="w-32 bg-slate-100 rounded-full h-2 overflow-hidden">
                          <div
                            className={`h-full rounded-full ${
                              Number(r.score) >= 90 ? 'bg-emerald-500' :
                              Number(r.score) >= 75 ? 'bg-amber-500' : 'bg-rose-500'
                            }`}
                            style={{ width: `${Math.min(100, Number(r.score))}%` }}
                          />
                        </div>
                      </div>
                    </td>
                    <td className="py-3.5 px-6">
                      {getStatusBadge(r.status)}
                    </td>
                    <td className="py-3.5 px-6 text-slate-500 font-mono text-[11px]">
                      {new Date(r.execution_date).toLocaleString()}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={6} className="py-10 text-center text-slate-400">
                    No quality check executions recorded for this version. Click "Run Checks Against Version" above.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Educational Explanation Box */}
      <div className="bg-slate-900 text-slate-200 rounded-xl p-5 border border-slate-800 shadow-md">
        <div className="flex items-start space-x-3">
          <Info className="w-5 h-5 text-brand-400 shrink-0 mt-0.5" />
          <div className="space-y-2 text-xs">
            <h4 className="font-bold text-white text-sm">Deterministic Quality Scoring Methodology</h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 pt-1 text-[11px] text-slate-300">
              <div className="bg-slate-800/80 p-2.5 rounded-lg border border-slate-700">
                <span className="font-bold text-brand-300">Missing Values:</span> Score = (1 - Null_Cells / Total_Cells) * 100.
              </div>
              <div className="bg-slate-800/80 p-2.5 rounded-lg border border-slate-700">
                <span className="font-bold text-brand-300">Duplicate Check:</span> Score = (1 - Dup_Rows / Total_Rows) * 100.
              </div>
              <div className="bg-slate-800/80 p-2.5 rounded-lg border border-slate-700">
                <span className="font-bold text-brand-300">Status Thresholds:</span> Score &ge; Threshold &rarr; PASSED; Score &ge; (Threshold - 15) &rarr; WARNING; otherwise FAILED.
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Add Quality Check Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl border border-slate-200">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <h3 className="text-sm font-bold text-slate-900">Define New Data Quality Check</h3>
              <button
                onClick={() => setShowAddModal(false)}
                className="text-slate-400 hover:text-slate-600 text-lg leading-none"
              >
                &times;
              </button>
            </div>

            <form onSubmit={handleCreateCheck} className="mt-4 space-y-4 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Check Name *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Transaction Amount Range Check"
                  value={newCheckName}
                  onChange={(e) => setNewCheckName(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg focus:outline-hidden"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Check Type *</label>
                <select
                  value={newCheckType}
                  onChange={(e) => setNewCheckType(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg focus:outline-hidden"
                >
                  <option value="missing_values">Missing Values Integrity</option>
                  <option value="duplicates">Record Uniqueness (Duplicates)</option>
                  <option value="data_types">Data Type Consistency</option>
                  <option value="numerical_range">Numerical Range Validity</option>
                  <option value="categorical_validity">Categorical Value Validation</option>
                  <option value="schema_integrity">Schema Integrity</option>
                </select>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Pass Threshold (%) *</label>
                <input
                  type="number"
                  min="0"
                  max="100"
                  step="0.5"
                  required
                  value={newThreshold}
                  onChange={(e) => setNewThreshold(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg font-mono focus:outline-hidden"
                />
              </div>

              <div className="pt-3 border-t border-slate-100 flex items-center justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-3 py-1.5 rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50 font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-1.5 bg-brand-600 hover:bg-brand-700 text-white rounded-lg font-semibold shadow-xs"
                >
                  Save Check
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
