<template>
  <div class="preview-panel">
    <div class="preprocess-select-card">
      <div class="preview-title">
        <span>预处理选择</span>
      </div>
      <div class="preprocess-select-content">
        <a-row gutter="24" style="width: 100%">
          <a-col :span="6" style="display: flex; align-items: center">
            <div class="select-item">
              <span class="select-label">选择数据：</span>
              <a-tree-select
                v-model:value="selectedData"
                :tree-data="dataOptions"
                :field-names="{ label: 'label', value: 'value', children: 'children' }"
                placeholder="请选择数据"
                allow-clear
                tree-default-expand-all
                style="width: 100%"
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
          </a-col>
          <a-col :span="16" style="display: flex; align-items: center">
            <div class="select-item" style="flex: 1">
              <div
                class="preprocess-group-block"
                v-for="group in preprocessGroups"
                :key="group.label"
              >
                <span class="select-label">{{ group.label }}：</span>
                <div class="preprocess-value-group-wrap">
                  <div
                    v-for="item in group.options"
                    :key="item.value"
                    class="preprocess-value-group selectable hover"
                    :class="{ selected: selectedPreprocess.includes(item.value) }"
                    @click="togglePreprocess(item.value)"
                  >
                    <span class="select-value">{{ item.label }}</span>
                  </div>
                </div>
              </div>
            </div>
          </a-col>
        </a-row>
      </div>
    </div>
    <div class="preprocess-select-card">
      <div class="preview-title">
        <span>输入参数表</span>
      </div>
      <div class="preprocess-select-content">
        <a-form
          ref="inputParamsFormRef"
          :model="inputParamsForm"
          layout="vertical"
          class="input-params-form"
        >
          <div class="input-params-container">
            <!-- 预设模型参数 -->
            <div class="param-column">
              <div class="param-column-header">
                <span class="param-column-title">预设模型参数</span>
              </div>
              <div class="param-column-content">
                <a-form-item name="input_size">
                  <template #label>
                    <a-tooltip title="输入特征维度" placement="right">
                      <span>输入维度：</span>
                    </a-tooltip>
                  </template>
                  <a-input-number
                    v-model:value="inputParamsForm.input_size"
                    :min="0"
                    :max="10000"
                    :step="1"
                    style="width: 100%"
                  />
                </a-form-item>
                <a-form-item name="batch_size">
                  <template #label>
                    <a-tooltip title="批次大小" placement="right">
                      <span>批量大小：</span>
                    </a-tooltip>
                  </template>
                  <a-input-number
                    v-model:value="inputParamsForm.batch_size"
                    :min="0"
                    :max="10000"
                    :step="1"
                    style="width: 100%"
                  />
                </a-form-item>
                <a-form-item name="output_size">
                  <template #label>
                    <a-tooltip title="输出特征维度" placement="right">
                      <span>输出维度：</span>
                    </a-tooltip>
                  </template>
                  <a-input-number
                    v-model:value="inputParamsForm.output_size"
                    :min="0"
                    :max="10000"
                    :step="1"
                    style="width: 100%"
                  />
                </a-form-item>
              </div>
            </div>

            <!-- 物理约束类 -->
            <div class="param-column">
              <div class="param-column-header">
                <span class="param-column-title">物理约束类</span>
              </div>
              <div class="param-column-content">
                <a-form-item name="phy_equation">
                  <template #label>
                    <a-tooltip title="知识约束表达式" placement="right">
                      <span>物理方程：</span>
                    </a-tooltip>
                  </template>
                  <div class="range-inputs">
                    <a-input v-model:value="inputParamsForm.phy_equation" style="width: 100%" />
                  </div>
                </a-form-item>
                <a-form-item name="phy_loss_type">
                  <template #label>
                    <a-tooltip title="物理loss类型" placement="right">
                      <span>物理约束损失类型：</span>
                    </a-tooltip>
                  </template>
                  <a-select
                    v-model:value="inputParamsForm.phy_loss_type"
                    style="width: 100%"
                    allow-clear
                  >
                    <a-select-option value="mse">mse</a-select-option>
                    <a-select-option value="mae">mae</a-select-option>
                  </a-select>
                </a-form-item>
                <a-form-item name="phy_loss_weight">
                  <template #label>
                    <a-tooltip title="物理loss加权系数 beta" placement="right">
                      <span>物理约束损失权重：</span>
                    </a-tooltip>
                  </template>
                  <a-input-number
                    v-model:value="inputParamsForm.phy_loss_weight"
                    :min="0"
                    :max="1"
                    :step="0.1"
                    style="width: 100%"
                  />
                </a-form-item>
                <a-form-item name="phy_loss_lower">
                  <template #label>
                    <a-tooltip title="物理loss表达式的下边界" placement="right">
                      <span>物理约束下边界：</span>
                    </a-tooltip>
                  </template>
                  <a-input-number
                    v-model:value="inputParamsForm.phy_loss_lower"
                    :min="0"
                    :max="1"
                    :step="0.1"
                    style="width: 100%"
                  />
                </a-form-item>
                <a-form-item name="phy_loss_upper">
                  <template #label>
                    <a-tooltip title="物理loss表达式的上边界" placement="right">
                      <span>物理约束上边界：</span>
                    </a-tooltip>
                  </template>
                  <a-input-number
                    v-model:value="inputParamsForm.phy_loss_upper"
                    :min="0"
                    :max="1"
                    :step="0.1"
                    style="width: 100%"
                  />
                </a-form-item>
              </div>
            </div>

            <!-- 输入设置类 -->
            <div class="param-column">
              <div class="param-column-header">
                <span class="param-column-title">输入设置类</span>
              </div>
              <div class="param-column-content">
                <!-- <a-form-item name="input_directory">
                  <template #label>
                    <a-tooltip title="输入数据目录" placement="right">
                      <span>输入目录：</span>
                    </a-tooltip>
                  </template>
                  <a-input
                    v-model:value="inputParamsForm.input_directory"
                    placeholder="请选择文件或目录"
                    readonly
                    style="width: 100%; cursor: pointer"
                    @click="selectInputDir"
                  />
                </a-form-item> -->
                <a-form-item name="sequence_length">
                  <template #label>
                    <a-tooltip title="序列长度" placement="right">
                      <span>序列长度：</span>
                    </a-tooltip>
                  </template>
                  <a-input-number
                    v-model:value="inputParamsForm.sequence_length"
                    :min="0"
                    :max="10000"
                    :step="1"
                    style="width: 100%"
                  />
                </a-form-item>
                <a-form-item name="scaler_type">
                  <template #label>
                    <a-tooltip title="标准化器类型" placement="right">
                      <span>标准化类型：</span>
                    </a-tooltip>
                  </template>
                  <a-select
                    v-model:value="inputParamsForm.scaler_type"
                    style="width: 100%"
                    allow-clear
                  >
                    <a-select-option value="fixed">fixed (固定物理范围)</a-select-option>
                    <a-select-option value="minmax">minmax</a-select-option>
                    <a-select-option value="standard">standard</a-select-option>
                    <a-select-option value="robust">robust</a-select-option>
                  </a-select>
                </a-form-item>
                <a-form-item name="predict_target">
                  <template #label>
                    <a-tooltip title="预测目标列" placement="right">
                      <span>预测目标：</span>
                    </a-tooltip>
                  </template>
                  <a-select
                    v-model:value="inputParamsForm.predict_target"
                    :options="predictTargetOptions"
                    placeholder="请先选择数据文件"
                    allow-clear
                    show-search
                    style="width: 100%"
                  />
                </a-form-item>
              </div>
            </div>
          </div>
        </a-form>
      </div>
    </div>
    <div class="preprocess-bottom-row">
      <div class="preprocess-half-card left" style="display: flex; flex-direction: column;">
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
                    :options="tagOptions1"
                    allow-clear
                    :max-tag-count="maxTagCountFeature1"
                    :max-tag-text-length="maxTagTextLength"
                    :max-tag-placeholder="maxTagPlaceholderFeature1"
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
                  <a-button
                    v-if="shouldShowToggleFeature1"
                    type="link"
                    size="small"
                    style="padding: 0 6px; height: 32px"
                    @click="toggleFeature1Tags"
                  >
                    {{ showAllFeature1Tags ? '收起' : '展开' }}
                  </a-button>
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
                    :options="tagOptions2"
                    mode="multiple"
                    allow-clear
                    :max-tag-count="maxTagCountFeature2"
                    :max-tag-text-length="maxTagTextLength"
                    :max-tag-placeholder="maxTagPlaceholderFeature2"
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
                  <a-button
                    v-if="shouldShowToggleFeature2"
                    type="link"
                    size="small"
                    style="padding: 0 6px; height: 32px"
                    @click="toggleFeature2Tags"
                  >
                    {{ showAllFeature2Tags ? '收起' : '展开' }}
                  </a-button>
                </div>
              </div>
            </a-form-item>
          </a-form>
        </div>
        <div v-if="!enabledRaw" class="preprocess-select-content" style="flex: 1; min-height: 0;">
          <div
            v-if="loading"
            style="
              display: flex;
              align-items: center;
              justify-content: center;
              width: 100%;
              height: 100%;
            "
          >
            <a-spin tip="数据加载中..." />
          </div>
          <img
            v-else
            src="@/assets/无结果2.svg"
            alt="无结果"
            style="width: 100%; height: 100%; object-fit: contain; opacity: 0.7"
          />
        </div>
        <div v-else class="echarts-row" style="flex: 1;">
          <div class="echart-col">
            <div
              v-if="!canRenderRawFeature1"
              style="display: flex; justify-content: center; align-items: center; width: 100%; height: 100%;"
            >
              <a-empty description="暂无数据"></a-empty>
            </div>
            <div ref="chart1Ref" v-show="canRenderRawFeature1" class="chart-container"></div>
          </div>
          <div class="echart-col">
            <div
              v-if="!canRenderRawFeature2"
              style="display: flex; justify-content: center; align-items: center; width: 100%; height: 100%;"
            >
              <a-empty description="暂无数据"></a-empty>
            </div>
            <div ref="chart2Ref" v-show="canRenderRawFeature2" class="chart-container"></div>
          </div>
          <div v-if="loading" class="loading-overlay">
            <a-spin tip="数据加载中..." />
          </div>
        </div>
      </div>
      <div class="preprocess-half-card right" style="display: flex; flex-direction: column;">
        <div class="preview-title">
          <span>结果展示</span>
        </div>
        <div v-if="!enabledProcessed" class="preprocess-select-content" style="flex: 1; min-height: 0;">
          <div
            v-if="loading2"
            style="
              display: flex;
              align-items: center;
              justify-content: center;
              width: 100%;
              height: 100%;
            "
          >
            <a-spin tip="数据预处理中..." />
          </div>
          <img
            v-else
            src="@/assets/无结果2.svg"
            alt="无结果"
            style="width: 100%; height: 100%; object-fit: contain; opacity: 0.7"
          />
        </div>
        <div v-else class="echarts-row" style="flex: 1;">
          <div class="echart-col">
            <div
              v-if="!canRenderProcessedFeature1"
              style="display: flex; justify-content: center; align-items: center; width: 100%; height: 100%;"
            >
              <a-empty description="暂无数据"></a-empty>
            </div>
            <div ref="chart3Ref" v-show="canRenderProcessedFeature1" class="chart-container"></div>
          </div>
          <div class="echart-col">
            <div
              v-if="!canRenderProcessedFeature2"
              style="display: flex; justify-content: center; align-items: center; width: 100%; height: 100%;"
            >
              <a-empty description="暂无数据"></a-empty>
            </div>
            <div ref="chart4Ref" v-show="canRenderProcessedFeature2" class="chart-container"></div>
          </div>
          <div v-if="loading2" class="loading-overlay">
            <a-spin tip="数据预处理中..." />
          </div>
        </div>
      </div>
    </div>
  </div>
  <a-modal
    v-model:open="showSaveModal"
    title="保存结果"
    @ok="handleSaveOk"
    @cancel="handleSaveCancel"
    ok-text="确定"
    cancel-text="取消"
  >
    <a-form ref="saveFormRef" :model="saveForm" :rules="saveFormRules" layout="vertical">
      <a-form-item label="保存文件名称" name="fileName" required>
        <a-input v-model:value="saveForm.fileName" placeholder="请输入文件名" />
      </a-form-item>
    </a-form>
  </a-modal>

  <!-- 统一特征配置弹窗 - 特征1 -->
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
</template>
<script setup lang="ts">
// 可根据需要引入相关逻辑
import { ref, computed, onMounted, onUnmounted, watch, nextTick, h, reactive, onActivated, defineOptions } from 'vue'
import { DownloadOutlined } from '@ant-design/icons-vue'
import frameIcon from '@/assets/file/frame.svg'
import excelIcon from '@/assets/file/excel.svg'
import txtIcon from '@/assets/file/txt.svg'
import {
  buildEChartOption,
  initEChart,
  updateEChart,
  disposeEChart,
  getMaxMinRangeForAllCurves,
  getCurveRange,
  colorArray,
  defaultChartConfig,
} from '@/components/echarts/echartsHelper'
import { Modal, Form, Input, Spin, message } from 'ant-design-vue'
import { getEchartsData, getTreeData } from '@/utils/api'
import type { Rule } from 'ant-design-vue/es/form'
import EchartCard from '@/components/echarts/EchartCard.vue'
import { buildCustomOptions } from '@/components/echarts/chartOptionHelper'
import FeatureConfigModal from '@/components/echarts/FeatureConfigModal.vue'


