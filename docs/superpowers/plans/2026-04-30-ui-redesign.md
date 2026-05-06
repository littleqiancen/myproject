# 克莱因蓝 UI redesign 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 基于设计文档，从零重建 CaseGen 前端，整体替换为克莱因蓝主题（#002FA7），旧前端备份保留。

**Architecture:** 全新 Vite + Vue 3 项目，直接用设计文档中的 CSS 变量覆盖 Element Plus 默认主题。stores/api/types 从旧项目迁移（纯逻辑，无需改动），所有 .vue 组件重写。列表/详情/设置共 3 个页面 + 2 个公共组件。

**Tech Stack:** Vue 3.5 + Vite 6 + Element Plus 2.9 + Pinia 2.2 + Vue Router 4.4 + Axios 1.7 + TypeScript 5.6

---

### Task 1: 备份旧前端

**Files:**
- Rename: `frontend/` → `frontend-backup/`

- [ ] **Step 1: 重命名旧前端目录**

```bash
mv frontend frontend-backup
```

- [ ] **Step 2: 验证备份存在**

```bash
ls frontend-backup/package.json && echo "Backup OK"
```
Expected: `Backup OK`

- [ ] **Step 3: 提交备份**

```bash
git add frontend-backup/
git commit -m "chore: backup old frontend before UI redesign"
```

---

### Task 2: 脚手架新前端项目

**Files:**
- Create: `frontend/` (entire project scaffold)

- [ ] **Step 1: 创建 Vite + Vue 3 + TypeScript 项目**

```bash
npm create vite@latest frontend -- --template vue-ts
```
Choose defaults when prompted.

- [ ] **Step 2: 进入新项目安装依赖**

```bash
cd frontend && npm install
```

- [ ] **Step 3: 安装额外依赖**

```bash
npm install vue-router@^4.4.0 pinia@^2.2.0 element-plus@^2.9.0 @element-plus/icons-vue@^2.3.0 axios@^1.7.0
```

- [ ] **Step 4: 验证项目能启动**

```bash
npm run dev
```
Open http://localhost:5173, verify Vite welcome page appears. Stop dev server (Ctrl+C).

- [ ] **Step 5: 提交骨架**

```bash
git add frontend/
git commit -m "scaffold: new Vite + Vue 3 + TS project"
```

---

### Task 3: 创建 CSS 变量主题系统

**Files:**
- Create: `frontend/src/styles/theme.css`

- [ ] **Step 1: 编写 theme.css**

