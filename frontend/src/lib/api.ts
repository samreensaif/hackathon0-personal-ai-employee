import axios from 'axios';
import type { Task, DashboardStats, TaskCreate, Report, LogEntry } from '@/types/task';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const apiClient = {
  // Health check
  async healthCheck() {
    const response = await api.get('/api/health');
    return response.data;
  },

  // Dashboard stats
  async getStats(): Promise<DashboardStats> {
    const response = await api.get<DashboardStats>('/api/stats');
    return response.data;
  },

  // Tasks
  async getTasks(folder?: string, priority?: string): Promise<Task[]> {
    const params: any = {};
    if (folder) params.folder = folder;
    if (priority) params.priority = priority;

    const response = await api.get<Task[]>('/api/tasks', { params });
    return response.data;
  },

  async getTask(taskId: string): Promise<Task> {
    const response = await api.get<Task>(`/api/tasks/${taskId}`);
    return response.data;
  },

  async createTask(task: TaskCreate): Promise<Task> {
    const response = await api.post<Task>('/api/tasks', task);
    return response.data;
  },

  async approveTask(taskId: string) {
    const response = await api.post(`/api/tasks/${taskId}/action`, {
      action: 'approve',
    });
    return response.data;
  },

  async rejectTask(taskId: string) {
    const response = await api.post(`/api/tasks/${taskId}/action`, {
      action: 'reject',
    });
    return response.data;
  },

  async completeTask(taskId: string) {
    const response = await api.post(`/api/tasks/${taskId}/action`, {
      action: 'complete',
    });
    return response.data;
  },

  // Reports
  async getLatestReport(): Promise<Report> {
    const response = await api.get<Report>('/api/reports/latest');
    return response.data;
  },

  async generateReport() {
    const response = await api.post('/api/reports/generate');
    return response.data;
  },

  // Logs
  async getTodayLogs(): Promise<{ date: string; logs: LogEntry[] }> {
    const response = await api.get('/api/logs/today');
    return response.data;
  },
};
