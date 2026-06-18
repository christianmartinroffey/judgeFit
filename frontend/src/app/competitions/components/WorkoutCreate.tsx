'use client'
import React, { useState, useEffect } from 'react';
import { Plus, Trash2 } from 'lucide-react';
import { createWorkout, createWorkoutComponent, getMovements } from '@/lib/api/workouts';

interface Movement {
  id: number;
  name: string;
}

interface WorkoutMovementRow {
  movementId: string;
  reps: string;
  weight: string;
  height: string;
}

interface Workout {
  id: number;
  name: string;
  type: string;
  is_active: boolean;
  competition: number;
}

interface WorkoutCreateProps {
  competitionId: number;
  onWorkoutCreated: (workout: Workout) => void;
}

const WORKOUT_TYPES = [
  { value: 'AMRAP', label: 'AMRAP' },
  { value: 'FT', label: 'For Time' },
  { value: 'FW', label: 'For Weight' },
];

const emptyRow = (): WorkoutMovementRow => ({ movementId: '', reps: '', weight: '', height: '' });

export default function WorkoutCreate({ competitionId, onWorkoutCreated }: WorkoutCreateProps) {
  const [name, setName] = useState('');
  const [type, setType] = useState('AMRAP');
  const [timeCap, setTimeCap] = useState('');
  const [rounds, setRounds] = useState('1');
  const [movements, setMovements] = useState<WorkoutMovementRow[]>([emptyRow()]);
  const [availableMovements, setAvailableMovements] = useState<Movement[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getMovements()
      .then((data) => setAvailableMovements(data.results ?? data))
      .catch(() => setError('Failed to load movements.'));
  }, []);

  const updateRow = (index: number, field: keyof WorkoutMovementRow, value: string) => {
    setMovements((rows) => rows.map((r, i) => (i === index ? { ...r, [field]: value } : r)));
  };

  const addRow = () => setMovements((rows) => [...rows, emptyRow()]);

  const removeRow = (index: number) => {
    if (movements.length === 1) return;
    setMovements((rows) => rows.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (movements.some((r) => !r.movementId || !r.reps)) {
      setError('Each movement needs a movement and rep count.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const workout = await createWorkout({
        name,
        type,
        time_cap: timeCap ? parseInt(timeCap) : null,
        competition: competitionId,
        is_active: false,
      });

      const numRounds = Math.max(1, parseInt(rounds) || 1);
      const componentPromises: Promise<unknown>[] = [];
      for (let round = 1; round <= numRounds; round++) {
        movements.forEach((row, seq) => {
          componentPromises.push(
            createWorkoutComponent({
              workout: workout.id,
              movement: parseInt(row.movementId),
              round,
              sequence: seq + 1,
              reps: parseInt(row.reps),
              weight: row.weight ? parseInt(row.weight) : null,
              height: row.height ? parseInt(row.height) : null,
            })
          );
        });
      }
      await Promise.all(componentPromises);

      setName('');
      setType('AMRAP');
      setTimeCap('');
      setRounds('1');
      setMovements([emptyRow()]);
      onWorkoutCreated(workout);
    } catch (err) {
      setError('Failed to create workout.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="border border-gray-100 rounded-xl p-6 mb-6">
      {error && (
        <div className="mb-4 px-4 py-3 bg-red-50 border border-red-100 text-red-600 text-sm rounded-lg">
          {error}
        </div>
      )}

      <div className="grid sm:grid-cols-4 gap-4 mb-5">
        <div className="sm:col-span-2">
          <label className="block text-xs font-medium text-gray-600 mb-1.5">Name</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            className="w-full border border-gray-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:border-gray-900 transition-colors"
            placeholder="Workout 1"
          />
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1.5">Type</label>
          <select
            value={type}
            onChange={(e) => setType(e.target.value)}
            className="w-full border border-gray-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:border-gray-900 transition-colors bg-white"
          >
            {WORKOUT_TYPES.map((t) => (
              <option key={t.value} value={t.value}>{t.label}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1.5">Time cap (min)</label>
          <input
            type="number"
            value={timeCap}
            onChange={(e) => setTimeCap(e.target.value)}
            min={1}
            className="w-full border border-gray-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:border-gray-900 transition-colors"
            placeholder="—"
          />
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1.5">Rounds</label>
          <input
            type="number"
            value={rounds}
            onChange={(e) => setRounds(e.target.value)}
            min={1}
            required
            className="w-full border border-gray-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:border-gray-900 transition-colors"
          />
        </div>
      </div>

      <div className="mb-4">
        <p className="text-xs font-medium text-gray-600 mb-2">Movements</p>
        <div className="space-y-2">
          {movements.map((row, i) => (
            <div key={i} className="grid grid-cols-12 gap-2 items-center">
              <div className="col-span-4">
                <select
                  value={row.movementId}
                  onChange={(e) => updateRow(i, 'movementId', e.target.value)}
                  required
                  className="w-full border border-gray-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:border-gray-900 transition-colors bg-white"
                >
                  <option value="">Movement…</option>
                  {availableMovements.map((m) => (
                    <option key={m.id} value={m.id}>{m.name}</option>
                  ))}
                </select>
              </div>
              <div className="col-span-2">
                <input
                  type="number"
                  value={row.reps}
                  onChange={(e) => updateRow(i, 'reps', e.target.value)}
                  required
                  min={1}
                  placeholder="Reps"
                  className="w-full border border-gray-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:border-gray-900 transition-colors"
                />
              </div>
              <div className="col-span-2">
                <input
                  type="number"
                  value={row.weight}
                  onChange={(e) => updateRow(i, 'weight', e.target.value)}
                  min={0}
                  placeholder="lbs"
                  className="w-full border border-gray-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:border-gray-900 transition-colors"
                />
              </div>
              <div className="col-span-2">
                <input
                  type="number"
                  value={row.height}
                  onChange={(e) => updateRow(i, 'height', e.target.value)}
                  min={0}
                  placeholder="in"
                  className="w-full border border-gray-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:border-gray-900 transition-colors"
                />
              </div>
              <div className="col-span-2 flex gap-1 justify-end">
                {i === movements.length - 1 && (
                  <button
                    type="button"
                    onClick={addRow}
                    className="p-2 text-gray-400 hover:text-gray-900 transition-colors rounded-lg hover:bg-gray-100"
                  >
                    <Plus size={15} />
                  </button>
                )}
                <button
                  type="button"
                  onClick={() => removeRow(i)}
                  disabled={movements.length === 1}
                  className="p-2 text-gray-300 hover:text-red-500 transition-colors rounded-lg hover:bg-red-50 disabled:opacity-30 disabled:cursor-not-allowed"
                >
                  <Trash2 size={15} />
                </button>
              </div>
            </div>
          ))}
        </div>
        <div className="mt-1 grid grid-cols-12 gap-2 px-0">
          <div className="col-span-4" />
          <div className="col-span-2 text-center text-xs text-gray-400">reps</div>
          <div className="col-span-2 text-center text-xs text-gray-400">weight (lbs)</div>
          <div className="col-span-2 text-center text-xs text-gray-400">height (in)</div>
        </div>
      </div>

      <button
        type="submit"
        disabled={loading}
        className="bg-gray-900 text-white px-5 py-2.5 rounded-lg text-sm font-medium hover:bg-gray-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? 'Creating…' : 'Add workout'}
      </button>
    </form>
  );
}
