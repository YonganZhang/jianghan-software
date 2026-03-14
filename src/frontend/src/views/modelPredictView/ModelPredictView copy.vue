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
                <span class="select-label">特征1：</span>
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
                <span class="select-label">特征2：</span>
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
          <div ref="chart1Ref" class="echart-half"></div>
          <div ref="chart2Ref" class="echart-half"></div>
        </div>
      </div>
      <div class="preprocess-half-card right">
        <div class="preview-title">
          <span>结果展示</span>
          <span class="preview-title-actions">
            <!-- <a-button @click="handleShowMetricModal" :disabled="!logEnabled">误差展示表</a-button> -->
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
        <div
          class="echarts-row"
          v-show="!enabled"
          style="display: flex; justify-content: center; align-items: center"
        >
          <a-spin v-show="testLoading" tip="模型测试中..." />
          <a-empty v-show="!testLoading" description="暂无结果，请点击开始测试"></a-empty>
        </div>
        <div v-show="enabled" class="echarts-row" style="display: flex">
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
import { findParentDirectory } from '@/utils/tree'
import { useStore } from 'vuex'
import { buildCustomOptions } from '@/components/echarts/chartOptionHelper'
import FeatureConfigModal from '@/components/echarts/FeatureConfigModal.vue'

// vuex
const store = useStore()
const testTags = computed(() => store.state.testTags)
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

watch(
  testSetTags,
  (newTags) => {
    // 清空表单对象
    indicatorsForm.value = {}
    // 为每个选择项创建配置对象，赋默认值
    newTags.forEach((tag, index) => {
      // 创建配置对象

      if (!indicatorsForm[tag]) {
        indicatorsForm[tag] = {
          lineStyle: 'solid',
          color: colorArray[index],
        }
        // 坐标范围：从ECharts数据中获取min和max
        const chartData = allData.value[tag] || []
        if (chartData.length > 0) {
          const min = getCurveRange(tag).min
          const max = getCurveRange(tag).max
          indicatorsForm[tag].range = [min, max]
        }
      }
      console.log('indicatorsForm;：', indicatorsForm.value)
    })
  },
  { immediate: true }
)

function handleShowLog() {
  logModalVisible.value = true
}

function resizeCharts() {
  if (chart1Instance) chart1Instance.resize()
  if (chart2Instance) chart2Instance.resize()
  if (chart3Instance) chart3Instance.resize()
}

onActivated(async () => {
  // 读取模型权重
  const res = await getTreeData()
  if (res?.data) {
    const rawData = res.data[0]?.children ?? []
    treeData.value = patchTreeKeys(rawData)
    parentTreeId.value = res.data[0].id
  }
  const res2 = await getAddSelect()
  if (res2) {
    const best = res2.data['best-data'].map((t: any) => ({ label: t.name, value: t.id + '-best-data', type: 'best-data' }));
    const final = res2.data['final-data'].map((t: any) => ({ label: t.name, value: t.id + '-final-data', type: 'final-data' }));
    trainSetOptions.value = [...best, ...final];
  }
  window.addEventListener('resize', resizeCharts)
})

onUnmounted(() => {
  window.removeEventListener('resize', resizeCharts)
  if (logTimer) clearInterval(logTimer)
  if (chart1Instance) chart1Instance.dispose()
  if (chart2Instance) chart2Instance.dispose()
  if (chart3Instance) chart3Instance.dispose()
})

watch(
  testSetTags,
  (newTags) => {
    // 清空表单对象
    indicatorsForm.value = {}
    // 为每个选择项创建配置对象，赋默认值
    newTags.forEach((tag, index) => {
      // 创建配置对象

      if (!indicatorsForm[tag]) {
        indicatorsForm[tag] = {
          lineStyle: 'solid',
          color: colorArray[index],
        }
        // 坐标范围：从ECharts数据中获取min和max
        const chartData = allData.value[tag] || []
        if (chartData.length > 0) {
          const min = getCurveRange(tag).min
          const max = getCurveRange(tag).max
          indicatorsForm[tag].range = [min, max]
        }
      }
      console.log('indicatorsForm;：', indicatorsForm.value)
    })
  },
  { immediate: true }
)

watch(
  testSetTags2,
  (newTags) => {
    // 清空表单对象
    indicatorsForm2.value = {}
    // 为每个选择项创建配置对象，赋默认值
    newTags.forEach((tag, index) => {
      // 创建配置对象

      if (!indicatorsForm2[tag]) {
        indicatorsForm2[tag] = {
          lineStyle: 'solid',
          color: colorArray[index],
        }
        // 坐标范围：从ECharts数据中获取min和max
        const chartData = allData.value[tag] || []
        if (chartData.length > 0) {
          const min = getCurveRange(tag).min
          const max = getCurveRange(tag).max
          indicatorsForm2[tag].range = [min, max]
        }
      }
      console.log('indicatorsForm2;：', indicatorsForm2.value)
    })
  },
  { immediate: true }
)

