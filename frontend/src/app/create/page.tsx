'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { apiClient } from '@/lib/api';

export default function CreateTaskPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    priority: 'normal' as 'high' | 'normal' | 'low',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.title.trim() || !formData.description.trim()) {
      alert('Please fill in all fields');
      return;
    }

    try {
      setLoading(true);
      await apiClient.createTask(formData);
      alert('Task created successfully!');
      router.push('/');
    } catch (error) {
      console.error('Error creating task:', error);
      alert('Failed to create task');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Create New Task
        </h1>
        <p className="text-gray-600">
          Add a new task to your AI Employee system
        </p>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-md p-6 space-y-6">
        {/* Title */}
        <div>
          <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-2">
            Task Title *
          </label>
          <input
            type="text"
            id="title"
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            placeholder="E.g., Send quarterly report to stakeholders"
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            required
          />
        </div>

        {/* Description */}
        <div>
          <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
            Description *
          </label>
          <textarea
            id="description"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            placeholder="Provide detailed information about the task..."
            rows={8}
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            required
          />
          <p className="mt-2 text-sm text-gray-500">
            💡 Tip: Include keywords like "urgent", "email", or "payment" for automatic categorization
          </p>
        </div>

        {/* Priority */}
        <div>
          <label htmlFor="priority" className="block text-sm font-medium text-gray-700 mb-2">
            Priority Level
          </label>
          <select
            id="priority"
            value={formData.priority}
            onChange={(e) => setFormData({ ...formData, priority: e.target.value as any })}
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="high">High - Urgent attention required</option>
            <option value="normal">Normal - Standard priority</option>
            <option value="low">Low - Can be done later</option>
          </select>
        </div>

        {/* Auto-categorization Info */}
        <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
          <h3 className="font-semibold text-blue-900 mb-2">
            🤖 Auto-Categorization
          </h3>
          <p className="text-sm text-blue-800 mb-2">
            Your task will be automatically categorized based on keywords:
          </p>
          <ul className="text-sm text-blue-800 space-y-1 list-disc list-inside">
            <li><strong>Auto-complete:</strong> reminder, note, FYI → Done ✅</li>
            <li><strong>Approval required:</strong> email, payment, send → Pending 🔒</li>
            <li><strong>High priority:</strong> urgent, ASAP, critical → Priority ⚠️</li>
          </ul>
        </div>

        {/* Buttons */}
        <div className="flex gap-4">
          <button
            type="submit"
            disabled={loading}
            className="flex-1 px-6 py-3 bg-primary-600 text-white font-medium rounded-md hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? 'Creating...' : '✓ Create Task'}
          </button>
          <button
            type="button"
            onClick={() => router.push('/')}
            className="px-6 py-3 bg-gray-200 text-gray-700 font-medium rounded-md hover:bg-gray-300 transition-colors"
          >
            Cancel
          </button>
        </div>
      </form>

      {/* Examples */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Example Tasks
        </h2>
        <div className="space-y-3">
          <ExampleTask
            title="Reminder: Review Q1 report"
            description="FYI - Review the Q1 financial report when available"
            category="Will auto-complete ✅"
          />
          <ExampleTask
            title="URGENT: Server maintenance"
            description="Critical server issue requires immediate attention"
            category="High priority ⚠️"
          />
          <ExampleTask
            title="Send invoice to client"
            description="Send payment invoice #12345 to client via email"
            category="Requires approval 🔒"
          />
        </div>
      </div>
    </div>
  );
}

function ExampleTask({
  title,
  description,
  category,
}: {
  title: string;
  description: string;
  category: string;
}) {
  return (
    <div className="border border-gray-200 rounded-md p-3">
      <div className="font-medium text-gray-900 mb-1">{title}</div>
      <div className="text-sm text-gray-600 mb-2">{description}</div>
      <div className="text-xs text-primary-600 font-medium">{category}</div>
    </div>
  );
}
