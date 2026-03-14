import axios from 'axios'
import { message } from 'ant-design-vue'
import { getToken, logout } from './auth'
import { HTTP_STATUS, HTTP_ERROR_MSG } from './httpStatus'
import router from '../router'

// mock开关，true为mock，false为真实后端
// const USE_MOCK = false // 切换为false即为真实后端

// const instance = axios.create({
//   baseURL: USE_MOCK ? '/' : '/api',
//   timeout: 300000,
// })

const baseURL = '/api'
const instance = axios.create({
  baseURL,
  timeout: 6000000,
})

// 请求拦截器
instance.interceptors.request.use(
  async (config) => {
    // 自动携带token
    const token = getToken()
    if (token) {
      config.headers = config.headers || {}
      config.headers['Authorization'] = `Bearer ${token}`
    }
    if (!config.headers['Content-Type']) {
      config.headers['Content-Type'] = 'application/json'
    }
    return config
  },
  (error) => {
    message.error('请求发送失败')
    return Promise.reject(error)
  }
)

// 响应拦截器
instance.interceptors.response.use(
  async (response) => {
    const { data } = response

    // 检查业务状态码
    if (data?.code === 401 || data?.code === '401') {
      logout()
      message.error('登录已过期，请重新登录')
      router.push('/')
      return Promise.reject(new Error('登录已过期'))
    }

    return data
  },
  async (error) => {
    const { response, config } = error
    const isSilent = (config as any)?.silent === true // 静默模式：不弹出错误提示

    if (!response) {
      if (!isSilent) {
        const backendHint = import.meta.env.PROD
          ? baseURL
          : 'http://127.0.0.1:5000（通过 /api 代理）'
        message.error(`网络异常，无法连接后端服务：${backendHint}`)
      }
      return Promise.reject(error)
    }

    const status = response.status
    const serverMsg = response.data?.message || response.data?.error || response.data?.msg
    const msg = serverMsg || HTTP_ERROR_MSG[status] || `请求错误 [${status}]`

    if (status === HTTP_STATUS.UNAUTHORIZED) {
      logout()
      if (!isSilent) {
        message.error(msg)
      }
      router.push('/')
      const wrappedError = new Error(msg)
      ; (wrappedError as any).cause = error
      ; (wrappedError as any).response = response  // 保留response对象
      ; (wrappedError as any).config = config      // 保留config对象
      return Promise.reject(wrappedError)
    }

    // 普通错误统一弹窗提示（静默模式下不弹窗）
    if (!isSilent) {
      message.error(msg)
    }
    // 保留完整的错误对象，包括response数据
    const wrappedError = new Error(msg)
    ; (wrappedError as any).cause = error
    ; (wrappedError as any).response = response  // 保留response对象
    ; (wrappedError as any).config = config      // 保留config对象
    return Promise.reject(wrappedError)
  }
)

export default instance
