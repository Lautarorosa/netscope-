import type { ScanStatus } from '../types'

interface Props {
  status: ScanStatus
  statusText: string
}

const STATUS_LABEL: Record<ScanStatus, string> = {
  idle: 'Ready',
  scanning: '',
  done: '',
  error: '',
}

export function Topbar({ status, statusText }: Props) {
  return (
    <header style={styles.topbar}>
      <div style={styles.topbarLine} />
      <a href="#" style={styles.logo}>
        <div style={styles.logoIcon}>
          <svg viewBox="0 0 24 24" width={15} height={15} fill="none" stroke="var(--cyan)" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="3"/>
            <path d="M12 2a10 10 0 0 1 0 20A10 10 0 0 1 12 2"/>
            <path d="M12 6a6 6 0 0 1 0 12A6 6 0 0 1 12 6"/>
          </svg>
        </div>
        <span style={styles.logoText}>NETSCOPE</span>
      </a>

      <div style={styles.center}>
        <div style={styles.statusWrap}>
          <div style={{ ...styles.dot, ...dotStyle(status) }} />
          <span style={styles.statusText}>{statusText || STATUS_LABEL[status]}</span>
        </div>
      </div>

      <div style={styles.right}>
        <span style={styles.tag}>v2.0</span>
      </div>
    </header>
  )
}

function dotStyle(status: ScanStatus): React.CSSProperties {
  if (status === 'scanning') return { background: 'var(--cyan)', boxShadow: '0 0 0 3px rgba(121,192,255,.18)', animation: 'blink 1.2s infinite' }
  if (status === 'done')     return { background: 'var(--low)' }
  if (status === 'error')    return { background: 'var(--crit)' }
  return { background: 'var(--dimmer)' }
}

const styles: Record<string, React.CSSProperties> = {
  topbar: {
    gridColumn: '1 / -1',
    display: 'flex',
    alignItems: 'center',
    gap: 16,
    padding: '0 24px',
    borderBottom: '1px solid var(--border)',
    background: 'var(--surface)',
    zIndex: 10,
    position: 'relative',
    height: 56,
  },
  topbarLine: {
    position: 'absolute',
    bottom: -1,
    left: 0,
    right: 0,
    height: 1,
    background: 'linear-gradient(90deg, var(--cyan-dim), transparent 60%)',
    opacity: 0.4,
  },
  logo: {
    display: 'flex',
    alignItems: 'center',
    gap: 10,
    flexShrink: 0,
    textDecoration: 'none',
  },
  logoIcon: {
    width: 30,
    height: 30,
    border: '1.5px solid var(--cyan-dim)',
    borderRadius: 7,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    background: 'var(--cyan-glow)',
  },
  logoText: {
    fontSize: 12,
    fontWeight: 600,
    letterSpacing: '0.18em',
    color: 'var(--cyan)',
    fontFamily: 'var(--font-mono)',
  },
  center: {
    flex: 1,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  statusWrap: {
    display: 'flex',
    alignItems: 'center',
    gap: 8,
    fontSize: 11,
    color: 'var(--muted)',
    fontFamily: 'var(--font-mono)',
  },
  dot: {
    width: 7,
    height: 7,
    borderRadius: '50%',
    flexShrink: 0,
    transition: 'background .3s',
  },
  statusText: {},
  right: {
    display: 'flex',
    alignItems: 'center',
    gap: 12,
  },
  tag: {
    fontSize: 10,
    fontFamily: 'var(--font-mono)',
    color: 'var(--dimmer)',
    letterSpacing: '0.08em',
    padding: '3px 8px',
    border: '1px solid var(--border2)',
    borderRadius: 4,
  },
}
