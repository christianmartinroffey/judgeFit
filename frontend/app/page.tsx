'use client'
import { useState } from 'react';
import AthleteList from './components/AthleteList';
import CreateAthlete from './components/CreateAthlete';

export default function Home() {
  const [refreshKey, setRefreshKey] = useState(0);

  const handleAthleteCreated = () => {
    setRefreshKey(prev => prev + 1);
  };

  return (
    <main className="min-h-screen p-8">
      <div className="container mx-auto max-w-4xl">
        <h1 className="text-4xl font-bold mb-8 text-center">
          Django + Next.js App
        </h1>
        <CreateAthlete onAthleteCreated={handleAthleteCreated} />
        <AthleteList key={refreshKey} />
      </div>
    </main>
  );
}