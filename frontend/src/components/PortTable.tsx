import type { PortResult, Severity } from '../types'
import './PortTable.css'

interface Props {
  ports: PortResult[]
  scanId: number | null
  onExportPdf: () => void
}

const SEV_ORDER: Record<Severity, number> = { CRITICAL: 4, HIGH: 3, MEDIUM: 2, LOW: 1, NONE: 0 }

export function PortTable({ ports, scanId, onExportPdf }: Props) {
  const sorted = [...ports].sort((a, b) => SEV_ORDER[b.severity] - SEV_ORDER[a.severity] || a.port - b.port)

  return (
    <div className="pt-card">
      <div className="pt-head">
        <div className="pt-title">
          Port Results
          <span className="pt-count">{ports.length}</span>
        </div>
        <div className="pt-actions">
          <button className="pt-btn" onClick={onExportPdf} disabled={!scanId}>
            <svg viewBox="0 0 24 24" width={12} height={12} fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14,2 14,8 20,8"/>
              <line x1="16" y1="13" x2="8" y2="13"/>
              <line x1="16" y1="17" x2="8" y2="17"/>
            </svg>
            Export PDF
          </button>
        </div>
      </div>

      <div className="pt-wrap">
        <table>
          <thead>
            <tr>
              <th>Port</th>
              <th>Service</th>
              <th>Severity</th>
              <th>CVE</th>
              <th>Banner</th>
            </tr>
          </thead>
          <tbody>
            {sorted.length === 0 ? (
              <tr className="pt-empty">
                <td colSpan={5}>No results yet</td>
              </tr>
            ) : (
              sorted.map(p => (
                <tr key={p.port} className="pt-row">
                  <td className="pt-port">{p.port}</td>
                  <td className="pt-service">{p.service || '—'}</td>
                  <td>
                    <span className={`pt-badge pt-badge-${p.severity}`}>{p.severity}</span>
                  </td>
                  <td className="pt-cve">{p.cve || '—'}</td>
                  <td className="pt-banner" title={p.banner}>{p.banner || '—'}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
