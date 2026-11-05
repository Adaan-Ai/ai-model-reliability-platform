import React, { useState, useEffect } from 'react';
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  AlertOctagon,
  Info,
  Calendar,
  Layers,
  BrainCircuit,
  Search,
  ChevronRight,
  TrendingDown,
  ArrowRight
} from 'lucide-react';
import { api } from '../services/api';

export default function DriftPage() {
  const [driftRecords, setDriftRecords] = useState([]);
  const [selectedEvalId, setSelectedEvalId] = useState(null);
  const [driftDetail, setDriftDetail] = useState(null);
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);

  useEffect(() => {
    loadDriftRecords();
  }, []);

  useEffect(() => {
    if (selectedEvalId) {
      loadDriftDetail(selectedEvalId);
    }
  }, [selectedEvalId]);

  const loadDriftRecords = async () => {
    setLoading(true);
    try {
      const res = await api.getDriftRecords();
      setDriftRecords(res);
      if (res.length > 0) {
        setSelectedEvalId(res[0].evaluation_id);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const loadDriftDetail = async (evalId) => {
    setDetailLoading(true);
    try {
      const res = await api.getEvaluationDriftDetail(evalId);
      setDriftDetail(res);
    } catch (err) {
      console.error(err);
    } finally {
      setDetailLoading(false);
    }
  };

  const getDriftPill = (status) => {
    if (status === 'HIGH') {
      return (
        <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-rose-100 text-rose-800 border border-rose-200">
          <AlertOctagon className="w-3 h-3 text-rose-600" />
          <span>HIGH DRIFT</span>
        </span>
      );
    } else if (status === 'MEDIUM') {
      return (
        <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-800 border border-amber-200">
          <AlertTriangle className="w-3 h-3 text-amber-600" />
          <span>MODERATE DRIFT</span>
        </span>
      );
    }
    return (
      <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-200">
        <CheckCircle2 className="w-3 h-3 text-emerald-600" />
        <span>LOW DRIFT (STABLE)</span>
      </span>
    );
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-slate-900 tracking-tight">Data Drift Monitoring</h1>
        <p className="text-xs text-slate-500 mt-0.5">
          Population Stability Index (PSI) & Kolmogorov-Smirnov 2-sample tests measuring covariate distribution shifts (Core Entity 11).
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Drift Record Selector (5 cols) */}
        <div className="lg:col-span-5 space-y-3">
          <div className="bg-white p-3.5 rounded-xl border border-slate-200 shadow-xs">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-600">
              Evaluations Monitored ({driftRecords.length})
            </h3>
          </div>

          <div className="space-y-2 max-h-[650px] overflow-y-auto pr-1">
            {loading ? (
              <div className="py-12 text-center text-xs text-slate-400">Loading drift measurements...</div>
            ) : driftRecords.length === 0 ? (
              <div className="p-8 text-center bg-white rounded-xl border border-slate-200 text-xs text-slate-400">
                No drift measurements recorded yet.
              </div>
            ) : (
              driftRecords.map((item) => {
                const isSelected = item.evaluation_id === selectedEvalId;
                return (
                  <button
                    key={item.drift_id}
                    onClick={() => setSelectedEvalId(item.evaluation_id)}
                    className={`w-full text-left p-4 rounded-xl border transition flex flex-col justify-between ${
                      isSelected
                        ? 'border-brand-500 bg-brand-50/40 shadow-xs ring-1 ring-brand-500/30'
                        : 'bg-white border-slate-200 hover:border-slate-300'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-mono text-xs font-bold text-slate-500">
                        Run #{item.evaluation_id}
                      </span>
                      {getDriftPill(item.drift_status)}
                    </div>

                    <div className="mt-2">
                      <h4 className="text-xs font-bold text-slate-900">
                        {item.model_name} <span className="font-mono text-slate-500">v{item.model_version}</span>
                      </h4>
                      <p className="text-[11px] text-slate-500 mt-0.5">
                        {item.dataset_name} <span className="font-mono">v{item.dataset_version}</span>
                      </p>
                    </div>

                    <div className="mt-3 pt-2.5 border-t border-slate-100 flex items-center justify-between text-[11px]">
                      <span className="font-mono font-semibold text-slate-800">
                        Overall PSI: {Number(item.drift_score).toFixed(4)}
                      </span>
                      <span className="text-slate-400 text-[10px] font-mono">
                        {new Date(item.detected_date).toLocaleDateString()}
                      </span>
                    </div>
                  </button>
                );
              })
            )}
          </div>
        </div>

        {/* Right Column: Detailed Breakdown (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          {detailLoading ? (
            <div className="bg-white rounded-xl border border-slate-200 p-16 text-center">
              <div className="w-8 h-8 border-3 border-brand-200 border-t-brand-600 rounded-full animate-spin mx-auto" />
              <p className="text-xs text-slate-500 mt-2">Computing feature-level PSI breakdown...</p>
            </div>
          ) : driftDetail ? (
            <div className="space-y-6">
              {/* Header Overview Card */}
              <div className="bg-white rounded-xl border border-slate-200 shadow-xs p-5">
                <div className="flex items-start justify-between pb-4 border-b border-slate-100">
                  <div>
                    <h3 className="text-base font-bold text-slate-900 flex items-center space-x-2">
                      <span>Statistical Drift Assessment</span>
                      <span className="text-xs font-mono font-normal text-slate-400">
                        (Evaluation #{driftDetail.evaluation_id})
                      </span>
                    </h3>
                    <p className="text-xs text-slate-500 mt-1">
                      Target: <span className="font-semibold text-slate-800">{driftDetail.dataset_name} v{driftDetail.dataset_version}</span>
                      {driftDetail.reference_version && (
                        <span> vs Reference: <span className="font-semibold text-slate-800">v{driftDetail.reference_version}</span></span>
                      )}
                    </p>
                  </div>
                  {getDriftPill(driftDetail.drift_status)}
                </div>

                <div className="mt-4 grid grid-cols-2 gap-3">
                  <div className="bg-slate-50 p-3 rounded-xl border border-slate-100">
                    <span className="text-[11px] text-slate-500 font-medium">Population Stability Index</span>
                    <p className="text-2xl font-bold font-mono text-slate-900 mt-0.5">
                      {Number(driftDetail.drift_score).toFixed(4)}
                    </p>
                    <span className="text-[10px] text-slate-400">
                      Mean PSI across all shared features
                    </span>
                  </div>

                  <div className="bg-slate-50 p-3 rounded-xl border border-slate-100">
                    <span className="text-[11px] text-slate-500 font-medium">Shift Severity</span>
                    <p className="text-lg font-bold text-slate-900 mt-0.5">
                      {driftDetail.drift_status}
                    </p>
                    <span className="text-[10px] text-slate-500">
                      {driftDetail.drift_status === 'HIGH' ? 'Retraining strongly recommended' :
                       driftDetail.drift_status === 'MEDIUM' ? 'Active monitoring advised' : 'Distribution stable'}
                    </span>
                  </div>
                </div>

                {driftDetail.overall_explanation && (
                  <p className="mt-4 text-xs text-slate-700 bg-brand-50/50 p-3 rounded-lg border border-brand-100 leading-relaxed">
                    {driftDetail.overall_explanation}
                  </p>
                )}
              </div>

              {/* Feature-Level Breakdown Table */}
              <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
                <div className="px-5 py-3.5 border-b border-slate-200 flex items-center justify-between">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700">
                    Feature-by-Feature Distribution Shift
                  </h4>
                  <span className="text-[10px] font-mono text-slate-400">
                    PSI + KS-Test (2-sample)
                  </span>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-slate-50 text-slate-500 uppercase tracking-wider text-[10px] border-b border-slate-200">
                      <tr>
                        <th className="py-2.5 px-4 font-semibold">Feature Column</th>
                        <th className="py-2.5 px-4 font-semibold">Type</th>
                        <th className="py-2.5 px-4 font-semibold">PSI Score</th>
                        <th className="py-2.5 px-4 font-semibold">KS p-value</th>
                        <th className="py-2.5 px-4 font-semibold">Drift Level</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 font-mono text-[11px]">
                      {driftDetail.feature_drift_breakdown && driftDetail.feature_drift_breakdown.length > 0 ? (
                        driftDetail.feature_drift_breakdown.map((f, idx) => (
                          <tr key={idx} className="hover:bg-slate-50/70 transition">
                            <td className="py-2.5 px-4 font-bold text-slate-800">
                              {f.feature_name}
                            </td>
                            <td className="py-2.5 px-4 text-slate-500">
                              {f.feature_type}
                            </td>
                            <td className="py-2.5 px-4 font-bold text-slate-900">
                              {f.psi_score.toFixed(4)}
                            </td>
                            <td className="py-2.5 px-4 text-slate-600">
                              {f.p_value !== null ? f.p_value.toFixed(4) : 'N/A (Categorical)'}
                            </td>
                            <td className="py-2.5 px-4">
                              <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                                f.drift_level === 'HIGH' ? 'bg-rose-100 text-rose-800' :
                                f.drift_level === 'MEDIUM' ? 'bg-amber-100 text-amber-800' :
                                'bg-emerald-100 text-emerald-800'
                              }`}>
                                {f.drift_level}
                              </span>
                            </td>
                          </tr>
                        ))
                      ) : (
                        <tr>
                          <td colSpan={5} className="py-8 text-center text-slate-400 font-sans">
                            {driftDetail.reference_version
                              ? 'No individual feature breakdown available.'
                              : 'Initial version served as the statistical baseline; no earlier version to compare against.'}
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Statistical Guidance */}
              <div className="bg-slate-900 text-slate-200 rounded-xl p-5 border border-slate-800 shadow-md">
                <div className="flex items-start space-x-3">
                  <Info className="w-5 h-5 text-brand-400 shrink-0 mt-0.5" />
                  <div className="space-y-2 text-xs">
                    <h4 className="font-bold text-white text-sm">How Population Stability Index (PSI) Works</h4>
                    <p className="text-slate-300 text-[11px] leading-relaxed">
                      PSI divides continuous variables into 10 quantile bins on the reference dataset and compares actual bin frequencies in the current dataset:
                      <span className="font-mono block bg-slate-800 p-2 rounded my-1 text-brand-300">
                        PSI = &sum; [ (Actual% - Expected%) &times; ln(Actual% / Expected%) ]
                      </span>
                      - <strong>PSI &lt; 0.10:</strong> Minimal change; distribution is stable.<br />
                      - <strong>0.10 &le; PSI &le; 0.25:</strong> Moderate distribution change; system suggests monitoring.<br />
                      - <strong>PSI &gt; 0.25:</strong> Significant distribution change; model retrain required.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-white rounded-xl border border-slate-200 p-16 text-center text-xs text-slate-400">
              Select an evaluation run to inspect its statistical drift breakdown.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
