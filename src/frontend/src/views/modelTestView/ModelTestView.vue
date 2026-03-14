<template>
  <div class="preview-panel">
    <div class="preprocess-select-card">
      <div class="preview-title">
        <span>模型选择</span>
      </div>
      <div class="preprocess-select-content">
        <a-form layout="inline" class="model-select-row" style="width: 100%">
          <a-form-item
            class="select-item"
            style="flex: 1; padding: 0; margin-bottom: 0; border: none"
          >
            <div style="display: flex; align-items: center; width: 100%; gap: 8px">
              <span class="select-label">读取模型权重：</span>
              <a-select
                v-model:value="selectedModel"
                :options="modelOptions"
                placeholder="请选择模型权重"
                allow-clear
                style="flex: 1"
              />
            </div>
          </a-form-item>
          <a-form-item
            class="select-item"
            style="flex: 1; padding: 0; margin-bottom: 0; border: none"
          >
            <div style="display: flex; align-items: center; width: 100%; gap: 8px">
              <span class="select-label">筛选测试数据：</span>
              <a-select
                v-model:value="selectedTestData"
                :options="testDataOptions"
                placeholder="请选择测试数据"
                allow-clear
                style="flex: 1"
              />
            </div>
          </a-form-item>
          <a-form-item class="button-group" style="display: flex; align-items: center">
            <a-button type="primary" :loading="isTesting" @click="handleLoadModel">
              {{ isTesting ? '模型测试中' : '开始测试' }}
            </a-button>
            <a-button
              @click="handleShowLog"
              :disabled="!isTesting && !resultEnabled"
              style="margin-left: 12px"
              >输出日志</a-button
            >
          </a-form-item>
        </a-form>
      </div>
    </div>
    <div class="preprocess-bottom-row">
      <div class="preprocess-half-card left">
        <div class="preview-title">
          <a-form layout="inline" class="model-select-row" style="width: 100%">
            <a-form-item
              class="select-item"
              style="flex: 1; padding: 0; margin-bottom: 0; border: none"
            >
              <div style="display: flex; align-items: center; width: 100%">
                <span class="select-label">特征1：</span>
                <div style="display: flex; align-items: center; flex: 1; gap: 8px">
                  <a-select
                    :disabled="!originEnabled"
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
                  <a-button size="small" :disabled="!originEnabled" @click="showFeature1Modal = true"
                    >配置</a-button
                  >
                </div>
              </div>
            </a-form-item>
            <a-form-item
              class="select-item"
              style="flex: 1; padding: 0; margin-bottom: 0; border: none"
            >
              <div style="display: flex; align-items: center; width: 100%">
                <span class="select-label">特征2：</span>
                <div style="display: flex; align-items: center; flex: 1; gap: 8px">
                  <a-select
                    :disabled="!originEnabled"
                    v-model:value="testSetTags2"
                    :options="tagOptions"
                    mode="multiple"
                    allow-clear
                    style="
                      flex: 1;
                      border-right: none;
                      border-top-right-radius: 0;
                      border-bottom-right-radius: 0;
                    "
                    @change="onTagChange2"
                  />
                  <a-button size="small" :disabled="!originEnabled" @click="showFeature2Modal = true"
                    >配置</a-button
                  >
                </div>
              </div>
            </a-form-item>
          </a-form>
        </div>
        <div v-if="!originEnabled" class="preprocess-select-content">
          <img
            src="@/assets/无结果2.svg"
            alt="无结果"
            style="width: 100%; height: 100%; object-fit: contain; opacity: 0.7"
          />
        </div>
        <div v-else class="echarts-row">
          <div ref="chart1Ref" class="echart-half"></div>
          <div ref="chart2Ref" class="echart-half"></div>
        </div>
      </div>
      <div class="preprocess-half-card right">
        <div class="preview-title">
          <span>结果展示</span>
          <span class="preview-title-actions">
            <a-button @click="handleShowMetricModal" :disabled="!resultEnabled">误差展示表</a-button>
            <a-button
              type="primary"
              :icon="h(DownloadOutlined)"
              @click="exportExcel"
              :disabled="!resultEnabled"
            >
              导出为Excel
            </a-button>
            <a-button
              type="primary"
              :icon="h(DownloadOutlined)"
              @click="exportExcel"
              :disabled="!resultEnabled"
            >
              导出为TxT
            </a-button>
          </span>
        </div>
        <div v-if="!resultEnabled" class="preprocess-select-content">
          <img
            src="@/assets/无结果2.svg"
            alt="无结果"
            style="width: 100%; height: 100%; object-fit: contain; opacity: 0.7"
          />
        </div>
        <div v-else class="echarts-row">
          <div ref="chart3Ref" class="echart-all"></div>
        </div>
      </div>
    </div>

    <!-- 特征1弹窗 -->
    <a-modal
      v-model:open="showFeature1Modal"
      width="800px"
      :footer="null"
      :bodyStyle="{ height: modalHeight }"
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
          <div v-if="activeTab === 'indicators'" class="tab-content">
            <a-form
              :model="indicatorsForm"
              layout="vertical"
              ref="indicatorsFormRef"
              style="height: 100%; display: flex; flex-direction: column"
            >
              <div class="form-grid" style="flex: 1; overflow-y: auto">
                <template v-for="(tag, tagIndex) in testSetTags" :key="tagIndex">
                  <a-form-item
                    :label="`${tag}线条`"
                    :name="[tag, 'lineStyle']"
                    :rules="[{ required: true, message: '请选择线条样式' }]"
                  >
                    <a-select
                      v-model:value="indicatorsForm[tag].lineStyle"
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
                    :label="`${tag}颜色-RGB`"
                    :name="[tag, 'color']"
                    :rules="[{ required: true, message: '请选择颜色' }]"
                  >
                    <div style="display: flex; align-items: center; gap: 8px">
                      <a-input
                        v-model:value="indicatorsForm[tag].color"
                        :placeholder="`请输入${tag}颜色-16进制`"
                        style="flex: 1"
                      />
                      <input
                        type="color"
                        :value="indicatorsForm[tag].color"
                        @input="handleColorChange($event, tag)"
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
                        v-model:value="indicatorsForm[tag].range![0]"
                        :placeholder="`最小值`"
                        style="flex: 1"
                      />
                      <span style="color: #666; font-size: 14px; white-space: nowrap">-</span>
                      <a-input-number
                        v-model:value="indicatorsForm[tag].range![1]"
                        :placeholder="`最大值`"
                        style="flex: 1"
                      />
                    </div>
                  </a-form-item>
                </template>
              </div>
              <div style="margin-top: auto; text-align: right; padding-top: 16px">
                <a-button @click="handleFeature1ModalCancel" style="margin-right: 8px"
                  >取消</a-button
                >
                <a-button type="primary" @click="handleFeature1ModalOk"> 确定 </a-button>
              </div>
            </a-form>
          </div>

          <div v-if="activeTab === 'channels'" class="tab-content">
            <a-form layout="vertical" ref="channelsFormRef" :model="channelsForm">
              <div style="flex: 1; overflow-y: auto">
                <div class="channels-form-grid">
                  <a-form-item
                    label="对数刻度绘制曲线"
                    name="logarithmicScale"
                    :rules="[{ required: true, message: '请选择' }]"
                    ><a-select
                      v-model:value="channelsForm.logarithmicScale"
                      placeholder="请选择"
                      style="width: 100%"
                      ><a-select-option value="true">是 </a-select-option
                      ><a-select-option value="false">否 </a-select-option></a-select
                    ></a-form-item
                  >
                </div>
                <a-form-item style="width: 100%; margin-top: 20px"
                  ><a-checkbox v-model:checked="channelsForm.showScaleLines"
                    >显示刻度线</a-checkbox
                  ></a-form-item
                >
                <div class="channels-form-grid">
                  <a-form-item
                    label="细线"
                    name="thinLine"
                    :rules="[{ required: true, message: '请选择' }]"
                  >
                    <a-select
                      v-model:value="channelsForm.thinLine"
                      placeholder="请选择"
                      style="width: 100%"
                    >
                      <a-select-option value="1"
                        ><div style="display: flex; align-items: center; gap: 8px">
                          <span>1px</span>
                          <div
                            style="width: 40px; height: 1px; background: #333; border-radius: 0.5px"
                          ></div></div
                      ></a-select-option>
                      <a-select-option value="2"
                        ><div style="display: flex; align-items: center; gap: 8px">
                          <span>2px</span>
                          <div
                            style="width: 40px; height: 2px; background: #333; border-radius: 1px"
                          ></div></div
                      ></a-select-option>
                      <a-select-option value="3"
                        ><div style="display: flex; align-items: center; gap: 8px">
                          <span>3px</span>
                          <div
                            style="width: 40px; height: 3px; background: #333; border-radius: 1.5px"
                          ></div></div
                      ></a-select-option>
                      <a-select-option value="4"
                        ><div style="display: flex; align-items: center; gap: 8px">
                          <span>4px</span>
                          <div
                            style="width: 40px; height: 4px; background: #333; border-radius: 2px"
                          ></div></div
                      ></a-select-option>
                      <a-select-option value="5"
                        ><div style="display: flex; align-items: center; gap: 8px">
                          <span>5px</span>
                          <div
                            style="width: 40px; height: 5px; background: #333; border-radius: 2.5px"
                          ></div></div
                      ></a-select-option>
                    </a-select>
                  </a-form-item>
                  <a-form-item
                    label="份数"
                    name="thinLineCount"
                    :rules="[{ required: true, message: '请输入' }]"
                    ><a-input-number
                      v-model:value="channelsForm.thinLineCount"
                      :min="1"
                      :max="10"
                      style="width: 100%"
                  /></a-form-item>
                  <a-form-item label="粗线" name="thickLine" :rules="[{ required: true }]"
                    ><a-select
                      v-model:value="channelsForm.thickLine"
                      placeholder="请选择"
                      style="width: 100%"
                      ><a-select-option value="1"
                        ><div style="display: flex; align-items: center; gap: 8px">
                          <span>1px</span>
                          <div
                            style="width: 40px; height: 1px; background: #333; border-radius: 0.5px"
                          ></div></div></a-select-option
                      ><a-select-option value="2"
                        ><div style="display: flex; align-items: center; gap: 8px">
                          <span>2px</span>
                          <div
                            style="width: 40px; height: 2px; background: #333; border-radius: 1px"
                          ></div></div></a-select-option
                      ><a-select-option value="3"
                        ><div style="display: flex; align-items: center; gap: 8px">
                          <span>3px</span>
                          <div
                            style="width: 40px; height: 3px; background: #333; border-radius: 1.5px"
                          ></div></div></a-select-option
                      ><a-select-option value="4"
                        ><div style="display: flex; align-items: center; gap: 8px">
                          <span>4px</span>
                          <div
                            style="width: 40px; height: 4px; background: #333; border-radius: 2px"
                          ></div></div></a-select-option
                      ><a-select-option value="5"
                        ><div style="display: flex; align-items: center; gap: 8px">
                          <span>5px</span>
                          <div
                            style="width: 40px; height: 5px; background: #333; border-radius: 2.5px"
                          ></div></div></a-select-option></a-select
                  ></a-form-item>
                  <a-form-item
                    label="份数"
                    name="thickLineCount"
                    :rules="[{ required: true, message: '请输入' }]"
                    ><a-input-number
                      v-model:value="channelsForm.thickLineCount"
                      :min="1"
                      :max="10"
                      style="width: 100%"
                  /></a-form-item>
                </div>
                <a-form-item style="width: 100%; margin-top: 10px"
                  ><a-checkbox v-model:checked="channelsForm.showDepthLines"
                    >显示深度线</a-checkbox
                  ></a-form-item
                >
                <div class="channels-form-grid">
                  <a-form-item label="细线" name="depthThinLine" :rules="[{ required: true }]">
                    <a-select
                      placeholder="请选择"
                      style="width: 100%"
                      v-model:value="channelsForm.depthThinLine"
                    >
                      <a-select-option value="1"
                        ><div style="display: flex; align-items: center; gap: 8px">
                          <span>1px</span>
                          <div
                            style="width: 40px; height: 1px; background: #333; border-radius: 0.5px"
                          ></div></div
                      ></a-select-option>
                      <a-select-option value="2"
                        ><div style="display: flex; align-items: center; gap: 8px">
                          <span>2px</span>
                          <div
                            style="width: 40px; height: 2px; background: #333; border-radius: 1px"
                          ></div></div
                      ></a-select-option>
                      <a-select-option value="3"
                        ><div style="display: flex; align-items: center; gap: 8px">
                          <span>3px</span>
                          <div
                            style="width: 40px; height: 3px; background: #333; border-radius: 1.5px"
                          ></div></div
                      ></a-select-option>
                      <a-select-option value="4"
                        ><div style="display: flex; align-items: center; gap: 8px">
                          <span>4px</span>
                          <div
                            style="width: 40px; height: 4px; background: #333; border-radius: 2px"
                          ></div></div
                      ></a-select-option>
                      <a-select-option value="5"
                        ><div style="display: flex; align-items: center; gap: 8px">
                          <span>5px</span>
                          <div
                            style="width: 40px; height: 5px; background: #333; border-radius: 2.5px"
                          ></div></div
                      ></a-select-option>
                    </a-select>
                  </a-form-item>
                  <a-form-item
                    label="间隔"
                    name="depthInterval"
                    :rules="[{ required: true, message: '请输入' }]"
                    ><a-input-number
                      v-model:value="channelsForm.depthInterval"
                      :min="1"
                      :max="10"
                      addon-after="m"
                      style="width: 100%"
                  /></a-form-item>
                  <a-form-item label="粗线" :rules="[{ required: true }]"
                    ><a-select
                      placeholder="请选择"
                      style="width: 100%"
                      v-model:value="channelsForm.depthThickLine"
                      ><a-select-option value="1"
                        ><div style="display: flex; align-items: center; gap: 8px">
                          <span>1px</span>
                          <div
                            style="width: 40px; height: 1px; background: #333; border-radius: 0.5px"
                          ></div></div></a-select-option
                      ><a-select-option value="2"
                        ><div style="display: flex; align-items: center; gap: 8px">
                          <span>2px</span>
                          <div
                            style="width: 40px; height: 2px; background: #333; border-radius: 1px"
                          ></div></div></a-select-option
                      ><a-select-option value="3"
                        ><div style="display: flex; align-items: center; gap: 8px">
                          <span>3px</span>
                          <div
                            style="width: 40px; height: 3px; background: #333; border-radius: 1.5px"
                          ></div></div></a-select-option
                      ><a-select-option value="4"
                        ><div style="display: flex; align-items: center; gap: 8px">
                          <span>4px</span>
                          <div
                            style="width: 40px; height: 4px; background: #333; border-radius: 2px"
                          ></div></div></a-select-option
                      ><a-select-option value="5"
                        ><div style="display: flex; align-items: center; gap: 8px">
                          <span>5px</span>
                          <div
                            style="width: 40px; height: 5px; background: #333; border-radius: 2.5px"
                          ></div></div></a-select-option></a-select
                  ></a-form-item>
                  <a-form-item label="间隔" :rules="[{ required: true, message: '请输入' }]"
                    ><a-input-number
                      v-model:value="channelsForm.depthThickInterval"
                      :min="1"
                      :max="10"
                      addon-after="m"
                      style="width: 100%"
                  /></a-form-item>
                </div>
              </div>
              <div style="margin-top: auto; text-align: right; padding-top: 16px">
                <a-button @click="handleFeature1ModalCancel" style="margin-right: 8px"
                  >取消</a-button
                >
                <a-button type="primary" @click="handleFeature1ModalOk"> 确定 </a-button>
              </div>
            </a-form>
          </div>
        </div>
      </div>
    </a-modal>

    <!-- 特征2弹窗 -->
    <a-modal
      v-model:open="showFeature2Modal"
      width="800px"
      :footer="null"
      :bodyStyle="{ height: modalHeight2 }"
    >
      <div class="feature-modal-content">
        <div class="horizontal-anchor-nav">
          <a-anchor direction="horizontal">
            <a-anchor-link
              href="#indicators2"
              title="指标属性"
              :class="{ active: activeTab2 === 'indicators2' }"
              @click="activeTab2 = 'indicators2'"
            />
            <a-anchor-link
              href="#channels2"
              title="道属性"
              :class="{ active: activeTab2 === 'channels2' }"
              @click="activeTab2 = 'channels2'"
            />
          </a-anchor>
        </div>
        <div class="content-area">
          <div v-if="activeTab2 === 'indicators2'" class="tab-content">
            <a-form
              :model="indicatorsForm2"
              layout="vertical"
              ref="indicatorsFormRef2"
              style="height: 100%; display: flex; flex-direction: column"
            >
              <div class="form-grid" style="flex: 1; overflow-y: auto">
                <template v-for="(tag, tagIndex) in testSetTags2" :key="tagIndex">
                  <a-form-item
                    :label="`${tag}线条`"
                    :name="[tag, 'lineStyle']"
                    :rules="[{ required: true }]"
                    ><a-select
                      v-model:value="indicatorsForm2[tag].lineStyle"
                      :placeholder="`请选择${tag}线条`"
                      style="width: 100%"
                      ><a-select-option value="solid"
                        ><div style="display: flex; align-items: center; gap: 8px">
                          <span>实线</span>
                          <div
                            style="width: 40px; height: 2px; background: #333; border-radius: 1px"
                          ></div></div></a-select-option
                      ><a-select-option value="dashed"
                        ><div style="display: flex; align-items: center; gap: 8px">
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
                          ></div></div></a-select-option
                      ><a-select-option value="dotted"
                        ><div style="display: flex; align-items: center; gap: 8px">
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
                          ></div></div></a-select-option></a-select
                  ></a-form-item>
                  <a-form-item
                    :label="`${tag}颜色-RGB`"
                    :name="[tag, 'color']"
                    :rules="[{ required: true, message: '请选择颜色' }]"
                  >
                    <div style="display: flex; align-items: center; gap: 8px">
                      <a-input
                        v-model:value="indicatorsForm2[tag].color"
                        :placeholder="`请输入${tag}颜色-16进制`"
                        style="flex: 1"
                      />
                      <input
                        type="color"
                        :value="indicatorsForm2[tag].color || '#000000'"
                        @input="handleColorChange2($event, tag)"
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
                    :rules="[{ required: true, message: '请输入坐标范围' }]"
                    ><div style="display: flex; align-items: center; gap: 8px">
                      <a-input-number
                        v-model:value="indicatorsForm2[tag].range![0]"
                        :placeholder="`最小值`"
                        style="flex: 1"
                      /><span style="color: #666; font-size: 14px; white-space: nowrap">-</span
                      ><a-input-number
                        v-model:value="indicatorsForm2[tag].range![1]"
                        :placeholder="`最大值`"
                        style="flex: 1"
                      /></div
                  ></a-form-item>
                </template>
              </div>
              <div style="margin-top: auto; text-align: right; padding-top: 16px">
                <a-button @click="handleFeature2ModalCancel" style="margin-right: 8px"
                  >取消</a-button
                >
                <a-button type="primary" @click="handleFeature2ModalOk"> 确定 </a-button>
              </div>
            </a-form>
          </div>

          <div v-if="activeTab2 === 'channels2'" class="tab-content">
            <a-form layout="vertical" ref="channelsFormRef2" :model="channelsForm2">
              <div style="flex: 1; overflow-y: auto">
                <div class="channels-form-grid">
                  <a-form-item
                    label="对数刻度绘制曲线"
                    name="logarithmicScale"
                    :rules="[{ required: true }]"
                    ><a-select
                      v-model:value="channelsForm2.logarithmicScale"
                      placeholder="请选择"
                      style="width: 100%"
                      ><a-select-option value="true">是 </a-select-option
                      ><a-select-option value="false">否 </a-select-option></a-select
                    ></a-form-item
                  >
                </div>
                <a-form-item style="width: 100%; margin-top: 20px"
                  ><a-checkbox v-model:checked="channelsForm2.showScaleLines"
                    >显示刻度线</a-checkbox
                  ></a-form-item
                >
                <div class="channels-form-grid">
                  <a-form-item label="细线" name="thinLine" :rules="[{ required: true }]"
                    ><a-select
                      v-model:value="channelsForm2.thinLine"
                      placeholder="请选择"
                      style="width: 100%"
                      ><a-select-option value="1"
                        ><div style="display: flex; align-items: center; gap: 8px">
                          <span>1px</span>
                          <div
                            style="width: 40px; height: 1px; background: #333; border-radius: 0.5px"
                          ></div></div></a-select-option
                      ><a-select-option value="2"
                        ><div style="display: flex; align-items: center; gap: 8px">
                          <span>2px</span>
                          <div
                            style="width: 40px; height: 2px; background: #333; border-radius: 1px"
                          ></div></div></a-select-option
                      ><a-select-option value="3"
                        ><div style="display: flex; align-items: center; gap: 8px">
                          <span>3px</span>
                          <div
                            style="width: 40px; height: 3px; background: #333; border-radius: 1.5px"
                          ></div></div></a-select-option
                      ><a-select-option value="4"
                        ><div style="display: flex; align-items: center; gap: 8px">
                          <span>4px</span>
                          <div
                            style="width: 40px; height: 4px; background: #333; border-radius: 2px"
                          ></div></div></a-select-option
                      ><a-select-option value="5"
                        ><div style="display: flex; align-items: center; gap: 8px">
                          <span>5px</span>
                          <div
                            style="width: 40px; height: 5px; background: #333; border-radius: 2.5px"
                          ></div></div></a-select-option></a-select
                  ></a-form-item>
                  <a-form-item
                    label="份数"
                    name="thinLineCount"
                    :rules="[{ required: true, message: '请输入' }]"
                    ><a-input-number
                      v-model:value="channelsForm2.thinLineCount"
                      :min="1"
                      :max="10"
                      style="width: 100%"
                  /></a-form-item>
                  <a-form-item label="粗线" name="thickLine" :rules="[{ required: true }]"
                    ><a-select
                      v-model:value="channelsForm2.thickLine"
                      placeholder="请选择"
                      style="width: 100%"
                      ><a-select-option value="1"
                        ><div style="display: flex; align-items: center; gap: 8px">
                          <span>1px</span>
                          <div
                            style="width: 40px; height: 1px; background: #333; border-radius: 0.5px"
                          ></div></div></a-select-option
                      ><a-select-option value="2"
                        ><div style="display: flex; align-items: center; gap: 8px">
                          <span>2px</span>
                          <div
                            style="width: 40px; height: 2px; background: #333; border-radius: 1px"
                          ></div></div></a-select-option
                      ><a-select-option value="3"
                        ><div style="display: flex; align-items: center; gap: 8px">
                          <span>3px</span>
                          <div
                            style="width: 40px; height: 3px; background: #333; border-radius: 1.5px"
                          ></div></div></a-select-option
                      ><a-select-option value="4"
                        ><div style="display: flex; align-items: center; gap: 8px">
                          <span>4px</span>
                          <div
                            style="width: 40px; height: 4px; background: #333; border-radius: 2px"
                          ></div></div></a-select-option
                      ><a-select-option value="5"
                        ><div style="display: flex; align-items: center; gap: 8px">
                          <span>5px</span>
                          <div
                            style="width: 40px; height: 5px; background: #333; border-radius: 2.5px"
                          ></div></div></a-select-option></a-select
                  ></a-form-item>
                  <a-form-item
                    label="份数"
                    name="thickLineCount"
                    :rules="[{ required: true, message: '请输入' }]"
                    ><a-input-number
                      v-model:value="channelsForm2.thickLineCount"
                      :min="1"
                      :max="10"
                      style="width: 100%"
                  /></a-form-item>
                </div>
                <a-form-item style="width: 100%; margin-top: 10px"
                  ><a-checkbox v-model:checked="channelsForm2.showDepthLines"
                    >显示深度线</a-checkbox
                  ></a-form-item
                >
                <div class="channels-form-grid">
                  <a-form-item label="细线" name="depthThinLine" :rules="[{ required: true }]"
                    ><a-select
                      placeholder="请选择"
                      style="width: 100%"
                      v-model:value="channelsForm2.depthThinLine"
                      ><a-select-option value="1"
                        ><div style="display: flex; align-items: center; gap: 8px">
                          <span>1px</span>
                          <div
                            style="width: 40px; height: 1px; background: #333; border-radius: 0.5px"
                          ></div></div></a-select-option
                      ><a-select-option value="2"
                        ><div style="display: flex; align-items: center; gap: 8px">
                          <span>2px</span>
                          <div
                            style="width: 40px; height: 2px; background: #333; border-radius: 1px"
                          ></div></div></a-select-option
                      ><a-select-option value="3"
                        ><div style="display: flex; align-items: center; gap: 8px">
                          <span>3px</span>
                          <div
                            style="width: 40px; height: 3px; background: #333; border-radius: 1.5px"
                          ></div></div></a-select-option
                      ><a-select-option value="4"
                        ><div style="display: flex; align-items: center; gap: 8px">
                          <span>4px</span>
                          <div
                            style="width: 40px; height: 4px; background: #333; border-radius: 2px"
                          ></div></div></a-select-option
                      ><a-select-option value="5"
                        ><div style="display: flex; align-items: center; gap: 8px">
                          <span>5px</span>
                          <div
                            style="width: 40px; height: 5px; background: #333; border-radius: 2.5px"
                          ></div></div></a-select-option></a-select
                  ></a-form-item>
                  <a-form-item
                    label="间隔"
                    name="depthInterval"
                    :rules="[{ required: true, message: '请输入' }]"
                    ><a-input-number
                      v-model:value="channelsForm2.depthInterval"
                      :min="1"
                      :max="10"
                      addon-after="m"
                      style="width: 100%"
                  /></a-form-item>
                  <a-form-item label="粗线" :rules="[{ required: true }]"
                    ><a-select
                      placeholder="请选择"
                      style="width: 100%"
                      v-model:value="channelsForm2.depthThickLine"
                      ><a-select-option value="1"
                        ><div style="display: flex; align-items: center; gap: 8px">
                          <span>1px</span>
                          <div
                            style="width: 40px; height: 1px; background: #333; border-radius: 0.5px"
                          ></div></div></a-select-option
                      ><a-select-option value="2"
                        ><div style="display: flex; align-items: center; gap: 8px">
                          <span>2px</span>
                          <div
                            style="width: 40px; height: 2px; background: #333; border-radius: 1px"
                          ></div></div></a-select-option
                      ><a-select-option value="3"
                        ><div style="display: flex; align-items: center; gap: 8px">
                          <span>3px</span>
                          <div
                            style="width: 40px; height: 3px; background: #333; border-radius: 1.5px"
                          ></div></div></a-select-option
                      ><a-select-option value="4"
                        ><div style="display: flex; align-items: center; gap: 8px">
                          <span>4px</span>
                          <div
                            style="width: 40px; height: 4px; background: #333; border-radius: 2px"
                          ></div></div></a-select-option
                      ><a-select-option value="5"
                        ><div style="display: flex; align-items: center; gap: 8px">
                          <span>5px</span>
                          <div
                            style="width: 40px; height: 5px; background: #333; border-radius: 2.5px"
                          ></div></div></a-select-option></a-select
                  ></a-form-item>
                  <a-form-item label="间隔" :rules="[{ required: true, message: '请输入' }]"
                    ><a-input-number
                      v-model:value="channelsForm2.depthThickInterval"
                      :min="1"
                      :max="10"
                      addon-after="m"
                      style="width: 100%"
                  /></a-form-item>
                </div>
              </div>
              <div style="margin-top: auto; text-align: right; padding-top: 16px">
                <a-button @click="handleFeature2ModalCancel" style="margin-right: 8px"
                  >取消</a-button
                >
                <a-button type="primary" @click="handleFeature2ModalOk"> 确定 </a-button>
              </div>
            </a-form>
          </div>
        </div>
      </div>
    </a-modal>

    <!-- 现有日志与误差弹窗保留 -->
    <a-modal
      v-model:open="logModalVisible"
      title="输出日志"
      width="600px"
      :bodyStyle="{ padding: '0', height: '80vh', overflow: 'hidden' }"
    >
      <div class="log-modal-content">
        <div v-for="(log, idx) in logList" :key="idx">{{ log }}</div>
      </div>
      <template #footer>
        <div style="width: 100%; display: flex; justify-content: center">
          <button
            style="
              padding: 6px 32px;
              background: #fff;
              color: #e24a4ad9;
              border: 1px solid #d9d9d9;
              font-size: 14px;
              cursor: pointer;
            "
            @click="cancelTrain"
          >
            取消训练
          </button>
        </div>
      </template>
    </a-modal>
    <a-modal v-model:open="showMetricModal" title="误差展示表" width="400px" :footer="null">
      <a-table
        :columns="metricTableColumns"
        :data-source="metricTableData"
        :pagination="false"
        bordered
        size="small"
        style="margin-bottom: 24px"
      />
      <div style="width: 100%; display: flex; justify-content: center; gap: 24px">
        <a-button type="primary" :icon="h(DownloadOutlined)" @click="handleExportExcel"
          >导出为Excel</a-button
        >
        <a-button type="primary" :icon="h(DownloadOutlined)" @click="handleExportTxt"
          >导出为TxT</a-button
        >
      </div>
    </a-modal>
  </div>
