'use client'
import { useState, useEffect } from 'react';
import { getAthletes, deleteAthlete } from '@/lib/api';

// Define the Athlete type
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
      setError('Failed to fetch Athletes');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this athlete?')) return;
    try {
      await deleteAthlete(id);
        setAthletes(athletes.filter((athlete) => athlete.id !== id));
    } catch (err) {
      alert('Failed to delete athlete');
      console.error(err);
    }
  };

  if (loading) return <div className="p-4">Loading...</div>;
  if (error) return <div className="p-4 text-red-500">{error}</div>;

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">Athletes</h1>

      {athletes.length === 0 ? (
        <p>No athlete yet. Create one from Django admin!</p>
      ) : (
        <div className="grid gap-4">
          {athletes.map((athlete) => (
            <div key={athlete.id.toString()} className="border p-4 rounded shadow">
              <h2 className="text-xl font-semibold">{athlete.id}</h2>
              <p className="text-gray-600 mt-2">{athlete.surname}</p>
              <div className="mt-4 flex gap-2">
                <span className="text-sm text-gray-500">
                  {new Date(athlete.created_at).toLocaleDateString()}
                </span>
                <button
                  onClick={() => handleDelete(athlete.id)}
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