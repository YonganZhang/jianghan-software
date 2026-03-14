type MyTreeNode = {
  title: string
  id: number
  type: string
  children?: MyTreeNode[]
  key?: string
}

// 根据ID和类型查找节点本身
export function findNodeByIdAndType(
  nodes: MyTreeNode[],
  targetId: number,
  targetType: string
): MyTreeNode | null {
  for (const node of nodes) {
    if (node.id === targetId && node.type === targetType) {
      return node
    }
    if (node.children) {
      const found = findNodeByIdAndType(node.children, targetId, targetType)
      if (found) return found
    }
  }
  return null
}

// 根据key找父节点
export function findParentDirectory(tree: MyTreeNode[], targetKey: string): MyTreeNode | null {
  function dfs(node: MyTreeNode, parent: MyTreeNode | null): MyTreeNode | null {
    console.log('检查节点:', node.key, '目标:', targetKey)
    if (String(node.key) === String(targetKey)) {
      console.log('找到目标，父节点:', parent)
      return parent && parent.type === 'directory' ? parent : null
    }
    if (Array.isArray(node.children)) {
      for (const child of node.children) {
        const result = dfs(child, node)
        if (result) return result
      }
    }
    return null
  }

  for (const root of tree) {
    const result = dfs(root, null)
    if (result) return result
  }
  return null
}

// 根据key查找当前节点
export function findNodeByKey(tree: MyTreeNode[], targetKey: string): MyTreeNode | null {
  function dfs(node: MyTreeNode): MyTreeNode | null {
    if (String(node.key) === String(targetKey)) {
      return node
    }
    if (Array.isArray(node.children)) {
      for (const child of node.children) {
        const result = dfs(child)
        if (result) return result
      }
    }
    return null
  }

  for (const root of tree) {
    const result = dfs(root)
    if (result) return result
  }
  return null
}


