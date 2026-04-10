import type { WsProgress } from '../types'

interface Props {
  target: string
  progress: WsProgress
  openCount: number
}

export function Progress({ target, progress, openCount }: Props) {
  const pct = progress.total > 0 ? Math.round((progress.done / progress.total) * 100) : 0

  return (
    <div style={styles.wrap}>
      <div style={styles.header}>
        <span style={styles.target}>{target}</span>
        <span style={styles.pct}>{pct}%</span>
      </div>
      <div style={styles.barBg}>
        <div style={{ ...styles.bar, width: `${pct}%` }} />
      </div>
      <div style={styles.footer}>
        <span style={styles.counts}>{progress.done} / {progress.total} ports</span>
        <span style={styles.counts}>{openCount} open</span>
      </div>
    </div>
  )
}

const styles: Record<string, React.CSSProperties> = {
  wrap: {
    background: 'var(--surface)',
    border: '1px solid var(--border)',
    borderRadius: 10,
    padding: '16px 20px',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  target: {
    fontFamily: 'var(--font-mono)',
    fontSize: 12,
    color: 'var(--cyan)',
  },
  pct: {
    fontFamily: 'var(--font-mono)',
    fontSize: 12,
    color: 'var(--muted)',
  },
  barBg: {
    background: 'var(--border)',
    borderRadius: 4,
    height: 4,
    overflow: 'hidden',
  },
  bar: {
    height: 4,
    borderRadius: 4,
    background: 'var(--cyan-dim)',
    transition: 'width .25s',
    boxShadow: '0 0 10px rgba(56,139,253,.5)',
  },
  footer: {
    display: 'flex',
    justifyContent: 'space-between',
    marginTop: 8,
  },
  counts: {
    fontFamily: 'var(--font-mono)',
    fontSize: 10,
    color: 'var(--muted)',
  },
}
