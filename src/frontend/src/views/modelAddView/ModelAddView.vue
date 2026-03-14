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
            <div class="train-file-row">
              <div class="train-file-info">
                <span class="train-file-label">
                  <svg class="train-file-icon" viewBox="0 0 1024 1024" width="16" height="16">
                    <path d="M880 112H144c-17.7 0-32 14.3-32 32v736c0 17.7 14.3 32 32 32h736c17.7 0 32-14.3 32-32V144c0-17.7-14.3-32-32-32zM368 744c0 4.4-3.6 8-8 8h-80c-4.4 0-8-3.6-8-8V280c0-4.4 3.6-8 8-8h80c4.4 0 8 3.6 8 8v464zm192-280c0 4.4-3.6 8-8 8h-80c-4.4 0-8-3.6-8-8V280c0-4.4 3.6-8 8-8h80c4.4 0 8 3.6 8 8v184zm192 72c0 4.4-3.6 8-8 8h-80c-4.4 0-8-3.6-8-8V280c0-4.4 3.6-8 8-8h80c4.4 0 8 3.6 8 8v256z" fill="currentColor"/>
                  </svg>
                  训练文件：
                </span>
                <a-button class="train-file-btn" @click="trainFilesModalVisible = true">
                  <template #icon>
                    <svg viewBox="0 0 1024 1024" width="14" height="14">
                      <path d="M854.6 288.6L639.4 73.4c-6-6-14.1-9.4-22.6-9.4H192c-17.7 0-32 14.3-32 32v832c0 17.7 14.3 32 32 32h640c17.7 0 32-14.3 32-32V311.3c0-8.5-3.4-16.7-9.4-22.7zM790.2 326H602V137.8L790.2 326zm1.8 562H232V136h302v216a42 42 0 0042 42h216v494z" fill="currentColor"/>
                      <path d="M544 472c0-4.4-3.6-8-8-8h-48c-4.4 0-8 3.6-8 8v108H372c-4.4 0-8 3.6-8 8v48c0 4.4 3.6 8 8 8h108v108c0 4.4 3.6 8 8 8h48c4.4 0 8-3.6 8-8V644h108c4.4 0 8-3.6 8-8v-48c0-4.4-3.6-8-8-8H544V472z" fill="currentColor"/>
                    </svg>
                  </template>
                  选择文件（可多选）
                </a-button>
                <a-tag v-if="selectedTrainFileIds.length" color="blue" class="train-file-count">
                  已选 {{ selectedTrainFileIds.length }} 个文件
                </a-tag>
                <a-button v-if="selectedTrainFileIds.length" type="text" danger size="small" class="train-file-clear" @click="clearTrainFiles">
                  <template #icon>
                    <svg viewBox="0 0 1024 1024" width="12" height="12">
                      <path d="M563.8 512l262.5-312.9c4.4-5.2 0.7-13.1-6.1-13.1h-79.8c-4.7 0-9.2 2.1-12.3 5.7L511.6 449.8 295.1 191.7c-3-3.6-7.5-5.7-12.3-5.7H203c-6.8 0-10.5 7.9-6.1 13.1L459.4 512 196.9 824.9c-4.4 5.2-0.7 13.1 6.1 13.1h79.8c4.7 0 9.2-2.1 12.3-5.7l216.5-258.1 216.5 258.1c3 3.6 7.5 5.7 12.3 5.7h79.8c6.8 0 10.5-7.9 6.1-13.1L563.8 512z" fill="currentColor"/>
                    </svg>
                  </template>
                  清空
                </a-button>
              </div>
            </div>
            <div class="train-action-row">
              <a-button type="primary" class="train-start-btn" @click="handleTrain" :loading="trainLoading" :disabled="isTraining">
                <template #icon v-if="!trainLoading">
                  <svg viewBox="0 0 1024 1024" width="14" height="14">
                    <path d="M512 64C264.6 64 64 264.6 64 512s200.6 448 448 448 448-200.6 448-448S759.4 64 512 64zm144.1 454.9L437.7 677.8c-14.2 9.5-33.2-.6-33.2-17.8V363.9c0-17.2 19-27.3 33.2-17.8l218.4 158.9c12.5 9.1 12.5 26.8 0 35.9z" fill="currentColor"/>
                  </svg>
                </template>
                开始训练
              </a-button>
              <a-button type="primary" danger class="train-stop-btn" @click="handleStopTrain" :loading="stopLoading" :disabled="!isTraining">
                <template #icon v-if="!stopLoading">
                  <svg viewBox="0 0 1024 1024" width="14" height="14">
                    <path d="M512 64C264.6 64 64 264.6 64 512s200.6 448 448 448 448-200.6 448-448S759.4 64 512 64zm234.8 736.5L223.5 277.2c16-19.7 34-37.7 53.7-53.7l523.3 523.3c-16 19.6-34 37.7-53.7 53.7z" fill="currentColor"/>
                  </svg>
                </template>
                训练中止
              </a-button>
            </div>
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
        <div class="block log-block">
          <div class="block-title log-titlebar">
            <div class="log-titlebar-left">
              <span class="log-title-text">运行日志</span>
              <a-tag :color="state.isConnected ? 'green' : 'red'" class="log-status-tag">
                {{ state.isConnected ? '已连接' : '未连接' }}
              </a-tag>
              <a-tag v-if="isTraining" color="processing" class="log-status-tag">训练中…</a-tag>
            </div>
            <div class="log-titlebar-right">
              <div class="log-hardware-info" v-if="hardwareStatus">
                <div class="hardware-item">
                  <span class="hardware-label">计算设备</span>
                  <a-tag :color="hardwareStatus.device === 'cuda' ? 'geekblue' : 'default'" class="hardware-tag">
                    {{ hardwareStatus.device === 'cuda' ? 'GPU加速' : 'CPU计算' }}
                  </a-tag>
                </div>
                <div class="hardware-item" v-if="hardwareStatus?.gpu_name">
                  <span class="hardware-label">显卡</span>
                  <a-tooltip :title="gpuNameSimple">
                    <a-tag color="purple" class="hardware-tag hardware-tag-name">
                      {{ gpuNameShort }}
                    </a-tag>
                  </a-tooltip>
                </div>
                <div class="hardware-item" v-if="hardwareStatus?.cpu">
                  <span class="hardware-label">处理器</span>
                  <a-tooltip :title="hardwareStatus.cpu">
                    <a-tag class="hardware-tag hardware-tag-name">
                      {{ cpuNameShort }}
                    </a-tag>
                  </a-tooltip>
                </div>
              </div>
              <a-button size="small" class="log-clear-btn" @click="clearLogs" :disabled="state.logs.length === 0"
                >清空日志</a-button
              >
            </div>
          </div>
          <div ref="logContainerRef" class="block-content log-content">
            <div v-if="isTraining" class="log-banner">正在训练过程中，日志实时刷新…</div>
            <div v-if="displayLogs.length === 0" class="log-empty">暂无日志</div>
            <a-collapse
              v-else
              v-model:activeKey="activeLogKeys"
              :bordered="false"
              class="log-collapse"
            >
              <a-collapse-panel v-for="item in displayLogs" :key="item.key" class="log-panel">
                <template #header>
                  <div class="log-row">
                    <span class="log-index">{{ item.key + 1 }}</span>
                    <span v-if="item.time" class="log-time">{{ item.time }}</span>
                    <span class="log-header-text">{{ item.header }}</span>
                  </div>
                </template>
                <pre class="log-pre">{{ item.content }}</pre>
              </a-collapse-panel>
            </a-collapse>
          </div>
        </div>
        <div class="block fit-block">
          <div class="block-title fit-title">
            <span>训练集拟合图</span>
            <div class="fit-toolbar" v-if="enabled && fitEpochMax > 0">
              <span class="fit-toolbar-label">Epoch</span>
              <a-slider v-model:value="fitEpochSelected" :min="1" :max="fitEpochMax" :step="1" class="fit-slider" />
              <span class="fit-toolbar-value">{{ fitEpochSelected }}/{{ fitEpochMax }}</span>
            </div>
          </div>
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
        <div class="block fit-block">
          <div class="block-title fit-title">
            <span>验证集拟合图</span>
            <div class="fit-toolbar" v-if="enabled && fitEpochMax > 0">
              <span class="fit-toolbar-label">Epoch</span>
              <a-slider v-model:value="fitEpochSelected" :min="1" :max="fitEpochMax" :step="1" class="fit-slider" />
              <span class="fit-toolbar-value">{{ fitEpochSelected }}/{{ fitEpochMax }}</span>
            </div>
          </div>
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
          <div class="section-title">模型测试</div>
          <a-form layout="vertical" class="param-form-full" :model="formState">
            <a-row gutter="16" style="margin-bottom: 12px">
              <a-col :span="12">
                <a-form-item>
                  <template #label>
                    <span> 测试集 </span>
                  </template>
                  <a-select
                    class="param-select-full test-set-select"
                    v-model:value="testTagSingle"
                    :options="testSetOptions"
                    placeholder="请选择测试集文件"
                    allow-clear
                    @change="onTestSetSingleChange"
                  >
                    <template #suffixIcon>
                      <svg
                        class="icon"
                        viewBox="0 0 1024 1024"
                        version="1.1"
                        xmlns="http://www.w3.org/2000/svg"
                        width="12.25px"
                        height="12.25px"
                      >
                        <path
                          d="M512.002558 64.24521c-247.292176 0-447.75786 200.464661-447.75786 447.756837 0 247.287059 200.464661 447.752744 447.75786 447.752744 247.286036 0 447.75172-200.464661 447.75172-447.752744C959.754279 264.710894 759.288594 64.24521 512.002558 64.24521zM512.010745 735.87586c-20.602224 0-37.319977-16.718777-37.319977-37.323047 0-20.597107 16.717753-37.319977 37.319977-37.319977 20.60427 0 37.297464 16.72287 37.297464 37.319977C549.308209 719.158107 532.613992 735.87586 512.010745 735.87586zM549.308209 567.969733c0 20.600177-16.693194 37.293371-37.297464 37.293371-20.602224 0-37.319977-16.693194-37.319977-37.293371L474.690768 325.420581c0-20.605294 16.717753-37.297464 37.319977-37.297464 20.60427 0 37.297464 16.693194 37.297464 37.297464L549.308209 567.969733z"
                          fill="#1890FF"
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
        <div class="echarts-row" style="flex: 1; min-height: 0">
          <div class="echart-col">
            <div style="display: flex; align-items: center; width: 100%">
              <span class="select-label">测井曲线绘图栏（左侧）：</span>
              <div style="display: flex; align-items: center; flex: 1">
                <a-select
                  class="param-select-full"
                  v-model:value="testSetTags"
                  mode="multiple"
                  :max-tag-count="1"
                  :options="tagOptions"
                  :tagRender="featureTagRender"
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
              <a-empty v-show="!originLoading" description="暂无结果，请选择测试文件"></a-empty>
            </div>
            <div ref="chart1Ref" class="echart-half" v-show="showCharacter"></div>
          </div>
          <div class="echart-col">
            <div style="display: flex; align-items: center; width: 100%">
              <span class="select-label">测井曲线绘图栏（右侧）：</span>
              <div style="display: flex; align-items: center; flex: 1">
                <a-select
                  class="param-select-full"
                  v-model:value="testSetTags2"
                  mode="multiple"
                  :max-tag-count="1"
                  :options="tagOptions"
                  :tagRender="featureTagRender"
                  allow-clear
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
              <a-empty v-show="!originLoading" description="暂无结果，请选择测试文件"></a-empty>
            </div>
            <div ref="chart2Ref" class="echart-half" v-show="showCharacter"></div>
          </div>
          <div
            class="echart-col echart-col--large"
            v-show="!enabled2"
            style="display: flex; justify-content: center; align-items: center"
          >
            <a-spin v-show="testLoading" tip="模型测试中..." />
            <a-empty v-show="!testLoading" description="暂无结果，请点击开始测试"></a-empty>
          </div>
          <div class="echart-col echart-col--large" v-show="enabled2">
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
    <a-modal
      v-model:open="trainFilesModalVisible"
      title="选择训练文件"
      width="720px"
      :bodyStyle="{ maxHeight: '70vh', overflow: 'auto' }"
      @ok="applyTrainFiles"
    >
      <a-tree
        v-model:checkedKeys="trainFilesCheckedKeys"
        checkable
        :tree-data="treeData"
        :field-names="{ title: 'title', key: 'key', children: 'children' }"
      />
    </a-modal>
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
  getHardwareStatus,
  stopTrain,
  getModelTestingResult,
  getTestOutputResult,
  parameter
} from '@/utils/api'
import { eventBus, state, initSocket } from '@/socket'
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
} from '@/components/echarts/echartsHelper'
import { findNodeByKey } from '@/utils/tree'

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
  input_directory: '',
})
const trainLoading = ref(false)
const testLoading = ref(false)
const originLoading = ref(false)
const enabled = ref(false)
const enabled2 = ref(false)
const showCharacter = ref(false)