defineOptions({
  name: 'DataPreprocessView'
})

type MyTreeNode = {
  title: string
  key: number
  type: string
  id: number
  children?: MyTreeNode[]
}

const treeData = ref<MyTreeNode[]>([])
const enabledRaw = ref(false)
const enabledProcessed = ref(false)
const loading = ref(false)
const loading2 = ref(false)
const chart1Ref = ref<HTMLDivElement | null>(null)
const chart2Ref = ref<HTMLDivElement | null>(null)
const chart3Ref = ref<HTMLDivElement | null>(null)
const chart4Ref = ref<HTMLDivElement | null>(null)
let chart1Instance: any = null
let chart2Instance: any = null
let chart3Instance: any = null
let chart4Instance: any = null
const chart1Option = ref({})
const chart2Option = ref({})
const chart3Option = ref({})
const chart4Option = ref({})
const testSetTags = ref<string[]>([])
const testSetTags2 = ref<string[]>([])
const tagOptions1 = ref<{ label: string; value: string }[]>([])
const tagOptions2 = ref<{ label: string; value: string }[]>([])
const predictTargetOptions = computed(() => {
  const seen = new Set<string>()
  const res: { label: string; value: string }[] = []
  for (const opt of [...tagOptions1.value, ...tagOptions2.value]) {
    if (!opt?.value || seen.has(opt.value)) continue
    seen.add(opt.value)
    res.push({ label: opt.label, value: opt.value })
  }
  return res
})
const maxLenCurve = ref(0)
const rawData = ref<Record<string, number[][]>>({})
const processedData = ref<Record<string, number[][]>>({})
const canRenderRawFeature1 = computed(() => {
  return testSetTags.value.some((tag) => (rawData.value[tag] || []).length > 0)
})
const canRenderRawFeature2 = computed(() => {
  return testSetTags2.value.some((tag) => (rawData.value[tag] || []).length > 0)
})
const canRenderProcessedFeature1 = computed(() => {
  return testSetTags.value.some((tag) => (processedData.value[tag] || []).length > 0)
})
const canRenderProcessedFeature2 = computed(() => {
  return testSetTags2.value.some((tag) => (processedData.value[tag] || []).length > 0)
})
const MAX_VISIBLE_TAGS = 4
const maxTagTextLength = 12
const showAllFeature1Tags = ref(false)
const showAllFeature2Tags = ref(false)
const shouldShowToggleFeature1 = computed(() => testSetTags.value.length > MAX_VISIBLE_TAGS)
const shouldShowToggleFeature2 = computed(() => testSetTags2.value.length > MAX_VISIBLE_TAGS)
const maxTagCountFeature1 = computed(() => (showAllFeature1Tags.value ? undefined : MAX_VISIBLE_TAGS))
const maxTagCountFeature2 = computed(() => (showAllFeature2Tags.value ? undefined : MAX_VISIBLE_TAGS))
const defaultCurveColors = [
  '#2563eb',
  '#059669',
  '#d97706',
  '#dc2626',
  '#7c3aed',
  '#0d9488',
  '#ea580c',
  '#0891b2',
  '#9333ea',
  '#65a30d',
]
const getDefaultCurveColor = (index: number) => defaultCurveColors[index % defaultCurveColors.length]

