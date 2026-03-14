<template>
  <div class="preview-panel">
    <div class="preview-header" v-if="props.showAllData">
      <span class="preview-title">
        {{ props.showAllData ? '数据展示' : props.selectedFile || '数据展示' }}
      </span>
    </div>
    <div v-if="props.showAllData" class="all-data-grid-wrap">
      <div v-if="props.loading" class="loading-wrap">
        <span class="loading-spinner"></span>
        <span style="margin-left: 12px">数据加载中...</span>
      </div>
      <template v-else>
        <div class="all-data-grid">
          <div class="files-header">
            <span class="files-title">全部数据</span>
            <div class="files-divider"></div>
          </div>
          <template v-for="item in flatTree(props.treeData).folders" :key="item.id">
            <DataGridItem :item="item" @rename="handleRename" @delete="handleDelete" />
          </template>
          <div v-if="flatTree(props.treeData).files.length" class="files-header">
            <span class="files-title">最近文件</span>
            <div class="files-divider"></div>
          </div>
          <template v-for="item in flatTree(props.treeData).files" :key="item.id">
            <DataGridItem :item="item" @rename="handleRename" @delete="handleDelete" />
          </template>
        </div>
      </template>
    </div>
    <template v-else>
      <div class="file-preview-card">
        <div class="preview-title">
          <span>{{ props.selectedFile }}</span>
          <span class="preview-title-actions">
            <a-button class="preview-btn" size="small">取消</a-button>
            <a-button
              class="preview-btn confirm"
              type="primary"
              size="small"
              style="margin-left: 12px"
              @click="handleConfirm"
              >确认</a-button
            >
          </span>
        </div>
        <template v-if="props.selectedFile">
          <div class="table-wrap">
            <a-table
              :columns="columns"
              :data-source="dataSource"
              :pagination="pagination"
              :scroll="{ x: 'max-content' }"
              bordered
              :locale="zhCN"
            />
          </div>
        </template>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, defineProps, watch } from 'vue'
import DataGridItem from './DataGridItem.vue'
import { message } from 'ant-design-vue'
import zhCN from 'ant-design-vue/es/locale/zh_CN'
import { getDataSource } from '@/utils/api'
const emit = defineEmits(['rename', 'delete'])

const props = defineProps<{
  showAllData: boolean
  loading: boolean
  treeData: unknown[]
  selectedFile: string
  selectedId: number
}>()

const columns = ref<{ title: string; dataIndex: string; key: string }[]>([])
const dataSource = ref<any[]>([])

const pagination = ref({
  current: 1,
  pageSize: 20,
  total: 0,
  showTotal: (total: number) => `共 ${Math.ceil(total / pagination.value.pageSize)} 页`,
  showQuickJumper: true,
  showSizeChanger: true,
  pageSizeOptions: ['10', '20', '50', '100'],
  onShowSizeChange: (current: number, size: number) => {
    pagination.value.pageSize = size
    pagination.value.current = 1
    fetchData(props.selectedId, props.selectedFile, 1, size)
  },
  onChange: (page: number, pageSize: number) => {
    pagination.value.current = page
    pagination.value.pageSize = pageSize
    fetchData(props.selectedId, props.selectedFile, page, pageSize)
  },
})

// const customLocale = {
//   ...zhCN,
//   Pagination: {
//     ...zhCN.Pagination,
//     items_per_page: '页',
//   },
// }

watch(
  () => props.selectedFile,
  (newVal) => {
    console.log('newVal????????????:', newVal)
    if (newVal) {
      pagination.value.current = 1
      fetchData(props.selectedId, newVal, 1, pagination.value.pageSize)
    }
  },
  { immediate: true },
)

async function fetchData(selectedId: number, selectedFile: string, pageNum = 1, pageSize = 20) {
  try {
    const res = await getDataSource({ id: selectedId, name: selectedFile, pageNum, pageSize })
    if (res?.code) {
      console.log('res????????????:', res.data)
      columns.value = res.data.columns
      dataSource.value = res.data.dataSource
      pagination.value.total = res.data.totalCount
    }
    console.log('dataSource????????????:', dataSource.value)
    console.log('columns????????????:', columns.value)
  } catch (err) {
    console.error('请求失败', err)
  }
}

// grid分组，先文件夹后文件
function flatTree(tree: unknown[]): {
  folders: { id: string; title: string; icon: string; type: string }[]
  files: { id: string; title: string; icon: string; type: string }[]
} {
  const folders: { id: string; title: string; icon: string; type: string }[] = []
  const files: { id: string; title: string; icon: string; type: string }[] = []

  const queue: any[] = [...tree] // 用于广度优先遍历

  while (queue.length > 0) {
    const node = queue.shift()

    if (node.children && Array.isArray(node.children)) {
      folders.push({
        id: node.id,
        title: node.title,
        icon: new URL('@/assets/file/frame.svg', import.meta.url).href,
        type: node.type,
      })
      // 把子节点加入队列，等待后续遍历
      queue.push(...node.children)
    } else if (/\.xlsx?$/.test(node.title)) {
      files.push({
        id: node.id,
        title: node.title,
        icon: new URL('@/assets/file/excel.svg', import.meta.url).href,
        type: node.type,
      })
    } else if (/\.(txt|las)$/i.test(node.title)) {
      files.push({
        id: node.id,
        title: node.title,
        icon: new URL('@/assets/file/txt.svg', import.meta.url).href,
        type: node.type,
      })
    }
  }

  return { folders, files }
}