const hardwareStatus = ref<null | {
  device: 'cpu' | 'cuda' | string
  gpu_available?: boolean
  gpu_count?: number
  gpu_name?: string | null
  cpu?: string
}>(null)

const cpuNameShort = computed(() => {
  const cpu = hardwareStatus.value?.cpu
  if (!cpu) return ''
  return cpu.length > 26 ? `${cpu.slice(0, 26)}…` : cpu
})

const gpuNameShort = computed(() => {
  const name = gpuNameSimple.value
  if (!name) return ''
  return name.length > 20 ? `${name.slice(0, 20)}…` : name
})

const gpuNameSimple = computed(() => {
  const raw = hardwareStatus.value?.gpu_name
  if (!raw) return ''
  const normalized = String(raw).replace(/\s+/g, ' ').trim()
  const cut = normalized.split('|')[0].split(',')[0].split('(')[0].split('[')[0].split('{')[0].split(';')[0]
  return String(cut).trim()
})

const fetchHardwareStatus = async () => {
  try {
    const res: any = await getHardwareStatus()
    if (res?.code === 200 && res?.data) {
      hardwareStatus.value = res.data
    }
  } catch (e) {
  }
}

const logContainerRef = ref<HTMLDivElement | null>(null)
const activeLogKeys = ref<(string | number)[]>([])
const MAX_LOG_LINES = 500

