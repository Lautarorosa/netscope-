import type { ScanStats } from '../types'

interface Props {
  stats: ScanStats
}

export function StatsGrid({ stats }: Props) {
  return (
    <div style={styles.grid}>
      <div style={{ ...styles.card, ...styles.cardOpen }}>
        <div style={styles.label}>Open Ports</div>
        <div style={{ ...styles.value, color: 'var(--cyan)' }}>{stats.open}</div>
        <div style={styles.sub}>of {stats.total} scanned</div>
      </div>

      <div style={{ ...styles.card, ...styles.cardCrit }}>
        <div style={styles.label}>Critical</div>
        <div style={{ ...styles.value, color: 'var(--crit)' }}>{stats.critical}</div>
        <div style={styles.sub}>vulnerabilities</div>
      </div>

      <div style={{ ...styles.card, ...styles.cardHigh }}>
        <div style={styles.label}>High</div>
        <div style={{ ...styles.value, color: 'var(--high)' }}>{stats.high}</div>
        <div style={styles.sub}>vulnerabilities</div>
      </div>

      <div style={styles.card}>
        <div style={styles.label}>Duration</div>
        <div style={{ ...styles.value, fontSize: 20, color: 'var(--text)' }}>
          {stats.duration !== null ? `${stats.duration}s` : '—'}
        </div>
        <div style={styles.sub}>seconds</div>
      </div>
    </div>
  )
}

const styles: Record<string, React.CSSProperties> = {
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(4, 1fr)',
    gap: 12,
  },
  card: {
    background: 'var(--surface)',
    border: '1px solid var(--border)',
    borderRadius: 10,
    padding: '14px 16px',
  },
  cardOpen: {},
  cardCrit: {},
  cardHigh: {},
  label: {
    fontSize: 10,
    color: 'var(--muted)',
    fontFamily: 'var(--font-mono)',
    letterSpacing: '.07em',
    textTransform: 'uppercase',
    marginBottom: 8,
  },
  value: {
    fontSize: 28,
    fontWeight: 600,
    fontFamily: 'var(--font-mono)',
    lineHeight: 1,
  },
  sub: {
    fontSize: 10,
    color: 'var(--muted)',
    marginTop: 5,
  },
}
