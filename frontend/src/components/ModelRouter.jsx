const DEFAULT_CONFIGS = {
  'Phi-3-Mini-4K': {
    type: 'Text / RAG',
    vram_pct: 30,
    tasks_today: 16,
    size: '3.8B params (Q4_K_M)',
    color: '#5B8DEF',
    taskTypes: ['Policy Q&A', 'ChromaDB RAG', 'Guardian Review'],
  },
  'Qwen2.5-VL-7B': {
    type: 'Vision / Document',
    vram_pct: 65,
    tasks_today: 22,
    size: '7.2B params (Q4_K_M)',
    color: '#00C896',
    taskTypes: ['OCR Inspection', 'Table Extraction', 'Engineering PDFs'],
  },
  'Qwen2.5-7B': {
    type: 'Text / Reasoning',
    vram_pct: 65,
    tasks_today: 17,
    size: '7.2B params (Q4_K_M)',
    color: '#00C896',
    taskTypes: ['Executive Drafting', 'Policy Notes', 'Summaries'],
  },
  'DeepSeek-Coder-V2-Lite': {
    type: 'Code / Reasoning',
    vram_pct: 85,
    tasks_today: 11,
    size: '15.7B params (Q4_K_M)',
    color: '#F5A623',
    taskTypes: ['Code Generation', 'AST Syntax', 'gVisor Sandbox'],
  },
};

export default function ModelRouter({ models }) {
  const MODEL_DATA = (models && Array.isArray(models) && models.length > 0
    ? models
    : [
        { name: 'Phi-3-Mini-4K', ...DEFAULT_CONFIGS['Phi-3-Mini-4K'] },
        { name: 'Qwen2.5-VL-7B', ...DEFAULT_CONFIGS['Qwen2.5-VL-7B'] },
        { name: 'DeepSeek-Coder-V2-Lite', ...DEFAULT_CONFIGS['DeepSeek-Coder-V2-Lite'] },
      ]
  ).map(m => {
    const fallback = DEFAULT_CONFIGS[m.name] || {
      type: m.type || 'General AI',
      vram_pct: m.vram_pct || 50,
      tasks_today: m.tasks_today || 0,
      size: m.size || 'Local Model',
      color: '#00C896',
      taskTypes: ['Local Inference', 'Sovereign Enclave'],
    };

    return {
      name: m.name,
      type: m.type || fallback.type,
      vram_pct: m.vram_pct ?? fallback.vram_pct,
      tasks_today: m.tasks_today ?? fallback.tasks_today,
      size: m.size || fallback.size,
      color: m.color || fallback.color,
      taskTypes: m.taskTypes || m.task_types || fallback.taskTypes || ['Sovereign Task'],
    };
  });

  return (
    <div className="relative">
      {/* Central router node */}
      <div className="flex flex-col items-center mb-8">
        <div className="card p-4 text-center w-52"
          style={{ border: '1px solid rgba(0,200,150,0.4)', boxShadow: '0 0 24px rgba(0,200,150,0.15)' }}>
          <div className="text-lg mb-1">🔀</div>
          <div className="font-bold text-text-primary text-sm">Task Router</div>
          <div className="text-xs text-text-muted mt-1">LiteLLM Proxy v1.47</div>
          <div className="text-[10px] font-mono text-accent mt-2">localhost:4000</div>
        </div>

        {/* Arrow down */}
        <div className="w-px h-6 mt-1" style={{ background: 'rgba(0,200,150,0.4)' }} />
        <div className="text-accent text-xs">↓ routes to</div>
      </div>

      {/* Model boxes */}
      <div className="grid grid-cols-3 gap-4">
        {MODEL_DATA.map((model, i) => (
          <div key={model.name} className="card p-4 animate-slide-up" style={{ animationDelay: `${i * 100}ms` }}>
            {/* Model header */}
            <div className="flex items-start justify-between mb-3">
              <div className="w-2.5 h-2.5 rounded-full animate-pulse-green mt-1"
                style={{ background: model.color }} />
              <span className="text-[10px] font-mono text-text-muted">{model.size}</span>
            </div>

            <h4 className="font-bold text-sm text-text-primary mb-0.5">{model.name}</h4>
            <p className="text-xs text-text-muted mb-3">{model.type}</p>

            {/* VRAM bar */}
            <div className="mb-3">
              <div className="flex justify-between text-[10px] text-text-muted mb-1">
                <span>VRAM</span>
                <span className="font-mono">{model.vram_pct}%</span>
              </div>
              <div className="vram-bar">
                <div
                  className="vram-fill"
                  style={{
                    width: `${model.vram_pct}%`,
                    background: `linear-gradient(90deg, ${model.color}88, ${model.color})`,
                  }}
                />
              </div>
            </div>

            {/* Task types */}
            <div className="flex flex-wrap gap-1 mb-3">
              {(model.taskTypes || []).map(t => (
                <span key={t} className="text-[10px] px-2 py-0.5 rounded"
                  style={{ background: `${model.color}15`, color: model.color, border: `1px solid ${model.color}30` }}>
                  {t}
                </span>
              ))}
            </div>

            {/* Tasks today */}
            <div className="flex items-center justify-between text-[11px]">
              <span className="text-text-muted">Tasks today</span>
              <span className="font-mono font-bold" style={{ color: model.color }}>{model.tasks_today}</span>
            </div>
          </div>
        ))}
      </div>

      {/* SVG connection lines above */}
      <div className="absolute top-[72px] left-0 right-0" style={{ height: '60px', pointerEvents: 'none' }}>
        <svg width="100%" height="60" preserveAspectRatio="none">
          <defs>
            <marker id="arrow-head" markerWidth="6" markerHeight="6" refX="3" refY="3" orient="auto">
              <path d="M0,0 L0,6 L6,3 z" fill="rgba(0,200,150,0.6)" />
            </marker>
          </defs>
          {/* Left line */}
          <line x1="50%" y1="0" x2="16.67%" y2="60"
            stroke="rgba(0,200,150,0.4)" strokeWidth="1.5" strokeDasharray="6,3"
            markerEnd="url(#arrow-head)" className="flow-arrow" />
          {/* Center line */}
          <line x1="50%" y1="0" x2="50%" y2="60"
            stroke="rgba(0,200,150,0.6)" strokeWidth="1.5" strokeDasharray="6,3"
            markerEnd="url(#arrow-head)" className="flow-arrow" />
          {/* Right line */}
          <line x1="50%" y1="0" x2="83.33%" y2="60"
            stroke="rgba(0,200,150,0.4)" strokeWidth="1.5" strokeDasharray="6,3"
            markerEnd="url(#arrow-head)" className="flow-arrow" />
        </svg>
      </div>

      {/* Input node above */}
      <div className="absolute" style={{ top: '-48px', left: '50%', transform: 'translateX(-50%)' }}>
        <div className="px-4 py-2 rounded-lg text-xs font-semibold"
          style={{ background: 'rgba(15,43,91,0.8)', border: '1px solid rgba(0,200,150,0.3)', color: '#E8F0FE' }}>
          📥 Task Input
        </div>
        <div className="w-px h-5 mx-auto" style={{ background: 'rgba(0,200,150,0.4)' }} />
      </div>
    </div>
  );
}
