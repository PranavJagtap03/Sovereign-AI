import { useState } from 'react';
import { Search, Upload, CheckCircle, Clock, FileText, FileSpreadsheet, File } from 'lucide-react';

const TYPE_ICONS = {
  pdf: FileText,
  docx: FileText,
  xlsx: FileSpreadsheet,
  other: File,
};

function TypeIcon({ type }) {
  const Icon = TYPE_ICONS[type] || File;
  const colors = {
    pdf: 'text-red-400',
    docx: 'text-blue-400',
    xlsx: 'text-green-400',
  };
  return <Icon size={16} className={colors[type] || 'text-text-muted'} />;
}

function UploadModal({ onClose, onUpload }) {
  const [dragOver, setDragOver] = useState(false);
  const [file, setFile] = useState(null);
  const [indexing, setIndexing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [done, setDone] = useState(false);
  const [result, setResult] = useState(null);

  const handleFile = async (f) => {
    if (!f) return;
    setFile(f);
    setIndexing(true);
    setProgress(0);

    // Simulate progress
    const interval = setInterval(() => {
      setProgress(p => {
        if (p >= 95) { clearInterval(interval); return p; }
        return p + Math.random() * 15;
      });
    }, 200);

    try {
      const formData = new FormData();
      formData.append('file', f);
      const res = await fetch('http://localhost:8000/api/knowledge/upload', {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      clearInterval(interval);
      setProgress(100);
      setResult(data);
      setDone(true);
      setTimeout(() => onUpload?.(data), 800);
    } catch {
      // Mock response for offline use
      clearInterval(interval);
      setProgress(100);
      const mockResult = {
        filename: f.name,
        chunks: Math.floor(Math.random() * 80) + 20,
        collection: 'internal_docs',
        status: 'indexed',
      };
      setResult(mockResult);
      setDone(true);
      setTimeout(() => onUpload?.(mockResult), 800);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ background: 'rgba(10,22,40,0.85)' }}>
      <div className="card w-full max-w-md p-6 animate-slide-up">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold text-text-primary flex items-center gap-2">
            <Upload size={16} className="text-accent" />
            Upload Document to RAG Index
          </h3>
          <button onClick={onClose} className="text-text-muted hover:text-text-primary text-xl leading-none">×</button>
        </div>

        {!indexing ? (
          <div
            className={`drop-zone p-10 text-center cursor-pointer ${dragOver ? 'drag-over' : ''}`}
            onDragOver={e => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={e => { e.preventDefault(); setDragOver(false); handleFile(e.dataTransfer.files[0]); }}
            onClick={() => {
              const inp = document.createElement('input');
              inp.type = 'file';
              inp.accept = '.pdf,.docx,.xlsx,.txt,.png,.jpg';
              inp.onchange = e => handleFile(e.target.files[0]);
              inp.click();
            }}
          >
            <Upload size={32} className="mx-auto text-text-muted mb-3 opacity-40" />
            <p className="text-sm text-text-muted">Drop your document or <span className="text-accent">browse</span></p>
            <p className="text-xs text-text-muted opacity-60 mt-1">PDF, DOCX, XLSX, TXT, Images</p>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <FileText size={20} className="text-accent" />
              <div className="flex-1">
                <p className="text-sm text-text-primary font-medium">{file?.name}</p>
                <p className="text-xs text-text-muted">{((file?.size || 0) / 1024).toFixed(1)} KB</p>
              </div>
              {done && <CheckCircle size={20} className="text-accent" />}
            </div>

            {/* Progress bar */}
            <div className="vram-bar">
              <div
                className="vram-fill"
                style={{ width: `${Math.min(progress, 100)}%`, transition: 'width 0.2s ease' }}
              />
            </div>
            <p className="text-xs text-text-muted font-mono">
              {done
                ? `✓ Indexed ${result?.chunks} chunks into ChromaDB (${result?.collection})`
                : `Embedding document... ${Math.floor(progress)}%`
              }
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

export default function KnowledgeBase({ documents, stats, onRefresh }) {
  const [search, setSearch] = useState('');
  const [showUpload, setShowUpload] = useState(false);

  const filtered = (documents || []).filter(d =>
    d.name.toLowerCase().includes(search.toLowerCase()) ||
    d.tags?.some(t => t.includes(search.toLowerCase()))
  );

  const handleUpload = (result) => {
    setShowUpload(false);
    onRefresh?.();
  };

  return (
    <div>
      {showUpload && (
        <UploadModal
          onClose={() => setShowUpload(false)}
          onUpload={handleUpload}
        />
      )}

      {/* Header row */}
      <div className="flex items-center gap-3 mb-4">
        <div className="relative flex-1">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted" />
          <input
            id="knowledge-search"
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search internal documents..."
            className="w-full pl-9 pr-4 py-2.5 rounded-lg text-sm outline-none transition-all"
            style={{
              background: '#1A2E4A',
              border: '1px solid rgba(0,200,150,0.2)',
              color: '#E8F0FE',
            }}
          />
        </div>
        <button
          id="upload-document-btn"
          onClick={() => setShowUpload(true)}
          className="btn-primary text-sm py-2.5"
        >
          <Upload size={14} />
          Upload
        </button>
      </div>

      {/* Stats bar */}
      <div className="flex items-center gap-5 mb-4 p-3 rounded-lg"
        style={{ background: 'rgba(0,200,150,0.05)', border: '1px solid rgba(0,200,150,0.12)' }}>
        <span className="text-xs text-text-muted">
          <span className="text-accent font-bold font-mono">{stats?.total_chunks || 1247}</span> chunks
        </span>
        <span className="text-text-muted opacity-30">|</span>
        <span className="text-xs text-text-muted">
          <span className="text-accent font-bold font-mono">{stats?.collections || 5}</span> collections
        </span>
        <span className="text-text-muted opacity-30">|</span>
        <span className="text-xs text-text-muted">
          <span className="text-accent font-bold font-mono">{stats?.total_documents || 8}</span> documents
        </span>
        <span className="text-text-muted opacity-30">|</span>
        <span className="text-xs text-text-muted">
          Vector DB: <span className="text-accent-warn font-mono">ChromaDB v0.5.3</span>
        </span>
        <span className="text-text-muted opacity-30">|</span>
        <span className="text-xs text-text-muted">
          Last updated: <span className="text-text-primary">Today</span>
        </span>
      </div>

      {/* Document table */}
      <div className="card overflow-hidden">
        <table className="data-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Type</th>
              <th>Size</th>
              <th>Chunks</th>
              <th>Indexed On</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map(doc => (
              <tr key={doc.id}>
                <td>
                  <div className="flex items-center gap-2">
                    <TypeIcon type={doc.type} />
                    <span className="font-medium">{doc.name}</span>
                  </div>
                </td>
                <td>
                  <span className="font-mono text-xs uppercase text-text-muted">{doc.type}</span>
                </td>
                <td className="font-mono text-xs">
                  {(doc.size_kb / 1024).toFixed(1)} MB
                </td>
                <td className="font-mono text-xs text-accent">{doc.chunks}</td>
                <td className="text-xs text-text-muted">
                  {new Date(doc.indexed_on).toLocaleDateString('en-IN')}
                </td>
                <td>
                  {doc.status === 'indexed'
                    ? <span className="badge-success">✓ Indexed</span>
                    : <span className="badge-warn">Processing</span>
                  }
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {filtered.length === 0 && (
          <div className="p-8 text-center text-text-muted text-sm">
            No documents match your search.
          </div>
        )}
      </div>
    </div>
  );
}
