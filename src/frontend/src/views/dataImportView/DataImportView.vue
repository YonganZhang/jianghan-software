<template>
  <div class="import-page">
    <div class="tree-panel">
      <a-input
        v-model:value="inputValue"
        placeholder="搜索"
        style="margin-bottom: 8px"
        @pressEnter="onSearch"
      >
        <template #prefix>
          <svg viewBox="0 0 1024 1024" width="18" height="18" style="color: #c3cdd9">
            <path
              d="M832 864a32 32 0 0 1-22.56-9.44l-144.8-144.8A319.36 319.36 0 0 1 512 832C300.32 832 128 659.68 128 448S300.32 64 512 64s384 172.32 384 384a383.36 383.36 0 0 1-73.76 224.64l144.8 144.8A32 32 0 0 1 832 864zM512 128C335.36 128 192 271.36 192 448s143.36 320 320 320 320-143.36 320-320S688.64 128 512 128z"
              fill="#c3cdd9"
            />
          </svg>
        </template>
      </a-input>
      <div class="all-data-btn-wrap">
        <div
          class="all-data-btn"
          :class="{ active: showAllData }"
          @click="selectedFile = ''"
        >
          <span>全部数据</span>
          <a-popover
            placement="right"
            trigger="click"
            v-model:open="addPopoverOpen"
            overlay-class-name="all-data-add-popover"
          >
            <template #content>
              <div class="add-popover-option" @click="onAdd('folder', originParentId)">
                <img :src="frameIcon" width="16" style="margin-right: 8px" />新文件夹
              </div>
              <div class="add-popover-option" @click="onAdd('excel', originParentId)">
                <img :src="excelIcon" width="16" style="margin-right: 8px" />上传Excel
              </div>
              <div class="add-popover-option" @click="onAdd('las', originParentId)">
                <img :src="txtIcon" width="16" style="margin-right: 8px" />上传LAS
              </div>
              <div class="add-popover-option" @click="onAdd('txt', originParentId)">
                <img :src="txtIcon" width="16" style="margin-right: 8px" />上传TXT
              </div>
            </template>
            <span class="all-data-add-btn" @click.stop="onAddPopoverClick()">
              <svg width="18" height="18" viewBox="0 0 1024 1024">
                <path
                  d="M480 480V224a32 32 0 1 1 64 0v256h256a32 32 0 1 1 0 64H544v256a32 32 0 1 1-64 0V544H224a32 32 0 1 1 0-64h256z"
                  fill="currentColor"
                />
              </svg>
            </span>
          </a-popover>
        </div>
      </div>
      <div class="tree-actions">
        <a-button class="convert-all-btn" :loading="converting" @click="onConvertAllToXlsx"
          >一键转换LAS和TXT</a-button
        >
      </div>
      <a-tree
        class="draggable-tree"
        block-node
        :tree-data="filteredTreeData"
        :expanded-keys="expandedKeys"
        :auto-expand-parent="autoExpandParent"
        @expand="onExpand"
        @select="onSelect"
        :field-names="{ title: 'title', key: 'key', children: 'children' }"
      >
        <template #title="{ title, children, id, type, key, readonly }">
          <div class="custom-tree-row">
            <span v-if="children" style="margin-right: 6px; display: inline-flex">
              <img
                src="@/assets/file/frame.svg"
                width="18"
                height="18"
                style="vertical-align: middle"
              />
            </span>
            <span
              v-else-if="/\.xlsx?$/.test(title)"
              style="margin-right: 6px; display: inline-flex"
            >
              <img
                src="@/assets/file/excel.svg"
                width="16"
                height="16"
                style="vertical-align: middle"
              />
            </span>
            <span
              v-else-if="/\.(txt|las)$/i.test(title)"
              style="margin-right: 6px; display: inline-flex"
            >
              <img
                src="@/assets/file/txt.svg"
                width="16"
                height="16"
                style="vertical-align: middle"
              />
            </span>
            <span v-if="editingKey === id">
              <input
                :id="'edit-input-' + String(id)"
                v-model="editingValue"
                @blur="finishEdit"
                @keyup.enter="finishEdit"
                class="edit-input"
                style="
                  width: 120px;
                  border: 1px solid #c3cdd9;
                  border-radius: 4px;
                  padding: 2px 8px;
                "
              />
            </span>
            <span v-else>{{ title }}</span>
            <span class="tree-title-actions">
              <a-popover
                placement="right"
                trigger="click"
                :open="addPopoverRowKey === key"
                @openChange="
                  (val: boolean) => {
                    console.log('addPopoverRowKey:', val, addPopoverRowKey)
                    if (!val) addPopoverRowKey = ''
                  }
                "
                overlay-class-name="all-data-add-popover"
              >
                <template #content>
                  <div class="add-popover-option" @click="onAdd('folder', id)">
                    <img :src="frameIcon" width="16" style="margin-right: 8px" />新文件夹
                  </div>
                  <div class="add-popover-option" @click="onAdd('excel', id)">
                    <img :src="excelIcon" width="16" style="margin-right: 8px" />上传Excel
                  </div>
                  <div class="add-popover-option" @click="onAdd('las', id)">
                    <img :src="txtIcon" width="16" style="margin-right: 8px" />上传LAS
                  </div>
                  <div class="add-popover-option" @click="onAdd('txt', id)">
                    <img :src="txtIcon" width="16" style="margin-right: 8px" />上传TXT
                  </div>
                </template>
                <span v-if="children && !readonly" class="tree-add-btn" @click.stop="onAddPopoverClick(key)">
                  <svg width="16" height="16" viewBox="0 0 1024 1024">
                    <path
                      d="M480 480V224a32 32 0 1 1 64 0v256h256a32 32 0 1 1 0 64H544v256a32 32 0 1 1-64 0V544H224a32 32 0 1 1 0-64h256z"
                      fill="#5A5A68"
                    />
                  </svg>
                </span>
              </a-popover>
              <a-popover
                placement="right"
                trigger="click"
                :open="menuPopoverKey === key"
                @openChange="
                  (val: boolean) => {
                    if (!val) menuPopoverKey = ''
                  }
                "
                overlay-class-name="item-popover"
              >
                <template #content>
                  <div class="popover-option" @click="onRename(id, title, type)">
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
                  <div class="popover-option" @click="onDelete(id, type)">
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
                <span class="tree-menu-btn" @click.stop="onMenuClick(key)">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                    <circle cx="12" cy="5" r="2" fill="#5A5A68" />
                    <circle cx="12" cy="12" r="2" fill="#5A5A68" />
                    <circle cx="12" cy="19" r="2" fill="#5A5A68" />
                  </svg>
                </span>
              </a-popover>
            </span>
          </div>
        </template>
      </a-tree>
    </div>
    <DataPreview
      :show-all-data="showAllData"
      :loading="loading"
      :tree-data="displayTreeData"
      :selected-file="selectedFile"
      :selected-id="selectedId"
      @rename="(id, newTitle, type) => onEdit(Number(id), String(newTitle), String(type))"
      @delete="(id, type) => onDelete(Number(id), type)"
    />
    <input
      ref="fileInputRef"
      type="file"
      style="display: none"
      @change="handleFileChange"
      :accept="
        uploadType === 'excel'
          ? '.xls,.xlsx'
          : uploadType === 'txt'
            ? '.txt'
            : uploadType === 'las'
              ? '.las'
              : ''
      "
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick, defineOptions, onActivated } from 'vue'
import DataPreview from './DataPreview.vue'
import frameIcon from '@/assets/file/frame.svg'
import excelIcon from '@/assets/file/excel.svg'
import txtIcon from '@/assets/file/txt.svg'
import { message } from 'ant-design-vue'
import { addTreeNode, convertAllToXlsx, deleteTreeNode, editTreeNode, getTreeData } from '@/utils/api'
import { findNodeByIdAndType } from '@/utils/tree'

