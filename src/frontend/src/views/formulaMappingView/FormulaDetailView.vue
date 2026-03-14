<template>
  <div class="preview-panel">
    <div class="preprocess-select-card" style="height: 116px">
      <div class="preview-title">
        <span>数据处理</span>
      </div>
      <div class="preprocess-select-content">
        <a-form layout="inline" class="model-select-row" style="width: 100%">
          <a-form-item
            class="select-item"
            style="flex: 1; padding: 0; margin-bottom: 0; border: none"
          >
            <div style="display: flex; align-items: center; width: 100%; gap: 8px">
              <span class="select-label">异常深度剔除(m)：</span>
              <a-tree-select
                v-model:value="selectedData"
                :tree-data="dataOptions"
                :field-names="{ label: 'label', value: 'value', children: 'children' }"
                placeholder="请输入值，以逗号隔开4400,4100"
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
          <a-form-item class="button-group" style="display: flex; align-items: center">
            <a-button type="primary" @click="handleShowLog" style="margin-left: 12px"
              >确认</a-button
            >
          </a-form-item>
        </a-form>
      </div>
    </div>
    <div class="preprocess-select-card">
      <div class="preview-title">
        <span>{{ formula?.name }}</span>
      </div>
      <div class="preprocess-select-content">
        <div v-if="loading" class="loading-container">
          <a-spin size="large" />
          <p style="margin-top: 8px; color: #666">加载中...</p>
        </div>
        <img
          v-else-if="formula?.picture"
          :src="formula.picture"
          alt="公式图片"
          class="formula-image"
        />
        <p v-else>{{ formula?.description || '暂无图片' }}</p>
      </div>
    </div>
    <div class="preprocess-select-card">
      <div
        class="preview-title"
        style="display: flex; justify-content: space-between; align-items: center"
      >
        <span>公式映射图</span>
        <a-button type="primary" style="margin-left: 8px" @click="openSaveModal">保存结果</a-button>
      </div>
      <div class="preprocess-select-content" style="width: 100%">
        <div v-if="loading" class="loading-container">
          <a-spin size="large" />
          <p style="margin-top: 8px; color: #666">加载中...</p>
        </div>
        <img v-else-if="formulaImage" :src="formulaImage" alt="公式映射图" class="formula-image" />
        <div v-else class="no-image-placeholder">
          <p style="color: #999; text-align: center">暂无映射图</p>
        </div>
      </div>
    </div>

    <!-- 保存结果弹窗 -->
    <a-modal
      v-model:open="saveModalVisible"
      title="保存结果"
      :confirm-loading="saving"
      @ok="handleSaveOk"
      @cancel="handleSaveCancel"
      ok-text="确定"
      cancel-text="取消"
    >
      <div style="display: flex; align-items: center; gap: 12px; width: 100%">
        <span style="white-space: nowrap; font-size: 14px; color: #666">公式名称：</span>
        <a-input
          v-model:value="saveName"
          placeholder="例如：公式1"
          :maxlength="50"
          allow-clear
          style="flex: 1"
        />
      </div>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, inject, onMounted, onActivated } from 'vue'
import EchartCard from '@/components/echarts/EchartCard.vue'
import type { EChartsOption } from 'echarts'
import { getFormulaSpecificImage } from '@/utils/api'

// 注入面包屑更新方法
const setFormulaBreadcrumb = inject('setFormulaBreadcrumb') as (formulaName: string) => void
const backToFormulaList = inject('backToFormulaList') as () => void

// 图片数据
const formulaImage = ref<string>('')
const loading = ref(false)

// 定义props
interface Props {
  formula: {
    id: number
    name: string
    description: string
    picture: string
  } | null
}

const props = defineProps<Props>()

// 定义emits
const emit = defineEmits<{
  backToList: []
  editFormula: [formula: { id: number; name: string; description: string }]
  deleteFormula: [formula: { id: number; name: string; description: string }]
  saveFormula: [payload: { name: string }]
}>()

// ====== 兼容上方表单需要的ref与方法（占位，防止linter错误） ======
const selectedData = ref<string | undefined>()
const dataOptions = ref<any[]>([])
const onSelect = (_value: string) => {}
const handleShowLog = () => {}
// ==========================================================

// 示例图表 option，可替换为真实数据
const demoOption = ref<EChartsOption>({
  tooltip: { trigger: 'axis' },
  xAxis: { type: 'category', data: ['A', 'B', 'C', 'D', 'E'] },
  yAxis: { type: 'value' },
  series: [{ name: '示例', type: 'line', data: [5, 20, 36, 10, 10] }],
})

