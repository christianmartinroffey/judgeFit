'use client'
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { ClipboardList, Users, Trophy } from 'lucide-react';
import AdminProtectedPage from '../components/AdminProtectedPage';
import { getReviewQueue } from '@/lib/api/videos';
import { getCompetitions } from '@/lib/api/competitions';
import { getAthletes } from '@/lib/api/athletes';

interface Stat {
  label: string;
  value: number | null;
  href: string;
  icon: React.ElementType;
  accent: string;
}

function DashboardContent() {
  const [pendingReviews, setPendingReviews] = useState<number | null>(null);
  const [competitionCount, setCompetitionCount] = useState<number | null>(null);
  const [athleteCount, setAthleteCount] = useState<number | null>(null);

  useEffect(() => {
    getReviewQueue({ status: 'S' }).then((d) => setPendingReviews(d.count ?? 0)).catch(() => setPendingReviews(0));
    getCompetitions().then((d) => setCompetitionCount(d.count ?? 0)).catch(() => setCompetitionCount(0));
    getAthletes().then((d) => setAthleteCount(d.count ?? 0)).catch(() => setAthleteCount(0));
  }, []);

  const stats: Stat[] = [
    { label: 'Pending reviews', value: pendingReviews, href: '/review', icon: ClipboardList, accent: 'text-amber-600 bg-amber-50 border-amber-100' },
    { label: 'Competitions', value: competitionCount, href: '/competitions', icon: Trophy, accent: 'text-blue-600 bg-blue-50 border-blue-100' },
    { label: 'Registered athletes', value: athleteCount, href: '/athletes/roster', icon: Users, accent: 'text-green-600 bg-green-50 border-green-100' },
  ];

  return (
    <main className="min-h-screen bg-white">
      <div className="max-w-6xl mx-auto px-6 py-12">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 tracking-tight">Dashboard</h1>
          <p className="text-sm text-gray-500 mt-1">Competition management overview.</p>
        </div>

        <div className="grid sm:grid-cols-3 gap-5">
          {stats.map((stat) => {
            const Icon = stat.icon;
            return (
              <Link
                key={stat.label}
                href={stat.href}
                className="group border border-gray-100 rounded-xl p-6 hover:border-gray-300 hover:shadow-sm transition-all"
              >
                <div className={`inline-flex items-center justify-center w-9 h-9 rounded-lg border mb-4 ${stat.accent}`}>
                  <Icon size={16} />
                </div>
                <p className="text-3xl font-bold text-gray-900">{stat.value ?? '—'}</p>
                <p className="text-sm text-gray-500 mt-1">{stat.label}</p>
                <span className="mt-3 inline-block text-xs text-gray-400 group-hover:text-gray-700 transition-colors">
                  View →
                </span>
              </Link>
            );
          })}
        </div>
      </div>
    </main>
  );
}

export default function DashboardPage() {
  return (
    <AdminProtectedPage>
      <DashboardContent />
    </AdminProtectedPage>
  );
}