defineOptions({
  name: 'DataImportView'
})


const inputValue = ref('') // 搜索框输入值
const searchValue = ref('') // 搜索值
const expandedKeys = ref<string[]>(['0']) // 展开的节点id
const autoExpandParent = ref(true) // 自动展开匹配结果父节点
const selectedFile = ref('') // 选中的文件
const selectedId = ref(0) // 选中的id
const showAllData = computed(() => !selectedFile.value) // 只要没选文件就显示全部数据
const loading = ref(true)
const showAdd = ref(false)
const addPopoverOpen = ref(false)
const displayTreeData = ref<MyTreeNode[]>([])
const originParentId = ref(0)
const converting = ref(false)

// 编辑中的key和value
const editingKey = ref<number | null>(null)
const editingValue = ref<string>('')
const editingType = ref<string>('')
const isFinishingEdit = ref(false) // 防止 blur+enter 双重调用

// 每行的popover显示状态
const menuPopoverKey = ref('')

// 每行加号popover显示状态
const addPopoverRowKey = ref('')

// 上传弹窗相关
const fileInputRef = ref<HTMLInputElement | null>(null)
const uploadType = ref<'excel' | 'txt' | 'las' | ''>('')
const uploadParentKey = ref<number | null>(null)

function triggerFileInput(type: 'excel' | 'txt' | 'las', parentKey?: number) {
  uploadType.value = type
  uploadParentKey.value = parentKey ?? null
  if (!fileInputRef.value) return
  fileInputRef.value.value = '' // 重置
  fileInputRef.value.accept = type === 'excel' ? '.xls,.xlsx' : type === 'las' ? '.las' : '.txt'
  fileInputRef.value.click()
}

