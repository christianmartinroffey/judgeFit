'use client'
import React, { useState, useEffect, useRef } from 'react';
import { submitVideo } from '@/lib/api/videos';
import { getCompetitions } from '@/lib/api/competitions';
import { getWorkouts } from '@/lib/api/workouts';
import { Video } from "@/src/app/video/components/VideoList";
import { ChevronDown } from 'lucide-react';

interface Option {
  id: number;
  label: string;
}

function SearchableSelect({
  options,
  value,
  onChange,
  placeholder,
  loading: optionsLoading,
}: {
  options: Option[];
  value: number | null;
  onChange: (id: number | null) => void;
  placeholder: string;
  loading?: boolean;
}) {
  const [query, setQuery] = useState('');
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
        setQuery('');
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const selected = options.find((o) => o.id === value);
  const filtered = query
    ? options.filter((o) => o.label.toLowerCase().includes(query.toLowerCase()))
    : options;

  return (
    <div ref={ref} className="relative">
      <div className="relative">
        <input
          type="text"
          value={open ? query : (selected?.label ?? '')}
          onChange={(e) => { setQuery(e.target.value); setOpen(true); if (!e.target.value) onChange(null); }}
          onFocus={() => setOpen(true)}
          placeholder={optionsLoading ? 'Loading…' : placeholder}
          disabled={optionsLoading}
          autoComplete="off"
          className="w-full border border-gray-200 rounded-lg px-4 py-3 pr-10 text-sm focus:outline-none focus:border-gray-900 transition-colors disabled:bg-gray-50 disabled:text-gray-400"
        />
        <ChevronDown
          size={14}
          className={`absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none transition-transform ${open ? 'rotate-180' : ''}`}
        />
      </div>

      {open && (
        <div className="absolute z-20 w-full bg-white border border-gray-200 rounded-lg mt-1 shadow-lg max-h-52 overflow-y-auto">
          {filtered.length > 0 ? (
            filtered.map((option) => (
              <button
                key={option.id}
                type="button"
                onMouseDown={(e) => e.preventDefault()}
                onClick={() => { onChange(option.id); setOpen(false); setQuery(''); }}
                className={`w-full text-left px-4 py-2.5 text-sm transition-colors hover:bg-gray-50 ${
                  option.id === value ? 'font-medium text-gray-900 bg-gray-50' : 'text-gray-700'
                }`}
              >
                {option.label}
              </button>
            ))
          ) : (
            <p className="px-4 py-3 text-sm text-gray-400">
              {query ? `No results for "${query}"` : 'No options available'}
            </p>
          )}
        </div>
      )}
    </div>
  );
}

interface SubmitVideoProps {
  onVideoSubmit: (video: Video) => void;
}

export default function SubmitVideo({ onVideoSubmit }: SubmitVideoProps) {
  const [videoURL, setVideoURL] = useState('');
  const [competitionId, setCompetitionId] = useState<number | null>(null);
  const [workoutId, setWorkoutId] = useState<number | null>(null);

  const [competitions, setCompetitions] = useState<Option[]>([]);
  const [workouts, setWorkouts] = useState<Option[]>([]);
  const [optionsLoading, setOptionsLoading] = useState(true);

  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([getCompetitions(), getWorkouts()])
      .then(([compData, workData]) => {
        setCompetitions(
          (compData.results ?? compData).map((c: { id: number; name: string }) => ({ id: c.id, label: c.name }))
        );
        setWorkouts(
          (workData.results ?? workData).map((w: { id: number; name: string }) => ({ id: w.id, label: w.name }))
        );
      })
      .catch(() => setError('Failed to load competitions and workouts.'))
      .finally(() => setOptionsLoading(false));
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!competitionId || !workoutId) {
      setError('Please select a competition and workout.');
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      const newVideo = await submitVideo({ videoURL, competition: competitionId, workout: workoutId });
      setVideoURL('');
      setCompetitionId(null);
      setWorkoutId(null);
      if (onVideoSubmit) onVideoSubmit(newVideo);
    } catch {
      setError('Failed to submit video. Please check the URL and try again.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="border border-gray-100 rounded-xl p-6">
      <p className="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-5">Video details</p>

      {error && (
        <div className="mb-5 px-4 py-3 bg-red-50 border border-red-100 text-red-600 text-sm rounded-lg">
          {error}
        </div>
      )}

      <div className="space-y-4 mb-6">
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1.5">Video URL</label>
          <input
            type="url"
            value={videoURL}
            onChange={(e) => setVideoURL(e.target.value)}
            required
            className="w-full border border-gray-200 rounded-lg px-4 py-3 text-sm focus:outline-none focus:border-gray-900 transition-colors"
            placeholder="https://youtube.com/watch?v=..."
          />
        </div>

        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1.5">Competition</label>
          <SearchableSelect
            options={competitions}
            value={competitionId}
            onChange={setCompetitionId}
            placeholder="Search competitions…"
            loading={optionsLoading}
          />
        </div>

        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1.5">Workout</label>
          <SearchableSelect
            options={workouts}
            value={workoutId}
            onChange={setWorkoutId}
            placeholder="Search workouts…"
            loading={optionsLoading}
          />
        </div>
      </div>

      <button
        type="submit"
        disabled={submitting || optionsLoading}
        className="bg-gray-900 text-white px-6 py-3 rounded-lg text-sm font-medium hover:bg-gray-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {submitting ? 'Submitting…' : 'Submit video'}
      </button>
    </form>
  );
}
