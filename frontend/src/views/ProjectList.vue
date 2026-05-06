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
                <el-dropdown-item
                  style="color: var(--el-color-danger)"
                  @click="deleteProject(project)"
                >
                  删除
                </el-dropdown-item>
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

const deleteProject = async (project: Project) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除项目「${project.name}」吗？此操作不可恢复。`,
      '删除确认',
      { type: 'warning' }
    )
    await projectApi.delete(project.id)
    ElMessage.success('删除成功')
    loadProjects()
  } catch {
    // user cancelled or error
  }
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
