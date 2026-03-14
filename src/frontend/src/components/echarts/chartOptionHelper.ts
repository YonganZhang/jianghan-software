import * as echarts from 'echarts'
import { buildEChartOption, colorArray, getCurveRange } from './echartsHelper'

// 弹窗配置类型
export type ChannelsConfig = {
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

// 工具函数
// 计算主/次分割线
function getSplitPositions(xMin: number, xMax: number, count: number): number[] {
  const positions: number[] = []
  if (!count || count <= 0 || !isFinite(xMin) || !isFinite(xMax) || xMax <= xMin) return positions
  for (let i = 1; i < count; i++) {
    positions.push(xMin + (i * (xMax - xMin)) / count)
  }
  return positions
}

// 构造series
function buildSeries(
  curves: string[],
  data: Record<string, number[][]>,
  customConfig: Record<string, { lineStyle?: string; color?: string; range?: [number, number] }>
) {
  const lithologyColors = [
    'rgba(255,0,0,0.5)',
    'rgba(0,0,255,0.5)',
    'rgba(0,255,0,0.5)',
    'rgba(255,165,0,0.5)',
    'rgba(255,0,255,0.5)',
  ]

  return curves.map((c, index) => {
    if (c === 'cluster_label') {
      const raw = (data[c] || []).filter((d) => Array.isArray(d) && d.length >= 2)
      const processed = raw.map((d, i) => {
        const label = Number(d[0])
        const depth = Number(d[1])
        const prevDepth = i > 0 ? Number(raw[i - 1][1]) : depth
        const nextDepth = i < raw.length - 1 ? Number(raw[i + 1][1]) : depth
        const y0 = i === 0 ? depth : (depth + prevDepth) / 2
        const y1 = i === raw.length - 1 ? depth : (depth + nextDepth) / 2
        return [Number.isFinite(label) ? label : 0, y0, y1]
      })

      return {
        name: c,
        type: 'custom',
        data: processed,
        renderItem: (params: any, api: any) => {
          const label = api.value(0)
          const y0 = api.value(1)
          const y1 = api.value(2)

          const p0 = api.coord([0, y0])
          const p1 = api.coord([1, y1])
          const left = Math.min(p0[0], p1[0])
          const right = Math.max(p0[0], p1[0])
          const top = Math.min(p0[1], p1[1])
          const bottom = Math.max(p0[1], p1[1])

          const rect = echarts.graphic.clipRectByRect(
            {
              x: left,
              y: top,
              width: Math.max(1, right - left),
              height: Math.max(1, bottom - top),
            },
            params.coordSys
          )
          if (!rect) return null

          const idx = ((Number(label) % lithologyColors.length) + lithologyColors.length) % lithologyColors.length
          return {
            type: 'rect',
            shape: rect,
            style: api.style({ fill: lithologyColors[idx], stroke: 'transparent' }),
          }
        },
        silent: true,
        yAxisIndex: 0,
        xAxisIndex: index,
        z: 2,
      }
    }

    const config = customConfig?.[c] || {}
    const color = config.color || colorArray[index]
    const seriesData = data[c] || []
    return {
      name: c,
      type: 'line',
      data: seriesData,
      lineStyle: { color },
      itemStyle: { color },
      symbol: 'none',
      showSymbol: false,
      yAxisIndex: 0,
      xAxisIndex: index,
    }
  })
}

function buildXAxis(
  curves: string[],
  data: Record<string, number[][]>,
  customConfig: Record<string, { lineStyle?: string; color?: string; range?: [number, number] }>
) {
  return curves.map((c, index) => {
    const config = customConfig?.[c] || {}
    const lineStyle = config.lineStyle || 'solid'
    const color = config.color || colorArray[index]

    if (c === 'cluster_label') {
      return {
        name: c,
        nameLocation: 'middle',
        nameGap: 5,
        nameTextStyle: { color },
        type: 'value',
        position: 'top',
        offset: 10 + 30 * index,
        axisLine: { show: true, lineStyle: { color, type: lineStyle } },
        axisLabel: { show: false },
        axisTick: { show: false },
        splitLine: { show: false },
        min: 0,
        max: 1,
      }
    }

    const { min: defaultMin, max: defaultMax } = getCurveRange(c, data[c])
    const min = config.range?.[0] ?? defaultMin
    const max = config.range?.[1] ?? defaultMax
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
      nameTextStyle: { color },
      type: 'value',
      position: 'top',
      offset: 10 + 30 * index,
      axisLine: { show: true, lineStyle: { color, type: lineStyle } },
      axisLabel: {
        color,
        margin: 3,
        showMinLabel: true,
        showMaxLabel: true,
        hideOverlap: false,
        formatter: (value: number) => {
          if (Math.abs(value - min) <= labelEpsilon) return formatAxisLabel(min)
          if (Math.abs(value - max) <= labelEpsilon) return formatAxisLabel(max)
          return ''
        },
      },
      axisTick: { show: false },
      splitLine: { show: false },
      min,
      max,
    }
  })
}

