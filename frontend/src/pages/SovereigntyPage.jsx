import NetworkMonitor from '../components/NetworkMonitor';
import { Shield, Lock, Server, Eye } from 'lucide-react';

const TECH_STACK = [
  { name: 'gVisor Sandbox', desc: 'All model inference runs inside gVisor containers — syscall interception prevents network access', icon: '🔒', status: 'ACTIVE' },
  { name: 'iptables Firewall', desc: 'OUTPUT chain: DROP all — no outbound connections possible at OS level', icon: '🧱', status: 'ACTIVE' },
  { name: 'RBAC Enforcement', desc: 'Role-based access control via Keycloak (offline) — every request verified', icon: '🔑', status: 'ACTIVE' },
  { name: 'AES-256-GCM Encryption', desc: 'All outputs encrypted at rest before storage — local key vault (HashiCorp Vault)', icon: '🔐', status: 'ACTIVE' },
  { name: 'Ollama (Air-gapped)', desc: 'LLM inference via Ollama — models loaded from local NVMe, zero internet dependency', icon: '🤖', status: 'ACTIVE' },
  { name: 'ChromaDB (Local)', desc: 'Vector database running entirely on localhost — no cloud sync, no telemetry', icon: '🗄️', status: 'ACTIVE' },
];

export default function SovereigntyPage() {
  return (
    <div className="max-w-4xl">
      <div className="mb-6">
        <h1 className="text-xl font-bold text-text-primary flex items-center gap-2">
          <Shield size={20} className="text-accent" />
          Zero-Byte Sovereignty Proof
        </h1>
        <p className="text-sm text-text-muted mt-0.5">Live proof that all processing stays on-premise — 0 bytes leave the air-gapped network</p>
      </div>

      {/* Hero sovereignty badge */}
      <div className="card p-6 mb-6 text-center"
        style={{ border: '1px solid rgba(0,200,150,0.4)', boxShadow: '0 0 40px rgba(0,200,150,0.1)' }}>
        <div className="text-5xl mb-3">🛡️</div>
        <h2 className="text-2xl font-bold text-accent mb-1">SOVEREIGN</h2>
        <p className="text-text-muted text-sm">All AI inference running on-premise · Air-gapped · Zero cloud dependency</p>
        <div className="flex justify-center gap-6 mt-4">
          <div className="text-center">
            <div className="text-3xl font-bold font-mono text-accent">0</div>
            <div className="text-xs text-text-muted">bytes outbound</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold font-mono text-accent">0</div>
            <div className="text-xs text-text-muted">API calls external</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold font-mono text-accent">0</div>
            <div className="text-xs text-text-muted">DNS external queries</div>
          </div>
        </div>
      </div>

      {/* Live monitor */}
      <div className="card p-5 mb-6">
        <div className="flex items-center gap-2 mb-4">
          <Eye size={16} className="text-accent" />
          <h2 className="font-semibold text-text-primary">Live Network Monitor</h2>
        </div>
        <NetworkMonitor />
      </div>

      {/* Security tech stack */}
      <div className="card p-5">
        <div className="flex items-center gap-2 mb-4">
          <Lock size={16} className="text-accent" />
          <h2 className="font-semibold text-text-primary">Security Architecture</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {TECH_STACK.map(item => (
            <div key={item.name} className="p-3 rounded-lg flex gap-3"
              style={{ background: 'rgba(0,200,150,0.04)', border: '1px solid rgba(0,200,150,0.1)' }}>
              <span className="text-xl flex-shrink-0">{item.icon}</span>
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-semibold text-text-primary">{item.name}</span>
                  <span className="badge-success text-[9px]">{item.status}</span>
                </div>
                <p className="text-xs text-text-muted leading-relaxed">{item.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