function normalizeLogText(content: string) {
  return String(content ?? '')
    .replace(/^\s*\[进度\]\s*/i, '')
    .replace(/^\s*info:\s*/i, '')
    .trim()
}

function buildLogHeader(content: string, type?: string, time?: string) {
  const oneLine = normalizeLogText(content)
    .replace(/\r?\n/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()

  const fileSavedPrefix = '新训练周期文件已保存:'
  if (oneLine.includes(fileSavedPrefix)) {
    const idx = oneLine.indexOf(fileSavedPrefix)
    const rest = oneLine.slice(idx + fileSavedPrefix.length).trim()
    const basename = rest.split(/[\\/]/).filter(Boolean).pop() || rest
    return `${fileSavedPrefix} ${basename}`
  }

  if (type && type !== 'log') {
    const shortText = oneLine.length > 120 ? `${oneLine.slice(0, 120)}…` : oneLine
    return `${shortText}`
  }

  const text = oneLine.length > 140 ? `${oneLine.slice(0, 140)}…` : oneLine
  return `${text}`
}

const displayLogs = computed(() => {
  const start = Math.max(0, state.logs.length - MAX_LOG_LINES)
  return state.logs.slice(start).map((log, idx) => {
    const key = start + idx
    return {
      key,
      type: log.type,
      time: (log as any).time,
      content: normalizeLogText(log.content),
      header: buildLogHeader(log.content, log.type, (log as any).time),
    }
  })
})

function clearLogs() {
  state.logs.splice(0)
  activeLogKeys.value = []
}

watch(
  () => state.logs.length,
  () => {
    nextTick(() => {
      const el = logContainerRef.value
      if (!el) return
      const distanceToBottom = el.scrollHeight - el.scrollTop - el.clientHeight
      if (distanceToBottom < 120) el.scrollTop = el.scrollHeight
    })
  }
)

const trainFilesModalVisible = ref(false)
const trainFilesCheckedKeys = ref<(string | number)[]>([])
const selectedTrainFileIds = ref<number[]>([])

const testTags = ref<number[]>([])
// 单选测试集文件ID
const testTagSingle = ref<number | undefined>(undefined)
// trainSetTags 是字符串
const trainSetTags = ref<string>('')
const testSetOptions = ref<{ label: string; value: number }[]>([])
const fileIdToName = ref<Record<number, string>>({})
const maxLenCurve = ref(0)
const testSetTags = ref<string[]>([])
const testSetTags2 = ref<string[]>([])
const tagOptions = ref<{ label: string; value: string }[]>([])
const allData = ref<Record<string, number[][]>>({})
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
const columns = [
  {
    title: '指标',
    dataIndex: 'metric',
  },
  {
    title: '数值',
    dataIndex: 'value',
  },
]
interface DataItem {
  key: number
  metric: string
  value: number
}
const tableData = ref<DataItem[]>([])
// 自定义 tag 渲染：显示文件名
const testSetTagRender = (props: any) => {
  const id = props.value as number
  const text = fileIdToName.value[id] || String(props.label)
  return h(
    Tag,
    {
      style: { marginRight: '4px', maxWidth: '240px' },
      title: text,
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
        text
      )
  )
}

const featureTagRender = (props: any) => {
  const text = String(props.label ?? props.value ?? '')
  return h(
    Tag,
    {
      style: { marginRight: '4px', maxWidth: '240px' },
      title: text,
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
        text
      )
  )
}
const trainSetOptions = ref<{ label: string; value: string, type: string }[]>([])
const targetname_value = ref<string>('')
const trainSetCascaderValue = ref([])
const treeData = ref<MyTreeNode[]>([])
const parentTreeId = ref(0)
type MyTreeNode = {
  title: string
  key: string
  type: string
  id: number
  children?: MyTreeNode[]
}
const file_id = ref(0)

const loadFeaturePreviewFromFileId = async (fileId: number) => {
  showCharacter.value = false
  originLoading.value = true
  testSetTags.value = []
  testSetTags2.value = []
  tagOptions.value = []
  file_id.value = fileId
  try {
    const res: any = await getModelTestingResult({ file_id: file_id.value })
    if (res?.code === 200) {
      const c1 = res?.data.options.character1 || []
      const c2 = res?.data.options.character2 || []
      maxLenCurve.value = Math.max(c1.length, c2.length)
      const data1 = res?.data.axisData || {}
      const data2 = res?.data.axisData2 || {}
      // 默认只选择第一条曲线
      testSetTags.value = c1.length > 0 ? [c1[0]] : []
      testSetTags2.value = c2.length > 0 ? [c2[0]] : []
      tagOptions.value = [...c1, ...c2].map((tag) => ({
        label: tag,
        value: tag,
      }))
      allData.value = { ...data1, ...data2 }
      // 使用只选择第一条曲线后的 testSetTags 构建图表
      chart1Option.value = customOptions(testSetTags.value, allData.value, buildCustomConfig(testSetTags.value, allData.value, indicatorsForm), channelsForm)
      chart2Option.value = customOptions(
        testSetTags2.value,
        allData.value,
        buildCustomConfig(testSetTags2.value, allData.value, indicatorsForm2),
        channelsForm2
      )
      updateCharts()
      showCharacter.value = true
    } else {
      showCharacter.value = false
    }
  } catch (e) {
    showCharacter.value = false
  } finally {
    originLoading.value = false
  }
}

watch(
  () => testTags.value,
  (ids) => {
    const normalized = Array.isArray(ids) ? ids.filter((x) => typeof x === 'number') : []
    if (normalized.length === 0) {
      showCharacter.value = false
      originLoading.value = false
      testSetTags.value = []
      testSetTags2.value = []
      tagOptions.value = []
      return
    }
    const preferred = normalized.includes(file_id.value) ? file_id.value : normalized[0]
    loadFeaturePreviewFromFileId(preferred)
  },
  { deep: true, immediate: true }
)

// 训练相关
const isTraining = ref(false)
const isTest = ref(false)
// const trainResult = ref<null | { accuracy: number; loss: number }>(null)
const trainResult = ref<boolean | null>(true)

watch(
  () => state.logs[state.logs.length - 1],
  (last) => {
    const content = last?.content ? String(last.content) : ''
    if (!content) return
    if (content.includes('训练完成')) isTraining.value = false
    if (content.includes('训练已中止') || content.includes('训练中止')) isTraining.value = false
  }
)

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
const trainLossLastXMap: Record<string, number> = {}
let resizeObserver: ResizeObserver | null = null
interface Point {
  seriesName: string
  x: number
  y: number
}

const chartTypes = ['train', 'verify', 'trainLoss']
const clearRecord = (record: Record<string, any>) => {
  Object.keys(record).forEach((k) => delete record[k])
}

const applyStreamBaseOption = (chart: echarts.ECharts | null) => {
  if (!chart) return
  chart.clear()
  chart.setOption(
    {
      animation: true,
      tooltip: {
        trigger: 'item',
        formatter: function (params: any) {
          if (params.seriesName === undefined) return ''
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
    },
    true
  )
}

const resetTrainingCharts = () => {
  clearRecord(trainSeriesMap)
  clearRecord(verifySeriesMap)
  clearRecord(trainLossSeriesMap)
  clearRecord(seriesDataCache)
  clearRecord(trainLossLastXMap)
  applyStreamBaseOption(trainChartInstance)
  applyStreamBaseOption(verifyChartInstance)
  applyStreamBaseOption(trainLossChartInstance)
  fitEpochs.value = []
  fitEpochSelected.value = 1
}

type FitEpoch = {
  trainBlue?: [number, number][]
  trainRed?: [number, number][]
  verifyBlue?: [number, number][]
  verifyRed?: [number, number][]
}

const fitEpochs = ref<FitEpoch[]>([])
const fitEpochSelected = ref(1)
const fitEpochMax = computed(() => fitEpochs.value.length)
// 拟合图最多保留最近 MAX_FIT_EPOCHS 个 epoch，防止内存无限增长导致浏览器崩溃
const MAX_FIT_EPOCHS = 100

const FIT_BLUE = '#1677ff'
const FIT_RED = '#ff4d4f'

const LOSS_SERIES_COLOR: Record<string, string> = {
  损失: FIT_BLUE,
  训练集总损失: FIT_BLUE,
  验证集总损失: FIT_RED,
  训练集数据损失: '#13c2c2',
  验证集数据损失: '#fa8c16',
  训练集知识嵌入损失: '#722ed1',
  验证集知识嵌入损失: '#52c41a',
}

const setFitChartOption = (
  chart: echarts.ECharts | null,
  blueData: [number, number][],
  redData: [number, number][]
) => {
  if (!chart) return
  chart.setOption(
    {
      animation: true,
      animationDuration: 400,
      animationEasing: 'cubicOut',
      animationDurationUpdate: 280,
      animationEasingUpdate: 'cubicOut',
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'cross' },
      },
      grid: { left: 92, right: 28, top: 30, bottom: 92, containLabel: true },
      xAxis: {
        type: 'value',
        name: '标准化后的目标测井曲线',
        nameLocation: 'middle',
        nameGap: 56,
        nameTextStyle: { fontSize: 12, color: 'rgba(0,0,0,0.65)' },
        axisLabel: { color: 'rgba(0,0,0,0.65)' },
      },
      yAxis: {
        type: 'value',
        name: '深度片段样本号',
        nameLocation: 'middle',
        nameGap: 68,
        nameTextStyle: { fontSize: 12, color: 'rgba(0,0,0,0.65)' },
        axisLabel: { color: 'rgba(0,0,0,0.65)' },
      },
      legend: { data: ['真实值', '预测值'] },
      series: [
        {
          name: '真实值',
          type: 'line',
          showSymbol: false,
          lineStyle: { width: 2, color: FIT_BLUE },
          itemStyle: { color: FIT_BLUE },
          data: blueData,
        },
        {
          name: '预测值',
          type: 'line',
          showSymbol: false,
          lineStyle: { width: 2, color: FIT_RED },
          itemStyle: { color: FIT_RED },
          data: redData,
        },
      ],
    },
    { notMerge: false, lazyUpdate: true }
  )
}

const renderFitEpoch = (epoch: number) => {
  const idx = Math.max(0, epoch - 1)
  const ep = fitEpochs.value[idx]
  if (!ep) return
  setFitChartOption(trainChartInstance, ep.trainBlue ?? [], ep.trainRed ?? [])
  setFitChartOption(verifyChartInstance, ep.verifyBlue ?? [], ep.verifyRed ?? [])
}

watch(
  fitEpochSelected,
  (val) => {
    if (!enabled.value) return
    renderFitEpoch(val)
  },
  { immediate: false }
)

const ensureFitEpoch = () => {
  if (fitEpochs.value.length === 0) {
    fitEpochs.value.push({})
    fitEpochSelected.value = 1
  }
}

const onTrainPoints = (points: Point[]) => {
  if (!points.length) return
  const seriesKey = points[0].seriesName
  const data = points.map((p) => [p.x, p.y] as [number, number])

  if (seriesKey === 'tuyilan') {
    fitEpochs.value.push({})
    // 超过上限时丢弃最早的 epoch，防止内存无限增长
    if (fitEpochs.value.length > MAX_FIT_EPOCHS) {
      const removed = fitEpochs.value.length - MAX_FIT_EPOCHS
      fitEpochs.value.splice(0, removed)
      // 调整选中索引，避免指向已删除的 epoch
      fitEpochSelected.value = Math.max(1, fitEpochSelected.value - removed)
    }
    fitEpochSelected.value = fitEpochs.value.length
  } else {
    ensureFitEpoch()
  }

  const ep = fitEpochs.value[fitEpochs.value.length - 1]
  if (seriesKey === 'tuyilan') ep.trainBlue = data
  if (seriesKey === 'tuyihong') ep.trainRed = data

  if (fitEpochSelected.value === fitEpochs.value.length) renderFitEpoch(fitEpochSelected.value)
}

const onVerifyPoints = (points: Point[]) => {
  if (!points.length || fitEpochs.value.length === 0) return
  const seriesKey = points[0].seriesName
  const data = points.map((p) => [p.x, p.y] as [number, number])
  const ep = fitEpochs.value[fitEpochs.value.length - 1]
  if (seriesKey === 'tuerlan') ep.verifyBlue = data
  if (seriesKey === 'tuerhong') ep.verifyRed = data

  if (fitEpochSelected.value === fitEpochs.value.length) renderFitEpoch(fitEpochSelected.value)
}

const onTrainLossPoints = (points: Point[]) =>
  appendPoints2(points, trainLossChartInstance, trainLossSeriesMap)

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
    // 更新缓存
    if (!seriesDataCache[seriesName]) {
      seriesDataCache[seriesName] = []
    }
    const cached = seriesDataCache[seriesName]
    let lastX = trainLossLastXMap[seriesName] ?? Number.NEGATIVE_INFINITY

    // 仅接收有效数值点；按 epoch 单调追加，丢弃回退点
    seriesPoints.forEach((p) => {
      const x = Number(p.x)
      const y = Number(p.y)
      if (!Number.isFinite(x) || !Number.isFinite(y)) return

      if (x < lastX) return
      if (x === lastX && cached.length > 0) {
        cached[cached.length - 1] = [x, y]
        return
      }

      cached.push([x, y])
      lastX = x
    })
    trainLossLastXMap[seriesName] = lastX

    // 超过上限时截断，防止内存无限增长
    if (cached.length > 1000) {
      seriesDataCache[seriesName] = cached.slice(-500)
    }

    let seriesIndex = seriesMap[seriesName]

    if (seriesIndex === undefined) {
      // 新 series - 创建新的数据系列
      const currentOption = chart.getOption()
      const currentSeries = (currentOption.series as any[]) || []
      const currentLegendData = ((currentOption.legend as any)?.[0]?.data as string[]) || []

      seriesIndex = currentSeries.length
      seriesMap[seriesName] = seriesIndex

      const color = LOSS_SERIES_COLOR[seriesName]
      chart.setOption(
        {
          tooltip: {
            trigger: 'item',
            axisPointer: { type: 'cross', label: { backgroundColor: '#6a7985' } },
            formatter: function (params: any) {
              return `${params.seriesName}<br/>x: ${params.value[0]}<br/>y: ${params.value[1]}`
            },
          },
          series: [
            ...currentSeries,
            {
              id: seriesName,
              name: seriesName,
              type: 'line',
              showSymbol: true,
              symbolSize: 4,
              lineStyle: { width: 2, color },
              itemStyle: { color },
              animation: true,
              animationDuration: 300,
              data: seriesDataCache[seriesName],
            },
          ],
          legend: { data: [...new Set([...currentLegendData, seriesName])] },
        },
        false
      )
    } else {
      // 已存在的 series — 按索引定位，非目标位用空对象占位（merge 时无副作用）
      const patchSeries: any[] = []
      for (let i = 0; i <= seriesIndex; i++) {
        patchSeries.push(i === seriesIndex
          ? { data: seriesDataCache[seriesName] }
          : {})
      }
      chart.setOption({ series: patchSeries }, false)
    }
  })
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

