<script setup lang="ts">
import {
  ref,
  shallowRef,
  defineAsyncComponent,
  watch,
  onMounted,
  reactive,
  onUnmounted,
  computed,
  provide,
} from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { MenuUnfoldOutlined, MenuFoldOutlined } from '@ant-design/icons-vue'
import { ConfigProvider, Modal } from 'ant-design-vue'
import { logout } from '@/utils/auth'
import iconDataImport from '@/assets/sider/数据导入.svg'
import iconDataPreprocess from '@/assets/sider/数据预处理.svg'
import iconModelManage from '@/assets/sider/模型管理.svg'
import iconModelAdd from '@/assets/sider/新增模型.svg'
import iconModelTrain from '@/assets/sider/模型训练.svg'
import iconModelTest from '@/assets/sider/模型测试.svg'
import iconModelPredict from '@/assets/sider/模型预测.svg'
import iconFormulaMapping from '@/assets/sider/智能公式映射.svg'

const state = reactive({ collapsed: false })
const selectedKeys = ref(['1'])
const headerTitle = ref('公共数据')
const route = useRoute()
const router = useRouter()
const userName = ref(localStorage.getItem('username') || '未登录')
const currentTime = ref('')

// 获取用户角色
const userRole = ref('user')
const isAdmin = computed(() => userRole.value === 'admin')

// 面包屑状态管理
const breadcrumbState = ref({
  basePath: '',
  formulaName: '',
})

// 添加一个状态来通知子组件返回列表
const shouldReturnToList = ref(false)

const breadcrumbList = computed(() => {
  const base = breadcrumbState.value.basePath || headerTitle.value

  if (headerTitle.value === '新增模型') {
    return ['模型管理', '新增模型']
  }

  if (breadcrumbState.value.formulaName) {
    return [base, `${breadcrumbState.value.formulaName}`]
  }

  return [base]
})

// 更新面包屑状态
const updateBreadcrumb = (basePath: string, formulaName?: string) => {
  breadcrumbState.value.basePath = basePath
  breadcrumbState.value.formulaName = formulaName || ''
}

// 暴露给子组件的方法
const setFormulaBreadcrumb = (formulaName: string) => {
  updateBreadcrumb('智能公式映射', formulaName)
}

// 返回公式列表的方法
const backToFormulaList = () => {
  updateBreadcrumb('智能公式映射')
  // 通知子组件返回列表
  shouldReturnToList.value = true
  // 重置状态
  setTimeout(() => {
    shouldReturnToList.value = false
  }, 100)
}

// 通过provide提供面包屑更新方法和返回列表方法
provide('setFormulaBreadcrumb', setFormulaBreadcrumb)
provide('backToFormulaList', backToFormulaList)
provide('shouldReturnToList', shouldReturnToList)

// 基础菜单列表
const baseMenuList = [
  { key: '1', title: '公共数据', icon: iconDataImport, path: 'dataimport' },
  { key: '2', title: '数据预处理', icon: iconDataPreprocess, path: 'datapreprocess' },
  { key: '4', title: '新增模型', icon: iconModelAdd, path: 'modeladd' },
  { key: '3', title: '模型管理', icon: iconModelManage, path: 'modelmanage' },
  // { key: '5', title: '模型训练', icon: iconModelTrain, path: 'modeltrain' },
  // { key: '6', title: '模型测试', icon: iconModelTest, path: 'modeltest' },
  { key: '7', title: '模型预测', icon: iconModelPredict, path: 'modelpredict' },
  { key: '8', title: '智能公式映射', icon: iconFormulaMapping, path: 'formulamapping' },
]

// 管理员菜单项
const adminMenuList = [
  { key: '9', title: '用户管理', icon: iconModelManage, path: 'usermanage', adminOnly: true },
]

// 根据用户角色动态生成菜单列表
const menuList = computed(() => {
  if (isAdmin.value) {
    return [...baseMenuList, ...adminMenuList]
  }
  return baseMenuList
})

const componentMap: Record<string, ReturnType<typeof defineAsyncComponent>> = {
  dataimport: defineAsyncComponent(() => import('../views/dataImportView/DataImportView.vue')),
  datapreprocess: defineAsyncComponent(
    () => import('../views/dataPreprocessView/DataPreprocessView.vue')
  ),
  modelmanage: defineAsyncComponent(() => import('../views/modelManageView/ModelManageView.vue')),
  modeladd: defineAsyncComponent(() => import('../views/modelAddView/ModelAddView.vue')),
  modeltrain: defineAsyncComponent(() => import('../views/modelTrainView/ModelTrainView.vue')),
  modeltest: defineAsyncComponent(() => import('../views/modelTestView/ModelTestView.vue')),
  modelpredict: defineAsyncComponent(
    () => import('../views/modelPredictView/ModelPredictView.vue')
  ),
  formulamapping: defineAsyncComponent(
    () => import('../views/formulaMappingView/FormulaMappingView.vue')
  ),
  usermanage: defineAsyncComponent(
    () => import('../views/userManageView/UserManageView.vue')
  ),
}

