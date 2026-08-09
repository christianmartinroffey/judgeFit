'use client'
import { useRouter } from 'next/navigation';
import AdminProtectedPage from '../../components/AdminProtectedPage';
import CreateAthlete from '../components/CreateAthlete';
import { Athlete } from '../components/AthleteList';

export default function CreateAthletePage() {
  const router = useRouter();

  const handleCreated = (_athlete: Athlete) => {
    router.push('/athletes/roster');
  };

  return (
    <AdminProtectedPage>
      <main className="min-h-screen bg-white">
        <div className="max-w-6xl mx-auto px-6 py-12">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 tracking-tight">Add athlete</h1>
            <p className="text-sm text-gray-500 mt-1">Register a new athlete profile.</p>
          </div>
          <div className="max-w-2xl">
            <CreateAthlete onAthleteCreated={handleCreated} />
          </div>
        </div>
      </main>
    </AdminProtectedPage>
  );
}
