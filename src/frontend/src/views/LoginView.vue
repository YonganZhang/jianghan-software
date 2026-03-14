<template>
  <div class="login-bg">
    <!-- 顶部logo栏 -->
    <div class="login-header">
      <img src="@/assets/login/logo.svg" class="header-logo" alt="logo" />
    </div>
    <!-- 主体内容：左右两栏 -->
    <div class="login-content">
      <div class="login-graphics">
        <div class="model-row">
          <img
            src="@/assets/login/model1.svg"
            class="model-img"
            :style="{ height: modelImgHeight }"
          />
          <img
            src="@/assets/login/model2.svg"
            class="model-img"
            :style="{ height: modelImgHeight }"
          />
          <img
            src="@/assets/login/model3.svg"
            class="model-img"
            :style="{ height: modelImgHeight }"
          />
        </div>
        <img src="@/assets/login/desk.svg" class="desk-img" />
      </div>
      <div class="login-card-figma" ref="loginCardRef">
        <div class="login-title-figma">中石化模型预测系统</div>
        <div class="login-subtitle-figma">欢迎使用中石化模型预测系统，请输入账号密码登录</div>
        <div class="login-divider-figma"></div>
        <a-form
          :model="form"
          :rules="rules"
          ref="formRef"
          class="login-form-figma"
          @submit.prevent="onSubmit"
        >
          <a-form-item name="username">
            <div class="input-label-figma">账号</div>
            <a-input
              v-model:value="form.username"
              size="large"
              placeholder="请输入账号"
              class="figma-input"
            />
          </a-form-item>
          <a-form-item name="password">
            <div class="input-label-figma">密码</div>
            <a-input-password
              v-model:value="form.password"
              size="large"
              placeholder="请输入密码"
              class="figma-input"
            />
          </a-form-item>
          <a-form-item>
            <a-button
              type="primary"
              html-type="submit"
              size="large"
              block
              :loading="loading"
              :disabled="!serverReady"
              class="figma-login-btn"
            >
              {{ serverReady ? '登 录' : '正在连接服务器...' }}
            </a-button>
          </a-form-item>
          <a-form-item>
            <div class="register-link">
              还没有账号？<a @click="goToRegister">立即注册</a>
            </div>
          </a-form-item>
        </a-form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick, onUnmounted } from 'vue'
import { message } from 'ant-design-vue'
import { useRouter } from 'vue-router'
import { loginApi, healthCheckApi } from '@/utils/api'
import { setToken } from '@/utils/auth'

const router = useRouter()
const formRef = ref()
const loading = ref(false)
const serverReady = ref(false) // 服务器是否就绪
let healthCheckTimer: ReturnType<typeof setInterval> | null = null

const form = reactive({
  username: '',
  password: '',
})

const rules = {
  username: [
    { required: true, type: 'string', message: '请输入账号', trigger: ['blur', 'change'] },
  ],
  password: [
    { required: true, type: 'string', message: '请输入密码', trigger: ['blur', 'change'] },
  ],
}

const onSubmit = async () => {
  loading.value = true
  console.log('form:', form.username, form.password)
  try {
    const res = await loginApi({
      username: form.username,
      password: form.password,
    })
    console.log('登录：', res)
    if (res?.data) {
      setToken(res.data.token)
      // 保存用户信息到localStorage
      if (res.data.userInfo) {
        localStorage.setItem('userInfo', JSON.stringify(res.data.userInfo))
      }
      message.success(res.data.msg || '登陆成功')
      localStorage.setItem('username', form.username)
      router.push('/home')
    } else {
      message.error('登录请求失败，请检查网络或联系管理员')
    }
  } catch (err: any) {
    console.error('登录出错：', err)
    // 仅在无响应（网络断开等）时弹提示，有响应的错误已由 axios 拦截器处理
    if (!err?.response) {
      message.error('服务器异常，请稍后再试')
    }
  } finally {
    loading.value = false
  }
}

const goToRegister = () => {
  router.push('/register')
}

// 新增：动态设置model图片高度为登录框高度一半
const loginCardRef = ref<HTMLElement | null>(null)
const modelImgHeight = ref('100px')

const setModelImgHeight = () => {
  if (loginCardRef.value) {
    const cardHeight = loginCardRef.value.offsetHeight
    modelImgHeight.value = cardHeight / 2 + 'px'
  }
}

// 检查服务器是否就绪
const checkServerHealth = async () => {
  try {
    await healthCheckApi()
    serverReady.value = true
    // 服务已就绪，停止轮询
    if (healthCheckTimer) {
      clearInterval(healthCheckTimer)
      healthCheckTimer = null
    }
    console.log('后端服务已就绪')
  } catch (err) {
    serverReady.value = false
    console.log('等待后端服务启动...')
  }
}

onMounted(() => {
  nextTick(() => {
    setModelImgHeight()
    window.addEventListener('resize', setModelImgHeight)
  })
  // 启动后端健康检查轮询
  checkServerHealth() // 立即检查一次
  healthCheckTimer = setInterval(checkServerHealth, 1500) // 每1.5秒检查一次
})

