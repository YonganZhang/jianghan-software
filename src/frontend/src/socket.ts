import { reactive } from 'vue'
import mitt from 'mitt'

declare const io: any
const MAX_POINTS = 1000 // 最多保留的点数
const MAX_LOGS = 500 // 日志条数上限，防止内存无限增长
const TRAIN_LOSS_SERIES_NAME: Record<string, string> = {
  trainloss: '损失',
  trainloss1: '训练集总损失',
  trainloss2: '训练集数据损失',
  trainloss3: '训练集知识嵌入损失',
  trainloss4: '验证集总损失',
  trainloss5: '验证集数据损失',
  trainloss6: '验证集知识嵌入损失',
}

export interface Point {
  seriesName: string
  x: number
  y: number
}

interface ServerToClientEvents {
  connect: () => void
  disconnect: () => void
  message: (data: string) => void
}

interface ClientToServerEvents {
  sendMessage: (data: string) => void
}

type Events = {
  train: Point[]
  verify: Point[]
  trainLoss: Point[]
}

export const eventBus = mitt<Events>()

// 管理状态
export const state = reactive({
  isConnected: false,
  logs: [] as { type: string; content: string; ts: number; time: string }[],
})

let socket: any | null = null
let hasBoundEvents = false
let frontendLogCounter = 0

function reportFrontendLog(level: 'INFO' | 'WARN' | 'ERROR', message: string, extra?: unknown) {
  // 采样上报，避免高频事件刷爆日志文件
  frontendLogCounter += 1
  if (frontendLogCounter % 5 !== 0 && level === 'INFO') return
  fetch('/api/debug/frontend-log', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      level,
      source: 'frontend.socket',
      message,
      extra,
    }),
    keepalive: true,
  }).catch(() => {
    // 忽略上报失败，不影响业务
  })
}

function formatLogTime(date: Date) {
  const pad2 = (n: number) => String(n).padStart(2, '0')
  const pad3 = (n: number) => String(n).padStart(3, '0')
  return `${pad2(date.getHours())}:${pad2(date.getMinutes())}:${pad2(date.getSeconds())}.${pad3(
    date.getMilliseconds()
  )}`
}

const NOISE_LINE_PATTERNS: RegExp[] = [
  // tqdm 进度条碎片
  /^\s*\d{1,3}%\|/,
]

function isNoiseLogLine(line: string) {
  const trimmed = line.trim()
  if (!trimmed) return true
  return NOISE_LINE_PATTERNS.some((re) => re.test(trimmed))
}

function pushLogLines(type: string, content: unknown) {
  const normalizedContent = typeof content === 'string' ? content : JSON.stringify(content, null, 2)
  const lines = String(normalizedContent).split(/\r?\n/)
  const now = new Date()
  const ts = now.getTime()
  const time = formatLogTime(now)
  lines.forEach((line) => {
    const cleaned = line.replace(/^\s*\[log\]\s*/i, '').trimEnd()
    if (isNoiseLogLine(cleaned)) return
    state.logs.push({ type, content: cleaned, ts, time })
  })
  // 超过上限时丢弃最早的日志（在循环外统一截断，避免每行都 splice）
  if (state.logs.length > MAX_LOGS) {
    state.logs.splice(0, state.logs.length - MAX_LOGS)
  }
}

function bindSocketEvents(sock: any) {
  if (hasBoundEvents) return
  hasBoundEvents = true

  sock.on('connect', () => {
    state.isConnected = true
    reportFrontendLog('INFO', 'socket connected')
  })

  sock.on('disconnect', () => {
    state.isConnected = false
    reportFrontendLog('WARN', 'socket disconnected')
  })

  sock.on('connect_error', (err: any) => {
    state.isConnected = false
    reportFrontendLog('ERROR', 'socket connect_error', String(err?.message || err || 'unknown'))
  })

  sock.on('data', (payload: any) => {
    if (payload.event === 'log') {
      const { type, content } = payload.data
      pushLogLines(type, content)
    }
  })

  sock.on('multitype_log', (data: any) => {
    const { event, data: innerData } = data
    if (!innerData) {
      reportFrontendLog('WARN', 'multitype_log missing data', data)
      return
    }
    const { type, content } = innerData
    const seriesName = TRAIN_LOSS_SERIES_NAME[type] ?? type

    let targetEvent: keyof Events | null = null

    if (event.startsWith('trainloss')) targetEvent = 'trainLoss'
    else if (event.startsWith('tuyi')) targetEvent = 'train'
    else if (event.startsWith('tuer')) targetEvent = 'verify'

    if (event === 'log') {
      pushLogLines(type, content)
    } else {
      let points: Point[] = []
      if (Array.isArray(content) && Array.isArray(content[0])) {
        points = (content as [number, number][]).map(([x, y]) => ({
          seriesName,
          x,
          y,
        }))
      } else if (Array.isArray(content) && content.length >= 2) {
        const [x, y] = content as [number, number]
        points = [{ seriesName, x, y }]
      } else {
        reportFrontendLog('WARN', 'invalid multitype_log content', { event, type, content })
        return
      }
      if (targetEvent) {
        eventBus.emit(targetEvent, points)
      }
    }
  })
}

export function initSocket(url: string = window.location.origin) {
  if (socket) return socket
  if (typeof io !== 'function') return null

  socket = io(url, {
    // Flask-SocketIO(threading) 在当前部署下对 websocket 升级不稳定，固定 polling
    transports: ['polling'],
    upgrade: false,
    reconnection: true,
    reconnectionAttempts: 10,
    reconnectionDelay: 800,
    timeout: 5000,
  })
  bindSocketEvents(socket)
  return socket
}

export function getSocket() {
  return socket
}

export function disconnectSocket() {
  if (socket) {
    socket.disconnect()
  }
  socket = null
  hasBoundEvents = false
  state.isConnected = false
}
