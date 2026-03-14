import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import HomeView from '../views/HomeView.vue'
import { logout } from '@/utils/auth'
const RegisterView = () => import('../views/RegisterView.vue')
const UserManageView = () => import('../views/userManageView/UserManageView.vue')
const DataImportView = () => import('../views/dataImportView/DataImportView.vue')
const DataPreprocessView = () => import('../views/dataPreprocessView/DataPreprocessView.vue')
const ModelManageView = () => import('../views/modelManageView/ModelManageView.vue')
const ModelAddView = () => import('../views/modelAddView/ModelAddView.vue')
const ModelTrainView = () => import('../views/modelTrainView/ModelTrainView.vue')
const ModelTestView = () => import('../views/modelTestView/ModelTestView.vue')
const ModelPredictView = () => import('../views/modelPredictView/ModelPredictView.vue')
const FormulaMappingView = () => import('../views/formulaMappingView/FormulaMappingView.vue')

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'login',
      component: LoginView,
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView,
    },
    {
      path: '/user-manage',
      name: 'user-manage',
      component: UserManageView,
    },
    {
      path: '/home',
      name: 'home',
      component: HomeView,
      children: [
        {
          path: ':subpath',
          component: HomeView,
        },
      ],
    },
    // { path: '/data-import', name: 'data-import', component: DataImportView, meta: { keepAlive: true } },
    // { path: '/data-preprocess', name: 'data-preprocess', component: DataPreprocessView, meta: { keepAlive: true } },
    // { path: '/model-manage', name: 'model-manage', component: ModelManageView, meta: { keepAlive: true } },
    // { path: '/model-add', name: 'model-add', component: ModelAddView, meta: { keepAlive: true } },
    // { path: '/model-train', name: 'model-train', component: ModelTrainView, meta: { keepAlive: true } },
    // { path: '/model-test', name: 'model-test', component: ModelTestView, meta: { keepAlive: true } },
    // { path: '/model-predict', name: 'model-predict', component: ModelPredictView, meta: { keepAlive: true } },
    // { path: '/formula-mapping', name: 'formula-mapping', component: FormulaMappingView, meta: { keepAlive: true } },
     { path: '/data-import', name: 'data-import', component: DataImportView },
    { path: '/data-preprocess', name: 'data-preprocess', component: DataPreprocessView },
    { path: '/model-manage', name: 'model-manage', component: ModelManageView },
    { path: '/model-add', name: 'model-add', component: ModelAddView },
    { path: '/model-train', name: 'model-train', component: ModelTrainView },
    { path: '/model-test', name: 'model-test', component: ModelTestView },
    { path: '/model-predict', name: 'model-predict', component: ModelPredictView },
    { path: '/formula-mapping', name: 'formula-mapping', component: FormulaMappingView },
  ],
})

router.beforeEach((to, from, next) => {
  if (to.path === '/') {
    next()
    return
  }

  const baseTime = new Date('2026-01-05T12:00:00')
  const currentTime = new Date()
  const timeDiff = currentTime.getTime() - baseTime.getTime()
  const ninetyDays = 90 * 24 * 60 * 60 * 1000

  if (timeDiff > ninetyDays) {
    logout()
    localStorage.removeItem('username')
    next('/')
  } else {
    next()
  }
})

export default router
