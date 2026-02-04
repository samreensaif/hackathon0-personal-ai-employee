'use client';

import { useState } from 'react';
import { apiClient } from '@/lib/api';
import type { Task } from '@/types/task';
import { formatDistanceToNow } from 'date-fns';

interface TaskCardProps {
  task: Task;
  onAction?: () => void;
  showActions?: boolean;
}

export default function TaskCard({ task, onAction, showActions = true }: TaskCardProps) {
  const [loading, setLoading] = useState(false);

  const handleApprove = async () => {
    if (!confirm('Approve this task?')) return;

    try {
      setLoading(true);
      await apiClient.approveTask(task.id);
      onAction?.();
    } catch (error) {
      console.error('Error approving task:', error);
      alert('Failed to approve task');
    } finally {
      setLoading(false);
    }
  };

  const handleReject = async () => {
    if (!confirm('Reject this task?')) return;

    try {
      setLoading(true);
      await apiClient.rejectTask(task.id);
      onAction?.();
    } catch (error) {
      console.error('Error rejecting task:', error);
      alert('Failed to reject task');
    } finally {
      setLoading(false);
    }
  };

  const handleComplete = async () => {
    if (!confirm('Mark this task as complete?')) return;

    try {
      setLoading(true);
      await apiClient.completeTask(task.id);
      onAction?.();
    } catch (error) {
      console.error('Error completing task:', error);
      alert('Failed to complete task');
    } finally {
      setLoading(false);
    }
  };

  const priorityColors = {
    high: 'bg-red-100 text-red-800',
    normal: 'bg-blue-100 text-blue-800',
    low: 'bg-gray-100 text-gray-800',
  };

  const folderIcons = {
    inbox: '📥',
    needs_action: '📋',
    high_priority: '⚠️',
    pending_approval: '🔒',
    done: '✅',
    approved: '✅',
    rejected: '🚫',
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-2">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xl">
              {folderIcons[task.folder as keyof typeof folderIcons] || '📄'}
            </span>
            <h3 className="font-semibold text-gray-900 line-clamp-1">
              {task.title}
            </h3>
          </div>
          <p className="text-sm text-gray-600 line-clamp-2 mb-2">
            {task.description.split('\n').slice(0, 2).join(' ')}
          </p>
        </div>
      </div>

      <div className="flex items-center gap-2 mb-3">
        <span
          className={`px-2 py-1 rounded text-xs font-medium ${
            priorityColors[task.priority as keyof typeof priorityColors]
          }`}
        >
          {task.priority.toUpperCase()}
        </span>
        <span className="px-2 py-1 rounded text-xs font-medium bg-gray-100 text-gray-700">
          {task.category}
        </span>
      </div>

      <div className="text-xs text-gray-500 mb-3">
        Created {task.created_at ? formatDistanceToNow(new Date(task.created_at), { addSuffix: true }) : 'Unknown'}
      </div>

      {showActions && task.folder === 'pending_approval' && (
        <div className="flex gap-2">
          <button
            onClick={handleApprove}
            disabled={loading}
            className="flex-1 px-3 py-2 bg-green-600 text-white text-sm font-medium rounded hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            ✓ Approve
          </button>
          <button
            onClick={handleReject}
            disabled={loading}
            className="flex-1 px-3 py-2 bg-red-600 text-white text-sm font-medium rounded hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            ✕ Reject
          </button>
        </div>
      )}

      {showActions && (task.folder === 'high_priority' || task.folder === 'needs_action') && (
        <button
          onClick={handleComplete}
          disabled={loading}
          className="w-full px-3 py-2 bg-primary-600 text-white text-sm font-medium rounded hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          ✓ Mark Complete
        </button>
      )}
    </div>
  );
}