async function handleFileChange(e: Event) {
  const files = (e.target as HTMLInputElement).files
  if (!files || files.length === 0) return
  const file = files[0]
  // 校验类型
  if (uploadType.value === 'excel' && !/\.xlsx?$/.test(file.name)) {
    message.warning('请选择Excel文件')
    return
  }
  if (uploadType.value === 'txt' && !/\.txt$/i.test(file.name)) {
    message.warning('请选择TXT文件')
    return
  }
  if (uploadType.value === 'las' && !/\.las$/i.test(file.name)) {
    message.warning('请选择LAS文件')
    return
  }
  // 调用后端上传接口

  // const res = await addTreeNode(file, uploadParentKey.value ?? 0)
  const res = await addTreeNode({
    type: 'file',
    name: file.name,
    parent_id: uploadParentKey.value || 0,
    file: file,
  })
  if (res?.code === '00000') {
    message.success('上传成功')
    // 刷新树
    const treeRes = await getTreeData()
    const d = treeRes.data?.[0]?.children ?? []
    treeData.value = patchTreeKeys(d)
    displayTreeData.value = [...treeData.value]
    const parentId = uploadParentKey.value ?? 0
    const parentNode = parentId ? findNodeByIdAndType(treeData.value, parentId, 'directory') : null
    if (parentNode?.key) {
      const nextExpanded = new Set(expandedKeys.value)
      nextExpanded.add(parentNode.key)
      expandedKeys.value = Array.from(nextExpanded)
      autoExpandParent.value = true
    }
    // 自动选中新上传的文件，触发右侧预览加载
    const newFileId = res.key
    if (newFileId) {
      const uploadedNode = findNodeById(treeData.value, newFileId)
      if (uploadedNode) {
        selectedFile.value = uploadedNode.title
        selectedId.value = uploadedNode.id
      }
    }
  } else {
    message.error(res.data?.message || '上传失败')
  }
}

async function onConvertAllToXlsx() {
  if (converting.value) return
  converting.value = true
  try {
    const res = await convertAllToXlsx()
    if (res?.code === '00000') {
      const converted = Number(res.data?.converted ?? 0)
      const skipped = Number(res.data?.skipped ?? 0)
      message.success(`转换完成：${converted} 个；跳过：${skipped} 个`)
      const treeRes = await getTreeData()
      const d = treeRes.data?.[0]?.children ?? []
      treeData.value = patchTreeKeys(d)
      displayTreeData.value = [...treeData.value]
    } else {
      message.error(res?.message || '转换失败')
    }
  } catch {
    message.error('转换请求失败')
  } finally {
    converting.value = false
  }
}

