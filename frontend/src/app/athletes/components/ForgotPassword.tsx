'use client'
import React, { useState } from 'react';
import { requestPasswordReset } from '@/lib/api/auth';

interface ForgotPasswordProps {
  onBack: () => void;
}

export default function ForgotPassword({ onBack }: ForgotPasswordProps) {
  const [email, setEmail] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await requestPasswordReset(email);
      setSubmitted(true);
    } catch (err: unknown) {
      const msg = (err as { message?: string })?.message;
      setError(msg ?? 'Something went wrong. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <button onClick={onBack} className="text-sm text-gray-400 hover:text-gray-700 transition-colors mb-8 flex items-center gap-1">
          ← Back
        </button>

        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900 tracking-tight">Reset your password</h1>
          <p className="text-sm text-gray-500 mt-1">We&apos;ll email you a link to reset it.</p>
        </div>

        {submitted ? (
          <div className="px-4 py-3 bg-gray-50 border border-gray-200 text-gray-700 text-sm rounded-lg">
            If that email is registered, a reset link has been sent. Check your inbox.
          </div>
        ) : (
          <>
            {error && (
              <div className="mb-5 px-4 py-3 bg-red-50 border border-red-100 text-red-600 text-sm rounded-lg">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">Email</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="w-full border border-gray-200 rounded-lg px-4 py-3 text-sm focus:outline-none focus:border-gray-900 transition-colors"
                  placeholder="jane@example.com"
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-gray-900 text-white py-3 rounded-lg text-sm font-medium hover:bg-gray-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed mt-2"
              >
                {loading ? 'Sending…' : 'Send reset link'}
              </button>
            </form>
          </>
        )}
      </div>
    </div>
  );
}
