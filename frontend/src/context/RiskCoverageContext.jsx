import { createContext, useContext, useState, useCallback } from 'react';

export const ATTACK_CLASSES = [
  {
    id: 'prompt_injection_text',
    name: 'Prompt Injection (text)',
    stage: 1,
    stageLabel: 'Stage 1: Input Guard',
    description: 'Adversarial jailbreak and override pattern interception'
  },
  {
    id: 'prompt_injection_image',
    name: 'Prompt Injection (image)',
    stage: 1,
    stageLabel: 'Stage 1: Vision Guard',
    description: 'Adversarial visual payload / OCR injection interception'
  },
  {
    id: 'unauthorized_document_access',
    name: 'Unauthorized Document Access',
    stage: 4,
    stageLabel: 'Stage 4: RBAC Filter',
    description: 'Role-based clearance filtering blocked restricted documents'
  },
  {
    id: 'pii_leakage',
    name: 'PII Leakage',
    stage: 2,
    stageLabel: 'Stage 2: PII Sanitizer',
    description: 'Live query sensitive PII tokens (phone, Aadhaar, PAN) masked'
  },
  {
    id: 'overconfident_ai',
    name: 'Overconfident AI Recommendation',
    stage: 8,
    stageLabel: 'Stage 8: Guardian Agent',
    description: 'High-impact assertions escalated for human sign-off'
  },
  {
    id: 'malformed_tool_call',
    name: 'Malformed Tool Call',
    stage: 9,
    stageLabel: 'Stage 9: Tool Validator',
    description: 'Path traversal or unauthorized tool schema invocation blocked'
  },
  {
    id: 'resource_exhaustion',
    name: 'Resource Exhaustion',
    stage: 10,
    stageLabel: 'Stage 10: Budget Limiter',
    description: 'Step count and timeout execution limits enforced'
  },
  {
    id: 'malicious_code_execution',
    name: 'Malicious Code Execution',
    stage: 11,
    stageLabel: 'Stage 11: gVisor Sandbox',
    description: 'Kernel-isolated container execution with network and FS locks'
  },
  {
    id: 'log_tampering',
    name: 'Log Tampering',
    stage: 13,
    stageLabel: 'Stage 13: Hash Chain',
    description: 'HMAC-SHA256 signature mismatch detected database modification'
  }
];

const RiskCoverageContext = createContext(null);

export function RiskCoverageProvider({ children }) {
  // In-memory state tracking demonstrated attacks (no localStorage)
  // Seed with 2 baseline demonstrated scenarios for quick visual feedback, or start empty
  const [demonstrated, setDemonstrated] = useState({
    prompt_injection_text: false,
    prompt_injection_image: false,
    unauthorized_document_access: false,
    pii_leakage: false,
    overconfident_ai: false,
    malformed_tool_call: false,
    resource_exhaustion: false,
    malicious_code_execution: false,
    log_tampering: false
  });

  const [networkStats] = useState({
    externalCalls: 0,
    bytesTransferred: 0,
    blockedAttempts: 43
  });

  const recordAttackDemonstration = useCallback((attackId) => {
    setDemonstrated(prev => ({
      ...prev,
      [attackId]: true
    }));
  }, []);

  const recordPipelineResult = useCallback((result, taskInput = {}) => {
    if (!result) return;

    setDemonstrated(prev => {
      const next = { ...prev };

      // 1. Prompt Injection
      if (
        result.status === 'blocked' ||
        result.stage_results?.stage_1?.result?.injection_detected ||
        result.stages_pipeline?.find(s => s.stage === 1 && s.status === 'blocked')
      ) {
        if (taskInput.file || taskInput.scenario === 'vision') {
          next.prompt_injection_image = true;
        } else {
          next.prompt_injection_text = true;
        }
      }

      // 2. PII Leakage Sanitized
      if (
        result.stage_results?.stage_2?.result?.pii_detected ||
        result.stages_pipeline?.find(s => s.stage === 2 && s.summary?.toLowerCase().includes('sanitized'))
      ) {
        next.pii_leakage = true;
      }

      // 3. Unauthorized Document Access (RBAC)
      const filteredDocs = result.stage_results?.stage_4?.result?.filtered_documents ||
        result.stage_results?.stage_4?.result?.sources_blocked;
      if (filteredDocs && filteredDocs.length > 0) {
        next.unauthorized_document_access = true;
      }

      // 4. Overconfident AI Recommendation (Guardian)
      if (
        result.pending_approval ||
        result.guardian_review?.requires_human_approval ||
        result.stage_results?.stage_8?.result?.requires_human_approval
      ) {
        next.overconfident_ai = true;
      }

      // 5. Malformed Tool Call
      if (
        result.stage_results?.stage_9?.result?.valid === false ||
        result.halt_reason?.toLowerCase().includes('tool')
      ) {
        next.malformed_tool_call = true;
      }

      // 6. Resource Exhaustion
      if (
        result.stage_results?.stage_10?.result?.within_budget === false ||
        result.halt_reason?.toLowerCase().includes('budget') ||
        result.halt_reason?.toLowerCase().includes('resource')
      ) {
        next.resource_exhaustion = true;
      }

      // 7. Malicious Code Execution
      if (
        result.sandbox_result ||
        result.stage_results?.stage_11?.result?.executed ||
        result.stages_pipeline?.find(s => s.stage === 11 && s.status === 'passed')
      ) {
        next.malicious_code_execution = true;
      }

      // 8. Log Tampering
      if (
        result.stage_results?.stage_13?.result?.chain_valid === false ||
        result.stages_pipeline?.find(s => s.stage === 13 && s.status === 'compromised')
      ) {
        next.log_tampering = true;
      }

      return next;
    });
  }, []);

  const demonstratedCount = Object.values(demonstrated).filter(Boolean).length;

  return (
    <RiskCoverageContext.Provider
      value={{
        demonstrated,
        demonstratedCount,
        totalAttacks: ATTACK_CLASSES.length,
        attackClasses: ATTACK_CLASSES,
        networkStats,
        recordAttackDemonstration,
        recordPipelineResult
      }}
    >
      {children}
    </RiskCoverageContext.Provider>
  );
}

export function useRiskCoverage() {
  const ctx = useContext(RiskCoverageContext);
  if (!ctx) {
    throw new Error('useRiskCoverage must be used within a RiskCoverageProvider');
  }
  return ctx;
}
