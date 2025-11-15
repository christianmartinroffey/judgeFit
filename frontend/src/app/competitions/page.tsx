'use client'
import { useState } from 'react';
import CompetitionList from './components/CompetitionList';
import CreateCompetition from "@/src/app/competitions/components/CompetitionCreate";

export default function AthletesPage() {
  const [refreshKey, setRefreshKey] = useState(0);

  const handleCompetitionCreated = () => {
    setRefreshKey(prev => prev + 1);
  };

  return (
    <main className="min-h-screen p-8">
      <div className="container mx-auto max-w-4xl">
        <h1 className="text-4xl font-bold mb-8">Athletes</h1>
        <CreateCompetition onCompetitionCreated={handleCompetitionCreated} />
        <CompetitionList key={refreshKey} />
      </div>
    </main>
  );
}