'use client'
import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, Plus, X } from 'lucide-react';
import ProtectedPage from '../../components/ProtectedPage';
import WorkoutList from '../components/WorkoutList';
import WorkoutCreate from '../components/WorkoutCreate';
import { getCompetition } from '@/lib/api/competitions';
import { checkIsAdmin } from '@/lib/auth';
import { Competition } from '../components/CompetitionList';

export default function CompetitionDetailPage() {
  const { id } = useParams<{ id: string }>();
  const competitionId = parseInt(id);

  const [competition, setCompetition] = useState<Competition | null>(null);
  const [isAdmin, setIsAdmin] = useState(false);
  const [showCreate, setShowCreate] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setIsAdmin(checkIsAdmin());
  }, []);

  useEffect(() => {
    getCompetition(competitionId)
      .then(setCompetition)
      .catch(() => setError('Failed to load competition.'))
      .finally(() => setLoading(false));
  }, [competitionId]);

  const handleWorkoutCreated = () => {
    setShowCreate(false);
    setRefreshKey((k) => k + 1);
  };

  if (loading) return (
    <ProtectedPage>
      <main className="min-h-screen bg-white">
        <div className="max-w-6xl mx-auto px-6 py-12">
          <div className="flex items-center gap-2 text-sm text-gray-400">
            <div className="w-4 h-4 border-2 border-gray-200 border-t-gray-500 rounded-full animate-spin" />
            Loading…
          </div>
        </div>
      </main>
    </ProtectedPage>
  );

  if (error || !competition) return (
    <ProtectedPage>
      <main className="min-h-screen bg-white">
        <div className="max-w-6xl mx-auto px-6 py-12">
          <p className="text-sm text-red-500">{error ?? 'Competition not found.'}</p>
        </div>
      </main>
    </ProtectedPage>
  );

  return (
    <ProtectedPage>
      <main className="min-h-screen bg-white">
        <div className="max-w-6xl mx-auto px-6 py-12">
          <Link
            href="/competitions"
            className="inline-flex items-center gap-1.5 text-sm text-gray-400 hover:text-gray-900 transition-colors mb-8"
          >
            <ArrowLeft size={14} />
            Competitions
          </Link>

          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 tracking-tight">{competition.name}</h1>
            <p className="text-sm text-gray-500 mt-1">
              {competition.location} ·{' '}
              {new Date(competition.start_date).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })}
              {' – '}
              {new Date(competition.end_date).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })}
            </p>
            {competition.description && (
              <p className="text-sm text-gray-400 mt-1">{competition.description}</p>
            )}
          </div>

          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Workouts</h2>
            {isAdmin && (
              <button
                onClick={() => setShowCreate((v) => !v)}
                className="inline-flex items-center gap-1.5 bg-gray-900 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-700 transition-colors"
              >
                {showCreate ? <X size={14} /> : <Plus size={14} />}
                {showCreate ? 'Cancel' : 'Add workout'}
              </button>
            )}
          </div>

          {showCreate && (
            <WorkoutCreate competitionId={competitionId} onWorkoutCreated={handleWorkoutCreated} />
          )}

          <WorkoutList competitionId={competitionId} isAdmin={isAdmin} refreshKey={refreshKey} />
        </div>
      </main>
    </ProtectedPage>
  );
}