const toggleFeature1Tags = (e: MouseEvent) => {
  e.stopPropagation()
  showAllFeature1Tags.value = !showAllFeature1Tags.value
}
const toggleFeature2Tags = (e: MouseEvent) => {
  e.stopPropagation()
  showAllFeature2Tags.value = !showAllFeature2Tags.value
}

const maxTagPlaceholderFeature1 = (omittedValues: unknown[]) => {
  return h(
    'span',
    {
      style: 'cursor: pointer; color: #1677ff; user-select: none;',
      onMousedown: (e: MouseEvent) => e.preventDefault(),
      onClick: (e: MouseEvent) => {
        e.stopPropagation()
        showAllFeature1Tags.value = true
      },
    },
    `+${omittedValues.length}...`
  )
}

const maxTagPlaceholderFeature2 = (omittedValues: unknown[]) => {
  return h(
    'span',
    {
      style: 'cursor: pointer; color: #1677ff; user-select: none;',
      onMousedown: (e: MouseEvent) => e.preventDefault(),
      onClick: (e: MouseEvent) => {
        e.stopPropagation()
        showAllFeature2Tags.value = true
      },
    },
    `+${omittedValues.length}...`
  )
}

// 输入参数表相关变量
const inputParamsFormRef = ref()
const inputParamsForm = reactive({
  input_size: 15,
  batch_size: 1024,
  output_size: 1,
  phy_equation: 'x0 + x1 - x2 * y = 0',
  phy_loss_type: 'mse',
  phy_loss_weight: 0,
  phy_loss_lower: 0,
  phy_loss_upper: 0,
  // input_directory: '',
  sequence_length: 64,
  scaler_type: 'standard',
  predict_target: 'RD',
})

// 特征1弹窗相关
const showFeature1Modal = ref(false)
const activeTab = ref('indicators') // 'indicators' | 'channels'

// 特征2弹窗相关
const showFeature2Modal = ref(false)
const activeTab2 = ref('indicators2') // 'indicators2' | 'channels2'

