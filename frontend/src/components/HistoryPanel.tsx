import type { ScanSummary } from '../types'
import './HistoryPanel.css'

interface Props {
  history: ScanSummary[]
  activeScanId: number | null
  onSelect: (id: number) => void
  onDelete: (id: number) => void
}

export function HistoryPanel({ history, activeScanId, onSelect, onDelete }: Props) {
  return (
    <div className="hp-block">
      <div className="hp-label">
        History
        <span className="hp-label-line" />
      </div>

      {history.length === 0 ? (
        <div className="hp-empty">No scans yet</div>
      ) : (
        <div className="hp-list">
          {history.map(s => (
            <div
              key={s.id}
              className={`hp-item ${s.id === activeScanId ? 'active' : ''}`}
              onClick={() => onSelect(s.id)}
            >
              <div className="hp-target">{s.target}</div>
              <div className="hp-meta">
                <span>{s.created_at ? s.created_at.slice(0, 16).replace('T', ' ') : ''}</span>
              </div>
              <div className="hp-badges">
                <span className="hp-badge hp-badge-open">{s.open_count} open</span>
                {s.critical > 0 && (
                  <span className="hp-badge hp-badge-crit">{s.critical} crit</span>
                )}
              </div>
              <button
                className="hp-del"
                onClick={e => { e.stopPropagation(); onDelete(s.id) }}
                title="Delete"
              >
                ×
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
