import * as echarts from 'echarts'

export const colorArray = [
  '#00B050',
  '#009966',
  '#00B0B0',
  '#0090C0',
  '#0070C0',
  '#4050C0',
  '#8040C0',
  '#A02090',
  '#C000B0',
  '#C00070',
]

export interface EChartSeries {
  name: string
  type: string
  xAxisIndex?: number
  yAxisIndex?: number
  data: any[]
  lineStyle?: object
  itemStyle?: object
  symbol?: string
  showSymbol?: boolean
}

export interface EChartOptionsParams {
  series: EChartSeries[]
  legendData?: string[]
  xAxis?: any[]
  yAxis?: any
  grid?: any
  dataZoom?: any[]
  toolbox?: any
  tooltip?: any
  showYAxisLabel?: boolean
}

export function buildEChartOption(params: EChartOptionsParams): echarts.EChartsOption {
  return {
    dataZoom: params.dataZoom ?? [
      // { type: 'inside', realtime: true },
      // { type: 'slider', orient: 'vertical' },
      {
        type: 'slider',
        orient: 'vertical',
        start: 0,
        end: 100,
        xAxisIndex: 'none',
        yAxisIndex: 0,
        // 防止zoomin时影响y轴范围
        filterMode: 'filter',
        rangeMode: ['value', 'value'],
      },
    ],
    tooltip: params.tooltip ?? {
      trigger: 'axis',
      axisPointer: { type: 'cross' },
    },
    legend: {
      bottom: 0,
      data: params.legendData ?? params.series.map((s) => s.name),
    },
    grid: params.grid ?? {
      // left: 70,
      // right: 20,
      top: 300,
      // bottom: 20,
    },
    xAxis: params.xAxis ?? [],
    yAxis: params.yAxis ?? {
      type: 'value',
      inverse: true,
      name: '',
      position: 'left',
      nameLocation: 'start',
      nameGap: 10,
      min: function (value) {
        const range = value.max - value.min
        let padding = 1
        if (range >= 1000) {
          padding = 100
        } else if (range >= 100) {
          padding = 10
        } else if (range >= 10) {
          padding = 1
        } else {
          padding = 0.1
        }
        return Math.round((value.min - padding) * 10) / 10
      },
      max: function (value) {
        const range = value.max - value.min
        let padding = 1
        if (range >= 1000) {
          padding = 100
        } else if (range >= 100) {
          padding = 10
        } else if (range >= 10) {
          padding = 1
        } else {
          padding = 0.1
        }
        return Math.round((value.max + padding) * 10) / 10
      },
    },
    series: params.series,
    toolbox: params.toolbox ?? {
      feature: {
        dataZoom: { xAxisIndex: 'none' },
        restore: {},
        saveAsImage: {},
      },
    },
    graphic: params.showYAxisLabel !== false ? {
      type: 'text',
      left: 5,
      top: 'middle', // 垂直居中
      style: {
        text: 'Depth (m)',
        fontSize: 14,
        fontWeight: 'bold',
        fill: '#666',
        textAlign: 'center',
      },
      rotation: Math.PI / 2, // 旋转90度，使文字竖向显示
    } : undefined,
  }
}

export function initEChart(dom: HTMLDivElement, option: echarts.EChartsOption): echarts.ECharts {
  const instance = echarts.init(dom)
  instance.setOption(option, { notMerge: true })
  return instance
}

export function updateEChart(instance: echarts.ECharts, option: echarts.EChartsOption) {
  instance.setOption(option, { notMerge: true })
}

export function disposeEChart(instance: echarts.ECharts | null) {
  if (instance) {
    instance.dispose()
  }
}

export function getMaxMinRangeForAllCurves(allData: number[][]) {
  let globalMin = Infinity
  let globalMax = -Infinity

  for (const curveData of allData) {
    const localMin = Math.min(...curveData)
    const localMax = Math.max(...curveData)
    globalMin = Math.min(globalMin, localMin)
    globalMax = Math.max(globalMax, localMax)
  }

  // 计算统一范围，并加点 padding
  const range = globalMax - globalMin
  const padding = range * 0.1 || 1 // 防止 range 为 0
  const min = globalMin - padding
  const max = globalMax + padding
  console.log('min:', {
    min: Math.round(min * 10) / 10,
    max: Math.round(max * 10) / 10,
  })
  return {
    min: Math.round(min * 10) / 10,
    max: Math.round(max * 10) / 10,
  }
}

