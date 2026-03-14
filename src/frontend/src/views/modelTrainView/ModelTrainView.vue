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
              <span class="select-label">读取模型权重：</span>
              <a-select
                v-model:value="selectedModel"
                :options="modelOptions"
                placeholder="请选择模型权重"
                allow-clear
                style="flex: 1"
              />
            </div>
          </a-form-item>
          <a-form-item
            class="select-item"
            style="flex: 1; padding: 0; margin-bottom: 0; border: none"
          >
            <div style="display: flex; align-items: center; width: 100%; gap: 8px">
              <span class="select-label">筛选测试数据：</span>
              <a-select
                v-model:value="selectedTestData"
                :options="testDataOptions"
                placeholder="请选择测试数据"
                allow-clear
                style="flex: 1"
              />
            </div>
          </a-form-item>
          <a-form-item class="button-group" style="display: flex; align-items: center">
            <a-button type="primary" :loading="isTesting" @click="handleLoadModel">
              {{ isTesting ? '模型测试中' : '开始测试' }}
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
                <span class="select-label">特征1：</span>
                <a-select
                  v-model:value="feature1"
                  mode="tags"
                  allow-clear
                  style="flex: 1"
                  :disabled="!logEnabled"
                />
              </div>
            </a-form-item>
            <a-form-item
              class="select-item"
              style="flex: 1; padding: 0; margin-bottom: 0; border: none"
            >
              <div style="display: flex; align-items: center; width: 100%">
                <span class="select-label">特征2：</span>
                <a-select
                  v-model:value="feature2"
                  mode="tags"
                  allow-clear
                  style="flex: 1"
                  :disabled="!logEnabled"
                />
              </div>
            </a-form-item>
          </a-form>
        </div>
        <div v-if="!logEnabled" class="preprocess-select-content">
          <img
            src="@/assets/无结果2.svg"
            alt="无结果"
            style="width: 100%; height: 100%; object-fit: contain; opacity: 0.7"
          />
        </div>
        <div v-else class="echarts-row">
          <div ref="chart1Ref" class="echart-half"></div>
          <div ref="chart2Ref" class="echart-half"></div>
        </div>
      </div>
      <div class="preprocess-half-card right">
        <div class="preview-title">
          <span>结果展示</span>
          <span class="preview-title-actions">
            <a-button @click="handleShowMetricModal" :disabled="!logEnabled">误差展示表</a-button>
            <a-button
              type="primary"
              :icon="h(DownloadOutlined)"
              @click="exportExcel"
              :disabled="!logEnabled"
            >
              导出为Excel
            </a-button>
            <a-button
              type="primary"
              :icon="h(DownloadOutlined)"
              @click="exportExcel"
              :disabled="!logEnabled"
            >
              导出为TxT
            </a-button>
          </span>
        </div>
        <div v-if="!logEnabled" class="preprocess-select-content">
          <img
            src="@/assets/无结果2.svg"
            alt="无结果"
            style="width: 100%; height: 100%; object-fit: contain; opacity: 0.7"
          />
        </div>
        <div v-else class="echarts-row">
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
    <a-modal v-model:open="showMetricModal" title="误差展示表" width="400px" :footer="null">
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
    </a-modal>
  </div>
