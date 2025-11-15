'use client'
import { useState, useEffect } from 'react';
import { getCompetitions, deleteCompetition } from '@/lib/api/competitions';


// Define the Competition type
export interface Competition {
  key: number;
  id: number;
  surname: string;
  created_at: string;
}

export default function CompetitionList() {
  const [competitions, setCompetitions] = useState<Competition[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

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
      setError('Failed to fetch Competitions');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this Competition?')) return;
    try {
      await deleteCompetition(id);
        setCompetitions(competitions.filter((competition) => competition.id !== id));
    } catch (err) {
      alert('Failed to delete competition');
      console.error(err);
    }
  };

  if (loading) return <div className="p-4">Loading...</div>;
  if (error) return <div className="p-4 text-red-500">{error}</div>;

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">Competitions</h1>

      {competitions.length === 0 ? (
        <p>No competition yet. Create one from Django admin!</p>
      ) : (
        <div className="grid gap-4">
          {competitions.map((competition) => (
            <div key={competition.id.toString()} className="border p-4 rounded shadow">
              <h2 className="text-xl font-semibold">{competition.id}</h2>
              <p className="text-gray-600 mt-2">{competition.surname}</p>
              <div className="mt-4 flex gap-2">
                <span className="text-sm text-gray-500">
                  {new Date(competition.created_at).toLocaleDateString()}
                </span>
                <button
                  onClick={() => handleDelete(competition.id)}
                  className="ml-auto text-red-500 hover:text-red-700"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}