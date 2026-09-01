import { Zap } from 'lucide-react';

const SCENARIOS = [
  {
    id: 'analysis',
    emoji: '📊',
    label: 'Analyze engineering report PDF → Excel summary',
    task: 'Analyze this equipment inspection report and create an Excel summary with defect counts by category, severity classification (Critical/Major/Minor), and recommended action plan.',
    format: 'Excel',
    file: 'Equipment_Inspection_Q3_2026.pdf',
    scenario: 'analysis',
  },
  {
    id: 'draft',
    emoji: '📝',
    label: 'Draft approval note from policy document',
    task: 'What is the approval process for high-value procurement according to our procurement policy? Draft a formal approval note for a ₹45 lakh equipment purchase.',
    format: 'Word Doc',
    file: null,
    scenario: 'text',
  },
  {
    id: 'code',
    emoji: '💻',
    label: 'Write Python data parser from requirements',
    task: 'Write a Python script to parse our JSON sensor logs and flag anomalies above 3 standard deviations. Include error handling, logging, and a CLI interface.',
    format: 'Code',
    file: null,
    scenario: 'code',
  },
  {
    id: 'qa',
    emoji: '🔍',
    label: 'Answer question from internal SOP',
    task: 'According to our SOP manual, what is the standard document approval workflow? Provide step-by-step procedure with responsible authorities.',
    format: 'Word Doc',
    file: null,
    scenario: 'rag',
  },
];

export default function DemoScenarios({ onSelect }) {
  return (
    <div className="mb-6">
      <div className="flex items-center gap-2 mb-3">
        <Zap size={14} className="text-accent-warn" />
        <span className="text-xs font-semibold text-text-muted uppercase tracking-wider">
          Quick Launch Demos
        </span>
      </div>
      <div className="grid grid-cols-1 gap-2">
        {SCENARIOS.map((s) => (
          <button
            key={s.id}
            id={`demo-${s.id}`}
            onClick={() => onSelect(s)}
            className="text-left px-4 py-3 rounded-lg transition-all duration-200 group"
            style={{
              background: 'rgba(0,200,150,0.04)',
              border: '1px solid rgba(0,200,150,0.15)',
            }}
            onMouseEnter={e => {
              e.currentTarget.style.background = 'rgba(0,200,150,0.08)';
              e.currentTarget.style.borderColor = 'rgba(0,200,150,0.35)';
            }}
            onMouseLeave={e => {
              e.currentTarget.style.background = 'rgba(0,200,150,0.04)';
              e.currentTarget.style.borderColor = 'rgba(0,200,150,0.15)';
            }}
          >
            <span className="text-sm font-medium text-text-primary">
              {s.emoji} {s.label}
            </span>
          </button>
        ))}
      </div>
    </div>
  );
}