// 动态计算弹窗高度
const modalHeight = computed(() => {
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

interface IndicatorConfig {
  lineStyle?: string
  color?: string
  range?: [number, number]
}
// 指标属性表单 - 使用customConfig格式
const indicatorsForm = reactive<Record<string, IndicatorConfig>>({})
const indicatorsFormRef = ref()
// 校验坐标范围
const validateRange: Rule['validator'] = (_, value: unknown) => {
  if (!Array.isArray(value) || value.length !== 2) {
    return Promise.reject('必须输入两个数值')
  }
  if (value.some((v) => v === undefined || v === null || v === '')) {
    return Promise.reject('坐标不能为空')
  }
  if (Number(value[0]) >= Number(value[1])) {
    return Promise.reject('最小值必须小于最大值')
  }
  return Promise.resolve()
}
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
const channelsForm = reactive<ChannelConfig>({ ...defaultChartConfig })
const channelsFormRef = ref()

// 特征2的指标属性表单
const indicatorsForm2 = reactive<Record<string, IndicatorConfig>>({})
const indicatorsFormRef2 = ref()
const channelsFormRef2 = ref()
const channelsForm2 = reactive<ChannelConfig>({ ...defaultChartConfig })
// 选择输入目录/文件
// const selectInputDir = async () => {
//   try {
//     console.log('点击输入目录，检查 electronAPI:', window.electronAPI)
//     if (!window.electronAPI?.openFile) {
//       console.error('electronAPI.openFile 不可用，可能在浏览器环境中运行')
//       message.error('文件选择功能仅在 Electron 环境中可用')
//       return
//     }

//     const filePath = await window.electronAPI.openFile({
//       properties: ['openFile'],
//     })
//     console.log('选择的文件路径:', filePath)
//     if (filePath) {
//       inputParamsForm.input_directory = filePath
//       message.success('文件选择成功')
//     }
//   } catch (e) {
//     console.error('文件选择失败:', e)
//     message.error('文件选择失败')
//   }
// }

// 监听特征1选择框变化，更新表单对象
watch(
  testSetTags,
  (newTags) => {
    if (newTags.length <= MAX_VISIBLE_TAGS) {
      showAllFeature1Tags.value = false
    }
    Object.keys(indicatorsForm).forEach((k) => delete (indicatorsForm as any)[k])
    // 为每个选择项创建配置对象，赋默认值
    newTags.forEach((tag, index) => {
      indicatorsForm[tag] = {
        lineStyle: 'solid',
        color: getDefaultCurveColor(index),
      }
      // 坐标范围：从ECharts数据中获取min和max（只有当rawData中有数据时才设置）
      const chartData = rawData.value[tag]
      if (chartData && chartData.length > 0) {
        const min = getCurveRange(tag, chartData).min
        const max = getCurveRange(tag, chartData).max
        indicatorsForm[tag].range = [min, max]
      }
    })
  },
  { immediate: true }
)

// 监听特征2选择框变化，更新表单对象
watch(
  testSetTags2,
  (newTags) => {
    if (newTags.length <= MAX_VISIBLE_TAGS) {
      showAllFeature2Tags.value = false
    }
    Object.keys(indicatorsForm2).forEach((k) => delete (indicatorsForm2 as any)[k])
    // 为每个选择项创建配置对象，赋默认值
    newTags.forEach((tag, index) => {
      indicatorsForm2[tag] = {
        lineStyle: 'solid',
        color: getDefaultCurveColor(index),
      }
      // 坐标范围：从ECharts数据中获取min和max（只有当rawData中有数据时才设置）
      const chartData = rawData.value[tag]
      if (chartData && chartData.length > 0) {
        const min = getCurveRange(tag, chartData).min
        const max = getCurveRange(tag, chartData).max
        indicatorsForm2[tag].range = [min, max]
      }
    })
  },
  { immediate: true }
)

// 构建自定义配置对象 - 直接使用indicatorsForm的格式
const buildCustomConfig = (
  tags: string[],
  data: Record<string, number[][]>,
  indicatorModel: Record<string, IndicatorConfig> = indicatorsForm,
  mode: 'raw' | 'processed' = 'raw'
) => {
  const config: Record<string, { lineStyle?: string; color?: string; range?: [number, number] }> =
    {}

  const approxEqual = (a: number, b: number) =>
    Math.abs(a - b) <= Math.max(Math.abs(a), Math.abs(b), 1) * 1e-6
  const isValidRange = (r: unknown): r is [number, number] =>
    Array.isArray(r) &&
    r.length === 2 &&
    typeof r[0] === 'number' &&
    typeof r[1] === 'number' &&
    Number.isFinite(r[0]) &&
    Number.isFinite(r[1])
  const padRange = (r: [number, number]): [number, number] => {
    const [minV, maxV] = r
    const span = maxV - minV
    const pad = span > 0 ? span * 0.05 : Math.max(Math.abs(maxV) * 0.05, 1e-6)
    return [minV - pad, maxV + pad]
  }

  tags.forEach((tag, index) => {
    const tagConfig = indicatorModel[tag] || {}

    if (tag === 'cluster_label') {
      config[tag] = {
        lineStyle: tagConfig.lineStyle || 'solid',
        color: tagConfig.color || getDefaultCurveColor(index),
        range: [0, 4],
      }
      return
    }

    // 先初始化range为undefined，避免直接访问未定义报错
    let range: [number, number] | undefined = undefined

    const { min: dataMin, max: dataMax } = getCurveRange(tag, data[tag])
    const dataRange: [number, number] = [dataMin, dataMax]

    if (mode === 'processed') {
      let isAutoRange = false
      if (isValidRange(tagConfig.range)) {
        const rawChartData = rawData.value[tag]
        const rawDefault =
          Array.isArray(rawChartData) && rawChartData.length > 0
            ? ([
                getCurveRange(tag, rawChartData).min,
                getCurveRange(tag, rawChartData).max,
              ] as [number, number])
            : undefined
        const isAutoFromRaw =
          rawDefault &&
          approxEqual(tagConfig.range[0], rawDefault[0]) &&
          approxEqual(tagConfig.range[1], rawDefault[1])
        range = isAutoFromRaw ? dataRange : [tagConfig.range[0], tagConfig.range[1]]
        isAutoRange = Boolean(isAutoFromRaw)
      } else {
        range = dataRange
        isAutoRange = true
      }
      if (isAutoRange) {
        range = padRange(range)
      }
    } else {
      range = isValidRange(tagConfig.range) ? [tagConfig.range[0], tagConfig.range[1]] : dataRange
    }

    config[tag] = {
      lineStyle: tagConfig.lineStyle || 'solid',
      color: tagConfig.color || getDefaultCurveColor(index),
      range,
    }
  })

  return config
}

const handleColorChange = (event: Event, tag: string) => {
  const target = event.target as HTMLInputElement
  const hexColor = target.value

  // 直接存储十六进制颜色值
  indicatorsForm[tag].color = hexColor
}

// const testSetOptions = testSetTags.value.map((t) => ({ label: t, value: t }))
const selectedData = ref()
const selectedNode = ref()
const showSaveModal = ref(false)
const saveForm = ref({ fileName: '' })
const saveFormRef = ref()
const saveFormRules = {
  fileName: [{ required: true, message: '请输入文件名', trigger: 'blur' }],
}

function resizeCharts() {
  if (chart1Instance) chart1Instance.resize()
  if (chart2Instance) chart2Instance.resize()
  if (chart3Instance) chart3Instance.resize()
  if (chart4Instance) chart4Instance.resize()
}

function patchTreeKeys(nodes: MyTreeNode[], parentPath: string = ''): any[] {
  return nodes.map((node) => {
    const currentKey = parentPath ? `${parentPath}-${node.id}` : `${node.id}`
    const patchedNode = {
      ...node,
      key: currentKey,
    }
    if (node.children) {
      patchedNode.children = patchTreeKeys(node.children, currentKey)
    }
    return patchedNode
  })
}

async function refreshTreeData() {
  const res = await getTreeData()
  if (res.data) {
    const rawData = res.data?.[0]?.children ?? []
    treeData.value = patchTreeKeys(rawData)
  }
}

onActivated(async () => {
  await refreshTreeData()
  window.addEventListener('resize', resizeCharts)

  // 检查 Electron API 是否可用
  console.log('组件挂载时检查 electronAPI:', {
    isAvailable: !!window.electronAPI,
    hasOpenFile: !!window.electronAPI?.openFile,
    userAgent: navigator.userAgent,
  })
})

// onMounted(async () => {
//   const res = await getTreeData()
//   if (res.data) {
//     const rawData = res.data?.[0]?.children ?? []
//     treeData.value = patchTreeKeys(rawData)
//   }
//   window.addEventListener('resize', resizeCharts)
// })

// onMounted(async () => {
//   loading.value = true
//   // const res = await getOriginData({ key: node.id })
//   window.addEventListener('resize', resizeCharts)
//   const c1 = ['CAL', 'HAZI', 'DEVI', 'AC', 'GR', 'RD', 'RS', 'SP']
//   const c2 = ['CNL', 'DEN', 'GRSL', 'K', 'KTH', 'TH', 'PE']
//   maxLenCurve.value = Math.max(c1.length, c2.length)
//   testSetTags.value = c1
//   testSetTags2.value = c2
//   tagOptions.value = [...testSetTags.value, ...testSetTags2.value].map((tag) => ({
//     label: tag,
//     value: tag,
//   }))
//   allData.value = { ...data1, ...data2 }
//   console.log('channelsForm.value$$%%%%%%%%%%%%%%%', channelsForm)
//   chart1Option.value = buildCustomOptions(
//     c1,
//     allData.value,
//     buildCustomConfig(c1),
//     channelsForm,
//     maxLenCurve.value
//   )
//   chart2Option.value = buildCustomOptions(
//     c2,
//     allData.value,
//     buildCustomConfig(c2),
//     channelsForm2,
//     maxLenCurve.value
//   )
//   chart3Option.value = buildCustomOptions(
//     c1,
//     allData.value,
//     buildCustomConfig(c1),
//     channelsForm,
//     maxLenCurve.value
//   )
//   chart4Option.value = buildCustomOptions(
//     c2,
//     allData.value,
//     buildCustomConfig(c2),
//     channelsForm2,
//     maxLenCurve.value
//   )
//   updateCharts()
//   enabled.value = true
//   loading.value = false
// })

onUnmounted(() => {
  window.removeEventListener('resize', resizeCharts)
  disposeEChart(chart1Instance)
  disposeEChart(chart2Instance)
  disposeEChart(chart3Instance)
  disposeEChart(chart4Instance)
})

function rebuildChartOptions() {
  console.log('rebuildChartOptions: 特征1=', testSetTags.value, '特征2=', testSetTags2.value)

  chart1Option.value =
    testSetTags.value.length > 0
      ? buildCustomOptions(
          testSetTags.value,
          rawData.value,
          buildCustomConfig(testSetTags.value, rawData.value, indicatorsForm, 'raw'),
          channelsForm,
          maxLenCurve.value,
          false,
          true
        )
      : {}

  chart2Option.value =
    testSetTags2.value.length > 0
      ? buildCustomOptions(
          testSetTags2.value,
          rawData.value,
          buildCustomConfig(testSetTags2.value, rawData.value, indicatorsForm2, 'raw'),
          channelsForm2,
          maxLenCurve.value,
          false,
          true
        )
      : {}

  chart3Option.value =
    enabledProcessed.value && testSetTags.value.length > 0
      ? buildCustomOptions(
          testSetTags.value,
          processedData.value,
          buildCustomConfig(
            testSetTags.value,
            processedData.value,
            indicatorsForm,
            'processed'
          ),
          channelsForm,
          maxLenCurve.value,
          isStandardizeSelected.value,
          true
        )
      : {}

  chart4Option.value =
    enabledProcessed.value && testSetTags2.value.length > 0
      ? buildCustomOptions(
          testSetTags2.value,
          processedData.value,
          buildCustomConfig(
            testSetTags2.value,
            processedData.value,
            indicatorsForm2,
            'processed'
          ),
          channelsForm2,
          maxLenCurve.value,
          isStandardizeSelected.value,
          true
        )
      : {}

  console.log('图表状态: 特征1可渲染=', canRenderRawFeature1.value, '特征2可渲染=', canRenderRawFeature2.value)

  // 更新图表
  updateCharts()
}

watch(maxLenCurve, () => {
  rebuildChartOptions()
})

// 监听选择数据变化，预留与后端交互位置
// watch(selectedData, async (val) => {
//   if (val) {
//     loading.value = true
//     // 模拟异步加载
//     setTimeout(() => {
//       testSetTags.value = ['GR (API)', 'SP (mV)', 'CAL (mm)']
//       testSetTags2.value = ['AC (µs/m)', 'CNL (%)', 'DEN (g/cm³)']
//       enabled.value = true
//       loading.value = false
//       updateCharts()
//     }, 3000)
//   }
// })

// 递归将treeData转为a-select options，支持分组和icon
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

const dataOptions = computed(() => {
  const res = getOptions(treeData.value)
  return res
})

// 预处理方法分组
const preprocessGroups = [
  {
    label: '通用预处理',
    options: [
      { label: 'Z score去噪', value: 'zscore' },
      { label: '标准化', value: 'basic_normalization' },
    ],
  },
  {
    label: '特殊预处理',
    options: [
      { label: '岩性区分', value: '岩性分类' },
      { label: '消除套管栓', value: 'casing_bolt_removal' },
    ],
  },
]
const selectedPreprocess = ref<string[]>([])
const isStandardizeSelected = computed(() => selectedPreprocess.value.includes('basic_normalization'))

// 防抖定时器
let preprocessDebounceTimer: number | null = null

function resetProcessedState() {
  enabledProcessed.value = false
  processedData.value = {}
}

async function togglePreprocess(val: string) {
  console.log('val:', val)
  console.log('selectedPreprocess', selectedPreprocess.value)
  const idx = selectedPreprocess.value.indexOf(val)
  if (idx === -1) {
    selectedPreprocess.value.push(val)
  } else {
    selectedPreprocess.value.splice(idx, 1)
  }

  // 清除之前的定时器
  if (preprocessDebounceTimer) {
    clearTimeout(preprocessDebounceTimer)
  }

  // 设置防抖延迟，500ms后执行API调用
  preprocessDebounceTimer = setTimeout(async () => {
    // todo: 调用后端-预处理
    console.log("selectedPreprocess", selectedPreprocess)
    if (!selectedNode.value?.id) {
      resetProcessedState()
      message.warning('请先选择数据')
      return
    }

    if (selectedPreprocess.value.length === 0) {
      resetProcessedState()
      loading2.value = false
      return
    }

    loading2.value = true
    const value = [...selectedPreprocess.value]
    const requiresPredictTarget = value.some((t) =>
      ['岩性分类', 'zscore', 'basic_normalization'].includes(t)
    )
    if (requiresPredictTarget) {
      const target = String(inputParamsForm.predict_target || '').trim()
      if (!target) {
        resetProcessedState()
        message.warning('请先指定预测目标列')
        loading2.value = false
        return
      }
      const available = new Set(predictTargetOptions.value.map((o) => o.value))
      if (available.size > 0 && !available.has(target)) {
        resetProcessedState()
        message.warning('预测目标列不在当前数据中')
        loading2.value = false
        return
      }
    }
    try {
      const res = await getEchartsData(
        {
          type: value,
          key: String(selectedNode.value.id),
          predict_target: inputParamsForm.predict_target,
          scaler_type: inputParamsForm.scaler_type,
          sequence_length: inputParamsForm.sequence_length,
          batch_size: inputParamsForm.batch_size,
          input_size: inputParamsForm.input_size,
        },
        { timeout: 120000 }
      )
      if (res?.code === 200) {
        const payload = res?.data
        const c1 = payload?.options?.character1
        const c2 = payload?.options?.character2
        if (!Array.isArray(c1) || !Array.isArray(c2)) {
          resetProcessedState()
          message.error(payload?.message || res?.message || '数据解析失败')
          return
        }
        tagOptions1.value = c1.map((tag: string) => ({ label: tag, value: tag }))
        tagOptions2.value = c2.map((tag: string) => ({ label: tag, value: tag }))
        const availableTags = new Set<string>([...c1, ...c2].map((t) => String(t)))
        testSetTags.value = testSetTags.value.filter((t) => availableTags.has(t))
        testSetTags2.value = testSetTags2.value.filter((t) => availableTags.has(t))
        const hasLithology = value.includes('岩性分类') || value.includes('岩性区分')
        if (hasLithology && availableTags.has('cluster_label')) {
          const selected = new Set<string>([...testSetTags.value, ...testSetTags2.value])
          if (!selected.has('cluster_label')) {
            testSetTags.value = [...testSetTags.value, 'cluster_label']
          }
        }
        if (testSetTags.value.length === 0 && c1.length > 0) {
          testSetTags.value = [c1[0]]
        }
        if (testSetTags2.value.length === 0 && c2.length > 0) {
          testSetTags2.value = [c2[0]]
        }
        const data1 = payload?.axisData
        const data2 = payload?.axisData2
        processedData.value = { ...(data1 || {}), ...(data2 || {}) }
        Object.keys(processedData.value).forEach((key) => {
          if (Array.isArray(processedData.value[key])) {
            processedData.value[key].sort((a, b) => a[1] - b[1])
          }
        })

        maxLenCurve.value = Math.max(testSetTags.value.length, testSetTags2.value.length)
        chart3Option.value = buildCustomOptions(
          testSetTags.value,
          processedData.value,
          buildCustomConfig(
            testSetTags.value,
            processedData.value,
            indicatorsForm,
            'processed'
          ),
          channelsForm,
          maxLenCurve.value,
          isStandardizeSelected.value,
          true  // showYAxisName
        )
        chart4Option.value = buildCustomOptions(
          testSetTags2.value,
          processedData.value,
          buildCustomConfig(
            testSetTags2.value,
            processedData.value,
            indicatorsForm2,
            'processed'
          ),
          channelsForm2,
          maxLenCurve.value,
          isStandardizeSelected.value,
          false  // showYAxisName - 特征2不显示
        )
        enabledProcessed.value = true
        // 必须调用 updateCharts 来初始化预处理后的图表实例
        updateCharts()
        await refreshTreeData()
      } else {
        resetProcessedState()
        message.error(res?.message || '预处理失败')
      }
    } catch (e: unknown) {
      resetProcessedState()
      message.error((e as Error)?.message || '预处理请求失败')
    } finally {
      loading2.value = false
    }
  }, 2000) // 2s防抖延迟
}

async function onSelect(value: number, node: MyTreeNode) {
  // todo:传后端-原始数据
  loading.value = true
  
  // 先销毁旧的图表实例，确保重新选择数据时能正确刷新
  disposeEChart(chart1Instance)
  disposeEChart(chart2Instance)
  disposeEChart(chart3Instance)
  disposeEChart(chart4Instance)
  chart1Instance = null
  chart2Instance = null
  chart3Instance = null
  chart4Instance = null
  
  // 清除旧的曲线选择
  testSetTags.value = []
  testSetTags2.value = []
  
  enabledRaw.value = false
  enabledProcessed.value = false
  processedData.value = {}
  selectedPreprocess.value = []
  if (preprocessDebounceTimer) {
    clearTimeout(preprocessDebounceTimer)
    preprocessDebounceTimer = null
  }
  try {
    const nodeId = (node as any)?.id ?? Number(String((node as any)?.value ?? '').split('-').pop())
    const res = await getEchartsData(
      {
        type: [],
        key: String(nodeId),
        predict_target: inputParamsForm.predict_target,
        scaler_type: inputParamsForm.scaler_type,
        sequence_length: inputParamsForm.sequence_length,
        batch_size: inputParamsForm.batch_size,
        input_size: inputParamsForm.input_size,
      },
      { timeout: 60000 }
    )
    if (res?.code === 200) {
      const payload = res?.data
      const c1 = payload?.options?.character1
      const c2 = payload?.options?.character2
      if (!Array.isArray(c1) || !Array.isArray(c2)) {
        enabledRaw.value = false
        selectedNode.value = node
        message.error(payload?.message || res?.message || '数据解析失败')
        return
      }
      const data1 = payload?.axisData
      const data2 = payload?.axisData2

      console.log('数据加载: 特征1选项', c1.length, '个, 特征2选项', c2.length, '个')

      tagOptions1.value = c1.map((tag: string) => ({ label: tag, value: tag }))
      tagOptions2.value = c2.map((tag: string) => ({ label: tag, value: tag }))
      const currentPredictTarget = String(inputParamsForm.predict_target || '').trim()
      const available = new Set([...c1, ...c2].map((t: string) => String(t)))
      if (!currentPredictTarget || (available.size > 0 && !available.has(currentPredictTarget))) {
        inputParamsForm.predict_target = (c1[0] || c2[0] || '') as any
      }

      // 先设置rawData，这样watch中的indicatorsForm初始化时才能获取到正确的数据
      rawData.value = { ...(data1 || {}), ...(data2 || {}) }
      Object.keys(rawData.value).forEach((key) => {
        if (Array.isArray(rawData.value[key])) {
          rawData.value[key].sort((a, b) => a[1] - b[1])
        }
      })

      console.log('rawData已加载，共', Object.keys(rawData.value).length, '个特征数据')

      // 然后设置testSetTags和testSetTags2，触发watch来初始化indicatorsForm
      testSetTags.value = c1.length > 0 ? [c1[0]] : []
      testSetTags2.value = c2.length > 0 ? [c2[0]] : []

      // maxLenCurve 是曲线的数量（用于计算顶部多个x轴的空间）
      maxLenCurve.value = Math.max(testSetTags.value.length, testSetTags2.value.length)
      if (maxLenCurve.value === 0) {
         maxLenCurve.value = 1
      }

      // 使用nextTick确保所有watch执行完毕后再重建图表选项
      // 必须先设置 enabledRaw = true，这样图表容器才会被挂载到DOM
      enabledRaw.value = true
      nextTick(() => {
        // 再次 nextTick 确保 v-else 条件下的图表容器已经挂载
        nextTick(() => {
          rebuildChartOptions()
        })
      })

      selectedNode.value = { ...(node as any), id: nodeId }
    } else {
      message.error(res?.message || '获取数据失败')
    }
  } catch (e: unknown) {
    message.error((e as Error)?.message || '获取数据失败')
  } finally {
    loading.value = false
    loading2.value = false
  }
}

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
    if (chart3Ref.value) {
      if (!chart3Instance) {
        chart3Instance = initEChart(chart3Ref.value, chart3Option.value)
      } else {
        updateEChart(chart3Instance, chart3Option.value)
      }
    }
    if (chart4Ref.value) {
      if (!chart4Instance) {
        chart4Instance = initEChart(chart4Ref.value, chart4Option.value)
      } else {
        updateEChart(chart4Instance, chart4Option.value)
      }
    }
    resizeCharts()
  })
}