type MyTreeNode = {
  title: string
  id: number
  type: string
  children?: MyTreeNode[]
  key?: string
  readonly?: boolean
}

const treeData = ref<MyTreeNode[]>([])

function findNodeById(nodes: MyTreeNode[], targetId: number): MyTreeNode | null {
  for (const node of nodes) {
    if (node.id === targetId && !node.children) return node
    if (node.children) {
      const found = findNodeById(node.children, targetId)
      if (found) return found
    }
  }
  return null
}

function patchTreeKeys(nodes: MyTreeNode[], parentPath: string = '', isReadonly: boolean = false): any[] {
  return nodes.map((node) => {
    const currentKey = parentPath ? `${parentPath}-${node.id}` : `${node.id}`
    const currentReadonly = isReadonly || (node.type === 'directory' && node.title === '预处理数据')
    const patchedNode = {
      ...node,
      key: currentKey,
      readonly: currentReadonly,
    }
    if (node.children) {
      patchedNode.children = patchTreeKeys(node.children, currentKey, currentReadonly)
    }
    return patchedNode
  })
}


onActivated(async () => {
  console.log('onActivated激活')
  loading.value = true
  try {
    // mock
    // const res = await mockApi.getTree()
    // 真实后端
    const res = await getTreeData()
    if (res.data) {
      originParentId.value = res.data[0].id
      const rawData = res.data?.[0]?.children ?? []
      treeData.value = patchTreeKeys(rawData)
      console.log('patchTreeKeys:', treeData.value)
      displayTreeData.value = treeData.value
    }
    console.log('treedata:', res.data[0].children, treeData.value)
  } finally {
    loading.value = false
  }
})

const filteredTreeData = computed((): MyTreeNode[] => {
  if (!searchValue.value) {
    return Array.isArray(treeData.value) ? treeData.value : []
  }
  // 递归过滤树，保留所有匹配节点及其祖先和子孙
  function filterTree(nodes: MyTreeNode[], keyword: string): MyTreeNode[] {
    const res: MyTreeNode[] = []
    for (const node of nodes) {
      const matched = node.title.includes(keyword)
      let filteredChildren: MyTreeNode[] = []
      if (node.children) {
        filteredChildren = filterTree(node.children, keyword)
      }
      if (matched || (filteredChildren && filteredChildren.length > 0)) {
        // 只要原始有 children 字段就保留（哪怕过滤后为空数组）
        res.push({
          ...node,
          children: node.children ? filteredChildren : undefined,
        })
      }
    }
    return res
  }
  // 收集所有匹配节点的祖先 key
  function collectAncestorKeys(
    nodes: MyTreeNode[],
    keyword: string,
    parentKeys: string[] = [],
    result: Set<string> = new Set()
  ) {
    for (const node of nodes) {
      const matched = node.title.includes(keyword)
      if (matched) {
        parentKeys.forEach((k) => result.add(k))
      }
      if (node.children) {
        const nextParentKeys =
          node.type === 'directory' && node.key ? [...parentKeys, node.key] : parentKeys
        collectAncestorKeys(node.children, keyword, nextParentKeys, result)
      }
    }
    return result
  }
  const filtered = filterTree(
    Array.isArray(treeData.value) ? treeData.value : [],
    searchValue.value
  )
  const ancestorKeys = Array.from(collectAncestorKeys(filtered, searchValue.value))
  expandedKeys.value = ancestorKeys
  return filtered
})

function onExpand(ids: string[]) {
  console.log('ids:', ids)
  expandedKeys.value = ids
  autoExpandParent.value = false
}
function onSelect(ids: number[], e: { node: MyTreeNode }) {
  if (!e.node) return
  // 判断是否为文件（无 children）
  if (!e.node.children) {
    selectedFile.value = e.node.title
    selectedId.value = e.node.id
    // TODO: 这里预留后端加载文件内容的接口调用
    // 例如 await fetchFileData(e.node.id)
  }
  // 如果是文件夹，不做任何处理，保持当前 DataPreview 内容
}

