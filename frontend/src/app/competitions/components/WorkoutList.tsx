'use client'
import { useState, useEffect } from 'react';
import { Trash2, Zap } from 'lucide-react';
import { getWorkouts, activateWorkout, deleteWorkout } from '@/lib/api/workouts';

interface WorkoutComponent {
  id: number;
  movement: number;
  movement_name: string;
  round: number;
  sequence: number;
  reps: number;
  weight: number | null;
  height: number | null;
}

export interface Workout {
  id: number;
  name: string;
  type: string;
  time_cap: number | null;
  is_active: boolean;
  competition: number;
  components: WorkoutComponent[];
}

interface WorkoutListProps {
  competitionId: number;
  isAdmin: boolean;
  refreshKey?: number;
}

const TYPE_LABELS: Record<string, string> = {
  AMRAP: 'AMRAP',
  FT: 'For Time',
  FW: 'For Weight',
};

export default function WorkoutList({ competitionId, isAdmin, refreshKey }: WorkoutListProps) {
  const [workouts, setWorkouts] = useState<Workout[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchWorkouts();
  }, [competitionId, refreshKey]);

  const fetchWorkouts = async () => {
    try {
      setLoading(true);
      const data = await getWorkouts(competitionId);
      setWorkouts(data.results ?? data);
      setError(null);
    } catch {
      setError('Failed to load workouts.');
    } finally {
      setLoading(false);
    }
  };

  const handleActivate = async (id: number) => {
    if (!confirm('Activate this workout? It will be locked for editing and open for submissions.')) return;
    try {
      await activateWorkout(id);
      setWorkouts((ws) => ws.map((w) => (w.id === id ? { ...w, is_active: true } : w)));
    } catch {
      alert('Failed to activate workout.');
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Delete this workout?')) return;
    try {
      await deleteWorkout(id);
      setWorkouts((ws) => ws.filter((w) => w.id !== id));
    } catch {
      alert('Failed to delete workout.');
    }
  };

  const rounds = (components: WorkoutComponent[]) =>
    components.length > 0 ? Math.max(...components.map((c) => c.round)) : 0;

  const movementsForRound = (components: WorkoutComponent[], round: number) =>
    components.filter((c) => c.round === round).sort((a, b) => a.sequence - b.sequence);

  if (loading) return (
    <div className="flex items-center gap-2 text-sm text-gray-400 py-6">
      <div className="w-4 h-4 border-2 border-gray-200 border-t-gray-500 rounded-full animate-spin" />
      Loading workouts…
    </div>
  );
  if (error) return <p className="text-sm text-red-500 py-4">{error}</p>;

  if (workouts.length === 0) {
    return (
      <div className="border border-dashed border-gray-200 rounded-xl p-8 text-center">
        <p className="text-sm text-gray-400">No workouts yet.</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {workouts.map((workout) => {
        const numRounds = rounds(workout.components);
        const round1Movements = movementsForRound(workout.components, 1);

        return (
          <div key={workout.id} className="border border-gray-100 rounded-xl p-5">
            <div className="flex items-start justify-between mb-3">
              <div>
                <div className="flex items-center gap-2">
                  <p className="text-sm font-medium text-gray-900">{workout.name}</p>
                  <span className="text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-600">
                    {TYPE_LABELS[workout.type] ?? workout.type}
                  </span>
                  {workout.is_active ? (
                    <span className="text-xs px-2 py-0.5 rounded-full bg-green-50 text-green-700 border border-green-100">
                      Live
                    </span>
                  ) : (
                    <span className="text-xs px-2 py-0.5 rounded-full bg-yellow-50 text-yellow-700 border border-yellow-100">
                      Draft
                    </span>
                  )}
                </div>
                {workout.time_cap && (
                  <p className="text-xs text-gray-400 mt-0.5">{workout.time_cap} min cap</p>
                )}
              </div>
              {isAdmin && (
                <div className="flex items-center gap-1">
                  {!workout.is_active && (
                    <>
                      <button
                        onClick={() => handleActivate(workout.id)}
                        className="flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-green-700 bg-green-50 hover:bg-green-100 rounded-lg transition-colors border border-green-100"
                      >
                        <Zap size={12} />
                        Activate
                      </button>
                      <button
                        onClick={() => handleDelete(workout.id)}
                        className="p-2 text-gray-300 hover:text-red-500 transition-colors rounded-lg hover:bg-red-50"
                      >
                        <Trash2 size={14} />
                      </button>
                    </>
                  )}
                </div>
              )}
            </div>

            {round1Movements.length > 0 && (
              <div className="text-xs text-gray-500">
                {numRounds > 1 && (
                  <p className="font-medium text-gray-600 mb-1">{numRounds} rounds of:</p>
                )}
                <ul className="space-y-0.5">
                  {round1Movements.map((c) => (
                    <li key={c.id} className="flex items-center gap-1">
                      <span className="font-medium text-gray-700">{c.reps}</span>
                      <span>{c.movement_name}</span>
                      {c.weight && <span className="text-gray-400">@ {c.weight} lbs</span>}
                      {c.height && <span className="text-gray-400">/ {c.height}"</span>}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