// 导出功能占位，防止报错
function exportExcel() {
  showSaveModal.value = true
}

function handleSaveOk() {
  // 校验表单
  saveFormRef.value
    .validate()
    .then(() => {
      // todo: 调用后端保存
      //   console.log('handleSaveOk:', saveForm.value.fileName)
      // 这里处理保存逻辑
      showSaveModal.value = false
      // 清空表单
      saveForm.value.fileName = ''
    })
    .catch(() => {})
}

function handleSaveCancel() {
  showSaveModal.value = false
}

const onTagChange1 = (value: string[]) => {
  console.log('onTagChange1:', value)
  testSetTags.value = value
  // 更新最大曲线数量，至少为1
  maxLenCurve.value = Math.max(1, value.length, testSetTags2.value.length)
  rebuildChartOptions()
}
const onTagChange2 = (value: string[]) => {
  console.log('onTagChange2:', value)
  testSetTags2.value = value
  // 更新最大曲线数量，至少为1
  maxLenCurve.value = Math.max(1, testSetTags.value.length, value.length)
  rebuildChartOptions()
}

// 特征1图标按钮点击事件
const handleFeature1IconClick = () => {
  console.log('特征1图标按钮被点击')
  showFeature1Modal.value = true
}

// 特征2图标按钮点击事件
const handleFeature2IconClick = () => {
  console.log('特征2图标按钮被点击')
  showFeature2Modal.value = true
}