```css
/* 克莱因蓝主题 — CSS 变量覆盖 Element Plus */

:root {
  /* 品牌色 */
  --el-color-primary: #002FA7;
  --el-color-primary-light-3: #3B82F6;
  --el-color-primary-light-5: #60A5FA;
  --el-color-primary-light-7: #93C5FD;
  --el-color-primary-light-8: #BFDBFE;
  --el-color-primary-light-9: #EFF6FF;
  --el-color-primary-dark-2: #1E3A8A;

  /* 成功色 */
  --el-color-success: #059669;
  --el-color-success-light-3: #34D399;
  --el-color-success-light-5: #6EE7B7;
  --el-color-success-light-7: #A7F3D0;
  --el-color-success-light-8: #D1FAE5;
  --el-color-success-light-9: #ECFDF5;

  /* 警告色 */
  --el-color-warning: #B45309;
  --el-color-warning-light-3: #D97706;
  --el-color-warning-light-5: #F59E0B;
  --el-color-warning-light-7: #FCD34D;
  --el-color-warning-light-8: #FDE68A;
  --el-color-warning-light-9: #FEF3C7;

  /* 危险色 */
  --el-color-danger: #B91C1C;
  --el-color-danger-light-3: #DC2626;
  --el-color-danger-light-5: #EF4444;
  --el-color-danger-light-7: #F87171;
  --el-color-danger-light-8: #FCA5A5;
  --el-color-danger-light-9: #FEE2E2;

  /* 圆角 */
  --el-border-radius-base: 8px;
  --el-border-radius-small: 6px;
  --el-border-radius-round: 999px;

  /* 字体 */
  --el-font-size-base: 14px;
  --el-font-size-small: 12px;

  /* 自定义令牌 */
  --brand-primary: #002FA7;
  --brand-primary-light: #3B82F6;
  --brand-primary-lighter: #60A5FA;
  --bg-page: #F8FAFC;
  --bg-card: #FFFFFF;
  --border-card: #E2E8F0;
  --border-light: #F1F5F9;
  --text-primary: #0F172A;
  --text-secondary: #64748B;
  --text-tertiary: #94A3B8;
  --shadow-card: 0 1px 3px rgba(0, 0, 0, 0.04);
  --shadow-primary: 0 2px 8px rgba(0, 47, 167, 0.25);
  --shadow-highlight: 0 4px 20px rgba(0, 47, 167, 0.3);
  --radius-card: 16px;
  --radius-btn: 8px;
  --radius-icon: 10px;
}

/* 全局基础样式 */
body {
  margin: 0;
  background: var(--bg-page);
  color: var(--text-primary);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
    'Helvetica Neue', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* Element Plus 组件全局覆盖 */
.el-card {
  border-radius: var(--radius-card) !important;
  border-color: var(--border-card) !important;
}

.el-button--primary {
  --el-button-bg-color: var(--brand-primary);
  --el-button-border-color: var(--brand-primary);
  --el-button-hover-bg-color: var(--brand-primary-light);
  --el-button-hover-border-color: var(--brand-primary-light);
  --el-button-active-bg-color: var(--brand-primary);
  border-radius: var(--radius-btn);
  font-weight: 500;
}

.el-button {
  border-radius: var(--radius-btn);
  font-weight: 500;
}

.el-tag {
  border-radius: 999px;
  padding: 3px 12px;
  font-weight: 500;
  border: none;
}

.el-table {
  --el-table-border-color: transparent;
}

.el-table th.el-table__cell {
  background: var(--bg-page);
  color: var(--text-secondary);
  font-weight: 500;
  font-size: 12px;
  border-bottom: none;
}

.el-table td.el-table__cell {
  border-bottom: 1px solid var(--border-light);
}

.el-table--striped .el-table__body tr.el-table__row--striped td.el-table__cell {
  background: var(--bg-page);
}

.el-input .el-input__wrapper {
  border-radius: var(--radius-btn);
  box-shadow: 0 0 0 1px var(--border-card) inset;
}

.el-input .el-input__wrapper:hover {
  box-shadow: 0 0 0 1px var(--border-card) inset;
}

.el-input.is-focus .el-input__wrapper {
  box-shadow: 0 0 0 1px var(--brand-primary) inset !important;
}

.el-select .el-input__wrapper {
  border-radius: var(--radius-btn);
}

.el-dialog {
  border-radius: var(--radius-card);
}

.el-pagination {
  justify-content: flex-end;
}

.el-tabs__active-bar {
  background-color: var(--brand-primary);
}

.el-tabs__item.is-active {
  color: var(--brand-primary);
  font-weight: 600;
}
```

- [ ] **Step 2: 提交**

```bash
git add frontend/src/styles/theme.css
git commit -m "feat: add Klein Blue CSS variable theme system"
```

---

### Task 4: 配置 main.ts 入口文件

**Files:**
- Write: `frontend/src/main.ts`

- [ ] **Step 1: 编写 main.ts**

```typescript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import './styles/theme.css'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(ElementPlus, { locale: zhCn })

app.mount('#app')
```

- [ ] **Step 2: 提交**

```bash
git add frontend/src/main.ts
git commit -m "feat: configure main.ts with Klein Blue theme and Element Plus"
```

---

### Task 5: 配置 App.vue 根组件

**Files:**
- Write: `frontend/src/App.vue`

- [ ] **Step 1: 编写 App.vue**

```vue
<template>
  <router-view />
</template>
```

- [ ] **Step 2: 提交**

```bash
git add frontend/src/App.vue
git commit -m "feat: minimal App.vue root component"
```

---

### Task 6: 迁移基础设施文件（types, api, stores, router）

**Files:**
- Create: `frontend/src/types/index.ts`
- Create: `frontend/src/api/index.ts`
- Create: `frontend/src/stores/project.ts`
- Create: `frontend/src/stores/document.ts`
- Create: `frontend/src/stores/testPoint.ts`
- Create: `frontend/src/stores/testCase.ts`
- Create: `frontend/src/stores/knowledgeBase.ts`
- Create: `frontend/src/router/index.ts`

- [ ] **Step 1: 从备份复制 types/index.ts**

```bash
cp frontend-backup/src/types/index.ts frontend/src/types/index.ts
```

- [ ] **Step 2: 从备份复制 api/index.ts**

