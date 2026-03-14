<template>
  <div class="all-data-item" style="position: relative">
    <img :src="item.icon" class="all-data-icon" />
    <div class="all-data-label">
      <template v-if="!isEditing">
        <span>{{ props.item.title }}</span>
      </template>
      <template v-else>
        <input
          :id="'edit-input-' + props.item.id"
          v-model="editValue"
          @blur="finishEdit"
          @keyup.enter="finishEdit"
          class="edit-input"
          :style="'width: 100%; text-align: center; font-weight: normal; color: #232b3a; background: #fff; border: 1px solid #C3CDD9; border-radius: 4px;'"
        />
      </template>
    </div>
    <a-popover
      placement="right"
      trigger="click"
      v-model:open="showPopover"
      overlay-class-name="item-popover"
    >
      <template #content>
        <div class="popover-option" @click="startEdit">
          <svg
            t="1751358829006"
            class="icon"
            viewBox="0 0 1024 1024"
            version="1.1"
            xmlns="http://www.w3.org/2000/svg"
            p-id="1502"
            width="12"
            height="12"
            style="margin-right: 6px"
          >
            <path
              d="M544 768l-384 0C142.336 768 128 753.664 128 736l0-384C128 334.336 142.336 320 160 320l384 0C561.664 320 576 334.336 576 352S561.664 384 544 384L192 384l0 320 352 0C561.664 704 576 718.336 576 736S561.664 768 544 768zM288 512C270.336 512 256 526.336 256 544S270.336 576 288 576l192 0C497.664 576 512 561.664 512 544S497.664 512 480 512L288 512zM800 896 704 896 704 192l96 0C817.664 192 832 177.664 832 160S817.664 128 800 128l-256 0C526.336 128 512 142.336 512 160S526.336 192 544 192L640 192l0 704L544 896C526.336 896 512 910.336 512 928S526.336 960 544 960l256 0c17.664 0 32-14.336 32-32S817.664 896 800 896zM864 320l-64 0C782.336 320 768 334.336 768 352S782.336 384 800 384L832 384l0 320-32 0c-17.664 0-32 14.336-32 32s14.336 32 32 32l64 0c17.664 0 32-14.336 32-32l0-384C896 334.336 881.664 320 864 320z"
              fill="#020202"
              p-id="1503"
            ></path>
          </svg>
          重命名
        </div>
        <div class="popover-option" @click="handleDelete">
          <svg
            t="1751358915034"
            class="icon"
            viewBox="0 0 1024 1024"
            version="1.1"
            xmlns="http://www.w3.org/2000/svg"
            p-id="2629"
            width="12"
            height="12"
            style="margin-right: 6px"
          >
            <path
              d="M729.6 838.4H294.4l-25.6-512h486.4l-25.6 512zM864 256h-704c-19.2 0-32 12.8-32 32V320c0 6.4 6.4 6.4 6.4 6.4H192l25.6 524.8c0 32 32 64 64 64h454.4c32 0 64-25.6 64-64l25.6-524.8h57.6c6.4 0 12.8 0 12.8-6.4v-32c0-19.2-12.8-32-32-32zM358.4 185.6h-6.4c6.4 0 6.4-6.4 6.4-6.4v6.4h307.2v-6.4c0 6.4 6.4 6.4 6.4 6.4h-6.4V256h70.4V179.2c0-38.4-25.6-64-64-64h-320c-38.4 0-64 25.6-64 64V256h70.4V185.6z"
              fill="#020202"
              p-id="2630"
            ></path>
          </svg>
          删除
        </div>
      </template>
      <div class="item-menu-trigger" @click.stop="showPopover = !showPopover">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
          <circle cx="12" cy="5" r="2" fill="#C3CDD9" />
          <circle cx="12" cy="12" r="2" fill="#C3CDD9" />
          <circle cx="12" cy="19" r="2" fill="#C3CDD9" />
        </svg>
      </div>
    </a-popover>
  </div>
</template>
<script setup lang="ts">
import { ref, nextTick } from 'vue'
const props = defineProps<{ item: { id: string; title: string; icon: string; type: string } }>()
const emit = defineEmits(['rename', 'delete'])
const showPopover = ref(false)
const isEditing = ref(false)
const editValue = ref('')

function startEdit() {
  showPopover.value = false
  isEditing.value = true
  editValue.value = props.item.title
  nextTick(() => {
    const input = document.getElementById('edit-input-' + props.item.id) as HTMLInputElement
    if (input) input.focus()
  })
}

let submitting = false
async function finishEdit() {
  // 防止重复触发
  if (submitting) return
  submitting = true

  const trimmed = editValue.value.trim()
  if (trimmed && trimmed !== props.item.title) {
    console.log('trimmed????????????:', props.item, trimmed)
    emit('rename', props.item.id, trimmed, props.item.type)
  }
  isEditing.value = false
  await nextTick()
  submitting = false
}

function handleDelete() {
  showPopover.value = false
  emit('delete', props.item.id, props.item.type)
}
</script>
<style scoped>
.all-data-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  width: 160px;
  height: 160px;
  box-sizing: border-box;
  padding: 16px;
  background: #ffffff;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border-radius: 12px;
  position: relative;
  border: 1px solid #e5e7eb;
  cursor: pointer;
}

.all-data-item:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px -10px rgba(0, 0, 0, 0.15);
  border-color: var(--primary-color, #1890ff); /* Fallback if var not defined */
}

/* Ensure the blue frame effect is prominent on hover as requested */
.all-data-item:hover::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border-radius: 12px;
  border: 1px solid var(--primary-color, #1890ff);
  pointer-events: none;
}

.item-menu-trigger {
  position: absolute;
  top: 8px;
  right: 8px;
  cursor: pointer;
  z-index: 2;
  opacity: 0;
  transition: all 0.2s;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(4px);
}

.all-data-item:hover .item-menu-trigger {
  opacity: 1;
}

.item-menu-trigger:hover {
  background: #ffffff;
  color: var(--primary-color, #1890ff);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.item-menu-trigger svg circle {
  fill: currentColor;
}

:deep(.item-popover) {
  min-width: 120px;
  background: #fff;
  box-shadow: 0 4px 16px 0 rgba(35, 43, 58, 0.1);
  border-radius: 8px;
  padding: 8px 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
  z-index: 10;
  border: 1px solid #f0f0f0;
}

.popover-option {
  display: flex;
  align-items: center;
  padding: 8px 16px;
  font-size: 14px;
  color: #232b3a;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.2s;
  margin: 0 4px;
}

.popover-option:hover {
  background: #f5f7fa;
  color: var(--primary-color, #1890ff);
}

.popover-option svg {
  fill: currentColor;
}

.edit-input {
  height: 28px;
  font-size: 14px;
  padding: 0 8px;
  outline: none;
  background: #fff;
  color: #232b3a;
  font-weight: normal;
  border: 1px solid var(--primary-color, #1890ff) !important;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}

.all-data-icon {
  width: 64px;
  height: 64px;
  object-fit: contain;
  margin-bottom: 12px;
  margin-top: 8px;
  transition: transform 0.3s;
}

.all-data-item:hover .all-data-icon {
  transform: scale(1.05);
}

.all-data-label {
  width: 100%;
  text-align: center;
  font-size: 14px;
  color: #333;
  margin-top: auto;
  margin-bottom: 4px;
}

.all-data-label span {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  width: 100%;
}</style>
