export function Welcome() {
  return (
    <div style={styles.wrap}>
      <div style={styles.icon}>
        <svg viewBox="0 0 24 24" width={26} height={26} fill="none" stroke="var(--dimmer)" strokeWidth={1.5} strokeLinecap="round">
          <circle cx="12" cy="12" r="3"/>
          <path d="M2 12h3M19 12h3M12 2v3M12 19v3"/>
          <path d="M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M5.6 18.4l2.1-2.1M16.3 7.7l2.1-2.1"/>
        </svg>
      </div>
      <h2 style={styles.h2}>Network Port Scanner</h2>
      <p style={styles.p}>Enter a target IP or hostname and configure your scan parameters to get started.</p>
      <div style={styles.hint}>← Configure &amp; run a scan from the sidebar</div>
    </div>
  )
}

const styles: Record<string, React.CSSProperties> = {
  wrap: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: '60vh',
    textAlign: 'center',
    gap: 12,
  },
  icon: {
    width: 56,
    height: 56,
    border: '1.5px solid var(--border2)',
    borderRadius: 14,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 8,
    background: 'var(--surface)',
  },
  h2: {
    fontSize: 18,
    fontWeight: 500,
    color: 'var(--text)',
    fontFamily: 'var(--font-sans)',
    margin: 0,
  },
  p: {
    fontSize: 13,
    color: 'var(--muted)',
    maxWidth: 320,
    lineHeight: 1.6,
    margin: 0,
  },
  hint: {
    fontSize: 11,
    color: 'var(--dimmer)',
    fontFamily: 'var(--font-mono)',
    border: '1px solid var(--border)',
    borderRadius: 6,
    padding: '6px 12px',
    marginTop: 4,
  },
}
