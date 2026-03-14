<template>
  <div class="preview-panel">
    <div class="preprocess-select-card">
      <div class="preview-title">
        <span>参数设置</span>
      </div>
      <div class="preprocess-select-content">
        <!-- 输入参数表 -->
        <div class="input-params-section">
          <a-form :model="inputParamsForm" layout="vertical" class="input-params-form">
            <div class="section-title">训练参数表</div>
            <div class="input-params-container">
              <div class="param-column">
                <div class="param-column-header">
                  <span class="param-column-title">通用模型结构参数</span>
                </div>
                <div class="param-column-content">
                  <a-form-item name="model_name">
                    <template #label>
                      <a-tooltip title="选择模型结构" placement="right">
                        <span>模型选择：</span>
                      </a-tooltip>
                    </template>
                    <a-select
                      v-model:value="inputParamsForm.model_name"
                      style="width: 100%"
                      allow-clear
                    >
                      <a-select-option value="LSTM">LSTM</a-select-option>
                      <a-select-option value="GRU">GRU</a-select-option>
                      <a-select-option value="BiLSTM">BiLSTM</a-select-option>
                      <a-select-option value="TCN">TCN</a-select-option>
                      <a-select-option value="Transformer">Transformer</a-select-option>
                      <a-select-option value="Transformer_KAN">Transformer_KAN</a-select-option>
                      <a-select-option value="BP">BP</a-select-option>
                      <a-select-option value="Autoformer">Autoformer</a-select-option>
                    </a-select>
                  </a-form-item>
                  <a-form-item name="hidden_size">
                    <template #label>
                      <a-tooltip title="隐藏层维度" placement="right">
                        <span>隐藏层维度：</span>
                      </a-tooltip>
                    </template>
                    <a-input-number
                      v-model:value="inputParamsForm.hidden_size"
                      :min="0"
                      :max="10000"
                      :step="1"
                      style="width: 100%"
                    />
                  </a-form-item>
                  <a-form-item name="num_layers">
                    <template #label>
                      <a-tooltip title="网络层数" placement="right">
                        <span>网络层数：</span>
                      </a-tooltip>
                    </template>
                    <a-input-number
                      v-model:value="inputParamsForm.num_layers"
                      :min="0"
                      :max="10000"
                      :step="1"
                      style="width: 100%"
                    />
                  </a-form-item>
                  <a-form-item name="dropout">
                    <template #label>
                      <a-tooltip title="Dropout概率" placement="right">
                        <span>Dropout概率：</span>
                      </a-tooltip>
                    </template>
                    <a-input-number
                      v-model:value="inputParamsForm.dropout"
                      :min="0"
                      :max="1"
                      :step="0.1"
                      style="width: 100%"
                    />
                  </a-form-item>
                </div>
              </div>

              <div class="param-column">
                <div class="param-column-header">
                  <span class="param-column-title">TCN相关参数</span>
                </div>
                <div class="param-column-content">
                  <a-form-item name="num_channels">
                    <template #label>
                      <a-tooltip title="TCN中每层通道数" placement="right">
                        <span>TCN通道数：</span>
                      </a-tooltip>
                    </template>
                    <div class="range-inputs">
                      <a-input
                        v-model:value="inputParamsForm.num_channels"
                        allow-clear
                        style="width: 100%"
                      />
                    </div>
                  </a-form-item>
                  <a-form-item name="kernel_size">
                    <template #label>
                      <a-tooltip title="TCN中卷积核大小" placement="right">
                        <span>TCN卷积核大小：</span>
                      </a-tooltip>
                    </template>
                    <a-input-number
                      v-model:value="inputParamsForm.kernel_size"
                      :min="0"
                      :max="10000"
                      :step="1"
                      style="width: 100%"
                    />
                  </a-form-item>
                </div>
                <div class="param-column-header">
                  <span class="param-column-title">Transformer相关参数</span>
                </div>
                <div class="param-column-content">
                  <a-form-item name="num_heads">
                    <template #label>
                      <a-tooltip title="Transformer多头注意力数" placement="right">
                        <span>Transformer注意力头数：</span>
                      </a-tooltip>
                    </template>
                    <a-input-number
                      v-model:value="inputParamsForm.num_heads"
                      :min="0"
                      :max="10000"
                      :step="1"
                      style="width: 100%"
                    />
                  </a-form-item>
                  <a-form-item name="hidden_space">
                    <template #label>
                      <a-tooltip title="Transformer注意力空间维度" placement="right">
                        <span>Transformer注意力空间维度：</span>
                      </a-tooltip>
                    </template>
                    <a-input-number
                      v-model:value="inputParamsForm.hidden_space"
                      :min="0"
                      :max="10000"
                      :step="1"
                      style="width: 100%"
                    />
                  </a-form-item>
                </div>
              </div>

              <!-- 输入设置类 -->
              <div class="param-column">
                <div class="param-column-header">
                  <span class="param-column-title">Autoformer相关参数</span>
                </div>
                <div class="param-column-content">
                  <a-form-item name="e_layers">
                    <template #label>
                      <a-tooltip title="Autoformer编码器层数" placement="right">
                        <span>Autoformer编码器层数：</span>
                      </a-tooltip>
                    </template>
                    <a-input-number
                      v-model:value="inputParamsForm.e_layers"
                      :min="0"
                      :max="10000"
                      :step="1"
                      style="width: 100%"
                    />
                  </a-form-item>
                  <a-form-item name="d_ff">
                    <template #label>
                      <a-tooltip title="前馈神经网络维度" placement="right">
                        <span>前馈网络维度：</span>
                      </a-tooltip>
                    </template>
                    <a-input-number
                      v-model:value="inputParamsForm.d_ff"
                      :min="0"
                      :max="10000"
                      :step="1"
                      style="width: 100%"
                    />
                  </a-form-item>
                  <a-form-item name="moving_avg">
                    <template #label>
                      <a-tooltip title="Autoformer滑动平均窗口大小" placement="right">
                        <span>Autoformer滑动平均窗口大小：</span>
                      </a-tooltip>
                    </template>
                    <a-input-number
                      v-model:value="inputParamsForm.moving_avg"
                      :min="0"
                      :max="10000"
                      :step="1"
                      style="width: 100%"
                    />
                  </a-form-item>
                  <a-form-item name="factor">
                    <template #label>
                      <a-tooltip title="AutoCorrelation的top-k因子" placement="right">
                        <span>自相关top-k因子：</span>
                      </a-tooltip>
                    </template>
                    <a-input-number
                      v-model:value="inputParamsForm.factor"
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
                  <span class="param-column-title">训练控制参数</span>
                </div>
                <div class="param-column-content">
                  <a-form-item name="activation">
                    <template #label>
                      <a-tooltip title="激活函数" placement="right">
                        <span>激活函数：</span>
                      </a-tooltip>
                    </template>
                    <a-select
                      v-model:value="inputParamsForm.activation"
                      style="width: 100%"
                      allow-clear
                    >
                      <a-select-option value="relu">relu</a-select-option>
                      <a-select-option value="leaky_relu">leaky_relu</a-select-option>
                      <a-select-option value="elu">elu</a-select-option>
                      <a-select-option value="gelu">gelu</a-select-option>
                      <a-select-option value="sigmoid">sigmoid</a-select-option>
                      <a-select-option value="tanh">tanh</a-select-option>
                      <a-select-option value="softplus">softplus</a-select-option>
                      <a-select-option value="silu">silu</a-select-option>
                      <a-select-option value="none">none</a-select-option>
                    </a-select>
                  </a-form-item>
                  <!-- <a-form-item name="use_layer_norm">
                    <template #label>
                      <a-tooltip title="是否使用LayerNorm" placement="right">
                        <span>学习率：</span>
                      </a-tooltip>
                    </template>
                    <a-select
                      v-model:value="inputParamsForm.use_layer_norm"
                      style="width: 100%"
                      allow-clear
                    >
                      <a-select-option :value="true">true</a-select-option>
                      <a-select-option :value="false">false</a-select-option>
                    </a-select>
                  </a-form-item> -->
                  <a-form-item name="learning_rate">
                    <template #label>
                      <a-tooltip title="学习率" placement="right">
                        <span>学习率：</span>
                      </a-tooltip>
                    </template>
                    <a-input-number
                      v-model:value="inputParamsForm.learning_rate"
                      :min="0"
                      :max="1"
                      :step="0.0001"
                      style="width: 100%"
                    />
                  </a-form-item>
                  <a-form-item name="loss">
                    <template #label>
                      <a-tooltip title="回归任务损失函数类型" placement="right">
                        <span>损失函数类型：</span>
                      </a-tooltip>
                    </template>
                    <a-select v-model:value="inputParamsForm.loss" style="width: 100%" allow-clear>
                      <a-select-option value="mse">mse</a-select-option>
                      <a-select-option value="mae">mae</a-select-option>
                      <a-select-option value="huber">huber</a-select-option>
                      <a-select-option value="smooth_l1">smooth_l1</a-select-option>
                      <a-select-option value="log_cosh">log_cosh</a-select-option>
                      <a-select-option value="quantile">quantile</a-select-option>
                      <a-select-option value="mape">mape</a-select-option>
                      <a-select-option value="smape">smape</a-select-option>
                    </a-select>
                  </a-form-item>
                </div>
                <div class="param-column-header">
                  <span class="param-column-title">正则化与归一化参数</span>
                </div>
                <div class="param-column-content">
                  <a-form-item name="num_epochs">
                    <template #label>
                      <a-tooltip title="训练轮数" placement="right">
                        <span>训练轮数：</span>
                      </a-tooltip>
                    </template>
                    <a-input-number
                      v-model:value="inputParamsForm.num_epochs"
                      :min="0"
                      :max="10000"
                      :step="1"
                      style="width: 100%"
                    />
                  </a-form-item>
                   <a-form-item name="use_layer_norm">
                    <template #label>
                      <a-tooltip title="是否使用LayerNorm" placement="right">
                        <span>是否使用LayerNorm：</span>
                      </a-tooltip>
                    </template>
                    <a-select
                      v-model:value="inputParamsForm.use_layer_norm"
                      style="width: 100%"
                      allow-clear
                    >
                      <a-select-option :value="true">true</a-select-option>
                      <a-select-option :value="false">false</a-select-option>
                    </a-select>
                  </a-form-item>
                </div>
              </div>
            </div>
            <a-button type="primary" @click="handleTrain" :loading="trainLoading"
            style="margin-top: 16px;"
                >开始训练</a-button
              >
          </a-form>
        </div>
      </div>
    </div>
    <div class="preprocess-select-card">
      <div
        class="preview-title"
        style="display: flex; justify-content: space-between; align-items: center"
      >
        <span>模型拟合情况</span>
        <a-button v-if="trainResult" type="primary" style="margin-left: 8px">保存模型</a-button>
      </div>
      <div
        class="preprocess-select-content"
        style="display: flex; justify-content: center; align-items: stretch; height: 1000px"
      >
        <div class="block">
          <div class="block-title">运行日志</div>
          <div class="block-content">
            <pre>