```bash
cp frontend-backup/src/api/index.ts frontend/src/api/index.ts
```

- [ ] **Step 3: 从备份复制所有 stores**

```bash
cp frontend-backup/src/stores/project.ts frontend/src/stores/project.ts
cp frontend-backup/src/stores/document.ts frontend/src/stores/document.ts
cp frontend-backup/src/stores/testPoint.ts frontend/src/stores/testPoint.ts
cp frontend-backup/src/stores/testCase.ts frontend/src/stores/testCase.ts
cp frontend-backup/src/stores/knowledgeBase.ts frontend/src/stores/knowledgeBase.ts
```

- [ ] **Step 4: 从备份复制 router/index.ts**

```bash
cp frontend-backup/src/router/index.ts frontend/src/router/index.ts
```

- [ ] **Step 5: 验证文件都存在**

```bash
ls frontend/src/types/index.ts frontend/src/api/index.ts frontend/src/stores/*.ts frontend/src/router/index.ts
```
Expected: All 8 files listed.

- [ ] **Step 6: 提交**

```bash
git add frontend/src/types/index.ts frontend/src/api/index.ts frontend/src/stores/ frontend/src/router/index.ts
git commit -m "feat: migrate types, api, stores, router from old frontend"
```

---

### Task 7: 创建 AppLayout.vue（克莱因蓝布局）

**Files:**
- Create: `frontend/src/components/AppLayout.vue`

- [ ] **Step 1: 编写 AppLayout.vue**

```vue
<template>
  <div class="app-shell">
    <!-- 侧边栏 -->
    <aside class="sidebar">
      <div class="sidebar-brand">
        <div class="brand-icon">◆</div>
      </div>
      <nav class="sidebar-nav">
        <router-link to="/" class="nav-item" :class="{ active: isProjectsActive }">
          <el-icon :size="18"><FolderOpened /></el-icon>
        </router-link>
        <router-link to="/settings" class="nav-item" :class="{ active: route.path === '/settings' }">
          <el-icon :size="18"><Setting /></el-icon>
        </router-link>
      </nav>
      <div class="sidebar-user">
        <div class="user-avatar">U</div>
      </div>
    </aside>

    <!-- 主内容区 -->
    <div class="main-area">
      <header class="top-header">
        <div class="header-left">
          <slot name="header-title">
            <h1 class="page-title">{{ pageTitle }}</h1>
          </slot>
        </div>
        <div class="header-right">
          <slot name="header-actions" />
        </div>
      </header>
      <main class="main-content">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { FolderOpened, Setting } from '@element-plus/icons-vue'

const route = useRoute()

const isProjectsActive = computed(() =>
  route.path === '/' || route.path.startsWith('/projects')
)

const pageTitle = computed(() => {
  if (route.path === '/') return '项目管理'
  if (route.path === '/settings') return '系统设置'
  if (route.name === 'ProjectDetail') return '项目详情'
  return ''
})
</script>

<style scoped>
.app-shell {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

/* 侧边栏 */
.sidebar {
  width: 56px;
  display: flex;
  flex-direction: column;
  background: #fff;
  box-shadow: 2px 0 12px rgba(0, 47, 167, 0.08);
  z-index: 10;
  flex-shrink: 0;
}

.sidebar-brand {
  height: 52px;
  background: var(--brand-primary);
  display: flex;
  align-items: center;
  justify-content: center;
}

.brand-icon {
  width: 28px;
  height: 28px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 14px;
  font-weight: bold;
}

.sidebar-nav {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 16px;
  gap: 6px;
}

.nav-item {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-tertiary);
  text-decoration: none;
  transition: all 0.15s ease;
}

.nav-item:hover {
  background: var(--el-color-primary-light-9);
  color: var(--brand-primary);
}

.nav-item.active {
  background: var(--el-color-primary-light-9);
  color: var(--brand-primary);
}

.sidebar-user {
  height: 52px;
  border-top: 1px solid var(--el-color-primary-light-9);
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-avatar {
  width: 28px;
  height: 28px;
  background: var(--brand-primary);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 12px;
}

/* 主内容区 */
.main-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: var(--bg-page);
}

.top-header {
  height: 52px;
  background: rgba(248, 250, 252, 0.85);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border-card);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  position: sticky;
  top: 0;
  z-index: 5;
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.page-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.main-content {
  flex: 1;
  overflow: auto;
  padding: 24px;
}
</style>
```

