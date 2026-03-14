<template>
  <div>
    <!-- 特征1弹窗 -->
    <a-modal
      v-if="false"
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

        <!-- 内容区域 -->
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
                <a-button @click="handleFeature1ModalCancel" style="margin-right: 8px">
                  取消
                </a-button>
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
                  >
                    <a-select
                      v-model:value="channelsForm.logarithmicScale"
                      placeholder="请选择"
                      style="width: 100%"
                    >
                      <a-select-option value="true">是 </a-select-option>
                      <a-select-option value="false">否 </a-select-option>
                    </a-select>
                  </a-form-item>
                </div>
                <a-form-item style="width: 100%; margin-top: 20px">
                  <a-checkbox v-model:checked="channelsForm.showScaleLines">显示刻度线</a-checkbox>
                </a-form-item>
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
                      <a-select-option value="1">
                        <div style="display: flex; align-items: center; gap: 8px">
                          <span>1px</span>
                          <div
                            style="width: 40px; height: 1px; background: #333; border-radius: 0.5px"
                          ></div>
                        </div>
                      </a-select-option>
                      <a-select-option value="2">
                        <div style="display: flex; align-items: center; gap: 8px">
                          <span>2px</span>
                          <div
                            style="width: 40px; height: 2px; background: #333; border-radius: 1px"
                          ></div>
                        </div>
                      </a-select-option>
                      <a-select-option value="3">
                        <div style="display: flex; align-items: center; gap: 8px">
                          <span>3px</span>
                          <div
                            style="width: 40px; height: 3px; background: #333; border-radius: 1.5px"
                          ></div>
                        </div>
                      </a-select-option>
                      <a-select-option value="4">
                        <div style="display: flex; align-items: center; gap: 8px">
                          <span>4px</span>
                          <div
                            style="width: 40px; height: 4px; background: #333; border-radius: 2px"
                          ></div>
                        </div>
                      </a-select-option>
                      <a-select-option value="5">
                        <div style="display: flex; align-items: center; gap: 8px">
                          <span>5px</span>
                          <div
                            style="width: 40px; height: 5px; background: #333; border-radius: 2.5px"
                          ></div>
                        </div>
                      </a-select-option>
                    </a-select>
                  </a-form-item>
                  <a-form-item
                    label="份数"
                    name="thinLineCount"
                    :rules="[{ required: true, message: '请输入' }]"
                  >
                    <a-input-number
                      v-model:value="channelsForm.thinLineCount"
                      :min="1"
                      :max="10"
                      style="width: 100%"
                    />
                  </a-form-item>
                  <a-form-item label="粗线" name="thickLine" :rules="[{ required: true }]">
                    <a-select
                      v-model:value="channelsForm.thickLine"
                      placeholder="请选择"
                      style="width: 100%"
                    >
                      <a-select-option value="1">
                        <div style="display: flex; align-items: center; gap: 8px">
                          <span>1px</span>
                          <div
                            style="width: 40px; height: 1px; background: #333; border-radius: 0.5px"
                          ></div>
                        </div>
                      </a-select-option>
                      <a-select-option value="2">
                        <div style="display: flex; align-items: center; gap: 8px">
                          <span>2px</span>
                          <div
                            style="width: 40px; height: 2px; background: #333; border-radius: 1px"
                          ></div>
                        </div>
                      </a-select-option>
                      <a-select-option value="3">
                        <div style="display: flex; align-items: center; gap: 8px">
                          <span>3px</span>
                          <div
                            style="width: 40px; height: 3px; background: #333; border-radius: 1.5px"
                          ></div>
                        </div>
                      </a-select-option>
                      <a-select-option value="4">
                        <div style="display: flex; align-items: center; gap: 8px">
                          <span>4px</span>
                          <div
                            style="width: 40px; height: 4px; background: #333; border-radius: 2px"
                          ></div>
                        </div>
                      </a-select-option>
                      <a-select-option value="5">
                        <div style="display: flex; align-items: center; gap: 8px">
                          <span>5px</span>
                          <div
                            style="width: 40px; height: 5px; background: #333; border-radius: 2.5px"
                          ></div>
                        </div>
                      </a-select-option>
                    </a-select>
                  </a-form-item>
                  <a-form-item
                    label="份数"
                    name="thickLineCount"
                    :rules="[{ required: true, message: '请输入' }]"
                  >
                    <a-input-number
                      v-model:value="channelsForm.thickLineCount"
                      :min="1"
                      :max="10"
                      style="width: 100%"
                    />
                  </a-form-item>
                </div>
                <a-form-item style="width: 100%; margin-top: 10px">
                  <a-checkbox v-model:checked="channelsForm.showDepthLines">显示深度线</a-checkbox>
                </a-form-item>
                <div class="channels-form-grid">
                  <a-form-item label="细线" name="depthThinLine" :rules="[{ required: true }]">
                    <a-select
                      placeholder="请选择"
                      style="width: 100%"
                      v-model:value="channelsForm.depthThinLine"
                    >
                      <a-select-option value="1">
                        <div style="display: flex; align-items: center; gap: 8px">
                          <span>1px</span>
                          <div
                            style="width: 40px; height: 1px; background: #333; border-radius: 0.5px"
                          ></div>
                        </div>
                      </a-select-option>
                      <a-select-option value="2">
                        <div style="display: flex; align-items: center; gap: 8px">
                          <span>2px</span>
                          <div
                            style="width: 40px; height: 2px; background: #333; border-radius: 1px"
                          ></div>
                        </div>
                      </a-select-option>
                      <a-select-option value="3">
                        <div style="display: flex; align-items: center; gap: 8px">
                          <span>3px</span>
                          <div
                            style="width: 40px; height: 3px; background: #333; border-radius: 1.5px"
                          ></div>
                        </div>
                      </a-select-option>
                      <a-select-option value="4">
                        <div style="display: flex; align-items: center; gap: 8px">
                          <span>4px</span>
                          <div
                            style="width: 40px; height: 4px; background: #333; border-radius: 2px"
                          ></div>
                        </div>
                      </a-select-option>
                      <a-select-option value="5">
                        <div style="display: flex; align-items: center; gap: 8px">
                          <span>5px</span>
                          <div
                            style="width: 40px; height: 5px; background: #333; border-radius: 2.5px"
                          ></div>
                        </div>
                      </a-select-option>
                    </a-select>
                  </a-form-item>
                  <a-form-item
                    label="间隔"
                    name="depthInterval"
                    :rules="[{ required: true, message: '请输入' }]"
                  >
                    <a-input-number
                      v-model:value="channelsForm.depthInterval"
                      :min="1"
                      :max="10"
                      addon-after="m"
                      style="width: 100%"
                    />
                  </a-form-item>
                  <a-form-item label="粗线" :rules="[{ required: true }]">
                    <a-select
                      placeholder="请选择"
                      style="width: 100%"
                      v-model:value="channelsForm.depthThickLine"
                    >
                      <a-select-option value="1">
                        <div style="display: flex; align-items: center; gap: 8px">
                          <span>1px</span>
                          <div
                            style="width: 40px; height: 1px; background: #333; border-radius: 0.5px"
                          ></div>
                        </div>
                      </a-select-option>
                      <a-select-option value="2">
                        <div style="display: flex; align-items: center; gap: 8px">
                          <span>2px</span>
                          <div
                            style="width: 40px; height: 2px; background: #333; border-radius: 1px"
                          ></div>
                        </div>
                      </a-select-option>
                      <a-select-option value="3">
                        <div style="display: flex; align-items: center; gap: 8px">
                          <span>3px</span>
                          <div
                            style="width: 40px; height: 3px; background: #333; border-radius: 1.5px"
                          ></div>
                        </div>
                      </a-select-option>
                      <a-select-option value="4">
                        <div style="display: flex; align-items: center; gap: 8px">
                          <span>4px</span>
                          <div
                            style="width: 40px; height: 4px; background: #333; border-radius: 2px"
                          ></div>
                        </div>
                      </a-select-option>
                      <a-select-option value="5">
                        <div style="display: flex; align-items: center; gap: 8px">
                          <span>5px</span>
                          <div
                            style="width: 40px; height: 5px; background: #333; border-radius: 2.5px"
                          ></div>
                        </div>
                      </a-select-option>
                    </a-select>
                  </a-form-item>
                  <a-form-item label="间隔" :rules="[{ required: true, message: '请输入' }]">
                    <a-input-number
                      v-model:value="channelsForm.depthThickInterval"
                      :min="1"
                      :max="10"
                      addon-after="m"
                      style="width: 100%"
                    />
                  </a-form-item>
                </div>
              </div>
              <div style="margin-top: auto; text-align: right; padding-top: 16px">
                <a-button @click="handleFeature1ModalCancel" style="margin-right: 8px">
                  取消
                </a-button>
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
        <!-- 横向锚点导航 -->
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

        <!-- 内容区域 -->
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
                  >
                    <a-select
                      v-model:value="indicatorsForm2[tag].lineStyle"
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
                  >
                    <div style="display: flex; align-items: center; gap: 8px">
                      <a-input-number
                        v-model:value="indicatorsForm2[tag].range![0]"
                        :placeholder="`最小值`"
                        style="flex: 1"
                      />
                      <span style="color: #666; font-size: 14px; white-space: nowrap">-</span>
                      <a-input-number
                        v-model:value="indicatorsForm2[tag].range![1]"
                        :placeholder="`最大值`"
                        style="flex: 1"
                      />
                    </div>
                  </a-form-item>
                </template>
              </div>
              <div style="margin-top: auto; text-align: right; padding-top: 16px">
                <a-button @click="handleFeature2ModalCancel" style="margin-right: 8px">
                  取消
                </a-button>
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
                  >
                    <a-select
                      v-model:value="channelsForm2.logarithmicScale"
                      placeholder="请选择"
                      style="width: 100%"
                    >
                      <a-select-option value="true">是 </a-select-option>
                      <a-select-option value="false">否 </a-select-option>
                    </a-select>
                  </a-form-item>
                </div>
                <a-form-item style="width: 100%; margin-top: 20px">
                  <a-checkbox v-model:checked="channelsForm2.showScaleLines">显示刻度线</a-checkbox>
                </a-form-item>
                <div class="channels-form-grid">
                  <a-form-item label="细线" name="thinLine" :rules="[{ required: true }]">
                    <a-select
                      v-model:value="channelsForm2.thinLine"
                      placeholder="请选择"
                      style="width: 100%"
                    >
                      <a-select-option value="1">
                        <div style="display: flex; align-items: center; gap: 8px">
                          <span>1px</span>
                          <div
                            style="width: 40px; height: 1px; background: #333; border-radius: 0.5px"
                          ></div>
                        </div>
                      </a-select-option>
                      <a-select-option value="2">
                        <div style="display: flex; align-items: center; gap: 8px">
                          <span>2px</span>
                          <div
                            style="width: 40px; height: 2px; background: #333; border-radius: 1px"
                          ></div>
                        </div>
                      </a-select-option>
                      <a-select-option value="3">
                        <div style="display: flex; align-items: center; gap: 8px">
                          <span>3px</span>
                          <div
                            style="width: 40px; height: 3px; background: #333; border-radius: 1.5px"
                          ></div>
                        </div>
                      </a-select-option>
                      <a-select-option value="4">
                        <div style="display: flex; align-items: center; gap: 8px">
                          <span>4px</span>
                          <div
                            style="width: 40px; height: 4px; background: #333; border-radius: 2px"
                          ></div>
                        </div>
                      </a-select-option>
                      <a-select-option value="5">
                        <div style="display: flex; align-items: center; gap: 8px">
                          <span>5px</span>
                          <div
                            style="width: 40px; height: 5px; background: #333; border-radius: 2.5px"
                          ></div>
                        </div>
                      </a-select-option>
                    </a-select>
                  </a-form-item>
                  <a-form-item
                    label="份数"
                    name="thinLineCount"
                    :rules="[{ required: true, message: '请输入' }]"
                  >
                    <a-input-number
                      v-model:value="channelsForm2.thinLineCount"
                      :min="1"
                      :max="10"
                      style="width: 100%"
                    />
                  </a-form-item>
                  <a-form-item label="粗线" name="thickLine" :rules="[{ required: true }]">
                    <a-select
                      v-model:value="channelsForm2.thickLine"
                      placeholder="请选择"
                      style="width: 100%"
                    >
                      <a-select-option value="1">
                        <div style="display: flex; align-items: center; gap: 8px">
                          <span>1px</span>
                          <div
                            style="width: 40px; height: 1px; background: #333; border-radius: 0.5px"
                          ></div>
                        </div>
                      </a-select-option>
                      <a-select-option value="2">
                        <div style="display: flex; align-items: center; gap: 8px">
                          <span>2px</span>
                          <div
                            style="width: 40px; height: 2px; background: #333; border-radius: 1px"
                          ></div>
                        </div>
                      </a-select-option>
                      <a-select-option value="3">
                        <div style="display: flex; align-items: center; gap: 8px">
                          <span>3px</span>
                          <div
                            style="width: 40px; height: 3px; background: #333; border-radius: 1.5px"
                          ></div>
                        </div>
                      </a-select-option>
                      <a-select-option value="4">
                        <div style="display: flex; align-items: center; gap: 8px">
                          <span>4px</span>
                          <div
                            style="width: 40px; height: 4px; background: #333; border-radius: 2px"
                          ></div>
                        </div>
                      </a-select-option>
                      <a-select-option value="5">
                        <div style="display: flex; align-items: center; gap: 8px">
                          <span>5px</span>
                          <div
                            style="width: 40px; height: 5px; background: #333; border-radius: 2.5px"
                          ></div>
                        </div>
                      </a-select-option>
                    </a-select>
                  </a-form-item>
                  <a-form-item
                    label="份数"
                    name="thickLineCount"
                    :rules="[{ required: true, message: '请输入' }]"
                  >
                    <a-input-number
                      v-model:value="channelsForm2.thickLineCount"
                      :min="1"
                      :max="10"
                      style="width: 100%"
                    />
                  </a-form-item>
                </div>
                <a-form-item style="width: 100%; margin-top: 10px">
                  <a-checkbox v-model:checked="channelsForm2.showDepthLines">显示深度线</a-checkbox>
                </a-form-item>
                <div class="channels-form-grid">
                  <a-form-item label="细线" name="depthThinLine" :rules="[{ required: true }]">
                    <a-select
                      placeholder="请选择"
                      style="width: 100%"
                      v-model:value="channelsForm2.depthThinLine"
                    >
                      <a-select-option value="1">
                        <div style="display: flex; align-items: center; gap: 8px">
                          <span>1px</span>
                          <div
                            style="width: 40px; height: 1px; background: #333; border-radius: 0.5px"
                          ></div>
                        </div>
                      </a-select-option>
                      <a-select-option value="2">
                        <div style="display: flex; align-items: center; gap: 8px">
                          <span>2px</span>
                          <div
                            style="width: 40px; height: 2px; background: #333; border-radius: 1px"
                          ></div>
                        </div>
                      </a-select-option>
                      <a-select-option value="3">
                        <div style="display: flex; align-items: center; gap: 8px">
                          <span>3px</span>
                          <div
                            style="width: 40px; height: 3px; background: #333; border-radius: 1.5px"
                          ></div>
                        </div>
                      </a-select-option>
                      <a-select-option value="4">
                        <div style="display: flex; align-items: center; gap: 8px">
                          <span>4px</span>
                          <div
                            style="width: 40px; height: 4px; background: #333; border-radius: 2px"
                          ></div>
                        </div>
                      </a-select-option>
                      <a-select-option value="5">
                        <div style="display: flex; align-items: center; gap: 8px">
                          <span>5px</span>
                          <div
                            style="width: 40px; height: 5px; background: #333; border-radius: 2.5px"
                          ></div>
                        </div>
                      </a-select-option>
                    </a-select>
                  </a-form-item>
                  <a-form-item
                    label="间隔"
                    name="depthInterval"
                    :rules="[{ required: true, message: '请输入' }]"
                  >
                    <a-input-number
                      v-model:value="channelsForm2.depthInterval"
                      :min="1"
                      :max="10"
                      addon-after="m"
                      style="width: 100%"
                    />
                  </a-form-item>
                  <a-form-item label="粗线" :rules="[{ required: true }]">
                    <a-select
                      placeholder="请选择"
                      style="width: 100%"
                      v-model:value="channelsForm2.depthThickLine"
                    >
                      <a-select-option value="1">
                        <div style="display: flex; align-items: center; gap: 8px">
                          <span>1px</span>
                          <div
                            style="width: 40px; height: 1px; background: #333; border-radius: 0.5px"
                          ></div>
                        </div>
                      </a-select-option>
                      <a-select-option value="2">
                        <div style="display: flex; align-items: center; gap: 8px">
                          <span>2px</span>
                          <div
                            style="width: 40px; height: 2px; background: #333; border-radius: 1px"
                          ></div>
                        </div>
                      </a-select-option>
                      <a-select-option value="3">
                        <div style="display: flex; align-items: center; gap: 8px">
                          <span>3px</span>
                          <div
                            style="width: 40px; height: 3px; background: #333; border-radius: 1.5px"
                          ></div>
                        </div>
                      </a-select-option>
                      <a-select-option value="4">
                        <div style="display: flex; align-items: center; gap: 8px">
                          <span>4px</span>
                          <div
                            style="width: 40px; height: 4px; background: #333; border-radius: 2px"
                          ></div>
                        </div>
                      </a-select-option>
                      <a-select-option value="5">
                        <div style="display: flex; align-items: center; gap: 8px">
                          <span>5px</span>
                          <div
                            style="width: 40px; height: 5px; background: #333; border-radius: 2.5px"
                          ></div>
                        </div>
                      </a-select-option>
                    </a-select>
                  </a-form-item>
                  <a-form-item label="间隔" :rules="[{ required: true, message: '请输入' }]">
                    <a-input-number
                      v-model:value="channelsForm2.depthThickInterval"
                      :min="1"
                      :max="10"
                      addon-after="m"
                      style="width: 100%"
                    />
                  </a-form-item>
                </div>
              </div>
              <div style="margin-top: auto; text-align: right; padding-top: 16px">
                <a-button @click="handleFeature2ModalCancel" style="margin-right: 8px">
                  取消
                </a-button>
                <a-button type="primary" @click="handleFeature2ModalOk"> 确定 </a-button>
              </div>
            </a-form>
          </div>
        </div>
      </div>
    </a-modal>
  </div>
</template>
