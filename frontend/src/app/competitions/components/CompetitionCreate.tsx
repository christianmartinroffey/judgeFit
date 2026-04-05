'use client'
import React, { useState } from 'react';
import { Competition } from './CompetitionList';
import { createCompetition } from '@/lib/api/competitions';

interface CreateCompetitionProps {
  onCompetitionCreated: (competition: Competition) => void;
}

export default function CreateCompetition({ onCompetitionCreated }: CreateCompetitionProps) {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [location, setLocation] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const newCompetition = await createCompetition({ name, description, startDate, endDate, location });
      setName('');
      setDescription('');
      setStartDate('');
      setEndDate('');
      setLocation('');
      if (onCompetitionCreated) onCompetitionCreated(newCompetition);
    } catch (err) {
      setError('Failed to create competition.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="border border-gray-100 rounded-xl p-6 mb-6">
      {error && (
        <div className="mb-4 px-4 py-3 bg-red-50 border border-red-100 text-red-600 text-sm rounded-lg">
          {error}
        </div>
      )}

      <div className="grid sm:grid-cols-3 gap-4 mb-5">
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1.5">Name</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            className="w-full border border-gray-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:border-gray-900 transition-colors"
            placeholder="Your Throwdown 2025"
          />
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1.5">Description</label>
          <input
            type="text"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            required
            className="w-full border border-gray-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:border-gray-900 transition-colors"
            placeholder=""
          />
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1.5">Location</label>
          <input
            type="text"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            required
            className="w-full border border-gray-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:border-gray-900 transition-colors"
            placeholder="Online"
          />
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1.5">Start date</label>
          <input
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            required
            className="w-full border border-gray-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:border-gray-900 transition-colors"
            placeholder=""
          />
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1.5">End date</label>
          <input
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            required
            className="w-full border border-gray-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:border-gray-900 transition-colors"
            placeholder=""
          />
        </div>
      </div>

      <button
        type="submit"
        disabled={loading}
        className="bg-gray-900 text-white px-5 py-2.5 rounded-lg text-sm font-medium hover:bg-gray-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? 'Adding…' : 'Add competition'}
      </button>
    </form>
  );
}
