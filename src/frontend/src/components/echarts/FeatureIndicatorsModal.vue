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
          <a-anchor-link href="#indicators" title="指标属性" />
        </a-anchor>
      </div>
      <div class="content-area">
        <div id="indicators" class="tab-content">
          <a-form
            :model="localForm"
            layout="vertical"
            ref="formRef"
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
                    v-model:value="localForm[tag].lineStyle"
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
                      v-model:value="localForm[tag].color"
                      :placeholder="`请输入${tag}颜色-16进制`"
                      style="flex: 1"
                    />
                    <input
                      type="color"
                      :value="localForm[tag].color || '#000000'"
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
                      v-model:value="localForm[tag].range![0]"
                      :placeholder="`最小值`"
                      style="flex: 1"
                    />
                    <span style="color: #666; font-size: 14px; white-space: nowrap">-</span>
                    <a-input-number
                      v-model:value="localForm[tag].range![1]"
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
    formModel: Record<string, { lineStyle?: string; color?: string; range?: [number, number] }>
    width?: string | number
    bodyHeight?: string | number
  }>(),
  {
    width: '800px',
    bodyHeight: '600px',
  }
)

const emit = defineEmits<{
  (e: 'update:open', v: boolean): void
  (
    e: 'save',
    form: Record<string, { lineStyle?: string; color?: string; range?: [number, number] }>
  ): void
  (e: 'cancel'): void
}>()

const innerOpen = ref(props.open)
watch(
  () => props.open,
  (v) => (innerOpen.value = v)
)
watch(innerOpen, (v) => emit('update:open', v))

const formRef = ref()
const localForm = reactive<
  Record<string, { lineStyle?: string; color?: string; range?: [number, number] }>
>({})

watch(
  () => props.formModel,
  (v) => {
    Object.keys(localForm).forEach((k) => delete localForm[k])
    Object.entries(v || {}).forEach(([k, val]) => {
      localForm[k] = { ...val }
    })
  },
  { immediate: true, deep: true }
)

const validateRange: Rule['validator'] = (_, value: unknown) => {
  if (!Array.isArray(value) || value.length !== 2) return Promise.reject('必须输入两个数值')
  if (value.some((v) => v === undefined || v === null || v === ''))
    return Promise.reject('坐标不能为空')
  if (Number(value[0]) >= Number(value[1])) return Promise.reject('最小值必须小于最大值')
  return Promise.resolve()
}

function onColorInput(e: Event, tag: string) {
  const target = e.target as HTMLInputElement
  localForm[tag].color = target.value
}

function handleOk() {
  formRef.value
    .validate()
    .then(() => {
      emit('save', JSON.parse(JSON.stringify(localForm)))
      innerOpen.value = false
    })
    .catch(() => {})
}

function handleCancel() {
  emit('cancel')
  innerOpen.value = false
}
</script>

<style scoped>
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
</style>
