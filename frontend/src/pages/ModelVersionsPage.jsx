import React, { useState, useEffect } from 'react';
import {
  GitBranch,
  BrainCircuit,
  Calendar,
  Plus,
  PlayCircle,
  TrendingUp,
  Cpu,
  ShieldCheck,
  ChevronRight
} from 'lucide-react';
import { api } from '../services/api';

export default function ModelVersionsPage({ selectedModelId, onNavigate, onLaunchEvaluation }) {
  const [models, setModels] = useState([]);
  const [currentModelId, setCurrentModelId] = useState(selectedModelId || null);
  const [modelDetail, setModelDetail] = useState(null);
  const [loading, setLoading] = useState(true);

  // Add version modal
  const [showModal, setShowModal] = useState(false);
  const [versionNumber, setVersionNumber] = useState('');
  const [algorithm, setAlgorithm] = useState('Logistic Regression');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    loadModels();
  }, []);

  useEffect(() => {
    if (selectedModelId) {
      setCurrentModelId(selectedModelId);
    }
  }, [selectedModelId]);

  useEffect(() => {
    if (currentModelId) {
      loadModelDetail(currentModelId);
    }
  }, [currentModelId]);

  const loadModels = async () => {
    setLoading(true);
    try {
      const res = await api.getModels();
      setModels(res);
      if (res.length > 0) {
        const activeId = selectedModelId || res[0].model_id;
        setCurrentModelId(activeId);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const loadModelDetail = async (modelId) => {
    try {
      const res = await api.getModel(modelId);
      setModelDetail(res);
      // Auto-suggest next version number
      const count = res.versions?.length || 0;
      setVersionNumber(`${count + 1}.0`);
    } catch (err) {
      console.error(err);
    }
  };

  const handleCreateVersion = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await api.createModelVersion(currentModelId, {
        version_number: versionNumber,
        algorithm: algorithm,
      });
      setShowModal(false);
      loadModelDetail(currentModelId);
    } catch (err) {
      alert(`Failed to add version: ${err.message}`);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Model Versions & Algorithms</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Algorithmic iterations, serialized artifacts, and historical benchmark metrics (Core Entity 8).
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2">
            <label className="text-xs font-semibold text-slate-600">Model:</label>
            <select
              value={currentModelId || ''}
              onChange={(e) => setCurrentModelId(Number(e.target.value))}
              className="px-3 py-1.5 bg-white border border-slate-200 rounded-lg text-xs font-medium shadow-xs focus:outline-hidden"
            >
              {models.map((m) => (
                <option key={m.model_id} value={m.model_id}>
                  {m.model_name}
                </option>
              ))}
            </select>
          </div>

          <button
            onClick={() => setShowModal(true)}
            className="inline-flex items-center space-x-1.5 px-3 py-1.5 bg-brand-600 hover:bg-brand-700 text-white rounded-lg text-xs font-semibold shadow-xs transition"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Add Algorithm Version</span>
          </button>
        </div>
      </div>

      {/* Model Info Card */}
      {modelDetail && (
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs">
          <div className="flex items-start justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2.5 rounded-xl bg-purple-50 text-purple-600">
                <BrainCircuit className="w-6 h-6" />
              </div>
              <div>
                <div className="flex items-center space-x-2">
                  <h2 className="text-base font-bold text-slate-900">{modelDetail.model_name}</h2>
                  <span className="text-[10px] font-semibold px-2 py-0.5 bg-purple-100 text-purple-800 rounded-full">
                    {modelDetail.model_type}
                  </span>
                </div>
                <p className="text-xs text-slate-500 mt-1">{modelDetail.description}</p>
              </div>
            </div>

            <div className="text-right text-xs text-slate-500">
              <p>Owner: <span className="font-semibold text-slate-700">{modelDetail.owner?.name}</span></p>
              <p className="font-mono text-[11px] text-slate-400 mt-0.5">Created: {modelDetail.created_date}</p>
            </div>
          </div>
        </div>
      )}

      {/* Versions List */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700">
            Registered Versions ({modelDetail?.versions?.length || 0})
          </h3>
          <span className="text-[11px] text-slate-400 font-mono">
            Table: model_version
          </span>
        </div>

        <div className="divide-y divide-slate-100">
          {modelDetail?.versions && modelDetail.versions.length > 0 ? (
            modelDetail.versions.map((ver) => (
              <div key={ver.model_version_id} className="p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:bg-slate-50/70 transition">
                <div className="flex items-center space-x-4">
                  <div className="w-10 h-10 rounded-xl bg-slate-100 border border-slate-200 flex items-center justify-center font-mono font-bold text-slate-700 text-xs">
                    v{ver.version_number}
                  </div>
                  <div>
                    <div className="flex items-center space-x-2">
                      <h4 className="text-sm font-bold text-slate-800 flex items-center space-x-1.5">
                        <Cpu className="w-3.5 h-3.5 text-slate-400" />
                        <span>{ver.algorithm}</span>
                      </h4>
                      <span className="text-[10px] font-mono text-slate-400 bg-slate-100 px-1.5 py-0.5 rounded">
                        ID: #{ver.model_version_id}
                      </span>
                    </div>
                    <div className="flex items-center space-x-3 text-[11px] text-slate-500 mt-1">
                      <span className="flex items-center space-x-1">
                        <Calendar className="w-3 h-3 text-slate-400" />
                        <span>Registered: {ver.created_date}</span>
                      </span>
                      <span>•</span>
                      <span className="text-emerald-600 font-medium">Joblib Serialized</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-3 self-end sm:self-auto">
                  <button
                    onClick={() => {
                      if (onLaunchEvaluation) onLaunchEvaluation(ver.model_version_id);
                      onNavigate('evaluations');
                    }}
                    className="inline-flex items-center space-x-1.5 px-3.5 py-1.5 bg-brand-600 hover:bg-brand-700 text-white rounded-lg text-xs font-semibold shadow-xs transition"
                  >
                    <PlayCircle className="w-3.5 h-3.5" />
                    <span>Run Evaluation</span>
                  </button>
                </div>
              </div>
            ))
          ) : (
            <div className="p-8 text-center text-xs text-slate-400">
              No versions created for this model yet. Click "Add Algorithm Version" above.
            </div>
          )}
        </div>
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl border border-slate-200">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <h3 className="text-sm font-bold text-slate-900">Add Algorithm Version</h3>
              <button onClick={() => setShowModal(false)} className="text-slate-400 hover:text-slate-600 text-lg leading-none">
                &times;
              </button>
            </div>

            <form onSubmit={handleCreateVersion} className="mt-4 space-y-4 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Version Number *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. 2.0"
                  value={versionNumber}
                  onChange={(e) => setVersionNumber(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg font-mono focus:outline-hidden"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Classifier Algorithm *</label>
                <select
                  value={algorithm}
                  onChange={(e) => setAlgorithm(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg focus:outline-hidden font-medium"
                >
                  <option value="Logistic Regression">Logistic Regression (Linear baseline)</option>
                  <option value="Random Forest">Random Forest Classifier (Ensemble)</option>
                  <option value="Decision Tree">Decision Tree Classifier (Interpretable)</option>
                </select>
                <p className="text-[10px] text-slate-400 mt-1">
                  Evaluated using Scikit-learn with leak-free preprocessing pipeline.
                </p>
              </div>

              <div className="pt-3 border-t border-slate-100 flex items-center justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-3 py-1.5 rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50 font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-4 py-1.5 bg-brand-600 hover:bg-brand-700 text-white rounded-lg font-semibold shadow-xs disabled:opacity-50"
                >
                  {submitting ? 'Adding...' : 'Create Model Version'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
