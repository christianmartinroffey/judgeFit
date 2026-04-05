'use client'
import { useState, useEffect } from 'react';
import Link from 'next/link';
import CompetitionList from './components/CompetitionList';
import ProtectedPage from '../components/ProtectedPage';
import { checkIsAdmin } from '@/lib/auth';

export default function CompetitionsPage() {
  const [isAdmin, setIsAdmin] = useState(false);

  useEffect(() => {
    setIsAdmin(checkIsAdmin());
  }, []);

  return (
    <ProtectedPage>
      <main className="min-h-screen bg-white">
        <div className="max-w-6xl mx-auto px-6 py-12">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 tracking-tight">Competitions</h1>
              <p className="text-sm text-gray-500 mt-1">View and enter competitions.</p>
            </div>
            {isAdmin && (
              <Link
                href="/competitions/create"
                className="bg-gray-900 text-white px-5 py-2.5 rounded-lg text-sm font-medium hover:bg-gray-700 transition-colors"
              >
                Add competition
              </Link>
            )}
          </div>
          <CompetitionList />
        </div>
      </main>
    </ProtectedPage>
  );
}
