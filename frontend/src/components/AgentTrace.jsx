import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  CheckCircle, Circle, Loader2, Download, ChevronDown, ChevronUp,
  Lock, Brain, BookOpen, Cog, ShieldCheck, FileDown,
  AlertTriangle, AlertCircle, ShieldAlert, XCircle, Info, Shield, Key
} from 'lucide-react';

const STAGE_DEFINITIONS = [
  { stage: 1, shortLabel: '1. Injection Scan', fullName: 'Prompt Injection Scanner', defaultSummary: 'Adversarial pattern scan clean' },
  { stage: 2, shortLabel: '2. PII Sanitize', fullName: 'Live PII Sanitizer', defaultSummary: 'Live user query sanitized' },
  { stage: 3, shortLabel: '3. Task Routing', fullName: 'Task Classification & Routing', defaultSummary: 'Classified and routed to model' },
  { stage: 4, shortLabel: '4. RBAC Auth', fullName: 'Authorization & RBAC Filter', defaultSummary: 'Clearance authorization verified' },
  { stage: 5, shortLabel: '5. Model Select', fullName: 'Local Model Selection', defaultSummary: 'Air-gapped model allocated to VRAM' },
  { stage: 6, shortLabel: '6. Brain Retrieval', fullName: 'Company Brain Retrieval (RAG)', defaultSummary: 'ChromaDB vector retrieval' },
  { stage: 7, shortLabel: '7. Primary Agent', fullName: 'Primary Agent ReAct Loop', defaultSummary: 'Autonomous reasoning loop completed' },
  { stage: 8, shortLabel: '8. Guardian Review', fullName: 'Guardian Agent Review', defaultSummary: 'Independent model safety review' },
  { stage: 9, shortLabel: '9. Tool Validator', fullName: 'Tool Call Validator', defaultSummary: 'Tool schemas & path traversals checked' },
  { stage: 10, shortLabel: '10. Resource Budget', fullName: 'Resource Budget Limiter', defaultSummary: 'Step count & execution duration verified' },
  { stage: 11, shortLabel: '11. Secure Sandbox', fullName: 'gVisor Secure Sandbox', defaultSummary: 'Isolated runsc container execution' },
  { stage: 12, shortLabel: '12. Vault Store', fullName: 'Air-Gapped Vault Storage', defaultSummary: 'Encrypted in local deliverable vault' },
  { stage: 13, shortLabel: '13. Audit Log', fullName: 'HMAC-SHA256 Hash Chaining', defaultSummary: 'Cryptographic hash-chain attested' },
];

const STEP_ICONS = {
  1: Lock,
  2: Brain,
  3: BookOpen,
  4: Cog,
  5: ShieldCheck,
  6: FileDown,
};

const STEP_DELAYS = [600, 900, 700, 1400, 600, 500];