watch(maxLenCurve, (newValue) => {
  // 更新图表1的配置
  chart1Option.value = customOptions(
    testSetTags.value,
    allData.value,
    buildCustomConfig(testSetTags.value),
    channelsForm
  )
  // 更新图表2的配置
  chart2Option.value = customOptions(
    testSetTags2.value,
    allData.value,
    buildCustomConfig(testSetTags2.value),
    channelsForm2
  )
  // 更新图表3的配置
  chart3Option.value = customOptions(
    testSetTags.value,
    allData.value,
    buildCustomConfig(testSetTags.value),
    channelsForm,
    true
  )
  // 强制重新初始化图表实例
  if (chart1Instance) {
    disposeEChart(chart1Instance)
    chart1Instance = null
  }
  if (chart2Instance) {
    disposeEChart(chart2Instance)
    chart2Instance = null
  }
  if (chart3Instance) {
    disposeEChart(chart3Instance)
    chart3Instance = null
  }
  updateCharts()
})

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
  testSetTags.value = value
  // 更新最大曲线数量
  maxLenCurve.value = Math.max(value.length, testSetTags2.value.length)
  chart2Option.value = customOptions(value, allData.value, buildCustomConfig(value), channelsForm2)
  if (chart2Instance) {
    disposeEChart(chart2Instance)
    chart2Instance = null
  }
  updateCharts()
}

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
    } else if (node.type === 'txt') {
      option.icon = txtIcon
    } else if (node.type === 'xlsx') {
      option.icon = excelIcon
    } else {
      option.icon = frameIcon
    }
    return option
  })
}
const file_id = ref(0)
const onSelect = async (value: any, node: any) => {
  showCharacter.value = false
  originLoading.value = true
  testSetTags.value = []
  testSetTags2.value = []
  tagOptions.value = []
  let n = findParentDirectory(treeData.value, node.key)
  file_id.value = n ? n.id : parentTreeId.value
  const res = await getModelTestingResult({ file_id: file_id.value })
  if (res?.code === 200) {
    console.log('res.data:', res.data)
    const c1 = res?.data.options.character1
    const c2 = res?.data.options.character2
    maxLenCurve.value = Math.max(c1.length, c2.length)
    const data1 = res?.data.axisData
    const data2 = res?.data.axisData2
    testSetTags.value = c1
    testSetTags2.value = c2
    tagOptions.value = [...testSetTags.value, ...testSetTags2.value].map((tag) => ({
      label: tag,
      value: tag,
    }))
    allData.value = { ...data1, ...data2 }
    chart1Option.value = customOptions(c1, allData.value, buildCustomConfig(c1), channelsForm)
    chart2Option.value = customOptions(c2, allData.value, buildCustomConfig(c2), channelsForm2)
    updateCharts()
    showCharacter.value = true
    originLoading.value = false
  } else {
    // 如果请求失败，也要关闭loading状态
    showCharacter.value = false
    originLoading.value = true
  }
}

// 导出功能占位，防止报错
function exportExcel() {
  // 占位方法，后续可实现导出功能
}

