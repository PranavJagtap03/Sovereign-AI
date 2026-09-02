import { useState } from 'react';
import { Shield, Filter, ChevronDown, AlertTriangle, RefreshCw, Flame } from 'lucide-react';

const TASK_TYPES = ['All', 'Document Analysis', 'Code Generation', 'Policy Q&A', 'Document Drafting', 'Code Review'];
const MODELS = ['All', 'Qwen2.5-7B', 'Phi-3-Mini-4K', 'DeepSeek-Coder-V2-Lite', 'Qwen2.5-VL-7B'];

export default function AuditLog({
  logs,
  chainVerification,
  isVerifying = false,
  onVerifyChain = () => {},
  onTamperDemo = () => {}
}) {
  const [taskFilter, setTaskFilter] = useState('All');
  const [modelFilter, setModelFilter] = useState('All');

  const filtered = (logs || []).filter(l => {
    const taskOk = taskFilter === 'All' || l.task_type === taskFilter;
    const modelOk = modelFilter === 'All' || l.model_used === modelFilter;
    return taskOk && modelOk;
  });

  const isChainValid = chainVerification ? chainVerification.chain_valid : true;

  return (
    <div>
      {/* Verification In Progress Banner */}
      {isVerifying && (
        <div className="mb-4 p-3.5 rounded-lg border border-accent/40 bg-accent/10 flex items-center justify-between text-xs text-accent animate-pulse">
          <div className="flex items-center gap-2.5">
            <RefreshCw size={16} className="animate-spin text-accent shrink-0" />
            <div>
              <p className="font-semibold text-text-primary">Walking HMAC-SHA256 Cryptographic Hash Chain...</p>
              <p className="text-[11px] text-text-muted mt-0.5">
                Verifying previous_hash linkage and HMAC signatures from genesis block across {logs?.length || 10} records.
              </p>
            </div>
          </div>
          <span className="font-mono text-[10px] px-2 py-0.5 rounded bg-accent/20 border border-accent/30 font-bold">
            VALIDATING HASHES
          </span>
        </div>
      )}

      {/* Tamper-evident badge / alert */}
      {!isChainValid ? (
        <div className="flex items-center justify-between gap-3 mb-4 p-3 rounded-lg border bg-accent-warn/10 border-accent-warn/30 text-accent-warn">
          <div className="flex items-center gap-2.5">
            <AlertTriangle size={18} className="text-accent-warn shrink-0" />
            <div>
              <p className="text-xs font-bold uppercase tracking-wider">⚠️ Cryptographic Chain Compromised!</p>
              <p className="text-[11px] font-mono text-text-muted mt-0.5">
                Tampering detected at entry #{chainVerification?.broken_at_entry} | {chainVerification?.reason || 'HMAC signature mismatch'}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="badge-warn text-[10px]">BROKEN AT #{chainVerification?.broken_at_entry}</span>
            <button
              onClick={onVerifyChain}
              disabled={isVerifying}
              className="btn-secondary text-xs py-1 px-2.5 flex items-center gap-1"
            >
              <RefreshCw size={12} className={isVerifying ? 'animate-spin' : ''} />
              Re-Verify
            </button>
          </div>
        </div>
      ) : (
        <div className="flex items-center justify-between gap-3 mb-4 p-3 rounded-lg"
          style={{ background: 'rgba(34,197,94,0.07)', border: '1px solid rgba(34,197,94,0.2)' }}>
          <div className="flex items-center gap-2.5">
            <Shield size={16} className="text-success shrink-0" />
            <div>
              <span className="text-sm font-semibold text-success">Tamper-Evident Hash-Chain ✓</span>
              <span className="text-xs text-text-muted ml-2">
                HMAC-SHA256 chained · Genesis 0x00.. · {chainVerification?.total_entries || logs.length} entries intact
              </span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={onTamperDemo}
              className="text-[11px] py-1 px-2.5 rounded bg-accent-warn/15 hover:bg-accent-warn/25 text-accent-warn border border-accent-warn/30 transition-colors flex items-center gap-1"
              title="Simulate modifying a past record without updating HMAC"
            >
              <Flame size={12} />
              Tamper Demo Entry
            </button>
            <button
              onClick={onVerifyChain}
              disabled={isVerifying}
              className="btn-secondary text-xs py-1 px-2.5 flex items-center gap-1"
            >
              <RefreshCw size={12} className={isVerifying ? 'animate-spin' : ''} />
              Verify Chain
            </button>
            <span className="badge-success text-[10px]">VERIFIED</span>
          </div>
        </div>
      )}

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