function onSearch() {
  searchValue.value = inputValue.value.trim()
  console.log('搜索关键字:', searchValue.value)
  const getParentKey = (key: string | undefined, tree: MyTreeNode[]): string | undefined => {
    let parentKey
    for (let i = 0; i < tree.length; i++) {
      const node = tree[i]
      if (node.children) {
        if (node.children.some((item) => item.key === key)) {
          parentKey = node.key
        } else if (getParentKey(key, node.children)) {
          parentKey = getParentKey(key, node.children)
        }
      }
    }
    return parentKey
  }
  const expanded = treeData.value
    .map((item) => {
      if (item.title.includes(searchValue.value)) {
        return getParentKey(item.key, treeData.value)
      }
      return null
    })
    .filter((item, i, self) => item && self.indexOf(item) === i)
  console.log('exex:', expanded)
  expandedKeys.value = expanded
  // autoExpandParent.value = true
}

// function onSearch() {
//   if (!searchValue.value) {
//     expandedKeys.value = []
//     return
//   }
//   // 递归搜集所有包含关键字的节点和父节点
//   const expanded: string[] = []
//   const collect = (nodes: MyTreeNode[], parentKey?: string): boolean => {
//     let matchedInChildren = false
//     for (const node of nodes) {
//       let matched = node.title.includes(searchValue.value)
//       if (node.children) {
//         const childMatched = collect(node.children, node.key)
//         if (childMatched) expanded.push(node.key)
//         matched = matched || childMatched
//       }
//       if (matched && parentKey) {
//         expanded.push(parentKey)
//       }
//       matchedInChildren = matchedInChildren || matched
//     }
//     return matchedInChildren
//   }
//   collect(treeData.value)
//   expandedKeys.value = Array.from(new Set(expanded))
// }

async function onAdd(type: 'folder' | 'excel' | 'txt' | 'las', parentId: number = 0) {
  addPopoverOpen.value = false
  addPopoverRowKey.value = ''

  if (type === 'folder') {
    // 新建文件夹逻辑
    // const newNode: MyTreeNode = {
    //   title: '新建文件夹',
    //   id: Date.now(),
    //   type: 'directory',
    //   children: [],
    // }
    const insertNode = (
      nodes: MyTreeNode[],
      parentId: number,
      nodeToInsert: MyTreeNode
    ): boolean => {
      for (const node of nodes) {
        if (node.id === parentId) {
          if (!node.children) node.children = []
          node.children.unshift(nodeToInsert)
          const parentNode = findNodeByIdAndType(treeData.value, parentId, 'directory')
          expandedKeys.value.push(parentNode?.key)
          return true
        } else if (node.children) {
          if (insertNode(node.children, parentId, nodeToInsert)) return true
        }
      }
      return false
    }
    // 调用后端接口
    const res = await addTreeNode({
      type: 'directory',
      name: '新建文件夹',
      parent_id: parentId || 0,
    })
    if (res?.code === '00000') {
      // 创建新的节点对象
      const newNode: MyTreeNode = {
        title: '新建文件夹',
        id: res.data,
        type: 'directory',
        children: [],
      }
      if (parentId === originParentId.value) {
        // 添加到最外层，使用patchTreeKeys给newNode赋予key值
        const newNodeWithKey = patchTreeKeys([newNode])[0]
        treeData.value.unshift(newNodeWithKey)
      } else {
        // 需要获取父节点类型
        let parentType = 'directory' // 默认类型，可根据实际情况调整
        // 尝试在 treeData 中查找父节点类型
        const parentNodeForType = (treeData.value as MyTreeNode[]).find((n) => n.id === parentId)
        if (parentNodeForType) {
          parentType = parentNodeForType.type
        }
        const parentNode = findNodeByIdAndType(treeData.value, parentId, parentType)
        if (parentNode) {
          const parentKey = parentNode.key || `${parentId}`
          const newNodeWithKey = {
            ...newNode,
            key: `${parentKey}-${newNode.id}`,
          }
          insertNode(treeData.value, parentId, newNodeWithKey)
        } else {
          // 如果找不到父节点，使用默认key
          const newNodeWithKey = {
            ...newNode,
            key: `${newNode.id}`,
          }
          insertNode(treeData.value, parentId, newNodeWithKey)
        }
      }
      // 同步 displayTreeData，确保右侧"全部数据"面板刷新
      displayTreeData.value = [...treeData.value]
      editingKey.value = res.data
      editingValue.value = String(newNode.title)
      editingType.value = newNode.type
      nextTick(() => {
        const input = document.getElementById('edit-input-' + String(res.data)) as HTMLInputElement
        if (input) input.focus()
      })
    } else {
      message.error(res.data.message || '添加失败')
    }
  } else if (type === 'excel' || type === 'txt' || type === 'las') {
    triggerFileInput(type, parentId)
  } else {
    message.warning('类型选择不正确！')
  }
}