// 特征1弹窗事件处理
const handleFeature1ModalOk = () => {
  console.log('特征1弹窗确定')

  // 根据当前激活的tab进行不同的处理
  if (activeTab.value === 'indicators') {
    // 指标属性表单验证
    indicatorsFormRef.value
      .validate()
      .then(() => {
        console.log('values', indicatorsForm)
        rebuildChartOptions()
        message.success('指标属性配置已更新，图表已刷新')
        showFeature1Modal.value = false
      })
      .catch((err) => {
        console.log('error:', err)
      })
  } else if (activeTab.value === 'channels') {
    // 获取表单实例
    console.log('channelsForm', channelsForm)
    channelsFormRef.value
      .validate()
      .then(() => {
        console.log('values', channelsForm)
        rebuildChartOptions()
        message.success('道属性配置已更新，图表已刷新')
        showFeature1Modal.value = false
      })
      .catch((err: unknown) => {
        console.log('error:', err)
      })
  }
}

// 新的统一弹窗保存回调 - 特征1 指标
const onFeature1SaveIndicators = (form: Record<string, any>) => {
  Object.keys(indicatorsForm).forEach((k) => delete (indicatorsForm as any)[k])
  Object.entries(form || {}).forEach(([k, v]) => ((indicatorsForm as any)[k] = v))
  rebuildChartOptions()
  message.success('指标属性配置已更新，图表已刷新')
}

