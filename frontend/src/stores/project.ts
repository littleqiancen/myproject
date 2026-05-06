import { defineStore } from 'pinia'
import { ref } from 'vue'
import { projectApi } from '../api'
import type { Project } from '../types'

export const useProjectStore = defineStore('project', () => {
  const projects = ref<Project[]>([])
  const currentProject = ref<Project | null>(null)
  const loading = ref(false)

  const loadProjects = async () => {
    loading.value = true
    try {
      const { data } = await projectApi.list()
      projects.value = data.items
    } finally {
      loading.value = false
    }
  }

  const loadProject = async (id: string) => {
    const { data } = await projectApi.get(id)
    currentProject.value = data
  }

  return { projects, currentProject, loading, loadProjects, loadProject }
})