function onMenuClick(id: string) {
  menuPopoverKey.value = menuPopoverKey.value === id ? '' : id
}
function onRename(id: string, title: string, type: string) {
  menuPopoverKey.value = ''
  editingKey.value = Number(id)
  editingValue.value = String(title)
  editingType.value = String(type)
  nextTick(() => {
    const input = document.getElementById('edit-input-' + String(id)) as HTMLInputElement
    if (input) input.focus()
  })
}

async function onDelete(targetId: number, targetType: string) {
  console.log('targetId????????????:', targetId, targetType)
  const deleteNode = (nodes: MyTreeNode[]): boolean => {
    const index = nodes.findIndex((n) => n.id === targetId && n.type === targetType)
    if (index !== -1) {
      nodes.splice(index, 1)
      return true
    }
    for (const node of nodes) {
      if (node.children && deleteNode(node.children)) return true
    }
    return false
  }

  // try {
  //   const res = await mockApi.deleteTreeNode({ key: targetKey, type: targetType })
  //   if (res.data.code === 0) {
  //     const newTree = JSON.parse(JSON.stringify(treeData.value))
  //     deleteNode(newTree)
  //     treeData.value = newTree
  //     message.success('删除成功')
  //   } else {
  //     message.error(res.data.message || '删除失败')
  //   }
  // } catch {
  //   message.error('删除请求失败')
  // }
  let type: string
  if (targetType == 'txt' || targetType == 'xlsx' || targetType == 'las') {
    type = 'file'
  } else {
    type = 'directory'
  }
  const res = await deleteTreeNode({ id: targetId, type: type })
  console.log('res111????????????:', res)
  if (res?.code === '00000') {
    console.log('res????????????:', res)
    // 删除成功后，重新拉取后端树数据，保证和后端一致
    const treeRes = await getTreeData()
    const rawData = treeRes.data?.[0]?.children ?? []
    treeData.value = patchTreeKeys(rawData)
    displayTreeData.value = treeData.value
    message.success('删除成功')
  } else {
    message.error('删除失败')
  }
}

async function finishEdit() {
  // 防止 blur + enter 双重调用
  if (isFinishingEdit.value) return
  if (editingKey.value !== null && editingValue.value?.trim()) {
    isFinishingEdit.value = true
    const currentId = editingKey.value
    const currentName = editingValue.value.trim()
    const currentType = editingType.value
    try {
      // 将文件原始类型转换为后端期望的 'file' / 'directory'
      let apiType = currentType
      if (apiType === 'txt' || apiType === 'xlsx' || apiType === 'las') {
        apiType = 'file'
      }
      const res = await editTreeNode({
        id: currentId,
        name: currentName,
        type: apiType,
      })

      if (res?.code === '00000') {
        const newTree = JSON.parse(JSON.stringify(treeData.value))
        const update = (nodes: MyTreeNode[]) => {
          for (const node of nodes) {
            // 同时匹配 id 和 type，避免目录/文件 ID 重叠导致误改
            if (node.id === currentId && node.type === currentType) {
              node.title = currentName
              return true
            }
            if (node.children && update(node.children)) return true
          }
          return false
        }
        update(newTree)
        treeData.value = newTree
        displayTreeData.value = [...treeData.value]
        message.success('重命名成功')
      } else {
        message.error('重命名失败')
      }
    } catch {
      message.error('重命名请求失败')
    } finally {
      isFinishingEdit.value = false
    }
  }
  editingKey.value = null
  editingValue.value = ''
}

