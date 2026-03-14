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
          <a-anchor-link href="#channels" title="道属性" />
        </a-anchor>
      </div>
      <div class="content-area">
        <div id="channels" class="tab-content">
          <a-form layout="vertical" ref="formRef" :model="localForm">
            <div style="flex: 1; overflow-y: auto">
              <div class="channels-form-grid">
                <a-form-item
                  label="对数刻度绘制曲线"
                  name="logarithmicScale"
                  :rules="[{ required: true, message: '请选择' }]"
                >
                  <a-select
                    v-model:value="localForm.logarithmicScale"
                    placeholder="请选择"
                    style="width: 100%"
                  >
                    <a-select-option value="true">是</a-select-option>
                    <a-select-option value="false">否</a-select-option>
                  </a-select>
                </a-form-item>
              </div>
              <a-form-item style="width: 100%; margin-top: 20px">
                <a-checkbox v-model:checked="localForm.showScaleLines">显示刻度线</a-checkbox>
              </a-form-item>
              <div class="channels-form-grid">
                <a-form-item
                  label="细线"
                  name="thinLine"
                  :rules="[{ required: true, message: '请选择' }]"
                >
                  <a-select
                    v-model:value="localForm.thinLine"
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
                    v-model:value="localForm.thinLineCount"
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
                    v-model:value="localForm.thickLine"
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
                    v-model:value="localForm.thickLineCount"
                    :min="1"
                    :max="10"
                    style="width: 100%"
                  />
                </a-form-item>
              </div>
              <a-form-item style="width: 100%; margin-top: 10px">
                <a-checkbox v-model:checked="localForm.showDepthLines">显示深度线</a-checkbox>
              </a-form-item>
              <div class="channels-form-grid">
                <a-form-item
                  label="细线"
                  name="depthThinLine"
                  :rules="[{ required: true, message: '请选择' }]"
                >
                  <a-select
                    v-model:value="localForm.depthThinLine"
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
                    v-model:value="localForm.depthInterval"
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
                    v-model:value="localForm.depthThickLine"
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
                    v-model:value="localForm.depthThickInterval"
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

const props = withDefaults(
  defineProps<{
    open: boolean
    formModel: {
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
  }>(),
  {
    width: '800px',
    bodyHeight: '600px',
  }
)

const emit = defineEmits<{
  (e: 'update:open', v: boolean): void
  (e: 'save', form: any): void
  (e: 'cancel'): void
}>()

const innerOpen = ref(props.open)
watch(
  () => props.open,
  (v) => (innerOpen.value = v)
)
watch(innerOpen, (v) => emit('update:open', v))

const formRef = ref()
const localForm = reactive<any>({})

watch(
  () => props.formModel,
  (v) => {
    Object.keys(localForm).forEach((k) => delete localForm[k])
    Object.assign(localForm, v || {})
  },
  { immediate: true, deep: true }
)

function handleOk() {
  formRef.value
    .validate?.()
    ?.then?.(() => {
      emit('save', JSON.parse(JSON.stringify(localForm)))
      innerOpen.value = false
    })
    ?.catch?.(() => {})
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
</style>
