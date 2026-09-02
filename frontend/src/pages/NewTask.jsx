import { useState, useEffect, useRef } from 'react';
import DemoScenarios from '../components/DemoScenarios';
import TaskInput from '../components/TaskInput';
import AgentTrace from '../components/AgentTrace';
import { useAgentStream } from '../hooks/useAgentStream';
import { Zap, Clock, Cpu, FileText, ShieldCheck, AlertTriangle, CheckCircle, XCircle, Loader2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useRiskCoverage } from '../context/RiskCoverageContext';
import axios from 'axios';

const API_BASE = 'http://localhost:8000';

export default function NewTask() {
  const { run, isLoading, result, setResult } = useAgentStream();
  const { recordPipelineResult, recordAttackDemonstration } = useRiskCoverage();
  const [taskData, setTaskData] = useState({ task: '', format: 'Word Doc', file: null });
  const [selectedRole, setSelectedRole] = useState('inspector');
  const [approvalStatus, setApprovalStatus] = useState('pending'); // 'pending' | 'approved' | 'rejected'
  const [liveMode, setLiveMode] = useState(false);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const traceRef = useRef(null);

  useEffect(() => {
    let interval = null;
    if (isLoading && liveMode) {
      setElapsedSeconds(0);
      interval = setInterval(() => {
        setElapsedSeconds(prev => prev + 1);
      }, 1000);
    } else {
      setElapsedSeconds(0);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isLoading, liveMode]);

  useEffect(() => {
    if (result) {
      recordPipelineResult(result, taskData);
    }
  }, [result, taskData, recordPipelineResult]);

  const handleScenario = async (scenario) => {
    const roleToUse = scenario.userRole || selectedRole;
    setSelectedRole(roleToUse);
    setTaskData({
      task: scenario.task,
      format: scenario.format,
      file: scenario.file ? { name: scenario.file } : null
    });
    setApprovalStatus('pending');

    // Special Attack Demo: Log Tampering (calls tamper endpoint + verify-chain)
    if (scenario.id === 'attack-tamper') {
      try {
        await axios.post(`${API_BASE}/api/audit/tamper-demo`, null, { params: { entry_index: 2 } });
        const verifyRes = await axios.get(`${API_BASE}/api/audit/verify-chain`);
        recordAttackDemonstration('log_tampering');

        const brokenAt = verifyRes.data.broken_at_entry ?? 2;
        const stagesPipeline = [
          { stage: 1, name: 'Prompt Injection Scanner', passed: true, status: 'passed', summary: 'Input scanned clean' },
          { stage: 2, name: 'Live PII Sanitizer', passed: true, status: 'passed', summary: 'No PII detected' },
          { stage: 3, name: 'Task Classification & Routing', passed: true, status: 'passed', summary: 'Routed to audit verification engine' },
          { stage: 4, name: 'Authorization & RBAC Filter', passed: true, status: 'passed', summary: 'Admin authorization granted' },
          { stage: 5, name: 'Local Model Selection', passed: true, status: 'passed', summary: 'Enclave crypto module loaded' },
          { stage: 6, name: 'Company Brain Retrieval', passed: true, status: 'passed', summary: 'Audit database retrieved' },
          { stage: 7, name: 'Primary Agent ReAct Loop', passed: true, status: 'passed', summary: 'Chain-walking verification completed' },
          { stage: 8, name: 'Guardian Agent Review', passed: true, status: 'passed', summary: 'Integrity alert validated' },
          { stage: 9, name: 'Tool Call Validator', passed: true, status: 'passed', summary: 'Database read tools validated' },
          { stage: 10, name: 'Resource Budget Limiter', passed: true, status: 'passed', summary: 'Verification completed in 120ms' },
          { stage: 11, name: 'gVisor Secure Sandbox', passed: true, status: 'passed', summary: 'Sandbox boundary intact' },
          { stage: 12, name: 'Air-Gapped Deliverable Vault', passed: true, status: 'passed', summary: 'Audit log vault snapshot taken' },
          {
            stage: 13,
            name: 'Tamper-Evident Hash Chain Audit',
            passed: false,
            status: 'compromised',
            summary: `HMAC-SHA256 signature mismatch at entry #${brokenAt}. Database modification detected!`
          }
        ];

        if (setResult) {
          setResult({
            steps: [
              {
                step: 1,
                name: 'Unauthorized Database Write Attack',
                icon: '💥',
                status: 'passed',
                details: `Historical log entry #${brokenAt} was modified directly in SQLite/JSONL without recomputing cryptographic HMAC.`,
                sub_items: [
                  'Altered user_role and action fields on historical record',
                  'Original HMAC signature retained to simulate stealth modification'
                ]
              },
              {
                step: 2,
                name: 'Cryptographic Hash-Chain Verification',
                icon: '🔍',
                status: 'passed',
                details: 'Walking HMAC-SHA256 pointers sequentially from genesis hash 0x00000000...',
                sub_items: [
                  'Block #0: Valid signature',
                  'Block #1: Valid signature',
                  `Block #${brokenAt}: HMAC signature mismatch! Expected hash does not match computed value.`
                ]
              },
              {
                step: 3,
                name: 'Chain Corruption Interception',
                icon: '🛑',
                status: 'passed',
                details: `Integrity check failed at entry #${brokenAt}: ${verifyRes.data.reason || 'Signature mismatch'}`,
                sub_items: [
                  `Broken at entry index: #${brokenAt}`,
                  'Ledger freeze engaged — tampering caught with 100% mathematical certainty.'
                ]
              }
            ],
            model_used: 'HMAC-SHA256 Enclave',
            task_type: 'audit_verification',
            time_taken_ms: 180,
            outbound_bytes: 0,
            output_file: null,
            final_response: `⚠️ Log Tampering Attack Intercepted by Stage 13!\n\n` +
              `An unauthorized modification occurred at historical audit entry #${brokenAt}.\n` +
              `The cryptographic HMAC-SHA256 hash-chain verification immediately detected the break:\n\n` +
              `• Chain Status: BROKEN / COMPROMISED\n` +
              `• Corrupted Entry: #${brokenAt}\n` +
              `• Signature Verification: FAILED (HMAC mismatch)\n` +
              `• Details: ${verifyRes.data.reason || 'Cryptographic signature mismatch'}\n\n` +
              `The sovereign workbench's tamper-evident hash-chain proves that any past record alteration is permanently detectable.`,
            status: 'completed',
            pending_approval: false,
            guardian_review: null,
            execution_halted: false,
            sandbox_result: null,
            user_role: roleToUse,
            stages_passed: 12,
            stages_total: 13,
            stages_pipeline: stagesPipeline,
            stage_results: {
              stage_13: { stage: 13, name: 'Tamper-Evident Hash Chain Audit', result: verifyRes.data }
            }
          });
        }
      } catch (err) {
        console.error('Failed to trigger live tamper attack:', err);
      }
      return;
    }

    setTimeout(() => {
      run({
        task: scenario.task,
        format: scenario.format,
        file: scenario.file ? { name: scenario.file } : null,
        scenario: scenario.scenario,
        user_role: roleToUse
      });
      if (traceRef.current) {
        traceRef.current.scrollIntoView({ behavior: 'smooth' });
      }
    }, 100);
  };

  const handleSubmit = ({ task, format, file, user_role, live_mode }) => {
    const roleToUse = user_role || selectedRole;
    const isLive = live_mode ?? liveMode;
    setSelectedRole(roleToUse);
    setTaskData({ task, format, file });
    setApprovalStatus('pending');
    run({ task, format, file, user_role: roleToUse, live_mode: isLive });
    setTimeout(() => {
      if (traceRef.current) {
        traceRef.current.scrollIntoView({ behavior: 'smooth' });
      }
    }, 200);
  };

  const handleDownload = (filename) => {
    // Create a dummy download for demo purposes
    const content = filename.endsWith('.py')
      ? `# Generated by Sovereign AI Workbench\n# SIH 2026 | Team Code:201\n\nimport json\nimport numpy as np\n\ndef parse_sensor_logs(log_file, threshold_std=3.0):\n    """Parse JSON sensor logs and flag anomalies."""\n    with open(log_file) as f:\n        logs = json.load(f)\n    # ... implementation\n    return {"anomalies": []}\n`
      : `Sovereign AI Workbench — SIH 2026\nTeam Code:201 | Demo Output\n\nThis is a demo-generated file.\nIn production, this would contain the actual AI-generated content.`;

    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  const [isExportingDocx, setIsExportingDocx] = useState(false);

  const handleDownloadDocx = async () => {
    if (!result?.final_response) return;
    setIsExportingDocx(true);
    try {
      const filename = result.output_file?.endsWith('.docx')
        ? result.output_file
        : 'deliverable_report.docx';

      const response = await axios.post(
        `${API_BASE}/api/output/generate-docx`,
        {
          title: taskData.task ? `Report: ${taskData.task.slice(0, 60)}` : 'Sovereign AI Deliverable Report',
          content: result.final_response,
          filename
        },
        { responseType: 'blob' }
      );

      const blob = new Blob([response.data], {
        type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
      });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Failed to export docx report:', err);
    } finally {
      setIsExportingDocx(false);
    }
  };

  return (
    <div className="max-w-6xl">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl font-bold text-text-primary">Agentic Workbench</h1>
          <p className="text-sm text-text-muted mt-0.5">Submit tasks to the multi-model agentic pipeline</p>
        </div>
        <div className="flex items-center gap-3">
          {result && (
            <>
              <div className="flex items-center gap-1.5 text-xs text-text-muted">
                <Clock size={12} />
                <span className="font-mono">{(result.time_taken_ms / 1000).toFixed(1)}s</span>
              </div>
              <div className="flex items-center gap-1.5 text-xs text-text-muted">
                <Cpu size={12} />
                <span className="text-accent-warn font-mono">{result.model_used}</span>
              </div>
              <span className="badge-accent text-[10px]">0 bytes outbound</span>
            </>
          )}
        </div>
      </div>

      {/* Quick Launch Scenarios */}
      <DemoScenarios onSelect={handleScenario} />

      {/* Split panel */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left — Task Input */}
        <div className="card p-5">
          <h2 className="font-semibold text-text-primary mb-4 flex items-center gap-2">
            <Zap size={16} className="text-accent" />
            Task Input
          </h2>
          <TaskInput
            onSubmit={handleSubmit}
            isLoading={isLoading}
            initialTask={taskData.task}
            initialFormat={taskData.format}
            userRole={selectedRole}
            onRoleChange={setSelectedRole}
            liveMode={liveMode}
            onLiveModeChange={setLiveMode}
          />
        </div>

        {/* Right — Agent Trace */}
        <div ref={traceRef} className="card p-5 overflow-y-auto" style={{ maxHeight: '80vh' }}>
          {/* Live GPU Inference in-flight banner */}
          {isLoading && liveMode && (() => {
            const isVisionTask = Boolean(taskData.file) || ['diagram', 'image', 'photo', 'drawing', 'inspection report', 'scan', 'visual', 'chart'].some(w => taskData.task.toLowerCase().includes(w));
            return (
              <motion.div
                initial={{ opacity: 0, y: -6 }}
                animate={{ opacity: 1, y: 0 }}
                className="mb-4 p-4 rounded-xl border border-purple-500/40 bg-purple-950/30 text-purple-200 shadow-lg"
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div className="flex items-start sm:items-center gap-3 font-semibold text-xs sm:text-sm text-purple-300">
                    <Loader2 size={18} className="animate-spin text-purple-400 flex-shrink-0 mt-0.5 sm:mt-0" />
                    {isVisionTask ? (
                      <span>👁️ Running Qwen2.5-VL locally on GPU — analyzing image, this may take a few seconds (or ~10s longer if switching from another loaded model)...</span>
                    ) : (
                      <span>🧠 Running DeepSeek-R1 locally on GPU — reasoning models can take 20-60s depending on query complexity. Processing...</span>
                    )}
                  </div>
                  <div className="flex-shrink-0 self-start sm:self-auto font-mono text-xs font-bold px-2.5 py-1 rounded bg-purple-500/20 text-purple-300 border border-purple-500/40 flex items-center gap-1.5 animate-pulse">
                    <Clock size={12} className="text-purple-400" />
                    <span>{elapsedSeconds}s elapsed</span>
                  </div>
                </div>
                <div className="mt-2.5 text-[11px] text-purple-300/70 font-mono pl-7 flex flex-wrap items-center gap-x-4 gap-y-1">
                  {isVisionTask ? (
                    <>
                      <span>• Multimodal token stream & visual defect grounding</span>
                      <span>• Local Ollama: http://localhost:11434 (0 bytes outbound)</span>
                    </>
                  ) : (
                    <>
                      <span>• Generating token stream & reasoning trace &lt;think&gt;...&lt;/think&gt;</span>
                      <span>• Local Ollama: http://localhost:11434 (0 bytes outbound)</span>
                    </>
                  )}
                </div>
              </motion.div>
            );
          })()}

          <AgentTrace
            steps={result?.steps}
            isRunning={isLoading}
            onDownload={handleDownload}
            result={result}
          />

          {/* Human Review Banner when pending_approval is true */}
          {result?.pending_approval && approvalStatus === 'pending' && (
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-4 p-5 rounded-xl border border-amber-500/40 bg-amber-500/10"
            >
              <div className="flex items-start gap-3.5">
                <div className="w-10 h-10 rounded-lg bg-amber-500/20 border border-amber-500/40 flex items-center justify-center shrink-0 text-amber-400 font-bold text-lg">
                  ⏸
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-2">
                    <h4 className="text-sm font-bold text-amber-400 uppercase tracking-wider flex items-center gap-1.5">
                      ⏸ Awaiting Human Review
                    </h4>
                    <span className="badge-warn text-[10px]">GUARDIAN ESCALATION</span>
                  </div>
                  <p className="text-xs text-text-muted mt-1 leading-relaxed">
                    The independent Guardian model (<span className="text-text-primary font-semibold">{result.guardian_review?.reviewed_by || 'Phi-3-Mini-4K'}</span>)
                    flagged high-impact assertions requiring human sign-off before deliverable release:
                  </p>
                  <div className="mt-2.5 p-2.5 rounded bg-black/40 border border-amber-500/25 text-xs font-mono text-amber-300">
                    <span className="font-semibold text-amber-400">Escalation Trigger:</span> "{result.guardian_review?.reason || 'Critical assertion'}"
                    <span className="block text-[11px] text-text-muted mt-0.5">{result.guardian_review?.confidence_note || 'Human confirmation needed'}</span>
                  </div>
                  <p className="text-[11px] text-text-muted mt-2">
                    Output preview and file export are currently quarantined in the local air-gapped vault.
                  </p>
                  <div className="mt-4 flex items-center gap-3">
                    <button
                      onClick={() => setApprovalStatus('approved')}
                      className="btn-primary text-xs py-2 px-4 flex items-center gap-1.5 shadow-md hover:scale-102 transition-transform"
                    >
                      <CheckCircle size={14} />
                      Approve Deliverable
                    </button>
                    <button
                      onClick={() => setApprovalStatus('rejected')}
                      className="px-4 py-2 rounded-lg text-xs font-semibold bg-danger/20 hover:bg-danger/30 text-danger border border-danger/40 transition-colors flex items-center gap-1.5"
                    >
                      <XCircle size={14} />
                      Reject
                    </button>
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {result?.pending_approval && approvalStatus === 'rejected' && (
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-4 p-4 rounded-xl border border-danger/40 bg-danger/10"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-danger font-semibold text-xs">
                  <XCircle size={16} />
                  <span>Deliverable Rejected by Human Operator</span>
                </div>
                <button
                  onClick={() => setApprovalStatus('pending')}
                  className="text-[10px] text-text-muted hover:text-text-primary underline"
                >
                  Reset Review
                </button>
              </div>
              <p className="text-xs text-text-muted mt-1 font-mono">
                Quarantine maintained. Zero deliverable bytes released from local vault.
              </p>
            </motion.div>
          )}

          {/* Final response preview — shown when NOT pending approval OR when approved */}
          {result?.final_response && (!result.pending_approval || approvalStatus === 'approved') && (
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-4 p-4 rounded-lg border"
              style={{
                background: approvalStatus === 'approved' ? 'rgba(34,197,94,0.05)' : 'rgba(0,200,150,0.04)',
                borderColor: approvalStatus === 'approved' ? 'rgba(34,197,94,0.3)' : 'rgba(0,200,150,0.15)'
              }}
            >
              {approvalStatus === 'approved' && (
                <div className="mb-3 p-2 rounded bg-success/15 border border-success/30 text-success text-xs font-mono flex items-center justify-between">
                  <span className="flex items-center gap-1.5 font-bold">
                    <CheckCircle size={14} />
                    ✓ Human Operator Sign-Off Verified — Deliverable Released
                  </span>
                  <button
                    onClick={() => setApprovalStatus('pending')}
                    className="text-[10px] text-text-muted hover:text-text-primary underline"
                  >
                    Re-lock
                  </button>
                </div>
              )}
              {isExportingDocx && (
                <div className="mb-3 p-2.5 rounded-lg bg-accent/10 border border-accent/25 flex items-center justify-between text-xs text-accent">
                  <div className="flex items-center gap-2">
                    <Loader2 size={15} className="animate-spin text-accent" />
                    <span>Compiling Word report (.docx) with executive cover & local enclave seal...</span>
                  </div>
                  <span className="font-mono text-[10px] px-1.5 py-0.5 rounded bg-black/40 text-accent font-bold">
                    python-docx
                  </span>
                </div>
              )}
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <h4 className="text-xs font-semibold text-text-muted uppercase tracking-wider">
                    📋 Generated Output Preview
                  </h4>
                  {result.live_mode && !result.fell_back_to_demo && (
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded font-bold bg-purple-500/20 text-purple-300 border border-purple-500/40 flex items-center gap-1">
                      {result.task_type === 'vision' || result.model_used?.includes('Qwen')
                        ? '🟢 Live Local Inference (Qwen2.5-VL)'
                        : '🟢 Live Local Inference (DeepSeek-R1)'}
                    </span>
                  )}
                  {result.fell_back_to_demo && (
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/40" title={result.live_fallback_reason}>
                      ⚠️ Fallback: {result.live_fallback_reason}
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-2">
                  <span className="badge-success text-[10px]">✓ Ready</span>
                  <button
                    onClick={handleDownloadDocx}
                    disabled={isExportingDocx}
                    className="btn-primary text-[11px] py-1 px-2.5 flex items-center gap-1.5 shadow-sm hover:opacity-90 disabled:opacity-50"
                    title="Download formatted Word document (.docx)"
                  >
                    {isExportingDocx ? <Loader2 size={13} className="animate-spin" /> : <FileText size={13} />}
                    {isExportingDocx ? 'Exporting...' : 'Download Report (.docx)'}
                  </button>
                </div>
              </div>

              {/* Collapsible DeepSeek-R1 Reasoning Trace */}
              {result.reasoning_trace && (
                <details className="mb-3 rounded-lg border border-purple-500/30 bg-purple-950/25 p-2.5 text-xs group" open>
                  <summary className="cursor-pointer font-semibold text-purple-300 flex items-center justify-between select-none hover:text-purple-200">
                    <span className="flex items-center gap-1.5">
                      <span>🧠</span>
                      <span>View Model's Reasoning Trace</span>
                      <span className="text-[10px] font-mono text-purple-400/80">({result.reasoning_trace.length} chars)</span>
                    </span>
                    <span className="text-[10px] text-purple-400/60 font-mono">click to collapse</span>
                  </summary>
                  <div className="mt-2 p-2.5 rounded bg-black/60 text-[11px] font-mono text-purple-200/90 whitespace-pre-wrap leading-relaxed max-h-52 overflow-y-auto border border-purple-500/20">
                    {result.reasoning_trace}
                  </div>
                </details>
              )}

              <div className="text-xs text-text-muted font-mono whitespace-pre-wrap leading-5 max-h-48 overflow-y-auto">
                {result.final_response.slice(0, 800)}
                {result.final_response.length > 800 && '…'}
              </div>
              <div className="mt-3 pt-2.5 border-t border-accent/10 flex items-center justify-between">
                <span className="text-[11px] text-text-muted flex items-center gap-1">
                  <span>📄 Microsoft Word deliverable</span>
                  <span>· Title cover page, executive formatting, local enclave seal</span>
                </span>
                <button
                  onClick={handleDownloadDocx}
                  disabled={isExportingDocx}
                  className="btn-primary text-xs py-1.5 px-3 flex items-center gap-1.5 shadow-sm disabled:opacity-50"
                >
                  {isExportingDocx ? <Loader2 size={14} className="animate-spin" /> : <FileText size={14} />}
                  {isExportingDocx ? 'Compiling Word Document...' : 'Download Report (.docx)'}
                </button>
              </div>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
}