// 保存结果弹窗状态
const saveModalVisible = ref(false)
const saveName = ref('')
const saving = ref(false)

onActivated(async () => {
  if (props.formula) {
    await loadFormulaImage()
  }
})

// 加载公式图片
const loadFormulaImage = async () => {
  if (!props.formula?.id) return
  loading.value = true
  try {
    const res = (await getFormulaSpecificImage({ id: props.formula.id })) as any
    if (res?.code === 200) {
      formulaImage.value = `data:image/png;base64,${res.data.formula_image.data.picture}`
    }
  } catch (error) {
    console.error('加载公式图片失败:', error)
  } finally {
    loading.value = false
  }
}

const openSaveModal = () => {
  saveName.value = props.formula?.name || ''
  saveModalVisible.value = true
}

const handleSaveOk = async () => {
  if (!saveName.value || !saveName.value.trim()) {
    // 简单校验，避免空名称
    return
  }
  saving.value = true
  try {
    // 这里可调用后端接口保存，当前先触发事件给父级
    emit('saveFormula', { name: saveName.value.trim() })
    saveModalVisible.value = false
  } finally {
    saving.value = false
  }
}

const handleSaveCancel = () => {
  saveModalVisible.value = false
}

// 返回公式列表
const handleBackToList = () => {
  // 清除面包屑中的公式名称
  setFormulaBreadcrumb('')
  // 触发返回事件
  emit('backToList')
}

// 编辑公式
const handleEditFormula = () => {
  if (props.formula) {
    console.log('编辑公式:', props.formula.name)
    emit('editFormula', props.formula)
  }
}

// 删除公式
const handleDeleteFormula = () => {
  if (props.formula) {
    console.log('删除公式:', props.formula.name)
    emit('deleteFormula', props.formula)
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
}
.preprocess-select-card {
  width: 100%;
  min-width: 320px;
  /* height: 116px; */
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
  margin-left: auto;
}
/* .add-model-btn {
  min-width: 96px;
  font-size: 14px;
  font-weight: 500;
  display: flex;
  align-items: center;
  justify-content: center;
} */
.preprocess-select-content {
  flex: 1;
  display: flex;
  align-items: center;
  padding: 0 24px;
  gap: 24px;
  justify-content: space-between;
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
  padding: 24px;
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
  font-size: 16px;
  color: #5a5a68;
  min-width: 80px;
  font-weight: 400;
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
.file-preview-card {
  width: 100%;
  min-width: 0;
}
:deep(.ant-btn),
:deep(.ant-btn-primary),
:deep(.ant-btn-default),
:deep(.ant-btn-dangerous) {
  border-radius: 0 !important;
}
.param-modal-vertical2 {
  display: flex;
  flex-direction: row;
  gap: 24px;
  margin-top: 16px;
  background: #fff;
  border-radius: 2px;
  width: 100%;
  box-sizing: border-box;
}
.param-modal-col2 {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  /* gap: 12px; */
}
.param-block {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  background: #fff;
  padding: 0 0 12px 0;
  border: none;
}
.param-label2 {
  color: #000;
  font-size: 14px;
  font-weight: 400;
  text-align: left;
  padding: 0 0 4px 0;
  background: #fff;
  word-break: break-all;
  line-height: 22px;
}
.param-value2 {
  color: #333;
  font-size: 14px;
  line-height: 24px;
  background: #fff;
  word-break: break-all;
}
.param-block-row {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  gap: 0;
  padding-bottom: 12px;
}
.param-block-row .param-label2,
.param-block-row .param-value2 {
  width: auto;
  min-width: 80px;
  padding-right: 12px;
  padding-left: 0;
  padding-top: 0;
  padding-bottom: 0;
  display: flex;
  align-items: center;
}
/* .param-block-row .param-label2 {
  color: #999;
  font-size: 12px;
  font-weight: 400;
} */
.param-block-row .param-value2 {
  color: #333;
  font-size: 14px;
  line-height: 24px;
}
.param-label-full {
  width: 100%;
  display: block;
  margin-bottom: 4px;
}
.param-select-full {
  width: 100%;
  margin-bottom: 0;
}
.icon-wrapper {
  display: inline-flex;
  align-items: center;
  margin-left: 6px;
  vertical-align: middle;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  width: 100%;
}

.no-image-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 200px;
  width: 100%;
  background: #f5f5f5;
  border: 1px dashed #d9d9d9;
  border-radius: 4px;
}

.formula-image {
  width: 100%;
  height: auto;
  max-height: 300px;
  object-fit: contain;
  display: block;
  border-radius: 4px;
}
</style>
