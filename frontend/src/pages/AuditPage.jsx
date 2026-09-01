import { useEffect, useState } from 'react';
import AuditLog from '../components/AuditLog';
import axios from 'axios';
import { ScrollText } from 'lucide-react';

// Offline mock audit logs
const buildMockLogs = () => {
  const entries = [
    { id: 'LOG-20260831-0001', user: 'analyst_priya', user_role: 'Data Analyst', task_type: 'Document Analysis', model_used: 'Qwen2.5-VL-7B', input_summary: 'Equipment_Inspection_Q2.pdf (24 pages)', output_summary: 'inspection_summary.xlsx', duration_ms: 4230, status: 'SUCCESS', input_hash: 'a3f2c9d1', output_hash: 'b7e4a210', chain_hash: 'c9f3b201', previous_hash: '0000000000000000', timestamp: new Date(Date.now() - 2*60000).toISOString() },
    { id: 'LOG-20260831-0002', user: 'dev_karthik', user_role: 'Software Engineer', task_type: 'Code Generation', model_used: 'DeepSeek-Coder-V2-Lite', input_summary: 'JSON sensor log parser', output_summary: 'anomaly_detector.py', duration_ms: 3890, status: 'SUCCESS', input_hash: 'd8f1a920', output_hash: 'e2b3c410', chain_hash: 'f1a2c930', previous_hash: 'c9f3b201', timestamp: new Date(Date.now() - 18*60000).toISOString() },
    { id: 'LOG-20260831-0003', user: 'manager_sunita', user_role: 'Operations Manager', task_type: 'Policy Q&A', model_used: 'Phi-3-Mini-4K', input_summary: 'High-value procurement query', output_summary: '5-step approval process', duration_ms: 2710, status: 'SUCCESS', input_hash: 'g9c2b830', output_hash: 'h3d4e510', chain_hash: 'i4e5f640', previous_hash: 'f1a2c930', timestamp: new Date(Date.now() - 34*60000).toISOString() },
    { id: 'LOG-20260831-0004', user: 'analyst_rajan', user_role: 'Quality Analyst', task_type: 'Document Drafting', model_used: 'Qwen2.5-7B', input_summary: 'Approval note from Safety_Policy_2025.docx', output_summary: 'Approval note draft', duration_ms: 3140, status: 'SUCCESS', input_hash: 'j5f6g750', output_hash: 'k6g7h860', chain_hash: 'l7h8i970', previous_hash: 'i4e5f640', timestamp: new Date(Date.now() - 52*60000).toISOString() },
    { id: 'LOG-20260831-0005', user: 'dev_meera', user_role: 'ML Engineer', task_type: 'Code Generation', model_used: 'DeepSeek-Coder-V2-Lite', input_summary: 'REST API client for data pipeline', output_summary: 'api_client.py (134 lines)', duration_ms: 5120, status: 'SUCCESS', input_hash: 'm8i9j080', output_hash: 'n9j0k190', chain_hash: 'o0k1l200', previous_hash: 'l7h8i970', timestamp: new Date(Date.now() - 74*60000).toISOString() },
    { id: 'LOG-20260831-0006', user: 'admin_vikram', user_role: 'System Administrator', task_type: 'Document Analysis', model_used: 'Qwen2.5-VL-7B', input_summary: 'Network_Topology_Diagram.png', output_summary: 'Topology analysis report', duration_ms: 2890, status: 'SUCCESS', input_hash: 'p1l2m310', output_hash: 'q2m3n420', chain_hash: 'r3n4o530', previous_hash: 'o0k1l200', timestamp: new Date(Date.now() - 95*60000).toISOString() },
    { id: 'LOG-20260831-0007', user: 'analyst_priya', user_role: 'Data Analyst', task_type: 'Data Extraction', model_used: 'Qwen2.5-7B', input_summary: 'QC_Checklist.xlsx — extract failed items', output_summary: 'Failed items report: 7 flagged', duration_ms: 1980, status: 'SUCCESS', input_hash: 's4o5p640', output_hash: 't5p6q750', chain_hash: 'u6q7r860', previous_hash: 'r3n4o530', timestamp: new Date(Date.now() - 112*60000).toISOString() },
    { id: 'LOG-20260831-0008', user: 'manager_anand', user_role: 'Department Manager', task_type: 'Policy Q&A', model_used: 'Phi-3-Mini-4K', input_summary: 'Leave encashment policy query', output_summary: 'Leave policy clarification', duration_ms: 1640, status: 'SUCCESS', input_hash: 'v7r8s970', output_hash: 'w8s9t080', chain_hash: 'x9t0u190', previous_hash: 'u6q7r860', timestamp: new Date(Date.now() - 130*60000).toISOString() },
    { id: 'LOG-20260831-0009', user: 'dev_karthik', user_role: 'Software Engineer', task_type: 'Code Review', model_used: 'DeepSeek-Coder-V2-Lite', input_summary: 'data_pipeline.py (230 lines)', output_summary: 'Code review: 4 issues, 2 security warnings', duration_ms: 4560, status: 'SUCCESS', input_hash: 'y0u1v200', output_hash: 'z1v2w310', chain_hash: 'a2w3x420', previous_hash: 'x9t0u190', timestamp: new Date(Date.now() - 148*60000).toISOString() },
    { id: 'LOG-20260831-0010', user: 'analyst_rajan', user_role: 'Quality Analyst', task_type: 'Document Analysis', model_used: 'Qwen2.5-VL-7B', input_summary: 'Safety_Audit_Report_Aug2026.pdf', output_summary: '14 observations, 3 non-conformances', duration_ms: 5870, status: 'SUCCESS', input_hash: 'b3x4y530', output_hash: 'c4y5z640', chain_hash: 'd5z6a750', previous_hash: 'a2w3x420', timestamp: new Date(Date.now() - 168*60000).toISOString() },
  ];
  return entries;
};

export default function AuditPage() {
  const [logs, setLogs] = useState(buildMockLogs());

  useEffect(() => {
    const load = async () => {
      try {
        const res = await axios.get('http://localhost:8000/api/audit/logs', { timeout: 3000 });
        setLogs(res.data.logs);
      } catch { /* use mock */ }
    };
    load();
  }, []);

  return (
    <div className="max-w-6xl">
      <div className="mb-6">
        <h1 className="text-xl font-bold text-text-primary flex items-center gap-2">
          <ScrollText size={20} className="text-accent" />
          Audit Log
        </h1>
        <p className="text-sm text-text-muted mt-0.5">Immutable, hash-chained record of all AI operations</p>
      </div>
      <AuditLog logs={logs} />
    </div>
  );
}
