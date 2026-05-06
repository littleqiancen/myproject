import { defineStore } from 'pinia'
import { ref } from 'vue'
import { knowledgeBaseApi } from '../api'
import type { KnowledgeBase, KnowledgeBaseDocument } from '../types'

export const useKnowledgeBaseStore = defineStore('knowledgeBase', () => {
  const knowledgeBases = ref<KnowledgeBase[]>([])
  const kbDocuments = ref<Record<string, KnowledgeBaseDocument[]>>({})
  const loading = ref(false)

  const loadKnowledgeBases = async (projectId: string) => {
    loading.value = true
    try {
      const { data } = await knowledgeBaseApi.list(projectId)
      knowledgeBases.value = data.items
    } finally {
      loading.value = false
    }
  }

  const loadKBDocuments = async (kbId: string) => {
    const { data } = await knowledgeBaseApi.listDocuments(kbId)
    kbDocuments.value[kbId] = data.items
  }

  return { knowledgeBases, kbDocuments, loading, loadKnowledgeBases, loadKBDocuments }
})
