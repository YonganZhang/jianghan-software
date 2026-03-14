import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import Antd from 'ant-design-vue'
import 'ant-design-vue/dist/reset.css'
import './assets/angle.css'
import zhCN from 'ant-design-vue/es/locale/zh_CN'
import { ConfigProvider } from 'ant-design-vue'
import store from './store'

const app = createApp(App)
app.use(router)
app.use(Antd)
app.use(ConfigProvider)
app.use(store)
app.mount('#app')
