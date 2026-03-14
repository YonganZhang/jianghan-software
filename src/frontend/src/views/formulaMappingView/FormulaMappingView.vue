<template>
  <!-- 如果选中了公式，显示公式详情页面 -->
  <FormulaDetailView
    v-if="selectedFormula"
    :formula="selectedFormula"
    @back-to-list="handleBackToList"
    @edit-formula="handleEditFormula"
    @delete-formula="handleDeleteFormula"
  />
  <div v-else class="preview-panel" style="background-color: #fff; padding: 0">
    <!-- 如果没有选中公式，显示原有的tabs -->
    <div class="formula-content-wrapper" style="width: 100%; height: 100%">
        <div class="preview-panel">
          <div class="preprocess-select-card">
            <div class="preview-title">
              <span>公式智能映射参数</span>
            </div>
            <div style="padding: 16px">
              <a-form :model="inputParamsForm" layout="vertical" class="input-params-form">
                <div class="input-params-container">
                  <!-- 预设模型参数 -->
                  <div class="param-column">
                    <div class="param-column-header">
                      <span class="param-column-title">数据相关</span>
                    </div>
                    <div class="param-column-content">
                      <a-form-item name="目标文件名">
                        <template #label>
                          <a-tooltip
                            title="输入的 Excel 文件名（含扩展名），需放在目标目录下。通常包含原始实验/测井结果数据，例如 'TOC.xlsx'、'孔隙度.xlsx'。建议文件名体现内容，以便快速识别。"
                            placement="right"
                          >
                            <span>目标文件名：</span>
                          </a-tooltip>
                        </template>
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
                      </a-form-item>
                      <a-form-item name="目标参数">
                        <template #label>
                          <a-tooltip
                            title="要拟合/预测的目标列名（Y变量）。选择Excel中需要预测的目标列。"
                            placement="right"
                          >
                            <span>目标参数：</span>
                          </a-tooltip>
                        </template>
                        <a-select
                          v-model:value="inputParamsForm.目标参数"
                          style="width: 100%"
                          placeholder="请先选择目标文件"
                          :loading="columnsLoading"
                          :disabled="excelColumns.length === 0"
                          show-search
                          allow-clear
                        >
                          <a-select-option v-for="col in excelColumns" :key="col" :value="col">{{ col }}</a-select-option>
                        </a-select>
                      </a-form-item>
                      <a-form-item name="深度列表头">
                        <template #label>
                          <a-tooltip
                            title="深度列的列名（X变量之一）。如果未选择，则默认第一列为深度。"
                            placement="right"
                          >
                            <span>深度列表头：</span>
                          </a-tooltip>
                        </template>
                        <a-select
                          v-model:value="inputParamsForm.深度列表头"
                          style="width: 100%"
                          placeholder="请先选择目标文件"
                          :loading="columnsLoading"
                          :disabled="excelColumns.length === 0"
                          show-search
                          allow-clear
                        >
                          <a-select-option v-for="col in excelColumns" :key="col" :value="col">{{ col }}</a-select-option>
                        </a-select>
                      </a-form-item>
                    </div>
                    <div class="param-column-header">
                      <span class="param-column-title">表达式规则</span>
                    </div>
                    <div class="param-column-content">
                      <a-form-item name="constraints">
                        <template #label>
                          <a-tooltip
                            title='用于限制表达式复杂度或禁止某些组合。例如 &#123;"^": [-3, 3]&#125; 表示幂运算的指数范围在 -3 到 3 之间。'
                            placement="right"
                          >
                            <span>表达式约束条件：</span>
                          </a-tooltip>
                        </template>
                        <a-input v-model:value="inputParamsForm.constraints" style="width: 100%" />
                      </a-form-item>
                      <a-form-item name="nested_constraints">
                        <template #label>
                          <a-tooltip
                            title='嵌套约束，限制算子嵌套深度。默认配置：禁止 log 自嵌套，禁止 sin/cos 互相或自嵌套。例如 &#123;"sin": &#123;"sin": 1&#125;&#125; 表示允许最多两层 sin 嵌套。'
                            placement="right"
                          >
                            <span>嵌套结构约束条件：</span>
                          </a-tooltip>
                        </template>
                        <a-input
                          v-model:value="inputParamsForm.nested_constraints"
                          style="width: 100%"
                        />
                      </a-form-item>
                      <a-form-item name="maxsize">
                        <template #label>
                          <a-tooltip
                            title="表达式复杂度上限，表示语法树节点总数。越大越灵活，但过大可能过拟合。建议地质建模初期设 20~40。"
                            placement="right"
                          >
                            <span>表达式最大规模：</span>
                          </a-tooltip>
                        </template>
                        <a-input-number
                          v-model:value="inputParamsForm.maxsize"
                          :min="1"
                          :max="10000"
                          :step="1"
                          style="width: 100%"
                        />
                      </a-form-item>
                      <a-form-item name="maxdepth">
                        <template #label>
                          <a-tooltip
                            title="-1 表示自适应深度控制。设为正整数则固定最大树深度。推荐用默认 -1，让算法自适应调整。"
                            placement="right"
                          >
                            <span>表达式最大深度：</span>
                          </a-tooltip>
                        </template>
                        <a-input-number
                          v-model:value="inputParamsForm.maxdepth"
                          :min="-1"
                          :max="10000"
                          :step="1"
                          style="width: 100%"
                        />
                      </a-form-item>
                      <a-form-item name="warmup_maxsize_by">
                        <template #label>
                          <a-tooltip
                            title="逐步放宽复杂度的比例。例如设为 0.5，前半程搜索较简单模型，后半程逐步增加复杂度。可提升稳定性，减少早期过拟合。"
                            placement="right"
                          >
                            <span>随迭代放宽最大规模：</span>
                          </a-tooltip>
                        </template>
                        <a-input-number
                          v-model:value="inputParamsForm.warmup_maxsize_by"
                          :min="0"
                          :max="1"
                          :step="0.1"
                          style="width: 100%"
                        />
                      </a-form-item>
                      <a-form-item name="use_frequency">
                        <template #label>
                          <a-tooltip
                            title="是否在进化搜索中使用复杂度频率。开启后会平衡搜索，避免总是偏向低复杂度或高复杂度。"
                            placement="right"
                          >
                            <span>根据频率使用算子：</span>
                          </a-tooltip>
                        </template>
                        <a-select
                          v-model:value="inputParamsForm.use_frequency"
                          style="width: 1"
                          allow-clear
                        >
                          <a-select-option :value="0">0</a-select-option>
                          <a-select-option :value="1">1</a-select-option>
                        </a-select>
                      </a-form-item>
                      <a-form-item name="use_frequency_in_tournament">
                        <template #label>
                          <a-tooltip
                            title="在候选比较时是否考虑复杂度频率。若开启，选择过程中会偏好多样化公式。"
                            placement="right"
                          >
                            <span>锦标赛中使用频率信息：</span>
                          </a-tooltip>
                        </template>
                        <a-select
                          v-model:value="inputParamsForm.use_frequency_in_tournament"
                          style="width: 1"
                          allow-clear
                        >
                          <a-select-option :value="0">0</a-select-option>
                          <a-select-option :value="1">1</a-select-option>
                        </a-select>
                      </a-form-item>
                      <a-form-item name="adaptive_parsimony_scaling">
                        <template #label>
                          <a-tooltip
                            title="自适应简约惩罚强度。数值越大，算法越倾向于选择更简单的公式。避免出现复杂但过拟合的表达式。"
                            placement="right"
                          >
                            <span>自适应简约惩罚因子：</span>
                          </a-tooltip>
                        </template>
                        <a-input-number
                          v-model:value="inputParamsForm.adaptive_parsimony_scaling"
                          :min="0"
                          :max="10000"
                          :step="0.1"
                          style="width: 100%"
                        />
                      </a-form-item>
                    </div>
                  </div>

                  <div class="param-column">
                    <div class="param-column-header">
                      <span class="param-column-title">算子选择</span>
                    </div>
                    <div class="param-column-content">
                      <a-form-item name="考虑cos">
                        <template #label>
                          <a-tooltip
                            title="是否允许余弦函数 cos(x) 出现在回归公式中。cos 可表达周期性规律，如旋回沉积或曲线振荡。但在孔隙度、TOC 等平滑趋势参数拟合中，容易带来非物理震荡。若确有明显周期性再启用。"
                            placement="right"
                          >
                            <span>考虑余弦函数：</span>
                          </a-tooltip>
                        </template>
                        <div class="range-inputs">
                          <a-select
                            v-model:value="inputParamsForm.考虑cos"
                            style="width: 1"
                            allow-clear
                          >
                            <a-select-option value="是">是</a-select-option>
                            <a-select-option value="否">否</a-select-option>
                          </a-select>
                        </div>
                      </a-form-item>
                      <a-form-item name="考虑sin">
                        <template #label>
                          <a-tooltip
                            title="是否允许正弦函数 sin(x)。与 cos 类似，用于周期性模式建模。适用于波浪状、循环性的地层特征，但通常石油储层曲线不明显。默认关闭以避免不必要的震荡项。"
                            placement="right"
                          >
                            <span>考虑正弦函数：</span>
                          </a-tooltip>
                        </template>
                        <div class="range-inputs">
                          <a-select
                            v-model:value="inputParamsForm.考虑sin"
                            style="width: 1"
                            allow-clear
                          >
                            <a-select-option value="是">是</a-select-option>
                            <a-select-option value="否">否</a-select-option>
                          </a-select>
                        </div>
                      </a-form-item>
                      <a-form-item name="考虑exp">
                        <template #label>
                          <a-tooltip
                            title="是否纳入指数函数 exp(x)。在地质中常用于描述压实导致的孔隙度随深度呈指数衰减，或有机质成熟度呈指数增长等现象。若变量对目标参数存在衰减/增强趋势，开启较合理。"
                            placement="right"
                          >
                            <span>考虑指数函数：</span>
                          </a-tooltip>
                        </template>
                        <div class="range-inputs">
                          <a-select
                            v-model:value="inputParamsForm.考虑exp"
                            style="width: 1"
                            allow-clear
                          >
                            <a-select-option value="是">是</a-select-option>
                            <a-select-option value="否">否</a-select-option>
                          </a-select>
                        </div>
                      </a-form-item>
                      <a-form-item name="考虑log">
                        <template #label>
                          <a-tooltip
                            title="是否纳入对数函数 log(x)。对数可把乘性关系转化为加性关系，对右偏分布拉直。石油领域常用于渗透率分布建模。注意输入必须大于 0，否则会报错。"
                            placement="right"
                          >
                            <span>考虑对数函数：</span>
                          </a-tooltip>
                        </template>
                        <div class="range-inputs">
                          <a-select
                            v-model:value="inputParamsForm.考虑log"
                            style="width: 1"
                            allow-clear
                          >
                            <a-select-option value="是">是</a-select-option>
                            <a-select-option value="否">否</a-select-option>
                          </a-select>
                        </div>
                      </a-form-item>
                      <a-form-item name="考虑inv(x)=1/x">
                        <template #label>
                          <a-tooltip
                            title="是否纳入倒数算子 1/x。用于表达“随变量增大而快速衰减”的规律，如裂缝密度影响渗透率。但对接近 0 的数值敏感，易引发数值不稳定。"
                            placement="right"
                          >
                            <span>考虑倒数函数：</span>
                          </a-tooltip>
                        </template>
                        <div class="range-inputs">
                          <a-select
                            v-model:value="inputParamsForm['考虑inv(x)=1/x']"
                            style="width: 1"
                            allow-clear
                          >
                            <a-select-option value="是">是</a-select-option>
                            <a-select-option value="否">否</a-select-option>
                          </a-select>
                        </div>
                      </a-form-item>
                      <a-form-item name="考虑+">
                        <template #label>
                          <a-tooltip
                            title="加法运算。最基础的线性组合方式。通常用于叠加多个独立效应，建议始终保留。"
                            placement="right"
                          >
                            <span>考虑加法运算：</span>
                          </a-tooltip>
                        </template>
                        <div class="range-inputs">
                          <a-select
                            v-model:value="inputParamsForm['考虑+']"
                            style="width: 1"
                            allow-clear
                          >
                            <a-select-option value="是">是</a-select-option>
                            <a-select-option value="否">否</a-select-option>
                          </a-select>
                        </div>
                      </a-form-item>
                      <a-form-item name="考虑-">
                        <template #label>
                          <a-tooltip
                            title="减法运算。允许变量之间形成差异关系。如“压实效应 - 胀裂效应”。建议保留，否则表达能力不足。"
                            placement="right"
                          >
                            <span>考虑减法运算：</span>
                          </a-tooltip>
                        </template>
                        <div class="range-inputs">
                          <a-select
                            v-model:value="inputParamsForm['考虑-']"
                            style="width: 1"
                            allow-clear
                          >
                            <a-select-option value="是">是</a-select-option>
                            <a-select-option value="否">否</a-select-option>
                          </a-select>
                        </div>
                      </a-form-item>
                      <a-form-item name="考虑*">
                        <template #label>
                          <a-tooltip
                            title="乘法。可表达交互项，体现两个变量联合效应。例如“孔隙度 * 渗透率影响产能”。通常必需，建议保留。"
                            placement="right"
                          >
                            <span>考虑乘法运算：</span>
                          </a-tooltip>
                        </template>
                        <div class="range-inputs">
                          <a-select
                            v-model:value="inputParamsForm['考虑*']"
                            style="width: 1"
                            allow-clear
                          >
                            <a-select-option value="是">是</a-select-option>
                            <a-select-option value="否">否</a-select-option>
                          </a-select>
                        </div>
                      </a-form-item>
                      <a-form-item name="考虑/">
                        <template #label>
                          <a-tooltip
                            title="除法。常见于比值关系，如“孔隙度/渗透率”。能刻画相对效应，但要注意零除风险。"
                            placement="right"
                          >
                            <span>考虑除法运算：</span>
                          </a-tooltip>
                        </template>
                        <div class="range-inputs">
                          <a-select
                            v-model:value="inputParamsForm['考虑/']"
                            style="width: 1"
                            allow-clear
                          >
                            <a-select-option value="是">是</a-select-option>
                            <a-select-option value="否">否</a-select-option>
                          </a-select>
                        </div>
                      </a-form-item>
                      <a-form-item name="考虑^">
                        <template #label>
                          <a-tooltip
                            title="幂运算。可表达非线性增强/衰减效应。例如 TOC^2 强调高丰度样本的贡献。但容易过拟合，默认关闭，必要时手动开启。"
                            placement="right"
                          >
                            <span>考虑幂运算：</span>
                          </a-tooltip>
                        </template>
                        <div class="range-inputs">
                          <a-select
                            v-model:value="inputParamsForm['考虑^']"
                            style="width: 1"
                            allow-clear
                          >
                            <a-select-option value="是">是</a-select-option>
                            <a-select-option value="否">否</a-select-option>
                          </a-select>
                        </div>
                      </a-form-item>
                    </div>
                  </div>

                  <!-- 物理约束类 -->
                  <div class="param-column">
                    <div class="param-column-header">
                      <span class="param-column-title">搜索规模与复杂度</span>
                    </div>
                    <div class="param-column-content">
                      <a-form-item name="niterations">
                        <template #label>
                          <a-tooltip
                            title="进化迭代次数。越大结果越稳定，但计算更耗时。一般设 30~50 就能收敛。"
                            placement="right"
                          >
                            <span>总迭代次数：</span>
                          </a-tooltip>
                        </template>
                        <a-input-number
                          v-model:value="inputParamsForm.niterations"
                          :min="0"
                          :max="10000"
                          :step="1"
                          style="width: 100%"
                        />
                      </a-form-item>
                      <a-form-item name="populations">
                        <template #label>
                          <a-tooltip
                            title="种群数量。多个种群并行进化，有助于多样化搜索。通常 10~30 之间。"
                            placement="right"
                          >
                            <span>种群数目：</span>
                          </a-tooltip>
                        </template>
                        <a-input-number
                          v-model:value="inputParamsForm.populations"
                          :min="0"
                          :max="10000"
                          :step="1"
                          style="width: 100%"
                        />
                      </a-form-item>
                      <a-form-item name="population_size">
                        <template #label>
                          <a-tooltip
                            title="每个种群的个体数。越大越全面，但计算量也增加。1000 是经验值，适合大多数情况。"
                            placement="right"
                          >
                            <span>种群大小：</span>
                          </a-tooltip>
                        </template>
                        <a-input-number
                          v-model:value="inputParamsForm.population_size"
                          :min="0"
                          :max="10000"
                          :step="1"
                          style="width: 100%"
                        />
                      </a-form-item>
                      <a-form-item name="ncycles_per_iteration">
                        <template #label>
                          <a-tooltip
                            title="每次迭代的突变/选择循环次数。循环越多，搜索越充分，但速度更慢。"
                            placement="right"
                          >
                            <span>每次迭代循环次数：</span>
                          </a-tooltip>
                        </template>
                        <a-input-number
                          v-model:value="inputParamsForm.ncycles_per_iteration"
                          :min="0"
                          :max="10000"
                          :step="1"
                          style="width: 100%"
                        />
                      </a-form-item>
                    </div>
                  </div>
                  <div class="param-column">
                    <div class="param-column-header">
                      <span class="param-column-title">特征优选/交叉参数等</span>
                    </div>
                    <div class="param-column-content">
                      <a-form-item name="elementwise_loss">
                        <template #label>
                          <a-tooltip
                            title="逐点损失函数。L2 距离 (均方误差) 常用于连续变量拟合。在 TOC、孔隙度预测中，能平滑惩罚大误差。可换为 L1 等以增强鲁棒性。"
                            placement="right"
                          >
                            <span>逐元素损失计算：</span>
                          </a-tooltip>
                        </template>
                        <a-input
                          v-model:value="inputParamsForm.elementwise_loss"
                          style="width: 100%"
                        />
                      </a-form-item>
                      <a-form-item name="model_selection">
                        <template #label>
                          <a-tooltip
                            title="最终模型选择标准。best：综合考虑复杂度和精度，推荐默认。accuracy：更偏向精度。score：使用内部评分。"
                            placement="right"
                          >
                            <span>模型选择方式：</span>
                          </a-tooltip>
                        </template>
                        <a-select
                          v-model:value="inputParamsForm.model_selection"
                          style="width: 100%"
                          allow-clear
                        >
                          <a-select-option value="best">best</a-select-option>
                          <a-select-option value="accuracy">accuracy</a-select-option>
                          <a-select-option value="score">score</a-select-option>
                        </a-select>
                      </a-form-item>
                      <a-form-item name="select_k_features">
                        <template #label>
                          <a-tooltip
                            title="是否在回归前执行特征选择。空表示不启用；正整数表示最多选择多少特征。适合输入特征较多的情况。"
                            placement="right"
                          >
                            <span>选择的特征数量：</span>
                          </a-tooltip>
                        </template>
                        <a-input-number
                          v-model:value="inputParamsForm.select_k_features"
                          :min="0"
                          :max="10000"
                          :step="1"
                          style="width: 100%"
                        />
                      </a-form-item>
                      <a-form-item name="optimizer_algorithm">
                        <template #label>
                          <a-tooltip
                            title="用于常数优化的算法。BFGS：拟牛顿法，收敛快，适合光滑问题。NelderMead：单纯形法，更鲁棒但可能慢。"
                            placement="right"
                          >
                            <span>常数优化算法：</span>
                          </a-tooltip>
                        </template>
                        <a-select
                          v-model:value="inputParamsForm.optimizer_algorithm"
                          style="width: 100%"
                          allow-clear
                        >
                          <a-select-option value="BFGS">BFGS</a-select-option>
                          <a-select-option value="NelderMead">NelderMead</a-select-option>
                        </a-select>
                      </a-form-item>
                      <a-form-item name="optimizer_iterations">
                        <template #label>
                          <a-tooltip
                            title="单次常数优化的最大迭代步数。过大可能耗时过长，过小则不充分。"
                            placement="right"
                          >
                            <span>常数优化迭代次数：</span>
                          </a-tooltip>
                        </template>
                        <a-input-number
                          v-model:value="inputParamsForm.optimizer_iterations"
                          :min="0"
                          :max="10000"
                          :step="1"
                          style="width: 100%"
                        />
                      </a-form-item>
                      <a-form-item name="optimizer_nrestarts">
                        <template #label>
                          <a-tooltip
                            title="常数优化的随机重启次数。重启能帮助跳出局部最优。推荐 2~5。"
                            placement="right"
                          >
                            <span>常数优化随机重启次数：</span>
                          </a-tooltip>
                        </template>
                        <a-input-number
                          v-model:value="inputParamsForm.optimizer_nrestarts"
                          :min="0"
                          :max="10000"
                          :step="1"
                          style="width: 100%"
                        />
                      </a-form-item>
                      <a-form-item name="optimize_probability">
                        <template #label>
                          <a-tooltip
                            title="常数优化的概率。值越大，搜索过程中更频繁尝试优化常数项。能提高公式精度，但速度更慢。"
                            placement="right"
                          >
                            <span>常数优化概率：</span>
                          </a-tooltip>
                        </template>
                        <a-input-number
                          v-model:value="inputParamsForm.optimize_probability"
                          :min="0"
                          :max="1"
                          :step="0.01"
                          style="width: 100%"
                        />
                      </a-form-item>
                      <a-form-item name="crossover_probability">
                        <template #label>
                          <a-tooltip
                            title="遗传算法中交叉操作的概率。值越大，新个体来源于父代交叉的比例越高。过大可能导致收敛慢，过小则缺乏多样性。"
                            placement="right"
                          >
                            <span>交叉操作概率：</span>
                          </a-tooltip>
                        </template>
                        <a-input-number
                          v-model:value="inputParamsForm.crossover_probability"
                          :min="0"
                          :max="1"
                          :step="0.0001"
                          style="width: 100%"
                        />
                      </a-form-item>
                    </div>
                  </div>
                </div>

                <div style="display: flex; justify-content: flex-start; margin-top: 12px">
                  <a-button type="primary" :loading="isTesting" @click="handleLoadModel" :disabled="isTesting">
                    {{ isTesting ? '公式拟合中...' : '拟合公式' }}
                  </a-button>
                  <a-button
                    v-if="isTesting"
                    danger
                    @click="handleStopFitting"
                    style="margin-left: 12px"
                  >
                    中止拟合
                  </a-button>
                </div>
              </a-form>
            </div>
          </div>
        </div>

        <!-- 运行日志区域 - 始终显示 -->
        <div class="preprocess-select-card" style="margin: 16px">
          <div class="preview-title" style="display: flex; justify-content: space-between; align-items: center">
            <div style="display: flex; align-items: center; gap: 8px">
              <span>运行日志</span>
              <a-tag :color="state.isConnected ? 'green' : 'red'">
                {{ state.isConnected ? '已连接' : '未连接' }}
              </a-tag>
              <a-tag v-if="isTesting" color="processing">拟合中...</a-tag>
            </div>
            <a-button size="small" @click="clearFormulaLogs" :disabled="formulaLogs.length === 0">
              清空日志
            </a-button>
          </div>
          <div ref="formulaLogContainerRef" class="log-content-area" style="height: 480px; overflow-y: auto; padding: 12px; background: #fafafa; border-radius: 4px;">
            <div v-if="isTesting" class="log-banner" style="background: #e6f7ff; padding: 8px 12px; border-radius: 4px; margin-bottom: 8px; color: #1890ff;">
              正在进行公式拟合，日志实时刷新...
            </div>
            <div v-if="formulaLogs.length === 0" style="text-align: center; color: #999; padding: 20px;">
              暂无日志
            </div>
            <a-collapse v-else v-model:activeKey="activeFormulaLogKeys" :bordered="false">
              <a-collapse-panel v-for="item in displayFormulaLogs" :key="item.key">
                <template #header>
                  <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="color: #999; font-size: 12px; min-width: 30px;">{{ item.key + 1 }}</span>
                    <span v-if="item.time" style="color: #1890ff; font-size: 12px;">{{ item.time }}</span>
                    <span style="flex: 1;">{{ item.header }}</span>
                  </div>
                </template>
                <pre style="margin: 0; white-space: pre-wrap; word-break: break-all; font-size: 12px; background: #f5f5f5; padding: 8px; border-radius: 4px;">{{ item.content }}</pre>
              </a-collapse-panel>
            </a-collapse>
          </div>
        </div>

        <!-- 公式卡片区域 -->
        <div class="formulas-section">
          <!-- 无数据占位 -->
          <a-spin :spinning="isLoading">
          <div v-if="!formulas.length && !isTesting" class="no-data-placeholder">
            <div class="preprocess-select-card">
              <div class="preview-title">
                <span>具体公式展示</span>
              </div>
              <div
                style="padding: 16px; display: flex; justify-content: center; align-items: center"
              >
                <a-empty description="暂无数据，请先拟合公式" />
              </div>
            </div>
          </div>

          <!-- 动态公式卡片网格 -->
            <div v-if="!isTesting && formulas.length > 0" class="formulas-grid">
              <div
                v-for="formula in formulas"
                :key="formula.id"
                class="formula-card"
                @click="handleFormulaClick(formula)"
              >
                <div class="formula-card-header">
                  <span class="formula-name">{{ formula.name }}</span>
                  <span v-if="formula.r2" class="formula-r2">R²={{ parseFloat(formula.r2).toFixed(4) }}</span>
                </div>
                <div class="formula-card-content">
                  <!-- 公式图（LaTeX渲染） -->
                  <div v-if="formula.formulaPicture" class="formula-latex-section">
                    <a-image
                      :src="formula.formulaPicture"
                      alt="公式"
                      :preview="true"
                      class="formula-latex-img"
                    />
                  </div>
                  <!-- 拟合曲线图 -->
                  <div v-if="formula.predictionPicture" class="formula-prediction-section">
                    <a-image
                      :src="formula.predictionPicture"
                      alt="拟合曲线"
                      :preview="true"
                      class="formula-prediction-img"
                    />
                  </div>
                  <!-- 指标信息 -->
                  <div class="formula-metrics" v-if="formula.complexity || formula.mae">
                    <span v-if="formula.complexity">复杂度: {{ formula.complexity }}</span>
                    <span v-if="formula.rmse">RMSE: {{ parseFloat(formula.rmse).toFixed(4) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </a-spin>
        </div>
    </div>
  </div>
<a-modal
  v-model:open="showAllParams"
  title="公式智能映射参数"
  width="80%"
  :footer="null"
>
  <a-descriptions
    bordered
    :column="3"
    size="small"
  >
    <!-- 数据相关 -->
    <a-descriptions-item label="目标文件名">{{ detail.目标文件名 }}</a-descriptions-item>
    <a-descriptions-item label="目标目录">{{ detail.目标目录 }}</a-descriptions-item>
    <a-descriptions-item label="目标参数">{{ detail.目标参数 }}</a-descriptions-item>
    <a-descriptions-item label="深度列表头">{{ detail.深度列表头 }}</a-descriptions-item>

    <!-- 表达式规则 -->
    <a-descriptions-item label="表达式约束条件">{{ detail.constraints }}</a-descriptions-item>
    <a-descriptions-item label="嵌套结构约束条件">{{ detail.nested_constraints }}</a-descriptions-item>
    <a-descriptions-item label="表达式最大规模">{{ detail.maxsize }}</a-descriptions-item>
    <a-descriptions-item label="表达式最大深度">{{ detail.maxdepth }}</a-descriptions-item>
    <a-descriptions-item label="随迭代放宽最大规模">{{ detail.warmup_maxsize_by }}</a-descriptions-item>
    <a-descriptions-item label="根据频率使用算子">{{ detail.use_frequency }}</a-descriptions-item>
    <a-descriptions-item label="锦标赛中使用频率信息">{{ detail.use_frequency_in_tournament }}</a-descriptions-item>
    <a-descriptions-item label="自适应简约惩罚因子">{{ detail.adaptive_parsimony_scaling }}</a-descriptions-item>

    <!-- 算子选择 -->
    <a-descriptions-item label="考虑余弦函数">{{ detail.考虑cos }}</a-descriptions-item>
    <a-descriptions-item label="考虑正弦函数">{{ detail.考虑sin }}</a-descriptions-item>
    <a-descriptions-item label="考虑指数函数">{{ detail.考虑exp }}</a-descriptions-item>
    <a-descriptions-item label="考虑对数函数">{{ detail.考虑log }}</a-descriptions-item>
    <a-descriptions-item label="考虑倒数函数">{{ detail['考虑inv(x)=1/x'] }}</a-descriptions-item>
    <a-descriptions-item label="考虑加法运算">{{ detail['考虑+'] }}</a-descriptions-item>
    <a-descriptions-item label="考虑减法运算">{{ detail['考虑-'] }}</a-descriptions-item>
    <a-descriptions-item label="考虑乘法运算">{{ detail['考虑*'] }}</a-descriptions-item>
    <a-descriptions-item label="考虑除法运算">{{ detail['考虑/'] }}</a-descriptions-item>
    <a-descriptions-item label="考虑幂运算">{{ detail['考虑^'] }}</a-descriptions-item>

    <!-- 搜索规模与复杂度 -->
    <a-descriptions-item label="总迭代次数">{{ detail.niterations }}</a-descriptions-item>
    <a-descriptions-item label="种群数目">{{ detail.populations }}</a-descriptions-item>
    <a-descriptions-item label="种群大小">{{ detail.population_size }}</a-descriptions-item>
    <a-descriptions-item label="每次迭代循环次数">{{ detail.ncycles_per_iteration }}</a-descriptions-item>

    <!-- 特征优选/交叉参数等 -->
    <a-descriptions-item label="逐元素损失计算">{{ detail.elementwise_loss }}</a-descriptions-item>
    <a-descriptions-item label="模型选择方式">{{ detail.model_selection }}</a-descriptions-item>
    <a-descriptions-item label="选择的特征数量">{{ detail.select_k_features }}</a-descriptions-item>
    <a-descriptions-item label="常数优化算法">{{ detail.optimizer_algorithm }}</a-descriptions-item>
    <a-descriptions-item label="常数优化迭代次数">{{ detail.optimizer_iterations }}</a-descriptions-item>
    <a-descriptions-item label="常数优化随机重启次数">{{ detail.optimizer_nrestarts }}</a-descriptions-item>
    <a-descriptions-item label="常数优化概率">{{ detail.optimize_probability }}</a-descriptions-item>
    <a-descriptions-item label="交叉操作概率">{{ detail.crossover_probability }}</a-descriptions-item>
  </a-descriptions>
</a-modal>
</template>
<script setup lang="ts">
import {
  ref,
  computed,
  getCurrentInstance,
  inject,
  watch,
  type Ref,
  onMounted,
  reactive,
  onActivated,
  onDeactivated,
  nextTick
} from 'vue'
import { useRouter } from 'vue-router'
import FormulaDetailView from './FormulaDetailView.vue'
import {
  deleteFormulaPageList,
  getFormulaImage,
  getFormulaPageList,
  runSmartFormula,
  stopSmartFormula,
  getTreeData,
  FormulaDetail,
  getExcelColumns
} from '@/utils/api'
import zhCN from 'ant-design-vue/es/locale/zh_CN'
import { message } from 'ant-design-vue'
import { state, initSocket } from '@/socket'

const router = useRouter()

// 注入面包屑更新方法和返回列表方法
const setFormulaBreadcrumb = inject('setFormulaBreadcrumb') as (formulaName: string) => void
const backToFormulaList = inject('backToFormulaList') as () => void
const shouldReturnToList = inject('shouldReturnToList') as Ref<boolean>
import frameIcon from '@/assets/file/frame.svg'
import excelIcon from '@/assets/file/excel.svg'
import txtIcon from '@/assets/file/txt.svg'
const activeKey = ref<'new' | 'existing'>('new')

// 添加缺失的响应式变量
const selectedData = ref<string | undefined>()
const trainSetTags = ref<string | undefined>()
const trainSetOptions = ref([])
const isTesting = ref(false)
const logEnabled = ref(false)

// Excel列名相关变量
const excelColumns = ref<string[]>([])
const columnsLoading = ref(false)

// 运行日志相关变量
const formulaLogs = ref<{ type: string; content: string; ts: number; time: string }[]>([])
const activeFormulaLogKeys = ref<number[]>([])
const formulaLogContainerRef = ref<HTMLElement | null>(null)
const MAX_FORMULA_LOG_LINES = 500

// 初始化WebSocket连接
initSocket()

// 监听全局日志变化，同步到本地日志
watch(
  () => state.logs.length,
  () => {
    // 只在拟合过程中同步日志
    if (isTesting.value && state.logs.length > 0) {
      const latestLog = state.logs[state.logs.length - 1]
      // 避免重复添加
      const exists = formulaLogs.value.some(log => log.ts === latestLog.ts && log.content === latestLog.content)
      if (!exists) {
        formulaLogs.value.push(latestLog)
        // 自动滚动到底部
        nextTick(() => {
          if (formulaLogContainerRef.value) {
            formulaLogContainerRef.value.scrollTop = formulaLogContainerRef.value.scrollHeight
          }
        })
      }
    }
  }
)

// 格式化日志显示
const displayFormulaLogs = computed(() => {
  const start = Math.max(0, formulaLogs.value.length - MAX_FORMULA_LOG_LINES)
  return formulaLogs.value.slice(start).map((log, idx) => {
    const key = start + idx
    return {
      key,
      time: log.time,
      header: log.content.length > 80 ? log.content.substring(0, 80) + '...' : log.content,
      content: log.content,
    }
  })
})

// 清空日志
const clearFormulaLogs = () => {
  formulaLogs.value = []
  activeFormulaLogKeys.value = []
}

// 中止拟合
const handleStopFitting = async () => {
  try {
    await stopSmartFormula()
    message.info('已发送中止请求')
    isTesting.value = false
    saveTaskStatus('failed')
    clearTaskStatus()
    stopPolling()
  } catch (error: any) {
    console.error('中止失败:', error)
    message.error('中止失败: ' + (error?.message || '未知错误'))
  }
}

// 任务状态持久化的key
const TASK_STATUS_KEY = 'formula_prediction_task'

// 检查并恢复任务状态
const checkAndRestoreTaskStatus = () => {
  try {
    const savedTask = localStorage.getItem(TASK_STATUS_KEY)
    if (savedTask) {
      const task = JSON.parse(savedTask)
      // 检查任务是否在24小时内开始（防止旧任务永久保留）
      const taskAge = Date.now() - task.startedAt
      if (task.status === 'running' && taskAge < 24 * 60 * 60 * 1000) {
        console.log('检测到正在运行的预测任务，恢复状态')
        isTesting.value = true
        startPollingForResult()
      } else if (taskAge >= 24 * 60 * 60 * 1000) {
        // 任务超过24小时，清理
        localStorage.removeItem(TASK_STATUS_KEY)
      }
    }
  } catch (e) {
    console.error('恢复任务状态失败:', e)
    localStorage.removeItem(TASK_STATUS_KEY)
  }
}

// 保存任务状态到localStorage
const saveTaskStatus = (status: 'running' | 'completed' | 'failed') => {
  try {
    const task = {
      status,
      startedAt: status === 'running' ? Date.now() : JSON.parse(localStorage.getItem(TASK_STATUS_KEY) || '{}').startedAt,
      updatedAt: Date.now()
    }
    localStorage.setItem(TASK_STATUS_KEY, JSON.stringify(task))
  } catch (e) {
    console.error('保存任务状态失败:', e)
  }
}

// 清除任务状态
const clearTaskStatus = () => {
  localStorage.removeItem(TASK_STATUS_KEY)
}

// 轮询检查结果的定时器
let pollingTimer: ReturnType<typeof setTimeout> | null = null

// 开始轮询检查结果
const startPollingForResult = async () => {
  // 清除之前的轮询
  if (pollingTimer) {
    clearTimeout(pollingTimer)
  }
  
  // 轮询检查是否有新的公式图片
  const checkResult = async () => {
    try {
      const r = await getFormulaImage()
      if (Number(r?.code) === 200 && Array.isArray(r.images) && r.images.length > 0) {
        // 有结果了，停止轮询
        console.log('检测到预测结果，更新显示', r.images.length, '个公式')
        const images = r.images.map((item: any, index: number) => {
          return {
            id: item.id || index + 1,
            name: `公式 ${index + 1}`,
            index: item.index,
            complexity: item.complexity,
            r2: item.r2,
            mae: item.mae,
            rmse: item.rmse,
            latex: item.latex,
            predictionPicture: item.data?.prediction_picture 
              ? `data:image/png;base64,${item.data.prediction_picture}` 
              : undefined,
            formulaPicture: item.data?.formula_picture 
              ? `data:image/png;base64,${item.data.formula_picture}` 
              : undefined,
          }
        })
        formulas.value = images
        isTesting.value = false
        saveTaskStatus('completed')
        message.success(`公式预测完成，共 ${images.length} 个公式`)
        return true // 停止轮询
      }
    } catch (e) {
      // 忽略错误，继续轮询
      console.log('轮询检查中...', e)
    }
    return false // 继续轮询
  }
  
  // 每10秒检查一次
  const poll = async () => {
    const hasResult = await checkResult()
    if (!hasResult && isTesting.value) {
      pollingTimer = setTimeout(poll, 10000)
    }
  }
  
  // 开始轮询
  poll()
}

// 停止轮询
const stopPolling = () => {
  if (pollingTimer) {
    clearTimeout(pollingTimer)
    pollingTimer = null
  }
}
const treeData = ref<MyTreeNode[]>([])
const detail = ref<any>({}); //参数查看
const showAllParams = ref(false);  // 展示所有参数弹窗

const isLoading= ref(true)

type MyTreeNode = {
  title: string
  key: number
  type: string
  id: number
  children?: MyTreeNode[]
}

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

const dataOptions = computed(() => {
  const res = getOptions(treeData.value)
  return res
})

// 输入参数表单数据
const inputParamsForm = reactive({
  // 数据相关
  id: 0,
  目标文件名: 'TOC.xlsx',
  目标目录: 'test',
  目标参数: '',
  深度列表头: 'DEPTH',
  // 表达式规则
  constraints: '{"^": [-3, 3]}',
  nested_constraints: '{"log": {"log": 0}, "sin": {"sin": 1}}',
  maxsize: 50,
  maxdepth: -1,
  warmup_maxsize_by: 0,
  use_frequency: 1,
  use_frequency_in_tournament: 1,
  adaptive_parsimony_scaling: 1040,
  // 算子选择
  考虑cos: '是',
  考虑sin: '是',
  考虑exp: '是',
  考虑log: '是',
  '考虑inv(x)=1/x': '是',
  '考虑+': '是',
  '考虑-': '是',
  '考虑*': '是',
  '考虑/': '是',
  '考虑^': '是',
  // 搜索规模与复杂度 - 平衡速度和拟合效果
  niterations: 40,          // 迭代次数（适中）
  populations: 15,          // 种群数（适中）
  population_size: 33,      // 每个种群大小（PySR推荐）
  ncycles_per_iteration: 550,  // 每次迭代的循环数
  // 特征优选/交叉参数等
  elementwise_loss: 'L2DistLoss()',
  model_selection: 'best',
  select_k_features: null,  // 不限制特征数，使用全部特征
  optimize_probability: 0.14,  // 优化概率
  optimizer_algorithm: 'BFGS',
  optimizer_iterations: 8,    // 优化迭代
  optimizer_nrestarts: 2,     // 重启次数
  crossover_probability: 0.066,  // 交叉概率
  should_simplify: 1,
})

const loading = ref(true)
const tableData = ref<any[]>([])
const tableColumns = ref<{ title: string; dataIndex: string; key: string }[]>([])
const pagination = ref({
  current: 1,
  pageSize: 20,
  total: tableData.value.length,
  showTotal: (total: number) => `共 ${Math.ceil(total / pagination.value.pageSize)} 页`,
  showQuickJumper: true,
  showSizeChanger: true,
  pageSizeOptions: ['10', '20', '50', '100'],
  onShowSizeChange: (current: number, size: number) => {
    pagination.value.pageSize = size
    pagination.value.current = 1
  },
  onChange: (page: number, pageSize: number) => {
    pagination.value.current = page
    pagination.value.pageSize = pageSize
  },
})
const customLocale = {
  ...zhCN,
  Pagination: {
    ...zhCN.Pagination,
    items_per_page: '页',
  },
}

// 选中的公式
const selectedFormula = ref<{
  id: number
  name: string
  description: string
  picture: string
} | null>(null)

// 公式数据 - 每个公式包含拟合图和公式图
const formulas = ref<{
  id: number;
  name: string;
  index?: string;
  complexity?: string;
  r2?: string;
  mae?: string;
  rmse?: string;
  latex?: string;
  predictionPicture?: string;  // 拟合曲线图
  formulaPicture?: string;     // LaTeX公式图
}[]>([])
// const formulas = ref([
//   { id: 1, name: '公式1', description: '第一个公式描述' },
//   { id: 2, name: '公式2', description: '第二个公式描述' },
//   { id: 3, name: '公式3', description: '第三个公式描述' },
//   { id: 4, name: '公式4', description: '第四个公式描述' },
//   { id: 5, name: '公式5', description: '第五个公式描述' },
//   { id: 6, name: '公式6', description: '第六个公式描述' },
// ])

// 计算每行显示的公式数量
const formulasPerRow = 4

// 将公式分组为行
const formulaRows = computed(() => {
  const rows = []
  for (let i = 0; i < formulas.value.length; i += formulasPerRow) {
    rows.push(formulas.value.slice(i, i + formulasPerRow))
  }
  return rows
})

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

onActivated(async () => {
  // 恢复任务状态（检查是否有正在运行的预测任务）
  checkAndRestoreTaskStatus()

  const res2 = await getTreeData()
  if (res2.data) {
    const rawData = res2.data?.[0]?.children ?? []
    treeData.value = patchTreeKeys(rawData)
  }

  loading.value = true
  const pageNum = pagination.value.current
  const pageSize = pagination.value.pageSize
  isLoading.value = true
  const res = await getFormulaPageList({ pageNum, pageSize })
  if (res?.code === '00000') {
    isLoading.value = false
    loading.value = false
    tableColumns.value = res.data.columns

    // 图片列使用 className 以便精准控制列宽与内边距
    const imgCol = tableColumns.value.find(
      (c: any) => c.key === 'formula_image' || c.dataIndex === 'formula_image'
    ) as any
    if (imgCol) {
      imgCol.className = (imgCol.className ? imgCol.className + ' ' : '') + 'formula-image-col'
    }

    tableColumns.value.push({
      title: '操作',
      key: 'action',
      dataIndex: 'action',
    })
    tableData.value = res.data.dataSource.map((item: any) => ({
      ...item,
      key: `${item.id}_${item.model_type}`,
    }))
  }

  // 如果没有正在运行的任务，才获取公式图片
  if (!isTesting.value) {
    try {
      const r = await getFormulaImage()
      if (Number(r?.code) === 200 && Array.isArray(r.images) && r.images.length > 0) {
        const images = r.images.map((item: any, index: number) => {
          return {
            id: item.id || index + 1,
            name: `公式 ${index + 1}`,
            index: item.index,
            complexity: item.complexity,
            r2: item.r2,
            mae: item.mae,
            rmse: item.rmse,
            latex: item.latex,
            predictionPicture: item.data?.prediction_picture 
              ? `data:image/png;base64,${item.data.prediction_picture}` 
              : undefined,
            formulaPicture: item.data?.formula_picture 
              ? `data:image/png;base64,${item.data.formula_picture}` 
              : undefined,
          }
        })
        formulas.value = images
      } else {
        formulas.value = []
        console.log('暂无公式图片数据')
      }
    } catch (error: any) {
      // 404错误或"未找到该用户的图片数据"都是正常情况(用户首次使用时没有数据),不显示错误提示
      if (error?.response?.status === 404 || 
          error?.message?.includes('404') || 
          error?.message?.includes('未找到该用户的图片数据')) {
        console.log('用户暂无公式数据,这是首次使用的正常情况')
        formulas.value = []
      } else {
        console.error('获取公式图片失败:', error)
        formulas.value = []
        // 只有非404且非"未找到数据"的错误才显示错误提示
        message.error(error?.response?.data?.message || '获取公式图片失败')
      }
    }
  }
})

// 组件失活时停止轮询（但保持任务状态，以便切回时恢复）
onDeactivated(() => {
  stopPolling()
})

async function handleShow(record: Record<string, any>) {
  console.log('参数查看:', record)
  detail.value = {};
  detail.value = record.config_params;
  showAllParams.value = true;
}

async function handleDelete(record: Record<string, any>) {
  // 预留：此处可调用后端接口删除
  const res = await deleteFormulaPageList({ id: record.id })
  if (res.code == 200) {
    const key = record.key
    tableData.value = tableData.value.filter((item) => item.key !== key)
  }
}

// 添加缺失的方法
const onSelect = async (value: number, node: MyTreeNode) => {
  console.log('选择数据:', node.id)
  inputParamsForm.id = node.id;
  // 自动更新目标文件名为选中的文件名
  if (node.title) {
    inputParamsForm.目标文件名 = node.title;
  }
  console.log('已选择文件:', node)
  
  // 获取Excel文件的列名
  if (node.id) {
    await fetchExcelColumns(node.id)
  }
}

// 获取Excel文件列名
const fetchExcelColumns = async (fileId: number) => {
  columnsLoading.value = true
  excelColumns.value = []
  // 重置目标参数和深度列
  inputParamsForm.目标参数 = ''
  inputParamsForm.深度列表头 = ''
  
  try {
    const res = await getExcelColumns(fileId)
    if (res?.code === 200 && Array.isArray(res.columns)) {
      excelColumns.value = res.columns
      console.log('获取到列名:', res.columns)
      
      // 自动选择深度列（如果存在常见的深度列名）
      const depthCandidates = ['DEPTH', 'Depth', 'depth', '深度']
      for (const candidate of depthCandidates) {
        if (res.columns.includes(candidate)) {
          inputParamsForm.深度列表头 = candidate
          break
        }
      }
    }
  } catch (error) {
    console.error('获取列名失败:', error)
    message.warning('获取文件列名失败，请手动输入')
  } finally {
    columnsLoading.value = false
  }
}

// 选择输入目录/文件
const selectInputDir = async () => {
  try {
    console.log('点击输入目录，检查 electronAPI:', window.electronAPI)
    if (!window.electronAPI?.openFile) {
      console.error('electronAPI.openFile 不可用，可能在浏览器环境中运行')
      message.error('文件选择功能仅在 Electron 环境中可用')
      return
    }

    const filePath = await window.electronAPI.openFile({
      properties: ['openFile'],
    })
    console.log('选择的文件路径:', filePath)
    if (filePath) {
      inputParamsForm.input_directory = filePath
      message.success('文件选择成功')
    }
  } catch (e) {
    console.error('文件选择失败:', e)
    message.error('文件选择失败')
  }
}

const handleLoadModel = async () => {
  // 验证必填字段
  if (!inputParamsForm.id || inputParamsForm.id === 0) {
    message.error('请先选择目标文件')
    return
  }
  
  if (!inputParamsForm.目标参数 || inputParamsForm.目标参数.trim() === '') {
    message.error('请填写目标参数（Excel中要拟合的列名）')
    return
  }
  
  isTesting.value = true
  // 保存任务状态到LocalStorage（支持页面切换后恢复）
  saveTaskStatus('running')
  
  try {
    const res = await runSmartFormula(inputParamsForm)
    
    if (res?.code === 200) {
      message.success('公式拟合成功！')
      saveTaskStatus('completed')
      
      // 获取生成的公式图片并自动显示
      const r = await getFormulaImage()
      console.log('getFormulaImage 返回:', r)
      if (Number(r?.code) === 200 && Array.isArray(r.images) && r.images.length > 0) {
        const images = r.images.map((item: any, index: number) => {
          return {
            id: item.id || index + 1,
            name: `公式 ${index + 1}`,
            index: item.index,
            complexity: item.complexity,
            r2: item.r2,
            mae: item.mae,
            rmse: item.rmse,
            latex: item.latex,
            predictionPicture: item.data?.prediction_picture 
              ? `data:image/png;base64,${item.data.prediction_picture}` 
              : undefined,
            formulaPicture: item.data?.formula_picture 
              ? `data:image/png;base64,${item.data.formula_picture}` 
              : undefined,
          }
        })
        formulas.value = images
        message.success(`成功生成 ${images.length} 个公式，已自动展示在下方`)
      } else {
        message.warning('拟合完成，但未生成公式图片')
        formulas.value = []
      }
    } else {
      saveTaskStatus('failed')
      message.error(res?.message || '拟合失败，请检查参数设置')
    }
  } catch (error: any) {
    saveTaskStatus('failed')
    console.error('预测失败:', error)
    
    // 构建更详细的错误消息
    let errorMsg = '服务器内部错误';
    if (error?.response?.data?.message) {
      errorMsg = error.response.data.message;
    } else if (error?.response?.data?.错误) {
      errorMsg = error.response.data.错误;
    } else if (error?.message) {
      errorMsg = error.message;
    }
    
    message.error(errorMsg)
  } finally {
    isTesting.value = false
    // 清理任务状态（任务完成）
    clearTaskStatus()
    // 停止轮询
    stopPolling()
  }
}

const handleShowLog = () => {
  console.log('显示日志')
}

// 添加新公式
const addFormula = () => {
  const newId = Math.max(...formulas.value.map((f) => f.id)) + 1
  formulas.value.push({
    id: newId,
    name: `公式${newId}`,
    description: `第${newId}个公式描述`,
  })
}

// 删除公式
const removeFormula = (id: number) => {
  const index = formulas.value.findIndex((f) => f.id === id)
  if (index > -1) {
    formulas.value.splice(index, 1)
  }
}

// 处理公式点击
const handleFormulaClick = (formula: {
  id: number
  name: string
  description: string
  picture?: string
}) => {
  // 更新面包屑
  setFormulaBreadcrumb(formula.name)

  // 设置选中的公式
  selectedFormula.value = {
    id: formula.id,
    name: formula.name,
    description: formula.description,
    picture: formula.formulaPicture ?? '',
  }
}

// 返回公式列表
const handleBackToList = () => {
  // 调用父组件的返回列表方法
  backToFormulaList()
  // 清除选中的公式
  selectedFormula.value = null
}

// 编辑公式
const handleEditFormula = (formula: {
  id: number
  name: string
  description: string
  picture?: string
}) => {
  console.log('编辑公式:', formula.name)
  // 这里可以添加编辑逻辑
}

// 删除公式
const handleDeleteFormula = (formula: {
  id: number
  name: string
  description: string
  picture?: string
}) => {
  console.log('删除公式:', formula.name)
  // 从公式列表中删除
  const index = formulas.value.findIndex((f) => f.id === formula.id)
  if (index > -1) {
    formulas.value.splice(index, 1)
  }
  // 返回列表
  handleBackToList()
}

// 监听shouldReturnToList状态变化
watch(shouldReturnToList, (newValue) => {
  if (newValue && selectedFormula.value) {
    // 当shouldReturnToList为true且有选中的公式时，返回列表
    selectedFormula.value = null
  }
})

// 监听标签页切换，当切换到"已有公式"时重新加载数据
watch(activeKey, async (newKey) => {
  if (newKey === 'existing') {
    // 切换到"已有公式"标签页时，重新加载数据
    loading.value = true
    const pageNum = pagination.value.current
    const pageSize = pagination.value.pageSize
    try {
      const res = await getFormulaPageList({ pageNum, pageSize })
      if (res?.code === '00000') {
        loading.value = false
        tableColumns.value = res.data.columns

        // 图片列使用 className 以便精准控制列宽与内边距
        const imgCol = tableColumns.value.find(
          (c: any) => c.key === 'formula_image' || c.dataIndex === 'formula_image'
        ) as any
        if (imgCol) {
          imgCol.className = (imgCol.className ? imgCol.className + ' ' : '') + 'formula-image-col'
        }

        tableColumns.value.push({
          title: '操作',
          key: 'action',
          dataIndex: 'action',
        })
        tableData.value = res.data.dataSource.map((item: any) => ({
          ...item,
          key: `${item.id}_${item.model_type}`,
        }))
        pagination.value.total = res.data.totalCount
      }
    } catch (error) {
      console.error('加载已有公式失败:', error)
      loading.value = false
    }
  }
})
</script>
<style scoped>
.preview-panel {
  flex: 1;
  padding: 16px 16px 0px 16px;
  background: #f0f2f5;
  /* background-color: #fff; */
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
.full-tabs {
  width: 100%;
  background: #fff;
  border-top: 1px solid #e8e8e8;
}

.full-tabs :deep(.ant-tabs-nav) {
  padding: 0 16px;
}
.full-tabs :deep(.ant-tabs-nav),
.full-tabs :deep(.ant-tabs-content-holder) {
  background: #fff;
}
.file-preview-card {
  width: 100%;
  min-width: 0;
  background: #fff;
  border-radius: 2px;
  box-shadow: 0px 0px 12px 0px #00000040;
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
.tab-content {
  padding: 16px;
  background: #f0f2f5;
  margin: 16px;
  border-radius: 6px;
}
.select-item {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

/* 公式卡片区域样式 */
.formulas-section {
  width: 100%;
  /* margin-top: 24px; */

  flex: 1;
  padding: 0px 16px;
  background: #f0f2f5;
  /* background-color: #fff; */
  /* display: flex; */
  /* flex-direction: column; */
  /* align-items: flex-start; */
}

/* 公式网格 - 统一工业风格 */
.formulas-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--spacing-lg);
  width: 100%;
  padding: var(--spacing-md);
}

/* 公式卡片 - 改进设计 */
.formula-card {
  min-width: 0;
  background: var(--bg-primary);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-color);
  overflow: hidden;
  cursor: pointer;
  transition: var(--transition-base);
}

.formula-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
  border-color: var(--primary-color);
}

/* 公式卡片头部 - 工业蓝配色 */
.formula-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-sm) var(--spacing-md);
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-dark) 100%);
  color: #ffffff;
  font-size: 12px;
  position: relative;
}

