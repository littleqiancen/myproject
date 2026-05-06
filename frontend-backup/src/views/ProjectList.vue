<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
      <h2 style="margin: 0;">项目列表</h2>
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon> 新建项目
      </el-button>
    </div>

    <el-row :gutter="20" v-loading="loading">
      <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="project in projects" :key="project.id" style="margin-bottom: 20px;">
        <el-card shadow="hover" class="project-card" @click="goToProject(project.id)">
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="font-weight: bold; font-size: 16px;">{{ project.name }}</span>
              <el-dropdown @click.stop trigger="click" @command="(cmd: string) => handleCommand(cmd, project)">
                <el-icon style="cursor: pointer; padding: 4px;" @click.stop><MoreFilled /></el-icon>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="edit">编辑</el-dropdown-item>
                    <el-dropdown-item command="delete" style="color: #f56c6c;">删除</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </template>
          <p style="color: #909399; font-size: 13px; min-height: 40px;">
            {{ project.description || '暂无描述' }}
          </p>
          <div style="display: flex; justify-content: space-around; margin-top: 12px;">
            <div style="text-align: center;">
              <div style="font-size: 20px; font-weight: bold; color: #409EFF;">{{ project.stats.document_count }}</div>
              <div style="font-size: 12px; color: #909399;">文档</div>
            </div>
            <div style="text-align: center;">
              <div style="font-size: 20px; font-weight: bold; color: #67c23a;">{{ project.stats.test_point_count }}</div>
              <div style="font-size: 12px; color: #909399;">测试点</div>
            </div>
            <div style="text-align: center;">
              <div style="font-size: 20px; font-weight: bold; color: #e6a23c;">{{ project.stats.test_case_count }}</div>
              <div style="font-size: 12px; color: #909399;">用例</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-empty v-if="!loading && projects.length === 0" description="暂无项目，点击上方按钮创建" />

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingProject ? '编辑项目' : '新建项目'"
      width="500px"
    >
      <el-form :model="form" label-width="80px">
        <el-form-item label="项目名称" required>
          <el-input v-model="form.name" placeholder="请输入项目名称" />
        </el-form-item>
        <el-form-item label="项目描述">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入项目描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="submitProject" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, MoreFilled } from '@element-plus/icons-vue'
import { projectApi } from '../api'
import type { Project } from '../types'

const router = useRouter()
const projects = ref<Project[]>([])
const loading = ref(false)
const showCreateDialog = ref(false)
const submitting = ref(false)
const editingProject = ref<Project | null>(null)
const form = ref({ name: '', description: '' })

const loadProjects = async () => {
  loading.value = true
  try {
    const { data } = await projectApi.list()
    projects.value = data.items
  } catch (e: any) {
    ElMessage.error('加载项目列表失败')
  } finally {
    loading.value = false
  }
}

const goToProject = (id: string) => {
  router.push(`/projects/${id}`)
}

const handleCommand = (command: string, project: Project) => {
  if (command === 'edit') editProject(project)
  else if (command === 'delete') deleteProject(project)
}

const editProject = (project: Project) => {
  editingProject.value = project
  form.value = { name: project.name, description: project.description || '' }
  showCreateDialog.value = true
}

const deleteProject = async (project: Project) => {
  try {
    await ElMessageBox.confirm(`确定要删除项目「${project.name}」吗？此操作不可恢复。`, '删除确认', {
      type: 'warning',
    })
    await projectApi.delete(project.id)
    ElMessage.success('删除成功')
    loadProjects()
  } catch {}
}

const submitProject = async () => {
  if (!form.value.name.trim()) {
    ElMessage.warning('请输入项目名称')
    return
  }
  submitting.value = true
  try {
    if (editingProject.value) {
      await projectApi.update(editingProject.value.id, form.value)
      ElMessage.success('更新成功')
    } else {
      await projectApi.create(form.value)
      ElMessage.success('创建成功')
    }
    showCreateDialog.value = false
    editingProject.value = null
    form.value = { name: '', description: '' }
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
.project-card {
  cursor: pointer;
  transition: transform 0.2s;
}
.project-card:hover {
  transform: translateY(-4px);
}
</style>