- [ ] **Step 2: 提交**

```bash
git add frontend/src/components/AppLayout.vue
git commit -m "feat: create Klein Blue AppLayout with 56px sidebar and glass header"
```

---

### Task 8: 创建 ProjectList.vue（项目列表页）

**Files:**
- Create: `frontend/src/views/ProjectList.vue`

- [ ] **Step 1: 编写 ProjectList.vue — template 部分**

```vue
<template>
  <AppLayout>
    <template #header-actions>
      <div class="header-search">
        <el-input
          v-model="searchQuery"
          placeholder="搜索项目..."
          :prefix-icon="Search"
          clearable
          size="default"
        />
      </div>
      <el-button type="primary" @click="openCreate">
        <el-icon><Plus /></el-icon>
        <span>新建项目</span>
      </el-button>
    </template>

    <template #header-title>
      <h1 class="page-title">项目管理</h1>
      <span class="count-pill" v-if="projects.length">{{ projects.length }} 个项目</span>
    </template>

    <!-- 统计卡片 -->
    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-icon">
          <el-icon :size="18"><Document /></el-icon>
        </div>
        <div class="stat-label">文档总数</div>
        <div class="stat-value">{{ totalDocuments }}</div>
        <div class="stat-trend up" v-if="totalDocuments > 0">↑ 较上月</div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">
          <el-icon :size="18"><Aim /></el-icon>
        </div>
        <div class="stat-label">测试点总数</div>
        <div class="stat-value">{{ totalTestPoints }}</div>
        <div class="stat-trend up" v-if="totalTestPoints > 0">↑ 较上月</div>
      </div>
      <div class="stat-card stat-card-highlight">
        <div class="stat-icon stat-icon-glow">
          <el-icon :size="18"><List /></el-icon>
        </div>
        <div class="stat-label">用例总数</div>
        <div class="stat-value">{{ totalTestCases }}</div>
        <div class="stat-trend" v-if="totalTestCases > 0">↑ 较上月</div>
      </div>
    </div>

    <!-- 操作栏 -->
    <div class="toolbar">
      <h2 class="section-title">全部项目</h2>
    </div>

    <!-- 项目卡片网格 -->
    <div v-loading="loading" class="project-grid">
      <div
        v-for="project in projects"
        :key="project.id"
        class="project-card"
        @click="$router.push(`/projects/${project.id}`)"
      >
        <div class="card-top">
          <div class="card-icon" :style="{ background: iconColor(project.id) }">
            {{ iconEmoji(project.id) }}
          </div>
          <el-dropdown trigger="click" @click.stop>
            <el-icon class="card-more" :size="16"><MoreFilled /></el-icon>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="editProject(project, $event)">编辑</el-dropdown-item>
                <el-dropdown-item style="color: var(--el-color-danger)">删除</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
        <h3 class="card-title">{{ project.name }}</h3>
        <p class="card-desc">{{ project.description || '暂无描述' }}</p>
        <div class="card-stats">
          <div class="card-stat">
            <span class="card-stat-num">{{ project.stats.document_count }}</span>
            <span class="card-stat-label">文档</span>
          </div>
          <div class="card-stat">
            <span class="card-stat-num">{{ project.stats.test_point_count }}</span>
            <span class="card-stat-label">测试点</span>
          </div>
          <div class="card-stat">
            <span class="card-stat-num">{{ project.stats.test_case_count }}</span>
            <span class="card-stat-label">用例</span>
          </div>
        </div>
      </div>
    </div>

    <el-empty v-if="!loading && projects.length === 0" description="暂无项目，点击上方按钮创建" />

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="showDialog"
      :title="editing ? '编辑项目' : '新建项目'"
      width="480px"
      :close-on-click-modal="false"
    >
      <el-form :model="form" label-width="80px" @submit.prevent="submit">
        <el-form-item label="项目名称" required>
          <el-input v-model="form.name" placeholder="请输入项目名称" />
        </el-form-item>
        <el-form-item label="项目描述">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请输入项目描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="submit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </AppLayout>
</template>
```

- [ ] **Step 2: 编写 ProjectList.vue — script 部分**