</template>
<script setup lang="ts">
// 可根据需要引入相关逻辑
import { ref, h, onMounted, onUnmounted, nextTick, watch, reactive, computed } from 'vue'
import * as echarts from 'echarts'
// 已不再需要文件icon相关内容
import { DownloadOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import { getCurveRange } from '@/components/echarts/echartsHelper'
import { buildCustomOptions } from '@/components/echarts/chartOptionHelper'
import { getAddSelect, getTreeData, getModelTestingResult, getTestOutputResult } from '@/utils/api'
import type { Rule } from 'ant-design-vue/es/form'
import { useStore } from 'vuex'
// import VChart from 'vue-echarts' // 未直接用到可移除

// Socket.IO 相关
declare const io: any
let socket: any = null

// 日志弹窗相关
const logModalVisible = ref(false)
const logList = ref<string[]>([])
let logTimer: number | null = null

const store = useStore()
const testTags = computed(() => store.state.testTags)

// echarts相关
const testSetTags = ref<string[]>([])
const testSetTags2 = ref<string[]>([])
const tagOptions = ref<{ label: string; value: string }[]>([])
const maxLenCurve = ref(0)
const allData = ref<Record<string, number[][]>>({})
const resultData = ref<Record<string, number[][]>>({})
interface IndicatorConfig {
  lineStyle?: string
  color?: string
  range?: [number, number]
}
const indicatorsForm = reactive<Record<string, IndicatorConfig>>({})
const indicatorsForm2 = reactive<Record<string, IndicatorConfig>>({})
const colorArray = [
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

watch(
  testSetTags,
  (newTags) => {
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
          const { min, max } = getCurveRange(tag, chartData)
          indicatorsForm[tag].range = [min, max]
        }
      }
      console.log('indicatorsForm：', indicatorsForm)
    })
  },
  { immediate: true }
)

