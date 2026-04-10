import { useRef, useCallback } from 'react'
import type { PortResult, WsProgress } from '../types'

interface WsCallbacks {
  onProgress: (p: WsProgress) => void
  onPort: (port: PortResult) => void
  onDone: (data: { scan_id: number; open_count: number; total: number; duration: number; target: string; hostname: string }) => void
  onError: (msg: string) => void
}

interface ScanParams {
  target: string
  port_from: number
  port_to: number
  threads: number
  timeout: number
}

export function useWebSocket() {
  const wsRef = useRef<WebSocket | null>(null)

  const connect = useCallback((params: ScanParams, callbacks: WsCallbacks) => {
    const proto = location.protocol === 'https:' ? 'wss' : 'ws'
    const ws = new WebSocket(`${proto}://${location.host}/ws/scan`)
    wsRef.current = ws

    ws.onopen = () => {
      ws.send(JSON.stringify(params))
    }

    ws.onmessage = (e) => {
      const msg = JSON.parse(e.data)
      switch (msg.type) {
        case 'progress':
          callbacks.onProgress({ done: msg.done, total: msg.total })
          break
        case 'port':
          callbacks.onPort({
            port: msg.port,
            state: msg.state,
            service: msg.service,
            banner: msg.banner,
            cve: msg.cve,
            severity: msg.severity,
            cve_desc: msg.cve_desc,
          })
          break
        case 'done':
          callbacks.onDone({
            scan_id: msg.scan_id,
            open_count: msg.open_count,
            total: msg.total,
            duration: msg.duration,
            target: msg.target,
            hostname: msg.hostname,
          })
          break
        case 'error':
          callbacks.onError(msg.msg || 'Unknown error')
          break
      }
    }

    ws.onerror = () => callbacks.onError('WebSocket connection failed. Is the server running?')
    ws.onclose = () => { /* handled by caller */ }
  }, [])

  const stop = useCallback(() => {
    if (wsRef.current) {
      try { wsRef.current.send(JSON.stringify({ type: 'stop' })) } catch { /* ignore */ }
      wsRef.current.close()
      wsRef.current = null
    }
  }, [])

  return { connect, stop }
}
