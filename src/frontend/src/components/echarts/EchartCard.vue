<template>
  <div class="echart-card">
    <!-- <div class="echart-card-header"> -->
    <div class="echart-card-title">{{ title }}</div>
    <div class="echart-card-actions">
      <slot name="actions"></slot>
    </div>
    <!-- </div> -->
    <div class="echart-card-body" :style="height ? { height } : undefined">
      <div ref="chartRef" class="echart-container"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import type { ECharts, EChartsOption } from 'echarts'

const props = withDefaults(
  defineProps<{
    title?: string
    option: EChartsOption
    height?: string
    theme?: string | object
    autoResize?: boolean
  }>(),
  {
    title: '',
    autoResize: true,
  }
)

const chartRef = ref<HTMLDivElement | null>(null)
let chart: ECharts | null = null

const initChart = () => {
  if (!chartRef.value) return
  chart = echarts.init(chartRef.value, props.theme)
  chart.setOption(props.option, true)
}

const disposeChart = () => {
  if (chart) {
    chart.dispose()
    chart = null
  }
}

const resize = () => {
  chart?.resize()
}

// 暴露手动resize能力
defineExpose({ resize })

onMounted(() => {
  initChart()
  if (props.autoResize) {
    window.addEventListener('resize', resize)
  }
})

onBeforeUnmount(() => {
  if (props.autoResize) {
    window.removeEventListener('resize', resize)
  }
  disposeChart()
})

// 深监听 option 变化
watch(
  () => props.option,
  async (val) => {
    if (!val) return
    await nextTick()
    if (!chart) {
      initChart()
    } else {
      chart.setOption(val, true)
    }
  },
  { deep: true }
)
</script>

<style scoped>
.echart-card {
  background: #fff;
  /* border-radius: 2px; */
  /* box-shadow: 0px 0px 12px 0px #00000040; */
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  box-sizing: border-box;
}
.echart-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 60px;
  padding: 12px;
  background: #f5f7fa;
  border-top-left-radius: 2px;
  border-top-right-radius: 2px;
}
.echart-card-title {
  font-size: 16px;
  font-weight: 700;
  color: #161b25;
}
.echart-card-body {
  width: 100%;
  flex: 1;
  min-height: 0;
  box-sizing: border-box;
}
.echart-container {
  width: 100%;
  height: 100%;
  box-sizing: border-box;
}
</style>
