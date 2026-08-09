'use client'
import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, Trophy } from 'lucide-react';
import ProtectedPage from '@/src/app/components/ProtectedPage';
import { getWorkout, getWorkoutLeaderboard } from '@/lib/api/workouts';

interface LeaderboardEntry {
  rank: number;
  athlete_id: number;
  athlete_name: string;
  good_reps: number | null;
  total_reps: number | null;
  no_reps: number | null;
  is_valid: boolean;
  is_scaled: boolean;
  video_id: string;
}

interface WorkoutInfo {
  id: number;
  name: string;
  competition: number;
}

const RANK_STYLES: Record<number, string> = {
  1: 'bg-yellow-50 text-yellow-700 border-yellow-200',
  2: 'bg-gray-100 text-gray-700 border-gray-200',
  3: 'bg-orange-50 text-orange-700 border-orange-200',
};

function LeaderboardContent() {
  const { id } = useParams<{ id: string }>();
  const workoutId = parseInt(id);

  const [workout, setWorkout] = useState<WorkoutInfo | null>(null);
  const [entries, setEntries] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!workoutId) return;
    Promise.all([getWorkout(workoutId), getWorkoutLeaderboard(workoutId)])
      .then(([w, board]) => {
        setWorkout(w);
        setEntries(board);
      })
      .catch(() => setError('Failed to load leaderboard.'))
      .finally(() => setLoading(false));
  }, [workoutId]);

  if (loading) return (
    <main className="min-h-screen bg-white flex items-center justify-center">
      <div className="w-5 h-5 border-2 border-gray-200 border-t-gray-900 rounded-full animate-spin" />
    </main>
  );

  if (error) return (
    <main className="min-h-screen bg-white flex items-center justify-center">
      <p className="text-sm text-red-500">{error}</p>
    </main>
  );

  return (
    <main className="min-h-screen bg-white">
      <div className="max-w-4xl mx-auto px-6 py-12">
        <Link
          href={workout ? `/competitions/${workout.competition}` : '/competitions'}
          className="inline-flex items-center gap-1.5 text-sm text-gray-400 hover:text-gray-900 transition-colors mb-8"
        >
          <ArrowLeft size={14} />
          Back to competition
        </Link>

        <div className="flex items-center gap-3 mb-8">
          <Trophy size={24} className="text-yellow-500" />
          <div>
            <h1 className="text-3xl font-bold text-gray-900 tracking-tight">{workout?.name ?? 'Leaderboard'}</h1>
            <p className="text-sm text-gray-500 mt-0.5">Ranked by good reps, then total reps.</p>
          </div>
        </div>

        {entries.length === 0 ? (
          <div className="border border-dashed border-gray-200 rounded-xl p-10 text-center">
            <p className="text-sm text-gray-400">No completed submissions yet.</p>
          </div>
        ) : (
          <div className="border border-gray-100 rounded-xl overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left border-b border-gray-100 bg-gray-50">
                  <th className="px-5 py-3 text-xs font-medium text-gray-400">Rank</th>
                  <th className="px-5 py-3 text-xs font-medium text-gray-400">Athlete</th>
                  <th className="px-5 py-3 text-xs font-medium text-gray-400 text-center">Good reps</th>
                  <th className="px-5 py-3 text-xs font-medium text-gray-400 text-center">Total reps</th>
                  <th className="px-5 py-3 text-xs font-medium text-gray-400 text-center">No-reps</th>
                  <th className="px-5 py-3 text-xs font-medium text-gray-400 text-center">Valid</th>
                </tr>
              </thead>
              <tbody>
                {entries.map((entry) => (
                  <tr key={entry.athlete_id} className="border-b border-gray-50 last:border-0 hover:bg-gray-50 transition-colors">
                    <td className="px-5 py-3.5">
                      <span className={`inline-flex items-center justify-center w-7 h-7 rounded-full text-xs font-semibold border ${RANK_STYLES[entry.rank] ?? 'bg-white text-gray-500 border-gray-200'}`}>
                        {entry.rank}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 font-medium text-gray-900">
                      {entry.athlete_name}
                      {entry.is_scaled && (
                        <span className="ml-2 text-xs bg-gray-100 text-gray-500 px-2 py-0.5 rounded-full">Scaled</span>
                      )}
                    </td>
                    <td className="px-5 py-3.5 text-center font-semibold text-green-600">{entry.good_reps ?? '—'}</td>
                    <td className="px-5 py-3.5 text-center text-gray-700">{entry.total_reps ?? '—'}</td>
                    <td className="px-5 py-3.5 text-center text-red-500">{entry.no_reps ?? '—'}</td>
                    <td className="px-5 py-3.5 text-center">
                      {entry.is_valid
                        ? <span className="text-green-600">Yes</span>
                        : <span className="text-red-500">No</span>}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </main>
  );
}

export default function LeaderboardPage() {
  return (
    <ProtectedPage>
      <LeaderboardContent />
    </ProtectedPage>
  );
}