const isTesting = ref(false)
// 新增：输出日志按钮可用状态
const logEnabled = ref(false)

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
    if (chart1Instance) chart1Instance.resize()
    if (chart2Instance) chart2Instance.resize()
  })
}

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
      const { min, max } = getCurveRange(tag)
      range = [min, max]
    }

    config[tag] = {
      lineStyle: tagConfig.lineStyle || 'solid',
      color: tagConfig.color || colorArray[index] || '#000000',
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
  const a1 = channelsConfig.thickLineCount // 主分割线份数
  const a2 = channelsConfig.thinLineCount // 次分割线份数
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
    const color = config.color || colorArray[index]

    return {
      name: c,
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
  series.push({
    name: '',
    type: 'line',
    data: [],
    lineStyle: { opacity: 0 },
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
  })

  const xAxis = curves.map((c, index) => {
    // 获取自定义配置，如果没有则使用默认值
    const config = customConfig?.[c] || {}
    const lineStyle = config.lineStyle || 'solid'
    const color = config.color || colorArray[index]
    // 如果传入了自定义的min和max，使用传入的值，否则默认
    const min = config.range?.[0] !== undefined ? config.range[0] : getCurveRange(c).min
    const max = config.range?.[1] !== undefined ? config.range[1] : getCurveRange(c).max

    return {
      name: c,
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
        formatter: function (value: number) {
          // 只显示最小值和最大值，中间显示空白
          if (value === min || value === max) {
            return value.toString()
          }
          return ''
        },
      },
      axisTick: { show: false },
      splitLine: {
        // 主刻度线
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

    xAxis.push({
      type: 'log',
      logBase: 10,
      min: 0.1,
      max: logMax,
      splitLine: {
        show: true,
        lineStyle: {
          type: 'dashed',
          color: '#ccc',
        },
      },
      axisLabel: { show: false },
      // axisLabel: {
      //   formatter: (val) => `10^${Math.log10(val)}`,
      // },
    })
  }

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

  return buildEChartOption({
    grid: {
      top: 30 * maxLenCurve.value + 20,
    },
    series,
    xAxis,
    yAxis: {
      type: 'value',
      inverse: true,
      name: '',
      position: 'left',
      nameLocation: 'start',
      nameGap: 0,
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
      interval: channelsConfig.depthThickInterval,
      splitLine: {
        // 主刻度线
        show: !!channelsConfig?.showDepthLines,
        lineStyle: {
          width: channelsConfig?.depthThickLine ? parseInt(channelsConfig.depthThickLine) : 3,
          type: 'solid',
        },
      },
      minorTick: {
        show: false,
        splitNumber: channelsConfig?.depthThickInterval / channelsConfig?.depthInterval, // 在主刻度之间分成20份，每份间隔就是1
      },
      minorSplitLine: {
        //细刻度
        show: !!channelsConfig?.showDepthLines,
        lineStyle: {
          width: channelsConfig?.depthThinLine ? parseInt(channelsConfig.depthThinLine) : 1, // 线宽
          type: 'solid',
        },
      },
    },
  })
}

// 按钮处理函数
const handleLoadModel = async () => {
  if (!selectedData.value || !trainSetTags.value) {
    message.warning('请先选择模型权重和测试数据！')
    return
  }
  if (!testTags.value[0]) {
    message.warning('请到新增模型模块选择测试集！')
    return
  }
  testLoading.value = true
  enabled.value = false
  // startLog()
  // TODO: 实现加载模型的逻辑
  const data = {
    dir_id: testTags.value[0],
    idm: Number((trainSetTags.value).split('-')[0]) || 0,
    file_id: file_id.value,
    predict_mode: true,
    type: trainSetOptions.value.find((item) => item.value === trainSetTags.value)?.type || 'best-data',
  }
  const res = await getTestOutputResult(data)
  if (res?.code === 200) {
    const c1 = ['prediction_coords', 'true_coords']
    const d1 = { prediction_coords: res.data.prediction_coords },
      d2 = { true_coords: res.data.true_coords }
    allData.value = { ...d1, ...d2 }

    // 为prediction_coords和true_coords计算实际数据范围
    const customConfig = buildCustomConfig(c1)

    // 为prediction_coords和true_coords设置基于实际数据的范围和颜色
    c1.forEach(curveName => {
      const curveData = allData.value[curveName]
      if (curveData && Array.isArray(curveData) && curveData.length > 0) {
        // 对于坐标数据，point[0] 是横坐标值，添加强验证
        const values = curveData
          .filter(d => d && Array.isArray(d) && d.length > 0 && d[0] != null && !isNaN(d[0]))
          .map(d => d[0])

        if (values.length > 0) {
          const min = Math.min(...values)
          const max = Math.max(...values)
          console.log("curveName,min,max", curveName, min, max)

          // 设置特定颜色：prediction_coords为红色，true_coords为蓝色
          const curveColor = curveName === 'prediction_coords' ? '#FF0000' : '#0000FF'

          customConfig[curveName] = {
            ...customConfig[curveName],
            range: [Math.floor(min), Math.ceil(max)],
            color: curveColor
          }
        } else {
          console.warn(`没有找到有效的 ${curveName} 数据点`)
        }
      } else {
        console.warn(`${curveName} 数据为空或格式不正确:`, curveData)
      }
    })
    console.log("customConfig", customConfig )
    chart3Option.value = customOptions(c1, allData.value, customConfig, channelsForm, true)
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
    })
    testLoading.value = false
    enabled.value = true
  } else {
    testLoading.value = true
    enabled.value = false
  }
}

// 取消训练逻辑
function cancelTrain() {
  logModalVisible.value = false
  isTesting.value = false
  logEnabled.value = false
  if (logTimer) clearInterval(logTimer)
  selectedData.value = null
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
  position: relative;
}
.echart-half {
  width: 100%;
  height: 100%;
  min-width: 0;
  position: relative;
}
.echart-all {
  width: 990px;
  height: 900px;
  position: relative;
}
</style>