// 新的统一弹窗保存回调 - 特征1 道
const onFeature1SaveChannels = (form: any) => {
  Object.keys(channelsForm).forEach((k) => delete (channelsForm as any)[k])
  Object.assign(channelsForm, form || {})
  rebuildChartOptions()
  message.success('道属性配置已更新，图表已刷新')
}

// 新的统一弹窗保存回调 - 特征2 指标
const onFeature2SaveIndicators = (form: Record<string, any>) => {
  Object.keys(indicatorsForm2).forEach((k) => delete (indicatorsForm2 as any)[k])
  Object.entries(form || {}).forEach(([k, v]) => ((indicatorsForm2 as any)[k] = v))
  rebuildChartOptions()
  message.success('指标属性配置已更新，图表已刷新')
}

// 新的统一弹窗保存回调 - 特征2 道
const onFeature2SaveChannels = (form: any) => {
  Object.keys(channelsForm2).forEach((k) => delete (channelsForm2 as any)[k])
  Object.assign(channelsForm2, form || {})
  rebuildChartOptions()
  message.success('道属性配置已更新，图表已刷新')
}

const handleFeature2ModalOk = () => {
  console.log('特征2弹窗确定')
  console.log('~~~~~~~:', activeTab2.value)
  // 根据当前激活的tab进行不同的处理
  if (activeTab2.value === 'indicators2') {
    // 指标属性表单验证
    indicatorsFormRef2.value
      .validate()
      .then(() => {
        console.log('values', indicatorsForm2)
        rebuildChartOptions()
        message.success('指标属性配置已更新，图表已刷新')
        showFeature2Modal.value = false
      })
      .catch((err: unknown) => {
        console.log('error:', err)
      })
  } else if (activeTab2.value === 'channels2') {
    // 获取表单实例
    console.log('channelsForm2', channelsForm2)
    channelsFormRef2.value
      .validate()
      .then(() => {
        console.log('values', channelsForm2)
        rebuildChartOptions()
        message.success('道属性配置已更新，图表已刷新')
        showFeature2Modal.value = false
      })
      .catch((err: unknown) => {
        console.log('error:', err)
      })
  }
}

const handleFeature1ModalCancel = () => {
  console.log('特征1弹窗取消')
  showFeature1Modal.value = false
}

const handleFeature2ModalCancel = () => {
  console.log('特征2弹窗取消')
  showFeature2Modal.value = false
}

// 图标悬停事件
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

// 提交时传 selectedPreprocess.value 给后端即可

const handleColorChange2 = (event: Event, tag: string) => {
  const target = event.target as HTMLInputElement
  const hexColor = target.value

  // 直接存储十六进制颜色值
  indicatorsForm2[tag].color = hexColor
}
</script>
<style scoped>
/* 特征1弹窗样式 */
.feature-modal-content {
  display: flex;
  flex-direction: column;
  min-height: 300px;
  /* max-height: 600px; */
}

.horizontal-anchor-nav {
  padding-bottom: 16px;
  /* border-bottom: 1px solid #f0f0f0; */
  margin-bottom: 16px;
}

:deep(.ant-anchor-link-title) {
  color: #595959;
  transition: color 0.3s;
  padding: 8px 16px;
  border-radius: 4px;
  margin-right: 8px;
}

:deep(.ant-anchor-link-title:hover) {
  color: #1890ff;
  background-color: #f0f8ff;
}

:deep(.ant-anchor-link-title.active) {
  color: #1890ff;
  font-weight: 500;
  background-color: #e6f7ff;
}

:deep(.ant-anchor-horizontal) {
  display: flex;
  align-items: center;
}

/* 指标属性表单网格样式 */
.form-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  /* padding: 16px 0; */
}

.form-grid .ant-form-item {
  margin-bottom: 0;
}