const initData = async () => {
  // 页面重新激活时执行的逻辑
  console.log('加载页面数据')
  try {
    const res = await getTreeData()
    if (res?.data) {
      const rawData = res.data[0]?.children ?? []
      treeData.value = patchTreeKeys(rawData)
      parentTreeId.value = res.data[0].id
      const fileOptions: { label: string; value: number }[] = []
      const idToName: Record<number, string> = {}

      const collect = (node: any, currentPath: string) => {
        if (!node) return
        if (node.type === 'directory') {
          const nextPath = currentPath ? `${currentPath}/${node.title}` : String(node.title ?? '')
          if (Array.isArray(node.children)) node.children.forEach((ch: any) => collect(ch, nextPath))
          return
        }
        // 放宽文件类型限制，只要不是 directory 且有 id 就视为文件
        if (node.type !== 'directory') {
          const baseName = String(node.title ?? node.name ?? node.label ?? node.value ?? node.id)
          const id = Number(node.id)
          if (Number.isFinite(id)) {
            const displayName = currentPath ? `${currentPath}/${baseName}` : baseName
            idToName[id] = displayName
            fileOptions.push({ label: displayName, value: id })
          }
        }
        if (Array.isArray(node.children)) node.children.forEach((ch: any) => collect(ch, currentPath))
      }

      // 遍历整个文件树，不再局限于特定文件夹
      if (Array.isArray(res.data)) {
        res.data.forEach((rootNode: any) => {
             // 如果根节点是目录，不应该把根节点名字加到路径里，否则太长了？
             // 通常根节点是类似 "Root" 或 "/"，视情况而定
             // 这里我们保持原逻辑，传入空字符串作为初始路径
             collect(rootNode, '')
        })
      }

      testSetOptions.value = fileOptions
      fileIdToName.value = idToName
    }

    const res2 = await getAddSelect()
    console.log('res2:', res2)
    if (res2) {
      // 显示 name，保存 id
      const best = res2.data['best-data']?.map((t: any) => ({ label: t.name, value: t.id + '-best-data', type: 'best-data' })) || [];
      const final = res2.data['final-data']?.map((t: any) => ({ label: t.name, value: t.id + '-final-data', type: 'final-data' })) || [];
      const merged = [...best, ...final]
      merged.sort((a: any, b: any) => parseInt(String(b.value), 10) - parseInt(String(a.value), 10))
      trainSetOptions.value = merged
    }
  } catch (e) {
    console.error('initData error:', e)
  }
}