// 判断测井曲线范围的函数
// export function getCurveRange(curveName: string): { min: number; max: number; type: string } {
//   // 获取曲线名称的前缀（去掉后缀）
//   const prefix = curveName.split(' ')[0].toUpperCase()

//   switch (prefix) {
//     case 'SP':
//       return { min: 0, max: 100, type: 'category' }
//     case 'GR':
//       return { min: 0, max: 150, type: 'category' }
//     case 'CAL':
//       return { min: 6, max: 16, type: 'category' }
//     case 'DEN':
//       return { min: 1.9, max: 2.9, type: 'category' }
//     case 'CNL':
//       return { min: -15, max: 45, type: 'category' }
//     case 'AC':
//       return { min: 30, max: 130, type: 'category' }
//     case 'RD':
//       return { min: 0.1, max: 100, type: 'log' }
//     case 'RS':
//       return { min: 0.1, max: 100, type: 'log' }
//     default:
//       // 默认范围，可以根据需要调整
//       return { min: 0, max: 100, type: 'category' }
//   }
// }

export function getCurveRange(
  curveName: string,
  curveData?: number[][]
): { min: number; max: number; type: string } {
  const prefix = curveName.split(' ')[0].toUpperCase()

  const type = prefix === 'RD' || prefix === 'RS' ? 'log' : 'category'

  if (curveData && curveData.length > 0) {
    const values = curveData
      .map((d) => d?.[0])
      .filter((v): v is number => typeof v === 'number' && Number.isFinite(v) && (type !== 'log' || v > 0))

    if (values.length > 0) {
      const dataMin = Math.min(...values)
      const dataMax = Math.max(...values)
      const range = dataMax - dataMin
      const padding = range > 0 ? range * 0.05 : Math.max(Math.abs(dataMax) * 0.05, 1)
      const min = type === 'log' ? Math.max(1e-6, dataMin - padding) : dataMin - padding
      const max = dataMax + padding
      return { min, max, type }
    }
  }

  switch (prefix) {
    case 'SP':
      return { min: 0, max: 100, type }
    case 'GR':
      return { min: 0, max: 150, type }
    case 'CAL':
      return { min: 6, max: 16, type }
    case 'DEN':
      return { min: 1.9, max: 2.9, type }
    case 'CNL':
      return { min: -15, max: 45, type }
    case 'AC':
      return { min: 30, max: 130, type }
    case 'RD':
      return { min: 0.1, max: 100, type }
    case 'RS':
      return { min: 0.1, max: 100, type }
    default:
      return { min: 0, max: 100, type }
  }
}

export const defaultChartConfig = {
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
  }
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
    const color = config.color || colorArray[index % colorArray.length]

    return {
      name: c,
      type: 'line',
      data: data[c] || [],
      lineStyle: { color, width: 2 }, // 加粗曲线
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
    const min =
      config.range?.[0] !== undefined ? config.range[0] : getCurveRange(c, data[c]).min
    const max =
      config.range?.[1] !== undefined ? config.range[1] : getCurveRange(c, data[c]).max
    const labelEpsilon = Math.max(Math.abs(max - min) * 1e-6, 1e-9)
    const formatAxisLabel = (v: number) => {
      if (!Number.isFinite(v)) return ''
      const abs = Math.abs(v)
      if (abs >= 10000 || (abs > 0 && abs < 0.001)) return v.toExponential(2)
      const rounded = Math.round(v * 100) / 100
      return String(rounded)
    }

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
        showMinLabel: true,
        showMaxLabel: true,
        hideOverlap: false,
        formatter: function (value: number) {
          if (Math.abs(value - min) <= labelEpsilon) return formatAxisLabel(min)
          if (Math.abs(value - max) <= labelEpsilon) return formatAxisLabel(max)
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
    xAxis.push({
      type: 'log',
      logBase: 10,
      min: 0.1,
      max: 1000,
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

export function patchTreeKeys(nodes: any[], parentPath: string = ''): any[] {
  return nodes.map((node) => {
    const currentKey = parentPath
      ? `${parentPath}-${node.id}/${node.type}`
      : `${node.id}/${node.type}`
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
