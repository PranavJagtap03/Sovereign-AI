import { useEffect, useState } from 'react';
import ModelRouter from '../components/ModelRouter';
import axios from 'axios';
import { Network, Activity } from 'lucide-react';

export default function ModelRouterPage() {
  const [models, setModels] = useState(null);

  useEffect(() => {
    const load = async () => {
      try {
        const res = await axios.get('http://localhost:8000/api/system/status', { timeout: 3000 });
        setModels(res.data.models?.list);
      } catch { /* use defaults in component */ }
    };
    load();
  }, []);

  return (
    <div className="max-w-4xl">
      <div className="mb-8">
        <h1 className="text-xl font-bold text-text-primary flex items-center gap-2">
          <Network size={20} className="text-accent" />
          Multi-Model Routing Diagram
        </h1>
        <p className="text-sm text-text-muted mt-0.5">
          LiteLLM proxy routes tasks to the optimal model based on type classification
        </p>
      </div>

      {/* Routing legend */}
      <div className="flex gap-4 mb-8 text-xs">
        {[
          { label: 'Text/RAG tasks → Phi-3-Mini', color: '#5B8DEF' },
          { label: 'Vision/Document → Qwen2.5-VL', color: '#00C896' },
          { label: 'Code/Reasoning → DeepSeek-Coder', color: '#F5A623' },
        ].map(l => (
          <div key={l.label} className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full" style={{ background: l.color }} />
            <span className="text-text-muted">{l.label}</span>
          </div>
        ))}
      </div>

      {/* Diagram */}
      <div className="card p-8 pt-16 relative">
        <ModelRouter models={models} />
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-3 gap-4 mt-6">
        {[
          { label: 'Phi-3-Mini-4K', tasks: 14, lat: '1.2s', type: 'Text/RAG', color: '#5B8DEF' },
          { label: 'Qwen2.5-VL-7B', tasks: 22, lat: '2.8s', type: 'Vision/Doc', color: '#00C896' },
          { label: 'DeepSeek-Coder', tasks: 11, lat: '3.5s', type: 'Code', color: '#F5A623' },
        ].map(m => (
          <div key={m.label} className="card p-4">
            <div className="flex items-center gap-2 mb-3">
              <Activity size={14} style={{ color: m.color }} />
              <span className="text-xs font-semibold text-text-muted uppercase">{m.type}</span>
            </div>
            <p className="text-sm font-bold text-text-primary mb-3">{m.label}</p>
            <div className="flex justify-between text-xs">
              <div>
                <p className="text-text-muted">Tasks today</p>
                <p className="font-mono font-bold" style={{ color: m.color }}>{m.tasks}</p>
              </div>
              <div className="text-right">
                <p className="text-text-muted">Avg latency</p>
                <p className="font-mono font-bold text-accent-warn">{m.lat}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
