'use client';

import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api';
import type { DashboardStats, Task } from '@/types/task';
import Link from 'next/link';
import TaskCard from '@/components/TaskCard';

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [pendingTasks, setPendingTasks] = useState<Task[]>([]);
  const [highPriorityTasks, setHighPriorityTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [statsData, pendingData, priorityData] = await Promise.all([
        apiClient.getStats(),
        apiClient.getTasks('pending_approval'),
        apiClient.getTasks('high_priority'),
      ]);

      setStats(statsData);
      setPendingTasks(pendingData);
      setHighPriorityTasks(priorityData);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Task Dashboard
        </h1>
        <p className="text-gray-600">
          Intelligent task management with automatic categorization
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Tasks"
          value={stats?.total_tasks || 0}
          icon="📊"
          color="blue"
        />
        <StatCard
          title="Pending Approval"
          value={stats?.pending_approval || 0}
          icon="🔒"
          color="yellow"
          href="/tasks?folder=pending_approval"
        />
        <StatCard
          title="High Priority"
          value={stats?.high_priority || 0}
          icon="⚠️"
          color="red"
          href="/tasks?folder=high_priority"
        />
        <StatCard
          title="Completed"
          value={stats?.done || 0}
          icon="✅"
          color="green"
          href="/tasks?folder=done"
        />
      </div>

      {/* Pending Approval Section */}
      {pendingTasks.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-bold text-gray-900">
              🔒 Awaiting Approval
            </h2>
            <Link
              href="/tasks?folder=pending_approval"
              className="text-primary-600 hover:text-primary-700 text-sm font-medium"
            >
              View All →
            </Link>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {pendingTasks.slice(0, 3).map((task) => (
              <TaskCard key={task.id} task={task} onAction={loadData} />
            ))}
          </div>
        </div>
      )}

      {/* High Priority Section */}
      {highPriorityTasks.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-bold text-gray-900">
              ⚠️ High Priority Tasks
            </h2>
            <Link
              href="/tasks?folder=high_priority"
              className="text-primary-600 hover:text-primary-700 text-sm font-medium"
            >
              View All →
            </Link>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {highPriorityTasks.slice(0, 3).map((task) => (
              <TaskCard key={task.id} task={task} onAction={loadData} />
            ))}
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">
          Quick Actions
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Link
            href="/create"
            className="flex items-center justify-center px-6 py-4 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
          >
            <span className="text-lg font-medium">➕ Create New Task</span>
          </Link>
          <Link
            href="/reports"
            className="flex items-center justify-center px-6 py-4 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
          >
            <span className="text-lg font-medium">📊 View CEO Report</span>
          </Link>
          <Link
            href="/tasks"
            className="flex items-center justify-center px-6 py-4 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
          >
            <span className="text-lg font-medium">📋 All Tasks</span>
          </Link>
        </div>
      </div>
    </div>
  );
}

function StatCard({
  title,
  value,
  icon,
  color,
  href,
}: {
  title: string;
  value: number;
  icon: string;
  color: 'blue' | 'yellow' | 'red' | 'green';
  href?: string;
}) {
  const colorClasses = {
    blue: 'bg-blue-50 border-blue-200 text-blue-700',
    yellow: 'bg-yellow-50 border-yellow-200 text-yellow-700',
    red: 'bg-red-50 border-red-200 text-red-700',
    green: 'bg-green-50 border-green-200 text-green-700',
  };

  const content = (
    <>
      <div className="flex items-center justify-between mb-2">
        <span className="text-3xl">{icon}</span>
        <span className="text-3xl font-bold">{value}</span>
      </div>
      <div className="text-sm font-medium text-gray-600">{title}</div>
    </>
  );

  if (href) {
    return (
      <Link
        href={href}
        className={`block p-6 border-2 rounded-lg transition-all hover:shadow-lg ${colorClasses[color]}`}
      >
        {content}
      </Link>
    );
  }

  return (
    <div className={`p-6 border-2 rounded-lg ${colorClasses[color]}`}>
      {content}
    </div>
  );
}