<template v-for="(log, index) in state.logs" :key="index">
[{{ log.type}}] {{ log.content }}
</template>
</pre>
          </div>
        </div>
        <div class="block">
          <div class="block-title">训练集拟合图</div>
          <div
            class="block-content"
            style="display: flex; justify-content: center; align-items: center"
            v-if="!enabled"
          >
            <a-empty description="暂无结果，请点击开始训练"></a-empty>
          </div>
          <div class="block-content" v-else>
            <div ref="trainChartRef" style="width: 100%; height: 100%"></div>
          </div>
        </div>
        <div class="block">
          <div class="block-title">验证集拟合图</div>
          <div
            class="block-content"
            style="display: flex; justify-content: center; align-items: center"
            v-if="!enabled"
          >
            <a-empty description="暂无结果，请点击开始训练"></a-empty>
          </div>
          <div class="block-content" v-else>
            <div ref="verifyChartRef" style="width: 100%; height: 100%"></div>
          </div>
        </div>
      </div>
    </div>
    <div class="preprocess-select-card">
      <div
        class="preview-title"
        style="display: flex; justify-content: space-between; align-items: center"
      >
        <span>模型训练损失结果</span>
        <a-button v-if="trainResult" type="primary" style="margin-left: 8px">保存模型</a-button>
      </div>
      <div
        class="preprocess-select-content"
        style="display: flex; justify-content: center; align-items: center; height: 800px"
      >
        <a-empty description="暂无结果，请点击开始训练" v-if="!enabled"></a-empty>
        <div ref="trainLossChartRef" style="width: 100%; height: 100%" v-else></div>
      </div>
    </div>
    <div class="preprocess-select-card">

      <div class="dataset-selection-section">
          <div class="section-title">测试参数表</div>
          <a-form layout="vertical" class="param-form-full" :model="formState">
            <a-row gutter="16" style="margin-bottom: 12px">
              <a-col :span="12">
                <a-form-item>
                  <template #label>
                    <span> 测试集 </span>
                  </template>
                  <a-select
                    mode="multiple"
                    :max-tag-count="1"
                    class="param-select-full"
                    v-model:value="testTags"
                    :options="testSetOptions"
                    :tagRender="testSetTagRender"
                    @change="onTestSetChange"
                  >
                    <template #suffixIcon>
                      <svg
                        t="1751614777434"
                        class="icon"
                        viewBox="0 0 1024 1024"
                        version="1.1"
                        xmlns="http://www.w3.org/2000/svg"
                        p-id="8073"
                        width="12.25px"
                        height="12.25px"
                      >
                        <path
                          d="M512.002558 64.24521c-247.292176 0-447.75786 200.464661-447.75786 447.756837 0 247.287059 200.464661 447.752744 447.75786 447.752744 247.286036 0 447.75172-200.464661 447.75172-447.752744C959.754279 264.710894 759.288594 64.24521 512.002558 64.24521zM512.010745 735.87586c-20.602224 0-37.319977-16.718777-37.319977-37.323047 0-20.597107 16.717753-37.319977 37.319977-37.319977 20.60427 0 37.297464 16.72287 37.297464 37.319977C549.308209 719.158107 532.613992 735.87586 512.010745 735.87586zM549.308209 567.969733c0 20.600177-16.693194 37.293371-37.297464 37.293371-20.602224 0-37.319977-16.693194-37.319977-37.293371L474.690768 325.420581c0-20.605294 16.717753-37.297464 37.319977-37.297464 20.60427 0 37.297464 16.693194 37.297464 37.297464L549.308209 567.969733z"
                          fill="#1890FF"
                          p-id="8074"
                          data-spm-anchor-id="a313x.search_index.0.i8.264b3a81LVp7CK"
                          class="selected"
                        ></path>
                      </svg>
                    </template>
                  </a-select>
                </a-form-item>
              </a-col>
              <a-col :span="12">
                <a-form-item>
                  <template #label>
                    <span> 模型 </span>
                  </template>
                  <a-select
                    class="param-select-full"
                    v-model:value="trainSetTags"
                    :options="trainSetOptions"
                    @change="handleChange_select1"
                  >
                  </a-select>
                </a-form-item>
              </a-col>
            </a-row>
            <div
              style="
                display: flex;
                justify-content: flex-start;
                align-items: center;
                width: 100%;
                margin-top: 12px;
              "
            >
              <a-button
                type="primary"
                @click="handleTest"
                :loading="testLoading"
                >开始测试</a-button
              >
            </div>
          </a-form>
        </div>
      <div
        class="preview-title"
        style="display: flex; justify-content: space-between; align-items: center"
      >
        <span>模型测试结果</span>
        <a-button v-if="trainResult" type="primary" style="margin-left: 8px">保存模型</a-button>
      </div>
      <div
        class="preprocess-select-content"
        style="display: flex; flex-direction: column; height: 1000px"
      >
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

        <div class="echarts-row" style="flex: 1; min-height: 0">
          <div class="echart-col">
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
            <div
              class="echart-half"
              v-show="!showCharacter"
              style="display: flex; justify-content: center; align-items: center"
            >
              <a-spin v-show="originLoading" tip="模型测试中..." />
              <a-empty v-show="!originLoading" description="暂无结果，请选择数据"></a-empty>
            </div>
            <div ref="chart1Ref" class="echart-half" v-show="showCharacter"></div>
          </div>
          <div class="echart-col">
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
            <div
              class="echart-half"
              v-show="!showCharacter"
              style="display: flex; justify-content: center; align-items: center"
            >
              <a-spin v-show="originLoading" tip="模型测试中..." />
              <a-empty v-show="!originLoading" description="暂无结果，请选择数据"></a-empty>
            </div>
            <div ref="chart2Ref" class="echart-half" v-show="showCharacter"></div>
          </div>
          <div
            class="echart-col"
            v-show="!enabled2"
            style="display: flex; justify-content: center; align-items: center"
          >
            <a-spin v-show="testLoading" tip="模型测试中..." />
            <a-empty v-show="!testLoading" description="暂无结果，请点击开始测试"></a-empty>
          </div>
          <div class="echart-col" v-show="enabled2">
            <div ref="chart3Ref" class="echart-half"></div>
          </div>
          <div class="echart-col">
            <a-table :columns="columns" :data-source="tableData" bordered :pagination="false">
              <template #bodyCell="{ column, text }">
                <template v-if="column.dataIndex === 'name'">
                  <a>{{ text }}</a>
                </template>
              </template>
              <!-- <template #title>测试集输出误差表</template> -->
            </a-table>
          </div>
        </div>

        <!-- <template v-if="isTest">
          <a-spin tip="模型训练中..." />
        </template>
        <template v-else-if="trainResult">
          <div class="select-item" style="margin-bottom: 16px">
            <span class="select-label">选择数据：</span>
            <a-tree-select
              v-model:value="selectedData"
              :tree-data="dataOptions"
              :field-names="{ label: 'label', value: 'value', children: 'children', key: 'key' }"
              placeholder="请选择数据"
              allow-clear
              tree-default-expand-all
              style="width: 50%"
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
          <div class="echarts-row" style="flex: 1; min-height: 0">
            <div class="echart-col">
              <div ref="chart1Ref" class="echart-half"></div>
            </div>
            <div class="echart-col">
              <div ref="chart2Ref" class="echart-half"></div>
            </div>
            <div class="echart-col">
              <div ref="chart3Ref" class="echart-half"></div>
            </div>
          </div>
        </template>
        <template v-else>
          <img
            src="@/assets/无结果.svg"
            alt="无结果"
            style="width: 100%; height: 100%; object-fit: contain; opacity: 0.7"
          />
        </template> -->
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted, nextTick, watch, onUnmounted, reactive, h, computed, onActivated } from 'vue'
import { Tag, message } from 'ant-design-vue'
import * as echarts from 'echarts'
import { useStore } from 'vuex'
import {
  getAddSelect,
  getTreeData,
  startTrain,
  getModelTestingResult,
  getTestOutputResult,
  parameter
} from '@/utils/api'
import { eventBus, state } from '@/socket'
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
} from '@/components/echarts/echartsHelper'
import { findParentDirectory } from '@/utils/tree'