// mock数据
// const mockTableColumns = [
//   { title: '模型名称', dataIndex: 'model_name', key: 'model_name' },
//   { title: '模型版本权重', dataIndex: 'model_version_weight', key: 'model_version_weight' },
//   { title: 'Loss值', dataIndex: 'loss', key: 'loss' },
//   { title: 'targetname', dataIndex: 'targetname', key: 'targetname' },
//   { title: 'model_name', dataIndex: 'model_name2', key: 'model_name2' },
// ]
// const mockTableData = Array.from({ length: 200 }).map((_, i) => ({
//   key: i,
//   model_name: `模型${i + 1}`,
//   model_version_weight: (Math.random() * 2 + 0.5).toFixed(3),
//   loss: (Math.random() * 0.5 + 0.1).toFixed(4),
//   targetname: `target_${(i % 5) + 1}`,
//   model_name2: `model_${(i % 3) + 1}`,
// }))

function handleConfirm() {
  message.success('已确认')
}

function handleRename(key: string, newTitle: string, type: string) {
  console.log('preview:', key, newTitle, type)
  emit('rename', key, newTitle, type)
}

function handleDelete(key: string, type: string) {
  emit('delete', key, type)
}
</script>

<style scoped>
.preview-panel {
  flex: 1;
  padding: 32px 40px;
  background: #f0f2f5;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  overflow: auto;
}
.preview-header {
  width: 100%;
  margin-bottom: 24px;
}
.preview-title {
  font-size: 14px;
  font-weight: 700;
  color: #161b25;
}
.all-data-grid-wrap {
  width: 100%;
  flex: 1;
  display: flex;
  flex-direction: column;
}
.all-data-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, 180px);
  gap: 32px 24px;
  width: 100%;
}
.all-data-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  width: 160px;
  height: 160px;
  box-sizing: border-box;
  padding: 17px 29px;
  background: transparent;
  transition:
    background 0.2s,
    box-shadow 0.2s;
  border-radius: 8px;
}
.all-data-item:hover {
  background: #fff;
  box-shadow: 0px 8px 24px 0px #4545501a;
}
.all-data-icon {
  width: 100%;
  height: auto;
  max-height: 90px;
  object-fit: contain;
  margin-bottom: 12px;
}
.all-data-label {
  font-family: 'Source Han Sans CN', 'Microsoft YaHei', Arial, sans-serif;
  font-weight: 700;
  font-size: 16px;
  line-height: 100%;
  letter-spacing: 0%;
  text-align: center;
  color: #000;
  border-radius: 6px;
  padding: 8px 0;
  width: 100%;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.file-preview {
  color: #3f9bfd;
  font-size: 20px;
  font-weight: bold;
  background: #1a2233;
  border-radius: 8px;
  padding: 32px 48px;
  min-width: 320px;
  min-height: 120px;
  box-shadow: 0 2px 8px 0 #0000000a;
}
.file-preview-placeholder {
  color: #7a869a;
  font-size: 16px;
  padding: 32px 48px;
}
.loading-wrap {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  min-height: 120px;
  font-size: 16px;
  color: #7a869a;
}
.loading-spinner {
  width: 24px;
  height: 24px;
  border: 3px solid #c3cdd9;
  border-top: 3px solid #3f9bfd;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  display: inline-block;
}
@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
.all-data-divider {
  grid-column: 1/-1;
  height: 1px;
  background: #c3cdd9;
  margin: 8px 0 16px 0;
  border-radius: 0.5px;
}
.item-menu-trigger {
  position: absolute;
  top: 8px;
  right: 8px;
  cursor: pointer;
  z-index: 2;
  opacity: 0;
  transition: opacity 0.2s;
}
.all-data-item:hover .item-menu-trigger {
  opacity: 1;
}
.item-popover {
  position: absolute;
  left: -160px;
  top: 0;
  min-width: 120px;
  background: #fff;
  box-shadow: 0 4px 16px 0 #232b3a22;
  border-radius: 8px;
  padding: 8px 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
  z-index: 10;
}
.popover-option {
  display: flex;
  align-items: center;
  padding: 8px 16px;
  font-size: 15px;
  color: #232b3a;
  cursor: pointer;
  border-radius: 4px;
  transition: background 0.2s;
}
.popover-option:hover {
  background: #f0f2f5;
}
.file-preview-card {
  width: 100%;
  min-width: 320px;
  min-height: 200px;
  border-radius: 2px;
  position: relative;
  /* top: 16px; */
  /* left: 16px; */
  background: #fff;
  box-shadow: 0px 0px 12px 0px #00000040;
  border-bottom-width: 1px;
  display: flex;
  flex-direction: column;
  /* padding: 32px 40px 24px 40px; */
  box-sizing: border-box;
  flex: 1;
  min-height: 0;
}
.file-preview-card .preview-title {
  font-size: 16px;
  font-weight: 700;
  color: #161b25;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-top-left-radius: 2px;
  border-top-right-radius: 2px;
  padding: 12px;
  background: #f5f7fa;
  margin-bottom: 24px;
}
.preview-title-actions {
  display: flex;
  align-items: center;
}
.preview-btn {
  min-width: 56px;
  height: 32px;
  font-size: 14px;
  /* border-radius: 4px; */
  /* font-weight: 500; */
}
.preview-btn.confirm {
  min-width: 80px;
}
.table-wrap {
  flex: 1;
  min-height: 0;
  overflow: auto;
  padding: 0 36px 24px 36px;
}
.files-header {
  grid-column: 1/-1;
  display: flex;
  align-items: center;
  margin: 8px 0 16px 0;
}
.files-title {
  font-size: 14px;
  font-weight: 700;
  color: #161b25;
  margin-right: 16px;
  white-space: nowrap;
}
.files-divider {
  flex: 1;
  height: 1px;
  background: #c3cdd9;
  border-radius: 0.5px;
}
</style>