</template>
<script setup lang="ts">
import { ref, h, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { DownloadOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'

// 日志弹窗相关
const logModalVisible = ref(false)
const logList = ref<string[]>([])
let logTimer: number | null = null

const feature1 = ref<string[]>([])
const feature2 = ref<string[]>([])

function startLog() {
  if (logTimer) clearInterval(logTimer)
  logList.value = []
  let count = 1
  logTimer = setInterval(() => {
    logList.value.push(`【${new Date().toLocaleTimeString()}】日志内容第${count}行...`)
    count++
    nextTick(() => {
      const modal = document.querySelector('.log-modal-content')
      if (modal) modal.scrollTop = modal.scrollHeight
    })
  }, 1000) as unknown as number
}
function handleShowLog() {
  logModalVisible.value = true
}

function resizeCharts() {
  if (chart1Instance) chart1Instance.resize()
  if (chart2Instance) chart2Instance.resize()
  if (chart3Instance) chart3Instance.resize()
}

onMounted(() => {
  window.addEventListener('resize', resizeCharts)
})

onUnmounted(() => {
  window.removeEventListener('resize', resizeCharts)
  if (logTimer) clearInterval(logTimer)
  if (chart1Instance) chart1Instance.dispose()
  if (chart2Instance) chart2Instance.dispose()
  if (chart3Instance) chart3Instance.dispose()
})

// 导出功能占位，防止报错
function exportExcel() {
  // 占位方法，后续可实现导出功能
}

const isTesting = ref(false)
// 新增：输出日志按钮可用状态
const logEnabled = ref(false)

// 独立的下拉框数据和选中项
const modelOptions = [
  { label: 'xxx数据20250619.xlsx', value: 'xxx数据20250619.xlsx' },
  { label: 'yyy数据20250619.xlsx', value: 'yyy数据20250619.xlsx' },
  { label: 'zzz数据20250619.xlsx', value: 'zzz数据20250619.xlsx' },
]
const selectedModel = ref()
const testDataOptions = [
  { label: 'xxx数据20250619.xlsx', value: 'xxx数据20250619.xlsx' },
  { label: 'yyy数据20250619.xlsx', value: 'yyy数据20250619.xlsx' },
  { label: 'zzz数据20250619.xlsx', value: 'zzz数据20250619.xlsx' },
]
const selectedTestData = ref()

const chart1Option = ref({})
const chart2Option = ref({})
const chart3Option = ref({})
// 不再使用vue-echarts，直接用echarts
const chart1Ref = ref<HTMLDivElement | null>(null)
const chart2Ref = ref<HTMLDivElement | null>(null)
const chart3Ref = ref<HTMLDivElement | null>(null)
let chart1Instance: echarts.ECharts | null = null
let chart2Instance: echarts.ECharts | null = null
let chart3Instance: echarts.ECharts | null = null

function updateCharts() {
  // 示例数据
  function generateCurveData(length = 100, min = 40, max = 160) {
    const data = []
    const depthStep = 6000 / length
    let current = (min + max) / 2
    for (let i = 0; i < length; i++) {
      const noise = (Math.random() - 0.5) * 20
      current = Math.max(min, Math.min(max, current + noise))
      const depth = i * depthStep
      data.push([current, depth])
    }
    return data
  }

  const gr = generateCurveData(100, 40, 160)
  const sp = generateCurveData(100, 50, 110)
  const cal = generateCurveData(100, 10, 40)

  const a = generateCurveData(100, 0, 1)
  const b = generateCurveData(100, 0, 1)

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' },
    },
    legend: {
      bottom: 0,
      // icon: 'line',
      data: ['GR (API)', 'SP (mV)', 'CAL (mm)'],
    },
    grid: {
      left: 70,
      right: 20,
      top: 40,
      bottom: 120,
    },
    xAxis: [
      {
        name: 'GR (API)',
        nameLocation: 'middle',
        // nameGap: 30,
        nameTextStyle: {
          align: 'left',
          color: '#00B050',
          padding: [0, 0, 0, -260],
        },
        type: 'value',
        min: 40,
        max: 160,
        position: 'bottom',
        offset: 24,
        axisLine: { show: false, lineStyle: { color: '#00B050' } },
        axisLabel: { color: '#00B050', margin: 8 },
        axisTick: { show: false },
      },
      {
        name: 'SP (mV)',
        nameLocation: 'middle',
        // nameGap: 30,
        nameTextStyle: {
          align: 'left',
          color: '#0070C0',
          padding: [0, 0, 0, -260],
        },
        type: 'value',
        min: 50,
        max: 110,
        position: 'bottom',
        offset: 12,
        axisLine: { show: false, lineStyle: { color: '#0070C0' } },
        axisLabel: { color: '#0070C0', margin: 8 },
        axisTick: { show: false },
      },
      {
        name: 'CAL (mm)',
        nameLocation: 'middle',
        // nameGap: 30,
        nameTextStyle: {
          align: 'left',
          color: '#C000B0',
          padding: [0, 0, 0, -260],
        },
        type: 'value',
        min: 10,
        max: 40,
        position: 'bottom',
        offset: 0,
        axisLine: { show: false, lineStyle: { color: '#C000B0' } },
        axisLabel: { color: '#C000B0', margin: 8 },
        axisTick: { show: false },
      },
    ],
    yAxis: {
      type: 'value',
      inverse: true,
      name: 'Depth (m)',
      nameLocation: 'start',
      nameGap: 10,
    },
    series: [
      {
        name: 'GR (API)',
        type: 'line',
        xAxisIndex: 0,
        yAxisIndex: 0,
        data: gr,
        lineStyle: { color: '#00B050' },
        itemStyle: { color: '#00B050' },
        symbol: 'none',
        showSymbol: false,
      },
      {
        name: 'SP (mV)',
        type: 'line',
        xAxisIndex: 1,
        yAxisIndex: 0,
        data: sp,
        lineStyle: { color: '#0070C0' },
        itemStyle: { color: '#0070C0' },
        symbol: 'none',
        showSymbol: false,
      },
      {
        name: 'CAL (mm)',
        type: 'line',
        xAxisIndex: 2,
        yAxisIndex: 0,
        data: cal,
        lineStyle: { color: '#C000B0' },
        itemStyle: { color: '#C000B0' },
        symbol: 'none',
        showSymbol: false,
      },
    ],
  }

  chart1Option.value = option
  chart2Option.value = JSON.parse(JSON.stringify(chart1Option.value))
  chart3Option.value = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' },
    },
    legend: {
      bottom: 0,
      // icon: 'line',
      data: ['A', 'B'],
    },
    grid: {
      left: 60,
      right: 20,
      top: 40,
      bottom: 60,
    },
    xAxis: {
      type: 'value',
      min: 0,
      max: 1,
      position: 'bottom',
      axisLine: { show: true, lineStyle: { color: '#000' } },
      axisLabel: { show: true, color: '#000', margin: 8 },
      axisTick: { show: false },
      name: '', // 不显示 name
    },
    yAxis: {
      type: 'value',
      inverse: true,
      name: 'Depth (m)',
      nameLocation: 'start',
      nameGap: 10,
    },
    series: [
      {
        name: 'A',
        type: 'line',
        xAxisIndex: 0,
        yAxisIndex: 0,
        data: a,
        lineStyle: { color: '#1CB052' },
        itemStyle: { color: '#1CB052' },
        symbol: 'none',
        showSymbol: false,
      },
      {
        name: 'B',
        type: 'line',
        xAxisIndex: 0,
        yAxisIndex: 0,
        data: b,
        lineStyle: { color: '#1650FF' },
        itemStyle: { color: '#1650FF' },
        symbol: 'none',
        showSymbol: false,
      },
    ],
  }
  nextTick(() => {
    if (chart1Ref.value) {
      if (!chart1Instance) {
        chart1Instance = echarts.init(chart1Ref.value)
      }
      chart1Instance.setOption(chart1Option.value)
    }
    if (chart2Ref.value) {
      if (!chart2Instance) {
        chart2Instance = echarts.init(chart2Ref.value)
      }
      chart2Instance.setOption(chart2Option.value)
    }
    if (chart3Ref.value) {
      if (!chart3Instance) {
        chart3Instance = echarts.init(chart3Ref.value)
      }
      chart3Instance.setOption(chart3Option.value)
    }
    resizeCharts()
  })
}

