<template>
  <div class="user-manage-container">
    <div class="header">
      <h2>用户管理</h2>
    </div>
    
    <div class="table-container">
      <a-table
        :columns="columns"
        :data-source="userList"
        :loading="loading"
        :pagination="pagination"
        @change="handleTableChange"
        row-key="id"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'role'">
            <a-tag :color="record.role === 'admin' ? 'red' : 'blue'">
              {{ record.role === 'admin' ? '管理员' : '普通用户' }}
            </a-tag>
          </template>
          <template v-else-if="column.key === 'created_at'">
            {{ formatDate(record.created_at) }}
          </template>
          <template v-else-if="column.key === 'last_login'">
            {{ record.last_login ? formatDate(record.last_login) : '从未登录' }}
          </template>
          <template v-else-if="column.key === 'action'">
            <a-space>
              <a-button type="link" size="small" @click="handleEdit(record)">编辑</a-button>
              <a-button type="link" size="small" @click="handleResetPassword(record)">重置密码</a-button>
              <a-button 
                type="link" 
                size="small" 
                danger 
                @click="handleDelete(record)"
                :disabled="record.role === 'admin' || record.id === currentUserId"
              >
                删除
              </a-button>
            </a-space>
          </template>
        </template>
      </a-table>
    </div>

    <!-- 编辑用户对话框 -->
    <a-modal
      v-model:open="editModalVisible"
      title="编辑用户信息"
      @ok="handleEditSubmit"
      @cancel="handleEditCancel"
    >
      <a-form :model="editForm" :label-col="{ span: 6 }" :wrapper-col="{ span: 16 }">
        <a-form-item label="用户名">
          <a-input v-model:value="editForm.username" placeholder="请输入用户名" />
        </a-form-item>
        <a-form-item label="邮箱">
          <a-input v-model:value="editForm.email" placeholder="请输入邮箱" />
        </a-form-item>
        <a-form-item label="角色" v-if="editForm.role !== 'admin' || currentUserId !== editForm.id">
          <a-select v-model:value="editForm.role">
            <a-select-option value="user">普通用户</a-select-option>
            <a-select-option value="admin">管理员</a-select-option>
          </a-select>
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 重置密码对话框 -->
    <a-modal
      v-model:open="resetPasswordModalVisible"
      title="重置用户密码"
      @ok="handleResetPasswordSubmit"
      @cancel="handleResetPasswordCancel"
    >
      <a-form :model="resetPasswordForm" :label-col="{ span: 6 }" :wrapper-col="{ span: 16 }">
        <a-form-item label="新密码">
          <a-input-password v-model:value="resetPasswordForm.password" placeholder="请输入新密码" />
        </a-form-item>
        <a-form-item label="确认密码">
          <a-input-password v-model:value="resetPasswordForm.confirmPassword" placeholder="请再次输入新密码" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { message, Modal } from 'ant-design-vue'
import { getUserListApi, deleteUserApi, updateUserApi, resetPasswordApi } from '@/utils/api'

interface User {
  id: number
  username: string
  email: string
  role: string
  created_at: string
  last_login: string | null
}

const loading = ref(false)
const userList = ref<User[]>([])
const currentUserId = ref<number | null>(null)

const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0,
  showSizeChanger: true,
  showTotal: (total: number) => `共 ${total} 条`,
})

const columns = [
  {
    title: 'ID',
    dataIndex: 'id',
    key: 'id',
    width: 80,
  },
  {
    title: '用户名',
    dataIndex: 'username',
    key: 'username',
  },
  {
    title: '邮箱',
    dataIndex: 'email',
    key: 'email',
  },
  {
    title: '角色',
    dataIndex: 'role',
    key: 'role',
    width: 120,
  },
  {
    title: '注册时间',
    dataIndex: 'created_at',
    key: 'created_at',
    width: 180,
  },
  {
    title: '最后登录',
    dataIndex: 'last_login',
    key: 'last_login',
    width: 180,
  },
  {
    title: '操作',
    key: 'action',
    width: 250,
  },
]

// 编辑用户
const editModalVisible = ref(false)
const editForm = reactive({
  id: 0,
  username: '',
  email: '',
  role: 'user',
})

// 重置密码
const resetPasswordModalVisible = ref(false)
const resetPasswordForm = reactive({
  userId: 0,
  password: '',
  confirmPassword: '',
})

