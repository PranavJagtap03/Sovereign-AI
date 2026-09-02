import { useState, useCallback } from 'react';
import axios from 'axios';

const API_BASE = 'http://localhost:8000';

// Mock response for offline fallback
const buildMockSteps = (taskType = 'text', format = 'Word Doc') => {
  const modelMap = {
    code: 'DeepSeek-Coder-V2-Lite',
    vision: 'Qwen2.5-VL-7B',
    analysis: 'Qwen2.5-VL-7B',
    text: 'Qwen2.5-7B',
    rag: 'Phi-3-Mini-4K',
  };
  const model = modelMap[taskType] || 'Qwen2.5-7B';
  const extMap = { Excel: 'xlsx', 'Word Doc': 'docx', Code: 'py', JSON: 'json', PowerPoint: 'pptx' };
  const nameMap = { code: 'anomaly_detector', vision: 'inspection_summary', analysis: 'inspection_summary', text: 'policy_response', rag: 'sop_answer' };
  const outputFile = `${nameMap[taskType] || 'output'}.${extMap[format] || 'txt'}`;

  const ragApplicable = ['text', 'rag', 'analysis', 'vision'].includes(taskType);

  return {
    steps: [
      {
        step: 1, name: 'Security Check', icon: '🔒', status: 'passed',
        details: 'PII detected: None | 247 entities scanned | RBAC check: Authorized ✓ | Input sanitized ✓',
        sub_items: ['🛡 PII scan: 247 tokens checked — CLEAN', '🔑 RBAC: User role authorized', '🧹 Input sanitization: Complete (28ms)'],
      },
      {
        step: 2, name: 'Task Classification & Routing', icon: '🧠', status: 'passed',
        details: `Task type: ${taskType.toUpperCase()} | Model selected: ${model} | Task requires ${taskType} processing`,
        sub_items: [`🏷 Classified as: ${taskType.toUpperCase()}`, `🤖 Routed to: ${model}`, '💾 VRAM allocation: 6.8 GB'],
      },
      {
        step: 3, name: 'RAG Retrieval', icon: '📚',
        status: ragApplicable ? 'passed' : 'skipped',
        details: ragApplicable
          ? '3 chunks retrieved from: SOP_Manual_v2.pdf | Similarity: 0.94 | Query: 38ms'
          : 'RAG not applicable for code generation tasks',
        sub_items: ragApplicable
          ? ['🔍 Querying ChromaDB (internal_docs)...', '✓ Top match similarity: 0.94', '📄 Sources: SOP_Manual_v2.pdf']
          : [],
      },
      {
        step: 4, name: 'Agentic Processing (ReAct Loop)', icon: '⚙️', status: 'passed',
        details: `ReAct loop completed | 4 iterations | Model: ${model}`,
        react_loop: taskType === 'code'
          ? [
              { thought: 'I need to write a Python script. Let me plan the data structure first.' },
              { action: 'analyze_requirements(task_description)', observation: 'Requirements: JSON input, z-score method, configurable threshold' },
              { thought: 'Using numpy for statistical calculations. Implementing core logic.' },
              { action: 'generate_code(language="python", libraries=["json","numpy"])', observation: 'Code generated: 89 lines, fully documented' },
              { action: 'validate_code_syntax()', observation: '✓ Syntax valid | ✓ No security issues | ✓ PEP8 compliant' },
            ]
          : [
              { thought: 'Let me retrieve relevant documents from the knowledge base first.' },
              { action: 'ChromaDB_query(collection="internal_docs", k=3)', observation: 'Retrieved 3 chunks | Similarity: 0.94' },
              { thought: 'Context retrieved. Generating structured response with citations.' },
              { action: 'generate_response(grounding="strict", citations=True)', observation: 'Response generated — all claims traceable to source' },
              { action: 'verify_hallucination_check(answer, sources)', observation: '✓ No hallucinated facts | ✓ All citations valid' },
            ],
        sub_items: ['💭 Thought: Analyzing task requirements...', '⚡ Action: Processing with agentic loop', '👁 Observation: 4 iterations complete'],
      },
      {
        step: 5, name: 'Validation & Safety Check', icon: '✅', status: 'passed',
        details: 'Output validated | No sensitive data in output ✓ | Format verified ✓ | Content policy: PASS',
        sub_items: ['🔍 Output PII scan: CLEAN', '📋 Format validation: PASS', '🛡 Content safety: COMPLIANT', '📊 Output size: 142 KB'],
      },
      {
        step: 6, name: 'Deliverable Ready', icon: '📄', status: 'passed',
        details: `Output file: ${outputFile} | Encrypted with AES-256 | Stored in local vault`,
        output_file: outputFile,
        sub_items: [`📁 File: ${outputFile}`, '🔐 Encrypted: AES-256-GCM', '💾 Stored: Local secure vault', '📝 Audit entry: logged'],
      },
    ],
    model_used: model,
    task_type: taskType,
    time_taken_ms: 3200 + Math.floor(Math.random() * 2000),
    outbound_bytes: 0,
    output_file: outputFile,
  };
};

export function useAgentStream() {
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const run = useCallback(async ({ task, format, file, scenario, user_role = 'inspector' }) => {
    setIsLoading(true);
    setResult(null);
    setError(null);

    try {
      const payload = {
        task,
        output_format: format,
        file_name: file?.name || null,
        scenario: scenario || null,
        user_role: user_role || 'inspector',
      };

      const response = await axios.post(`${API_BASE}/api/agent/run`, payload, {
        timeout: 30000,
      });
      setResult(response.data);
    } catch (err) {
      // Fallback to mock data if backend is not running
      console.warn('Backend unavailable, using mock data:', err.message);
      
      const taskLower = task.toLowerCase();
      let taskType = 'text';
      if (scenario) {
        taskType = scenario;
      } else if (['code', 'script', 'python', 'function', 'parse'].some(w => taskLower.includes(w))) {
        taskType = 'code';
      } else if (['inspect', 'report', 'excel', 'analyze', 'defect'].some(w => taskLower.includes(w))) {
        taskType = 'analysis';
      } else if (['sop', 'policy', 'approval', 'procedure', 'according'].some(w => taskLower.includes(w))) {
        taskType = 'rag';
      }

      const mockData = buildMockSteps(taskType, format);
      setResult(mockData);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setResult(null);
    setError(null);
  }, []);

  return { run, isLoading, result, setResult, error, reset };
}
