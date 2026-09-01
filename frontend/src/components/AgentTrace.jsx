import { useState, useEffect } from 'react';
import {
  CheckCircle, Circle, Loader2, Download, ChevronDown, ChevronUp,
  Lock, Brain, BookOpen, Cog, ShieldCheck, FileDown
} from 'lucide-react';

const STEP_ICONS = {
  1: Lock,
  2: Brain,
  3: BookOpen,
  4: Cog,
  5: ShieldCheck,
  6: FileDown,
};

const STEP_DELAYS = [600, 900, 700, 1400, 600, 500]; // ms per step

function ReActLoop({ items }) {
  const [visible, setVisible] = useState(0);
  useEffect(() => {
    if (visible < items.length) {
      const t = setTimeout(() => setVisible(v => v + 1), 350);
      return () => clearTimeout(t);
    }
  }, [visible, items.length]);

  return (
    <div className="mt-3 space-y-1.5">
      {items.slice(0, visible).map((item, i) => (
        <div key={i} className="animate-step-in" style={{ animationDelay: '0ms' }}>
          {item.thought && (
            <div className="react-thought">
              <span className="text-blue-400 font-semibold">💭 Thought:</span>{' '}
              <span className="text-text-muted">{item.thought}</span>
            </div>
          )}
          {item.action && (
            <div className="react-action">
              <span className="text-accent font-semibold">⚡ Action:</span>{' '}
              <span className="text-green-300">{item.action}</span>
            </div>
          )}
          {item.observation && (
            <div className="react-observation">
              <span className="text-accent-warn font-semibold">👁 Obs:</span>{' '}
              <span className="text-yellow-200">{item.observation}</span>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

function StepRow({ step, isActive, isComplete, isPending, onDownload }) {
  const [expanded, setExpanded] = useState(false);
  const Icon = STEP_ICONS[step.step] || Circle;

  useEffect(() => {
    if (isActive || (isComplete && step.step === 4)) {
      setExpanded(true);
    }
  }, [isActive, isComplete, step.step]);

  return (
    <div
      className={`card p-4 transition-all duration-300 ${
        isActive ? 'card-glow' : isComplete ? 'card-active' : 'opacity-40'
      }`}
      style={{ animationDelay: '0ms' }}
    >
      <div className="flex items-start gap-3">
        {/* Status icon */}
        <div className="flex-shrink-0 mt-0.5">
          {isActive && !isComplete && (
            <Loader2 size={20} className="text-accent-warn animate-spin" />
          )}
          {isComplete && (
            <CheckCircle size={20} className="text-accent" />
          )}
          {isPending && (
            <Circle size={20} className="text-text-muted opacity-40" />
          )}
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-2">
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-mono text-text-muted">STEP {step.step}</span>
              <span className="text-sm font-semibold text-text-primary">
                {step.icon} {step.name}
              </span>
              {step.status === 'skipped' && (
                <span className="badge-warn text-[10px]">SKIPPED</span>
              )}
              {isComplete && step.status !== 'skipped' && (
                <span className="badge-success text-[10px]">PASSED</span>
              )}
            </div>
            {isComplete && (
              <button
                onClick={() => setExpanded(e => !e)}
                className="text-text-muted hover:text-text-primary transition-colors"
              >
                {expanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
              </button>
            )}
          </div>

          {/* Details */}
          {(isActive || isComplete) && (
            <p className="text-xs text-text-muted mt-1 leading-relaxed font-mono">
              → {step.details}
            </p>
          )}

          {/* Expanded sub-items */}
          {expanded && isComplete && step.sub_items?.length > 0 && (
            <div className="mt-2 space-y-1">
              {step.sub_items.map((item, i) => (
                <div key={i} className="text-xs text-text-muted font-mono pl-3 border-l border-accent/20">
                  {item}
                </div>
              ))}
            </div>
          )}

          {/* ReAct loop */}
          {expanded && isComplete && step.react_loop && (
            <ReActLoop items={step.react_loop} />
          )}

          {/* Download button */}
          {isComplete && step.output_file && (
            <button
              onClick={() => onDownload?.(step.output_file)}
              className="mt-3 btn-primary text-sm py-2 px-4"
            >
              <Download size={14} />
              Download {step.output_file}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export default function AgentTrace({ steps, isRunning, onDownload }) {
  const [completedSteps, setCompletedSteps] = useState(0);
  const [activeStep, setActiveStep] = useState(0);

  useEffect(() => {
    if (!isRunning || !steps?.length) return;

    setCompletedSteps(0);
    setActiveStep(0);

    let idx = 0;
    let elapsed = 0;

    const advance = () => {
      if (idx >= steps.length) return;
      setActiveStep(idx + 1);

      const delay = STEP_DELAYS[idx] || 700;
      setTimeout(() => {
        setCompletedSteps(idx + 1);
        idx++;
        if (idx < steps.length) advance();
      }, delay);
    };

    // Small initial delay
    const t = setTimeout(advance, 300);
    return () => clearTimeout(t);
  }, [isRunning, steps]);

  if (!steps?.length && !isRunning) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-text-muted">
        <Cog size={40} className="mb-3 opacity-30" />
        <p className="text-sm">Submit a task to see the agent execution trace</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-text-primary flex items-center gap-2">
          <Cog size={16} className={`text-accent ${isRunning ? 'animate-spin-slow' : ''}`} />
          Agent Execution Trace
        </h3>
        {completedSteps === steps?.length && steps?.length > 0 && (
          <span className="badge-success">✓ Complete</span>
        )}
      </div>

      {(steps || []).map((step, i) => (
        <div
          key={step.step}
          className="animate-step-in"
          style={{ animationDelay: `${i * 80}ms` }}
        >
          <StepRow
            step={step}
            isActive={activeStep === i + 1 && completedSteps < i + 1}
            isComplete={completedSteps > i}
            isPending={activeStep <= i && completedSteps <= i}
            onDownload={onDownload}
          />
        </div>
      ))}
    </div>
  );
}
