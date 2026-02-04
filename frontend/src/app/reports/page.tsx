'use client';

import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api';
import type { Report } from '@/types/task';
import ReactMarkdown from 'react-markdown';

export default function ReportsPage() {
  const [report, setReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    loadReport();
  }, []);

  const loadReport = async () => {
    try {
      setLoading(true);
      const data = await apiClient.getLatestReport();
      setReport(data);
    } catch (error) {
      console.error('Error loading report:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateReport = async () => {
    if (!confirm('Generate a new CEO briefing? This may take a few seconds.')) {
      return;
    }

    try {
      setGenerating(true);
      await apiClient.generateReport();
      await loadReport();
      alert('Report generated successfully!');
    } catch (error) {
      console.error('Error generating report:', error);
      alert('Failed to generate report');
    } finally {
      setGenerating(false);
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
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              CEO Weekly Briefing
            </h1>
            <p className="text-gray-600">
              Executive summary of task activity and system performance
            </p>
          </div>
          <button
            onClick={handleGenerateReport}
            disabled={generating}
            className="px-6 py-3 bg-green-600 text-white font-medium rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {generating ? 'Generating...' : '🔄 Generate New Report'}
          </button>
        </div>
      </div>

      {/* Report */}
      {report ? (
        <div className="bg-white rounded-lg shadow-md p-8">
          <div className="mb-6 pb-6 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-sm font-medium text-gray-500">Report</h2>
                <p className="text-lg font-semibold text-gray-900">
                  {report.filename}
                </p>
              </div>
              <div className="text-right">
                <h2 className="text-sm font-medium text-gray-500">Generated</h2>
                <p className="text-lg font-semibold text-gray-900">
                  {new Date(report.generated_at).toLocaleString()}
                </p>
              </div>
            </div>
          </div>

          <div className="prose prose-lg max-w-none">
            <ReactMarkdown
              components={{
                h1: ({ children }) => (
                  <h1 className="text-3xl font-bold text-gray-900 mb-4 mt-8">
                    {children}
                  </h1>
                ),
                h2: ({ children }) => (
                  <h2 className="text-2xl font-bold text-gray-900 mb-3 mt-6">
                    {children}
                  </h2>
                ),
                h3: ({ children }) => (
                  <h3 className="text-xl font-semibold text-gray-900 mb-2 mt-4">
                    {children}
                  </h3>
                ),
                p: ({ children }) => (
                  <p className="text-gray-700 mb-4 leading-relaxed">
                    {children}
                  </p>
                ),
                ul: ({ children }) => (
                  <ul className="list-disc list-inside mb-4 space-y-2">
                    {children}
                  </ul>
                ),
                li: ({ children }) => (
                  <li className="text-gray-700">{children}</li>
                ),
                code: ({ children }) => (
                  <code className="bg-gray-100 px-2 py-1 rounded text-sm font-mono">
                    {children}
                  </code>
                ),
                pre: ({ children }) => (
                  <pre className="bg-gray-100 p-4 rounded-lg overflow-x-auto mb-4">
                    {children}
                  </pre>
                ),
                hr: () => <hr className="my-6 border-gray-300" />,
                strong: ({ children }) => (
                  <strong className="font-semibold text-gray-900">
                    {children}
                  </strong>
                ),
              }}
            >
              {report.content}
            </ReactMarkdown>
          </div>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-md p-12 text-center">
          <div className="text-6xl mb-4">📊</div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            No report available
          </h3>
          <p className="text-gray-600 mb-6">
            Generate your first CEO briefing to see executive insights
          </p>
          <button
            onClick={handleGenerateReport}
            disabled={generating}
            className="px-6 py-3 bg-primary-600 text-white font-medium rounded-md hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {generating ? 'Generating...' : 'Generate Report'}
          </button>
        </div>
      )}
    </div>
  );
}