onUnmounted(() => {
  window.removeEventListener('resize', setModelImgHeight)
  // 清理健康检查定时器
  if (healthCheckTimer) {
    clearInterval(healthCheckTimer)
    healthCheckTimer = null
  }
})
</script>

<style scoped>
.login-bg {
  min-height: 100vh;
  width: 100vw;
  background: linear-gradient(
    to bottom,
    #175ca6 90px,
    #f5f5f5 90px,
    #f5f5f5 25%,
    rgba(131, 103, 40, 0.6) 25%,
    rgba(29, 23, 9, 0.6) 50%,
    #f5f5f5 50%,
    #666666 100%
  );
  display: flex;
  flex-direction: column;
}

.login-header {
  width: 100vw;
  height: 90px;
  background: #175ca6;
  display: flex;
  align-items: center;
  padding-left: 40px;
  position: relative;
  z-index: 10;
}

.login-content {
  flex: 1;
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;
  width: 100%;
  min-height: 0;
  padding: 0 2vw;
  box-sizing: border-box;
}

.login-graphics {
  flex: 1 1 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-width: 240px;
  max-width: 40vw;
}

.model-row {
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: flex-end;
  gap: 2vw;
  margin-bottom: 2vh;
}

.model-img {
  width: auto;
  max-width: 140px;
  min-width: 80px;
  /* 高度由JS动态控制 */
}

.desk-img {
  width: 30vw;
  max-width: 320px;
  min-width: 160px;
  height: auto;
  margin-top: 2vh;
}

.login-card-figma {
  flex: 0 0 28vw;
  max-width: 450px;
  min-width: 300px;
  background: #2d2f30f2;
  border-radius: 10px;
  box-shadow: 0px 0px 14px 0px #000000b2;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding: 3vw 2vw 2vw 2vw;
  z-index: 1000;
  gap: 24px;
  margin-left: 4vw;
}

.login-title-figma,
.login-subtitle-figma,
.login-divider-figma,
.login-form-figma {
  margin-bottom: 0 !important;
}

.login-form-figma {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.a-form-item {
  margin-bottom: 0 !important;
}

.login-divider-figma {
  height: 1px;
  background-color: #a3a3a3; /* 线条颜色（可改为 #ccc、#333 等） */
  width: 100%; /* 撑满父容器 */
}

.login-logo {
  width: 72px;
  height: 72px;
  margin-bottom: 16px;
}

.login-title-figma {
  font-family: Source Han Sans CN;
  font-weight: 700;
  font-size: 25px;
  line-height: 100%;
  letter-spacing: 0%;
  color: #fbfafa;
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 8px;
  text-align: center;
  letter-spacing: 2px;
}

.login-subtitle-figma {
  font-family: Source Han Sans CN;
  font-weight: 300;
  font-size: 14px;
  line-height: 100%;
  letter-spacing: 0%;
  color: #b0b0b0;
  font-size: 14px;
  margin-bottom: 32px;
  text-align: center;
}

.login-form-figma {
  width: 100%;
}

.figma-input {
  background: #414344 !important;
  border: 1px solid #414344 !important;
  color: #fff !important;
  border-radius: 0px !important;
}

.figma-input::placeholder {
  color: #b0b0b0 !important;
}

.figma-login-btn {
  background: linear-gradient(180deg, #3f9bfd 0%, #28629f 100%) !important;
  border-radius: 0px !important;
  font-weight: bold !important;
  height: 48px !important;
  font-size: 16px !important;
  border: none !important;
  color: #fff !important;
  box-shadow: 0 2px 8px 0 rgba(22, 119, 255, 0.15) !important;
  transition: background 0.3s;
}

.figma-login-btn:hover {
  background: linear-gradient(90deg, #4096ff 0%, #69b1ff 100%) !important;
}

.input-label-figma {
  font-family: Source Han Sans CN;
  font-weight: 300;
  font-size: 14px;
  line-height: 100%;
  letter-spacing: 0%;
  color: #f6f6f6;
  margin-bottom: 6px;
}

.register-link {
  text-align: center;
  width: 100%;
  color: #b0b0b0;
  font-size: 14px;
}

.register-link a {
  color: #3f9bfd;
  cursor: pointer;
  text-decoration: none;
}

.register-link a:hover {
  color: #69b1ff;
  text-decoration: underline;
}

:deep(.ant-input.ant-input-lg) {
  background: #414344;
  color: #fff !important;
}
:deep(.ant-input.ant-input-lg)::placeholder {
  color: #b0b0b0 !important;
}

@media (max-width: 900px) {
  .login-content {
    flex-direction: column;
    align-items: center;
    padding: 0 1vw;
  }
  .login-graphics {
    max-width: 100vw;
    flex-direction: row;
    justify-content: center;
    min-width: 0;
    margin-bottom: 2vh;
  }
  .model-img,
  .desk-img {
    width: 18vw;
    max-width: 100px;
    min-width: 60px;
    margin: 0 1vw;
  }
  .desk-img {
    width: 24vw;
    max-width: 180px;
    min-width: 80px;
  }
  .login-card-figma {
    margin-left: 0;
    width: 90vw;
    max-width: 400px;
    min-width: 220px;
  }
}
</style>
