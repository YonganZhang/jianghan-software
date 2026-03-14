<template>
  <div class="preview-panel">
    <div class="preprocess-select-card">
      <div class="preview-title">
        <span>模型选择</span>
      </div>
      <div class="preprocess-select-content">
        <a-form layout="inline" class="model-select-row" style="width: 100%">
          <a-form-item
            class="select-item"
            style="flex: 1; padding: 0; margin-bottom: 0; border: none"
          >
            <div style="display: flex; align-items: center; width: 100%; gap: 8px">
              <span class="select-label">筛选测试数据：</span>
              <a-tree-select
                v-model:value="selectedData"
                :tree-data="dataOptions"
                :field-names="{ label: 'label', value: 'value', children: 'children' }"
                placeholder="请选择数据"
                allow-clear
                tree-default-expand-all
                style="flex: 1"
                @select="onSelect"
              >
                <template #title="{ label, icon, isFolder }">
                  <span style="display: flex; align-items: center">
                    <img
                      v-if="icon"
                      :src="icon"
                      :width="isFolder ? 18 : 16"
                      :height="isFolder ? 18 : 16"
                      style="margin-right: 8px"
                    />
                    <span>{{ label }}</span>
                  </span>
                </template>
              </a-tree-select>
            </div>
          </a-form-item>
          <a-form-item
            class="select-item"
            style="flex: 1; padding: 0; margin-bottom: 0; border: none"
          >
            <div style="display: flex; align-items: center; width: 100%; gap: 8px">
              <span class="select-label">读取模型权重：</span>
              <a-select
                v-model:value="trainSetTags"
                :options="trainSetOptions"
                placeholder="请选择测试数据"
                allow-clear
                style="flex: 1"
              />
            </div>
          </a-form-item>
          <a-form-item class="button-group" style="display: flex; align-items: center">
            <a-button type="primary" :loading="isTesting" @click="handleLoadModel">
              {{ isTesting ? '模型预测中' : '开始预测' }}
            </a-button>
            <a-button
              @click="handleShowLog"
              :disabled="!isTesting && !logEnabled"
              style="margin-left: 12px"
              >输出日志</a-button
            >
          </a-form-item>
        </a-form>
      </div>
    </div>
    <div class="preprocess-bottom-row">
      <div class="preprocess-half-card left">
        <div class="preview-title">
          <a-form layout="inline" class="model-select-row" style="width: 100%">
            <a-form-item
              class="select-item"
              style="flex: 1; padding: 0; margin-bottom: 0; border: none"
            >
              <div style="display: flex; align-items: center; width: 100%">
                <span class="select-label">测井曲线绘图栏（左侧）：</span>
                <div style="display: flex; align-items: center; flex: 1">
                  <a-select
                    v-model:value="testSetTags"
                    mode="multiple"
                    :options="tagOptions"
                    allow-clear
                    style="
                      flex: 1;
                      border-right: none;
                      border-top-right-radius: 0;
                      border-bottom-right-radius: 0;
                    "
                    @change="onTagChange1"
                  />
                  <div
                    style="
                      display: flex;
                      align-items: center;
                      justify-content: center;
                      width: 32px;
                      height: 32px;
                      border: 1px solid #d9d9d9;
                      border-left: none;
                      border-top-right-radius: 0;
                      border-bottom-right-radius: 0;
                      background: #fff;
                      cursor: pointer;
                      transition: all 0.3s;
                    "
                    @click="handleFeature1IconClick"
                    @mouseenter="handleIconHover"
                    @mouseleave="handleIconLeave"
                  >
                    <svg
                      viewBox="0 0 1024 1024"
                      version="1.1"
                      xmlns="http://www.w3.org/2000/svg"
                      width="16"
                      height="16"
                      style="color: #666"
                    >
                      <path
                        d="M512 64C264.6 64 64 264.6 64 512s200.6 448 448 448 448-200.6 448-448S759.4 64 512 64zm0 820c-205.4 0-372-166.6-372-372s166.6-372 372-372 372 166.6 372 372-166.6 372-372 372z"
                        fill="currentColor"
                      />
                      <path
                        d="M464 688a48 48 0 1 0 96 0 48 48 0 1 0-96 0zm24-112h48c4.4 0 8-3.6 8-8V296c0-4.4-3.6-8-8-8h-48c-4.4 0-8 3.6-8 8v272c0 4.4 3.6 8 8 8z"
                        fill="currentColor"
                      />
                    </svg>
                  </div>
                </div>
              </div>
            </a-form-item>
            <a-form-item
              class="select-item"
              style="flex: 1; padding: 0; margin-bottom: 0; border: none"
            >
              <div style="display: flex; align-items: center; width: 100%">
                <span class="select-label">测井曲线绘图栏（右侧）：</span>
                <div style="display: flex; align-items: center; flex: 1">
                  <a-select
                    v-model:value="testSetTags2"
                    mode="multiple"
                    :options="tagOptions"
                    allow-clear
                    style="
                      flex: 1;
                      border-right: none;
                      border-top-right-radius: 0;
                      border-bottom-right-radius: 0;
                    "
                    @change="onTagChange2"
                  />
                  <div
                    style="
                      display: flex;
                      align-items: center;
                      justify-content: center;
                      width: 32px;
                      height: 32px;
                      border: 1px solid #d9d9d9;
                      border-left: none;
                      border-top-right-radius: 0;
                      border-bottom-right-radius: 0;
                      background: #fff;
                      cursor: pointer;
                      transition: all 0.3s;
                    "
                    @click="handleFeature2IconClick"
                    @mouseenter="handleIconHover"
                    @mouseleave="handleIconLeave"
                  >
                    <svg
                      viewBox="0 0 1024 1024"
                      version="1.1"
                      xmlns="http://www.w3.org/2000/svg"
                      width="16"
                      height="16"
                      style="color: #666"
                    >
                      <path
                        d="M512 64C264.6 64 64 264.6 64 512s200.6 448 448 448 448-200.6 448-448S759.4 64 512 64zm0 820c-205.4 0-372-166.6-372-372s166.6-372 372-372 372 166.6 372 372-166.6 372-372 372z"
                        fill="currentColor"
                      />
                      <path
                        d="M464 688a48 48 0 1 0 96 0 48 48 0 1 0-96 0zm24-112h48c4.4 0 8-3.6 8-8V296c0-4.4-3.6-8-8-8h-48c-4.4 0-8 3.6-8 8v272c0 4.4 3.6 8 8 8z"
                        fill="currentColor"
                      />
                    </svg>
                  </div>
                </div>
              </div>
            </a-form-item>
          </a-form>
        </div>
        <div
          class="echarts-row"
          v-show="!showCharacter"
          style="display: flex; justify-content: center; align-items: center"
        >
          <a-spin v-show="originLoading" tip="模型测试中..." />
          <a-empty v-show="!originLoading" description="暂无结果，请选择数据"></a-empty>
        </div>
        <div v-show="showCharacter" class="echarts-row">
          <div class="chart-container">
            <div class="chart-label">测井曲线绘图栏（左侧）</div>
            <div ref="chart1Ref" class="echart-half"></div>
          </div>
          <div class="chart-container">
            <div class="chart-label">测井曲线绘图栏（右侧）</div>
            <div ref="chart2Ref" class="echart-half"></div>
          </div>
        </div>
      </div>
      <div class="preprocess-half-card right">
        <div class="preview-title">
          <span>结果展示</span>
          <span class="preview-title-actions">
            <a-button
              type="primary"
              :icon="h(DownloadOutlined)"
              @click="handleExportExcel"
              :disabled="!logEnabled"
              size="small"
            >
              导出Excel
            </a-button>
            <a-button
              type="primary"
              :icon="h(DownloadOutlined)"
              @click="handleExportTxt"
              :disabled="!logEnabled"
              size="small"
            >
              导出TxT
            </a-button>
            <a-button
              type="primary"
              :icon="h(DownloadOutlined)"
              @click="handleExportLas"
              :disabled="!logEnabled"
              size="small"
            >
              导出Las
            </a-button>
          </span>
        </div>
        <div
          class="echarts-row"
          v-show="!enabled"
          style="display: flex; justify-content: center; align-items: center"
        >
          <a-spin v-show="testLoading" tip="模型测试中..." />
          <a-empty v-show="!testLoading" description="暂无结果，请点击开始测试"></a-empty>
        </div>
        <div v-show="enabled" class="echarts-row" style="display: flex; justify-content: center">
          <div ref="chart3Ref" class="echart-all"></div>
        </div>
      </div>
    </div>
    <a-modal
      v-model:open="logModalVisible"
      title="输出日志"
      width="600px"
      :bodyStyle="{ padding: '0', height: '80vh', overflow: 'hidden' }"
    >
      <div class="log-modal-content">
        <div v-for="(log, idx) in logList" :key="idx">{{ log }}</div>
      </div>
      <template #footer>
        <div style="width: 100%; display: flex; justify-content: center">
          <button
            style="
              padding: 6px 32px;
              background: #fff;
              color: #e24a4ad9;
              border: 1px solid #d9d9d9;
              font-size: 14px;
              cursor: pointer;
            "
            @click="cancelTrain"
          >
            取消训练
          </button>
        </div>
      </template>
    </a-modal>
    <!-- <a-modal v-model:open="showMetricModal" title="误差展示表" width="400px" :footer="null">
      <a-table
        :columns="metricTableColumns"
        :data-source="metricTableData"
        :pagination="false"
        bordered
        size="small"
        style="margin-bottom: 24px"
      />
      <div style="width: 100%; display: flex; justify-content: center; gap: 24px">
        <a-button type="primary" :icon="h(DownloadOutlined)" @click="handleExportExcel"
          >导出为Excel</a-button
        >
        <a-button type="primary" :icon="h(DownloadOutlined)" @click="handleExportTxt"
          >导出为TxT</a-button
        >
      </div>
    </a-modal> -->
    <FeatureConfigModal
      v-model:open="showFeature1Modal"
      :tags="testSetTags"
      :indicatorFormModel="indicatorsForm"
      :channelFormModel="channelsForm"
      :bodyHeight="modalHeight"
      @save-indicators="onFeature1SaveIndicators"
      @save-channels="onFeature1SaveChannels"
      @tab-change="(tab) => (activeTab = tab)"
    />

    <!-- 统一特征配置弹窗 - 特征2 -->
    <FeatureConfigModal
      v-model:open="showFeature2Modal"
      :tags="testSetTags2"
      :indicatorFormModel="indicatorsForm2"
      :channelFormModel="channelsForm2"
      :bodyHeight="modalHeight2"
      @save-indicators="onFeature2SaveIndicators"
      @save-channels="onFeature2SaveChannels"
      @tab-change="(tab) => (activeTab2 = tab)"
    />
  </div>