/* 顶部装饰 */
.formula-card-header::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  right: 0;
  height: 2px;
  background: var(--primary-light);
}

.formula-card-header .formula-name {
  font-size: 12px;
  font-weight: 500;
  color: #ffffff !important;
}

.formula-r2 {
  font-size: 10px;
  background: rgba(255, 255, 255, 0.2);
  padding: 1px 6px;
  border-radius: 3px;
  color: #ffffff;
}

/* 公式Latex区域 */
.formula-latex-section {
  padding: var(--spacing-md);
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 72px;
}

.formula-latex-img {
  max-height: 64px;
  width: auto;
  object-fit: contain;
}

/* 公式预测区域 */
.formula-prediction-section {
  padding: var(--spacing-xs);
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 240px;
  background: var(--bg-primary);
}

.formula-prediction-img {
  max-height: 240px;
  width: 100%;
  object-fit: contain;
}

/* 公式指标 */
.formula-metrics {
  display: flex;
  justify-content: space-between;
  padding: var(--spacing-xs) var(--spacing-sm);
  background: var(--bg-tertiary);
  font-size: 10px;
  color: var(--text-secondary);
  border-top: 1px solid var(--border-color);
}

/* 删除重复的.formula-name定义，避免覆盖卡片头部的白色文字 */

.formula-card-content {
  padding: 16px;
}

.formula-card-content p {
  margin: 0;
  color: #666;
  font-size: 14px;
  line-height: 1.5;
}

.table-thumb {
  width: auto;
  height: 100%;
  object-fit: contain;
  display: block;
}

.table-image-cell {
  width: 300px;
  height: 80px;
  overflow: hidden;
  display: inline-block;
  line-height: 0;
}

:deep(td.formula-image-col) {
  padding: 2px !important;
  white-space: nowrap;
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

.input-params-container-single {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  margin-top: 16px;
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
