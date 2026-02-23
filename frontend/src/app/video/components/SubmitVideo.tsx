'use client'
import React, { useState } from 'react';
import { submitVideo } from '@/lib/api/videos';
import {Video} from "@/src/app/video/components/VideoList";

interface SubmitVideoProps {
  onVideoSubmit: (video: Video) => void;
}

export default function SubmitVideo({ onVideoSubmit  }: SubmitVideoProps) {
  const [file, setFile] = useState('');
  const [competition, setCompetition] = useState('');
    const [workout, setWorkout] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e:  React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const newVideo = await submitVideo({ name, competition, workout });
      setFile('');
      setCompetition('');
      setWorkout('');
      if (onVideoSubmit) onVideoSubmit(newVideo);
      alert('Video created successfully!');
    } catch (err) {
      setError('Failed to create Video');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

    return (
    <form onSubmit={handleSubmit} className="mb-8 p-4 border rounded">
      <h2 className="text-2xl font-bold mb-4">Subit your video</h2>

      {error && (
        <div className="mb-4 p-2 bg-red-100 text-red-700 rounded">
          {error}
        </div>
      )}

      <div className="mb-4">
        <label className="block mb-2">Upload your video</label>
        <input
          type="file"
          value={file}
          onChange={(e) => setFile(e.target.value)}
          required
          className="w-full border p-2 rounded"
        />
      </div>

      <div className="mb-4">
        <label className="block mb-2">Select your competition</label>
        <textarea
          value={competition}
          onChange={(e) => setCompetition(e.target.value)}
          required
          className="w-full border p-2 rounded"
        />
      </div>

        <div className="mb-4">
        <label className="block mb-2">Select your workout</label>
        <textarea
          value={workout}
          onChange={(e) => setWorkout(e.target.value)}
          required
          className="w-full border p-2 rounded"
        />
      </div>

      <button
        type="submit"
        disabled={loading}
        className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 disabled:bg-gray-400"
      >
        {loading ? 'Submitting...' : 'Submit Video'}
      </button>
    </form>
  );
}