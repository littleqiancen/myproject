<template>
  <div>
    <h2 style="margin-top: 0;">系统设置</h2>

    <el-card style="margin-bottom: 20px;">
      <template #header><span style="font-weight: bold;">LLM 模型配置</span></template>

      <el-form :model="form" label-width="160px">
        <el-form-item label="API Base URL">
          <el-input
            v-model="form.llm_api_base"
            placeholder="留空使用官方地址，或输入自定义代理地址（如 https://api.example.com/v1）"
            clearable
          />
        </el-form-item>
        <el-form-item label="默认模型">
          <el-select
            v-model="form.default_llm_model"
            style="width: 100%;"
            filterable
            allow-create
            default-first-option
            placeholder="选择预设模型或输入自定义模型名称"
          >
            <el-option
              v-for="model in models"
              :key="model.id"
              :label="`${model.name} (${model.provider})`"
              :value="model.id"
            />
          </el-select>
          <div style="color: #909399; font-size: 12px; margin-top: 4px;">
            可直接输入自定义模型名称，如 openai/gpt-4o、deepseek/deepseek-chat 等
          </div>
        </el-form-item>
        <el-form-item label="OpenAI API Key">
          <el-input
            v-model="form.openai_api_key"
            type="password"
            show-password
            placeholder="请输入 OpenAI / DeepSeek 等兼容 API Key"
          />
          <div style="color: #909399; font-size: 12px; margin-top: 4px;">
            适用于 OpenAI、DeepSeek 等 OpenAI 兼容模型
          </div>
        </el-form-item>
        <el-form-item label="Anthropic API Key">
          <el-input
            v-model="form.anthropic_api_key"
            type="password"
            show-password
            placeholder="请输入 Anthropic API Key"
          />
          <div style="color: #909399; font-size: 12px; margin-top: 4px;">
            适用于 Claude 系列模型
          </div>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card style="margin-bottom: 20px;">
      <template #header><span style="font-weight: bold;">飞书通知配置</span></template>

      <el-form :model="form" label-width="160px">
        <el-form-item label="Webhook URL">
          <el-input v-model="form.feishu_webhook_url" placeholder="请输入飞书机器人 Webhook URL" />
        </el-form-item>
        <el-form-item label="签名密钥">
          <el-input v-model="form.feishu_webhook_secret" type="password" show-password placeholder="可选" />
        </el-form-item>
        <el-form-item>
          <el-button @click="testWebhook" :loading="testing">测试连接</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-button type="primary" @click="saveSettings" :loading="saving" size="large">保存设置</el-button>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { settingsApi, aiApi, notificationApi } from '../api'
import type { AppSettings, LLMModel } from '../types'

const settings = ref<AppSettings | null>(null)
const models = ref<LLMModel[]>([])
const saving = ref(false)
const testing = ref(false)

const form = ref({
  default_llm_model: '',
  llm_api_base: '',
  openai_api_key: '',
  anthropic_api_key: '',
  feishu_webhook_url: '',
  feishu_webhook_secret: '',
})

const loadSettings = async () => {
  try {
    const [settingsRes, modelsRes] = await Promise.all([
      settingsApi.get(),
      aiApi.getModels(),
    ])
    settings.value = settingsRes.data
    models.value = modelsRes.data
    form.value.default_llm_model = settingsRes.data.default_llm_model
    form.value.llm_api_base = settingsRes.data.llm_api_base
    form.value.openai_api_key = settingsRes.data.openai_api_key || ''
    form.value.anthropic_api_key = settingsRes.data.anthropic_api_key || ''
    form.value.feishu_webhook_url = settingsRes.data.feishu_webhook_url
    form.value.feishu_webhook_secret = settingsRes.data.feishu_webhook_secret
  } catch {
    ElMessage.error('加载设置失败')
  }
}

const saveSettings = async () => {
  saving.value = true
  try {
    const data: any = {
      default_llm_model: form.value.default_llm_model,
      llm_api_base: form.value.llm_api_base,
      openai_api_key: form.value.openai_api_key || undefined,
      anthropic_api_key: form.value.anthropic_api_key || undefined,
      feishu_webhook_url: form.value.feishu_webhook_url,
      feishu_webhook_secret: form.value.feishu_webhook_secret,
    }

    const { data: updated } = await settingsApi.update(data)
    settings.value = updated
    // 用返回的脱敏值更新表单
    form.value.openai_api_key = updated.openai_api_key || ''
    form.value.anthropic_api_key = updated.anthropic_api_key || ''
    // 重新加载模型列表（自定义模型可能已添加）
    const modelsRes = await aiApi.getModels()
    models.value = modelsRes.data
    ElMessage.success('设置已保存')
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

const testWebhook = async () => {
  if (!form.value.feishu_webhook_url) {
    ElMessage.warning('请先输入 Webhook URL')
    return
  }
  testing.value = true
  try {
    await notificationApi.test(form.value.feishu_webhook_url, form.value.feishu_webhook_secret || undefined)
    ElMessage.success('测试消息发送成功')
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '测试失败')
  } finally {
    testing.value = false
  }
}

onMounted(loadSettings)
</script>
