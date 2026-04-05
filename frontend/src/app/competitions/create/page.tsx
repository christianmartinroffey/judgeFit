'use client'
import { useRouter } from 'next/navigation';
import AdminProtectedPage from '../../components/AdminProtectedPage';
import CreateCompetition from '../components/CompetitionCreate';
import { Competition } from '../components/CompetitionList';

export default function CreateCompetitionPage() {
  const router = useRouter();

  const handleCreated = (_competition: Competition) => {
    router.push('/competitions');
  };

  return (
    <AdminProtectedPage>
      <main className="min-h-screen bg-white">
        <div className="max-w-6xl mx-auto px-6 py-12">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 tracking-tight">Add competition</h1>
            <p className="text-sm text-gray-500 mt-1">Create a new competition.</p>
          </div>
          <CreateCompetition onCompetitionCreated={handleCreated} />
        </div>
      </main>
    </AdminProtectedPage>
  );
}
