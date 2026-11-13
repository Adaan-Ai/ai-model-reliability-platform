import React, { useState, useEffect } from 'react';
import {
  PlayCircle,
  Play,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Download,
  Calendar,
  Layers,
  BrainCircuit,
  User,
  GitCompare,
  FileSpreadsheet,
  ChevronRight,
  ArrowRight,
  TrendingUp,
  Activity,
  ShieldCheck,
  RefreshCw,
  Search
} from 'lucide-react';
import { api } from '../services/api';

export default function EvaluationsPage({
  initialEvaluationId,
  preselectedModelVersionId,
  showLaunchModal,
  onCloseLaunchModal,
  onNavigate,
  onSelectForComparison
}) {
  const [evaluations, setEvaluations] = useState([]);
  const [selectedEvalId, setSelectedEvalId] = useState(initialEvaluationId || null);
  const [evalDetail, setEvalDetail] = useState(null);
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);
  const [runSearch, setRunSearch] = useState('');

  // Run modal state
  const [modalOpen, setModalOpen] = useState(showLaunchModal || false);
  const [models, setModels] = useState([]);
  const [datasetVersions, setDatasetVersions] = useState([]);
  const [users, setUsers] = useState([]);
  const [executing, setExecuting] = useState(false);
  const [execError, setExecError] = useState(null);

  // Form inputs
  const [formModelVersionId, setFormModelVersionId] = useState(preselectedModelVersionId || '');
  const [formDatasetVersionId, setFormDatasetVersionId] = useState('');
  const [formExecutedBy, setFormExecutedBy] = useState('');
  const [formTargetCol, setFormTargetCol] = useState('is_fraud');
  const [formTestSize, setFormTestSize] = useState(0.2);
  const [formSeed, setFormSeed] = useState(42);

  useEffect(() => {
    loadEvaluations();
    loadFormMetadata();
  }, []);

  useEffect(() => {
    if (showLaunchModal) setModalOpen(true);
  }, [showLaunchModal]);

  useEffect(() => {
    if (preselectedModelVersionId) {
      setFormModelVersionId(preselectedModelVersionId);
    }
  }, [preselectedModelVersionId]);

  useEffect(() => {
    if (selectedEvalId) {
      loadEvaluationDetail(selectedEvalId);
    }
  }, [selectedEvalId]);

  const loadEvaluations = async () => {
    setLoading(true);
    try {
      const res = await api.getEvaluations();
      setEvaluations(res);
      if (res.length > 0 && !selectedEvalId) {
        setSelectedEvalId(res[0].evaluation_id);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const loadFormMetadata = async () => {
    try {
      const [mRes, dRes, uRes] = await Promise.all([
        api.getModels(),
        api.getDatasets(),
        api.getUsers()
      ]);
      setUsers(uRes);
      if (uRes.length > 0) setFormExecutedBy(uRes[0].user_id);

      // Flatten model versions
      const mvList = [];
      for (const m of mRes) {
        const det = await api.getModel(m.model_id);
        if (det.versions) {
          det.versions.forEach((v) => {
            mvList.push({
              model_version_id: v.model_version_id,
              label: `${m.model_name} v${v.version_number} (${v.algorithm})`,
            });
          });
        }
      }
      setModels(mvList);
      if (mvList.length > 0 && !formModelVersionId) {
        setFormModelVersionId(mvList[0].model_version_id);
      }

      // Flatten dataset versions
      const dvList = [];
      for (const d of dRes) {
        const vList = await api.getDatasetVersions(d.dataset_id);
        vList.forEach((v) => {
          dvList.push({
            dataset_version_id: v.dataset_version_id,
            dataset_id: d.dataset_id,
            dataset_name: d.dataset_name,
            version_number: v.version_number,
            label: `${d.dataset_name} v${v.version_number} (${Number(v.record_count).toLocaleString()} rows)`,
          });
        });
      }
      setDatasetVersions(dvList);
      if (dvList.length > 0) {
        setFormDatasetVersionId(dvList[0].dataset_version_id);
      }
    } catch (e) {
      console.error('Failed to load evaluation metadata:', e);
    }
  };

  const loadEvaluationDetail = async (id) => {
    setDetailLoading(true);
    try {
      const res = await api.getEvaluationDetail(id);
      setEvalDetail(res);
    } catch (err) {
      console.error(err);
    } finally {
      setDetailLoading(false);
    }
  };

  const visibleEvaluations = evaluations.filter((run) => {
    const query = runSearch.trim().toLowerCase();
    if (!query) return true;
    return [
      run.evaluation_id,
      run.model_name,
      run.dataset_name,
      run.algorithm,
    ].some((value) => String(value || '').toLowerCase().includes(query));
  });

  const handleLaunchEvaluation = async (e) => {
    e.preventDefault();
    setExecuting(true);
    setExecError(null);

    try {
      const run = await api.triggerEvaluation({
        model_version_id: Number(formModelVersionId),
        dataset_version_id: Number(formDatasetVersionId),
        executed_by: Number(formExecutedBy),
        target_column: formTargetCol,
        test_size: Number(formTestSize),
        random_state: Number(formSeed),
      });

      setModalOpen(false);
      if (onCloseLaunchModal) onCloseLaunchModal();
      await loadEvaluations();
      setSelectedEvalId(run.evaluation_id);
    } catch (err) {
      setExecError(err.message || 'Model evaluation execution failed.');
    } finally {
      setExecuting(false);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Model Evaluation Engine</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Real Scikit-learn classification pipelines, leak-free preprocessing, metrics, and serialized artifacts (Core Entity 9 & 10).
          </p>
        </div>

        <button
          onClick={() => setModalOpen(true)}
          className="inline-flex items-center space-x-1.5 px-4 py-2 bg-brand-600 hover:bg-brand-700 text-white rounded-lg text-xs font-semibold shadow-xs transition self-start sm:self-auto"
        >
          <PlayCircle className="w-4 h-4" />
          <span>Launch New Evaluation</span>
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Evaluation Runs List (4 cols) */}
        <div className="lg:col-span-5 space-y-3">
          <div className="bg-white p-3.5 rounded-xl border border-slate-200 shadow-xs flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-600">
              Evaluation Runs ({visibleEvaluations.length} of {evaluations.length})
            </span>
            <button onClick={loadEvaluations} className="text-slate-400 hover:text-slate-600">
              <RefreshCw className="w-3.5 h-3.5" />
            </button>
          </div>

          <label className="relative block">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="search"
              placeholder="Search run, model, dataset, or algorithm..."
              value={runSearch}
              onChange={(event) => setRunSearch(event.target.value)}
              className="w-full pl-9 pr-3 py-2 bg-white border border-slate-200 rounded-lg text-xs focus:outline-hidden focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition"
              aria-label="Search evaluation runs"
            />
          </label>

          <div className="space-y-2 max-h-[700px] overflow-y-auto pr-1">
            {loading ? (
              <div className="py-12 text-center text-xs text-slate-400">Loading runs...</div>
            ) : evaluations.length === 0 ? (
              <div className="p-8 text-center bg-white rounded-xl border border-slate-200 text-xs text-slate-400">
                No evaluations yet.
              </div>
            ) : visibleEvaluations.length === 0 ? (
              <div className="p-8 text-center bg-white rounded-xl border border-slate-200 text-xs text-slate-400">
                No runs match “{runSearch}”. Try another search.
              </div>
            ) : (
              visibleEvaluations.map((run) => {
                const isSelected = run.evaluation_id === selectedEvalId;
                const relRating = run.reliability?.rating || 'N/A';
                const driftStatus = run.drift?.drift_status || 'LOW';

                return (
                  <button
                    key={run.evaluation_id}
                    onClick={() => setSelectedEvalId(run.evaluation_id)}
                    className={`w-full text-left p-4 rounded-xl border transition flex flex-col justify-between ${
                      isSelected
                        ? 'border-brand-500 bg-brand-50/40 shadow-xs ring-1 ring-brand-500/30'
                        : 'bg-white border-slate-200 hover:border-slate-300'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-mono text-xs font-bold text-slate-500">
                        Run #{run.evaluation_id}
                      </span>
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                        relRating === 'HIGH' ? 'bg-emerald-100 text-emerald-800' :
                        relRating === 'MEDIUM' ? 'bg-amber-100 text-amber-800' :
                        'bg-rose-100 text-rose-800'
                      }`}>
                        {relRating} RELIABILITY
                      </span>
                    </div>

                    <div className="mt-2">
                      <h4 className="text-xs font-bold text-slate-900">
                        {run.model_name} <span className="font-mono text-slate-500">v{run.model_version_number}</span>
                      </h4>
                      <p className="text-[11px] text-slate-500 mt-0.5">
                        {run.dataset_name} <span className="font-mono">v{run.dataset_version_number}</span> • {run.algorithm}
                      </p>
                    </div>

                    <div className="mt-3 pt-2.5 border-t border-slate-100 flex items-center justify-between text-[11px]">
                      <div className="flex items-center space-x-3">
                        <span className="font-semibold text-slate-800">
                          Acc: {run.result?.accuracy ? `${run.result.accuracy}%` : '—'}
                        </span>
                        <span className="font-semibold text-slate-800">
                          F1: {run.result?.f1_score ? `${run.result.f1_score}%` : '—'}
                        </span>
                      </div>
                      <span className={`text-[10px] font-semibold ${
                        driftStatus === 'HIGH' ? 'text-rose-600' : driftStatus === 'MEDIUM' ? 'text-amber-600' : 'text-emerald-600'
                      }`}>
                        {driftStatus} Drift
                      </span>
                    </div>
                  </button>
                );
              })
            )}
          </div>
        </div>

        {/* Right Column: Detailed Report Inspection (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          {detailLoading ? (
            <div className="bg-white rounded-xl border border-slate-200 p-16 text-center">
              <div className="w-8 h-8 border-3 border-brand-200 border-t-brand-600 rounded-full animate-spin mx-auto" />
              <p className="text-xs text-slate-500 mt-2">Loading detailed evaluation audit report...</p>
            </div>
          ) : evalDetail ? (
            <div className="space-y-6">
              {/* Report Header Card */}
              <div className="bg-white rounded-xl border border-slate-200 shadow-xs p-5">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-slate-100">
                  <div>
                    <div className="flex items-center space-x-2">
                      <h3 className="text-base font-bold text-slate-900">
                        {evalDetail.model_name}
                      </h3>
                      <span className="font-mono text-xs px-2 py-0.5 bg-slate-100 rounded font-semibold text-slate-700">
                        v{evalDetail.model_version_number}
                      </span>
                    </div>
                    <p className="text-xs text-slate-500 mt-1">
                      Evaluated on <span className="font-medium text-slate-800">{evalDetail.dataset_name}</span> (v{evalDetail.dataset_version_number})
                    </p>
                  </div>

                  <div className="flex items-center space-x-2 self-start sm:self-auto">
                    <a
                      href={api.getReportDownloadUrl(evalDetail.evaluation_id, 'csv')}
                      target="_blank"
                      rel="noreferrer"
                      className="px-2.5 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-medium flex items-center space-x-1 border border-slate-200"
                    >
                      <Download className="w-3.5 h-3.5" />
                      <span>Download CSV</span>
                    </a>
                    <a
                      href={api.getReportDownloadUrl(evalDetail.evaluation_id, 'json')}
                      target="_blank"
                      rel="noreferrer"
                      className="px-2.5 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-medium flex items-center space-x-1 border border-slate-200"
                    >
                      <Download className="w-3.5 h-3.5" />
                      <span>JSON</span>
                    </a>
                  </div>
                </div>

                {/* 4 Performance Metric Badges */}
                <div className="mt-4 grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
                  <div className="bg-blue-50/60 border border-blue-100 p-3 rounded-xl">
                    <span className="text-[10px] font-bold text-blue-600 uppercase">Accuracy</span>
                    <p className="text-xl font-extrabold text-blue-900 mt-0.5">
                      {evalDetail.result?.accuracy}%
                    </p>
                  </div>
                  <div className="bg-purple-50/60 border border-purple-100 p-3 rounded-xl">
                    <span className="text-[10px] font-bold text-purple-600 uppercase">F1-Score</span>
                    <p className="text-xl font-extrabold text-purple-900 mt-0.5">
                      {evalDetail.result?.f1_score}%
                    </p>
                  </div>
                  <div className="bg-emerald-50/60 border border-emerald-100 p-3 rounded-xl">
                    <span className="text-[10px] font-bold text-emerald-600 uppercase">Precision</span>
                    <p className="text-xl font-extrabold text-emerald-900 mt-0.5">
                      {evalDetail.result?.precision_score}%
                    </p>
                  </div>
                  <div className="bg-amber-50/60 border border-amber-100 p-3 rounded-xl">
                    <span className="text-[10px] font-bold text-amber-600 uppercase">Recall</span>
                    <p className="text-xl font-extrabold text-amber-900 mt-0.5">
                      {evalDetail.result?.recall_score}%
                    </p>
                  </div>
                </div>
              </div>

              {/* Confusion Matrix Card */}
              {evalDetail.confusion_matrix && (
                <div className="bg-white rounded-xl border border-slate-200 shadow-xs p-5">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700 mb-1">
                    Confusion Matrix (Holdout Test Split)
                  </h4>
                  <p className="text-[11px] text-slate-400 mb-4">
                    Evaluating actual vs predicted classification counts on the test set.
                  </p>

                  <div className="flex items-center justify-center py-4">
                    <div className="inline-block border border-slate-300 rounded-lg overflow-hidden font-mono text-xs shadow-xs">
                      <div className="bg-slate-100 text-slate-500 font-bold px-4 py-2 border-b border-slate-200 text-center">
                        Predicted Class
                      </div>
                      <div className="flex">
                        <div className="bg-slate-100 text-slate-500 font-bold px-2 py-4 border-r border-slate-200 flex items-center justify-center [writing-mode:vertical-lr] rotate-180">
                          Actual Class
                        </div>
                        <div className="divide-y divide-slate-200">
                          {evalDetail.confusion_matrix.map((row, rIdx) => (
                            <div key={rIdx} className="flex divide-x divide-slate-200">
                              {row.map((cell, cIdx) => {
                                const isDiagonal = rIdx === cIdx;
                                return (
                                  <div
                                    key={cIdx}
                                    className={`w-20 h-16 flex flex-col items-center justify-center p-2 text-center ${
                                      isDiagonal ? 'bg-emerald-50 text-emerald-900 font-bold' : 'bg-slate-50/50 text-slate-600'
                                    }`}
                                  >
                                    <span className="text-sm">{cell}</span>
                                    <span className="text-[9px] text-slate-400">
                                      {rIdx === 0 && cIdx === 0 ? 'TN' : rIdx === 0 && cIdx === 1 ? 'FP' : rIdx === 1 && cIdx === 0 ? 'FN' : 'TP'}
                                    </span>
                                  </div>
                                );
                              })}
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Diagnostic Reasons & Recommendations */}
              <div className="bg-white rounded-xl border border-slate-200 shadow-xs p-5 space-y-4">
                <div className="flex items-center justify-between">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center space-x-1.5">
                    <ShieldCheck className="w-4 h-4 text-brand-600" />
                    <span>Reliability Assessment ({evalDetail.reliability?.overall_score || 0}/100)</span>
                  </h4>
                  <span className={`px-2.5 py-0.5 rounded text-[10px] font-bold ${
                    evalDetail.reliability?.rating === 'HIGH' ? 'bg-emerald-100 text-emerald-800' :
                    evalDetail.reliability?.rating === 'MEDIUM' ? 'bg-amber-100 text-amber-800' :
                    'bg-rose-100 text-rose-800'
                  }`}>
                    {evalDetail.reliability?.rating} RATING
                  </span>
                </div>

                <div className="space-y-2 text-xs">
                  <h5 className="font-semibold text-slate-700 text-[11px] uppercase tracking-wide">Key Findings:</h5>
                  <ul className="space-y-1 text-slate-600 list-disc list-inside text-xs">
                    {evalDetail.reliability_reasons && evalDetail.reliability_reasons.length > 0 ? (
                      evalDetail.reliability_reasons.map((r, idx) => (
                        <li key={idx}>{r}</li>
                      ))
                    ) : (
                      <li>Model performance and dataset reliability evaluated.</li>
                    )}
                  </ul>
                </div>

                <div className="pt-3 border-t border-slate-100 space-y-2 text-xs">
                  <h5 className="font-semibold text-slate-700 text-[11px] uppercase tracking-wide">Actionable Recommendations:</h5>
                  <ul className="space-y-1 text-brand-900 list-disc list-inside text-xs font-medium bg-brand-50/50 p-3 rounded-lg border border-brand-100">
                    {evalDetail.recommendations && evalDetail.recommendations.length > 0 ? (
                      evalDetail.recommendations.map((rec, idx) => (
                        <li key={idx}>{rec}</li>
                      ))
                    ) : (
                      <li>System operating within expected parameters.</li>
                    )}
                  </ul>
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-white rounded-xl border border-slate-200 p-16 text-center text-xs text-slate-400">
              Select an evaluation run from the list to inspect performance and reliability metrics.
            </div>
          )}
        </div>
      </div>

      {/* Launch Evaluation Modal */}
      {modalOpen && (
        <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-200">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div className="flex items-center space-x-2">
                <PlayCircle className="w-5 h-5 text-brand-600" />
                <h3 className="text-sm font-bold text-slate-900">Launch New Scikit-learn Evaluation</h3>
              </div>
              <button
                onClick={() => {
                  setModalOpen(false);
                  if (onCloseLaunchModal) onCloseLaunchModal();
                }}
                className="text-slate-400 hover:text-slate-600 text-lg leading-none"
              >
                &times;
              </button>
            </div>

            <form onSubmit={handleLaunchEvaluation} className="mt-4 space-y-4 text-xs">
              {execError && (
                <div className="p-3 rounded-lg bg-rose-50 border border-rose-200 text-rose-700">
                  {execError}
                </div>
              )}

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Target Model & Version *</label>
                <select
                  value={formModelVersionId}
                  onChange={(e) => setFormModelVersionId(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg focus:outline-hidden font-medium"
                >
                  {models.map((m) => (
                    <option key={m.model_version_id} value={m.model_version_id}>
                      {m.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Target Dataset Snapshot *</label>
                <select
                  value={formDatasetVersionId}
                  onChange={(e) => setFormDatasetVersionId(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg focus:outline-hidden font-medium"
                >
                  {datasetVersions.map((d) => (
                    <option key={d.dataset_version_id} value={d.dataset_version_id}>
                      {d.label}
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Target Column Name *</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. is_fraud or churn"
                    value={formTargetCol}
                    onChange={(e) => setFormTargetCol(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg font-mono focus:outline-hidden"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Executed By (User) *</label>
                  <select
                    value={formExecutedBy}
                    onChange={(e) => setFormExecutedBy(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg focus:outline-hidden"
                  >
                    {users.map((u) => (
                      <option key={u.user_id} value={u.user_id}>
                        {u.name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Test Size Split (0.05 – 0.50)</label>
                  <input
                    type="number"
                    min="0.05"
                    max="0.5"
                    step="0.05"
                    value={formTestSize}
                    onChange={(e) => setFormTestSize(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg font-mono focus:outline-hidden"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Random State Seed</label>
                  <input
                    type="number"
                    value={formSeed}
                    onChange={(e) => setFormSeed(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg font-mono focus:outline-hidden"
                  />
                </div>
              </div>

              <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 text-[11px] text-slate-500">
                This triggers a real Scikit-learn execution pipeline: Stratified train/test split, column transformer (imputation + scaling + one-hot encoding), classifier training, metric scoring, drift calculation, and composite reliability scoring.
              </div>

              <div className="pt-3 border-t border-slate-100 flex items-center justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => {
                    setModalOpen(false);
                    if (onCloseLaunchModal) onCloseLaunchModal();
                  }}
                  className="px-3.5 py-1.5 rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50 font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={executing}
                  className="px-4 py-1.5 bg-brand-600 hover:bg-brand-700 text-white rounded-lg font-semibold shadow-xs disabled:opacity-50 flex items-center space-x-1.5"
                >
                  <Play className="w-3.5 h-3.5" />
                  <span>{executing ? 'Executing Pipeline...' : 'Execute Model Evaluation'}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
