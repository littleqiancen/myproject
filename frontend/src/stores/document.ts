import { defineStore } from 'pinia'
import { ref } from 'vue'
import { documentApi } from '../api'
import type { Document } from '../types'

export const useDocumentStore = defineStore('document', () => {
  const documents = ref<Document[]>([])

  const loadDocuments = async (projectId: string) => {
    const { data } = await documentApi.list(projectId)
    documents.value = data.items
  }

  return { documents, loadDocuments }
})