async function onEdit(id: number, newTitle: string, type: string) {
  let filetype: string
  if (type == 'txt' || type == 'xlsx' || type == 'las') {
    filetype = 'file'
  } else {
    filetype = 'directory'
  }
  const titleStr = String(newTitle)
  if (!id || !titleStr.trim()) return
  try {
    const res = await editTreeNode({
      id: id,
      name: newTitle.trim(),
      type: filetype,
    })

    if (res?.code === '00000') {
      const newTree = JSON.parse(JSON.stringify(treeData.value))
      const update = (nodes: MyTreeNode[]) => {
        for (const node of nodes) {
          // 同时匹配 id 和 type，避免目录/文件 ID 重叠导致误改
          if (node.id === id && node.type === type) {
            node.title = titleStr.trim()
            return true
          }
          if (node.children && update(node.children)) return true
        }
        return false
      }
      update(newTree)
      treeData.value = newTree
      displayTreeData.value = [...treeData.value]
      message.success('重命名成功')
    } else {
      message.error('重命名失败')
    }
  } catch {
    message.error('重命名请求失败')
  }
}

function onAddPopoverClick(rowKey?: string) {
  if (rowKey) {
    // 行内加号
    addPopoverOpen.value = false
    addPopoverRowKey.value = addPopoverRowKey.value === rowKey ? '' : rowKey
  } else {
    // 全部数据加号
    addPopoverRowKey.value = ''
    addPopoverOpen.value = !addPopoverOpen.value
  }
}
</script>

<style scoped>
.import-page {
  display: flex;
  height: 100%;
  min-height: 480px;
  background: var(--bg-secondary);
  border-radius: 0;
  overflow: hidden;
  gap: 0;
  padding: 0;
}

/* 树面板 - 改进设计 */
.tree-panel {
  width: 300px;
  background: var(--bg-primary);
  padding: var(--spacing-2xl) var(--spacing-lg);
  border-right: 2px solid var(--primary-color);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
  box-shadow: var(--shadow-md);
  position: relative;
}

/* 树面板顶部装饰条 */
.tree-panel::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--primary-color) 0%, var(--primary-light) 100%);
}

.preview-panel {
  flex: 1;
  padding: var(--spacing-2xl);
  background: var(--bg-secondary);
  display: flex;
  align-items: flex-start;
}

.file-preview {
  color: var(--primary-color);
  font-size: 18px;
  font-weight: 600;
  background: var(--bg-primary);
  border-radius: var(--radius-lg);
  padding: var(--spacing-2xl);
  min-width: 320px;
  min-height: 120px;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-color);
}

.file-preview-placeholder {
  color: var(--text-tertiary);
  font-size: 15px;
  padding: var(--spacing-2xl);
  text-align: center;
}

.all-data-btn-wrap {
  margin-bottom: var(--spacing-sm);
}

.tree-actions {
  margin-bottom: var(--spacing-sm);
}

.draggable-tree {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  overflow-x: auto;
  padding-right: 4px;
}

.convert-all-btn {
  width: 100%;
  font-weight: 500;
  height: 40px;
}

/* 全部数据按钮 - 改进设计 */
.all-data-btn {
  position: relative;
  width: 100%;
  min-height: 40px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--bg-secondary);
  color: var(--text-primary);
  padding: var(--spacing-md) var(--spacing-lg);
  font-weight: 500;
  font-size: 14px;
  cursor: pointer;
  transition: var(--transition-base);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
}

.all-data-btn.active,
.all-data-btn:hover {
  background: var(--primary-color);
  color: #ffffff;
  border-color: var(--primary-color);
  box-shadow: var(--shadow-md);
  transform: translateY(-1px);
}

.json-view {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border-radius: var(--radius-md);
  padding: var(--spacing-lg);
  font-size: 13px;
  line-height: 1.6;
  overflow-x: auto;
  border: 1px solid var(--border-color);
}

.loading-wrap {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  min-height: 120px;
  font-size: 15px;
  color: var(--text-tertiary);
}

