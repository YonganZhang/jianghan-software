import instance from './axios'
import type { AxiosRequestConfig } from 'axios'

// 登录
export function loginApi(data: { username: string; password: string }) {
  return instance.post('/login', data)
}

// 健康检查 - 用于确认后端服务是否就绪
export function healthCheckApi() {
  return instance.get('/health', {
    timeout: 2000,  // 短超时，快速检测
    silent: true    // 静默模式：失败时不弹出错误提示
  } as any)
}

// 数据导入
export function getTreeData() {
  return instance.get('/data-import/directory-file/file-structure')
}

export function deleteTreeNode(data: { id: number; type: string }) {
  return instance.post('/data-import/directory-file/delete', data)
}

export function editTreeNode(data: { id: number; name: string; type: string }) {
  return instance.post('/data-import/directory-file/rename', data)
}

/**
 * 上传文件到指定目录
 * @param file 要上传的文件对象（File）
 * @param directoryId 目标文件夹id（number或string）
 * @returns Promise
 */
export function addTreeNode(data: {
  type: 'file' | 'directory'
  name: string
  file?: File
  parent_id: number
}) {
  const formData = new FormData()
  formData.append('type', data.type)
  formData.append('name', data.name)
  formData.append('parent_id', String(data.parent_id))
  if (data.file) formData.append('file', data.file)
  return instance.post('/data-import/directory-file/create', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
}

export function convertAllToXlsx() {
  return instance.post('/data-import/directory-file/convert-all-to-xlsx')
}

export function getDataSource(data: {
  id: number
  name: string
  pageNum: number
  pageSize: number
}) {
  return instance.post('/data-import/directory-file/page', data)
}

// 数据预处理-选择数据
export function getOriginData(data: { key: number }) {
  return instance.post('/pretreatment/process-file', data)
}

export function getEchartsData(
  data: {
    type: string[];
    key: string;
    predict_target?: string;
    scaler_type?: string;
    sequence_length?: number;
    batch_size?: number;
    input_size?: number;
  },
  config?: AxiosRequestConfig
) {
  return instance.post('/pretreatment/process', data, config)
}


// 开始训练-传参
export function parameter(data: object) {
  return instance.post('/train/parameter', data)
}

// 新增模型-开始训练
export function startTrain(data?: { file_ids?: number[] }) {
  return instance.post('/train/start', data ?? {})
}

export function getHardwareStatus() {
  return instance.get('/train/hardware')
}

// 新增模型-中止训练
export function stopTrain() {
  return instance.post('/train/stop')
}

export function getAddSelect() {
  return instance.get('/modelname')
}

// 模型测试结果
export function getModelTestingResult(data: { file_id: number }) {
  return instance.post('/getfile', data)
}

export function getTestOutputResult(data: {
  dir_id?: number
  file_ids?: number[]
  idm: number
  file_id: number
  predict_mode: boolean
  type: string
}) {
  return instance.post('/test', data)
}

// 模型管理
export function getPreprocessModelResults(data: { pageNum: number; pageSize: number }) {
  return instance.post('/model-management/modelmagement_page', data)
}

export function deleteModelResults(data: { id: number; model_type: string }) {
  return instance.post('/model-management/modelmagement_delete', data)
}

export function editModelResults(data: { id: number; model_type: string; modelname: string }) {
  return instance.post('/model-management/modelmagement_modify', data)
}

export function getLossChart(data: { id: number; model_type: string }) {
  return instance.post('/model-management/modelmagement_pictures', data)
}

export function getParameters(data: { id: number; model_type: string }) {
  return instance.post('/model-management/modelmagement_visualization', data)
}

export function getFormulaImage() {
  // 使用静默模式，不在axios拦截器中弹出错误提示（404是正常情况）
  return instance.get('/Reimage', { silent: true } as any)
}

export function getFormulaSpecificImage(data: { id: number }) {
  return instance.post('/Resmart', data)
}

export function getFormulaPageList(data: { pageNum: number; pageSize: number }) {
  return instance.post('/Formulaspage', data)
}

export function deleteFormulaPageList(data: { id: number }) {
  return instance.post('/Deleterecord', data)
}



// 智能公式映射
export function runSmartFormula(data: {}) {
  return instance.post('/run-smart-formula', data)
}

// 获取Excel文件列名
export function getExcelColumns(fileId: number) {
  return instance.get(`/get-excel-columns/${fileId}`)
}

// 中止智能公式拟合
export function stopSmartFormula() {
  return instance.post('/stop-smart-formula')
}

// 查看参数
export function FormulaDetail(data: {}) {
  return instance.post('/FormulaDetail', data)
}

// 用户注册
export function registerApi(data: { username: string; password: string; email: string }) {
  return instance.post('/sign', data)
}

// 获取用户列表（管理员）
export function getUserListApi(params: { page: number; pageSize: number }) {
  return instance.get('/users', { params })
}

// 删除用户（管理员）
export function deleteUserApi(userId: number) {
  return instance.delete(`/users/${userId}`)
}

// 修改用户信息（管理员）
export function updateUserApi(userId: number, data: { username?: string; email?: string; password?: string; role?: string }) {
  return instance.put(`/users/${userId}`, data)
}

// 重置用户密码（管理员）
export function resetPasswordApi(userId: number, password: string) {
  return instance.post(`/users/${userId}/reset-password`, { password })
}
