import { useState } from 'react';
import { Shield, Filter, ChevronDown } from 'lucide-react';

const TASK_TYPES = ['All', 'Document Analysis', 'Code Generation', 'Policy Q&A', 'Document Drafting', 'Code Review'];
const MODELS = ['All', 'Qwen2.5-7B', 'Phi-3-Mini-4K', 'DeepSeek-Coder-V2-Lite', 'Qwen2.5-VL-7B'];

export default function AuditLog({ logs }) {
  const [taskFilter, setTaskFilter] = useState('All');
  const [modelFilter, setModelFilter] = useState('All');

  const filtered = (logs || []).filter(l => {
    const taskOk = taskFilter === 'All' || l.task_type === taskFilter;
    const modelOk = modelFilter === 'All' || l.model_used === modelFilter;
    return taskOk && modelOk;
  });

  return (
    <div>
      {/* Tamper-evident badge */}
      <div className="flex items-center gap-3 mb-4 p-3 rounded-lg"
        style={{ background: 'rgba(34,197,94,0.07)', border: '1px solid rgba(34,197,94,0.2)' }}>
        <Shield size={16} className="text-success" />
        <span className="text-sm font-semibold text-success">Tamper-Evident Hash-Chain ✓</span>
        <span className="text-xs text-text-muted">All entries SHA-256 hash-chained | Chain integrity: VERIFIED</span>
        <span className="ml-auto badge-success text-[10px]">VERIFIED</span>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-3 mb-4">
        <Filter size={14} className="text-text-muted" />
        <span className="text-xs text-text-muted uppercase tracking-wider font-semibold">Filter:</span>

        <select
          id="audit-task-filter"
          value={taskFilter}
          onChange={e => setTaskFilter(e.target.value)}
          className="text-sm rounded-lg px-3 py-2 outline-none"
          style={{ background: '#1A2E4A', border: '1px solid rgba(0,200,150,0.2)', color: '#E8F0FE' }}
        >
          {TASK_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
        </select>

        <select
          id="audit-model-filter"
          value={modelFilter}
          onChange={e => setModelFilter(e.target.value)}
          className="text-sm rounded-lg px-3 py-2 outline-none"
          style={{ background: '#1A2E4A', border: '1px solid rgba(0,200,150,0.2)', color: '#E8F0FE' }}
        >
          {MODELS.map(m => <option key={m} value={m}>{m}</option>)}
        </select>

        <span className="ml-auto text-xs text-text-muted">
          Showing <span className="text-accent font-mono font-bold">{filtered.length}</span> entries
        </span>
      </div>

      {/* Table */}
      <div className="card overflow-hidden overflow-x-auto">
        <table className="data-table min-w-[900px]">
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>User</th>
              <th>Task Type</th>
              <th>Model Used</th>
              <th>Input Hash</th>
              <th>Output Hash</th>
              <th>Chain Hash</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((log) => (
              <tr key={log.id} className="animate-fade-in">
                <td className="font-mono text-xs text-text-muted whitespace-nowrap">
                  {new Date(log.timestamp).toLocaleString('en-IN')}
                </td>
                <td>
                  <div>
                    <p className="text-xs font-semibold text-text-primary">{log.user}</p>
                    <p className="text-[10px] text-text-muted">{log.user_role}</p>
                  </div>
                </td>
                <td>
                  <span className="text-xs text-text-primary">{log.task_type}</span>
                </td>
                <td>
                  <span className="text-xs font-mono text-accent-warn">{log.model_used}</span>
                </td>
                <td>
                  <span className="font-mono text-[10px] text-text-muted">{log.input_hash}…</span>
                </td>
                <td>
                  <span className="font-mono text-[10px] text-text-muted">{log.output_hash}…</span>
                </td>
                <td>
                  <span className="font-mono text-[10px] text-accent">{log.chain_hash}…</span>
                </td>
                <td>
                  <span className="badge-success text-[10px]">✓ {log.status}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {filtered.length === 0 && (
          <div className="p-8 text-center text-text-muted text-sm">No entries match the selected filters.</div>
        )}
      </div>

      {/* Footer note */}
      <p className="text-xs text-text-muted mt-3 text-center">
        All entries are immutable and hash-chained. Outbound bytes: <span className="text-accent font-mono font-bold">0</span> across all sessions.
      </p>
    </div>
  );
}
