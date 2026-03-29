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

export interface Score {
  is_valid: boolean;
  total_reps: number | null;
  no_reps: number | null;
  is_scaled: boolean;
  score: string;
  status: string | null;
  movement_breakdown: BreakdownSet[];
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

export default function VideoList() {
  const [videos, setVideos] = useState<Video[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

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

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.preventDefault();
    if (!confirm('Delete this video?')) return;
    try {
      await deleteVideo(id);
      setVideos(videos.filter((v) => v.id !== id));
    } catch (err) {
      alert('Failed to delete video.');
      console.error(err);
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
              onClick={(e) => handleDelete(video.id, e)}
              className="p-2 text-gray-300 hover:text-red-500 transition-colors rounded-lg hover:bg-red-50"
              aria-label="Delete video"
            >
              <Trash2 size={14} />
            </button>
          </div>
        </Link>
      ))}
    </div>
  );
}
