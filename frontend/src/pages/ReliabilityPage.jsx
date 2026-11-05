import React, { useState, useEffect } from 'react';
import {
  ShieldCheck,
  AlertTriangle,
  CheckCircle2,
  Download,
  Info,
  Calendar,
  Layers,
  BrainCircuit,
  Activity,
  ArrowRight,
  TrendingUp,
  Award
} from 'lucide-react';
import { api } from '../services/api';

export default function ReliabilityPage() {
  const [scores, setScores] = useState([]);
  const [selectedEvalId, setSelectedEvalId] = useState(null);
  const [reliabilityDetail, setReliabilityDetail] = useState(null);
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);

  useEffect(() => {
    loadReliabilityScores();
  }, []);

  useEffect(() => {
    if (selectedEvalId) {
      loadReliabilityDetail(selectedEvalId);
    }
  }, [selectedEvalId]);

  const loadReliabilityScores = async () => {
    setLoading(true);
    try {
      const res = await api.getReliabilityScores();
      setScores(res);
      if (res.length > 0) {
        setSelectedEvalId(res[0].evaluation_id);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const loadReliabilityDetail = async (evalId) => {
    setDetailLoading(true);
    try {
      const res = await api.getEvaluationReliabilityDetail(evalId);
      setReliabilityDetail(res);
    } catch (err) {
      console.error(err);
    } finally {
      setDetailLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-slate-900 tracking-tight">Reliability Scoring Engine</h1>
        <p className="text-xs text-slate-500 mt-0.5">
          Signature composite assessment consolidating Data Quality, Model Performance, and Drift Health (Core Entity 12).
        </p>
      </div>

      {/* Transparent Formula Banner */}
      <div className="bg-gradient-to-r from-brand-900 via-indigo-950 to-slate-950 rounded-2xl p-6 text-white shadow-lg border border-brand-800/40">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2 text-brand-300 text-xs font-semibold uppercase tracking-wider mb-1">
              <Award className="w-4 h-4 text-brand-400" />
              <span>Platform Signature Weighted Scoring Formula</span>
            </div>
            <div className="text-lg md:text-xl font-mono font-bold tracking-tight text-white mt-2">
              Overall Reliability = <span className="text-emerald-400">(0.35 &times; Data Quality)</span> + <span className="text-blue-400">(0.45 &times; Model Performance)</span> + <span className="text-amber-400">(0.20 &times; Drift Health)</span>
            </div>
            <p className="text-xs text-slate-300 mt-2 max-w-2xl">
              All components normalized strictly between 0 and 100. Higher drift severity directly reduces Drift Health. Ratings: <span className="text-emerald-400 font-semibold">&ge;80 HIGH</span>, <span className="text-amber-400 font-semibold">60–79.99 MEDIUM</span>, <span className="text-rose-400 font-semibold">&lt;60 LOW</span>.
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Evaluation Selector (5 cols) */}
        <div className="lg:col-span-5 space-y-3">
          <div className="bg-white p-3.5 rounded-xl border border-slate-200 shadow-xs">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-600">
              Evaluations Scored ({scores.length})
            </h3>
          </div>

          <div className="space-y-2 max-h-[650px] overflow-y-auto pr-1">
            {loading ? (
              <div className="py-12 text-center text-xs text-slate-400">Loading reliability scores...</div>
            ) : scores.length === 0 ? (
              <div className="p-8 text-center bg-white rounded-xl border border-slate-200 text-xs text-slate-400">
                No reliability scores calculated yet.
              </div>
            ) : (
              scores.map((item) => {
                const isSelected = item.evaluation_id === selectedEvalId;
                return (
                  <button
                    key={item.reliability_id}
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
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                        item.rating === 'HIGH' ? 'bg-emerald-100 text-emerald-800' :
                        item.rating === 'MEDIUM' ? 'bg-amber-100 text-amber-800' :
                        'bg-rose-100 text-rose-800'
                      }`}>
                        {item.rating} RATING
                      </span>
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
                      <span className="font-semibold text-slate-800 font-mono">
                        Composite: {item.overall_score}/100
                      </span>
                      <span className="text-slate-400 text-[10px]">
                        DQ: {item.data_quality_score} • Model: {item.model_performance_score}
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
              <p className="text-xs text-slate-500 mt-2">Loading reliability assessment...</p>
            </div>
          ) : reliabilityDetail ? (
            <div className="space-y-6">
              {/* Header Card */}
              <div className="bg-white rounded-xl border border-slate-200 shadow-xs p-5">
                <div className="flex items-start justify-between pb-4 border-b border-slate-100">
                  <div>
                    <h3 className="text-base font-bold text-slate-900 flex items-center space-x-2">
                      <span>{reliabilityDetail.model_name} v{reliabilityDetail.model_version}</span>
                      <span className="text-xs font-mono font-normal text-slate-400">
                        (Run #{reliabilityDetail.evaluation_id})
                      </span>
                    </h3>
                    <p className="text-xs text-slate-500 mt-1">
                      Tested against {reliabilityDetail.dataset_name} (v{reliabilityDetail.dataset_version})
                    </p>
                  </div>

                  <div className="flex items-center space-x-2">
                    <a
                      href={api.getReportDownloadUrl(reliabilityDetail.evaluation_id, 'csv')}
                      target="_blank"
                      rel="noreferrer"
                      className="px-2.5 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-medium flex items-center space-x-1 border border-slate-200"
                    >
                      <Download className="w-3.5 h-3.5" />
                      <span>Audit CSV</span>
                    </a>
                  </div>
                </div>

                {/* 3 Component Breakdown Cards + Composite */}
                <div className="mt-5 grid grid-cols-1 sm:grid-cols-4 gap-3 text-center">
                  <div className="bg-emerald-50/70 border border-emerald-100 p-3.5 rounded-xl">
                    <span className="text-[10px] font-bold text-emerald-700 uppercase">Data Quality (35%)</span>
                    <p className="text-2xl font-black text-emerald-900 mt-1 font-mono">
                      {reliabilityDetail.data_quality_score}
                    </p>
                    <span className="text-[10px] text-emerald-600">Score &times; 0.35</span>
                  </div>

                  <div className="bg-blue-50/70 border border-blue-100 p-3.5 rounded-xl">
                    <span className="text-[10px] font-bold text-blue-700 uppercase">Model Perf (45%)</span>
                    <p className="text-2xl font-black text-blue-900 mt-1 font-mono">
                      {reliabilityDetail.model_performance_score}
                    </p>
                    <span className="text-[10px] text-blue-600">Score &times; 0.45</span>
                  </div>

                  <div className="bg-amber-50/70 border border-amber-100 p-3.5 rounded-xl">
                    <span className="text-[10px] font-bold text-amber-700 uppercase">Drift Health (20%)</span>
                    <p className="text-2xl font-black text-amber-900 mt-1 font-mono">
                      {reliabilityDetail.drift_score}
                    </p>
                    <span className="text-[10px] text-amber-600">Score &times; 0.20</span>
                  </div>

                  <div className="bg-slate-900 text-white p-3.5 rounded-xl border border-slate-800">
                    <span className="text-[10px] font-bold text-brand-300 uppercase">Overall Index</span>
                    <p className="text-2xl font-black text-white mt-1 font-mono">
                      {reliabilityDetail.overall_score}
                    </p>
                    <span className={`text-[10px] font-bold px-1.5 py-0.2 rounded ${
                      reliabilityDetail.rating === 'HIGH' ? 'bg-emerald-500/20 text-emerald-300' :
                      reliabilityDetail.rating === 'MEDIUM' ? 'bg-amber-500/20 text-amber-300' :
                      'bg-rose-500/20 text-rose-300'
                    }`}>
                      {reliabilityDetail.rating}
                    </span>
                  </div>
                </div>
              </div>

              {/* Reasons & Recommendations */}
              <div className="bg-white rounded-xl border border-slate-200 shadow-xs p-5 space-y-4">
                <div>
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700 mb-2">
                    Diagnostic Analysis
                  </h4>
                  <ul className="space-y-1.5 text-xs text-slate-700 list-disc list-inside">
                    {reliabilityDetail.reasons?.map((r, idx) => (
                      <li key={idx}>{r}</li>
                    ))}
                  </ul>
                </div>

                <div className="pt-3 border-t border-slate-100">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700 mb-2">
                    Actionable Recommendations
                  </h4>
                  <div className="space-y-1.5 bg-brand-50/50 p-3 rounded-xl border border-brand-100 text-xs text-brand-900 font-medium">
                    {reliabilityDetail.recommendations?.map((rec, idx) => (
                      <div key={idx} className="flex items-start space-x-2">
                        <CheckCircle2 className="w-3.5 h-3.5 text-brand-600 shrink-0 mt-0.5" />
                        <span>{rec}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-white rounded-xl border border-slate-200 p-16 text-center text-xs text-slate-400">
              Select an evaluation run from the list to view its complete reliability assessment.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
