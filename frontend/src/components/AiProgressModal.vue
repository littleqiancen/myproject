<template>
  <el-dialog
    :model-value="modelValue"
    title="AI 生成中"
    width="400px"
    :close-on-click-modal="true"
    :close-on-press-escape="true"
    :show-close="true"
    @update:model-value="onDialogChange"
  >
    <div style="text-align: center; padding: 20px 0;">
      <el-icon v-if="status === 'running'" class="is-loading" :size="48" color="var(--brand-primary)">
        <Loading />
      </el-icon>
      <el-icon v-else-if="status === 'completed'" :size="48" color="var(--el-color-success)">
        <CircleCheck />
      </el-icon>
      <el-icon v-else-if="status === 'failed'" :size="48" color="var(--el-color-danger)">
        <CircleClose />
      </el-icon>

      <p class="status-title" style="margin-top: 16px; font-size: 16px;">
        <template v-if="status === 'running'">正在生成，请稍候...</template>
        <template v-else-if="status === 'completed'">生成完成！</template>
        <template v-else-if="status === 'failed'">生成失败</template>
      </p>

      <p v-if="status === 'running'" class="status-hint" style="color: #909399; font-size: 13px;">
        可以关闭此窗口，生成将在后台继续进行
      </p>

      <p v-if="errorMessage" class="status-error" style="color: #f56c6c; font-size: 13px;">
        {{ errorMessage }}
      </p>

      <p v-if="tokenUsage" class="status-token" style="color: #909399; font-size: 12px;">
        Token 用量：{{ tokenUsage.total_tokens || 0 }}
      </p>
    </div>

    <template #footer>
      <el-button v-if="status === 'running'" @click="minimize">后台运行</el-button>
      <el-button v-else type="primary" @click="close">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch, onUnmounted } from 'vue'
import { Loading, CircleCheck, CircleClose } from '@element-plus/icons-vue'
import { aiApi } from '../api'

const props = defineProps<{
  modelValue: boolean
  batchId: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'completed': [status: string, errorMessage: string]
}>()

const status = ref('running')
const errorMessage = ref('')
const tokenUsage = ref<Record<string, number> | null>(null)
let pollTimer: ReturnType<typeof setInterval> | null = null

const pollStatus = async () => {
  if (!props.batchId) return
  try {
    const { data } = await aiApi.getBatchStatus(props.batchId)
    status.value = data.status
    errorMessage.value = data.error_message || ''
    tokenUsage.value = data.token_usage

    if (data.status !== 'running') {
      stopPolling()
      // 生成完成/失败时，无论弹窗是否打开都通知父组件刷新数据
      emit('completed', data.status, data.error_message || '')
    }
  } catch {
    // 忽略轮询错误
  }
}

const startPolling = () => {
  status.value = 'running'
  errorMessage.value = ''
  tokenUsage.value = null
  pollStatus()
  pollTimer = setInterval(pollStatus, 2000)
}

const stopPolling = () => {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

const minimize = () => {
  // 关闭弹窗但不停止轮询——继续后台监控
  emit('update:modelValue', false)
}

const close = () => {
  stopPolling()
  emit('update:modelValue', false)
  // 不再 emit('completed')——pollStatus 检测到完成时已经触发过
}

const onDialogChange = (visible: boolean) => {
  if (!visible) {
    if (status.value === 'running') {
      // 用户关闭弹窗但任务还在跑 → 只关弹窗，不停轮询
      emit('update:modelValue', false)
    } else {
      // 任务已完成/失败，关闭并清理
      stopPolling()
      emit('update:modelValue', false)
    }
  }
}

watch(() => props.modelValue, (visible) => {
  if (visible && props.batchId) {
    startPolling()
  }
  // 注意：不在 visible=false 时 stopPolling，让后台继续轮询
})

onUnmounted(stopPolling)
</script>

<style scoped>
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
