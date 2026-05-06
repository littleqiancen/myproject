<template>
  <AppLayout>
    <template #header-title>
      <h1 class="page-title">{{ project?.name || '项目详情' }}</h1>
    </template>
    <template #header-actions>
      <el-button @click="$router.push('/')">← 返回列表</el-button>
    </template>
    <div v-loading="loading">

    <el-tabs v-model="activeTab" type="border-card" class="project-tabs">
      <!-- 文档标签页 -->
      <el-tab-pane label="文档管理" name="documents">
        <div class="tab-toolbar">
          <el-upload
            :action="`/api/v1/projects/${id}/documents/upload`"
            name="files"
            :on-success="onUploadSuccess"
            :on-error="onUploadError"
            :before-upload="beforeUpload"
            multiple
            :show-file-list="false"
            accept=".pdf,.docx,.md"
          >
            <el-button type="primary">上传文档</el-button>
          </el-upload>
          <el-button
            type="success"
            @click="extractTestPoints"
            :disabled="selectedDocIds.length === 0 || isExtracting"
            :loading="isExtracting"
          >
            {{ isExtracting ? '提取中...' : 'AI 提取测试点' }}
          </el-button>
          <span v-if="selectedDocIds.length > 0" style="color: #909399; font-size: 13px;">
            已选 {{ selectedDocIds.length }} 个文档
          </span>
        </div>

        <el-table :data="documents" @selection-change="onDocSelectionChange" border>
          <el-table-column type="selection" width="50" />
          <el-table-column prop="filename" label="文件名" />
          <el-table-column prop="file_type" label="类型" width="80">
            <template #default="{ row }">
              <el-tag size="small">{{ row.file_type.toUpperCase() }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="大小" width="100">
            <template #default="{ row }">
              {{ row.file_size ? (row.file_size / 1024).toFixed(1) + ' KB' : '-' }}
            </template>
          </el-table-column>
          <el-table-column label="解析状态" width="120">
            <template #default="{ row }">
              <el-tag :type="parseStatusType(row.parse_status)" size="small">
                {{ parseStatusText(row.parse_status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150">
            <template #default="{ row }">
              <el-button link type="primary" @click="viewDocument(row)">查看</el-button>
              <el-button link type="warning" @click="reparseDoc(row)">重解析</el-button>
              <el-button link type="danger" @click="deleteDoc(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- 测试点标签页 -->
      <el-tab-pane label="测试点" name="testpoints">
        <div class="tab-toolbar">
          <el-select v-model="tpFilter.priority" placeholder="优先级" clearable style="width: 120px;" @change="onTpFilterChange">
            <el-option label="P0" value="P0" /><el-option label="P1" value="P1" />
            <el-option label="P2" value="P2" /><el-option label="P3" value="P3" />
          </el-select>
          <el-select v-model="tpFilter.category" placeholder="分类" clearable style="width: 140px;" @change="onTpFilterChange">
            <el-option label="功能测试" value="functional" /><el-option label="边界/异常" value="edge_case" />
            <el-option label="性能测试" value="performance" /><el-option label="安全测试" value="security" />
          </el-select>
          <el-button type="primary" @click="showCreatePointDialog = true">手动新增</el-button>
          <el-button
            type="success"
            @click="generateCases"
            :disabled="selectedPointIds.length === 0 || isGeneratingCases"
            :loading="isGeneratingCases"
          >
            {{ isGeneratingCases ? '生成中...' : '一键生成用例' }}
          </el-button>
          <el-button
            type="danger"
            @click="batchDeletePoints"
            :disabled="selectedPointIds.length === 0"
          >
            批量删除
          </el-button>
        </div>

        <el-table :data="testPoints" @selection-change="onPointSelectionChange" border>
          <el-table-column type="selection" width="50" />
          <el-table-column prop="title" label="测试点标题" min-width="200" show-overflow-tooltip />
          <el-table-column prop="description" label="描述" min-width="250" show-overflow-tooltip />
          <el-table-column label="优先级" width="80">
            <template #default="{ row }">
              <el-tag :type="priorityType(row.priority)" size="small">{{ row.priority }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="分类" width="100">
            <template #default="{ row }">
              {{ categoryText(row.category) }}
            </template>
          </el-table-column>
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="tpStatusType(row.status)" size="small">
                <el-icon v-if="row.status === 'generating'" class="is-loading" style="margin-right: 4px;"><Loading /></el-icon>
                {{ tpStatusText(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="test_case_count" label="用例数" width="80" />
          <el-table-column label="操作" width="120">
            <template #default="{ row }">
              <el-button link type="primary" @click="editPoint(row)">编辑</el-button>
              <el-button link type="danger" @click="deletePoint(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-pagination
          v-model:current-page="tpPage.current"
          v-model:page-size="tpPage.size"
          :total="tpPage.total"
          :page-sizes="[20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          style="margin-top: 16px; justify-content: flex-end;"
          @current-change="loadTestPoints"
          @size-change="onTpSizeChange"
        />
      </el-tab-pane>

      <!-- 知识库标签页 -->
      <el-tab-pane label="知识库" name="knowledgebase">
        <div class="tab-toolbar">
          <el-button type="primary" @click="openCreateKBDialog">新建知识库</el-button>
        </div>

        <el-collapse v-model="activeKBIds" v-if="knowledgeBases.length > 0" @change="onKBCollapseChange">
          <el-collapse-item v-for="kb in knowledgeBases" :key="kb.id" :name="kb.id">
            <template #title>
              <div style="display: flex; align-items: center; gap: 12px; width: 100%;">
                <span style="font-weight: bold;">{{ kb.name }}</span>
                <el-tag size="small">{{ kb.document_count }} 文档</el-tag>
                <el-tag size="small" type="info">{{ kb.chunk_count }} 分块</el-tag>
                <el-tag :type="kb.status === 'active' ? 'success' : 'warning'" size="small">
                  {{ kb.status === 'active' ? '正常' : '处理中' }}
                </el-tag>
              </div>
            </template>

            <div style="padding: 0 16px;">
              <p v-if="kb.description" style="color: #909399; margin-bottom: 12px;">{{ kb.description }}</p>

              <div style="margin-bottom: 12px; display: flex; gap: 8px;">
                <el-upload
                  :action="`/api/v1/knowledge-bases/${kb.id}/documents/upload`"
                  name="files"
                  :on-success="() => onKBUploadSuccess(kb.id)"
                  :on-error="onKBUploadError"
                  multiple
                  :show-file-list="false"
                  accept=".pdf,.docx,.md,.txt"
                >
                  <el-button size="small" type="primary">上传文档</el-button>
                </el-upload>
                <el-button size="small" type="warning" @click="openEditKBDialog(kb)">编辑</el-button>
                <el-button size="small" type="danger" @click="deleteKB(kb)">删除</el-button>
              </div>

              <el-table :data="kbDocumentsMap[kb.id] || []" size="small" border>
                <el-table-column prop="filename" label="文件名" />
                <el-table-column prop="file_type" label="类型" width="80">
                  <template #default="{ row }">
                    <el-tag size="small">{{ row.file_type.toUpperCase() }}</el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="分块数" width="80" prop="chunk_count" />
                <el-table-column label="状态" width="100">
                  <template #default="{ row }">
                    <el-tag :type="kbDocStatusType(row.status)" size="small">{{ kbDocStatusText(row.status) }}</el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="80">
                  <template #default="{ row }">
                    <el-button link type="danger" size="small" @click="deleteKBDoc(kb.id, row)">删除</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-collapse-item>
        </el-collapse>
        <el-empty v-else description="暂无知识库，点击上方按钮创建" />
      </el-tab-pane>

      <!-- 测试用例标签页 -->
      <el-tab-pane label="测试用例" name="testcases">
        <div class="tab-toolbar">
          <el-select v-model="tcFilter.priority" placeholder="优先级" clearable style="width: 120px;" @change="onTcFilterChange">
            <el-option label="P0" value="P0" /><el-option label="P1" value="P1" />
            <el-option label="P2" value="P2" /><el-option label="P3" value="P3" />
          </el-select>
          <el-select v-model="tcFilter.case_type" placeholder="用例类型" clearable style="width: 120px;" @change="onTcFilterChange">
            <el-option label="正向" value="positive" /><el-option label="反向" value="negative" />
            <el-option label="边界" value="boundary" /><el-option label="边缘" value="edge" />
          </el-select>
          <el-button type="success" @click="exportExcel">导出Excel</el-button>
        </div>

        <el-table :data="testCases" border row-key="id">
          <el-table-column type="expand">
            <template #default="{ row }">
              <div style="padding: 12px 24px;">
                <p v-if="row.preconditions"><strong>前置条件：</strong>{{ row.preconditions }}</p>
                <el-table :data="row.steps" size="small" border style="margin-top: 8px;">
                  <el-table-column prop="step_number" label="步骤" width="60" />
                  <el-table-column prop="action" label="操作步骤" />
                  <el-table-column prop="expected_result" label="预期结果" />
                </el-table>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="title" label="用例标题" min-width="200" show-overflow-tooltip />
          <el-table-column prop="test_point_title" label="关联测试点" min-width="150" show-overflow-tooltip />
          <el-table-column label="优先级" width="80">
            <template #default="{ row }">
              <el-tag :type="priorityType(row.priority)" size="small">{{ row.priority }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="类型" width="80">
            <template #default="{ row }">
              {{ caseTypeText(row.case_type) }}
            </template>
          </el-table-column>
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="statusType(row.status)" size="small">
                <el-icon v-if="row.status === 'generating'" class="is-loading" style="margin-right: 4px;"><Loading /></el-icon>
                {{ statusText(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120">
            <template #default="{ row }">
              <el-button link type="primary" @click="editCase(row)">编辑</el-button>
              <el-button link type="danger" @click="deleteCase(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-pagination
          v-model:current-page="tcPage.current"
          v-model:page-size="tcPage.size"
          :total="tcPage.total"
          :page-sizes="[20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          style="margin-top: 16px; justify-content: flex-end;"
          @current-change="loadTestCases"
          @size-change="onTcSizeChange"
        />
      </el-tab-pane>
    </el-tabs>

    <!-- AI 进度弹窗 -->
    <AiProgressModal
      v-model="showProgress"
      :batch-id="currentBatchId"
      @completed="onBatchCompleted"
    />

    <!-- 新增/编辑测试点对话框 -->
    <el-dialog v-model="showCreatePointDialog" :title="editingPoint ? '编辑测试点' : '新增测试点'" width="600px">
      <el-form :model="pointForm" label-width="80px">
        <el-form-item label="标题" required>
          <el-input v-model="pointForm.title" />
        </el-form-item>
        <el-form-item label="描述" required>
          <el-input v-model="pointForm.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="优先级">
          <el-select v-model="pointForm.priority" style="width: 100%;">
            <el-option label="P0" value="P0" /><el-option label="P1" value="P1" />
            <el-option label="P2" value="P2" /><el-option label="P3" value="P3" />
          </el-select>
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="pointForm.category" style="width: 100%;">
            <el-option label="功能测试" value="functional" /><el-option label="边界/异常" value="edge_case" />
            <el-option label="性能测试" value="performance" /><el-option label="安全测试" value="security" />
          </el-select>
        </el-form-item>
        <el-form-item label="前置条件">
          <el-input v-model="pointForm.preconditions" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="预期结果">
          <el-input v-model="pointForm.expected_result" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreatePointDialog = false">取消</el-button>
        <el-button type="primary" @click="submitPoint">确定</el-button>
      </template>
    </el-dialog>

    <!-- 文档预览对话框 -->
    <el-dialog v-model="showDocPreview" title="文档内容" width="70%" top="5vh">
      <div v-if="previewDoc" style="max-height: 70vh; overflow: auto; white-space: pre-wrap; font-size: 14px; line-height: 1.8;">
        {{ previewDoc.parsed_markdown || previewDoc.raw_text || '暂无内容' }}
      </div>
    </el-dialog>

    <!-- 编辑测试用例对话框 -->
    <el-dialog v-model="showEditCaseDialog" title="编辑测试用例" width="700px">
      <el-form :model="caseForm" label-width="80px">
        <el-form-item label="标题">
          <el-input v-model="caseForm.title" />
        </el-form-item>
        <el-form-item label="前置条件">
          <el-input v-model="caseForm.preconditions" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="优先级">
          <el-select v-model="caseForm.priority" style="width: 100%;">
            <el-option label="P0" value="P0" /><el-option label="P1" value="P1" />
            <el-option label="P2" value="P2" /><el-option label="P3" value="P3" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="caseForm.status" style="width: 100%;">
            <el-option label="草稿" value="draft" />
            <el-option label="评审" value="review" />
            <el-option label="通过" value="approved" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditCaseDialog = false">取消</el-button>
        <el-button type="primary" @click="submitCase">确定</el-button>
      </template>
    </el-dialog>

    <!-- 新建/编辑知识库对话框 -->
    <el-dialog v-model="showKBDialog" :title="editingKB ? '编辑知识库' : '新建知识库'" width="500px">
      <el-form :model="kbForm" label-width="80px">
        <el-form-item label="名称" required>
          <el-input v-model="kbForm.name" placeholder="如：接口文档、历史用例" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="kbForm.description" type="textarea" :rows="3" placeholder="知识库用途说明" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showKBDialog = false">取消</el-button>
        <el-button type="primary" @click="submitKB">确定</el-button>
      </template>
    </el-dialog>

    <!-- AI 提取测试点配置对话框 -->
    <el-dialog v-model="showExtractDialog" title="AI 提取测试点" width="500px">
      <el-form label-width="100px">
        <el-form-item label="已选文档">
          <span>{{ selectedDocIds.length }} 个文档</span>
        </el-form-item>
        <el-form-item label="关联知识库">
          <el-select v-model="selectedKBIds" multiple placeholder="可选：选择知识库增强上下文" style="width: 100%;">
            <el-option v-for="kb in knowledgeBases" :key="kb.id" :label="kb.name" :value="kb.id">
              <span>{{ kb.name }}</span>
              <span style="color: #909399; margin-left: 8px; font-size: 12px;">{{ kb.chunk_count }} 分块</span>
            </el-option>
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showExtractDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmExtractTestPoints">开始提取</el-button>
      </template>
    </el-dialog>

    <!-- AI 生成用例配置对话框 -->
    <el-dialog v-model="showGenerateDialog" title="AI 生成测试用例" width="500px">
      <el-form label-width="100px">
        <el-form-item label="已选测试点">
          <span>{{ selectedPointIds.length }} 个测试点</span>
        </el-form-item>
        <el-form-item label="关联知识库">
          <el-select v-model="selectedKBIds" multiple placeholder="可选：选择知识库增强上下文" style="width: 100%;">
            <el-option v-for="kb in knowledgeBases" :key="kb.id" :label="kb.name" :value="kb.id">
              <span>{{ kb.name }}</span>
              <span style="color: #909399; margin-left: 8px; font-size: 12px;">{{ kb.chunk_count }} 分块</span>
            </el-option>
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showGenerateDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmGenerateCases">开始生成</el-button>
      </template>
    </el-dialog>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import { projectApi, documentApi, testPointApi, testCaseApi, aiApi, knowledgeBaseApi } from '../api'
import AppLayout from '../components/AppLayout.vue'
import AiProgressModal from '../components/AiProgressModal.vue'
import type { Project, Document, TestPoint, TestCase, KnowledgeBase, KnowledgeBaseDocument } from '../types'

const props = defineProps<{ id: string }>()

const project = ref<Project | null>(null)
const loading = ref(false)
const activeTab = ref('documents')

// 文档
const documents = ref<Document[]>([])
const selectedDocIds = ref<string[]>([])
const showDocPreview = ref(false)
const previewDoc = ref<Document | null>(null)

// 测试点
const testPoints = ref<TestPoint[]>([])
const selectedPointIds = ref<string[]>([])
const tpFilter = ref({ priority: '', category: '' })
const tpPage = ref({ current: 1, size: 20, total: 0 })
const showCreatePointDialog = ref(false)
const editingPoint = ref<TestPoint | null>(null)
const pointForm = ref({
  title: '', description: '', priority: 'P2', category: 'functional',
  preconditions: '', expected_result: ''
})

// 测试用例
const testCases = ref<TestCase[]>([])
const tcFilter = ref({ priority: '', case_type: '' })
const tcPage = ref({ current: 1, size: 20, total: 0 })
const showEditCaseDialog = ref(false)
const editingCase = ref<TestCase | null>(null)
const caseForm = ref({ title: '', preconditions: '', priority: '', status: '' })

// AI进度
const showProgress = ref(false)
const currentBatchId = ref('')
const currentBatchType = ref<'extract' | 'generate'>('extract')
const isExtracting = ref(false)
const isGeneratingCases = ref(false)

// 知识库
const knowledgeBases = ref<KnowledgeBase[]>([])
const activeKBIds = ref<string[]>([])
const kbDocumentsMap = ref<Record<string, KnowledgeBaseDocument[]>>({})
const showKBDialog = ref(false)
const editingKB = ref<KnowledgeBase | null>(null)
const kbForm = ref({ name: '', description: '' })

// AI 配置对话框
const showExtractDialog = ref(false)
const showGenerateDialog = ref(false)
const selectedKBIds = ref<string[]>([])

const loadProject = async () => {
  loading.value = true
  try {
    const { data } = await projectApi.get(props.id)
    project.value = data
  } catch {
    ElMessage.error('加载项目失败')
  } finally {
    loading.value = false
  }
}

const loadDocuments = async () => {
  try {
    const { data } = await documentApi.list(props.id)
    documents.value = data.items
  } catch {}
}

const loadTestPoints = async () => {
  try {
    const params: any = {
      skip: (tpPage.value.current - 1) * tpPage.value.size,
      limit: tpPage.value.size,
    }
    if (tpFilter.value.priority) params.priority = tpFilter.value.priority
    if (tpFilter.value.category) params.category = tpFilter.value.category
    const { data } = await testPointApi.list(props.id, params)
    testPoints.value = data.items
    tpPage.value.total = data.total
  } catch {}
}

const loadTestCases = async () => {
  try {
    const params: any = {
      skip: (tcPage.value.current - 1) * tcPage.value.size,
      limit: tcPage.value.size,
    }
    if (tcFilter.value.priority) params.priority = tcFilter.value.priority
    if (tcFilter.value.case_type) params.case_type = tcFilter.value.case_type
    const { data } = await testCaseApi.list(props.id, params)
    testCases.value = data.items
    tcPage.value.total = data.total
  } catch {}
}

// 分页与筛选
const onTpFilterChange = () => { tpPage.value.current = 1; loadTestPoints() }
const onTpSizeChange = () => { tpPage.value.current = 1; loadTestPoints() }
const onTcFilterChange = () => { tcPage.value.current = 1; loadTestCases() }
const onTcSizeChange = () => { tcPage.value.current = 1; loadTestCases() }

// 文档操作
const onUploadSuccess = () => {
  ElMessage.success('上传成功')
  loadDocuments()
}
const onUploadError = () => ElMessage.error('上传失败')
const beforeUpload = (file: File) => {
  const ext = file.name.split('.').pop()?.toLowerCase()
  if (!['pdf', 'docx', 'md'].includes(ext || '')) {
    ElMessage.warning('仅支持 PDF、DOCX、MD 格式')
    return false
  }
  return true
}
const onDocSelectionChange = (rows: Document[]) => {
  selectedDocIds.value = rows.map(r => r.id)
}
const viewDocument = async (doc: Document) => {
  try {
    const { data } = await documentApi.get(doc.id)
    previewDoc.value = data
    showDocPreview.value = true
  } catch { ElMessage.error('加载文档失败') }
}
const reparseDoc = async (doc: Document) => {
  try {
    await documentApi.reparse(doc.id)
    ElMessage.success('重新解析已触发')
    loadDocuments()
  } catch { ElMessage.error('重新解析失败') }
}
const deleteDoc = async (doc: Document) => {
  try {
    await ElMessageBox.confirm('确定删除该文档？', '确认')
    await documentApi.delete(doc.id)
    ElMessage.success('删除成功')
    loadDocuments()
  } catch {}
}

// AI 操作
const extractTestPoints = () => {
  selectedKBIds.value = []
  showExtractDialog.value = true
}

const confirmExtractTestPoints = async () => {
  showExtractDialog.value = false
  try {
    isExtracting.value = true
    const { data } = await aiApi.extractTestPoints(props.id, {
      document_ids: selectedDocIds.value,
      knowledge_base_ids: selectedKBIds.value.length > 0 ? selectedKBIds.value : undefined,
    })
    currentBatchId.value = data.id
    currentBatchType.value = 'extract'
    showProgress.value = true
    ElMessage.info('测试点提取已启动，可关闭弹窗继续其他操作')
  } catch (e: any) {
    isExtracting.value = false
    ElMessage.error(e.response?.data?.detail || 'AI提取失败')
  }
}

const generateCases = () => {
  selectedKBIds.value = []
  showGenerateDialog.value = true
}

const confirmGenerateCases = async () => {
  showGenerateDialog.value = false
  try {
    const generatingIds = [...selectedPointIds.value]
    isGeneratingCases.value = true
    const { data } = await aiApi.generateTestCases(props.id, {
      test_point_ids: generatingIds,
      knowledge_base_ids: selectedKBIds.value.length > 0 ? selectedKBIds.value : undefined,
    })
    currentBatchId.value = data.id
    currentBatchType.value = 'generate'
    showProgress.value = true
    // 重新加载测试点以获取后端设置的 generating 状态
    loadTestPoints()
    ElMessage.info('用例生成已启动，可关闭弹窗继续其他操作')
  } catch (e: any) {
    isGeneratingCases.value = false
    ElMessage.error(e.response?.data?.detail || '生成失败')
    // 回滚状态
    loadTestPoints()
  }
}

const onBatchCompleted = (status?: string, errorMessage?: string) => {
  // 重置按钮状态
  isExtracting.value = false
  isGeneratingCases.value = false
  // 刷新数据
  loadTestPoints()
  loadTestCases()
  loadProject()
  // 如果弹窗已关闭（后台运行模式），弹出通知提示完成
  if (!showProgress.value) {
    if (status === 'failed') {
      ElMessage.error(`生成失败：${errorMessage || '未知错误'}`)
    } else {
      const msg = currentBatchType.value === 'extract' ? '测试点提取完成' : '测试用例生成完成'
      ElMessage.success(msg)
    }
  }
}

// 测试点操作
const onPointSelectionChange = (rows: TestPoint[]) => {
  selectedPointIds.value = rows.map(r => r.id)
}
const editPoint = (point: TestPoint) => {
  editingPoint.value = point
  pointForm.value = {
    title: point.title, description: point.description,
    priority: point.priority || 'P2', category: point.category || 'functional',
    preconditions: point.preconditions || '', expected_result: point.expected_result || ''
  }
  showCreatePointDialog.value = true
}
const deletePoint = async (point: TestPoint) => {
  try {
    await ElMessageBox.confirm('确定删除该测试点？', '确认')
    await testPointApi.delete(point.id)
    ElMessage.success('删除成功')
    loadTestPoints()
  } catch {}
}
const batchDeletePoints = async () => {
  try {
    await ElMessageBox.confirm(`确定删除选中的 ${selectedPointIds.value.length} 个测试点？`, '确认')
    await testPointApi.batchDelete(selectedPointIds.value)
    ElMessage.success('批量删除成功')
    loadTestPoints()
  } catch {}
}
const submitPoint = async () => {
  if (!pointForm.value.title || !pointForm.value.description) {
    ElMessage.warning('请填写标题和描述')
    return
  }
  try {
    if (editingPoint.value) {
      await testPointApi.update(editingPoint.value.id, pointForm.value)
    } else {
      await testPointApi.create(props.id, pointForm.value)
    }
    ElMessage.success('操作成功')
    showCreatePointDialog.value = false
    editingPoint.value = null
    loadTestPoints()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '操作失败')
  }
}

// 测试用例操作
const editCase = (tc: TestCase) => {
  editingCase.value = tc
  caseForm.value = {
    title: tc.title, preconditions: tc.preconditions || '',
    priority: tc.priority || 'P2', status: tc.status || 'draft'
  }
  showEditCaseDialog.value = true
}
const deleteCase = async (tc: TestCase) => {
  try {
    await ElMessageBox.confirm('确定删除该测试用例？', '确认')
    await testCaseApi.delete(tc.id)
    ElMessage.success('删除成功')
    loadTestCases()
  } catch {}
}
const submitCase = async () => {
  if (!editingCase.value) return
  try {
    await testCaseApi.update(editingCase.value.id, caseForm.value)
    ElMessage.success('更新成功')
    showEditCaseDialog.value = false
    loadTestCases()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '更新失败')
  }
}
const exportExcel = async () => {
  try {
    const { data } = await testCaseApi.export(props.id)
    const url = window.URL.createObjectURL(new Blob([data]))
    const link = document.createElement('a')
    link.href = url
    link.download = `test_cases_${props.id}.xlsx`
    link.click()
    window.URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch {
    ElMessage.error('导出失败')
  }
}

// 知识库操作
const loadKnowledgeBases = async () => {
  try {
    const { data } = await knowledgeBaseApi.list(props.id)
    knowledgeBases.value = data.items
  } catch {}
}

const loadKBDocuments = async (kbId: string) => {
  try {
    const { data } = await knowledgeBaseApi.listDocuments(kbId)
    kbDocumentsMap.value[kbId] = data.items
  } catch {}
}

const onKBCollapseChange = (ids: string[]) => {
  for (const id of ids) {
    if (!kbDocumentsMap.value[id]) {
      loadKBDocuments(id)
    }
  }
}

const openCreateKBDialog = () => {
  editingKB.value = null
  kbForm.value = { name: '', description: '' }
  showKBDialog.value = true
}

const openEditKBDialog = (kb: KnowledgeBase) => {
  editingKB.value = kb
  kbForm.value = { name: kb.name, description: kb.description || '' }
  showKBDialog.value = true
}

const submitKB = async () => {
  if (!kbForm.value.name) {
    ElMessage.warning('请填写知识库名称')
    return
  }
  try {
    if (editingKB.value) {
      await knowledgeBaseApi.update(editingKB.value.id, kbForm.value)
    } else {
      await knowledgeBaseApi.create(props.id, kbForm.value)
    }
    ElMessage.success('操作成功')
    showKBDialog.value = false
    editingKB.value = null
    loadKnowledgeBases()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '操作失败')
  }
}

const deleteKB = async (kb: KnowledgeBase) => {
  try {
    await ElMessageBox.confirm(`确定删除知识库「${kb.name}」？其中的所有文档和向量数据将一并删除。`, '确认')
    await knowledgeBaseApi.delete(kb.id)
    ElMessage.success('删除成功')
    loadKnowledgeBases()
  } catch {}
}

const onKBUploadSuccess = (kbId: string) => {
  ElMessage.success('上传成功，正在处理文档...')
  loadKBDocuments(kbId)
  // 延迟刷新以等待后台处理
  setTimeout(() => {
    loadKBDocuments(kbId)
    loadKnowledgeBases()
  }, 3000)
}

const onKBUploadError = () => ElMessage.error('上传失败')

const deleteKBDoc = async (kbId: string, doc: KnowledgeBaseDocument) => {
  try {
    await ElMessageBox.confirm('确定删除该文档？', '确认')
    await knowledgeBaseApi.deleteDocument(doc.id)
    ElMessage.success('删除成功')
    loadKBDocuments(kbId)
    loadKnowledgeBases()
  } catch {}
}

const kbDocStatusType = (s: string) => ({ completed: 'success', failed: 'danger', processing: 'warning', pending: 'info' }[s] || 'info') as any
const kbDocStatusText = (s: string) => ({ completed: '已完成', failed: '失败', processing: '处理中', pending: '待处理' }[s] || s)

// 工具函数
const parseStatusType = (s: string) => ({ completed: 'success', failed: 'danger', parsing: 'warning', pending: 'info' }[s] || 'info') as any
const parseStatusText = (s: string) => ({ completed: '已完成', failed: '失败', parsing: '解析中', pending: '待解析' }[s] || s)
const priorityType = (p: string) => ({ P0: 'danger', P1: 'warning', P2: '', P3: 'info' }[p] || '') as any
const categoryText = (c: string) => ({ functional: '功能', edge_case: '边界', performance: '性能', security: '安全' }[c] || c)
const caseTypeText = (t: string) => ({ positive: '正向', negative: '反向', boundary: '边界', edge: '边缘' }[t] || t)
const tpStatusType = (s: string) => ({ active: 'success', generating: 'warning' }[s] || 'info') as any
const tpStatusText = (s: string) => ({ active: '已就绪', generating: '生成中' }[s] || s)
const statusType = (s: string) => ({ draft: 'info', review: 'warning', approved: 'success', generating: 'warning' }[s] || '') as any
const statusText = (s: string) => ({ draft: '草稿', review: '评审', approved: '通过', generating: '生成中' }[s] || s)

watch(activeTab, (tab) => {
  if (tab === 'documents') loadDocuments()
  else if (tab === 'testpoints') loadTestPoints()
  else if (tab === 'testcases') loadTestCases()
  else if (tab === 'knowledgebase') loadKnowledgeBases()
})

// 切换项目时重置状态并重新加载数据
watch(() => props.id, () => {
  // 停止旧项目的轮询
  stopResumePoll()
  // 重置 AI 生成状态
  isExtracting.value = false
  isGeneratingCases.value = false
  showProgress.value = false
  currentBatchId.value = ''
  currentBatchType.value = ''
  // 重新加载新项目数据
  loadProject()
  loadDocuments()
  loadTestPoints()
  loadTestCases()
  loadKnowledgeBases()
  checkRunningBatches()
})

// 后台静默轮询（用于页面切换后恢复）
let resumePollTimer: ReturnType<typeof setInterval> | null = null

const stopResumePoll = () => {
  if (resumePollTimer) {
    clearInterval(resumePollTimer)
    resumePollTimer = null
  }
}

const startResumePoll = (batchId: string) => {
  stopResumePoll()
  resumePollTimer = setInterval(async () => {
    try {
      const { data } = await aiApi.getBatchStatus(batchId)
      if (data.status !== 'running') {
        stopResumePoll()
        onBatchCompleted(data.status, data.error_message || '')
      }
    } catch {}
  }, 2000)
}

const checkRunningBatches = async () => {
  try {
    const { data: batches } = await aiApi.getRunningBatches(props.id)
    if (batches.length > 0) {
      const batch = batches[0]
      currentBatchId.value = batch.id
      currentBatchType.value = batch.batch_type === 'test_point_extraction' ? 'extract' : 'generate'
      if (currentBatchType.value === 'extract') {
        isExtracting.value = true
      } else {
        isGeneratingCases.value = true
      }
      // 静默后台轮询，不弹出进度弹窗
      startResumePoll(batch.id)
    }
  } catch {}
}

onMounted(() => {
  loadProject()
  loadDocuments()
  loadTestPoints()
  loadTestCases()
  loadKnowledgeBases()  // 预加载知识库列表（AI对话框需要用）
  checkRunningBatches()  // 检查是否有正在运行的批次
})

onUnmounted(stopResumePoll)
</script>

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
