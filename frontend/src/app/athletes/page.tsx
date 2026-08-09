'use client'
import AthleteProfile from './components/AthleteProfile';
import ChangePassword from './components/ChangePassword';
import DeleteAccount from './components/DeleteAccount';
import ProtectedPage from '../components/ProtectedPage';

export default function ProfilePage() {
  return (
    <ProtectedPage>
      <main className="min-h-screen bg-white">
        <div className="max-w-6xl mx-auto px-6 py-12">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 tracking-tight">My profile</h1>
            <p className="text-sm text-gray-500 mt-1">View and update your athlete profile.</p>
          </div>
          <div className="max-w-2xl space-y-10">
            <AthleteProfile />

            <div>
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-4">Account settings</p>
              <div className="space-y-5">
                <ChangePassword />
                <DeleteAccount />
              </div>
            </div>
          </div>
        </div>
      </main>
    </ProtectedPage>
  );
}