</template>
<script setup lang="ts">
// 可根据需要引入相关逻辑
import { ref, h, onMounted, onUnmounted, nextTick, computed, reactive, watch, onActivated } from 'vue'
import * as echarts from 'echarts'
import { DownloadOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import frameIcon from '@/assets/file/frame.svg'
import excelIcon from '@/assets/file/excel.svg'
import txtIcon from '@/assets/file/txt.svg'
import {
  getAddSelect,
  getTreeData,
  startTrain,
  getModelTestingResult,
  getTestOutputResult,
} from '@/utils/api'
import {
  buildEChartOption,
  initEChart,
  updateEChart,
  disposeEChart,
  getMaxMinRangeForAllCurves,
  getCurveRange,
  colorArray,
  patchTreeKeys,
} from '@/components/echarts/echartsHelper'
import { findNodeByKey } from '@/utils/tree'
import { useStore } from 'vuex'
import { buildCustomOptions } from '@/components/echarts/chartOptionHelper'
import FeatureConfigModal from '@/components/echarts/FeatureConfigModal.vue'

// vuex
const store = useStore()
const testTags = computed(() => store.state.testTags)
const clearRecord = (record: Record<string, any>) => {
  Object.keys(record).forEach((k) => delete record[k])
}
// 日志弹窗相关
const logModalVisible = ref(false)
const logList = ref<string[]>([])
let logTimer: number | null = null

const feature1 = ref<string[]>([])
const feature2 = ref<string[]>([])

const showCharacter = ref(false)
const originLoading = ref(false)
const testLoading = ref(false)
const enabled = ref(false)

type MyTreeNode = {
  title: string
  key: string
  type: string
  id: number
  children?: MyTreeNode[]
}
const treeData = ref<MyTreeNode[]>([])
const dataOptions = computed(() => {
  const res = getOptions(treeData.value)
  console.log('getOptions:', res)
  return res
})
const parentTreeId = ref(0)
const selectedData = ref<number | null>(null)

const trainSetOptions = ref<{ label: string; value: string, type: string }[]>([])
const trainSetTags = ref<string>('')

const maxLenCurve = ref(0)
const testSetTags = ref<string[]>([])
const testSetTags2 = ref<string[]>([])
const tagOptions = ref<{ label: string; value: string }[]>([])
const allData = ref<Record<string, number[][]>>({})
interface IndicatorConfig {
  lineStyle?: string
  color?: string
  range?: [number, number]
}
// 指标属性表单 - 使用customConfig格式
const indicatorsForm = reactive<Record<string, IndicatorConfig>>({})
const indicatorsFormRef = ref()
interface ChannelConfig {
  logarithmicScale?: string
  showScaleLines?: boolean
  thinLine?: string
  thinLineCount?: number
  thickLine?: string
  thickLineCount?: number
  showDepthLines?: boolean
  depthThinLine?: string
  depthInterval?: number
  depthThickLine?: string
  depthThickInterval?: number
}
// 道属性表单数据
const channelsForm = reactive<ChannelConfig>({
  logarithmicScale: 'true', // 对数刻度绘制曲线
  showScaleLines: true, // 显示刻度线
  thinLine: '1', // 细线
  thinLineCount: 10, // 细线份数
  thickLine: '3', // 粗线
  thickLineCount: 2, // 粗线份数
  showDepthLines: true, // 显示深度线
  depthThinLine: '1', // 深度细线
  depthInterval: 1, // 深度间隔
  depthThickLine: '3', // 深度粗线
  depthThickInterval: 10, // 深度粗线间隔
})
const channelsFormRef = ref()
// 特征2的指标属性表单
const indicatorsForm2 = reactive<Record<string, IndicatorConfig>>({})
const indicatorsFormRef2 = ref()
const channelsFormRef2 = ref()
const channelsForm2 = reactive<ChannelConfig>({
  logarithmicScale: 'true', // 对数刻度绘制曲线
  showScaleLines: true, // 显示刻度线
  thinLine: '1', // 细线
  thinLineCount: 10, // 细线份数
  thickLine: '3', // 粗线
  thickLineCount: 2, // 粗线份数
  showDepthLines: true, // 显示深度线
  depthThinLine: '1', // 深度细线
  depthInterval: 1, // 深度间隔
  depthThickLine: '3', // 深度粗线
  depthThickInterval: 10, // 深度粗线间隔
})

const activeTab = ref('indicators')
const activeTab2 = ref('indicators2')
const modalHeight = computed(() => {
  console.log('$$$$$$$$:', activeTab.value)
  if (activeTab.value === 'indicators') {
    // 指标属性：根据testSetTags的数量计算高度
    const rows = testSetTags.value.length // 每行3个
    const baseHeight = 200 // 基础高度（标题、导航、按钮等）
    const rowHeight = 70 // 每行高度
    const totalHeight = baseHeight + rows * rowHeight
    return `${totalHeight}px` // 最大600px
  } else {
    // 道属性：固定高度
    return '700px'
  }
})

const modalHeight2 = computed(() => {
  if (activeTab2.value === 'indicators2') {
    // 指标属性：根据testSetTags2的数量计算高度
    const rows = testSetTags2.value.length // 每行3个
    const baseHeight = 200 // 基础高度（标题、导航、按钮等）
    const rowHeight = 70 // 每行高度
    const totalHeight = baseHeight + rows * rowHeight
    return `${totalHeight}px` // 最大600px
  } else {
    // 道属性：固定高度
    return '700px'
  }
})

// 辅助函数
type Option = {
  id: number
  label: string
  value: string
  icon?: string
  isFolder?: boolean
  children?: Option[]
}
function getOptions(nodes: MyTreeNode[]): Option[] {
  return nodes.map((node) => {
    const option: Option = {
      id: node.id,
      label: node.title,
      value: String(node.key),
    }
    if (node.type === 'directory') {
      option.icon = frameIcon
      option.isFolder = true
      if (node.children && node.children.length > 0) {
        option.children = getOptions(node.children)
      }
    } else if (node.type === 'txt' || node.type === 'las') {
      option.icon = txtIcon
    } else if (node.type === 'xlsx') {
      option.icon = excelIcon
    } else {
      option.icon = frameIcon
    }
    return option
  })
}

const isTesting = ref(false)
const logEnabled = ref(false)
const file_id = ref(0)

onMounted(async () => {
  console.log('ModelPredictView: onMounted started')
  // 获取模型权重下拉列表
  try {
    console.log('Fetching getAddSelect...')
    const selectRes = await getAddSelect()
    console.log('getAddSelect response:', selectRes)
    // Relaxed check: code 200 or 00000, and data existence
    if ((selectRes?.code === 200 || selectRes?.code === '200' || selectRes?.code === '00000') && selectRes.data) {
      let list: any[] = []
      if (Array.isArray(selectRes.data)) {
        list = selectRes.data
      } else if (typeof selectRes.data === 'object') {
         Object.keys(selectRes.data).forEach(key => {
             const group = selectRes.data[key]
             if (Array.isArray(group)) {
                 list.push(...group)
             }
         })
      }
      
      trainSetOptions.value = list.map((item: any) => ({
        label: item.name || item.modelname || `Model ${item.id}`,
        value: item.id + '-' + item.type,
        type: item.type,
      }))
    }
  } catch (e) {
    console.error('getAddSelect error:', e)
  }

  // 获取树形数据
  try {
    console.log('Fetching getTreeData...')
    const treeRes = await getTreeData()
    console.log('getTreeData response:', treeRes)
    // Relaxed check: code 200 or 00000
    if (treeRes?.code === 200 || treeRes?.code === '200' || treeRes?.code === '00000') {
      treeData.value = patchTreeKeys(treeRes.data)
      console.log('treeData updated:', treeData.value)
    }
  } catch (e) {
    console.error('getTreeData error:', e)
  }
})

function handleShowLog() {
  logModalVisible.value = true
}

function updateCharts() {
  nextTick(() => {
    if (chart1Ref.value) {
      if (!chart1Instance) {
        chart1Instance = initEChart(chart1Ref.value, chart1Option.value)
      } else {
        updateEChart(chart1Instance, chart1Option.value)
      }
    }
    if (chart2Ref.value) {
      if (!chart2Instance) {
        chart2Instance = initEChart(chart2Ref.value, chart2Option.value)
      } else {
        updateEChart(chart2Instance, chart2Option.value)
      }
    }
    // 立即resize
    if (chart1Instance) chart1Instance.resize()
    if (chart2Instance) chart2Instance.resize()
    // 延迟再次resize确保DOM完全渲染
    setTimeout(() => {
      if (chart1Instance) chart1Instance.resize()
      if (chart2Instance) chart2Instance.resize()
    }, 100)
  })
}

const onTagChange1 = (value: string[]) => {
  console.log('onTagChange1:', value)
  testSetTags.value = value
  // 更新最大曲线数量
  maxLenCurve.value = Math.max(value.length, testSetTags2.value.length)
  chart1Option.value = customOptions(value, allData.value, buildCustomConfig(value), channelsForm)
  if (chart1Instance) {
    disposeEChart(chart1Instance)
    chart1Instance = null
  }
  updateCharts()
}

const onTagChange2 = (value: string[]) => {
  console.log('onTagChange2:', value)
  testSetTags2.value = value
  // 更新最大曲线数量
  maxLenCurve.value = Math.max(testSetTags.value.length, value.length)
  chart2Option.value = customOptions(value, allData.value, buildCustomConfig(value), channelsForm2)
  if (chart2Instance) {
    disposeEChart(chart2Instance)
    chart2Instance = null
  }
  updateCharts()
}

const onSelect = async (value: any, node: any) => {
  showCharacter.value = false
  originLoading.value = true
  testSetTags.value = []
  testSetTags2.value = []
  tagOptions.value = []
  console.log('treeData.value', treeData.value)
  console.log('value', value)
  
  // 查找节点以获取ID
  let n = findNodeByKey(treeData.value, value)
  file_id.value = n ? n.id : parentTreeId.value
  
  const res = await getModelTestingResult({ file_id: file_id.value })
  if (res?.code === 200) {
    console.log('res.data:', res.data)
    const c1 = res?.data.options.character1
    const c2 = res?.data.options.character2
    maxLenCurve.value = Math.max(c1.length, c2.length)
    const data1 = res?.data.axisData
    const data2 = res?.data.axisData2
    // 默认选中第一个
    testSetTags.value = c1.length > 0 ? [c1[0]] : []
    testSetTags2.value = c2.length > 0 ? [c2[0]] : []
    
    tagOptions.value = [...c1, ...c2].map((tag) => ({
      label: tag,
      value: tag,
    }))
    allData.value = { ...data1, ...data2 }
    
    chart1Option.value = customOptions(testSetTags.value, allData.value, buildCustomConfig(testSetTags.value), channelsForm)
    chart2Option.value = customOptions(testSetTags2.value, allData.value, buildCustomConfig(testSetTags2.value), channelsForm2)
    updateCharts()
    showCharacter.value = true
    originLoading.value = false
  } else {
    // 如果请求失败，也要关闭loading状态
    showCharacter.value = false
    originLoading.value = false
  }
}

const chart1Option = ref({})
const chart2Option = ref({})
const chart3Option = ref({})
const chart1Ref = ref<HTMLDivElement | null>(null)
const chart2Ref = ref<HTMLDivElement | null>(null)
const chart3Ref = ref<HTMLDivElement | null>(null)
let chart1Instance: echarts.ECharts | null = null
let chart2Instance: echarts.ECharts | null = null
let chart3Instance: echarts.ECharts | null = null
const showFeature1Modal = ref(false)
const showFeature2Modal = ref(false)

const onFeature1SaveIndicators = (form: Record<string, any>) => {
  Object.keys(indicatorsForm).forEach((k) => delete (indicatorsForm as any)[k])
  Object.entries(form || {}).forEach(([k, v]) => ((indicatorsForm as any)[k] = v))
  chart1Option.value = buildCustomOptions(
    testSetTags.value,
    allData.value,
    indicatorsForm,
    channelsForm,
    maxLenCurve.value
  )
  if (chart1Instance) {
    disposeEChart(chart1Instance)
    chart1Instance = null
  }
  updateCharts()
  message.success('指标属性配置已更新，图表已刷新')
}

const onFeature2SaveIndicators = (form: Record<string, any>) => {
  Object.keys(indicatorsForm2).forEach((k) => delete (indicatorsForm2 as any)[k])
  Object.entries(form || {}).forEach(([k, v]) => ((indicatorsForm2 as any)[k] = v))
  chart2Option.value = buildCustomOptions(
    testSetTags2.value,
    allData.value,
    indicatorsForm2,
    channelsForm2,
    maxLenCurve.value
  )
  if (chart2Instance) {
    disposeEChart(chart2Instance)
    chart2Instance = null
  }
  updateCharts()
  message.success('指标属性配置已更新，图表已刷新')
}

const onFeature1SaveChannels = (form: any) => {
  Object.keys(channelsForm).forEach((k) => delete (channelsForm as any)[k])
  Object.assign(channelsForm, form || {})
  chart1Option.value = buildCustomOptions(
    testSetTags.value,
    allData.value,
    indicatorsForm,
    channelsForm,
    maxLenCurve.value
  )
  if (chart1Instance) {
    disposeEChart(chart1Instance)
    chart1Instance = null
  }
  updateCharts()
  message.success('道属性配置已更新，图表已刷新')
}

const onFeature2SaveChannels = (form: any) => {
  Object.keys(channelsForm2).forEach((k) => delete (channelsForm2 as any)[k])
  Object.assign(channelsForm2, form || {})
  chart2Option.value = buildCustomOptions(
    testSetTags2.value,
    allData.value,
    indicatorsForm2,
    channelsForm2,
    maxLenCurve.value
  )
  if (chart2Instance) {
    disposeEChart(chart2Instance)
    chart2Instance = null
  }
  updateCharts()
  message.success('道属性配置已更新，图表已刷新')
}

// 鲜艳颜色数组
const vividColorArray = ['#FF0000', '#0000FF', '#008000', '#FF8C00', '#8B008B', '#00CED1', '#DC143C', '#2F4F4F']

watch(
  testSetTags,
  (newTags) => {
    clearRecord(indicatorsForm)
    // 为每个选择项创建配置对象，赋默认值
    newTags.forEach((tag, index) => {
      // 创建配置对象

      if (!indicatorsForm[tag]) {
        indicatorsForm[tag] = {
          lineStyle: 'solid',
          color: vividColorArray[index % vividColorArray.length],
        }
        // 坐标范围：从ECharts数据中获取min和max
        const chartData = allData.value[tag] || []
        if (chartData.length > 0) {
          const min = getCurveRange(tag, chartData).min
          const max = getCurveRange(tag, chartData).max
          indicatorsForm[tag].range = [min, max]
        }
      }
      console.log('indicatorsForm;：', indicatorsForm)
    })
  },
  { immediate: true }
)

// ... (keep middle code, only replacing color usage)

watch(
  testSetTags2,
  (newTags) => {
    clearRecord(indicatorsForm2)
    // 为每个选择项创建配置对象，赋默认值
    newTags.forEach((tag, index) => {
      // 创建配置对象

      if (!indicatorsForm2[tag]) {
        indicatorsForm2[tag] = {
          lineStyle: 'solid',
          color: vividColorArray[index % vividColorArray.length],
        }
        // 坐标范围：从ECharts数据中获取min和max
        const chartData = allData.value[tag] || []
        if (chartData.length > 0) {
          const min = getCurveRange(tag, chartData).min
          const max = getCurveRange(tag, chartData).max
          indicatorsForm2[tag].range = [min, max]
        }
      }
      console.log('indicatorsForm2;：', indicatorsForm2)
    })
  },
  { immediate: true }
)

// ...

const buildCustomConfig = (tags: string[]) => {
  const config: Record<string, { lineStyle?: string; color?: string; range?: [number, number] }> =
    {}

  tags.forEach((tag, index) => {
    const tagConfig = indicatorsForm[tag] || {}

    // 先初始化range为undefined，避免直接访问未定义报错
    let range: [number, number] | undefined = undefined

    // 如果tagConfig.range存在且是长度为2的数组且两个元素都不是undefined，则用它
    if (
      Array.isArray(tagConfig.range) &&
      tagConfig.range.length === 2 &&
      tagConfig.range[0] !== undefined &&
      tagConfig.range[1] !== undefined
    ) {
      range = [tagConfig.range[0], tagConfig.range[1]]
    } else {
      // 否则从getCurveRange获取默认范围
      const curveData = allData.value[tag]
      if (curveData && Array.isArray(curveData) && curveData.length > 0) {
        const { min, max } = getCurveRange(tag, curveData)
        range = [min, max]
      } else {
        // 如果数据不存在，使用默认范围
        range = [0, 100]
      }
    }

    config[tag] = {
      lineStyle: tagConfig.lineStyle || 'solid',
      color: tagConfig.color || vividColorArray[index % vividColorArray.length] || '#000000',
      range,
    }
  })

  return config
}

function customOptions(
  curves: string[],
  data: Record<string, number[][]>,
  customConfig: Record<string, { lineStyle?: string; color?: string; range?: [number, number] }>,
  channelsConfig: {
    logarithmicScale?: string
    showScaleLines?: boolean
    thinLine?: string //x-细刻度
    thinLineCount?: number
    thickLine?: string //x-主刻度
    thickLineCount?: number
    showDepthLines?: boolean
    depthThinLine?: string
    depthInterval?: number
    depthThickLine?: string
    depthThickInterval?: number
  },
  isChart3: boolean = false // 新增参数，标识是否为图表3
) {
  console.log('channelsConfig:', channelsConfig)
  const curveDisplayName = (curveName: string) => {
    if (!isChart3) return curveName
    if (curveName === 'prediction_coords') return '预测曲线'
    if (curveName === 'true_coords') return '真实曲线'
    return curveName
  }

  const a1 = channelsConfig.thickLineCount || 2 // 主分割线份数
  const a2 = channelsConfig.thinLineCount || 10 // 次分割线份数
  let xMin = Infinity,
    xMax = -Infinity

  // 全局x轴最大最小值
  Object.values(customConfig).forEach((cfg) => {
    if (
      cfg.range &&
      Array.isArray(cfg.range) &&
      typeof cfg.range[0] === 'number' &&
      typeof cfg.range[1] === 'number'
    ) {
      xMin = Math.min(xMin, cfg.range[0])
      xMax = Math.max(xMax, cfg.range[1])
    }
  })

  // 计算主分割线位置
  const mainSplitPositions = []
  for (let i = 1; i < a1; i++) {
    mainSplitPositions.push(xMin + (i * (xMax - xMin)) / a1)
  }

  // 计算次分割线位置
  const minorSplitPositions = []
  for (let i = 1; i < a2; i++) {
    minorSplitPositions.push(xMin + (i * (xMax - xMin)) / a2)
  }
  console.log('mainSplitPositions:', mainSplitPositions, minorSplitPositions)

  const series = curves.map((c, index) => {
    // 获取自定义配置，如果没有则使用默认值
    const config = customConfig?.[c] || {}
    const color = config.color || vividColorArray[index % vividColorArray.length]

    return {
      name: curveDisplayName(c),
      type: 'line',
      data: data[c] || [],
      lineStyle: { color },
      itemStyle: { color },
      symbol: 'none',
      showSymbol: false,
      yAxisIndex: 0,
      xAxisIndex: index,
    }
  })
  // 分隔线
  const separatorSeries: any = {
    name: '',
    type: 'line',
    data: [],
    lineStyle: { color: 'transparent' },
    markLine: {
      silent: true,
      symbol: 'none',
      label: { show: false },
      data: channelsConfig.showScaleLines
        ? [
            ...mainSplitPositions.map((pos) => ({
              xAxis: pos,
              lineStyle: {
                color: '#999',
                width: channelsConfig?.thickLine ? parseInt(channelsConfig.thickLine) : 3,
                type: 'solid',
              },
            })),
            ...minorSplitPositions.map((pos) => ({
              xAxis: pos,
              lineStyle: {
                color: '#ccc',
                width: channelsConfig?.thinLine ? parseInt(channelsConfig.thinLine) : 1,
                type: 'solid',
              },
            })),
          ]
        : [],
    },
  }
  series.push(separatorSeries)

  // 如果curves为空，返回空的配置
  if (!curves || curves.length === 0) {
    return buildEChartOption({
      grid: {
        top: 30,
      },
      series: [],
      xAxis: [],
    })
  }

  const xAxis = curves.map((c, index) => {
    // 获取自定义配置，如果没有则使用默认值
    const config = customConfig?.[c] || {}
    const lineStyle = config.lineStyle || 'solid'
    const color = config.color || vividColorArray[index % vividColorArray.length]
    
    // 如果传入了自定义的min和max，使用传入的值，否则默认
    const min = config.range?.[0] !== undefined ? config.range[0] : getCurveRange(c, data[c]).min
    const max = config.range?.[1] !== undefined ? config.range[1] : getCurveRange(c, data[c]).max
    
    // 使用容差比较来处理浮点数精度问题
    const labelEpsilon = Math.max(Math.abs(max - min) * 1e-6, 1e-9)
    // 格式化数值显示
    const formatAxisLabel = (v: number) => {
      if (!Number.isFinite(v)) return ''
      const abs = Math.abs(v)
      if (abs >= 10000 || (abs > 0 && abs < 0.001)) return v.toExponential(2)
      const rounded = Math.round(v * 100) / 100
      return String(rounded)
    }

    return {
      name: curveDisplayName(c),
      nameLocation: 'middle',
      nameGap: 5,
      nameTextStyle: {
        color,
      },
      type: 'value',
      position: 'top',
      offset: 10 + 30 * index,
      axisLine: {
        show: true,
        lineStyle: {
          color,
          type: lineStyle,
        },
      },
      axisLabel: {
        color,
        margin: 3,
        showMinLabel: true,
        showMaxLabel: true,
        hideOverlap: false,
        formatter: function (value: number) {
          // 使用容差比较来判断是否为最小值或最大值
          if (Math.abs(value - min) <= labelEpsilon) return formatAxisLabel(min)
          if (Math.abs(value - max) <= labelEpsilon) return formatAxisLabel(max)
          return ''
        },
      },
      axisTick: { show: false },
      splitLine: {
        show: false,
      },
      min,
      max,
    }
  })
  
  if (channelsConfig.logarithmicScale === 'true') {
    // 只有图表3才使用自适应的最大值，图表1和图表2保持固定的0.1-1000
    let logMax = 1000
    if (isChart3 && xMax !== -Infinity && xMax > 0) {
      // 在实际最大值基础上增加一些边距
      logMax = xMax * 1.2
      // 确保最小值为0.1，如果计算出的最大值小于0.1，则使用默认值
      if (logMax <= 0.1) {
        logMax = 1000
      }
    }
    const logAxis: any = {
      type: 'log',
      logBase: 10,
      min: 0.1,
      max: logMax,
      splitLine: {
        show: true,
      },
      axisLabel: {
        color: '#666',
        margin: 8,
        formatter: (val: number) => val.toString(),
      },
    }
    xAxis.push(logAxis)
  }

  return buildEChartOption({
    showYAxisLabel: false,
    grid: {
      top: curves.length <= 1 ? 60 : (30 * (curves.length + (channelsConfig.logarithmicScale === 'true' ? 1 : 0)) +
        (isChart3 ? 26 : 20)),
      left: isChart3 ? 70 : 60,
      right: 50,
      containLabel: true,
      bottom: isChart3 ? 63 : 20,
    },
    series,
    xAxis,
    yAxis: {
      type: 'value',
      inverse: true,
      name: 'Depth (m)',
      nameLocation: 'middle',
      nameGap: 40,
      nameTextStyle: {
        fontSize: 12,
        color: '#666',
        align: 'center'
      },
      nameRotate: 90,
      position: 'left',
      min: function (value: any) {
        return Math.floor(value.min)
      },
      max: function (value: any) {
        return Math.ceil(value.max)
      },
      axisTick: { show: false },
      axisLine: {
        show: true,
        lineStyle: {
          type: 'solid',
        },
      },
      axisLabel: {
        hideOverlap: true, // 自动隐藏重叠的标签
        margin: 8,
        fontSize: 12,
        rotate: 0, // 不旋转标签
      },
      interval: channelsConfig.depthThickInterval,
      splitLine: {
        show: !!channelsConfig?.showDepthLines,
        lineStyle: {
          width: channelsConfig?.depthThickLine ? parseInt(channelsConfig.depthThickLine) : 3,
          type: 'solid',
        },
      },
      minorTick: {
        show: false,
        splitNumber:
          (channelsConfig?.depthThickInterval || 10) / (channelsConfig?.depthInterval || 1),
      },
      minorSplitLine: {
        show: !!channelsConfig?.showDepthLines,
        lineStyle: {
          width: channelsConfig?.depthThinLine ? parseInt(channelsConfig.depthThinLine) : 1,
          type: 'solid',
        },
      },
    },
  })
}

// 按钮处理函数
const handleLoadModel = async () => {
  if (!selectedData.value) {
    message.warning('请先选择预测数据！')
    return
  }
  if (!trainSetTags.value) {
    message.warning('请先选择模型权重！')
    return
  }
  testLoading.value = true
  enabled.value = false
  // startLog()
  // 预测模式下，使用当前页面选择的数据进行预测
  const data = {
    file_ids: [file_id.value],  // 使用当前选择的文件ID
    idm: Number((trainSetTags.value).split('-')[0]) || 0,
    file_id: file_id.value,
    predict_mode: true,
    type: trainSetOptions.value.find((item: any) => item.value === trainSetTags.value)?.type || 'best-data',
  }
  try {
    const res = await getTestOutputResult(data)
    if (res?.code === 200) {
      // 预测模式下只有预测结果，没有真实结果
      const curves: string[] = []
      const chartData: Record<string, number[][]> = {}

      if (
        res.data.prediction_coords &&
        Array.isArray(res.data.prediction_coords) &&
        res.data.prediction_coords.length > 0
      ) {
        curves.push('prediction_coords')
        chartData['prediction_coords'] = res.data.prediction_coords
      }

      allData.value = chartData

      if (curves.length === 0) {
        enabled.value = false
        logEnabled.value = false
        message.warning('预测完成，但未返回可展示的结果')
        return
      }

      const customConfig = buildCustomConfig(curves)

      curves.forEach((curveName) => {
        const curveData = allData.value[curveName]
        if (curveData && Array.isArray(curveData) && curveData.length > 0) {
          const values = curveData
            .filter(
              (d: any[]) => d && Array.isArray(d) && d.length > 0 && d[0] != null && !isNaN(d[0])
            )
            .map((d: any[]) => d[0])

          if (values.length > 0) {
            const min = Math.min(...values)
            const max = Math.max(...values)
            console.log('curveName,min,max', curveName, min, max)

            customConfig[curveName] = {
              ...customConfig[curveName],
              range: [Math.floor(min), Math.ceil(max)],
              color: curveName === 'prediction_coords' ? '#FF0000' : '#0000FF',
            }
          } else {
            console.warn(`没有找到有效的 ${curveName} 数据点`)
          }
        } else {
          console.warn(`${curveName} 数据为空或格式不正确:`, curveData)
        }
      })

      console.log('customConfig', customConfig)
      chart3Option.value = customOptions(curves, allData.value, customConfig, channelsForm, true)
      nextTick(() => {
        if (chart3Ref.value) {
          if (!chart3Instance) {
            chart3Instance = initEChart(chart3Ref.value, chart3Option.value)
          } else {
            updateEChart(chart3Instance, chart3Option.value)
          }
        }
        if (chart3Instance) {
          chart3Instance.resize()
        }
        setTimeout(() => {
          if (chart3Instance) {
            chart3Instance.resize()
          }
        }, 100)
      })
      enabled.value = true
      logEnabled.value = true
    } else {
      enabled.value = false
      logEnabled.value = false
      message.error(res?.message || '预测失败')
    }
  } catch (e: any) {
    enabled.value = false
    logEnabled.value = false
    const errorMsg = e?.response?.data?.message || e?.message || '预测请求失败'
    console.error('模型预测失败:', e)
    message.error(errorMsg)
  } finally {
    testLoading.value = false
  }
}

// 取消训练逻辑
function cancelTrain() {
  logModalVisible.value = false
  isTesting.value = false
  logEnabled.value = false
  if (logTimer) clearInterval(logTimer)
  selectedData.value = null
  trainSetTags.value = ''
}

// 误差展示表弹窗相关
const showMetricModal = ref(false)
const metricTableData = ref([
  { metric: 'MAE', value: 0.123 },
  { metric: 'MSE', value: 0.456 },
  { metric: 'RMSE', value: 0.789 },
  { metric: 'R2', value: 0.912 },
  { metric: 'MAPE', value: 0.234 },
  { metric: 'SMAPE', value: 0.345 },
  { metric: 'Bias', value: 0.567 },
])
const metricTableColumns = [
  { title: 'Metric', dataIndex: 'metric', key: 'metric' },
  { title: 'Value', dataIndex: 'value', key: 'value' },
]
function handleShowMetricModal() {
  showMetricModal.value = true
}
// 获取预测数据用于导出
function getPredictionDataForExport() {
  const predictionData = allData.value['prediction_coords']
  if (!predictionData || !Array.isArray(predictionData) || predictionData.length === 0) {
    message.warning('暂无可导出的预测数据')
    return null
  }
  return predictionData
}

// 导出为Excel (CSV格式，Excel可打开)
function handleExportExcel() {
  const predictionData = getPredictionDataForExport()
  if (!predictionData) return

  try {
    // 构建CSV内容
    let csvContent = '\uFEFF' // BOM for UTF-8
    csvContent += '深度(m),预测值\n'
    
    predictionData.forEach((point: any[]) => {
      if (point && Array.isArray(point) && point.length >= 2) {
        const value = point[0] // 预测值
        const depth = point[1] // 深度
        csvContent += `${depth},${value}\n`
      }
    })

    // 创建Blob并下载
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', `预测结果_${new Date().toISOString().slice(0, 10)}.csv`)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    
    message.success('Excel文件导出成功')
  } catch (error) {
    console.error('导出Excel失败:', error)
    message.error('导出Excel失败')
  }
}

// 导出为TxT
function handleExportTxt() {
  const predictionData = getPredictionDataForExport()
  if (!predictionData) return

  try {
    // 构建TXT内容
    let txtContent = '# 预测结果数据\n'
    txtContent += `# 导出时间: ${new Date().toLocaleString()}\n`
    txtContent += '# 格式: 深度(m) 预测值\n'
    txtContent += '#-------------------------------\n'
    txtContent += 'DEPTH\tPREDICTION\n'
    
    predictionData.forEach((point: any[]) => {
      if (point && Array.isArray(point) && point.length >= 2) {
        const value = point[0] // 预测值
        const depth = point[1] // 深度
        txtContent += `${depth}\t${value}\n`
      }
    })

    // 创建Blob并下载
    const blob = new Blob([txtContent], { type: 'text/plain;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', `预测结果_${new Date().toISOString().slice(0, 10)}.txt`)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    
    message.success('TxT文件导出成功')
  } catch (error) {
    console.error('导出TxT失败:', error)
    message.error('导出TxT失败')
  }
}

// 导出为LAS格式（测井数据标准格式）
function handleExportLas() {
  const predictionData = getPredictionDataForExport()
  if (!predictionData) return

  try {
    // 计算深度范围
    const depths = predictionData
      .filter((p: any[]) => p && Array.isArray(p) && p.length >= 2)
      .map((p: any[]) => p[1])
    
    const minDepth = Math.min(...depths)
    const maxDepth = Math.max(...depths)
    const step = depths.length > 1 ? Math.abs(depths[1] - depths[0]) : 0.125

    // 构建LAS 2.0格式内容
    let lasContent = ''
    
    // 版本信息部分
    lasContent += '~VERSION INFORMATION\n'
    lasContent += ' VERS.                          2.0 : CWLS LOG ASCII STANDARD - VERSION 2.0\n'
    lasContent += ' WRAP.                          NO  : ONE LINE PER DEPTH STEP\n'
    
    // 井信息部分
    lasContent += '~WELL INFORMATION\n'
    lasContent += ` STRT.M                    ${minDepth.toFixed(4)} : START DEPTH\n`
    lasContent += ` STOP.M                    ${maxDepth.toFixed(4)} : STOP DEPTH\n`
    lasContent += ` STEP.M                    ${step.toFixed(4)} : STEP\n`
    lasContent += ' NULL.                     -999.25 : NULL VALUE\n'
    lasContent += ' COMP.                     UNKNOWN : COMPANY\n'
    lasContent += ' WELL.                     PREDICTION : WELL NAME\n'
    lasContent += ` DATE.                     ${new Date().toISOString().slice(0, 10)} : DATE\n`
    
    // 曲线信息部分
    lasContent += '~CURVE INFORMATION\n'
    lasContent += ' DEPT.M                            : DEPTH\n'
    lasContent += ' PRED.                             : PREDICTION VALUE\n'
    
    // 参数信息部分
    lasContent += '~PARAMETER INFORMATION\n'
    
    // 数据部分
    lasContent += '~ASCII LOG DATA\n'
    
    predictionData.forEach((point: any[]) => {
      if (point && Array.isArray(point) && point.length >= 2) {
        const value = point[0] // 预测值
        const depth = point[1] // 深度
        // LAS格式每个值占一定宽度，用空格分隔
        lasContent += ` ${depth.toFixed(4)}  ${value.toFixed(6)}\n`
      }
    })

    // 创建Blob并下载
    const blob = new Blob([lasContent], { type: 'text/plain;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', `预测结果_${new Date().toISOString().slice(0, 10)}.las`)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    
    message.success('LAS文件导出成功')
  } catch (error) {
    console.error('导出LAS失败:', error)
    message.error('导出LAS失败')
  }
}
const handleFeature1IconClick = () => {
  console.log('特征1图标按钮被点击')
  showFeature1Modal.value = true
}

// 特征2图标按钮点击事件
const handleFeature2IconClick = () => {
  console.log('特征2图标按钮被点击')
  showFeature2Modal.value = true
}

const handleIconHover = (event: Event) => {
  const target = event.target as HTMLElement
  if (target) {
    target.style.backgroundColor = '#f5f5f5'
    target.style.borderColor = '#40a9ff'
  }
}

const handleIconLeave = (event: Event) => {
  const target = event.target as HTMLElement
  if (target) {
    target.style.backgroundColor = '#fff'
    target.style.borderColor = '#d9d9d9'
  }
}
</script>
<style scoped>
.preview-panel {
  flex: 1;
  padding: var(--spacing-2xl);
  background: var(--bg-secondary);
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  height: 100%;
  overflow-y: auto;
}

/* 选择卡片 - 统一工业风格 */
.preprocess-select-card {
  width: 100%;
  min-width: 320px;
  min-height: 120px;
  border-radius: var(--radius-lg);
  background: var(--bg-primary);
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
  margin-bottom: var(--spacing-2xl);
  flex-shrink: 0;
  border: 1px solid var(--border-color);
  overflow: hidden;
  transition: var(--transition-base);
}

.preprocess-select-card:hover {
  box-shadow: var(--shadow-md);
  border-color: var(--border-color-hover);
}

/* 卡片标题 - 改进设计（顶部+左侧蓝条） */
.preview-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  min-height: 56px;
  display: flex;
  align-items: center;
  padding: var(--spacing-lg) var(--spacing-xl);
  padding-left: var(--spacing-2xl);
  background: var(--bg-secondary);
  flex-shrink: 0;
  position: relative;
  border-left: 4px solid var(--primary-color);
  border-right: 3px solid var(--primary-color);
  border-bottom: 2px solid var(--primary-color);
}

/* 顶部蓝色渐变装饰条 */
.preview-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--primary-color) 0%, var(--primary-light) 100%);
}

