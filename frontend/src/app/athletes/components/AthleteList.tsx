'use client'
import { useState, useEffect } from 'react';
import { getAthletes, deleteAthlete } from '@/lib/api/athletes';
import { Trash2 } from 'lucide-react';

export interface Athlete {
  key: number;
  id: number;
  surname: string;
  created_at: string;
}

export default function AthleteList() {
  const [athletes, setAthletes] = useState<Athlete[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchAthletes();
  }, []);

  const fetchAthletes = async () => {
    try {
      setLoading(true);
      const data = await getAthletes();
      setAthletes(data.results);
      setError(null);
    } catch (err) {
      setError('Failed to load athletes.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Delete this athlete?')) return;
    try {
      await deleteAthlete(id);
      setAthletes(athletes.filter((a) => a.id !== id));
    } catch (err) {
      alert('Failed to delete athlete.');
      console.error(err);
    }
  };

  if (loading) return (
    <div className="flex items-center gap-2 text-sm text-gray-400 py-8">
      <div className="w-4 h-4 border-2 border-gray-200 border-t-gray-500 rounded-full animate-spin" />
      Loading athletes…
    </div>
  );
  if (error) return <p className="text-sm text-red-500 py-4">{error}</p>;

  if (athletes.length === 0) {
    return (
      <div className="border border-dashed border-gray-200 rounded-xl p-10 text-center">
        <p className="text-sm text-gray-400">No athletes yet. Add one above.</p>
      </div>
    );
  }

  return (
    <div className="divide-y divide-gray-100 border border-gray-100 rounded-xl overflow-hidden">
      {athletes.map((athlete) => (
        <div key={athlete.id} className="flex items-center justify-between px-5 py-4 hover:bg-gray-50 transition-colors">
          <div>
            <p className="text-sm font-medium text-gray-900">{athlete.surname}</p>
            <p className="text-xs text-gray-400 mt-0.5">ID {athlete.id} · Added {new Date(athlete.created_at).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })}</p>
          </div>
          <button
            onClick={() => handleDelete(athlete.id)}
            className="p-2 text-gray-300 hover:text-red-500 transition-colors rounded-lg hover:bg-red-50"
            aria-label="Delete athlete"
          >
            <Trash2 size={15} />
          </button>
        </div>
      ))}
    </div>
  );
}
