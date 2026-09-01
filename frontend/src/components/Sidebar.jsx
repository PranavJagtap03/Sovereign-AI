import { useState } from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard, Plus, Database, ScrollText, Shield,
  Network, ChevronRight, ChevronLeft, Zap
} from 'lucide-react';

const NAV_ITEMS = [
  { to: '/',            icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/task',        icon: Plus,            label: 'New Task' },
  { to: '/knowledge',   icon: Database,        label: 'Knowledge Base' },
  { to: '/audit',       icon: ScrollText,      label: 'Audit Log' },
  { to: '/sovereignty', icon: Shield,          label: 'Sovereignty' },
  { to: '/models',      icon: Network,         label: 'Model Router' },
];

export default function Sidebar() {
  const [expanded, setExpanded] = useState(true);

  return (
    <aside
      className="flex flex-col border-r transition-all duration-300 ease-in-out flex-shrink-0"
      style={{
        width: expanded ? '220px' : '64px',
        background: '#0D1B33',
        borderColor: 'rgba(0,200,150,0.12)',
      }}
    >
      {/* Logo area */}
      <div className="flex items-center gap-3 px-4 py-5 border-b" style={{ borderColor: 'rgba(0,200,150,0.1)' }}>
        <div className="flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center"
          style={{ background: 'rgba(0,200,150,0.15)', border: '1px solid rgba(0,200,150,0.3)' }}>
          <Zap size={16} className="text-accent" />
        </div>
        {expanded && (
          <div className="min-w-0">
            <div className="text-xs font-bold text-accent tracking-wider truncate">SOVEREIGN AI</div>
            <div className="text-[10px] text-text-muted truncate">Code:201 | SIH 2026</div>
          </div>
        )}
      </div>

      {/* Nav items */}
      <nav className="flex-1 p-3 space-y-1">
        {NAV_ITEMS.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              `nav-item ${isActive ? 'active' : ''}`
            }
            title={!expanded ? label : undefined}
          >
            <Icon size={18} className="flex-shrink-0" />
            {expanded && <span className="text-sm font-medium">{label}</span>}
          </NavLink>
        ))}
      </nav>

      {/* Toggle button */}
      <button
        onClick={() => setExpanded(e => !e)}
        className="flex items-center justify-center p-3 m-3 rounded-lg transition-all"
        style={{ background: 'rgba(0,200,150,0.06)', border: '1px solid rgba(0,200,150,0.12)' }}
        title={expanded ? 'Collapse sidebar' : 'Expand sidebar'}
      >
        {expanded
          ? <ChevronLeft size={16} className="text-text-muted" />
          : <ChevronRight size={16} className="text-text-muted" />
        }
      </button>
    </aside>
  );
}