watch(state.logs, (val) => {
  // if (val) nextTick(renderChart)
})

const formState = reactive({})
const store = useStore()

// 输入参数表单数据
const inputParamsForm = reactive({
  model_name: 'Transformer',
  hidden_size: 8,
  num_layers: 5,
  dropout: 0.1,
  num_channels: '25,50,25',
  kernel_size: 3,
  num_heads: 4,
  hidden_space: 8,
  e_layers: 2,
  d_ff: 64,
  moving_avg: 24,
  factor: 4,
  activation: 'tanh',
  use_layer_norm: false,
  loss: 'mae',
  num_epochs: 150,
  learning_rate: 0.0005,
})
const selectedData = ref<number | null>(null)
const trainLoading = ref(false)
const testLoading = ref(false)
const originLoading = ref(false)
const enabled = ref(false)
const enabled2 = ref(false)
const showCharacter = ref(false)

const testTags = ref<number[]>([])
// trainSetTags 是字符串
const trainSetTags = ref<string>('')
const testSetOptions = ref<{ label: string; value: number }[]>([])
// 目录 id -> 该目录下文件名（非 directory）拼接文本
const dirIdToFilesText = ref<Record<number, string>>({})
// 目录 id -> 该目录下文件名数组（非 directory）
const dirIdToFilesList = ref<Record<number, string[]>>({})
const columns = [
  {
    title: 'Metric',
    dataIndex: 'metric',
  },
  {
    title: 'Value',
    dataIndex: 'value',
  },
]
interface DataItem {
  key: number
  metric: string
  value: number
}
const tableData = ref<DataItem[]>([])
// 自定义 tag 渲染：显示该目录下的文件列表
const testSetTagRender = (props: any) => {
  const id = props.value as number
  const files = dirIdToFilesList.value[id]
  const fallbackText = dirIdToFilesText.value[id] || String(props.label)

  // 如果没有文件列表，退化为单个标签
  if (!files || files.length === 0) {
    return h(
      Tag,
      {
        // closable: props.closable,
        // onClose: (e: MouseEvent) => {
        //   e.preventDefault()
        //   props.onClose && props.onClose()
        // },
        style: {
          marginRight: '4px',
          maxWidth: '240px',
        },
        title: fallbackText,
      },
      () =>
        h(
          'span',
          {
            style: {
              display: 'inline-block',
              maxWidth: '200px',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              verticalAlign: 'bottom',
            },
          },
          fallbackText
        )
    )
  }

  // 返回一个容器，内部展示该目录下的多个文件 tag
  return h(
    'span',
    {
      style: {
        display: 'inline-flex',
        flexWrap: 'wrap',
        gap: '4px',
        alignItems: 'center',
        maxWidth: '100%',
      },
      title: fallbackText,
    },
    files.map((name) =>
      h(
        Tag,
        {
          // closable: props.closable,
          // onClose: (e: MouseEvent) => {
          //   // 关闭任意一个文件 tag，视为移除该目录选择
          //   e.preventDefault()
          //   props.onClose && props.onClose()
          // },
          style: {
            marginRight: '0',
            maxWidth: '240px',
          },
          title: name,
        },
        () =>
          h(
            'span',
            {
              style: {
                display: 'inline-block',
                maxWidth: '200px',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                verticalAlign: 'bottom',
              },
            },
            name
          )
      )
    )
  )
}
const trainSetOptions = ref<{ label: string; value: string, type: string }[]>([])
const targetname_value = ref<string>('')
const trainSetCascaderValue = ref([])
const treeData = ref<MyTreeNode[]>([])
const parentTreeId = ref(0)
const dataOptions = computed(() => {
  const res = getOptions(treeData.value)
  return res
})
type MyTreeNode = {
  title: string
  key: string
  type: string
  id: number
  children?: MyTreeNode[]
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
  console.log('n:', n)
  console.log(parentTreeId.value)
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

// 训练相关
const isTraining = ref(false)
const isTest = ref(false)
// const trainResult = ref<null | { accuracy: number; loss: number }>(null)
const trainResult = ref<boolean | null>(true)

const chartRef = ref<HTMLElement | null>(null)
const trainChartRef = ref<HTMLElement | null>(null)
const verifyChartRef = ref<HTMLElement | null>(null)
const trainLossChartRef = ref<HTMLElement | null>(null)
const chart1Ref = ref<HTMLDivElement | null>(null)
const chart2Ref = ref<HTMLDivElement | null>(null)
const chart3Ref = ref<HTMLDivElement | null>(null)
const chart1Option = ref({})
const chart2Option = ref({})
const chart3Option = ref({})
let trainChartInstance: echarts.ECharts | null = null
let verifyChartInstance: echarts.ECharts | null = null
let trainLossChartInstance: echarts.ECharts | null = null
let chart1Instance: echarts.ECharts | null = null
let chart2Instance: echarts.ECharts | null = null
let chart3Instance: echarts.ECharts | null = null
const trainSeriesMap: Record<string, number> = {}
const verifySeriesMap: Record<string, number> = {}
const trainLossSeriesMap: Record<string, number> = {}
const seriesDataCache: Record<string, [number, number][]> = {}
let resizeObserver: ResizeObserver | null = null
interface Point {
  seriesName: string
  x: number
  y: number
}

const chartTypes = ['train', 'verify', 'trainLoss']

// function renderChart() {
//   if (!chartRef.value) return
//   if (!chartInstance) {
//     chartInstance = echarts.init(chartRef.value)
//   }
//   chartInstance.setOption({
//     tooltip: {
//       trigger: 'axis',
//       axisPointer: {
//         type: 'cross',
//         label: {
//           backgroundColor: '#6a7985',
//         },
//       },
//       formatter: function (params: any) {
//         let result = `<div style="font-weight: bold; margin-bottom: 8px;">${params[0].axisValue}</div>`
//         params.forEach((param: any) => {
//           const color = param.color || '#666'
//           const value = Array.isArray(param.value) ? param.value[1] : param.value
//           result += `<div style="display: flex; align-items: center; margin: 4px 0;">
//             <span style="display: inline-block; width: 10px; height: 10px; background: ${color}; margin-right: 8px; border-radius: 50%;"></span>
//             <span style="font-weight: bold;">${param.seriesName}:</span>
//             <span style="margin-left: 8px;">${value}</span>
//           </div>`
//         })
//         return result
//       },
//     },
//     legend: {
//       data: ['Training Loss', 'Validation Loss'],
//       orient: 'horizontal',
//       bottom: 0,
//       symbol: 'line',
//     },
//     xAxis: {
//       type: 'category',
//       data: xAxisData,
//       splitLine: {
//         show: true,
//         lineStyle: {
//           type: 'dashed',
//         },
//       },
//     },
//     yAxis: {
//       type: 'value',
//       min: 0,
//       max: 0.0018,
//       splitLine: {
//         show: true,
//         lineStyle: {
//           type: 'dashed',
//         },
//       },
//     },
//     series: [
//       {
//         name: 'Training Loss',
//         type: 'line',
//         data: trainLossData,
//         lineStyle: { color: '#1890FF' },
//         itemStyle: { color: '#1890FF' },
//         smooth: true,
//       },
//       {
//         name: 'Validation Loss',
//         type: 'line',
//         data: valLossData,
//         lineStyle: { color: '#FF4D4F' },
//         itemStyle: { color: '#FF4D4F' },
//         smooth: true,
//       },
//     ],
//   })
// }

// watch(trainResult, (val) => {
//   if (val) nextTick(renderChart)
// })

const appendPoints = (
  points: Point[],
  chart: echarts.ECharts | null,
  seriesMap: Record<string, number>,
  replace = false
) => {
  if (!chart) return
  const option = chart.getOption() as any
  const optionSeries = (option.series as any[]) || []
  const optionLegendData = ((option.legend as any)?.[0]?.data as string[]) || []

  points.forEach(({ seriesName, x, y }) => {
    // 新折线创建
    if (!(seriesName in seriesMap)) {
      const idx = optionSeries.length
      seriesMap[seriesName] = idx

      chart.setOption({
        series: [
          ...optionSeries,
          { name: seriesName, type: 'line', showSymbol: true, data: [] }, // showSymbol=true 显示小圆点
        ],
        legend: { data: [...optionLegendData, seriesName] },
      })
    }

    // 只 append 当前单点，实现单点出现效果
    chart.appendData({
      seriesIndex: seriesMap[seriesName],
      data: [[x, y]],
    })
  })
}

const appendPoints2 = (
  points: Point[],
  chart: echarts.ECharts | null,
  seriesMap: Record<string, number>
) => {
  if (!chart || !points.length) return

  // 按 seriesName 分组处理数据点
  const pointsBySeries: Record<string, Point[]> = {}
  points.forEach((point) => {
    if (!pointsBySeries[point.seriesName]) {
      pointsBySeries[point.seriesName] = []
    }
    pointsBySeries[point.seriesName].push(point)
  })

  // 处理每个 series 的数据
  Object.entries(pointsBySeries).forEach(([seriesName, seriesPoints]) => {
    let seriesIndex = seriesMap[seriesName]

    if (seriesIndex === undefined) {
      // 新 series - 创建新的数据系列
      const currentOption = chart.getOption()
      const currentSeries = (currentOption.series as any[]) || []
      const currentLegendData = ((currentOption.legend as any)?.[0]?.data as string[]) || []

      seriesIndex = currentSeries.length
      seriesMap[seriesName] = seriesIndex

      // 初始化缓存
      seriesDataCache[seriesName] = []

      // 准备新 series 的数据
      const newSeriesData: [number, number][] = seriesPoints.map((point) => [point.x, point.y])
      seriesDataCache[seriesName] = [...newSeriesData]

      // 创建新的 series 配置
      const newSeries = {
        id: seriesName,
        name: seriesName,
        type: 'line',
        showSymbol: true,
        symbolSize: 4,
        lineStyle: {
          width: 2,
        },
        itemStyle: {
          color: undefined, // 让 echarts 自动分配颜色
        },
        animation: true,
        animationDuration: 300,
        data: newSeriesData,
      }

      // 更新图表配置，添加新的 series 和 tooltip
      chart.setOption(
        {
          tooltip: {
            trigger: 'item',
            axisPointer: {
              type: 'cross',
              label: {
                backgroundColor: '#6a7985',
              },
            },
            formatter: function (params: any) {
              return `
        ${params.seriesName}<br/>
        x: ${params.value[0]}<br/>
        y: ${params.value[1]}
      `
            },
          },
          series: [...currentSeries, newSeries],
          legend: {
            data: [...new Set([...currentLegendData, seriesName])],
          },
        },
        false
      ) // false 表示合并，不覆盖现有数据
    } else {
      // 已存在的 series - 增量添加数据点
      const newDataPoints: [number, number][] = seriesPoints.map((point) => [point.x, point.y])

      // 更新缓存
      if (!seriesDataCache[seriesName]) {
        seriesDataCache[seriesName] = []
      }
      seriesDataCache[seriesName].push(...newDataPoints)

      // 获取最新的图表配置
      const currentOption = chart.getOption()
      const currentSeries = (currentOption.series as any[]) || []

      // 验证 series 是否存在
      if (currentSeries[seriesIndex]) {
        // 使用 setOption 进行增量渲染，确保数据不丢失
        const updatedSeries = [...currentSeries]
        const existingData = updatedSeries[seriesIndex].data || []
        updatedSeries[seriesIndex] = {
          ...updatedSeries[seriesIndex],
          data: [...existingData, ...newDataPoints],
        }

        chart.setOption(
          {
            series: updatedSeries,
          },
          false
        )
      } else {
        console.warn(`Series index ${seriesIndex} does not exist for series: ${seriesName}`)

        // 如果 series 不存在，重新创建
        const existingData = seriesDataCache[seriesName] || []
        const currentLegendData = ((currentOption.legend as any)?.[0]?.data as string[]) || []

        chart.setOption(
          {
            series: [
              ...currentSeries,
              {
                id: seriesName,
                name: seriesName,
                type: 'line',
                showSymbol: true,
                symbolSize: 4,
                lineStyle: { width: 2 },
                animation: true,
                animationDuration: 300,
                data: existingData,
              },
            ],
            legend: {
              data: [...new Set([...currentLegendData, seriesName])],
            },
          },
          false
        )
      }
    }
  })

  // 可选：限制缓存大小以防止内存泄漏
  Object.keys(seriesDataCache).forEach((seriesName) => {
    if (seriesDataCache[seriesName].length > 1000) {
      seriesDataCache[seriesName] = seriesDataCache[seriesName].slice(-500)
    }
  })

  console.log('Updated seriesDataCache:', seriesDataCache)
}

const initChart = (refEl: HTMLElement | null) => {
  if (!refEl) return null
  const chart = echarts.init(refEl)
  chart.setOption({
    animation: true, // 开启动画，让单点出现更自然
    tooltip: {
      trigger: 'item',
      // axisPointer: {
      //   type: 'cross',
      //   label: {
      //     backgroundColor: '#6a7985',
      //   },
      // },
      formatter: function (params: any) {
        if(params.seriesName === undefined) return ''
        console.log("params", params)
        console.log(params.seriesName)
        console.log(params.value[0])
        return `
        ${params.seriesName}<br/>
        x: ${params.value[0]}<br/>
        y: ${params.value[1]}
      `
      },
    },
    xAxis: { type: 'value' },
    yAxis: { type: 'value' },
    series: [],
    legend: { data: [] },
  })
  return chart
}

onActivated(async () => {
  // 页面重新激活时执行的逻辑
  console.log('页面重新激活')
  // 页面加载时执行的初始化逻辑
  console.log('页面已加载')
  // test()
  const res = await getTreeData()
  if (res?.data) {
    const rawData = res.data[0]?.children ?? []
    treeData.value = patchTreeKeys(rawData)
    parentTreeId.value = res.data[0].id
    const dirOptions: { label: string; value: number }[] = []
    const dirToFiles: Record<number, string> = {}
    const dirToFilesList: Record<number, string[]> = {}

    const collect = (node: any) => {
      if (!node) return
      if (node.type === 'directory') {
        dirOptions.push({ label: node.title ?? node.name, value: node.id })
        const fileNames = Array.isArray(node.children)
          ? node.children
              .filter((c: any) => c.type !== 'directory')
              .map((c: any) => c.title ?? c.name)
          : []
        dirToFilesList[node.id] = fileNames
        dirToFiles[node.id] = fileNames.join(', ')
      }
      if (Array.isArray(node.children)) node.children.forEach(collect)
    }

    if (Array.isArray(res.data)) res.data.forEach(collect)
    else collect(res.data)

    testSetOptions.value = dirOptions
    dirIdToFilesText.value = dirToFiles
    dirIdToFilesList.value = dirToFilesList
  }

  const res2 = await getAddSelect()
  console.log('res2:', res2)
  if (res2) {
    // 显示 name，保存 id
    const best = res2.data['best-data'].map((t: any) => ({ label: t.name, value: t.id + '-best-data', type: 'best-data' }));
    const final = res2.data['final-data'].map((t: any) => ({ label: t.name, value: t.id + '-final-data', type: 'final-data' }));
    trainSetOptions.value = [...best, ...final];
  }
})



onMounted(async () => {

  trainChartInstance = initChart(trainChartRef.value)
  verifyChartInstance = initChart(verifyChartRef.value)
  trainLossChartInstance = initChart(trainLossChartRef.value)

  // 初始化三个图表
  chart1Instance = initChart(chart1Ref.value)
  chart2Instance = initChart(chart2Ref.value)
  chart3Instance = initChart(chart3Ref.value)

  // ---------- 监听 eventBus ----------
  eventBus.on('train', (points: Point[]) =>
    appendPoints(points, trainChartInstance, trainSeriesMap)
  )
  eventBus.on('verify', (points: Point[]) =>
    appendPoints(points, verifyChartInstance, verifySeriesMap)
  )
  eventBus.on('trainLoss', (points: Point[]) =>
    appendPoints2(points, trainLossChartInstance, trainLossSeriesMap)
  )

  // if (chartRef.value) {
  //   resizeObserver = new ResizeObserver(() => {
  //     resizeChart()
  //   })
  //   resizeObserver.observe(chartRef.value)
  // }

  //
})

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
    channelsForm
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
  updateCharts()
})

