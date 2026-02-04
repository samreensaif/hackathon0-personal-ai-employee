export interface Task {
  id: string;
  title: string;
  description: string;
  status: string;
  priority: 'high' | 'normal' | 'low';
  category: string;
  created_at: string;
  processed_at?: string;
  folder: string;
}

export interface DashboardStats {
  total_tasks: number;
  pending_approval: number;
  high_priority: number;
  done: number;
  inbox: number;
  needs_action: number;
}

export interface TaskCreate {
  title: string;
  description: string;
  priority: 'high' | 'normal' | 'low';
}

export interface Report {
  filename: string;
  content: string;
  generated_at: string;
}

export interface LogEntry {
  timestamp: string;
  action: string;
  file: string;
  source?: string;
  details?: Record<string, any>;
}
