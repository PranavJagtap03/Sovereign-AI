import { useEffect, useState } from 'react';
import { Shield, Wifi, WifiOff } from 'lucide-react';

export default function StatusBar() {
  const [time, setTime] = useState(new Date());

  useEffect(() => {
    const t = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(t);
  }, []);

  return (
    <header
      className="flex items-center justify-between px-5 py-2.5 flex-shrink-0 border-b"
      style={{
        background: '#0D1B33',
        borderColor: 'rgba(0,200,150,0.12)',
        minHeight: '52px',
      }}
    >
      {/* Left — branding */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <Shield size={18} className="text-accent" />
          <span className="font-bold text-text-primary text-sm tracking-wide">
            Sovereign AI Workbench
          </span>
        </div>
        <span className="text-[10px] font-mono px-2 py-0.5 rounded"
          style={{ background: 'rgba(0,200,150,0.1)', border: '1px solid rgba(0,200,150,0.2)', color: '#00C896' }}>
          Code:201
        </span>
        <span className="text-[10px] font-mono px-2 py-0.5 rounded"
          style={{ background: 'rgba(91,141,239,0.1)', border: '1px solid rgba(91,141,239,0.2)', color: '#5B8DEF' }}>
          SIH 2026 | PS-26117
        </span>
      </div>

      {/* Right — sovereignty indicator + time */}
      <div className="flex items-center gap-5">
        {/* Air-gapped badge */}
        <div className="flex items-center gap-2">
          <span
            className="w-2.5 h-2.5 rounded-full animate-pulse-green flex-shrink-0"
            style={{ background: '#00C896' }}
          />
          <span className="text-xs font-semibold text-accent">Air-Gapped</span>
          <span className="text-xs font-mono text-text-muted">|</span>
          <WifiOff size={13} className="text-accent" />
          <span className="text-xs font-mono text-accent font-bold">0 bytes outbound</span>
        </div>

        {/* Time */}
        <span className="text-xs font-mono text-text-muted">
          {time.toLocaleTimeString('en-IN', { hour12: false })}
        </span>
      </div>
    </header>
  );
}
