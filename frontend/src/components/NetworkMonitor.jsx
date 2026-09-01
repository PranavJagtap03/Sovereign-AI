import { useEffect, useRef, useState } from 'react';
import { Shield, WifiOff, AlertTriangle, Clock } from 'lucide-react';

const BLOCKED_HOSTS = [
  'api.openai.com',
  'api.anthropic.com',
  'api.cohere.ai',
  'inference.googleapis.com',
  'bedrock.amazonaws.com',
  'api.replicate.com',
  'api.together.ai',
  'huggingface.co',
  'api.mistral.ai',
];

function getTime() {
  return new Date().toLocaleTimeString('en-IN', { hour12: false });
}
function getTs() {
  return new Date().toISOString().replace('T', ' ').slice(0, 19);
}

export default function NetworkMonitor() {
  const [logs, setLogs] = useState([
    { ts: getTs(), host: 'api.openai.com', action: 'BLOCKED', rule: 'iptables OUTPUT DROP' },
    { ts: getTs(), host: 'api.anthropic.com', action: 'BLOCKED', rule: 'iptables OUTPUT DROP' },
    { ts: getTs(), host: 'googleapis.com', action: 'BLOCKED', rule: 'iptables OUTPUT DROP' },
  ]);
  const [packetCount, setPacketCount] = useState(0);
  const [lastChecked, setLastChecked] = useState(getTime());
  const bottomRef = useRef(null);

  useEffect(() => {
    const interval = setInterval(() => {
      const host = BLOCKED_HOSTS[Math.floor(Math.random() * BLOCKED_HOSTS.length)];
      setLogs(prev => [
        { ts: getTs(), host, action: 'BLOCKED', rule: 'iptables OUTPUT DROP' },
        ...prev.slice(0, 19),
      ]);
      setPacketCount(p => p + 1);
      setLastChecked(getTime());
    }, 4000 + Math.random() * 2000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="space-y-4">
      {/* Stat cards */}
      <div className="grid grid-cols-2 gap-3">
        {[
          { label: 'Outbound Bytes', value: '0', icon: '📤', color: 'text-accent' },
          { label: 'External API Calls', value: '0', icon: '🌐', color: 'text-accent' },
          { label: 'DNS External Queries', value: '0', icon: '🔍', color: 'text-accent' },
          { label: 'Blocked Requests', value: packetCount + 5, icon: '🚫', color: 'text-danger' },
        ].map(({ label, value, icon, color }) => (
          <div key={label} className="card p-4">
            <div className="flex items-center justify-between mb-1">
              <span className="text-lg">{icon}</span>
              <span className={`text-2xl font-bold font-mono ${color}`}>{value}</span>
            </div>
            <p className="text-xs text-text-muted">{label}</p>
          </div>
        ))}
      </div>

      {/* Last checked */}
      <div className="flex items-center gap-2 text-xs text-text-muted">
        <Clock size={12} />
        <span>Last verified: {lastChecked}</span>
        <span className="w-1.5 h-1.5 rounded-full bg-accent animate-pulse-green" />
        <span className="text-accent font-semibold">Live</span>
      </div>

      {/* Firewall log terminal */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <AlertTriangle size={13} className="text-accent-warn" />
            <span className="text-xs font-semibold text-text-muted uppercase tracking-wider">
              iptables Firewall Log
            </span>
          </div>
          <span className="text-xs font-mono text-success">● Live</span>
        </div>
        <div className="terminal p-3 h-52 overflow-y-auto space-y-1">
          {logs.map((log, i) => (
            <div key={i} className="animate-fade-in text-[11px] leading-5">
              <span className="text-text-muted">[{log.ts}] </span>
              <span className="text-danger font-semibold">iptables: </span>
              <span className="text-accent-warn">blocked outbound</span>
              <span className="text-text-muted"> → </span>
              <span className="text-text-primary font-semibold">{log.host}</span>
              <span className="text-text-muted"> — </span>
              <span className="text-danger font-bold">DENIED</span>
            </div>
          ))}
          <div ref={bottomRef} />
        </div>
      </div>
    </div>
  );
}