```vue
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, MoreFilled, Search, Document, Aim, List } from '@element-plus/icons-vue'
import { projectApi } from '../api'
import type { Project } from '../types'
import AppLayout from '../components/AppLayout.vue'

const projects = ref<Project[]>([])
const loading = ref(false)
const showDialog = ref(false)
const editing = ref(false)
const editingProject = ref<Project | null>(null)
const submitting = ref(false)
const searchQuery = ref('')
const form = ref({ name: '', description: '' })

const totalDocuments = computed(() =>
  projects.value.reduce((s, p) => s + (p.stats?.document_count || 0), 0)
)
const totalTestPoints = computed(() =>
  projects.value.reduce((s, p) => s + (p.stats?.test_point_count || 0), 0)
)
const totalTestCases = computed(() =>
  projects.value.reduce((s, p) => s + (p.stats?.test_case_count || 0), 0)
)

const iconColors = ['#002FA7', '#3B82F6', '#60A5FA']
const iconEmojis = ['🛒', '👤', '🔔', '📦', '💰', '📊', '⚡', '🏠']
const iconColor = (id: string) => {
  const idx = [...projects.value].findIndex(p => p.id === id)
  return iconColors[idx % iconColors.length]
}
const iconEmoji = (id: string) => {
  const idx = [...projects.value].findIndex(p => p.id === id)
  return iconEmojis[idx % iconEmojis.length]
}

const loadProjects = async () => {
  loading.value = true
  try {
    const { data } = await projectApi.list()
    projects.value = data.items
  } catch {
    ElMessage.error('加载项目列表失败')
  } finally {
    loading.value = false
  }
}

const openCreate = () => {
  editing.value = false
  editingProject.value = null
  form.value = { name: '', description: '' }
  showDialog.value = true
}

const editProject = (project: Project, event: Event) => {
  event.stopPropagation()
  editing.value = true
  editingProject.value = project
  form.value = { name: project.name, description: project.description || '' }
  showDialog.value = true
}

const submit = async () => {
  if (!form.value.name.trim()) {
    ElMessage.warning('请输入项目名称')
    return
  }
  submitting.value = true
  try {
    if (editing.value && editingProject.value) {
      await projectApi.update(editingProject.value.id, form.value)
      ElMessage.success('更新成功')
    } else {
      await projectApi.create(form.value)
      ElMessage.success('创建成功')
    }
    showDialog.value = false
    loadProjects()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '操作失败')
  } finally {
    submitting.value = false
  }
}

onMounted(loadProjects)
</script>
```

- [ ] **Step 3: 编写 ProjectList.vue — style 部分**

```css
<style scoped>
.page-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.count-pill {
  background: var(--el-color-primary-light-9);
  color: var(--brand-primary);
  padding: 2px 10px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 500;
}

.header-search {
  width: 200px;
}

/* 统计卡片 */
.stats-row {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  flex: 1;
  background: var(--bg-card);
  border-radius: var(--radius-card);
  padding: 20px;
  border: 1px solid var(--border-card);
  box-shadow: var(--shadow-card);
}

.stat-card-highlight {
  background: var(--brand-primary);
  color: #fff;
  border-color: var(--brand-primary);
  box-shadow: var(--shadow-highlight);
}

.stat-icon {
  width: 36px;
  height: 36px;
  background: var(--el-color-primary-light-9);
  border-radius: var(--radius-icon);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--brand-primary);
  margin-bottom: 12px;
}

.stat-icon-glow {
  background: rgba(255, 255, 255, 0.15);
  color: #fff;
}

.stat-card-highlight .stat-label {
  color: rgba(255, 255, 255, 0.7);
}

.stat-label {
  font-size: 12px;
  color: var(--text-secondary);
  font-weight: 500;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  line-height: 1;
  margin-bottom: 4px;
}

.stat-trend {
  font-size: 12px;
  font-weight: 500;
}

.stat-trend.up {
  color: var(--el-color-success);
}

.stat-card-highlight .stat-trend {
  color: rgba(255, 255, 255, 0.8);
}

/* 操作栏 */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

/* 项目卡片网格 */
.project-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

@media (max-width: 1200px) {
  .project-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 768px) {
  .project-grid { grid-template-columns: 1fr; }
}

.project-card {
  background: var(--bg-card);
  border-radius: var(--radius-card);
  padding: 20px;
  border: 1px solid var(--border-card);
  box-shadow: var(--shadow-card);
  cursor: pointer;
  transition: all 0.2s ease;
}

.project-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.card-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.card-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.card-more {
  color: var(--text-tertiary);
  cursor: pointer;
  padding: 2px;
  border-radius: 6px;
}

.card-more:hover {
  background: var(--border-light);
}

.card-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 6px 0;
}

.card-desc {
  font-size: 12px;
  color: var(--text-secondary);
  margin: 0 0 16px 0;
  line-height: 1.4;
}

.card-stats {
  display: flex;
  gap: 16px;
  padding-top: 12px;
  border-top: 1px solid var(--border-light);
}

.card-stat {
  text-align: left;
}

.card-stat-num {
  font-size: 16px;
  font-weight: 700;
  color: var(--brand-primary);
  display: block;
}

.card-stat-label {
  font-size: 10px;
  color: var(--text-tertiary);
}
</style>
```

