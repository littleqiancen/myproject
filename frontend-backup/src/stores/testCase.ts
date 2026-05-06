import { defineStore } from 'pinia'
import { ref } from 'vue'
import { testCaseApi } from '../api'
import type { TestCase } from '../types'

export const useTestCaseStore = defineStore('testCase', () => {
  const testCases = ref<TestCase[]>([])

  const loadTestCases = async (projectId: string, params?: any) => {
    const { data } = await testCaseApi.list(projectId, params)
    testCases.value = data.items
  }

  return { testCases, loadTestCases }
})