function ReActLoop({ items }) {
  const [visible, setVisible] = useState(0);
  useEffect(() => {
    if (visible < items.length) {
      const t = setTimeout(() => setVisible(v => v + 1), 300);
      return () => clearTimeout(t);
    }
  }, [visible, items.length]);

  return (
    <div className="mt-3 space-y-1.5">
      {items.slice(0, visible).map((item, i) => (
        <div key={i} className="animate-step-in">
          {item.thought && (
            <div className="react-thought text-xs">
              <span className="text-blue-400 font-semibold">💭 Thought:</span>{' '}
              <span className="text-text-muted">{item.thought}</span>
            </div>
          )}
          {item.action && (
            <div className="react-action text-xs">
              <span className="text-accent font-semibold">⚡ Action:</span>{' '}
              <span className="text-green-300 font-mono">{item.action}</span>
            </div>
          )}
          {item.observation && (
            <div className="react-observation text-xs">
              <span className="text-accent-warn font-semibold">👁 Obs:</span>{' '}
              <span className="text-yellow-200 font-mono">{item.observation}</span>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

function StageRow({ def, isComplete, isActive, isPending, stageData, result }) {
  const [expanded, setExpanded] = useState(false);

  // Compute flag condition (red / amber / normal)
  let flagType = 'none'; // 'none' | 'amber' | 'red'
  let flagBadge = 'VERIFIED';
  let tooltipText = stageData?.summary || def.defaultSummary;
  let detailReason = '';

  const s4Result = result?.stage_results?.stage_4?.result;
  const s8Result = result?.stage_results?.stage_8?.result || result?.guardian_review;
  const s1Result = result?.stage_results?.stage_1?.result;
  const s2Result = result?.stage_results?.stage_2?.result;

  if (def.stage === 1) {
    if (stageData?.status === 'blocked' || s1Result?.injection_detected || result?.status === 'blocked') {
      flagType = 'red';
      flagBadge = 'BLOCKED';
      detailReason = 'Adversarial prompt injection pattern intercepted.';
      tooltipText = stageData?.summary || 'Prompt injection pattern detected. Downstream execution halted.';
    }
  } else if (def.stage === 2) {
    if (s2Result?.pii_detected) {
      flagType = 'amber';
      flagBadge = 'SANITIZED';
      detailReason = `Sanitized PII: ${s2Result.entities_found?.join(', ')}`;
      tooltipText = `Live user query contained sensitive PII (${s2Result.entities_found?.join(', ')}). Automatically masked before model routing.`;
    }
  } else if (def.stage === 4) {
    if (s4Result?.filtered_documents?.length > 0) {
      flagType = 'amber';
      flagBadge = 'RBAC FILTER';
      detailReason = `Document restricted for role '${result?.user_role || 'inspector'}'`;
      tooltipText = `RBAC Access Enforced: User role has '${s4Result.user_clearance || 'Internal'}' clearance. ${s4Result.filtered_documents.join('; ')}`;
    }
  } else if (def.stage === 7) {
    if (stageData?.status === 'halted' || result?.execution_halted) {
      flagType = 'red';
      flagBadge = 'HALTED';
      detailReason = result?.halt_reason || 'Execution guard halted loop';
      tooltipText = result?.halt_reason || 'ReAct processing halted by security guard.';
    }
  } else if (def.stage === 8) {
    if (stageData?.status === 'escalated' || result?.pending_approval || s8Result?.requires_human_approval) {
      flagType = 'amber';
      flagBadge = 'ESCALATED';
      detailReason = `High-impact claim flagged (${s8Result?.reason || 'human review needed'})`;
      tooltipText = `Guardian Agent (${s8Result?.reviewed_by || 'Phi-3-Mini-4K'}) detected high-impact assertions: "${s8Result?.reason || 'critical action'}". Requires human operator approval.`;
    }
  } else if (def.stage === 9 && (stageData?.status === 'blocked' || !stageData?.passed)) {
    flagType = 'red';
    flagBadge = 'BLOCKED';
    detailReason = 'Unauthorized tool schema or path traversal';
    tooltipText = stageData?.summary || 'Tool call violation detected and blocked.';
  } else if (def.stage === 10 && (stageData?.status === 'exceeded' || !stageData?.passed)) {
    flagType = 'red';
    flagBadge = 'EXCEEDED';
    detailReason = 'Resource budget limit exceeded';
    tooltipText = stageData?.summary || 'Execution exceeded 15 steps or 30s budget.';
  } else if (def.stage === 12 && (stageData?.status === 'quarantined' || result?.pending_approval)) {
    flagType = 'amber';
    flagBadge = 'QUARANTINE';
    detailReason = 'Deliverable locked pending human approval';
    tooltipText = 'Deliverable encrypted with AES-256 and quarantined in local vault until sign-off.';
  } else if (def.stage === 13 && (stageData?.status === 'compromised' || !stageData?.passed)) {
    flagType = 'red';
    flagBadge = 'TAMPERED';
    detailReason = 'Audit hash chain signature mismatch';
    tooltipText = 'Cryptographic HMAC-SHA256 signature verification failed.';
  }

  return (
    <motion.div
      initial={{ opacity: 0, x: -6 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.25, delay: def.stage * 0.03 }}
      className={`relative group p-2.5 rounded-lg border transition-all text-xs font-mono mb-1.5 ${
        isActive
          ? 'bg-accent/10 border-accent/40 shadow-sm'
          : flagType === 'red'
          ? 'bg-danger/10 border-danger/35 text-danger'
          : flagType === 'amber'
          ? 'bg-amber-400/10 border-amber-400/30'
          : isComplete
          ? 'bg-surface border-gray-800/80 hover:border-accent/30'
          : 'bg-surface/40 border-gray-800/40 opacity-40'
      }`}
    >
      <div className="flex items-center justify-between gap-3">
        {/* Left: Icon & Name */}
        <div className="flex items-center gap-2.5 min-w-0">
          <div className="shrink-0 flex items-center justify-center w-5 h-5">
            {isActive && !isComplete && (
              <Loader2 size={16} className="text-accent animate-spin" />
            )}
            {isComplete && flagType === 'none' && (
              <motion.div
                initial={{ scale: 0, rotate: -45 }}
                animate={{ scale: 1, rotate: 0 }}
                transition={{ type: 'spring', stiffness: 450, damping: 20 }}
              >
                <CheckCircle size={16} className="text-success" />
              </motion.div>
            )}
            {isComplete && flagType === 'amber' && (
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: [1, 1.25, 1] }}
                transition={{ duration: 0.35 }}
              >
                <AlertTriangle size={16} className="text-amber-400" />
              </motion.div>
            )}
            {isComplete && flagType === 'red' && (
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: [1, 1.3, 1] }}
                transition={{ duration: 0.35 }}
              >
                <XCircle size={16} className="text-danger" />
              </motion.div>
            )}
            {isPending && (
              <Circle size={14} className="text-text-muted opacity-30" />
            )}
          </div>

          <div className="min-w-0 truncate">
            <div className="flex items-center gap-2">
              <span className={`font-semibold ${
                flagType === 'red' ? 'text-danger' : flagType === 'amber' ? 'text-amber-300' : isComplete ? 'text-text-primary' : 'text-text-muted'
              }`}>
                {def.shortLabel}
              </span>
              <span className="text-[10px] text-text-muted opacity-70 hidden sm:inline">
                ({def.fullName})
              </span>
            </div>
            {isComplete && (
              <p className={`text-[11px] truncate mt-0.5 ${
                flagType === 'red' ? 'text-danger/90' : flagType === 'amber' ? 'text-amber-300/90 font-medium' : 'text-text-muted'
              }`}>
                {detailReason ? `⚠️ ${detailReason}` : `✓ ${tooltipText}`}
              </p>
            )}
          </div>
        </div>

        {/* Right: Badge & Details */}
        <div className="flex items-center gap-1.5 shrink-0">
          {isActive && !isComplete && (
            <span className="badge text-[9px] bg-accent/20 text-accent font-semibold animate-pulse">RUNNING</span>
          )}
          {isComplete && (
            <span className={`text-[10px] px-2 py-0.5 rounded font-bold uppercase tracking-wider ${
              flagType === 'red'
                ? 'bg-danger/20 text-danger border border-danger/40'
                : flagType === 'amber'
                ? 'bg-amber-400/20 text-amber-400 border border-amber-400/40'
                : 'bg-success/15 text-success border border-success/30'
            }`}>
              {flagBadge}
            </span>
          )}
        </div>
      </div>

      {/* Hover Tooltip Popup */}
      <div className="absolute left-6 bottom-full mb-1 hidden group-hover:block z-40 w-80 p-2.5 rounded-lg bg-surface-secondary border border-gray-700 text-xs shadow-2xl text-text-primary pointer-events-none">
        <div className="font-semibold mb-1 flex items-center justify-between border-b border-gray-700/60 pb-1">
          <span className="text-accent">{def.fullName}</span>
          <span className={`text-[10px] font-bold ${flagType === 'red' ? 'text-danger' : flagType === 'amber' ? 'text-amber-400' : 'text-success'}`}>
            Stage {def.stage} / 13
          </span>
        </div>
        <p className="text-[11px] text-text-muted leading-relaxed font-sans">
          {tooltipText}
        </p>
      </div>
    </motion.div>
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
    >
      <div className="flex items-start gap-3">
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
              {step.status === 'pending_approval' && (
                <span className="badge-warn text-[10px]">AWAITING REVIEW</span>
              )}
              {isComplete && step.status !== 'skipped' && step.status !== 'pending_approval' && (
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

          {(isActive || isComplete) && (
            <p className="text-xs text-text-muted mt-1 leading-relaxed font-mono">
              → {step.details}
            </p>
          )}

          {expanded && isComplete && step.sub_items?.length > 0 && (
            <div className="mt-2 space-y-1">
              {step.sub_items.map((item, i) => (
                <div key={i} className="text-xs text-text-muted font-mono pl-3 border-l border-accent/20">
                  {item}
                </div>
              ))}
            </div>
          )}

          {expanded && isComplete && step.react_loop && (
            <ReActLoop items={step.react_loop} />
          )}

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

export default function AgentTrace({ steps, isRunning, onDownload, result }) {
  const [completedSteps, setCompletedSteps] = useState(0);
  const [activeStep, setActiveStep] = useState(0);

  // 13-stage stepper animation state
  const [completedStages, setCompletedStages] = useState(0);
  const [activeStage, setActiveStage] = useState(0);
  const [viewMode, setViewMode] = useState('pipeline'); // 'pipeline' | 'react'

  // Animate 13 stages with Framer Motion checkmarks while running
  useEffect(() => {
    if (!isRunning) {
      if (result) {
        setCompletedStages(13);
        setActiveStage(13);
      }
      return;
    }

    setCompletedStages(0);
    setActiveStage(1);

    let stageIdx = 1;
    const stageInterval = setInterval(() => {
      stageIdx += 1;
      if (stageIdx <= 13) {
        setActiveStage(stageIdx);
        setCompletedStages(stageIdx - 1);
      } else {
        clearInterval(stageInterval);
      }
    }, 180);

    return () => clearInterval(stageInterval);
  }, [isRunning, result]);

  // Animate macro 6-step ReAct trace
  useEffect(() => {
    if (!isRunning || !steps?.length) return;

    setCompletedSteps(0);
    setActiveStep(0);

    let idx = 0;
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

    const t = setTimeout(advance, 300);
    return () => clearTimeout(t);
  }, [isRunning, steps]);

  if (!steps?.length && !isRunning && !result) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-text-muted">
        <ShieldCheck size={40} className="mb-3 opacity-30 text-accent" />
        <p className="text-sm font-medium">Submit a task to see the 13-Stage Sovereign Pipeline execution</p>
        <p className="text-xs text-text-muted opacity-60 mt-1">Live prompt injection scan, live PII redaction, RBAC enforcement, & sandbox</p>
      </div>
    );
  }

  const passedCount = result?.stages_passed ?? (completedStages >= 13 ? 13 : completedStages);
  const totalCount = result?.stages_total || 13;

  return (
    <div className="space-y-3">
      {/* Header and View Mode Switcher */}
      <div className="flex items-center justify-between mb-3 pb-2 border-b border-gray-800">
        <div className="flex items-center gap-2">
          <ShieldCheck size={18} className={`text-accent ${isRunning ? 'animate-spin-slow' : ''}`} />
          <h3 className="font-semibold text-text-primary text-sm">
            Sovereign Pipeline Execution
          </h3>
        </div>

        {/* View Mode Toggle Tabs */}
        <div className="flex items-center gap-1.5 p-1 rounded-lg bg-surface border border-gray-800">
          <button
            onClick={() => setViewMode('pipeline')}
            className={`px-2.5 py-1 rounded text-xs font-semibold transition-colors flex items-center gap-1.5 ${
              viewMode === 'pipeline'
                ? 'bg-accent/20 text-accent border border-accent/30'
                : 'text-text-muted hover:text-text-primary'
            }`}
          >
            <span>🛡 13-Stage Pipeline</span>
            <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-black/40 font-bold">
              {passedCount}/{totalCount}
            </span>
          </button>
          <button
            onClick={() => setViewMode('react')}
            className={`px-2.5 py-1 rounded text-xs font-semibold transition-colors flex items-center gap-1.5 ${
              viewMode === 'react'
                ? 'bg-accent/20 text-accent border border-accent/30'
                : 'text-text-muted hover:text-text-primary'
            }`}
          >
            <span>⚙️ ReAct Loop</span>
          </button>
        </div>
      </div>

      {/* VIEW 1: 13-Stage Sovereign Stepper Checklist */}
      {viewMode === 'pipeline' && (
        <div className="space-y-1">
          <div className="flex items-center justify-between text-xs text-text-muted px-1 mb-2">
            <span className="uppercase font-semibold tracking-wider text-[10px]">
              End-to-End Cryptographic & Security Verification
            </span>
            <span className="text-[11px] font-mono text-accent">
              Role: <span className="font-bold">{result?.user_role || 'inspector'}</span>
            </span>
          </div>

          <div className="space-y-1">
            {STAGE_DEFINITIONS.map((def) => {
              const stageData = result?.stages_pipeline?.find((s) => s.stage === def.stage);
              const isComplete = !isRunning || completedStages >= def.stage;
              const isActive = isRunning && activeStage === def.stage;
              const isPending = isRunning && completedStages < def.stage && activeStage !== def.stage;

              return (
                <StageRow
                  key={def.stage}
                  def={def}
                  isComplete={isComplete}
                  isActive={isActive}
                  isPending={isPending}
                  stageData={stageData}
                  result={result}
                />
              );
            })}
          </div>
        </div>
      )}

      {/* VIEW 2: ReAct Execution Trace */}
      {viewMode === 'react' && (
        <div className="space-y-3">
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
      )}
    </div>
  );
}