watch(
  showCharacter,
  async (val) => {
    if (val) {
      await nextTick()
      chart1Instance = initChart(chart1Ref.value)
      chart2Instance = initChart(chart2Ref.value)
    }
  },
  { immediate: true }
)

watch(
  enabled,
  async (val) => {
    if (val) {
      await nextTick()
      trainChartInstance = initChart(trainChartRef.value)
      verifyChartInstance = initChart(verifyChartRef.value)
      trainLossChartInstance = initChart(trainLossChartRef.value)
    }
  },
  { immediate: true }
)

// 模型测试结果
function test() {
  window.addEventListener('resize', resizeCharts)
  const c1 = ['CAL', 'HAZI', 'DEVI', 'AC', 'GR', 'RD', 'RS', 'SP']
  const c2 = ['CNL', 'DEN', 'GRSL', 'K', 'KTH', 'TH', 'PE']
  maxLenCurve.value = Math.max(c1.length, c2.length)
  testSetTags.value = c1
  testSetTags2.value = c2
  tagOptions.value = [...testSetTags.value, ...testSetTags2.value].map((tag) => ({
    label: tag,
    value: tag,
  }))
  allData.value = { ...data1, ...data2 }
  chart1Option.value = customOptions(c1, allData.value, buildCustomConfig(c1), channelsForm)
  chart2Option.value = customOptions(c2, allData.value, buildCustomConfig(c2), channelsForm2)
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
  console.log('~~~~~~~~~@@@@@@@@@@@:', config)
  return config
}

