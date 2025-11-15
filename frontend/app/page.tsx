'use client'
import { useState, useEffect } from 'react';
import AthleteList from '@/app/components/AthleteList';
import CreateAthlete from '@/app/components/CreateAthlete';
import Login from '@/app/components/Login';

export default function Home() {
  const [refreshKey, setRefreshKey] = useState(0);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  console.log('Home component rendered. isAuthenticated:', isAuthenticated);
  useEffect(() => {
    // Check if user has a token
    const token = localStorage.getItem('access_token');
    setIsAuthenticated(!!token);
  }, []);

  const handleAthleteCreated = () => {
    setRefreshKey(prev => prev + 1);
  };


  const handleLoginSuccess = () => {
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setIsAuthenticated(false);
  };

  if (!isAuthenticated) {
    return <Login onLoginSuccess={handleLoginSuccess} />;
  }

  return (
    <main className="min-h-screen p-8">
      <div className="container mx-auto max-w-4xl">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-4xl font-bold">Athletes App</h1>
          <button
            onClick={handleLogout}
            className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
          >
            Logout
          </button>
        </div>
        <CreateAthlete onAthleteCreated={handleAthleteCreated} />
        <AthleteList key={refreshKey} />
      </div>
    </main>
  );
}