import { useEffect, useState } from 'react';
import KnowledgeBase from '../components/KnowledgeBase';
import axios from 'axios';
import { Database } from 'lucide-react';

const MOCK_DOCS = [
  { id: 'doc_001', name: 'SOP_Manual_v2.pdf', type: 'pdf', size_kb: 2847, chunks: 184, indexed_on: '2026-08-15T09:23:00', status: 'indexed', tags: ['sop'] },
  { id: 'doc_002', name: 'Safety_Policy_2025.docx', type: 'docx', size_kb: 1203, chunks: 97, indexed_on: '2026-08-18T14:45:00', status: 'indexed', tags: ['safety'] },
  { id: 'doc_003', name: 'QC_Checklist.xlsx', type: 'xlsx', size_kb: 456, chunks: 43, indexed_on: '2026-08-20T11:12:00', status: 'indexed', tags: ['quality'] },
  { id: 'doc_004', name: 'Procurement_Policy_v3.pdf', type: 'pdf', size_kb: 1876, chunks: 152, indexed_on: '2026-08-22T16:30:00', status: 'indexed', tags: ['procurement'] },
  { id: 'doc_005', name: 'Equipment_Maintenance_Standards.pdf', type: 'pdf', size_kb: 3412, chunks: 278, indexed_on: '2026-08-25T10:00:00', status: 'indexed', tags: ['maintenance'] },
  { id: 'doc_006', name: 'HR_Leave_Policy.pdf', type: 'pdf', size_kb: 634, chunks: 51, indexed_on: '2026-08-28T09:15:00', status: 'indexed', tags: ['hr'] },
  { id: 'doc_007', name: 'Network_Security_Guidelines.pdf', type: 'pdf', size_kb: 921, chunks: 73, indexed_on: '2026-08-29T14:22:00', status: 'indexed', tags: ['security'] },
  { id: 'doc_008', name: 'Maintenance_Budget_2025.pdf', type: 'pdf', size_kb: 1124, chunks: 89, indexed_on: '2026-08-30T11:45:00', status: 'indexed', tags: ['budget'] },
];

export default function KnowledgePage() {
  const [documents, setDocuments] = useState(MOCK_DOCS);
  const [stats, setStats] = useState({ total_chunks: 1247, total_documents: 8, collections: 5 });

  const load = async () => {
    try {
      const res = await axios.get('http://localhost:8000/api/knowledge/documents', { timeout: 3000 });
      setDocuments(res.data.documents);
      setStats(res.data.stats);
    } catch {
      // Use mock data
    }
  };

  useEffect(() => { load(); }, []);

  return (
    <div className="max-w-6xl">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl font-bold text-text-primary flex items-center gap-2">
            <Database size={20} className="text-accent" />
            Knowledge Base
          </h1>
          <p className="text-sm text-text-muted mt-0.5">Manage your RAG document index — powered by ChromaDB (local)</p>
        </div>
      </div>
      <KnowledgeBase documents={documents} stats={stats} onRefresh={load} />
    </div>
  );
}
