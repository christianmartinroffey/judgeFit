'use client'
import { useState } from 'react';
import CompetitionList from './components/CompetitionList';
import CreateCompetition from "@/src/app/competitions/components/CompetitionCreate";
import ProtectedPage from '../components/ProtectedPage';

export default function CompetitionsPage() {
  const [refreshKey, setRefreshKey] = useState(0);

  const handleCompetitionCreated = () => {
    setRefreshKey(prev => prev + 1);
  };

  return (
    <ProtectedPage>
      <main className="min-h-screen bg-white">
        <div className="max-w-6xl mx-auto px-6 py-12">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 tracking-tight">Competitions</h1>
            <p className="text-sm text-gray-500 mt-1">Manage your competitions.</p>
          </div>
          <CreateCompetition onCompetitionCreated={handleCompetitionCreated} />
          <CompetitionList key={refreshKey} />
        </div>
      </main>
    </ProtectedPage>
  );
}
