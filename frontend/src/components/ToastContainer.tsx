import type { Toast } from '../types'

interface Props {
  toasts: Toast[]
}

export function ToastContainer({ toasts }: Props) {
  if (toasts.length === 0) return null

  return (
    <div style={styles.wrap}>
      {toasts.map(t => (
        <div key={t.id} style={{ ...styles.toast, ...toastStyle(t.type) }}>
          {t.msg}
        </div>
      ))}
    </div>
  )
}

function toastStyle(type: Toast['type']): React.CSSProperties {
  if (type === 'success') return { borderLeft: '3px solid var(--low)' }
  if (type === 'error')   return { borderLeft: '3px solid var(--crit)' }
  return { borderLeft: '3px solid var(--cyan-dim)' }
}

const styles: Record<string, React.CSSProperties> = {
  wrap: {
    position: 'fixed',
    bottom: 24,
    right: 24,
    display: 'flex',
    flexDirection: 'column',
    gap: 8,
    zIndex: 100,
  },
  toast: {
    background: 'var(--surface2)',
    border: '1px solid var(--border2)',
    borderRadius: 8,
    padding: '10px 16px',
    fontSize: 12,
    fontFamily: 'var(--font-mono)',
    color: 'var(--text)',
    minWidth: 220,
    maxWidth: 320,
    animation: 'toastIn .25s ease',
  },
}
