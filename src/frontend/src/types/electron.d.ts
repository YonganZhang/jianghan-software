export interface ElectronAPI {
  getVersion: () => string
  getPlatform: () => string
  sendMessage: (message: any) => void
  onMessage: (callback: (event: any, ...args: any[]) => void) => void
  openFile: (options?: {
    properties?: string[]
    filters?: Array<{ name: string; extensions: string[] }>
  }) => Promise<string | null>
}

declare global {
  interface Window {
    electronAPI: ElectronAPI
  }
}