.loading-spinner {
  width: 24px;
  height: 24px;
  border: 3px solid var(--border-color);
  border-top: 3px solid var(--primary-color);
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

/* 添加按钮 - 改进设计 */
.all-data-add-btn {
  margin-left: var(--spacing-sm);
  cursor: pointer;
  display: flex;
  align-items: center;
  padding: var(--spacing-xs);
  border-radius: var(--radius-sm);
  opacity: 1;
  transition: var(--transition-base);
}

.all-data-btn:hover .all-data-add-btn {
  opacity: 1;
}

.all-data-add-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

/* Popover 样式 - 统一设计 */
.all-data-add-popover {
  min-width: 140px;
  background: var(--bg-primary);
  box-shadow: var(--shadow-lg);
  border-radius: var(--radius-md);
  padding: var(--spacing-sm) 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
  z-index: 10;
  border: 1px solid var(--border-color);
}

.add-popover-option {
  display: flex;
  align-items: center;
  padding: var(--spacing-sm) var(--spacing-lg);
  font-size: 14px;
  color: var(--text-primary);
  cursor: pointer;
  border-radius: var(--radius-sm);
  margin: 0 var(--spacing-xs);
  transition: var(--transition-fast);
}

.add-popover-option:hover {
  background: var(--bg-secondary);
  color: var(--primary-color);
}

/* 树行样式 - 改进设计 */
.custom-tree-row {
  width: 100%;
  min-height: 36px;
  border-radius: var(--radius-md);
  transition: var(--transition-fast);
  display: flex;
  align-items: center;
  position: relative;
  padding: var(--spacing-xs) var(--spacing-md);
  box-sizing: border-box;
}

:deep(.ant-tree .ant-tree-node-content-wrapper:hover),
.custom-tree-row:hover {
  background: rgba(26, 77, 143, 0.08) !important;
}

/* 选中状态 */
:deep(.ant-tree .ant-tree-node-selected .ant-tree-node-content-wrapper) {
  background: rgba(26, 77, 143, 0.12) !important;
  border-left: 3px solid var(--primary-color);
}

.tree-title-actions {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  opacity: 0;
  pointer-events: none;
  transition: var(--transition-fast);
}

.custom-tree-row:hover .tree-title-actions,
:deep(.ant-tree .ant-tree-node-content-wrapper:hover) .tree-title-actions {
  opacity: 1;
  pointer-events: auto;
}

.tree-add-btn,
.tree-menu-btn {
  border-radius: var(--radius-sm);
  transition: var(--transition-fast);
  padding: var(--spacing-xs);
  display: flex;
  align-items: center;
  cursor: pointer;
}

.tree-add-btn:hover,
.tree-menu-btn:hover {
  background: var(--bg-tertiary);
}

.tree-add-btn svg,
.tree-menu-btn svg {
  color: var(--text-secondary);
  fill: var(--text-secondary);
}

.tree-add-btn:hover svg,
.tree-menu-btn:hover svg {
  color: var(--primary-color);
  fill: var(--primary-color);
}

/* 编辑输入框 - 改进设计 */
.edit-input {
  height: 32px;
  font-size: 14px;
  padding: var(--spacing-xs) var(--spacing-md);
  outline: none;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-weight: normal;
  border: 2px solid var(--primary-color);
  border-radius: var(--radius-md);
  box-shadow: 0 0 0 3px rgba(26, 77, 143, 0.1);
  transition: var(--transition-fast);
}

.edit-input:focus {
  border-color: var(--primary-light);
}

:deep(.item-popover) {
  min-width: 130px;
  background: var(--bg-primary);
  box-shadow: var(--shadow-lg);
  border-radius: var(--radius-md);
  padding: var(--spacing-sm) 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
  z-index: 10;
  border: 1px solid var(--border-color);
}

.popover-option {
  display: flex;
  align-items: center;
  padding: var(--spacing-sm) var(--spacing-lg);
  font-size: 14px;
  color: var(--text-primary);
  cursor: pointer;
  border-radius: var(--radius-sm);
  margin: 0 var(--spacing-xs);
  transition: var(--transition-fast);
}

.popover-option:hover {
  background: var(--bg-secondary);
  color: var(--primary-color);
}
</style>