onActivated(() => {
  initData()
})



onMounted(async () => {
  initData()
  fetchHardwareStatus()

  trainChartInstance = initChart(trainChartRef.value)
  verifyChartInstance = initChart(verifyChartRef.value)
  trainLossChartInstance = initChart(trainLossChartRef.value)

  // 初始化三个图表
  chart1Instance = initChart(chart1Ref.value)
  chart2Instance = initChart(chart2Ref.value)
  chart3Instance = initChart(chart3Ref.value)

  // ---------- 监听 eventBus ----------
  eventBus.on('train', onTrainPoints)
  eventBus.on('verify', onVerifyPoints)
  eventBus.on('trainLoss', onTrainLossPoints)

  // if (chartRef.value) {
  //   resizeObserver = new ResizeObserver(() => {
  //     resizeChart()
  //   })
  //   resizeObserver.observe(chartRef.value)
  // }

  //
})
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
  tagOptions,
  (options) => {
    if (options && options.length > 0) {
      if (testSetTags.value.length === 0) {
        testSetTags.value = [options[0].value]
      }
      if (testSetTags2.value.length === 0) {
        testSetTags2.value = [options[0].value]
      }
    }
  },
  { immediate: true, deep: true }
)

watch(
  testSetTags,
  (newTags) => {
    clearRecord(indicatorsForm)
    // 为每个选择项创建配置对象，赋默认值
    newTags.forEach((tag, index) => {
      // 创建配置对象

      if (!indicatorsForm[tag]) {
        indicatorsForm[tag] = {
          lineStyle: 'solid',
          color: getDefaultCurveColor(index),
        }
        // 坐标范围：从ECharts数据中获取min和max
        const chartData = allData.value[tag] || []
        if (chartData.length > 0) {
          const { min, max } = getCurveRange(tag, chartData)
          indicatorsForm[tag].range = [min, max]
        }
      }
      console.log('indicatorsForm;：', indicatorsForm)
    })
  },
  { immediate: true }
)