export function buildCustomOptions(
  curves: string[],
  data: Record<string, number[][]>,
  customConfig: Record<string, { lineStyle?: string; color?: string; range?: [number, number] }>,
  channelsConfig: ChannelsConfig,
  maxLenCurve?: number,
  isStandardize?: boolean,
  showYAxisName?: boolean
) {
  // 全局范围
  let xMin = Infinity,
    xMax = -Infinity
  Object.values(customConfig).forEach((cfg) => {
    if (cfg.range) {
      xMin = Math.min(xMin, cfg.range[0])
      xMax = Math.max(xMax, cfg.range[1])
    }
  })

  // 刻度线
  const mainSplit = getSplitPositions(xMin, xMax, channelsConfig.thickLineCount || 0)
  const minorSplit = getSplitPositions(xMin, xMax, channelsConfig.thinLineCount || 0)

  const series = [
    ...buildSeries(curves, data, customConfig),
    {
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
            ...mainSplit.map((pos) => ({
              xAxis: pos,
              lineStyle: {
                color: '#999',
                width: channelsConfig?.thickLine ? parseInt(channelsConfig.thickLine) : 3,
              },
            })),
            ...minorSplit.map((pos) => ({
              xAxis: pos,
              lineStyle: {
                color: '#ccc',
                width: channelsConfig?.thinLine ? parseInt(channelsConfig.thinLine) : 1,
              },
            })),
          ]
          : [],
      },
    },
  ]

  const xAxis = buildXAxis(curves, data, customConfig)
  if (channelsConfig.logarithmicScale === 'true' && !isStandardize) {
    const x = {
      type: 'log',
      min: 0.1,
      max: 1000,
      splitLine: { show: true, lineStyle: { type: 'dashed', color: '#ccc' } },
      axisLabel: { show: false },
    } as any
    x.logBase = 10
    xAxis.push(x)
  }
  console.log('xAxis:', xAxis)

  const lanes = Math.max(1, maxLenCurve ?? curves.length)
  const result = buildEChartOption({
    grid: {
      top: 30 * lanes + 20,
      left: 70,
      right: 50, // 为垂直滚动条预留空间
      bottom: 80,
    },
    series,
    xAxis,
    showYAxisLabel: false,
    yAxis: {
      type: 'value',
      inverse: true,
      name: showYAxisName !== false ? 'Depth (m)' : '',
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
        // if(isGuiYi) {
        //   return -1;
        // }
        return Math.floor(value.min)
      },
      max: function (value: any) {
        // if(isGuiYi) {
        //   return 1;
        // }
        return Math.ceil(value.max)
      },
      axisTick: { show: false },
      axisLine: { show: true, lineStyle: { type: 'solid' } },
      axisLabel: { hideOverlap: true },
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
          (channelsConfig?.depthThickInterval ?? 10) / (channelsConfig?.depthInterval ?? 1),
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

  return result
}