const buildCustomConfig2 = (tags: string[]) => {
  const config: Record<string, { lineStyle?: string; color?: string; range?: [number, number] }> =
    {}

  tags.forEach((tag, index) => {
    const tagConfig = indicatorsForm[tag] || {}
    config[tag] = {
      lineStyle: tagConfig.lineStyle || 'solid',
      color: tagConfig.color || colorArray[index] || '#000000',
      range: [-Infinity, Infinity],
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
  const a1 = channelsConfig.thickLineCount || 2 // 主分割线份数
  const a2 = channelsConfig.thinLineCount || 10 // 次分割线份数
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
  console.log('&&&&&&&&&&&&&:', xMin, xMax)

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
  const separatorSeries: any = {
    name: '',
    type: 'line',
    data: [],
    lineStyle: { color: 'transparent' },
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
  }
  series.push(separatorSeries)

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
    const logAxis: any = {
      type: 'log',
      logBase: 10,
      min: 0.1,
      max: logMax,
      splitLine: {
        show: true,
      },
      axisLabel: {
        color: '#666',
        margin: 8,
        formatter: (val: number) => val.toString(),
      },
    }
    xAxis.push(logAxis)
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
        console.log('mmmmmmmmmmin:', value.min)
        return Math.floor(value.min)
      },
      max: function (value: any) {
        console.log('mmmmmmmmmmax:', value.max)
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
        splitNumber:
          (channelsConfig?.depthThickInterval || 10) / (channelsConfig?.depthInterval || 1), // 在主刻度之间分成20份，每份间隔就是1
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

function resizeCharts() {
  if (chart1Instance) chart1Instance.resize()
  if (chart2Instance) chart2Instance.resize()
  if (chart3Instance) chart3Instance.resize()
  if (trainChartInstance) trainChartInstance.resize()
  if (verifyChartInstance) verifyChartInstance.resize()
  if (trainLossChartInstance) trainLossChartInstance.resize()
}

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

onUnmounted(() => {
  trainChartInstance?.dispose()
  verifyChartInstance?.dispose()
  trainLossChartInstance?.dispose()
  chart1Instance?.dispose()
  chart2Instance?.dispose()
  chart3Instance?.dispose()

  if (resizeObserver && chartRef.value) {
    resizeObserver.unobserve(chartRef.value)
    resizeObserver = null
  }
})

const handleChange_select1 = (value: number[]) => {
  console.log(`selected ${value}`)
}

// 只允许选择一个目录：若出现超过 1 个，则保留最后一个
const onTestSetChange = (value: number[]) => {
  if (Array.isArray(value) && value.length > 1) {
    testTags.value = [value[value.length - 1]]
  } else {
    testTags.value = value || []
  }
  // 将 testTags 存入全局 store
  store.commit('setTestTags', testTags.value)
  console.log('testTags:', testTags.value[0], typeof testTags.value[0])
}

function patchTreeKeys(nodes: MyTreeNode[], parentPath: string = ''): any[] {
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

// const loadTrainSetData = (selectedOptions: unknown[]) => {
//   const targetOption = selectedOptions[selectedOptions.length - 1] as Record<string, unknown>
//   targetOption.loading = true
//   setTimeout(() => {
//     if (targetOption.value === '西2斜A区') {
//       targetOption.children = [
//         { value: '西2斜A区-1', label: '西2斜A区-1', isLeaf: true },
//         { value: '西2斜A区-2', label: '西2斜A区-2', isLeaf: true },
//       ]
//     } else if (targetOption.value === '西2斜B区') {
//       targetOption.children = [
//         { value: '西2斜B区-1', label: '西2斜B区-1', isLeaf: true },
//         { value: '西2斜B区-2', label: '西2斜B区-2', isLeaf: true },
//       ]
//     }
//     targetOption.loading = false
//     trainSetOptions.value = [...trainSetOptions.value]
//   }, 800)
// }

const handleTrain = async () => {
  trainLoading.value = true
  enabled.value = true

  const res2 = await parameter(inputParamsForm)
  const res = await startTrain()
  if (res?.code === 200) {
    trainLoading.value = false
    // enabled.value = falseg
  } else {
    trainLoading.value = true
  }
  console.log('startTrain', res)
}

const handleTest = async () => {
  console.log(`-========`)
  testLoading.value = true
  enabled2.value = false
  const data = {
    dir_id: testTags.value[0],
    idm: Number((trainSetTags.value).split('-')[0]) || 0,
    file_id: file_id.value,
    predict_mode: false,
    type: trainSetOptions.value.find((item) => item.value === trainSetTags.value)?.type || 'best-data',
  }

  const res = await getTestOutputResult(data)
  if (res?.code === 200) {
    const entries = Object.entries(res.data.table)
    tableData.value = entries.map(([key, value], index) => {
      return {
        key: index,
        metric: key,
        value: value as number,
      }
    })
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
      resizeCharts()
    })
    testLoading.value = false
    enabled2.value = true
  } else {
    testLoading.value = true
    enabled2.value = false
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

// 添加缺失的处理器函数
const handleFeature1IconClick = () => {
  console.log('Feature1 icon clicked')
}

const handleIconHover = (event: MouseEvent) => {
  const target = event.target as HTMLElement
  if (target) {
    target.style.backgroundColor = '#f0f0f0'
  }
}

const handleIconLeave = (event: MouseEvent) => {
  const target = event.target as HTMLElement
  if (target) {
    target.style.backgroundColor = '#fff'
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
  min-height: 100%;
}
.preprocess-select-card {
  width: 100%;
  min-width: 320px;
  /* border-radius: 2px; */
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
  /* border-top-left-radius: 2px; */
  /* border-top-right-radius: 2px; */
}
.preprocess-select-content {
  padding: 16px;
  /* flex: 1;
  display: flex;
  align-items: center;
  padding: 0 24px;
  gap: 24;
  justify-content: space-between; */
}
.block {
  flex: 1;
  display: flex;
  flex-direction: column;
  flex-direction: flex-start;
  margin: 0 4px;
  /* border: 1px solid #ddd; */
}
.block-title {
  padding: 6px 8px;
  border-bottom: 1px solid #ddd;
}
.block-content {
  flex: 1;
  min-width: 0;
  overflow-y: auto; /* 每块内容自己滚动 */
  overflow-x: hidden;
  padding: 8px;
  box-sizing: border-box;
}
.block-content pre {
  margin: 0;
  white-space: pre-wrap; /* 保留换行，同时允许自动换行 */
  word-wrap: break-word; /* 长单词或长字符串强制换行 */
  word-break: break-all; /* 必要时在任意位置断行 */
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
.content-item {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: start;
  height: 100%;
  width: 100%;
}
.select-item {
  /* flex: 1; */
  display: flex;
  align-items: center;
  gap: 38px;
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

/* 三个图表样式 */
.echarts-row {
  display: flex;
  width: 100%;
  gap: 16px;
  margin-top: 16px;
  height: 100%;
  position: relative;
}
.echart-col {
  display: flex;
  flex-direction: column;
  width: 25%;
  height: 100%;
  padding: 5px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); /* 阴影 */
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.echart-half {
  width: 100%;
  height: 100%;
  min-width: 0;
  position: relative;
}

/* 新增的输入参数表样式 */
.input-params-section {
  margin-bottom: 24px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #161b25;
  margin-bottom: 16px;
  padding-bottom: 8px;
  /* border-bottom: 2px solid #1890ff; */
}

.input-params-form {
  background: #fff;
  /* border-radius: 6px; */
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.input-params-container {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.param-column {
  flex: 1;
  min-width: 280px;
  background: #fafafa;
  /* border-radius: 4px; */
  border: 1px solid #e8e8e8;
}

.param-column-header {
  background: #f0f0f0;
  padding: 8px 12px;
  border-bottom: 1px solid #e8e8e8;
  /* border-radius: 4px 4px 0 0; */
}

.param-column-title {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.param-column-content {
  padding: 12px;
}

.param-column-content .ant-form-item {
  margin-bottom: 16px;
}

.param-column-content .ant-form-item:last-child {
  margin-bottom: 0;
}

.dataset-selection-section {
  background: #fff;
  /* border-radius: 6px; */
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
</style>
