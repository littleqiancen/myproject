import { defineStore } from 'pinia'
import { ref } from 'vue'
import { testPointApi } from '../api'
import type { TestPoint } from '../types'

export const useTestPointStore = defineStore('testPoint', () => {
  const testPoints = ref<TestPoint[]>([])

  const loadTestPoints = async (projectId: string, params?: any) => {
    const { data } = await testPointApi.list(projectId, params)
    testPoints.value = data.items
  }

  return { testPoints, loadTestPoints }
})
