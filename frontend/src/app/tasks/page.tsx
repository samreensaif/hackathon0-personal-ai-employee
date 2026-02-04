'use client';

import { useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { apiClient } from '@/lib/api';
import type { Task } from '@/types/task';
import TaskCard from '@/components/TaskCard';

export default function TasksPage() {
  const searchParams = useSearchParams();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterFolder, setFilterFolder] = useState(searchParams.get('folder') || '');
  const [filterPriority, setFilterPriority] = useState(searchParams.get('priority') || '');

  useEffect(() => {
    loadTasks();
  }, [filterFolder, filterPriority]);

  const loadTasks = async () => {
    try {
      setLoading(true);
      const data = await apiClient.getTasks(
        filterFolder || undefined,
        filterPriority || undefined
      );
      setTasks(data);
    } catch (error) {
      console.error('Error loading tasks:', error);
    } finally {
      setLoading(false);
    }
  };

  const folders = [
    { value: '', label: 'All Folders' },
    { value: 'inbox', label: '📥 Inbox' },
    { value: 'needs_action', label: '📋 Needs Action' },
    { value: 'high_priority', label: '⚠️ High Priority' },
    { value: 'pending_approval', label: '🔒 Pending Approval' },
    { value: 'done', label: '✅ Done' },
    { value: 'approved', label: '✅ Approved' },
    { value: 'rejected', label: '🚫 Rejected' },
  ];

  const priorities = [
    { value: '', label: 'All Priorities' },
    { value: 'high', label: 'High' },
    { value: 'normal', label: 'Normal' },
    { value: 'low', label: 'Low' },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">All Tasks</h1>
        <p className="text-gray-600">
          View and manage all tasks across different folders
        </p>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Filters</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Folder
            </label>
            <select
              value={filterFolder}
              onChange={(e) => setFilterFolder(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              {folders.map((folder) => (
                <option key={folder.value} value={folder.value}>
                  {folder.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Priority
            </label>
            <select
              value={filterPriority}
              onChange={(e) => setFilterPriority(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              {priorities.map((priority) => (
                <option key={priority.value} value={priority.value}>
                  {priority.label}
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-end">
            <button
              onClick={() => {
                setFilterFolder('');
                setFilterPriority('');
              }}
              className="w-full px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
            >
              Clear Filters
            </button>
          </div>
        </div>

        <div className="mt-4 text-sm text-gray-600">
          Showing {tasks.length} task{tasks.length !== 1 ? 's' : ''}
        </div>
      </div>

      {/* Tasks Grid */}
      {loading ? (
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      ) : tasks.length === 0 ? (
        <div className="bg-white rounded-lg shadow-md p-12 text-center">
          <div className="text-6xl mb-4">📭</div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            No tasks found
          </h3>
          <p className="text-gray-600">
            {filterFolder || filterPriority
              ? 'Try adjusting your filters'
              : 'Create a new task to get started'}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {tasks.map((task) => (
            <TaskCard key={task.id} task={task} onAction={loadTasks} />
          ))}
        </div>
      )}
    </div>
  );
}
