export const HTTP_STATUS = {
  SUCCESS: 200,
  UNAUTHORIZED: 401, // 未授权或 token 过期
  FORBIDDEN: 403, // 禁止访问
  NOT_FOUND: 404,
  SERVER_ERROR: 500,
  BAD_GATEWAY: 502,
  SERVICE_UNAVAILABLE: 503,
  GATEWAY_TIMEOUT: 504,
}

export const HTTP_ERROR_MSG: Record<number, string> = {
  400: '请求参数错误',
  401: '登录失效，请重新登录',
  403: '没有权限访问资源',
  404: '请求地址不存在',
  408: '请求超时',
  500: '服务器内部错误',
  502: '网关错误',
  503: '服务不可用',
  504: '网关超时',
}
