// src/utils/auth.ts

const TOKEN_KEY = 'app_token' // token 存储 key
const REFRESH_TOKEN_KEY = 'app_refresh_token' // 刷新 token

/**
 * 获取 Token
 */
export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

/**
 * 设置 Token
 */
export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token)
}

/**
 * 移除 Token
 */
export function removeToken(): void {
  localStorage.removeItem(TOKEN_KEY)
}

/**
 * 获取刷新 Token
 */
export function getRefreshToken(): string | null {
  return localStorage.getItem(REFRESH_TOKEN_KEY)
}

/**
 * 设置刷新 Token
 */
export function setRefreshToken(refreshToken: string): void {
  localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken)
}

/**
 * 移除刷新 Token
 */
export function removeRefreshToken(): void {
  localStorage.removeItem(REFRESH_TOKEN_KEY)
}

/**
 * 判断是否已登录
 */
export function isLoggedIn(): boolean {
  return !!getToken()
}

/**
 * 退出登录，清理所有登录信息
 */
export function logout(): void {
  removeToken()
  removeRefreshToken()
  // 其他清理操作，比如清除用户信息等
}

/**
 * (可选) 实现 Token 刷新逻辑
 * 具体实现视后端刷新接口而定
 */
export async function refreshToken(): Promise<string | null> {
  const refreshToken = getRefreshToken()
  if (!refreshToken) return null

  try {
    // 这里换成你的刷新接口请求
    const res = await fetch('/api/auth/refresh', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refreshToken }),
    })
    if (!res.ok) throw new Error('刷新Token失败')

    const data = await res.json()
    if (data.token) {
      setToken(data.token)
      if (data.refreshToken) {
        setRefreshToken(data.refreshToken)
      }
      return data.token
    }
  } catch (error) {
    console.log('登出错误：', error)
    logout()
    return null
  }
  return null
}
