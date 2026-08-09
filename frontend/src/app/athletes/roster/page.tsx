'use client'
import Link from 'next/link';
import { Plus } from 'lucide-react';
import AdminProtectedPage from '../../components/AdminProtectedPage';
import AthleteList from '../components/AthleteList';

export default function AthleteRosterPage() {
  return (
    <AdminProtectedPage>
      <main className="min-h-screen bg-white">
        <div className="max-w-6xl mx-auto px-6 py-12">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 tracking-tight">Athletes</h1>
              <p className="text-sm text-gray-500 mt-1">Manage registered athletes.</p>
            </div>
            <Link
              href="/athletes/create"
              className="inline-flex items-center gap-1.5 bg-gray-900 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-700 transition-colors"
            >
              <Plus size={14} />
              Add athlete
            </Link>
          </div>
          <AthleteList />
        </div>
      </main>
    </AdminProtectedPage>
  );
}