- [ ] **Step 4: 提交**

```bash
git add frontend/src/views/ProjectList.vue
git commit -m "feat: create Klein Blue ProjectList with stats cards and grid"
```

---

### Task 9: 创建 ProjectDetail.vue（项目详情页）

**Files:**
- Create: `frontend/src/views/ProjectDetail.vue`

- [ ] **Step 1: 从备份复制 ProjectDetail.vue 作为基础**

```bash
cp frontend-backup/src/views/ProjectDetail.vue frontend/src/views/ProjectDetail.vue
```

- [ ] **Step 2: 修改 ProjectDetail.vue 的 template 开头和 style**

将已有的 ProjectDetail.vue 包装在 `<AppLayout>` 中，更新标题+操作按钮位置，添加克莱因蓝样式。

具体的改动：

**模板改动：** 在 `<template>` 最外层包裹 `<AppLayout>`，去掉原来的返回按钮和项目标题（移到 header slot），将上传/操作按钮移到 `#header-actions` slot，保留 tabs 内容不变。

定位到文件开头，将：
```vue
<template>
  <div v-loading="loading">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
      <h2 style="margin: 0;">{{ project?.name || '项目详情' }}</h2>
      <el-button @click="$router.push('/')">返回列表</el-button>
    </div>
```
替换为：
```vue
<template>
  <AppLayout>
    <template #header-title>
      <h1 class="page-title">{{ project?.name || '项目详情' }}</h1>
    </template>
    <template #header-actions>
      <el-button @click="$router.push('/')">← 返回列表</el-button>
    </template>
    <div v-loading="loading">
```

以及将文件末尾的 `</div>` (最外层闭合) 改为：
```vue
    </div>
  </AppLayout>
</template>
```

在 `<script setup>` 中添加 AppLayout import：
```typescript
import AppLayout from '../components/AppLayout.vue'
```

在文件末尾添加 `<style scoped>` 块：
```css
<style scoped>
.page-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.project-tabs {
  margin-top: 0;
}

.project-tabs :deep(.el-tabs__header) {
  margin-bottom: 16px;
}

.project-tabs :deep(.el-tabs__nav-wrap::after) {
  height: 1px;
  background: var(--border-card);
}

.tab-toolbar {
  margin-bottom: 16px;
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}
</style>
```

并在第一个 `<el-tabs>` 上添加 `class="project-tabs"`。

在每个标签页的操作按钮区（文档上传行、测试点筛选行、测试用例筛选行），将外层的 `<div style="...">` 改为 `<div class="tab-toolbar">`。

- [ ] **Step 3: 提交**

```bash
git add frontend/src/views/ProjectDetail.vue
git commit -m "feat: wrap ProjectDetail in Klein Blue AppLayout with new styles"
```

---

### Task 10: 创建 Settings.vue（系统设置页）

**Files:**
- Create: `frontend/src/views/Settings.vue`

- [ ] **Step 1: 从备份复制 Settings.vue**

```bash
cp frontend-backup/src/views/Settings.vue frontend/src/views/Settings.vue
```

- [ ] **Step 2: 包装在 AppLayout 中并更新样式**

**模板改动：** 在 `<template>` 最外层包裹 AppLayout：

```vue
<template>
  <AppLayout>
    <h2 class="settings-title">系统设置</h2>

    <el-card class="settings-card">
      <template #header><span class="card-header-title">LLM 模型配置</span></template>
      <!-- 保持原有 el-form 内容不变 -->
    </el-card>

    <el-card class="settings-card">
      <template #header><span class="card-header-title">飞书通知配置</span></template>
      <!-- 保持原有 el-form 内容不变 -->
    </el-card>

    <el-button type="primary" @click="saveSettings" :loading="saving" size="large">保存设置</el-button>
  </AppLayout>
</template>
```

