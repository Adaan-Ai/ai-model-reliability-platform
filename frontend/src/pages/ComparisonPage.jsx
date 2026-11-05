import React, { useState, useEffect } from 'react';
import {
  GitCompare,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  TrendingUp,
  BrainCircuit,
  Database,
  Layers,
  Activity,
  ShieldCheck,
  Download
} from 'lucide-react';
import { api } from '../services/api';

export default function ComparisonPage() {
  const [evaluations, setEvaluations] = useState([]);
  const [selectedIds, setSelectedIds] = useState([]);
  const [compareRuns, setCompareRuns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [comparing, setComparing] = useState(false);

  useEffect(() => {
    loadEvaluations();
  }, []);

  const loadEvaluations = async () => {
    setLoading(true);
    try {
      const res = await api.getEvaluations({ status: 'COMPLETED' });
      setEvaluations(res);
      // Preselect first two runs if available
      if (res.length >= 2) {
        const initialPair = [res[0].evaluation_id, res[1].evaluation_id];
        setSelectedIds(initialPair);
        executeCompare(initialPair);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const toggleSelect = (id) => {
    let updated;
    if (selectedIds.includes(id)) {
      if (selectedIds.length <= 1) return; // Keep at least one
      updated = selectedIds.filter((item) => item !== id);
    } else {
      if (selectedIds.length >= 4) {
        alert('You can compare up to 4 runs simultaneously.');
        return;
      }
      updated = [...selectedIds, id];
    }
    setSelectedIds(updated);
    executeCompare(updated);
  };

  const executeCompare = async (ids) => {
    if (ids.length === 0) return;
    setComparing(true);
    try {
      const res = await api.compareEvaluations(ids);
      setCompareRuns(res);
    } catch (err) {
      console.error(err);
    } finally {
      setComparing(false);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-slate-900 tracking-tight">Model Evaluation Comparison</h1>
        <p className="text-xs text-slate-500 mt-0.5">
          Side-by-side benchmark comparison tracking accuracy, precision, recall, drift, and reliability deltas (Module 9).
        </p>
      </div>

      {/* Run Selection Pills */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
        <div className="flex items-center justify-between mb-3">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-600">
            Select Runs to Compare (Select 2–4):
          </span>
          <span className="text-xs text-brand-600 font-semibold">
            {selectedIds.length} Selected
          </span>
        </div>

        <div className="flex flex-wrap gap-2">
          {evaluations.map((run) => {
            const isSelected = selectedIds.includes(run.evaluation_id);
            return (
              <button
                key={run.evaluation_id}
                onClick={() => toggleSelect(run.evaluation_id)}
                className={`px-3 py-1.5 rounded-lg border text-xs font-medium transition flex items-center space-x-2 ${
                  isSelected
                    ? 'bg-brand-600 text-white border-brand-600 shadow-xs'
                    : 'bg-slate-50 text-slate-700 border-slate-200 hover:border-slate-300'
                }`}
              >
                <span className="font-mono">Run #{run.evaluation_id}</span>
                <span>•</span>
                <span>{run.model_name} v{run.model_version_number}</span>
                <span className={`text-[10px] px-1.5 py-0.2 rounded font-mono ${isSelected ? 'bg-brand-700' : 'bg-slate-200'}`}>
                  {run.result?.accuracy}%
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Comparison Grid Table */}
      {comparing ? (
        <div className="py-16 text-center">
          <div className="w-8 h-8 border-3 border-brand-200 border-t-brand-600 rounded-full animate-spin mx-auto" />
          <p className="text-xs text-slate-500 mt-2">Loading comparison metrics...</p>
        </div>
      ) : compareRuns.length > 0 ? (
        <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-600 border-b border-slate-200">
                <tr>
                  <th className="py-4 px-6 font-bold uppercase tracking-wider text-[11px] w-64 bg-slate-100/70">
                    Metric / Dimension
                  </th>
                  {compareRuns.map((run) => (
                    <th key={run.evaluation_id} className="py-4 px-6 font-bold text-slate-900 border-l border-slate-200">
                      <div className="flex items-center justify-between">
                        <span className="font-mono text-sm">Run #{run.evaluation_id}</span>
                        <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                          run.reliability?.rating === 'HIGH' ? 'bg-emerald-100 text-emerald-800' :
                          run.reliability?.rating === 'MEDIUM' ? 'bg-amber-100 text-amber-800' :
                          'bg-rose-100 text-rose-800'
                        }`}>
                          {run.reliability?.rating}
                        </span>
                      </div>
                      <div className="text-xs font-semibold text-slate-700 mt-1">
                        {run.model_name} v{run.model_version_number}
                      </div>
                    </th>
                  ))}
                </tr>
              </thead>

              <tbody className="divide-y divide-slate-100">
                {/* Algorithm */}
                <tr className="hover:bg-slate-50/50">
                  <td className="py-3 px-6 font-semibold text-slate-600 bg-slate-50/50">Algorithm</td>
                  {compareRuns.map((run) => (
                    <td key={run.evaluation_id} className="py-3 px-6 font-mono font-medium text-slate-800 border-l border-slate-100">
                      {run.algorithm}
                    </td>
                  ))}
                </tr>

                {/* Dataset Version */}
                <tr className="hover:bg-slate-50/50">
                  <td className="py-3 px-6 font-semibold text-slate-600 bg-slate-50/50">Dataset Version</td>
                  {compareRuns.map((run) => (
                    <td key={run.evaluation_id} className="py-3 px-6 font-medium text-slate-800 border-l border-slate-100">
                      {run.dataset_name} <span className="font-mono text-slate-500">v{run.dataset_version_number}</span>
                    </td>
                  ))}
                </tr>

                {/* Accuracy */}
                <tr className="hover:bg-slate-50/50 bg-blue-50/20">
                  <td className="py-3.5 px-6 font-bold text-slate-800 bg-blue-50/40">Accuracy (%)</td>
                  {compareRuns.map((run) => (
                    <td key={run.evaluation_id} className="py-3.5 px-6 font-black font-mono text-base text-blue-900 border-l border-slate-100">
                      {run.result?.accuracy}%
                    </td>
                  ))}
                </tr>

                {/* F1-Score */}
                <tr className="hover:bg-slate-50/50 bg-purple-50/20">
                  <td className="py-3.5 px-6 font-bold text-slate-800 bg-purple-50/40">F1-Score (%)</td>
                  {compareRuns.map((run) => (
                    <td key={run.evaluation_id} className="py-3.5 px-6 font-black font-mono text-base text-purple-900 border-l border-slate-100">
                      {run.result?.f1_score}%
                    </td>
                  ))}
                </tr>

                {/* Precision */}
                <tr className="hover:bg-slate-50/50">
                  <td className="py-3 px-6 font-semibold text-slate-600 bg-slate-50/50">Precision (%)</td>
                  {compareRuns.map((run) => (
                    <td key={run.evaluation_id} className="py-3 px-6 font-mono text-slate-800 border-l border-slate-100">
                      {run.result?.precision_score}%
                    </td>
                  ))}
                </tr>

                {/* Recall */}
                <tr className="hover:bg-slate-50/50">
                  <td className="py-3 px-6 font-semibold text-slate-600 bg-slate-50/50">Recall (%)</td>
                  {compareRuns.map((run) => (
                    <td key={run.evaluation_id} className="py-3 px-6 font-mono text-slate-800 border-l border-slate-100">
                      {run.result?.recall_score}%
                    </td>
                  ))}
                </tr>

                {/* Population Stability Index (PSI) */}
                <tr className="hover:bg-slate-50/50">
                  <td className="py-3 px-6 font-semibold text-slate-600 bg-slate-50/50">Data Drift (PSI)</td>
                  {compareRuns.map((run) => (
                    <td key={run.evaluation_id} className="py-3 px-6 font-mono font-bold text-slate-800 border-l border-slate-100">
                      {run.drift?.drift_score !== undefined ? Number(run.drift.drift_score).toFixed(4) : '0.0000'}
                    </td>
                  ))}
                </tr>

                {/* Drift Severity */}
                <tr className="hover:bg-slate-50/50">
                  <td className="py-3 px-6 font-semibold text-slate-600 bg-slate-50/50">Drift Severity</td>
                  {compareRuns.map((run) => (
                    <td key={run.evaluation_id} className="py-3 px-6 border-l border-slate-100">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        run.drift?.drift_status === 'HIGH' ? 'bg-rose-100 text-rose-800' :
                        run.drift?.drift_status === 'MEDIUM' ? 'bg-amber-100 text-amber-800' :
                        'bg-emerald-100 text-emerald-800'
                      }`}>
                        {run.drift?.drift_status || 'LOW'}
                      </span>
                    </td>
                  ))}
                </tr>

                {/* Overall Reliability Score */}
                <tr className="hover:bg-slate-50/50 bg-emerald-50/20">
                  <td className="py-4 px-6 font-bold text-slate-900 bg-emerald-50/40">Overall Reliability (0–100)</td>
                  {compareRuns.map((run) => (
                    <td key={run.evaluation_id} className="py-4 px-6 font-black font-mono text-lg text-emerald-900 border-l border-slate-100">
                      {run.reliability?.overall_score || '—'}
                    </td>
                  ))}
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      ) : null}
    </div>
  );
}