watch(
  testSetTags2,
  (newTags) => {
    clearRecord(indicatorsForm2)
    newTags.forEach((tag, index) => {
      if (!indicatorsForm2[tag]) {
        indicatorsForm2[tag] = {
          lineStyle: 'solid',
          color: getDefaultCurveColor(index),
        }
        const chartData = allData.value[tag] || []
        if (chartData.length > 0) {
          const { min, max } = getCurveRange(tag, chartData)
          indicatorsForm2[tag].range = [min, max]
        }
      }
    })
  },
  { immediate: true }
)
watch(maxLenCurve, (newValue) => {
  // 更新图表1的配置
  chart1Option.value = customOptions(
    testSetTags.value,
    allData.value,
    buildCustomConfig(testSetTags.value, allData.value, indicatorsForm),
    channelsForm
  )
  // 更新图表2的配置
  chart2Option.value = customOptions(
    testSetTags2.value,
    allData.value,
    buildCustomConfig(testSetTags2.value, allData.value, indicatorsForm2),
    channelsForm2
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
  
  // Default to selecting only the first curve
  testSetTags.value = c1.length > 0 ? [c1[0]] : []
  testSetTags2.value = c2.length > 0 ? [c2[0]] : []
  
  tagOptions.value = [...c1, ...c2].map((tag) => ({
    label: tag,
    value: tag,
  }))
  // allData.value = { ...data1, ...data2 }
  // chart1Option.value = customOptions(c1, allData.value, buildCustomConfig(c1, allData.value, indicatorsForm), channelsForm)
  // chart2Option.value = customOptions(c2, allData.value, buildCustomConfig(c2, allData.value, indicatorsForm2), channelsForm2)
}

const buildCustomConfig = (
  tags: string[],
  data: Record<string, number[][]>,
  indicatorModel: Record<string, IndicatorConfig> = indicatorsForm
) => {
  const config: Record<string, { lineStyle?: string; color?: string; range?: [number, number] }> =
    {}

  tags.forEach((tag, index) => {
    const tagConfig = indicatorModel[tag] || {}

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
      const { min, max } = getCurveRange(tag, data[tag])
      range = [min, max]
    }

    config[tag] = {
      lineStyle: tagConfig.lineStyle || 'solid',
      color: tagConfig.color || getDefaultCurveColor(index),
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
      color: tagConfig.color || getDefaultCurveColor(index),
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
  const curveDisplayName = (curveName: string) => {
    if (!isChart3) return curveName
    if (curveName === 'prediction_coords') return '预测曲线'
    if (curveName === 'true_coords') return '真实曲线'
    return curveName
  }
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
    const color = config.color || getDefaultCurveColor(index)

    return {
      name: curveDisplayName(c),
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
    const color = config.color || getDefaultCurveColor(index)
    // 如果传入了自定义的min和max，使用传入的值，否则默认
    const min = config.range?.[0] !== undefined ? config.range[0] : getCurveRange(c).min
    const max = config.range?.[1] !== undefined ? config.range[1] : getCurveRange(c).max
    // 使用容差比较来处理浮点数精度问题
    const labelEpsilon = Math.max(Math.abs(max - min) * 1e-6, 1e-9)
    // 格式化数值显示
    const formatAxisLabel = (v: number) => {
      if (!Number.isFinite(v)) return ''
      const abs = Math.abs(v)
      if (abs >= 10000 || (abs > 0 && abs < 0.001)) return v.toExponential(2)
      const rounded = Math.round(v * 100) / 100
      return String(rounded)
    }

    return {
      name: curveDisplayName(c),
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
          // 使用容差比较来判断是否为最小值或最大值
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
      top: curves.length <= 1 ? 60 : (30 * (curves.length + (channelsConfig.logarithmicScale === 'true' ? 1 : 0)) +
        (isChart3 ? 26 : 20)),
      left: isChart3 ? 70 : 60,
      right: 50,
      bottom: isChart3 ? 63 : 20, /* Reduced bottom padding for chart 1 & 2 to bring content up */
      containLabel: true,
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
  chart1Option.value = customOptions(value, allData.value, buildCustomConfig(value, allData.value, indicatorsForm), channelsForm)
  if (chart1Instance) {
    disposeEChart(chart1Instance)
    chart1Instance = null
  }
  updateCharts()
}

const onTagChange2 = (value: string[]) => {
  console.log('onTagChange2:', value)
  testSetTags2.value = value
  maxLenCurve.value = Math.max(testSetTags.value.length, value.length)
  chart2Option.value = customOptions(value, allData.value, buildCustomConfig(value, allData.value, indicatorsForm2), channelsForm2)
  if (chart2Instance) {
    disposeEChart(chart2Instance)
    chart2Instance = null
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
  eventBus.off('train', onTrainPoints)
  eventBus.off('verify', onVerifyPoints)
  eventBus.off('trainLoss', onTrainLossPoints)

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

const validateTrainParams = () => {
  const fieldLabelMap: Partial<Record<keyof typeof inputParamsForm, string>> = {
    model_name: '模型选择',
    num_channels: 'TCN通道数',
    activation: '激活函数',
    loss: '损失函数类型',
    hidden_size: '隐藏层维度',
    num_layers: '网络层数',
    dropout: 'Dropout概率',
    kernel_size: 'TCN卷积核大小',
    num_heads: 'Transformer注意力头数',
    hidden_space: 'Transformer注意力空间维度',
    e_layers: 'Autoformer编码器层数',
    d_ff: '前馈网络维度',
    moving_avg: 'Autoformer滑动平均窗口大小',
    factor: '自相关top-k因子',
    num_epochs: '训练轮数',
    learning_rate: '学习率',
  }
  const requiredStringFields: Array<keyof typeof inputParamsForm> = [
    'model_name',
    'num_channels',
    'activation',
    'loss',
  ]
  for (const field of requiredStringFields) {
    const val = inputParamsForm[field]
    if (typeof val !== 'string' || val.trim() === '') {
      message.error(`请填写参数：${fieldLabelMap[field] || String(field)}`)
      return false
    }
  }

  const requiredNumberFields: Array<keyof typeof inputParamsForm> = [
    'hidden_size',
    'num_layers',
    'dropout',
    'kernel_size',
    'num_heads',
    'hidden_space',
    'e_layers',
    'd_ff',
    'moving_avg',
    'factor',
    'num_epochs',
    'learning_rate',
  ]
  for (const field of requiredNumberFields) {
    const val = inputParamsForm[field]
    if (typeof val !== 'number' || Number.isNaN(val)) {
      message.error(`参数格式错误：${fieldLabelMap[field] || String(field)}`)
      return false
    }
  }

  if (inputParamsForm.hidden_size <= 0) return message.error('隐藏层维度必须大于 0'), false
  if (inputParamsForm.num_layers <= 0) return message.error('网络层数必须大于 0'), false
  if (inputParamsForm.num_epochs <= 0) return message.error('训练轮数必须大于 0'), false
  if (inputParamsForm.learning_rate <= 0) return message.error('学习率必须大于 0'), false
  if (inputParamsForm.dropout < 0 || inputParamsForm.dropout > 1)
    return message.error('Dropout概率必须在 0 到 1 之间'), false

  return true
}

const onTestSetChange = (value: number[]) => {
  testTags.value = Array.isArray(value) ? value : []
  // 将 testTags 存入全局 store
  store.commit('setTestTags', testTags.value)
}

// 单选测试集变更处理函数
const onTestSetSingleChange = (value: number | undefined) => {
  testTagSingle.value = value
  // 同步更新 testTags 用于兼容现有逻辑
  testTags.value = value !== undefined ? [value] : []
  // 将 testTags 存入全局 store
  store.commit('setTestTags', testTags.value)
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
  if (trainLoading.value || isTraining.value) return
  if (!validateTrainParams()) return

  trainLoading.value = true
  enabled.value = true
  resetTrainingCharts()
  isTraining.value = true

  try {
    const res2: any = await parameter(inputParamsForm)
    if (res2?.code !== 200) {
      enabled.value = false
      isTraining.value = false
      message.error(res2?.message || '参数保存失败')
      return
    }

    initSocket()
    const payload =
      selectedTrainFileIds.value.length > 0 ? { file_ids: selectedTrainFileIds.value } : undefined
    const res: any = await startTrain(payload)
    if (res?.code === 200) {
      message.success(res?.message || '开始训练')
    } else {
      enabled.value = false
      isTraining.value = false
      message.error(res?.message || '训练启动失败')
    }
  } catch (e) {
    enabled.value = false
    isTraining.value = false
  } finally {
    trainLoading.value = false
  }
}

const stopLoading = ref(false)

const handleStopTrain = async () => {
  if (!isTraining.value || stopLoading.value) return
  stopLoading.value = true
  try {
    const res: any = await stopTrain()
    if (res?.code === 200) {
      message.success(res?.message || '已发送中止请求')
    } else {
      message.error(res?.message || '中止失败')
    }
  } catch (e) {
    message.error('中止失败')
  } finally {
    stopLoading.value = false
  }
}

function applyTrainFiles() {
  const ids: number[] = []
  const keys = Array.isArray(trainFilesCheckedKeys.value) ? trainFilesCheckedKeys.value : []
  keys.forEach((k) => {
    const node = findNodeByKey(treeData.value, String(k))
    if (node && node.type !== 'directory') ids.push(node.id)
  })
  selectedTrainFileIds.value = Array.from(new Set(ids))
  trainFilesModalVisible.value = false
}

function clearTrainFiles() {
  selectedTrainFileIds.value = []
  trainFilesCheckedKeys.value = []
}

const handleTest = async () => {
  if (!Array.isArray(testTags.value) || testTags.value.length === 0) {
    message.warning('请先选择测试文件')
    return
  }
  if (!trainSetTags.value) {
    message.warning('请先选择模型')
    return
  }
  testLoading.value = true
  enabled2.value = false
  const selectedFileIds = testTags.value
  const preferredResultFileId =
    selectedFileIds.includes(file_id.value) ? file_id.value : selectedFileIds[0]
  file_id.value = preferredResultFileId
  const data = {
    file_ids: selectedFileIds,
    idm: Number((trainSetTags.value).split('-')[0]) || 0,
    file_id: preferredResultFileId,
    predict_mode: false,
    type: trainSetOptions.value.find((item) => item.value === trainSetTags.value)?.type || 'best-data',
  }

  try {
      const res: any = await getTestOutputResult(data)
      console.log("res", res)
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
        const customConfig = buildCustomConfig(c1, allData.value, {})

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
        testLoading.value = false
        enabled2.value = false
      }
  } catch (error) {
    console.log("error", error)
    testLoading.value = false
    enabled2.value = false
    return
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
  padding: var(--spacing-xl);
  background: var(--bg-secondary);
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  min-height: 100%;
}

.preprocess-select-card {
  width: 100%;
  min-width: 320px;
  border-radius: var(--radius-lg);
  background: var(--bg-primary);
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
  margin-bottom: var(--spacing-2xl);
  border: 1px solid var(--border-color);
  overflow: hidden;
  transition: var(--transition-base);
}

.preprocess-select-card:hover {
  box-shadow: var(--shadow-md);
  border-color: var(--border-color-hover);
}

/* 卡片标题 - 统一工业风格（完整四边框） */
.preview-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  min-height: 56px;
  display: flex;
  align-items: center;
  padding: var(--spacing-lg) var(--spacing-xl);
  padding-left: var(--spacing-2xl);
  background: var(--bg-secondary);
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

.preprocess-select-content {
  padding: var(--spacing-xl);
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
.log-block {
  border-radius: var(--radius-lg);
  overflow: hidden;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-sm);
}

/* 日志标题栏 - 统一工业风格（完整四边框） */
.log-titlebar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: var(--spacing-sm);
  background: var(--bg-secondary);
  color: var(--text-primary);
  padding: var(--spacing-md) var(--spacing-lg);
  padding-left: var(--spacing-2xl);
  min-height: 48px;
  position: relative;
  border-left: 4px solid var(--primary-color);
  border-right: 3px solid var(--primary-color);
  border-bottom: 2px solid var(--primary-color);
}

/* 顶部蓝色渐变装饰条 */
.log-titlebar::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--primary-color) 0%, var(--primary-light) 100%);
}

.log-titlebar-left {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  flex-shrink: 0;
  padding-left: var(--spacing-md);
}

.log-title-text {
  font-weight: 600;
  font-size: 14px;
  color: var(--text-primary);
}
.log-status-tag {
  font-size: 12px;
}
.log-titlebar-right {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}
.log-hardware-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 4px 10px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 6px;
  border: 1px solid #e0e0e0;
}
.hardware-item {
  display: flex;
  align-items: center;
  gap: 4px;
}
.hardware-label {
  font-size: 11px;
  color: rgba(0, 0, 0, 0.55);
  white-space: nowrap;
}
.hardware-tag {
  font-size: 11px;
  margin: 0;
  padding: 0 6px;
  line-height: 18px;
}
.hardware-tag-name {
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.log-clear-btn {
  font-size: 12px;
}
.log-content {
  background:
    linear-gradient(rgba(0, 0, 0, 0.03) 1px, transparent 1px) 0 0 / 100% 28px,
    linear-gradient(90deg, rgba(0, 0, 0, 0.03) 1px, transparent 1px) 0 0 / 28px 100%,
    #ffffff;
  color: #333;
  padding: 10px;
}
.log-banner {
  padding: 10px 12px;
  border: 1px dashed #91d5ff;
  border-radius: 8px;
  background: #e6f7ff;
  color: #0050b3;
  margin-bottom: 10px;
}
.log-empty {
  padding: 12px;
  border-radius: 8px;
  color: rgba(0, 0, 0, 0.55);
  background: #fafafa;
  border: 1px dashed #d9d9d9;
}
.log-row {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}
.log-index {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 42px;
  height: 22px;
  border-radius: 6px;
  background: #fafafa;
  border: 1px solid #e8e8e8;
  color: rgba(0, 0, 0, 0.65);
  font-variant-numeric: tabular-nums;
  flex: 0 0 auto;
}
.log-time {
  font-variant-numeric: tabular-nums;
  color: rgba(0, 0, 0, 0.55);
  flex: 0 0 auto;
}
.log-header-text {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: rgba(0, 0, 0, 0.88);
}
.log-pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New',
    monospace;
  font-size: 12px;
  line-height: 18px;
  color: rgba(0, 0, 0, 0.85);
  padding: 10px 12px;
  border-radius: 8px;
  background: #fafafa;
  border: 1px solid #e8e8e8;
}
:deep(.log-collapse) {
  background: transparent;
}
:deep(.log-collapse .ant-collapse-item) {
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid #e8e8e8;
  border-radius: 10px;
  overflow: hidden;
  margin-bottom: 10px;
}
:deep(.log-collapse .ant-collapse-header) {
  color: rgba(0, 0, 0, 0.88);
  padding: 10px 12px;
}
:deep(.log-collapse .ant-collapse-arrow) {
  color: rgba(0, 0, 0, 0.55);
}
:deep(.log-collapse .ant-collapse-content) {
  background: transparent;
  border-top: 1px solid #e8e8e8;
}
:deep(.log-collapse .ant-collapse-content-box) {
  padding: 10px 12px 12px;
}

.fit-block {
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid #e8e8e8;
  background: #fff;
}
.fit-block .block-title {
  background: #f0f0f0;
  border-bottom: 1px solid #e8e8e8;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}
.fit-toolbar {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}
.fit-toolbar-label {
  color: rgba(0, 0, 0, 0.65);
  font-size: 12px;
  white-space: nowrap;
}
.fit-toolbar-value {
  color: rgba(0, 0, 0, 0.65);
  font-size: 12px;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}
.fit-slider {
  width: 180px;
  margin: 0;
}

.train-file-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 16px;
  padding: 14px 16px;
  background: linear-gradient(135deg, #f8f9fa 0%, #f0f2f5 100%);
  border: 1px solid #e0e0e0;
  border-radius: 10px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);
}
.train-file-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  width: 100%;
}
.train-file-label {
  display: flex;
  align-items: center;
  gap: 6px;
  white-space: nowrap;
  color: rgba(0, 0, 0, 0.75);
  font-size: 14px;
  font-weight: 500;
}
.train-file-icon {
  color: #1890ff;
  flex-shrink: 0;
}
.train-file-btn {
  min-width: 160px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  background: linear-gradient(135deg, #ffffff 0%, #f5f5f5 100%);
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  color: rgba(0, 0, 0, 0.85);
  font-size: 13px;
  font-weight: 500;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);
}
.train-file-btn:hover,
.train-file-btn:focus {
  background: linear-gradient(135deg, #e6f7ff 0%, #bae7ff 100%);
  border-color: #40a9ff;
  color: #1890ff;
  box-shadow: 0 4px 8px rgba(24, 144, 255, 0.2);
  transform: translateY(-1px);
}
.train-file-count {
  font-size: 12px;
  font-weight: 500;
}
.train-file-clear {
  margin-left: auto;
  font-size: 12px;
}

/* 训练操作行样式 */
.train-action-row {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-top: 16px;
  padding: 12px 0;
}
.train-start-btn {
  min-width: 140px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  border-radius: 8px;
  background: linear-gradient(135deg, #1890ff 0%, #096dd9 100%);
  border: none;
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.3);
  transition: all 0.3s ease;
}
.train-start-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #40a9ff 0%, #1890ff 100%);
  box-shadow: 0 6px 16px rgba(24, 144, 255, 0.4);
  transform: translateY(-2px);
}
.train-start-btn:disabled {
  background: #bfbfbf;
  box-shadow: none;
}
.train-stop-btn {
  min-width: 140px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  border-radius: 8px;
  background: linear-gradient(135deg, #ff4d4f 0%, #cf1322 100%);
  border: none;
  box-shadow: 0 4px 12px rgba(255, 77, 79, 0.3);
  transition: all 0.3s ease;
}
.train-stop-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #ff7875 0%, #ff4d4f 100%);
  box-shadow: 0 6px 16px rgba(255, 77, 79, 0.4);
  transform: translateY(-2px);
}
.train-stop-btn:disabled {
  background: #bfbfbf;
  box-shadow: none;
}

/* 测试集选择器样式 */
.test-set-select {
  min-height: 36px;
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
  font-size: 14px;
  color: var(--text-secondary);
  min-width: 70px;
  font-weight: 500;
  white-space: nowrap;
}

/* 图表行 - 统一工业风格 */
.echarts-row {
  display: flex;
  width: 100%;
  gap: var(--spacing-lg);
  margin-top: var(--spacing-lg);
  height: 100%;
  position: relative;
}

.echart-col {
  display: flex;
  flex-direction: column;
  flex: 0.9 1 0;
  padding: var(--spacing-md);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-color);
  transition: var(--transition-base);
  background: var(--bg-primary);
  border-radius: var(--radius-md);
}

.echart-col:hover {
  box-shadow: var(--shadow-md);
  border-color: var(--primary-lighter);
  transform: translateY(-2px);
}

.echart-col--large {
  flex: 1.1 1 0;
}

.echart-half {
  width: 100%;
  flex: 1;
  min-height: 0;
  min-width: 0;
  position: relative;
}

/* 输入参数表样式 - 统一工业风格 */
.input-params-section {
  margin-bottom: var(--spacing-2xl);
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: var(--spacing-lg);
  padding-left: var(--spacing-lg);
  padding-bottom: var(--spacing-sm);
  border-left: 4px solid var(--primary-color);
}

.input-params-form {
  background: var(--bg-primary);
  padding: var(--spacing-xl);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-color);
}