.preview-title-actions {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--spacing-sm);
  margin-left: auto;
}

/* 右侧卡片标题样式调整 */
.preprocess-half-card.right .preview-title {
  flex-direction: column;
  align-items: flex-start;
  height: auto;
  min-height: 56px;
  padding: var(--spacing-md) var(--spacing-lg);
  gap: var(--spacing-sm);
  padding-left: var(--spacing-2xl);
}

.preprocess-half-card.right .preview-title-actions {
  width: 100%;
  justify-content: flex-start;
}

.preprocess-select-content {
  flex: 1;
  display: flex;
  align-items: center;
  padding: var(--spacing-md) var(--spacing-2xl);
  gap: var(--spacing-lg);
  justify-content: space-between;
  height: 100%;
}

.model-select-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  gap: var(--spacing-lg);
}

.preprocess-bottom-row {
  width: 100%;
  min-height: 850px;
  display: flex;
  gap: var(--spacing-2xl);
  flex: 1;
}

/* 半卡片 - 统一工业风格 */
.preprocess-half-card {
  flex: 1;
  min-width: 0;
  background: var(--bg-primary);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  margin-bottom: 0;
  min-height: 850px;
  transition: var(--transition-base);
  overflow: hidden;
}

.preprocess-half-card:hover {
  box-shadow: var(--shadow-md);
  border-color: var(--border-color-hover);
}

