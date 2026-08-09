'use client'
import React, { useState } from 'react';
import { deleteAccount } from '@/lib/api/auth';

export default function DeleteAccount() {
  const [confirming, setConfirming] = useState(false);
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [deleting, setDeleting] = useState(false);

  const handleDelete = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setDeleting(true);
    try {
      await deleteAccount(password);
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.dispatchEvent(new Event('auth-change'));
      window.location.href = '/';
    } catch (err: unknown) {
      const msg = (err as { message?: string })?.message;
      setError(msg ?? 'Failed to delete account.');
      setDeleting(false);
    }
  };

  return (
    <div className="border border-red-100 rounded-xl p-6">
      <p className="text-xs font-semibold text-red-400 uppercase tracking-widest mb-2">Danger zone</p>
      <p className="text-sm text-gray-500 mb-4">
        Deleting your account permanently removes your login and athlete profile. This cannot be undone.
      </p>

      {!confirming ? (
        <button
          onClick={() => setConfirming(true)}
          className="px-4 py-2 text-sm font-medium text-red-600 border border-red-200 rounded-lg hover:bg-red-50 transition-colors"
        >
          Delete account
        </button>
      ) : (
        <form onSubmit={handleDelete} className="max-w-sm space-y-3">
          {error && (
            <div className="px-4 py-3 bg-red-50 border border-red-100 text-red-600 text-sm rounded-lg">{error}</div>
          )}
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1.5">
              Enter your password to confirm
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full border border-gray-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:border-red-500 transition-colors"
              placeholder="••••••••"
            />
          </div>
          <div className="flex items-center gap-3">
            <button
              type="submit"
              disabled={deleting}
              className="px-4 py-2 text-sm font-medium bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {deleting ? 'Deleting…' : 'Permanently delete my account'}
            </button>
            <button
              type="button"
              onClick={() => { setConfirming(false); setPassword(''); setError(null); }}
              disabled={deleting}
              className="text-sm text-gray-500 hover:text-gray-900 transition-colors"
            >
              Cancel
            </button>
          </div>
        </form>
      )}
    </div>
  );
}
