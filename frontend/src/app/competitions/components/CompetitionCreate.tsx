'use client'
import React, { useState } from 'react';
import { Competition } from './CompetitionList';
import { createCompetition, updateCompetition } from '@/lib/api/competitions';

interface CreateCompetitionProps {
  competition?: Competition;
  onCompetitionCreated: (competition: Competition) => void;
  onCancel?: () => void;
}

export default function CreateCompetition({ competition, onCompetitionCreated, onCancel }: CreateCompetitionProps) {
  const isEdit = !!competition;
  const [name, setName] = useState(competition?.name ?? '');
  const [description, setDescription] = useState(competition?.description ?? '');
  const [startDate, setStartDate] = useState(competition?.start_date ?? '');
  const [endDate, setEndDate] = useState(competition?.end_date ?? '');
  const [location, setLocation] = useState(competition?.location ?? '');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      if (isEdit) {
        const updated = await updateCompetition(competition!.id, {
          name, description, location, start_date: startDate, end_date: endDate,
        });
        onCompetitionCreated(updated);
        return;
      }
      const newCompetition = await createCompetition({ name, description, startDate, endDate, location });
      setName('');
      setDescription('');
      setStartDate('');
      setEndDate('');
      setLocation('');
      if (onCompetitionCreated) onCompetitionCreated(newCompetition);
    } catch (err) {
      setError(isEdit ? 'Failed to save changes.' : 'Failed to create competition.');
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

      <div className="flex items-center gap-3">
        <button
          type="submit"
          disabled={loading}
          className="bg-gray-900 text-white px-5 py-2.5 rounded-lg text-sm font-medium hover:bg-gray-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? (isEdit ? 'Saving…' : 'Adding…') : (isEdit ? 'Save changes' : 'Add competition')}
        </button>
        {isEdit && onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="text-sm text-gray-500 hover:text-gray-900 transition-colors"
          >
            Cancel
          </button>
        )}
      </div>
    </form>
  );
}
