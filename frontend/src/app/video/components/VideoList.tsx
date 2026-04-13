'use client'
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { getVideos, deleteVideo } from "@/lib/api/videos";
import { Trash2, ArrowRight } from 'lucide-react';

export interface BreakdownSet {
  round: number;
  sequence: number;
  movement: string;
  reps: number;
  no_reps: number;
  expected_reps: number | null;
  advance_reason: string;
}

export interface ScoreBreakdown {
  id: number;
  is_good_rep: boolean;
  movement: string;
  no_rep_reason: string | null;
  rep_number: number | null;
  rep_timestamp: number | null;
  created_at: string;
}

export interface Score {
  is_valid: boolean;
  total_reps: number | null;
  no_reps: number | null;
  is_scaled: boolean;
  score: string;
  status: string | null;
  movement_breakdown: BreakdownSet[];
  score_breakdown: ScoreBreakdown[];
}

export interface Video {
  id: string;
  competition: string;
  workout: string;
  score: Score | null;
  created_at: string;
  status: string;
  urlPath: string | null;
}

function StatusBadge({ status }: { status: string | null }) {
  const styles: Record<string, string> = {
    complete: 'bg-green-50 text-green-700 border-green-100',
    processing: 'bg-yellow-50 text-yellow-700 border-yellow-100',
    failed: 'bg-red-50 text-red-700 border-red-100',
  };
  const label = status ?? 'pending';
  return (
    <span className={`text-xs font-medium px-2.5 py-1 rounded-full border ${styles[label] ?? 'bg-gray-50 text-gray-500 border-gray-100'}`}>
      {label.charAt(0).toUpperCase() + label.slice(1)}
    </span>
  );
}

function DeleteModal({ onConfirm, onCancel, deleting }: { onConfirm: () => void; onCancel: () => void; deleting: boolean }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/30" onClick={onCancel} />
      <div className="relative bg-white rounded-xl shadow-lg p-6 w-full max-w-sm mx-4">
        <h2 className="text-sm font-semibold text-gray-900 mb-2">Delete video?</h2>
        <p className="text-sm text-gray-500 mb-6">This action cannot be undone.</p>
        <div className="flex justify-end gap-3">
          <button
            onClick={onCancel}
            disabled={deleting}
            className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900 transition-colors disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            disabled={deleting}
            className="px-4 py-2 text-sm font-medium bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {deleting ? 'Deleting…' : 'Delete'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default function VideoList() {
  const [videos, setVideos] = useState<Video[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [pendingDeleteId, setPendingDeleteId] = useState<string | null>(null);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    fetchVideos();
  }, []);

  const fetchVideos = async () => {
    try {
      setLoading(true);
      const data = await getVideos();
      setVideos(data.results);
      setError(null);
    } catch (err) {
      setError('Failed to load videos.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteClick = (id: string, e: React.MouseEvent) => {
    e.preventDefault();
    setPendingDeleteId(id);
  };

  const handleDeleteConfirm = async () => {
    if (!pendingDeleteId) return;
    setDeleting(true);
    try {
      await deleteVideo(pendingDeleteId);
      setVideos(videos.filter((v) => v.id !== pendingDeleteId));
      setPendingDeleteId(null);
    } catch (err) {
      console.error(err);
      setError('Failed to delete video.');
      setPendingDeleteId(null);
    } finally {
      setDeleting(false);
    }
  };

  if (loading) return (
    <div className="flex items-center gap-2 text-sm text-gray-400 py-8">
      <div className="w-4 h-4 border-2 border-gray-200 border-t-gray-500 rounded-full animate-spin" />
      Loading videos…
    </div>
  );
  if (error) return <p className="text-sm text-red-500 py-4">{error}</p>;

  if (videos.length === 0) {
    return (
      <div className="border border-dashed border-gray-200 rounded-xl p-10 text-center">
        <p className="text-sm text-gray-400">No videos submitted yet.</p>
      </div>
    );
  }

  return (
    <>
      {pendingDeleteId && (
        <DeleteModal
          onConfirm={handleDeleteConfirm}
          onCancel={() => setPendingDeleteId(null)}
          deleting={deleting}
        />
      )}
      <div className="divide-y divide-gray-100 border border-gray-100 rounded-xl overflow-hidden">
        {videos.map((video) => (
          <Link
            key={video.id}
            href={`/video/${video.id}`}
            className="flex items-center justify-between px-5 py-4 hover:bg-gray-50 transition-colors group"
          >
            <div className="flex-1 min-w-0 mr-4">
              <div className="flex items-center gap-3 mb-1">
                <p className="text-sm font-medium text-gray-900 truncate">{video.workout}</p>
                <StatusBadge status={video.score?.status ?? null} />
              </div>
              <p className="text-xs text-gray-400">
                {video.competition} · {new Date(video.created_at).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })}
              </p>
              <div className="flex items-center gap-4 mt-2">
                <span className="text-xs text-gray-500">
                  Reps: <strong className="text-gray-800">{video.score?.total_reps ?? '—'}</strong>
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
              <ArrowRight size={14} className="text-gray-300 group-hover:text-gray-600 transition-colors" />
              <button
                onClick={(e) => handleDeleteClick(video.id, e)}
                className="p-2 text-gray-300 hover:text-red-500 transition-colors rounded-lg hover:bg-red-50"
                aria-label="Delete video"
              >
                <Trash2 size={14} />
              </button>
            </div>
          </Link>
        ))}
      </div>
    </>
  );
}