.form-grid .ant-form-item-label {
  padding-bottom: 4px;
}

.form-grid .ant-form-item-label > label {
  font-size: 14px;
  color: #262626;
  font-weight: 500;
}

/* 道属性表单网格样式 - 两个item为一行 */
.channels-form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.channels-form-grid .ant-form-item {
  margin-bottom: 0;
}

.channels-form-grid .ant-form-item-label {
  padding-bottom: 4px;
}

.channels-form-grid .ant-form-item-label > label {
  font-size: 14px;
  color: #262626;
  font-weight: 500;
}

.content-area {
  flex: 1;
  overflow-y: auto;
  min-height: 200px;
}

/* .tab-content {
  padding: 16px 0;
} */

/* .tab-content h3 {
  margin-bottom: 16px;
  color: #262626;
  font-size: 16px;
  font-weight: 600;
} */

.tab-content p {
  margin-bottom: 12px;
  color: #595959;
  line-height: 1.6;
}

.tab-content ul {
  padding-left: 20px;
}

.tab-content li {
  margin-bottom: 8px;
  color: #595959;
  line-height: 1.5;
}

.preview-panel {
  flex: 1;
  padding: 16px;
  background: #f0f2f5;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  min-height: 100%;
}
.preprocess-select-card {
  width: 100%;
  min-width: 320px;
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
  padding-left: 20px;
  background: #f5f7fa;
  border-top-left-radius: 2px;
  border-top-right-radius: 2px;
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
  gap: 12px;
  margin-left: auto;
}
.preprocess-select-content {
  display: flex;
  align-items: flex-start;
  padding: 24px;
  gap: 24px;
  justify-content: space-between;
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
  height: 1150px;
  display: flex;
  gap: 24px;
}
/* 预处理半卡片 - 统一工业风格 */
.preprocess-half-card {
  flex: 0 0 calc(50% - 12px);
  width: calc(50% - 12px);
  min-width: 0;
  background: var(--bg-primary);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  margin-bottom: 0;
  height: 100%;
  transition: var(--transition-base);
  overflow: hidden;
}

.preprocess-half-card:hover {
  box-shadow: var(--shadow-md);
  border-color: var(--border-color-hover);
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
  gap: var(--spacing-2xl);
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

/* 值组 */
.preprocess-value-group {
  border: 1px solid var(--border-color);
  padding: var(--spacing-xs) var(--spacing-2xl);
  background: var(--bg-primary);
  min-height: 32px;
  display: flex;
  align-items: center;
  border-radius: var(--radius-md);
  white-space: nowrap;
  transition: var(--transition-fast);
}

.preprocess-value-group:hover {
  border-color: var(--primary-lighter);
}

.preprocess-value-group-wrap {
  display: flex;
  gap: var(--spacing-md);
  flex-wrap: wrap;
}

.preprocess-value-group.selectable {
  cursor: pointer;
  transition: var(--transition-base);
}

.preprocess-value-group.selectable.selected {
  border: 2px solid var(--primary-color);
  background: rgba(26, 77, 143, 0.08);
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
  gap: 16px;
  padding: 12px;
  background: #f5f7fa;
  height: 60px;
}
/* 分组块样式 */
.preprocess-group-block {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  color: #000000d9;
  .hover:hover {
    border: 1px solid #3f9bfd;
    color: #3f9bfd;
  }
}
/* 图表行 - 统一工业风格 */
.echarts-row {
  display: flex;
  width: 100%;
  gap: var(--spacing-lg);
  height: 1050px;
  position: relative;
}

.echart-col {
  display: flex;
  flex-direction: column;
  width: calc(50% - var(--spacing-lg) / 2);
  height: 1020px;
  box-sizing: border-box;
  background: var(--bg-primary);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-color);
  padding: var(--spacing-md);
  justify-content: flex-start;
  transition: var(--transition-base);
}

.echart-col:hover {
  box-shadow: var(--shadow-md);
  border-color: var(--primary-lighter);
}

/* 图表容器 - 确保有固定高度 */
.chart-container {
  width: 100%;
  height: 930px;
  flex: 1;
}

.echart-half {
  flex: 1;
  width: 100%;
  min-height: 0;
  min-width: 0;
  position: relative;
  box-sizing: border-box;
}

.echart-all {
  flex: 1;
  width: 100%;
  min-height: 0;
  min-width: 0;
  box-sizing: border-box;
}

.chart-toolbar {
  display: flex;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-xs);
  align-items: center;
}

.chart-toolbar.chart-toolbar-top {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-xs);
  width: 100%;
}

/* 图表缩放按钮 */
.chart-zoom-btn {
  background: var(--bg-primary);
  border: 1px solid var(--primary-color);
  border-radius: var(--radius-sm);
  padding: var(--spacing-xs) var(--spacing-md);
  font-size: 13px;
  color: var(--primary-color);
  cursor: pointer;
  box-shadow: var(--shadow-xs);
  user-select: none;
  transition: var(--transition-base);
  display: inline-block;
}

.chart-zoom-btn:hover {
  background: rgba(26, 77, 143, 0.08);
  box-shadow: var(--shadow-sm);
}
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
}

/* 输入参数表三列布局样式 */
.input-params-form {
  width: 100%;
}

.input-params-container {
  display: flex;
  width: 100%;
  gap: 16px;
}

/* 参数列 - 统一工业风格 */
.param-column {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  overflow: hidden;
}

/* 参数列头部 - 工业风格（完整四边框） */
.param-column-header {
  background: var(--bg-tertiary);
  padding: var(--spacing-md) var(--spacing-lg);
  text-align: center;
  position: relative;
  border-left: 4px solid var(--primary-color);
  border-right: 3px solid var(--primary-color);
  border-bottom: 2px solid var(--primary-color);
}

/* 顶部渐变装饰条 */
.param-column-header::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--primary-color) 0%, var(--primary-light) 100%);
}

.param-column-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.param-column-content {
  padding: var(--spacing-lg);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.param-group {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: var(--spacing-md);
}

.param-group-label {
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 500;
  min-width: 80px;
  flex-shrink: 0;
}

.range-inputs {
  display: flex;
  align-items: center;
  gap: 8px;
}

.range-separator {
  color: #8c8c8c;
  font-weight: 500;
  flex-shrink: 0;
}

/* 输入控件样式 */
.param-group .ant-select,
.param-group .ant-input-number {
  flex: 1;
  min-width: 0;
}

/* 表单项样式调整 */
.param-column .ant-form-item {
  margin-bottom: 16px;
}

.param-column .ant-form-item-label {
  padding-bottom: 8px;
}

.param-column .ant-form-item-label > label {
  font-size: 13px;
  color: #595959;
  font-weight: 500;
  margin: 0;
}

/* 范围输入特殊处理 */
.range-inputs {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.range-inputs .ant-input-number {
  flex: 1;
  min-width: 0;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .input-params-container {
    flex-direction: column;
    gap: 16px;
  }
}
</style>
