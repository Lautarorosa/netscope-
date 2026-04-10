export type Severity = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'NONE'

export interface PortResult {
  port: number
  state: string
  service: string
  banner: string
  cve: string
  severity: Severity
  cve_desc: string
}

export interface ScanSummary {
  id: number
  target: string
  hostname: string
  open_count: number
  total_ports: number
  duration: number
  critical: number
  high: number
  created_at: string
}

export interface ScanDetail {
  scan: {
    id: number
    target: string
    hostname: string
    open_count: number
    total_ports: number
    duration: number
    critical: number
    high: number
    created_at: string
    start_time: string
    end_time: string
  }
  ports: PortResult[]
}

export type ScanStatus = 'idle' | 'scanning' | 'done' | 'error'

export interface ScanStats {
  open: number
  critical: number
  high: number
  duration: number | null
  total: number
}

export interface WsProgress {
  done: number
  total: number
}

export interface Toast {
  id: number
  msg: string
  type: 'success' | 'error' | 'info'
}