.input-params-container {
  display: flex;
  gap: var(--spacing-lg);
  flex-wrap: wrap;
}

.param-column {
  flex: 1;
  min-width: 280px;
  background: var(--bg-secondary);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
  overflow: hidden;
}

.param-column-header {
  background: var(--bg-tertiary);
  padding: var(--spacing-sm) var(--spacing-md);
  border-bottom: 2px solid var(--primary-color);
}

.param-column-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.param-column-content {
  padding: var(--spacing-md);
}

.param-column-content .ant-form-item {
  margin-bottom: var(--spacing-lg);
}

.param-column-content .ant-form-item:last-child {
  margin-bottom: 0;
}

.dataset-selection-section {
  background: var(--bg-primary);
  padding: var(--spacing-xl);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-color);
  margin-top: var(--spacing-xl);
}

/* 运行日志硬件信息适配 */
.log-hardware-info {
  display: flex;
  flex-wrap: wrap; /* 允许换行 */
  gap: 8px;
  align-items: center;
}
.hardware-item {
  white-space: nowrap; /* 不允许内部文字换行 */
  display: flex;
  align-items: center;
  gap: 4px;
}
/* 调整标题栏以适应高度变化 */
.log-titlebar {
  height: auto !important; /* 允许高度自动撑开 */
  min-height: 48px;
  flex-wrap: wrap;
  gap: 8px;
}
.log-titlebar-right {
  display: flex;
  align-items: center;
  flex-wrap: wrap; /* 允许右侧按钮和信息换行 */
  gap: 8px;
}
</style>
