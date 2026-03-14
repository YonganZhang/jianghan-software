<template>
  <a-modal
    v-model:open="innerOpen"
    :width="width"
    :footer="null"
    :bodyStyle="{ height: bodyHeight }"
  >
    <div class="feature-modal-content">
      <div class="horizontal-anchor-nav">
        <a-anchor direction="horizontal">
          <a-anchor-link
            href="#indicators"
            title="指标属性"
            :class="{ active: activeTab === 'indicators' }"
            @click="activeTab = 'indicators'"
          />
          <a-anchor-link
            href="#channels"
            title="道属性"
            :class="{ active: activeTab === 'channels' }"
            @click="activeTab = 'channels'"
          />
        </a-anchor>
      </div>

      <div class="content-area">
        <div v-if="activeTab === 'indicators'" id="indicators" class="tab-content">
          <a-form
            :model="localIndicatorsForm"
            layout="vertical"
            ref="indicatorsFormRef"
            style="height: 100%; display: flex; flex-direction: column"
          >
            <div class="form-grid" style="flex: 1; overflow-y: auto">
              <template v-for="(tag, idx) in tags" :key="idx">
                <a-form-item
                  :label="`${tag}线条`"
                  :name="[tag, 'lineStyle']"
                  :rules="[{ required: true, message: '请选择线条样式' }]"
                >
                  <a-select
                    v-model:value="localIndicatorsForm[tag].lineStyle"
                    :placeholder="`请选择${tag}线条`"
                    style="width: 100%"
                  >
                    <a-select-option value="solid">
                      <div style="display: flex; align-items: center; gap: 8px">
                        <span>实线</span>
                        <div
                          style="width: 40px; height: 2px; background: #333; border-radius: 1px"
                        ></div>
                      </div>
                    </a-select-option>
                    <a-select-option value="dashed">
                      <div style="display: flex; align-items: center; gap: 8px">
                        <span>虚线</span>
                        <div
                          style="
                            width: 40px;
                            height: 2px;
                            background: repeating-linear-gradient(
                              to right,
                              #333 0,
                              #333 4px,
                              transparent 4px,
                              transparent 8px
                            );
                            border-radius: 1px;
                          "
                        ></div>
                      </div>
                    </a-select-option>
                    <a-select-option value="dotted">
                      <div style="display: flex; align-items: center; gap: 8px">
                        <span>点线</span>
                        <div
                          style="
                            width: 40px;
                            height: 2px;
                            background: repeating-linear-gradient(
                              to right,
                              #333 0,
                              #333 2px,
                              transparent 2px,
                              transparent 4px
                            );
                            border-radius: 1px;
                          "
                        ></div>
                      </div>
                    </a-select-option>
                  </a-select>
                </a-form-item>
                <a-form-item
                  :label="`${tag}颜色`"
                  :name="[tag, 'color']"
                  :rules="[{ required: true, message: '请选择颜色' }]"
                >
                  <div style="display: flex; align-items: center; gap: 8px">
                    <a-input
                      v-model:value="localIndicatorsForm[tag].color"
                      :placeholder="`请输入${tag}颜色-16进制`"
                      style="flex: 1"
                    />
                    <input
                      type="color"
                      :value="localIndicatorsForm[tag].color || '#000000'"
                      @input="(e:any)=>onColorInput(e, tag)"
                      style="
                        width: 40px;
                        height: 32px;
                        border: 1px solid #d9d9d9;
                        border-radius: 4px;
                        cursor: pointer;
                      "
                    />
                  </div>
                </a-form-item>
                <a-form-item
                  :label="`${tag}坐标范围`"
                  :name="[tag, 'range']"
                  :rules="[
                    { required: true, message: '请输入坐标范围' },
                    { validator: validateRange },
                  ]"
                >
                  <div style="display: flex; align-items: center; gap: 8px">
                    <a-input-number
                      v-model:value="localIndicatorsForm[tag].range![0]"
                      :placeholder="`最小值`"
                      style="flex: 1"
                    />
                    <span style="color: #666; font-size: 14px; white-space: nowrap">-</span>
                    <a-input-number
                      v-model:value="localIndicatorsForm[tag].range![1]"
                      :placeholder="`最大值`"
                      style="flex: 1"
                    />
                  </div>
                </a-form-item>
              </template>
            </div>
            <div style="margin-top: auto; text-align: right; padding-top: 16px">
              <a-button @click="handleCancel" style="margin-right: 8px">取消</a-button>
              <a-button type="primary" @click="handleOk"> 确定 </a-button>
            </div>
          </a-form>
        </div>

        <div v-else id="channels" class="tab-content">
          <a-form layout="vertical" ref="channelsFormRef" :model="localChannelsForm">
            <div style="flex: 1; overflow-y: auto">
              <div class="channels-form-grid">
                <a-form-item
                  label="对数刻度绘制曲线"
                  name="logarithmicScale"
                  :rules="[{ required: true, message: '请选择' }]"
                >
                  <a-select
                    v-model:value="localChannelsForm.logarithmicScale"
                    placeholder="请选择"
                    style="width: 100%"
                  >
                    <a-select-option value="true">是</a-select-option>
                    <a-select-option value="false">否</a-select-option>
                  </a-select>
                </a-form-item>
              </div>
              <a-form-item style="width: 100%; margin-top: 20px">
                <a-checkbox v-model:checked="localChannelsForm.showScaleLines"
                  >显示刻度线</a-checkbox
                >
              </a-form-item>
              <div class="channels-form-grid">
                <a-form-item
                  label="细线"
                  name="thinLine"
                  :rules="[{ required: true, message: '请选择' }]"
                >
                  <a-select
                    v-model:value="localChannelsForm.thinLine"
                    placeholder="请选择"
                    style="width: 100%"
                  >
                    <a-select-option value="1"
                      ><div class="line-demo" style="height: 1px"></div>
                      1px</a-select-option
                    >
                    <a-select-option value="2"
                      ><div class="line-demo" style="height: 2px"></div>
                      2px</a-select-option
                    >
                    <a-select-option value="3"
                      ><div class="line-demo" style="height: 3px"></div>
                      3px</a-select-option
                    >
                    <a-select-option value="4"
                      ><div class="line-demo" style="height: 4px"></div>
                      4px</a-select-option
                    >
                    <a-select-option value="5"
                      ><div class="line-demo" style="height: 5px"></div>
                      5px</a-select-option
                    >
                  </a-select>
                </a-form-item>
                <a-form-item
                  label="份数"
                  name="thinLineCount"
                  :rules="[{ required: true, message: '请输入' }]"
                >
                  <a-input-number
                    v-model:value="localChannelsForm.thinLineCount"
                    :min="1"
                    :max="10"
                    style="width: 100%"
                  />
                </a-form-item>
                <a-form-item
                  label="粗线"
                  name="thickLine"
                  :rules="[{ required: true, message: '请选择' }]"
                >
                  <a-select
                    v-model:value="localChannelsForm.thickLine"
                    placeholder="请选择"
                    style="width: 100%"
                  >
                    <a-select-option value="1"
                      ><div class="line-demo" style="height: 1px"></div>
                      1px</a-select-option
                    >
                    <a-select-option value="2"
                      ><div class="line-demo" style="height: 2px"></div>
                      2px</a-select-option
                    >
                    <a-select-option value="3"
                      ><div class="line-demo" style="height: 3px"></div>
                      3px</a-select-option
                    >
                    <a-select-option value="4"
                      ><div class="line-demo" style="height: 4px"></div>
                      4px</a-select-option
                    >
                    <a-select-option value="5"
                      ><div class="line-demo" style="height: 5px"></div>
                      5px</a-select-option
                    >
                  </a-select>
                </a-form-item>
                <a-form-item
                  label="份数"
                  name="thickLineCount"
                  :rules="[{ required: true, message: '请输入' }]"
                >
                  <a-input-number
                    v-model:value="localChannelsForm.thickLineCount"
                    :min="1"
                    :max="10"
                    style="width: 100%"
                  />
                </a-form-item>
              </div>
              <a-form-item style="width: 100%; margin-top: 10px">
                <a-checkbox v-model:checked="localChannelsForm.showDepthLines"
                  >显示深度线</a-checkbox
                >
              </a-form-item>
              <div class="channels-form-grid">
                <a-form-item
                  label="细线"
                  name="depthThinLine"
                  :rules="[{ required: true, message: '请选择' }]"
                >
                  <a-select
                    v-model:value="localChannelsForm.depthThinLine"
                    placeholder="请选择"
                    style="width: 100%"
                  >
                    <a-select-option value="1"
                      ><div class="line-demo" style="height: 1px"></div>
                      1px</a-select-option
                    >
                    <a-select-option value="2"
                      ><div class="line-demo" style="height: 2px"></div>
                      2px</a-select-option
                    >
                    <a-select-option value="3"
                      ><div class="line-demo" style="height: 3px"></div>
                      3px</a-select-option
                    >
                    <a-select-option value="4"
                      ><div class="line-demo" style="height: 4px"></div>
                      4px</a-select-option
                    >
                    <a-select-option value="5"
                      ><div class="line-demo" style="height: 5px"></div>
                      5px</a-select-option
                    >
                  </a-select>
                </a-form-item>
                <a-form-item
                  label="间隔(m)"
                  name="depthInterval"
                  :rules="[{ required: true, message: '请输入' }]"
                >
                  <a-input-number
                    v-model:value="localChannelsForm.depthInterval"
                    :min="1"
                    :max="10"
                    style="width: 100%"
                  />
                </a-form-item>
                <a-form-item
                  label="粗线"
                  name="depthThickLine"
                  :rules="[{ required: true, message: '请选择' }]"
                >
                  <a-select
                    v-model:value="localChannelsForm.depthThickLine"
                    placeholder="请选择"
                    style="width: 100%"
                  >
                    <a-select-option value="1"
                      ><div class="line-demo" style="height: 1px"></div>
                      1px</a-select-option
                    >
                    <a-select-option value="2"
                      ><div class="line-demo" style="height: 2px"></div>
                      2px</a-select-option
                    >
                    <a-select-option value="3"
                      ><div class="line-demo" style="height: 3px"></div>
                      3px</a-select-option
                    >
                    <a-select-option value="4"
                      ><div class="line-demo" style="height: 4px"></div>
                      4px</a-select-option
                    >
                    <a-select-option value="5"
                      ><div class="line-demo" style="height: 5px"></div>
                      5px</a-select-option
                    >
                  </a-select>
                </a-form-item>
                <a-form-item
                  label="间隔(m)"
                  name="depthThickInterval"
                  :rules="[{ required: true, message: '请输入' }]"
                >
                  <a-input-number
                    v-model:value="localChannelsForm.depthThickInterval"
                    :min="1"
                    :max="10"
                    style="width: 100%"
                  />
                </a-form-item>
              </div>
            </div>
            <div style="margin-top: auto; text-align: right; padding-top: 16px">
              <a-button @click="handleCancel" style="margin-right: 8px">取消</a-button>
              <a-button type="primary" @click="handleOk"> 确定 </a-button>
            </div>
          </a-form>
        </div>
      </div>
    </div>
  </a-modal>