const currentComponent = shallowRef(componentMap['dataimport'])

function handleMenuSelect({ key }: { key: string }) {
  const menu = menuList.value.find((item) => item.key === key)
  if (menu) {
    selectedKeys.value = [key]
    headerTitle.value = menu.title
    currentComponent.value = componentMap[menu.path]
    router.replace(`/home/${menu.path}`)

    // 重置面包屑状态
    if (menu.path === 'formulamapping') {
      updateBreadcrumb('智能公式映射')
    } else {
      updateBreadcrumb(menu.title)
    }
  }
}

function syncByRoute() {
  // 取子路径
  const sub = route.path.split('/')[2] || 'dataimport'

  const menu = menuList.value.find((item) => item.path === sub) || menuList.value[0]
  selectedKeys.value = [menu.key]
  headerTitle.value = menu.title
  currentComponent.value = componentMap[menu.path]

  // 同步面包屑状态
  if (menu.path === 'formulamapping') {
    updateBreadcrumb('智能公式映射')
  } else {
    updateBreadcrumb(menu.title)
  }
}

watch(() => route.path, syncByRoute, { immediate: true })

function updateTime() {
  const now = new Date()
  const pad = (n: number) => n.toString().padStart(2, '0')
  currentTime.value = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())} ${pad(
    now.getHours()
  )}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`
}

let timer: number
onMounted(() => {
  updateTime()
  timer = setInterval(updateTime, 1000)
  
  // 从localStorage加载用户角色
  const userInfo = localStorage.getItem('userInfo')
  if (userInfo) {
    try {
      const parsed = JSON.parse(userInfo)
      userRole.value = parsed.role || 'user'
    } catch (e) {
      console.error('解析用户信息失败', e)
    }
  }
  
  // 进入/home时自动跳转到/home/dataimport
  if (route.path === '/home') {
    router.replace('/home/dataimport')
  }
})
onUnmounted(() => {
  clearInterval(timer)
})

// 暴露方法给子组件
defineExpose({
  setFormulaBreadcrumb,
})

function handleBreadcrumbClick(item: string, index: number) {
  if (index === 0) {
    // 点击第一个面包屑项（基础路径）
    if (headerTitle.value === '智能公式映射') {
      // 如果在智能公式映射页面，清除公式名称并返回公式列表
      backToFormulaList()
    } else {
      // 其他页面，跳转到对应的主页面
      const menu = menuList.value.find((menu) => menu.title === item)
      if (menu) {
        router.push(`/home/${menu.path}`)
        updateBreadcrumb(menu.title)
      }
    }
  } else if (index === 1 && headerTitle.value === '新增模型') {
    // 点击新增模型，跳转到新增模型页面
    router.push('/home/modeladd')
    updateBreadcrumb('新增模型')
  } else if (index === 1 && breadcrumbState.value.formulaName) {
    // 点击公式名称，清除公式名称（相当于返回列表）
    backToFormulaList()
  }
}

function isClickableBreadcrumb(item: string, index: number) {
  // 第一个面包屑项总是可点击的
  if (index === 0) return true

  // 第二个面包屑项在特定情况下可点击
  if (index === 1) {
    if (headerTitle.value === '新增模型') return true
    if (breadcrumbState.value.formulaName) return true
  }

  return false
}

// 退出登录
function handleLogout() {
  Modal.confirm({
    title: '确认退出',
    content: '确定要退出登录吗？',
    okText: '确定',
    cancelText: '取消',
    onOk: () => {
      logout()
      localStorage.removeItem('username')
      localStorage.removeItem('userInfo')
      router.push('/')
    },
  })
}
</script>

<template>
  <a-layout style="height: 100vh; overflow: hidden">
    <a-layout-sider
      :collapsed="state.collapsed"
      :width="200"
      :collapsible="false"
      :style="{ height: '100vh', position: 'fixed', left: '0', top: '0', zIndex: 100 }"
    >
      <div
        style="
          height: 56px;
          padding: 8px;
          background: transparent;
          text-align: center;
          display: flex;
          align-items: center;
          justify-content: center;
        "
      >
        <img
          src="@/assets/login/logo.svg"
          alt="logo"
          style="height: 56px; max-width: 100%; object-fit: contain; background: transparent"
        />
      </div>
      <ConfigProvider
        :theme="{
          components: {
            Menu: {
              itemBorderRadius: 6,
              subMenuItemBorderRadius: 6,
              itemMarginInline: 8,
              itemMarginBlock: 4
            }
          },
          token: {
            colorPrimary: '#1a4d8f',
            borderRadius: 6
          }
        }"
      >
        <a-menu
          theme="dark"
          mode="inline"
          v-model:selectedKeys="selectedKeys"
          @select="handleMenuSelect"
        >
          <a-menu-item v-for="item in menuList" :key="item.key">
            <template #icon>
              <img :src="item.icon" style="width: 18px; height: 18px" />
            </template>
            {{ item.title }}
          </a-menu-item>
        </a-menu>
      </ConfigProvider>
      <div
        style="
          position: absolute;
          right: 0;
          bottom: 0;
          width: 100%;
          display: flex;
          justify-content: flex-end;
          align-items: center;
          padding: 12px 12px 12px 0;
          background: transparent;
          z-index: 10;
        "
      >
        <span
          style="font-size: 20px; cursor: pointer; color: #c3cdd9"
          @click="state.collapsed = !state.collapsed"
        >
          <MenuUnfoldOutlined v-if="state.collapsed" />
          <MenuFoldOutlined v-else />
        </span>
      </div>
    </a-layout-sider>
    <a-layout
      :style="{
        marginLeft: state.collapsed ? '80px' : '200px',
        height: '100vh',
        display: 'flex',
        flexDirection: 'column',
      }"
    >
      <a-layout-header
        style="
          background: var(--bg-primary);
          padding: 0 20px;
          height: 60px;
          line-height: 60px;
          display: flex;
          align-items: center;
          justify-content: space-between;
          flex-shrink: 0;
          border-bottom: 1px solid var(--border-color);
          box-shadow: var(--shadow-xs);
        "
      >
        <a-breadcrumb separator="\" style="font-size: 14px">
          <a-breadcrumb-item
            v-for="(item, idx) in breadcrumbList"
            :key="idx"
            @click="handleBreadcrumbClick(item, idx)"
            :class="{ 'clickable-breadcrumb': isClickableBreadcrumb(item, idx) }"
          >
            {{ item }}
          </a-breadcrumb-item>
        </a-breadcrumb>
        <div class="header-info">
          <span class="header-time">{{ currentTime }}</span>
          <span class="header-divider"></span>
          <span class="header-username">{{ userName }}</span>
          <span class="header-divider"></span>
          <a-button type="link" size="small" @click="handleLogout" class="logout-btn">
            退出登录
          </a-button>
        </div>
      </a-layout-header>
      <a-layout-content style="flex: 1; overflow-y: auto; overflow-x: hidden">
        <keep-alive>
          <component :is="currentComponent" />
        </keep-alive>
      </a-layout-content>
    </a-layout>
  </a-layout>
</template>
<style scoped>
.header-title-text {
  color: #c3cdd9;
  font-size: 10x;
  display: inline-block;
  width: 70px;
  height: 24px;
  line-height: 24px;
  gap: 4px;
  vertical-align: middle;
}
.home-content {
  display: flex;
  flex-direction: row;
  gap: 16px;
}
.tree-content {
  width: 320px;
  height: 100%;
  background: #9d4444;
  border: 1px solid#14447f;
}
.right-content {
  flex: 1;
  height: 100%;
  background: #2d2f30;
}
.header-info {
  display: flex;
  align-items: center;
  gap: 16px;
}
.header-time {
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 500;
}
.header-divider {
  width: 1px;
  height: 20px;
  background: var(--border-color);
  margin: 0 var(--spacing-lg);
  display: inline-block;
}
.header-username {
  color: var(--text-primary);
  font-weight: 600;
  font-size: 15px;
}

.logout-btn {
  color: #ff4d4f !important;
  font-size: 14px;
  padding: 0 8px;
}

.logout-btn:hover {
  color: #ff7875 !important;
}

/* 可点击面包屑样式 */
.clickable-breadcrumb {
  cursor: pointer;
  color: var(--primary-color);
  transition: var(--transition-base);
  font-weight: 500;
}

.clickable-breadcrumb:hover {
  color: var(--primary-light);
  text-decoration: underline;
}
</style>
