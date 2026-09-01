import { useState, useRef } from 'react';
import { Upload, FileText, Image, FileSpreadsheet, FileCode, X } from 'lucide-react';

const FORMAT_OPTIONS = ['Word Doc', 'Excel', 'PowerPoint', 'Code', 'JSON'];

const FORMAT_ICONS = {
  'Word Doc': '📝',
  'Excel': '📊',
  'PowerPoint': '📸',
  'Code': '💻',
  'JSON': '{ }',
};

const FILE_ICONS = {
  pdf: FileText,
  docx: FileText,
  xlsx: FileSpreadsheet,
  png: Image,
  jpg: Image,
  jpeg: Image,
  py: FileCode,
};

function getFileIcon(filename) {
  const ext = filename?.split('.').pop()?.toLowerCase();
  return FILE_ICONS[ext] || FileText;
}

export default function TaskInput({ onSubmit, isLoading }) {
  const [task, setTask] = useState('');
  const [format, setFormat] = useState('Word Doc');
  const [file, setFile] = useState(null);
  const [dragOver, setDragOver] = useState(false);
  const fileRef = useRef(null);

  const handleFile = (f) => {
    if (f) setFile(f);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const f = e.dataTransfer.files[0];
    if (f) handleFile(f);
  };

  const handleSubmit = () => {
    if (!task.trim() && !file) return;
    onSubmit({ task: task.trim(), format, file });
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) handleSubmit();
  };

  const FileIcon = file ? getFileIcon(file.name) : Upload;

  return (
    <div className="space-y-4">
      {/* Task text area */}
      <div>
        <label className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-2 block">
          Task Description
        </label>
        <textarea
          id="task-input"
          value={task}
          onChange={e => setTask(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Describe your task... (Ctrl+Enter to submit)"
          rows={6}
          className="w-full rounded-lg p-4 text-sm text-text-primary resize-none outline-none transition-all duration-200"
          style={{
            background: '#1A2E4A',
            border: '1px solid rgba(0,200,150,0.2)',
            fontFamily: 'Inter, sans-serif',
          }}
          onFocus={e => e.target.style.borderColor = 'rgba(0,200,150,0.6)'}
          onBlur={e => e.target.style.borderColor = 'rgba(0,200,150,0.2)'}
        />
      </div>

      {/* File upload */}
      <div>
        <label className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-2 block">
          Attach File (optional)
        </label>
        <div
          className={`drop-zone p-4 text-center cursor-pointer ${dragOver ? 'drag-over' : ''}`}
          onClick={() => fileRef.current?.click()}
          onDragOver={e => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
        >
          {file ? (
            <div className="flex items-center justify-between px-2">
              <div className="flex items-center gap-3">
                <FileIcon size={20} className="text-accent" />
                <div className="text-left">
                  <p className="text-sm text-text-primary font-medium">{file.name}</p>
                  <p className="text-xs text-text-muted">
                    {(file.size / 1024).toFixed(1)} KB
                  </p>
                </div>
              </div>
              <button
                onClick={e => { e.stopPropagation(); setFile(null); }}
                className="text-text-muted hover:text-danger transition-colors p-1"
              >
                <X size={16} />
              </button>
            </div>
          ) : (
            <div className="py-2">
              <Upload size={24} className="mx-auto text-text-muted mb-2 opacity-50" />
              <p className="text-sm text-text-muted">
                Drop file here or <span className="text-accent">browse</span>
              </p>
              <p className="text-xs text-text-muted opacity-60 mt-1">PDF, DOCX, XLSX, PNG, JPG</p>
            </div>
          )}
        </div>
        <input
          ref={fileRef}
          type="file"
          className="hidden"
          accept=".pdf,.docx,.xlsx,.png,.jpg,.jpeg,.py,.txt"
          onChange={e => handleFile(e.target.files[0])}
        />
      </div>

      {/* Output format selector */}
      <div>
        <label className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-2 block">
          Output Format
        </label>
        <div className="flex flex-wrap gap-2">
          {FORMAT_OPTIONS.map(f => (
            <button
              key={f}
              onClick={() => setFormat(f)}
              className={`pill ${format === f ? 'active' : ''}`}
              id={`format-${f.replace(' ', '-').toLowerCase()}`}
            >
              {FORMAT_ICONS[f]} {f}
            </button>
          ))}
        </div>
      </div>

      {/* Submit */}
      <button
        id="run-agent-btn"
        onClick={handleSubmit}
        disabled={isLoading || (!task.trim() && !file)}
        className="btn-primary w-full justify-center text-base py-3"
      >
        {isLoading ? (
          <>
            <span className="animate-spin-slow inline-block">⚙️</span>
            Running Agent...
          </>
        ) : (
          <>
            ▶ Run Agent
          </>
        )}
      </button>
      <p className="text-xs text-text-muted text-center">Ctrl+Enter to submit</p>
    </div>
  );
}
