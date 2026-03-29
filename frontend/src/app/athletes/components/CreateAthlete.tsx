'use client'
import React, { useState } from 'react';
import { createAthlete } from '@/lib/api/athletes';
import { Athlete } from './AthleteList';

interface CreateAthleteProps {
  onAthleteCreated: (athlete: Athlete) => void;
}

export default function CreateAthlete({ onAthleteCreated }: CreateAthleteProps) {
  const [name, setName] = useState('');
  const [surname, setSurname] = useState('');
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const newAthlete = await createAthlete({ name, surname, email });
      setName('');
      setSurname('');
      setEmail('');
      if (onAthleteCreated) onAthleteCreated(newAthlete);
    } catch (err) {
      setError('Failed to create athlete.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="border border-gray-100 rounded-xl p-6 mb-6">
      <h2 className="text-sm font-semibold text-gray-900 mb-5">Add athlete</h2>

      {error && (
        <div className="mb-4 px-4 py-3 bg-red-50 border border-red-100 text-red-600 text-sm rounded-lg">
          {error}
        </div>
      )}

      <div className="grid sm:grid-cols-3 gap-4 mb-5">
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1.5">First name</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            className="w-full border border-gray-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:border-gray-900 transition-colors"
            placeholder="Jane"
          />
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1.5">Surname</label>
          <input
            type="text"
            value={surname}
            onChange={(e) => setSurname(e.target.value)}
            required
            className="w-full border border-gray-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:border-gray-900 transition-colors"
            placeholder="Smith"
          />
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1.5">Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="w-full border border-gray-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:border-gray-900 transition-colors"
            placeholder="jane@example.com"
          />
        </div>
      </div>

      <button
        type="submit"
        disabled={loading}
        className="bg-gray-900 text-white px-5 py-2.5 rounded-lg text-sm font-medium hover:bg-gray-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? 'Adding…' : 'Add athlete'}
      </button>
    </form>
  );
}
