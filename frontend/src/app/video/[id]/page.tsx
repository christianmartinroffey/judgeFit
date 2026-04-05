'use client'
import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { getVideo } from '@/lib/api/videos';
import { Video, BreakdownSet } from '@/src/app/video/components/VideoList';
import { ArrowLeft } from 'lucide-react';
import ProtectedPage from '@/src/app/components/ProtectedPage';

function formatMovement(key: string): string {
  return key.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
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

function SummaryCard({ video }: { video: Video }) {
  const score = video.score;
  const totalExpected = score?.movement_breakdown?.reduce(
    (sum, s) => sum + (s.expected_reps ?? 0), 0
  ) ?? null;

  const stats = [
    {
      label: 'Total Reps',
      value: score?.total_reps != null
        ? <>{score.total_reps}{totalExpected != null && <span className="text-lg font-normal text-gray-400"> / {totalExpected}</span>}</>
        : '—',
    },
    {
      label: 'No-Reps',
      value: <span className="text-red-500">{score?.no_reps ?? '—'}</span>,
    },
    {
      label: 'Valid',
      value: score?.is_valid ? <span className="text-green-600">Yes</span> : <span className="text-red-500">No</span>,
    },
    {
      label: 'Scaled',
      value: score?.is_scaled ? 'Yes' : 'No',
    },
  ];

  return (
    <div className="border border-gray-100 rounded-xl p-6 mb-6">
      <p className="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-5">Summary</p>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-6">
        {stats.map((stat) => (
          <div key={stat.label}>
            <p className="text-xs text-gray-400 mb-1">{stat.label}</p>
            <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

function RoundCard({ round, sets }: { round: number; sets: BreakdownSet[] }) {
  return (
    <div className="border border-gray-100 rounded-xl overflow-hidden mb-4">
      <div className="px-5 py-3 bg-gray-50 border-b border-gray-100">
        <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Round {round}</p>
      </div>
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left border-b border-gray-100">
            <th className="px-5 py-3 text-xs font-medium text-gray-400">Movement</th>
            <th className="px-5 py-3 text-xs font-medium text-gray-400 text-center">Expected</th>
            <th className="px-5 py-3 text-xs font-medium text-gray-400 text-center">Reps</th>
            <th className="px-5 py-3 text-xs font-medium text-gray-400 text-center">No-Reps</th>
            <th className="px-5 py-3 text-xs font-medium text-gray-400">Notes</th>
          </tr>
        </thead>
        <tbody>
          {sets.map((set, i) => {
            const repsMet = set.expected_reps != null && set.reps >= set.expected_reps;
            const hasNoReps = set.no_reps > 0;

            return (
              <tr key={i} className="border-b border-gray-50 last:border-0 hover:bg-gray-50 transition-colors">
                <td className="px-5 py-3.5 font-medium text-gray-900">{formatMovement(set.movement)}</td>
                <td className="px-5 py-3.5 text-center text-gray-400 text-sm">
                  {set.expected_reps ?? '—'}
                </td>
                <td className="px-5 py-3.5 text-center">
                  <span className={`font-semibold text-sm ${repsMet ? 'text-green-600' : 'text-amber-600'}`}>
                    {set.reps}{repsMet ? ' ✓' : ` / ${set.expected_reps}`}
                  </span>
                </td>
                <td className="px-5 py-3.5 text-center">
                  {hasNoReps
                    ? <span className="font-semibold text-red-500 text-sm">{set.no_reps}</span>
                    : <span className="text-gray-300 text-sm">0</span>
                  }
                </td>
                <td className="px-5 py-3.5">
                  <div className="flex flex-wrap gap-1.5">
                    {hasNoReps && (
                      <span className="text-xs bg-red-50 text-red-600 border border-red-100 px-2 py-0.5 rounded-full">
                        {set.no_reps} no-rep{set.no_reps > 1 ? 's' : ''}
                      </span>
                    )}
                    {set.advance_reason === 'video_end' && (
                      <span className="text-xs bg-amber-50 text-amber-700 border border-amber-100 px-2 py-0.5 rounded-full">
                        Video ended mid-set
                      </span>
                    )}
                  </div>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

function BreakdownSection({ breakdown }: { breakdown: BreakdownSet[] }) {
  if (!breakdown || breakdown.length === 0) {
    return (
      <div className="border border-dashed border-gray-200 rounded-xl p-8 text-center">
        <p className="text-sm text-gray-400">No breakdown available yet — analysis may still be processing.</p>
      </div>
    );
  }

  const rounds = breakdown.reduce<Record<number, BreakdownSet[]>>((acc, set) => {
    if (!acc[set.round]) acc[set.round] = [];
    acc[set.round].push(set);
    return acc;
  }, {});

  return (
    <div>
      <p className="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-5">Movement Breakdown</p>
      {Object.entries(rounds)
        .sort(([a], [b]) => Number(a) - Number(b))
        .map(([round, sets]) => (
          <RoundCard key={round} round={Number(round)} sets={sets} />
        ))}
    </div>
  );
}

function VideoDetailContent() {
  const { id } = useParams<{ id: string }>();
  const [video, setVideo] = useState<Video | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    getVideo(id)
      .then((data) => setVideo(data))
      .catch(() => setError('Failed to load video results.'))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return (
    <div className="min-h-screen bg-white flex items-center justify-center">
      <div className="w-5 h-5 border-2 border-gray-200 border-t-gray-900 rounded-full animate-spin" />
    </div>
  );
  if (error || !video) return (
    <div className="min-h-screen bg-white flex items-center justify-center">
      <p className="text-sm text-red-500">{error ?? 'Video not found.'}</p>
    </div>
  );

  return (
    <main className="min-h-screen bg-white">
      <div className="max-w-6xl mx-auto px-6 py-12">
        {/* Back */}
        <Link
          href="/video"
          className="inline-flex items-center gap-1.5 text-sm text-gray-400 hover:text-gray-900 transition-colors mb-8"
        >
          <ArrowLeft size={14} />
          Back to videos
        </Link>

        {/* Header */}
        <div className="flex items-start justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 tracking-tight">{video.workout}</h1>
            <p className="text-sm text-gray-400 mt-1">
              {video.competition} · {new Date(video.created_at).toLocaleDateString('en-GB', {
                day: 'numeric', month: 'long', year: 'numeric',
              })}
            </p>
          </div>
          <StatusBadge status={video.score?.status ?? null} />
        </div>

        {/* Summary */}
        <SummaryCard video={video} />

        {/* Breakdown */}
        <BreakdownSection breakdown={video.score?.movement_breakdown ?? []} />

        {/* No-rep guidance */}
        {(video.score?.no_reps ?? 0) > 0 && (
          <div className="mt-6 bg-amber-50 border border-amber-100 rounded-xl p-5 text-sm text-amber-800">
            <p className="font-semibold mb-1">Reviewing your no-reps</p>
            <p className="leading-relaxed">
              Your submission recorded <strong>{video.score!.no_reps} no-rep{video.score!.no_reps! > 1 ? 's' : ''}</strong>.
              Use the round breakdown above to identify which sets had issues, then
              rewatch your video to see where the movement standard wasn't met.
            </p>
          </div>
        )}
      </div>
    </main>
  );
}

export default function VideoDetailPage() {
  return (
    <ProtectedPage>
      <VideoDetailContent />
    </ProtectedPage>
  );
}
