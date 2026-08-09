'use client'
import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { Check, X, ArrowRight } from 'lucide-react';
import AdminProtectedPage from '../components/AdminProtectedPage';
import { getReviewQueue, approveVideo, rejectVideo } from '@/lib/api/videos';

interface ReviewVideo {
  id: string;
  athlete_name: string;
  athlete_email: string;
  competition: string;
  workout: string;
  status: string;
  raw_status?: string;
  created_at: string;
  score: {
    status: string | null;
    total_reps: number | null;
    good_reps: number | null;
    no_reps: number | null;
    is_valid: boolean;
  } | null;
}

const TABS: { value: string; label: string }[] = [
  { value: '', label: 'All' },
  { value: 'S', label: 'Pending' },
  { value: 'A', label: 'Approved' },
  { value: 'R', label: 'Rejected' },
];

function StatusBadge({ label }: { label: string }) {
  const styles: Record<string, string> = {
    Approved: 'bg-green-50 text-green-700 border-green-100',
    Rejected: 'bg-red-50 text-red-700 border-red-100',
    Submitted: 'bg-gray-50 text-gray-600 border-gray-100',
  };
  return (
    <span className={`text-xs font-medium px-2.5 py-1 rounded-full border ${styles[label] ?? 'bg-gray-50 text-gray-500 border-gray-100'}`}>
      {label}
    </span>
  );
}

export default function ReviewQueuePage() {
  const [videos, setVideos] = useState<ReviewVideo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tab, setTab] = useState('');
  const [actingOn, setActingOn] = useState<string | null>(null);

  const fetchQueue = useCallback(async () => {
    try {
      setLoading(true);
      const data = await getReviewQueue(tab ? { status: tab } : {});
      setVideos(data.results ?? data);
      setError(null);
    } catch {
      setError('Failed to load submissions.');
    } finally {
      setLoading(false);
    }
  }, [tab]);

  useEffect(() => {
    fetchQueue();
  }, [fetchQueue]);

  const handleDecision = async (id: string, action: 'approve' | 'reject') => {
    setActingOn(id);
    try {
      const updated = action === 'approve' ? await approveVideo(id) : await rejectVideo(id);
      setVideos((vs) => vs.map((v) => (v.id === id ? { ...v, status: updated.status === 'A' ? 'Approved' : 'Rejected' } : v)));
    } catch {
      setError(`Failed to ${action} submission.`);
    } finally {
      setActingOn(null);
    }
  };

  return (
    <AdminProtectedPage>
      <main className="min-h-screen bg-white">
        <div className="max-w-6xl mx-auto px-6 py-12">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 tracking-tight">Submission review</h1>
            <p className="text-sm text-gray-500 mt-1">Review athlete video submissions and their AI-judged scores.</p>
          </div>

          <div className="flex items-center gap-1 mb-6 border-b border-gray-100">
            {TABS.map((t) => (
              <button
                key={t.value}
                onClick={() => setTab(t.value)}
                className={`px-4 py-2.5 text-sm font-medium border-b-2 -mb-px transition-colors ${
                  tab === t.value
                    ? 'border-gray-900 text-gray-900'
                    : 'border-transparent text-gray-400 hover:text-gray-700'
                }`}
              >
                {t.label}
              </button>
            ))}
          </div>

          {error && (
            <div className="mb-5 px-4 py-3 bg-red-50 border border-red-100 text-red-600 text-sm rounded-lg">{error}</div>
          )}

          {loading ? (
            <div className="flex items-center gap-2 text-sm text-gray-400 py-8">
              <div className="w-4 h-4 border-2 border-gray-200 border-t-gray-500 rounded-full animate-spin" />
              Loading submissions…
            </div>
          ) : videos.length === 0 ? (
            <div className="border border-dashed border-gray-200 rounded-xl p-10 text-center">
              <p className="text-sm text-gray-400">No submissions here.</p>
            </div>
          ) : (
            <div className="divide-y divide-gray-100 border border-gray-100 rounded-xl overflow-hidden">
              {videos.map((video) => (
                <div key={video.id} className="flex items-center justify-between px-5 py-4 hover:bg-gray-50 transition-colors">
                  <div className="flex-1 min-w-0 mr-4">
                    <div className="flex items-center gap-3 mb-1">
                      <p className="text-sm font-medium text-gray-900">{video.athlete_name || video.athlete_email}</p>
                      <StatusBadge label={video.status} />
                    </div>
                    <p className="text-xs text-gray-400">
                      {video.workout} · {video.competition} · {new Date(video.created_at).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })}
                    </p>
                    <div className="flex items-center gap-4 mt-2">
                      <span className="text-xs text-gray-500">
                        Good: <strong className="text-green-600">{video.score?.good_reps ?? '—'}</strong>
                      </span>
                      <span className="text-xs text-gray-500">
                        Total: <strong className="text-gray-800">{video.score?.total_reps ?? '—'}</strong>
                      </span>
                      <span className="text-xs text-gray-500">
                        No-reps: <strong className="text-red-500">{video.score?.no_reps ?? '—'}</strong>
                      </span>
                      <span className="text-xs text-gray-500">
                        Valid: <strong className="text-gray-800">{video.score?.is_valid ? 'Yes' : 'No'}</strong>
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <button
                      onClick={() => handleDecision(video.id, 'approve')}
                      disabled={actingOn === video.id || video.status === 'Approved'}
                      className="p-2 text-gray-400 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
                      aria-label="Approve"
                    >
                      <Check size={16} />
                    </button>
                    <button
                      onClick={() => handleDecision(video.id, 'reject')}
                      disabled={actingOn === video.id || video.status === 'Rejected'}
                      className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
                      aria-label="Reject"
                    >
                      <X size={16} />
                    </button>
                    <Link
                      href={`/video/${video.id}`}
                      className="p-2 text-gray-300 hover:text-gray-700 transition-colors rounded-lg hover:bg-gray-100"
                      aria-label="View details"
                    >
                      <ArrowRight size={14} />
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </AdminProtectedPage>
  );
}
