'use client'
import { useState, useEffect } from 'react';
import { getCompetitions, deleteCompetition } from '@/lib/api/competitions';
import { checkIsAdmin } from '@/lib/auth';
import { Trash2 } from 'lucide-react';

export interface Competition {
  id: number;
  name: string;
  location: string;
  start_date: string;
  end_date: string;
  created_at: string;
  description: string;
}

export default function CompetitionList() {
  const [competitions, setCompetitions] = useState<Competition[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isAdmin, setIsAdmin] = useState(false);

  useEffect(() => {
    setIsAdmin(checkIsAdmin());
  }, []);

  useEffect(() => {
    fetchCompetitions();
  }, []);

  const fetchCompetitions = async () => {
    try {
      setLoading(true);
      const data = await getCompetitions();
      setCompetitions(data.results);
      setError(null);
    } catch (err) {
      setError('Failed to load competitions.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Delete this competition?')) return;
    try {
      await deleteCompetition(id);
      setCompetitions(competitions.filter((c) => c.id !== id));
    } catch (err) {
      alert('Failed to delete competition.');
      console.error(err);
    }
  };

  if (loading) return (
    <div className="flex items-center gap-2 text-sm text-gray-400 py-8">
      <div className="w-4 h-4 border-2 border-gray-200 border-t-gray-500 rounded-full animate-spin" />
      Loading competitions…
    </div>
  );
  if (error) return <p className="text-sm text-red-500 py-4">{error}</p>;

  if (competitions.length === 0) {
    return (
      <div className="border border-dashed border-gray-200 rounded-xl p-10 text-center">
        <p className="text-sm text-gray-400">No competitions yet.</p>
      </div>
    );
  }

  return (
    <div className="divide-y divide-gray-100 border border-gray-100 rounded-xl overflow-hidden">
      {competitions.map((competition) => (
        <div key={competition.id} className="flex items-center justify-between px-5 py-4 hover:bg-gray-50 transition-colors">
          <div>
            <p className="text-sm font-medium text-gray-900">{competition.name}</p>
            <p className="text-xs text-gray-400 mt-0.5">
              {competition.location} · {new Date(competition.start_date).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })} – {new Date(competition.end_date).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })}
            </p>
            {competition.description && (
              <p className="text-xs text-gray-400 mt-0.5">{competition.description}</p>
            )}
          </div>
          {isAdmin && (
            <button
              onClick={() => handleDelete(competition.id)}
              className="p-2 text-gray-300 hover:text-red-500 transition-colors rounded-lg hover:bg-red-50"
              aria-label="Delete competition"
            >
              <Trash2 size={15} />
            </button>
          )}
        </div>
      ))}
    </div>
  );
}
