'use client'
import React, { useState } from 'react';
import { createAthlete } from '@/lib/api';
import { Athlete } from './AthleteList';

interface CreateAthleteProps {
  onAthleteCreated: (athlete: Athlete) => void;
}

export default function CreateAthlete({ onAthleteCreated  }: CreateAthleteProps) {
  const [name, setName] = useState('');
  const [surname, setSurname] = useState('');
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e:  React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const newAthlete = await createAthlete({ name, surname, email });
      setName('');
      setSurname('');
      setEmail('');
      if (onAthleteCreated) onAthleteCreated(newAthlete);
      alert('Athlete created successfully!');
    } catch (err) {
      setError('Failed to create Athlete');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="mb-8 p-4 border rounded">
      <h2 className="text-2xl font-bold mb-4">Create New Athlete</h2>

      {error && (
        <div className="mb-4 p-2 bg-red-100 text-red-700 rounded">
          {error}
        </div>
      )}

      <div className="mb-4">
        <label className="block mb-2">Name</label>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
          className="w-full border p-2 rounded"
        />
      </div>

      <div className="mb-4">
        <label className="block mb-2">Surname</label>
        <textarea
          value={surname}
          onChange={(e) => setSurname(e.target.value)}
          required
          rows="4"
          className="w-full border p-2 rounded"
        />
      </div>

        <div className="mb-4">
        <label className="block mb-2">Email</label>
        <textarea
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          rows="4"
          className="w-full border p-2 rounded"
        />
      </div>

      <button
        type="submit"
        disabled={loading}
        className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 disabled:bg-gray-400"
      >
        {loading ? 'Creating...' : 'Create Athlete'}
      </button>
    </form>
  );
}