.preprocess-half-card.left {
  flex: 1.5;
}

.preprocess-half-card.right {
  flex: 0.6;
  max-width: 420px;
  min-width: 320px;
}

.half-card-content {
  flex: 1;
  height: 100%;
  padding: var(--spacing-xl);
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.select-item {
  flex: 1;
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  min-width: 0;
}

.select-label {
  font-size: 14px;
  color: var(--text-secondary);
  min-width: 70px;
  font-weight: 500;
  white-space: nowrap;
}

.select-value {
  font-size: 14px;
  color: var(--text-primary);
}

.preprocess-value-group {
  border: 1px solid var(--border-color);
  padding: var(--spacing-xs) var(--spacing-2xl);
  background: var(--bg-primary);
  min-height: 32px;
  display: flex;
  align-items: center;
  border-radius: var(--radius-md);
  transition: var(--transition-fast);
}

.preprocess-value-group:hover {
  border-color: var(--primary-lighter);
}
.data-select {
  width: 50% !important;
  min-width: 180px;
  max-width: none;
  height: auto;
}
.preprocess-title-inputs {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  background: #f5f7fa;
  height: 60px;
}

.feature-item {
  display: flex;
  align-items: center;
  /* gap: 12px; */
  flex: 1;
}

.button-group {
  display: flex;
  align-items: center;
  gap: 12px;
  height: 100%;
}

/* 移除按钮圆角覆盖，使用全局样式 */

/* 日志模态框内容 */
.log-modal-content {
  height: 100%;
  overflow-y: auto;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 13px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  padding: var(--spacing-md);
}

/* 图表行 - 改进设计 */
.echarts-row {
  display: flex;
  width: 100%;
  gap: var(--spacing-lg);
  margin-top: var(--spacing-lg);
  flex: 1;
  min-height: 0;
  height: 100%;
  position: relative;
  padding: var(--spacing-md);
  box-sizing: border-box;
}

/* 图表容器 - 统一工业风格 */
.chart-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: var(--spacing-md);
  background: var(--bg-primary);
  box-shadow: var(--shadow-xs);
  position: relative;
  min-width: 200px;
  transition: var(--transition-base);
}

.chart-container:hover {
  box-shadow: var(--shadow-sm);
  border-color: var(--primary-lighter);
}

/* 图表标签 - 改进设计 */
.chart-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--primary-color);
  padding: var(--spacing-xs) var(--spacing-sm);
  background: var(--bg-secondary);
  border-radius: var(--radius-sm);
  margin-bottom: var(--spacing-sm);
  text-align: center;
  border: 1px solid var(--border-color);
}

.echart-half {
  flex: 1;
  width: 100%;
  height: 100%;
  min-height: 0;
  position: relative;
  box-sizing: border-box;
  background: var(--bg-primary);
  border-radius: var(--radius-sm);
}

.echart-all {
  width: 100%;
  height: 100%;
  min-height: 0;
  position: relative;
  box-sizing: border-box;
}
</style>