// 按钮处理函数
const handleLoadModel = () => {
  if (!selectedModel.value || !selectedTestData.value) {
    message.warning('请先选择模型权重和测试数据！')
    return
  }
  isTesting.value = true
  logEnabled.value = false
  logModalVisible.value = true
  startLog()
  setTimeout(() => {
    isTesting.value = false
    logEnabled.value = true
    if (logTimer) clearInterval(logTimer) // 测试完成后停止日志刷新
    // 数据展示加载
    feature1.value = ['GR(API)', 'SP(mV)', 'CAL(mm)']
    feature2.value = ['AC(µs/m)', 'CNL(%)', 'DEN(g/cm³)']
    updateCharts()
  }, 1000)
  console.log('加载模型', selectedModel.value)
  // TODO: 实现加载模型的逻辑
}

// 取消训练逻辑
function cancelTrain() {
  logModalVisible.value = false
  isTesting.value = false
  logEnabled.value = false
  if (logTimer) clearInterval(logTimer)
  selectedModel.value = undefined
  selectedTestData.value = undefined
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
function handleExportExcel() {
  // TODO: 实现导出Excel
}
function handleExportTxt() {
  // TODO: 实现导出TxT
}
</script>
<style scoped>
.preview-panel {
  flex: 1;
  padding: 16px;
  background: #f0f2f5;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  height: 100%;
}
.preprocess-select-card {
  width: 100%;
  min-width: 320px;
  height: 116px;
  border-radius: 2px;
  background: #fff;
  box-shadow: 0px 0px 12px 0px #00000040;
  display: flex;
  flex-direction: column;
  margin-bottom: 24px;
}
.preview-title {
  font-size: 16px;
  font-weight: 700;
  color: #161b25;
  height: 60px;
  display: flex;
  align-items: center;
  padding: 12px;
  background: #f5f7fa;
  border-top-left-radius: 2px;
  border-top-right-radius: 2px;
}
.preview-title-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-left: auto;
}
.preprocess-select-content {
  flex: 1;
  display: flex;
  align-items: center;
  padding: 0 24px;
  gap: 24;
  justify-content: space-between;
  height: 100%;
}

