'use client'
import { useState, useEffect } from 'react';
import { getVideos, deleteVideo } from "@/lib/api/videos";

// Define the video type
export interface Video {
  key: number;
  id: number;
  athlete_id: number;
  created_at: string;
}

export default function VideoList() {
  const [videos, setVideos] = useState<Video[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchVideos();
  }, []);

  const fetchVideos = async () => {
    try {
      setLoading(true);
      const data = await getVideos();
      setVideos(data.results);
      setError(null);
    } catch (err) {
      setError('Failed to fetch Videos');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this video?')) return;
    try {
      await deleteVideo(id);
        setVideos(videos.filter((video) => video.id !== id));
    } catch (err) {
      alert('Failed to delete video');
      console.error(err);
    }
  };

  if (loading) return <div className="p-4">Loading...</div>;
  if (error) return <div className="p-4 text-red-500">{error}</div>;

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">Videos</h1>

      {videos.length === 0 ? (
        <p>No videos yet. Create one from Django admin!</p>
      ) : (
        <div className="grid gap-4">
          {videos.map((video) => (
            <div key={video.id.toString()} className="border p-4 rounded shadow">
              <h2 className="text-xl font-semibold">{video.id}</h2>
              <div className="mt-4 flex gap-2">
                <span className="text-sm text-gray-500">
                  {new Date(video.created_at).toLocaleDateString()}
                </span>
                <button
                  onClick={() => handleDelete(video.id)}
                  className="ml-auto text-red-500 hover:text-red-700"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}