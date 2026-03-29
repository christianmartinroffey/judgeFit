'use client'
import AthleteProfile from './components/AthleteProfile';

export default function ProfilePage() {
  return (
    <main className="min-h-screen bg-white">
      <div className="max-w-6xl mx-auto px-6 py-12">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 tracking-tight">My profile</h1>
          <p className="text-sm text-gray-500 mt-1">View and update your athlete profile.</p>
        </div>
        <div className="max-w-2xl">
          <AthleteProfile />
        </div>
      </div>
    </main>
  );
}