// 监听特征2选择框变化，更新表单对象（与 DataPreprocessView 保持一致）
watch(
  testSetTags2,
  (newTags) => {
    newTags.forEach((tag, index) => {
      if (!indicatorsForm2[tag]) {
        indicatorsForm2[tag] = {
          lineStyle: 'solid',
          color: colorArray[index],
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

function onTagChange1(value: string[]) {
  testSetTags.value = value
  maxLenCurve.value = Math.max(value.length, testSetTags2.value.length)
  chart1Option.value = buildCustomOptions(
    testSetTags.value,
    allData.value,
    buildCustomConfig(testSetTags.value, indicatorsForm, allData.value),
    channelsForm,
    maxLenCurve.value
  )
  updateCharts()
}

function onTagChange2(value: string[]) {
  testSetTags2.value = value
  maxLenCurve.value = Math.max(testSetTags.value.length, value.length)
  chart2Option.value = buildCustomOptions(
    testSetTags2.value,
    allData.value,
    buildCustomConfig(testSetTags2.value, indicatorsForm2, allData.value),
    channelsForm2,
    maxLenCurve.value
  )
  updateCharts()
}

// Socket.IO 连接和通信方法
function initSocket() {
  try {
    // 连接到Socket.IO服务器（这里使用本地服务器，您可以根据需要修改URL）
    socket = io('http://127.0.0.1:5000')

    // 连接成功
    socket.on('connect', () => {
      console.log('Socket.IO 连接成功')
      message.success('Socket.IO 连接成功')
    })

    // 连接错误
    socket.on('connect_error', (error: any) => {
      console.error('Socket.IO 连接失败:', error)
      message.error('Socket.IO 连接失败')
    })

    // 接收消息
    socket.on('message', (data: any) => {
      console.log('收到消息:', data)
      logList.value.push(`【${new Date().toLocaleTimeString()}】收到: ${JSON.stringify(data)}`)
      nextTick(() => {
        const modal = document.querySelector('.log-modal-content')
        if (modal) (modal as HTMLElement).scrollTop = (modal as HTMLElement).scrollHeight
      })
    })

    // 接收测试进度
    socket.on('testing_progress', (data: any) => {
      console.log('测试进度:', data)
      logList.value.push(`【${new Date().toLocaleTimeString()}】测试进度: ${data.progress}%`)
      nextTick(() => {
        const modal = document.querySelector('.log-modal-content')
        if (modal) (modal as HTMLElement).scrollTop = (modal as HTMLElement).scrollHeight
      })
    })

    // 接收测试完成
    socket.on('testing_complete', (data: any) => {
      console.log('测试完成:', data)
      logList.value.push(`【${new Date().toLocaleTimeString()}】测试完成: ${JSON.stringify(data)}`)
      isTesting.value = false
      resultEnabled.value = true
      if (logTimer) clearInterval(logTimer)
      nextTick(() => {
        const modal = document.querySelector('.log-modal-content')
        if (modal) (modal as HTMLElement).scrollTop = (modal as HTMLElement).scrollHeight
      })
    })

    socket.on('multitype_log', (payload: any) => {
      const event = payload?.event
      const content = payload?.data?.content
      const text =
        typeof content === 'string'
          ? content
          : content !== undefined
            ? JSON.stringify(content)
            : JSON.stringify(payload)
      logList.value.push(`【${new Date().toLocaleTimeString()}】${event || 'log'}: ${text}`)
      nextTick(() => {
        const modal = document.querySelector('.log-modal-content')
        if (modal) (modal as HTMLElement).scrollTop = (modal as HTMLElement).scrollHeight
      })
    })
  } catch (error) {
    console.error('初始化Socket.IO失败:', error)
    message.error('初始化Socket.IO失败')
  }
}

// 发送消息方法
function sendMessage(msg: string) {
  if (socket && socket.connected) {
    socket.emit('message', { text: msg, timestamp: new Date().toISOString() })
    console.log('发送消息:', msg)
  } else {
    message.warning('Socket.IO 未连接')
  }
}

// 发送测试请求
function sendTestingRequest(modelData: any) {
  if (socket && socket.connected) {
    socket.emit('start_testing', modelData)
    console.log('发送测试请求:', modelData)
  } else {
    message.warning('Socket.IO 未连接')
  }
}

const feature1 = ref<string[]>([])
const feature2 = ref<string[]>([])

function startLog() {
  logList.value = []
}
function handleShowLog() {
  logModalVisible.value = true
}

function resizeCharts() {
  if (chart1Instance) chart1Instance.resize()
  if (chart2Instance) chart2Instance.resize()
  if (chart3Instance) chart3Instance.resize()
}

onMounted(() => {
  window.addEventListener('resize', resizeCharts)
  // 初始化Socket.IO连接
  initSocket()
  refreshSelectOptions()
})

onUnmounted(() => {
  window.removeEventListener('resize', resizeCharts)
  if (logTimer) clearInterval(logTimer)
  if (chart1Instance) chart1Instance.dispose()
  if (chart2Instance) chart2Instance.dispose()
  if (chart3Instance) chart3Instance.dispose()

  // 断开Socket.IO连接
  if (socket) {
    socket.disconnect()
    console.log('Socket.IO 连接已断开')
  }
})

// 导出功能占位，防止报错
function exportExcel() {
  // 占位方法，后续可实现导出功能
}

const isTesting = ref(false)
const originEnabled = ref(false)
const resultEnabled = ref(false)

// 独立的下拉框数据和选中项
const modelOptions = ref<{ label: string; value: string; type: string }[]>([])
const selectedModel = ref<string>('')
const testDataOptions = ref<{ label: string; value: number }[]>([])
const selectedTestData = ref<number | undefined>(undefined)

watch(selectedTestData, async (fileId) => {
  resultEnabled.value = false
  resultData.value = {}
  chart3Option.value = {}
  if (!fileId) {
    originEnabled.value = false
    updateCharts()
    return
  }
  await loadOriginCurves(fileId)
})

const chart1Option = ref({})
const chart2Option = ref({})
const chart3Option = ref({})
// 不再使用vue-echarts，直接用echarts
const chart1Ref = ref<HTMLDivElement | null>(null)
const chart2Ref = ref<HTMLDivElement | null>(null)
const chart3Ref = ref<HTMLDivElement | null>(null)
let chart1Instance: echarts.ECharts | null = null
let chart2Instance: echarts.ECharts | null = null
let chart3Instance: echarts.ECharts | null = null

const buildCustomConfig = (
  tags: string[],
  formModel: Record<string, IndicatorConfig>,
  data: Record<string, number[][]>
) => {
  const config: Record<string, { lineStyle?: string; color?: string; range?: [number, number] }> =
    {}

  tags.forEach((tag, index) => {
    const tagConfig = formModel[tag] || {}

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
      color: tagConfig.color || colorArray[index] || '#000000',
      range,
    }
  })

  return config
}

async function refreshSelectOptions() {
  try {
    const [treeRes, modelRes] = await Promise.all([getTreeData(), getAddSelect()])

    if (treeRes?.data && Array.isArray(treeRes.data) && treeRes.data.length > 0) {
      const rawNodes = treeRes.data[0]?.children ?? []
      const fileOptions: { label: string; value: number }[] = []
      const visit = (nodes: any[]) => {
        ;(nodes || []).forEach((n: any) => {
          if (!n) return
          if (n.type === 'directory') {
            visit(n.children ?? [])
            return
          }
          if (typeof n.id === 'number') {
            fileOptions.push({ label: n.title ?? n.name ?? String(n.id), value: n.id })
          }
        })
      }
      visit(rawNodes)
      testDataOptions.value = fileOptions
    }

    if (modelRes?.data) {
      const best = (modelRes.data['best-data'] ?? []).map((t: any) => ({
        label: t.name,
        value: `${t.id}-best-data`,
        type: 'best-data',
      }))
      const final = (modelRes.data['final-data'] ?? []).map((t: any) => ({
        label: t.name,
        value: `${t.id}-final-data`,
        type: 'final-data',
      }))
      modelOptions.value = [...best, ...final]
    }
  } catch (e) {
    message.error('加载下拉选项失败')
  }
}

async function loadOriginCurves(fileId: number) {
  originEnabled.value = false
  testSetTags.value = []
  testSetTags2.value = []
  tagOptions.value = []
  allData.value = {}

  const res = await getModelTestingResult({ file_id: fileId })
  if (res?.code !== 200) {
    message.error(res?.message || '读取曲线数据失败')
    updateCharts()
    return
  }

  const c1 = res?.data?.options?.character1 ?? []
  const c2 = res?.data?.options?.character2 ?? []
  maxLenCurve.value = Math.max(c1.length, c2.length)

  testSetTags.value = c1
  testSetTags2.value = c2
  tagOptions.value = [...c1, ...c2].map((t: string) => ({ label: t, value: t }))

  const data1 = res?.data?.axisData ?? {}
  const data2 = res?.data?.axisData2 ?? {}
  allData.value = { ...data1, ...data2 }

  chart1Option.value = buildCustomOptions(
    testSetTags.value,
    allData.value,
    buildCustomConfig(testSetTags.value, indicatorsForm, allData.value),
    channelsForm,
    maxLenCurve.value
  )
  chart2Option.value = buildCustomOptions(
    testSetTags2.value,
    allData.value,
    buildCustomConfig(testSetTags2.value, indicatorsForm2, allData.value),
    channelsForm2,
    maxLenCurve.value
  )

  originEnabled.value = true
  updateCharts()
}

function updateCharts() {
  nextTick(() => {
    if (chart1Ref.value) {
      if (!chart1Instance) chart1Instance = echarts.init(chart1Ref.value)
      if (originEnabled.value) chart1Instance.setOption(chart1Option.value, { notMerge: true })
      else chart1Instance.clear()
    }
    if (chart2Ref.value) {
      if (!chart2Instance) chart2Instance = echarts.init(chart2Ref.value)
      if (originEnabled.value) chart2Instance.setOption(chart2Option.value, { notMerge: true })
      else chart2Instance.clear()
    }
    if (chart3Ref.value) {
      if (!chart3Instance) chart3Instance = echarts.init(chart3Ref.value)
      if (resultEnabled.value) chart3Instance.setOption(chart3Option.value, { notMerge: true })
      else chart3Instance.clear()
    }
    resizeCharts()
  })
  return
  // 示例数据
  function generateCurveData(length = 100, min = 40, max = 160) {
    const data = []
    const depthStep = 6000 / length
    let current = (min + max) / 2
    for (let i = 0; i < length; i++) {
      const noise = (Math.random() - 0.5) * 20
      current = Math.max(min, Math.min(max, current + noise))
      const depth = i * depthStep
      data.push([current, depth])
    }
    return data
  }

  const gr = generateCurveData(100, 40, 160)
  const sp = generateCurveData(100, 50, 110)
  const cal = generateCurveData(100, 10, 40)

  const a = generateCurveData(100, 0, 1)
  const b = generateCurveData(100, 0, 1)

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' },
    },
    legend: {
      bottom: 0,
      // icon: 'line',
      data: ['GR (API)', 'SP (mV)', 'CAL (mm)'],
    },
    grid: {
      left: 70,
      right: 20,
      top: 40,
      bottom: 120,
    },
    xAxis: [
      {
        name: 'GR (API)',
        nameLocation: 'middle',
        // nameGap: 30,
        nameTextStyle: {
          align: 'left',
          color: '#00B050',
          padding: [0, 0, 0, -260],
        },
        type: 'value',
        min: 40,
        max: 160,
        position: 'bottom',
        offset: 24,
        axisLine: { show: false, lineStyle: { color: '#00B050' } },
        axisLabel: { color: '#00B050', margin: 8 },
        axisTick: { show: false },
      },
      {
        name: 'SP (mV)',
        nameLocation: 'middle',
        // nameGap: 30,
        nameTextStyle: {
          align: 'left',
          color: '#0070C0',
          padding: [0, 0, 0, -260],
        },
        type: 'value',
        min: 50,
        max: 110,
        position: 'bottom',
        offset: 12,
        axisLine: { show: false, lineStyle: { color: '#0070C0' } },
        axisLabel: { color: '#0070C0', margin: 8 },
        axisTick: { show: false },
      },
      {
        name: 'CAL (mm)',
        nameLocation: 'middle',
        // nameGap: 30,
        nameTextStyle: {
          align: 'left',
          color: '#C000B0',
          padding: [0, 0, 0, -260],
        },
        type: 'value',
        min: 10,
        max: 40,
        position: 'bottom',
        offset: 0,
        axisLine: { show: false, lineStyle: { color: '#C000B0' } },
        axisLabel: { color: '#C000B0', margin: 8 },
        axisTick: { show: false },
      },
    ],
    yAxis: {
      type: 'value',
      inverse: true,
      name: 'Depth (m)',
      nameLocation: 'start',
      nameGap: 10,
    },
    series: [
      {
        name: 'GR (API)',
        type: 'line',
        xAxisIndex: 0,
        yAxisIndex: 0,
        data: gr,
        lineStyle: { color: '#00B050' },
        itemStyle: { color: '#00B050' },
        symbol: 'none',
        showSymbol: false,
      },
      {
        name: 'SP (mV)',
        type: 'line',
        xAxisIndex: 1,
        yAxisIndex: 0,
        data: sp,
        lineStyle: { color: '#0070C0' },
        itemStyle: { color: '#0070C0' },
        symbol: 'none',
        showSymbol: false,
      },
      {
        name: 'CAL (mm)',
        type: 'line',
        xAxisIndex: 2,
        yAxisIndex: 0,
        data: cal,
        lineStyle: { color: '#C000B0' },
        itemStyle: { color: '#C000B0' },
        symbol: 'none',
        showSymbol: false,
      },
    ],
  }

  chart1Option.value = option
  chart2Option.value = JSON.parse(JSON.stringify(chart1Option.value))
  chart3Option.value = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' },
    },
    legend: {
      bottom: 0,
      // icon: 'line',
      data: ['A', 'B'],
    },
    grid: {
      left: 60,
      right: 20,
      top: 40,
      bottom: 60,
    },
    xAxis: {
      type: 'value',
      min: 0,
      max: 1,
      position: 'bottom',
      axisLine: { show: true, lineStyle: { color: '#000' } },
      axisLabel: { show: true, color: '#000', margin: 8 },
      axisTick: { show: false },
      name: '', // 不显示 name
    },
    yAxis: {
      type: 'value',
      inverse: true,
      name: 'Depth (m)',
      nameLocation: 'start',
      nameGap: 10,
    },
    series: [
      {
        name: 'A',
        type: 'line',
        xAxisIndex: 0,
        yAxisIndex: 0,
        data: a,
        lineStyle: { color: '#1CB052' },
        itemStyle: { color: '#1CB052' },
        symbol: 'none',
        showSymbol: false,
      },
      {
        name: 'B',
        type: 'line',
        xAxisIndex: 0,
        yAxisIndex: 0,
        data: b,
        lineStyle: { color: '#1650FF' },
        itemStyle: { color: '#1650FF' },
        symbol: 'none',
        showSymbol: false,
      },
    ],
  }
  nextTick(() => {
    if (chart1Ref.value) {
      if (!chart1Instance) {
        chart1Instance = echarts.init(chart1Ref.value)
      }
      chart1Instance.setOption(chart1Option.value)
    }
    if (chart2Ref.value) {
      if (!chart2Instance) {
        chart2Instance = echarts.init(chart2Ref.value)
      }
      chart2Instance.setOption(chart2Option.value)
    }
    if (chart3Ref.value) {
      if (!chart3Instance) {
        chart3Instance = echarts.init(chart3Ref.value)
      }
      chart3Instance.setOption(chart3Option.value)
    }
    resizeCharts()
  })
}

// 按钮处理函数
const handleLoadModel = async () => {
  if (!selectedModel.value || !selectedTestData.value) {
    message.warning('请先选择模型权重和测试数据！')
    return
  }
  if (!testTags.value?.[0]) {
    message.warning('请到新增模型模块选择测试集！')
    return
  }

  isTesting.value = true
  resultEnabled.value = false
  resultData.value = {}
  chart3Option.value = {}
  logModalVisible.value = true
  startLog()

  const match = /^(\d+)-(best-data|final-data)$/.exec(selectedModel.value)
  const idm = match ? Number(match[1]) : Number(selectedModel.value.split('-')[0]) || 0
  const type = match ? match[2] : modelOptions.value.find((m) => m.value === selectedModel.value)?.type

  try {
    const res = await getTestOutputResult({
      dir_id: testTags.value[0],
      idm,
      file_id: selectedTestData.value,
      predict_mode: false,
      type: type || 'best-data',
    })

    if (res?.code !== 200) {
      resultEnabled.value = false
      return
    }

    const table = res?.data?.table ?? {}
    metricTableData.value = Object.entries(table).map(([metric, value]) => ({
      metric,
      value: value as any,
    }))

    const tags = ['prediction_coords', 'true_coords']
    resultData.value = {
      prediction_coords: res?.data?.prediction_coords ?? [],
      true_coords: res?.data?.true_coords ?? [],
    }

    const resultConfig: Record<string, { lineStyle?: string; color?: string; range?: [number, number] }> =
      {}
    tags.forEach((tag) => {
      const curveData = resultData.value[tag] || []
      const { min, max } = getCurveRange(tag, curveData)
      resultConfig[tag] = {
        lineStyle: 'solid',
        color: tag === 'prediction_coords' ? '#FF0000' : '#0000FF',
        range: [min, max],
      }
    })

    chart3Option.value = buildCustomOptions(tags, resultData.value, resultConfig, channelsForm, tags.length, true)
    resultEnabled.value = true
    updateCharts()
    logList.value.push(`【${new Date().toLocaleTimeString()}】测试完成`)
  } finally {
    isTesting.value = false
  }
}

// 取消训练逻辑
function cancelTrain() {
  logModalVisible.value = false
  isTesting.value = false
  if (logTimer) clearInterval(logTimer)
  selectedModel.value = ''
  selectedTestData.value = undefined
}

// 测试Socket.IO连接
function handleTestSocket() {
  const testMessage = `测试消息 - ${new Date().toLocaleTimeString()}`
  sendMessage(testMessage)
  message.success('测试消息已发送')
}

// 误差展示表弹窗相关
const showMetricModal = ref(false)
const metricTableData = ref([
  { metric: 'MAE', value: 0.123 },
  { metric: 'MSE', value: 0.456 },
  { metric: 'RMSE', value: 0.789 },
  { metric: 'R2', value: 0.912 },
  { metric: 'MAPE', value: 0.234 },
  { metric: 'SMAPE', value: 0.345 },
  { metric: 'Bias', value: 0.567 },
])
const metricTableColumns = [
  { title: 'Metric', dataIndex: 'metric', key: 'metric' },
  { title: 'Value', dataIndex: 'value', key: 'value' },
]
function handleShowMetricModal() {
  showMetricModal.value = true
}
function handleExportExcel() {
  // TODO: 实现导出Excel
}
function handleExportTxt() {
  // TODO: 实现导出TxT
}

// 特征1/特征2弹窗与表单（完全复用DataPreprocessView逻辑）
const showFeature1Modal = ref(false)
const activeTab = ref<'indicators' | 'channels'>('indicators')
const showFeature2Modal = ref(false)
const activeTab2 = ref<'indicators2' | 'channels2'>('indicators2')

const modalHeight = computed(() => {
  if (activeTab.value === 'indicators') {
    const rows = testSetTags.value.length
    const baseHeight = 200
    const rowHeight = 70
    return `${baseHeight + rows * rowHeight}px`
  }
  return '700px'
})

const modalHeight2 = computed(() => {
  if (activeTab2.value === 'indicators2') {
    const rows = testSetTags2.value.length
    const baseHeight = 200
    const rowHeight = 70
    return `${baseHeight + rows * rowHeight}px`
  }
  return '700px'
})

// 指标与道属性表单
const indicatorsFormRef = ref()
const channelsFormRef = ref()
const indicatorsFormRef2 = ref()
const channelsFormRef2 = ref()

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

const channelsForm = reactive<ChannelConfig>({
  logarithmicScale: 'true',
  showScaleLines: true,
  thinLine: '1',
  thinLineCount: 10,
  thickLine: '3',
  thickLineCount: 2,
  showDepthLines: true,
  depthThinLine: '1',
  depthInterval: 1,
  depthThickLine: '3',
  depthThickInterval: 10,
})

const channelsForm2 = reactive<ChannelConfig>({
  logarithmicScale: 'true',
  showScaleLines: true,
  thinLine: '1',
  thinLineCount: 10,
  thickLine: '3',
  thickLineCount: 2,
  showDepthLines: true,
  depthThinLine: '1',
  depthInterval: 1,
  depthThickLine: '3',
  depthThickInterval: 10,
})

// 校验坐标范围
const validateRange: Rule['validator'] = (_, value: unknown) => {
  if (!Array.isArray(value) || value.length !== 2) return Promise.reject('必须输入两个数值')
  if (value.some((v) => v === undefined || v === null || v === ''))
    return Promise.reject('坐标不能为空')
  if (Number(value[0]) >= Number(value[1])) return Promise.reject('最小值必须小于最大值')
  return Promise.resolve()
}

const handleColorChange = (event: Event, tag: string) => {
  const target = event.target as HTMLInputElement
  indicatorsForm[tag].color = target.value
}

const handleColorChange2 = (event: Event, tag: string) => {
  const target = event.target as HTMLInputElement
  indicatorsForm2[tag].color = target.value
}

const handleFeature1ModalCancel = () => {
  showFeature1Modal.value = false
}

const handleFeature2ModalCancel = () => {
  showFeature2Modal.value = false
}

const handleFeature1ModalOk = () => {
  if (activeTab.value === 'indicators') {
    indicatorsFormRef.value.validate().then(() => {
      updateCharts()
      message.success('指标属性配置已更新，图表已刷新')
      showFeature1Modal.value = false
    })
  } else if (activeTab.value === 'channels') {
    channelsFormRef.value.validate?.().then?.(() => {
      updateCharts()
      message.success('道属性配置已更新，图表已刷新')
      showFeature1Modal.value = false
    })
  }
}

const handleFeature2ModalOk = () => {
  if (activeTab2.value === 'indicators2') {
    indicatorsFormRef2.value.validate().then(() => {
      updateCharts()
      message.success('指标属性配置已更新，图表已刷新')
      showFeature2Modal.value = false
    })
  } else if (activeTab2.value === 'channels2') {
    channelsFormRef2.value.validate?.().then?.(() => {
      updateCharts()
      message.success('道属性配置已更新，图表已刷新')
      showFeature2Modal.value = false
    })
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
  height: 116px;
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
  padding: 16px;
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
  font-size: 14px;
  color: #5a5a68;
  min-width: 70px;
  font-weight: 400;
  white-space: nowrap;
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
.preprocess-title-inputs {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  background: #f5f7fa;
  height: 60px;
}

.feature-item {
  display: flex;
  align-items: center;
  /* gap: 12px; */
  flex: 1;
}

.button-group {
  display: flex;
  align-items: center;
  gap: 12px;
  height: 100%;
}

:deep(.ant-btn),
:deep(.ant-btn-primary),
:deep(.ant-btn-default),
:deep(.ant-btn-dangerous) {
  border-radius: 0 !important;
}
.log-modal-content {
  height: 100%;
  overflow-y: auto;
  background: #fff;
  color: #232b3a;
  font-family: monospace;
  font-size: 14px;
  /* padding: 12px;
      border-radius: 4px; */
  border: 1px solid #eee;
}
.echarts-row {
  display: flex;
  width: 100%;
  gap: 16px;
  margin-top: 16px;
  height: 100%;
}
.echart-half {
  width: 50%;
  height: 100%;
  min-width: 0;
}
.echart-all {
  width: 100%;
  height: 100%;
  min-width: 0;
}
/* 特征弹窗样式（复用） */
.feature-modal-content {
  display: flex;
  flex-direction: column;
  height: 100%;
}
.horizontal-anchor-nav {
  padding: 0 12px 12px;
  border-bottom: 1px solid #f0f0f0;
}
.horizontal-anchor-nav :deep(.ant-anchor-wrapper) {
  background: transparent;
}
.horizontal-anchor-nav :deep(.ant-anchor) {
  display: flex;
  gap: 12px;
}
.horizontal-anchor-nav :deep(.ant-anchor-link-title) {
  padding: 8px 12px;
  border-radius: 4px;
  cursor: pointer;
}
.horizontal-anchor-nav :deep(.ant-anchor-link-title.active) {
  background: #e6f4ff;
  color: #1677ff;
}
.content-area {
  flex: 1;
  display: flex;
  height: 100%;
  padding: 12px;
}
.tab-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}
.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px 16px;
}
.channels-form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px 16px;
}
</style>
