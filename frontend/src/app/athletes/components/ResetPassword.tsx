'use client'
import React, { useState } from 'react';
import { confirmPasswordReset } from '@/lib/api/auth';

interface ResetPasswordProps {
  uid: string;
  token: string;
  onSuccess: () => void;
}

export default function ResetPassword({ uid, token, onSuccess }: ResetPasswordProps) {
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    setLoading(true);
    try {
      await confirmPasswordReset({ uid, token, password });
      setSuccess(true);
    } catch (err: unknown) {
      const msg = (err as { message?: string })?.message;
      setError(msg ?? 'That reset link is invalid or has expired.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900 tracking-tight">Choose a new password</h1>
          <p className="text-sm text-gray-500 mt-1">Enter a new password for your account.</p>
        </div>

        {success ? (
          <>
            <div className="mb-5 px-4 py-3 bg-gray-50 border border-gray-200 text-gray-700 text-sm rounded-lg">
              Your password has been reset.
            </div>
            <button
              onClick={onSuccess}
              className="w-full bg-gray-900 text-white py-3 rounded-lg text-sm font-medium hover:bg-gray-700 transition-colors"
            >
              Sign in
            </button>
          </>
        ) : (
          <>
            {error && (
              <div className="mb-5 px-4 py-3 bg-red-50 border border-red-100 text-red-600 text-sm rounded-lg">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">New password</label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  minLength={8}
                  className="w-full border border-gray-200 rounded-lg px-4 py-3 text-sm focus:outline-none focus:border-gray-900 transition-colors"
                  placeholder="••••••••"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">Confirm password</label>
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                  minLength={8}
                  className="w-full border border-gray-200 rounded-lg px-4 py-3 text-sm focus:outline-none focus:border-gray-900 transition-colors"
                  placeholder="••••••••"
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-gray-900 text-white py-3 rounded-lg text-sm font-medium hover:bg-gray-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed mt-2"
              >
                {loading ? 'Resetting…' : 'Reset password'}
              </button>
            </form>
          </>
        )}
      </div>
    </div>
  );
}