const fetchUserList = async () => {
  loading.value = true
  try {
    const res = await getUserListApi({
      page: pagination.current,
      pageSize: pagination.pageSize,
    })
    console.log('用户列表：', res)
    if (res?.code === '00000') {
      userList.value = res.data.users
      pagination.total = res.data.total
    } else {
      message.error(res?.message || '获取用户列表失败')
    }
  } catch (err: any) {
    console.error('获取用户列表出错：', err)
    if (err.response?.data?.error) {
      message.error(err.response.data.error)
    } else if (err.message) {
      message.error(err.message)
    } else {
      message.error('获取用户列表失败')
    }
  } finally {
    loading.value = false
  }
}

const handleTableChange = (pag: any) => {
  pagination.current = pag.current
  pagination.pageSize = pag.pageSize
  fetchUserList()
}

const handleEdit = (record: User) => {
  editForm.id = record.id
  editForm.username = record.username
  editForm.email = record.email
  editForm.role = record.role
  editModalVisible.value = true
}

const handleEditSubmit = async () => {
  try {
    const res = await updateUserApi(editForm.id, {
      username: editForm.username,
      email: editForm.email,
      role: editForm.role,
    })
    if (res?.code === '00000') {
      message.success('修改用户信息成功')
      editModalVisible.value = false
      fetchUserList()
    } else {
      message.error(res?.message || '修改用户信息失败')
    }
  } catch (err: any) {
    console.error('修改用户信息出错：', err)
    if (err.response?.data?.error) {
      message.error(err.response.data.error)
    } else if (err.message) {
      message.error(err.message)
    } else {
      message.error('修改用户信息失败')
    }
  }
}

const handleEditCancel = () => {
  editModalVisible.value = false
}

const handleResetPassword = (record: User) => {
  resetPasswordForm.userId = record.id
  resetPasswordForm.password = ''
  resetPasswordForm.confirmPassword = ''
  resetPasswordModalVisible.value = true
}

const handleResetPasswordSubmit = async () => {
  if (!resetPasswordForm.password) {
    message.error('请输入新密码')
    return
  }
  if (resetPasswordForm.password !== resetPasswordForm.confirmPassword) {
    message.error('两次输入的密码不一致')
    return
  }
  try {
    const res = await resetPasswordApi(resetPasswordForm.userId, resetPasswordForm.password)
    if (res?.code === '00000') {
      message.success('重置密码成功')
      resetPasswordModalVisible.value = false
    } else {
      message.error(res?.message || '重置密码失败')
    }
  } catch (err: any) {
    console.error('重置密码出错：', err)
    if (err.response?.data?.error) {
      message.error(err.response.data.error)
    } else if (err.message) {
      message.error(err.message)
    } else {
      message.error('重置密码失败')
    }
  }
}

const handleResetPasswordCancel = () => {
  resetPasswordModalVisible.value = false
}

const handleDelete = (record: User) => {
  if (record.role === 'admin') {
    message.warning('不能删除管理员账号')
    return
  }
  if (currentUserId.value != null && record.id === currentUserId.value) {
    message.warning('不能删除当前登录的管理员账号')
    return
  }
  
  // 使用 Modal.confirm 进行确认
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除用户 "${record.username}" 吗？此操作不可恢复，将同时删除该用户的所有数据（目录、文件、配置等）。`,
    okText: '确定',
    okType: 'danger',
    cancelText: '取消',
    onOk: async () => {
      try {
        console.log('正在删除用户:', record.id, record.username)
        const res = await deleteUserApi(record.id)
        console.log('删除用户响应:', res)
        
        if (res?.code === '00000') {
          message.success('删除用户成功')
          fetchUserList()
        } else {
          const errorMsg = res?.message || res?.error || '删除用户失败'
          console.error('删除失败:', errorMsg)
          message.error(errorMsg)
        }
      } catch (err: any) {
        console.error('删除用户出错：', err)
        let errorMsg = '删除用户失败'
        
        if (err.response?.data?.error) {
          errorMsg = err.response.data.error
        } else if (err.response?.data?.message) {
          errorMsg = err.response.data.message
        } else if (err.message) {
          errorMsg = err.message
        }
        
        console.error('错误详情:', errorMsg)
        message.error(errorMsg, 5) // 显示5秒
      }
    },
  })
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

onMounted(() => {
  // 获取当前用户ID（从localStorage或其他地方）
  const userInfo = localStorage.getItem('userInfo')
  if (userInfo) {
    try {
      const parsed = JSON.parse(userInfo)
      currentUserId.value = parsed.id
    } catch (e) {
      console.error('解析用户信息失败', e)
    }
  }
  fetchUserList()
})
</script>

<style scoped>
.user-manage-container {
  padding: 24px;
  background: #fff;
  min-height: 100vh;
}

.header {
  margin-bottom: 24px;
}

.header h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.table-container {
  background: #fff;
  border-radius: 8px;
}
</style>