.model-select-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  gap: 16px;
}
.preprocess-bottom-row {
  width: 100%;
  display: flex;
  flex: 1;
  gap: 24px;
}
.preprocess-half-card {
  flex: 1;
  min-width: 0;
  background: #fff;
  border-radius: 2px;
  box-shadow: 0px 0px 12px 0px #00000040;
  display: flex;
  flex-direction: column;
  margin-bottom: 0;
  height: 100%;
}
.half-card-content {
  flex: 1;
  height: 100%;
  padding: 16px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
}
.select-item {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}
.select-label {
  font-family: Source Han Sans CN;
  font-size: 14px;
  color: #5a5a68;
  min-width: 70px;
  font-weight: 400;
  white-space: nowrap;
}
.select-value {
  font-size: 14px;
  color: #000000d9;
}
.preprocess-value-group {
  border: 1px solid #d9d9d9;
  padding: 4px 34px;
  background: #ffffff;
  min-height: 32px;
  display: flex;
  align-items: center;
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

:deep(.ant-btn),
:deep(.ant-btn-primary),
:deep(.ant-btn-default),
:deep(.ant-btn-dangerous) {
  border-radius: 0 !important;
}
.log-modal-content {
  height: 100%;
  overflow-y: auto;
  background: #fff;
  color: #232b3a;
  font-family: monospace;
  font-size: 14px;
  /* padding: 12px;
  border-radius: 4px; */
  border: 1px solid #eee;
}
.echarts-row {
  display: flex;
  width: 100%;
  gap: 16px;
  margin-top: 16px;
  height: 100%;
}
.echart-half {
  width: 50%;
  height: 100%;
  min-width: 0;
}
.echart-all {
  width: 100%;
  height: 100%;
  min-width: 0;
}
</style>