</template>

<script setup lang="ts">
import { ref, watch, reactive } from 'vue'
import type { Rule } from 'ant-design-vue/es/form'

const props = withDefaults(
  defineProps<{
    open: boolean
    tags: string[]
    indicatorFormModel: Record<
      string,
      { lineStyle?: string; color?: string; range?: [number, number] }
    >
    channelFormModel: {
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
    width?: string | number
    bodyHeight?: string | number
    defaultActiveTab?: 'indicators' | 'channels'
  }>(),
  {
    width: '800px',
    bodyHeight: '600px',
    defaultActiveTab: 'indicators',
  }
)

watch(
  () => props.bodyHeight,
  (newHeight) => {
    console.log('bodyHeight changed:', newHeight)
  },
  { immediate: true }
)

const emit = defineEmits<{
  (e: 'update:open', v: boolean): void
  (
    e: 'save-indicators',
    form: Record<string, { lineStyle?: string; color?: string; range?: [number, number] }>
  ): void
  (e: 'save-channels', form: any): void
  (e: 'cancel'): void
  (e: 'tab-change', tab: 'indicators' | 'channels'): void
}>()

const innerOpen = ref(props.open)
watch(
  () => props.open,
  (v) => (innerOpen.value = v)
)
watch(innerOpen, (v) => emit('update:open', v))

const activeTab = ref<'indicators' | 'channels'>(props.defaultActiveTab)

// Watch for activeTab changes and emit to parent
watch(activeTab, (newTab) => {
  emit('tab-change', newTab)
})

const indicatorsFormRef = ref()
const channelsFormRef = ref()

const localIndicatorsForm = reactive<
  Record<string, { lineStyle?: string; color?: string; range?: [number, number] }>
>({})
const localChannelsForm = reactive<any>({})

watch(
  () => props.indicatorFormModel,
  (v) => {
    Object.keys(localIndicatorsForm).forEach((k) => delete localIndicatorsForm[k])
    Object.entries(v || {}).forEach(([k, val]) => {
      localIndicatorsForm[k] = { ...(val as any) }
    })
  },
  { immediate: true, deep: true }
)

watch(
  () => props.channelFormModel,
  (v) => {
    Object.keys(localChannelsForm).forEach((k) => delete localChannelsForm[k])
    Object.assign(localChannelsForm, v || {})
  },
  { immediate: true, deep: true }
)

const validateRange: Rule['validator'] = (_, value: unknown) => {
  if (!Array.isArray(value) || value.length !== 2) return Promise.reject('必须输入两个数值')
  if ((value as any).some((v: any) => v === undefined || v === null || v === ''))
    return Promise.reject('坐标不能为空')
  if (Number((value as any)[0]) >= Number((value as any)[1]))
    return Promise.reject('最小值必须小于最大值')
  return Promise.resolve()
}

function onColorInput(e: Event, tag: string) {
  const target = e.target as HTMLInputElement
  if (!localIndicatorsForm[tag]) localIndicatorsForm[tag] = {}
  localIndicatorsForm[tag].color = target.value
}

function handleOk() {
  if (activeTab.value === 'indicators') {
    indicatorsFormRef.value
      ?.validate?.()
      ?.then?.(() => {
        emit('save-indicators', JSON.parse(JSON.stringify(localIndicatorsForm)))
        innerOpen.value = false
      })
      ?.catch?.(() => {})
  } else {
    channelsFormRef.value
      ?.validate?.()
      ?.then?.(() => {
        emit('save-channels', JSON.parse(JSON.stringify(localChannelsForm)))
        innerOpen.value = false
      })
      ?.catch?.(() => {})
  }
}

function handleCancel() {
  emit('cancel')
  innerOpen.value = false
}
</script>

<style scoped>
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
.feature-modal-content {
  display: flex;
  flex-direction: column;
  min-height: 300px;
}
.horizontal-anchor-nav {
  padding-bottom: 16px;
  margin-bottom: 16px;
}
.content-area {
  flex: 1;
  overflow-y: auto;
  min-height: 200px;
}
.form-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}
.form-grid :deep(.ant-form-item) {
  margin-bottom: 0;
}
.channels-form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}
.line-demo {
  width: 40px;
  background: #333;
  border-radius: 1px;
  display: inline-block;
  vertical-align: middle;
  margin-right: 8px;
}
:deep(.ant-anchor-link-title.active) {
  color: #1890ff;
  font-weight: 500;
  background-color: #e6f7ff;
}
</style>