在 `<script setup>` 中添加：
```typescript
import AppLayout from '../components/AppLayout.vue'
```

在文件末尾添加：
```css
<style scoped>
.settings-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 20px 0;
}

.settings-card {
  margin-bottom: 20px;
}

.card-header-title {
  font-weight: 600;
  font-size: 15px;
}

.help-text {
  color: var(--text-tertiary);
  font-size: 12px;
  margin-top: 4px;
}
</style>
```

并将 form-item 中的 help div 的 `style="color: #909399"` 替换为 `class="help-text"`。

- [ ] **Step 3: 提交**

```bash
git add frontend/src/views/Settings.vue
git commit -m "feat: wrap Settings in Klein Blue AppLayout with card styles"
```

---

### Task 11: 迁移 AiProgressModal.vue

**Files:**
- Create: `frontend/src/components/AiProgressModal.vue`

- [ ] **Step 1: 从备份复制并更新样式**

```bash
cp frontend-backup/src/components/AiProgressModal.vue frontend/src/components/AiProgressModal.vue
```

- [ ] **Step 2: 更新图标颜色**

将 `<el-icon>` 中的硬编码颜色替换为 CSS 变量：

- `color="#409EFF"` → `color="var(--brand-primary)"`
- `color="#67c23a"` → `color="var(--el-color-success)"`
- `color="#f56c6c"` → `color="var(--el-color-danger)"`

在文件末尾添加 scoped style：
```css
<style scoped>
.status-icon {
  margin-bottom: 8px;
}

.status-title {
  margin-top: 16px;
  font-size: 16px;
}

.status-hint {
  color: var(--text-tertiary);
  font-size: 13px;
}

.status-error {
  color: var(--el-color-danger);
  font-size: 13px;
}

.status-token {
  color: var(--text-tertiary);
  font-size: 12px;
}
</style>
```

并给模板中的对应元素加上这些 class。

- [ ] **Step 3: 提交**

```bash
git add frontend/src/components/AiProgressModal.vue
git commit -m "feat: update AiProgressModal with Klein Blue color tokens"
```

---

### Task 12: 验证与清理

**Files:**
- Verify: all frontend files

- [ ] **Step 1: 清理 Vite 脚手架默认文件**

```bash
rm -f frontend/src/components/HelloWorld.vue 2>/dev/null
rm -f frontend/src/assets/vue.svg 2>/dev/null
rm -f frontend/public/vite.svg 2>/dev/null
```

- [ ] **Step 2: 更新 index.html title**

修改 `frontend/index.html`，将 `<title>` 改为：
```html
<title>CaseGen - AI测试用例生成平台</title>
```

- [ ] **Step 3: TypeScript 编译检查**

```bash
cd frontend && npx vue-tsc --noEmit
```

- [ ] **Step 4: 启动开发服务器验证**

```bash
cd frontend && npm run dev
```

访问 http://localhost:5173，验证：
- [ ] 侧边栏 56px，品牌区克莱因蓝
- [ ] 页面背景 #F8FAFC
- [ ] 项目管理页面统计卡、项目卡片正确渲染
- [ ] 能进入项目详情，tabs 正常工作
- [ ] 系统设置页正确渲染
- [ ] 所有主操作按钮为克莱因蓝

- [ ] **Step 5: 提交最终版本**

```bash
git add frontend/index.html
git add -A frontend/src/
git commit -m "feat: complete Klein Blue UI redesign for all pages"
```

---

### Task 13: 连接到后端验证完整功能

**Files:**
- Verify: frontend proxies to backend

- [ ] **Step 1: 配置 Vite 代理**

检查 `frontend/vite.config.ts` 是否包含后端代理。如无，添加：

```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

- [ ] **Step 2: 启动后端**

```bash
cd backend && source venv/bin/activate && uvicorn app.main:app --reload --port 8000 &
```

- [ ] **Step 3: 端到端验证**

在浏览器中：
- [ ] 创建新项目 → 成功
- [ ] 上传文档 → 成功
- [ ] AI 提取测试点 → 进度弹窗正常工作
- [ ] 生成测试用例 → 成功
- [ ] 导出 Excel → 成功
- [ ] 系统设置保存 → 持久化

- [ ] **Step 4: 提交代理配置**

```bash
git add frontend/vite.config.ts
git commit -m "chore: add Vite proxy config for backend API"
```
