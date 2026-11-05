import React, { useState, useEffect } from 'react';
import {
  FileCode2,
  Database,
  Layers,
  BrainCircuit,
  CheckCircle2,
  ExternalLink,
  Server,
  BookOpen,
  Cpu,
  ShieldCheck,
  Table,
  Key
} from 'lucide-react';
import { api } from '../services/api';

export default function AboutPage() {
  const [health, setHealth] = useState(null);

  useEffect(() => {
    api.checkHealth().then(setHealth).catch(() => setHealth({ status: 'offline' }));
  }, []);

  const entities = [
    {
      name: 'USER',
      id: 1,
      pk: 'user_id',
      fks: [],
      cols: ['user_id', 'name', 'email (UNIQUE)', 'role', 'department'],
      purpose: 'Data practitioners, data engineers, and ML model owners managing platform assets.'
    },
    {
      name: 'DATA_SOURCE',
      id: 2,
      pk: 'source_id',
      fks: [],
      cols: ['source_id', 'source_name', 'source_type', 'location'],
      purpose: 'Ingestion origins (S3 Data Lakes, relational databases, streaming sinks).'
    },
    {
      name: 'DATASET',
      id: 3,
      pk: 'dataset_id',
      fks: ['source_id -> DATA_SOURCE', 'owner_id -> USER'],
      cols: ['dataset_id', 'dataset_name', 'description', 'source_id', 'owner_id', 'created_date'],
      purpose: 'Logical business datasets representing specific transactional domains.'
    },
    {
      name: 'DATASET_VERSION',
      id: 4,
      pk: 'dataset_version_id',
      fks: ['dataset_id -> DATASET'],
      cols: ['dataset_version_id', 'dataset_id', 'version_number', 'record_count', 'created_date', 'UNIQUE(dataset_id, version_number)'],
      purpose: 'Immutable timestamped CSV snapshots maintaining version history and record counts.'
    },
    {
      name: 'DATA_QUALITY_CHECK',
      id: 5,
      pk: 'quality_check_id',
      fks: ['dataset_id -> DATASET'],
      cols: ['quality_check_id', 'dataset_id', 'check_name', 'check_type', 'threshold'],
      purpose: 'Configured data validation rules (missingness, uniqueness, ranges, types).'
    },
    {
      name: 'DATA_QUALITY_RESULT',
      id: 6,
      pk: 'quality_result_id',
      fks: ['quality_check_id -> DATA_QUALITY_CHECK', 'dataset_version_id -> DATASET_VERSION'],
      cols: ['quality_result_id', 'quality_check_id', 'dataset_version_id', 'score (0..100)', 'status (PASSED/FAILED/WARNING)', 'execution_date'],
      purpose: 'Deterministic scores and verification statuses evaluated against real CSV data.'
    },
    {
      name: 'AI_MODEL',
      id: 7,
      pk: 'model_id',
      fks: ['owner_id -> USER'],
      cols: ['model_id', 'model_name', 'model_type', 'description', 'owner_id', 'created_date'],
      purpose: 'Machine learning model registry tracking architecture and model ownership.'
    },
    {
      name: 'MODEL_VERSION',
      id: 8,
      pk: 'model_version_id',
      fks: ['model_id -> AI_MODEL'],
      cols: ['model_version_id', 'model_id', 'version_number', 'algorithm', 'created_date', 'UNIQUE(model_id, version_number)'],
      purpose: 'Specific algorithmic implementations (Logistic Regression, Random Forest, Decision Tree).'
    },
    {
      name: 'EVALUATION_RUN',
      id: 9,
      pk: 'evaluation_id',
      fks: ['model_version_id -> MODEL_VERSION', 'dataset_version_id -> DATASET_VERSION', 'executed_by -> USER'],
      cols: ['evaluation_id', 'model_version_id', 'dataset_version_id', 'executed_by', 'execution_date', 'status (COMPLETED/RUNNING/FAILED)'],
      purpose: 'Central operational entity orchestrating real Scikit-learn classification pipeline runs.'
    },
    {
      name: 'EVALUATION_RESULT',
      id: 10,
      pk: 'result_id',
      fks: ['evaluation_id -> EVALUATION_RUN (UNIQUE 1:1)'],
      cols: ['result_id', 'evaluation_id', 'accuracy (0..100)', 'precision_score (0..100)', 'recall_score (0..100)', 'f1_score (0..100)'],
      purpose: 'Classification performance metrics evaluated on holdout test splits.'
    },
    {
      name: 'DRIFT_DETECTION',
      id: 11,
      pk: 'drift_id',
      fks: ['evaluation_id -> EVALUATION_RUN'],
      cols: ['drift_id', 'evaluation_id', 'drift_score (>=0)', 'drift_status (LOW/MEDIUM/HIGH)', 'detected_date'],
      purpose: 'Population Stability Index (PSI) and Kolmogorov-Smirnov distribution shift tests.'
    },
    {
      name: 'RELIABILITY_SCORE',
      id: 12,
      pk: 'reliability_id',
      fks: ['evaluation_id -> EVALUATION_RUN (UNIQUE 1:1)'],
      cols: ['reliability_id', 'evaluation_id', 'data_quality_score', 'model_performance_score', 'drift_score', 'overall_score', 'rating (LOW/MEDIUM/HIGH)'],
      purpose: 'Consolidated weighted reliability index: 0.35 DQ + 0.45 Model + 0.20 Drift Health.'
    },
  ];

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-slate-900 tracking-tight">Architecture & DBMS Specification</h1>
        <p className="text-xs text-slate-500 mt-0.5">
          PES University DBMS Project — Academic design mapping, 12 relational entities, and technology stack.
        </p>
      </div>

      {/* Authors & Project Card */}
      <div className="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 rounded-2xl p-6 text-white shadow-xl border border-slate-800">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-center">
          <div>
            <span className="text-[10px] font-mono uppercase tracking-widest text-brand-400 bg-brand-900/60 px-2 py-0.5 rounded border border-brand-700/50">
              Department of Computer Science & Engineering
            </span>
            <h2 className="text-lg font-bold text-white mt-2">
              AI Model Evaluation & Data Reliability Platform
            </h2>
            <p className="text-xs text-slate-300 mt-1 leading-relaxed">
              Designed and implemented as a normalized relational database application integrating backend analytical services and an enterprise analytics user interface.
            </p>

            <div className="mt-4 pt-4 border-t border-slate-800/80 grid grid-cols-2 gap-3 text-xs">
              <div>
                <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Lead Developer</span>
                <span className="font-bold text-white">MOHAMMED ADAAN HAMAD</span>
                <span className="font-mono text-[11px] text-brand-300 block">SRN: PES2UG24CS279</span>
              </div>
              <div>
                <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Co-Developer</span>
                <span className="font-bold text-white">NAVYA KISHORE DASH</span>
                <span className="font-mono text-[11px] text-brand-300 block">SRN: PES2UG24CS307</span>
              </div>
            </div>
          </div>

          <div className="bg-slate-800/60 p-4 rounded-xl border border-slate-700/60 space-y-3 text-xs">
            <h4 className="font-bold text-white text-xs uppercase tracking-wider flex items-center space-x-2">
              <Server className="w-4 h-4 text-emerald-400" />
              <span>Runtime Environment Status</span>
            </h4>
            <div className="space-y-1.5 font-mono text-[11px]">
              <div className="flex justify-between py-1 border-b border-slate-700/40">
                <span className="text-slate-400">Database Engine:</span>
                <span className="text-emerald-400 font-bold">MySQL Server 8.0 (Port 3306)</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-700/40">
                <span className="text-slate-400">Backend Framework:</span>
                <span className="text-white">Python 3.12 + FastAPI + Uvicorn</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-700/40">
                <span className="text-slate-400">ORM & Driver:</span>
                <span className="text-white">SQLAlchemy 2.0 + PyMySQL</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-700/40">
                <span className="text-slate-400">ML & Analytics:</span>
                <span className="text-white">Pandas, NumPy, Scikit-learn, SciPy</span>
              </div>
              <div className="flex justify-between py-1">
                <span className="text-slate-400">API Documentation:</span>
                <a href="http://localhost:8000/docs" target="_blank" rel="noreferrer" className="text-brand-400 hover:underline flex items-center space-x-1">
                  <span>/docs (OpenAPI Swagger)</span>
                  <ExternalLink className="w-2.5 h-2.5" />
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 12 Core Entities Relational Grid */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-base font-bold text-slate-900">
              The 12 Core Relational Database Entities
            </h2>
            <p className="text-xs text-slate-500">
              Faithfully implementing the approved DBMS project submission DDL without removing or modifying relations.
            </p>
          </div>
          <span className="px-3 py-1 bg-brand-50 border border-brand-200 text-brand-700 rounded-full text-xs font-mono font-bold">
            12 Entities • 3NF Normalized
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {entities.map((ent) => (
            <div
              key={ent.id}
              className="bg-white rounded-xl border border-slate-200 p-4 shadow-xs flex flex-col justify-between hover:border-slate-300 transition"
            >
              <div>
                <div className="flex items-center justify-between pb-2 border-b border-slate-100">
                  <div className="flex items-center space-x-2">
                    <span className="w-5 h-5 rounded-md bg-brand-50 text-brand-700 font-mono text-[10px] font-bold flex items-center justify-center">
                      {ent.id}
                    </span>
                    <h3 className="font-bold font-mono text-xs text-slate-900">{ent.name}</h3>
                  </div>
                  <span className="text-[10px] font-mono text-emerald-600 bg-emerald-50 px-1.5 py-0.5 rounded border border-emerald-200">
                    PK: {ent.pk}
                  </span>
                </div>

                <p className="text-[11px] text-slate-600 mt-2 line-clamp-2">
                  {ent.purpose}
                </p>

                {/* Attributes */}
                <div className="mt-3 pt-2 border-t border-slate-100">
                  <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400 block mb-1">
                    Attributes:
                  </span>
                  <div className="flex flex-wrap gap-1 font-mono text-[10px]">
                    {ent.cols.map((col, idx) => (
                      <span key={idx} className="bg-slate-50 border border-slate-200 px-1.5 py-0.5 rounded text-slate-600">
                        {col}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Foreign Keys */}
                {ent.fks.length > 0 && (
                  <div className="mt-3 pt-2 border-t border-slate-100">
                    <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400 block mb-1">
                      Foreign Keys:
                    </span>
                    <div className="space-y-0.5 font-mono text-[10px] text-slate-500">
                      {ent.fks.map((fk, idx) => (
                        <div key={idx} className="flex items-center space-x-1 text-slate-700">
                          <Key className="w-2.5 h-2.5 text-amber-500 shrink-0" />
                          <span>{fk}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
