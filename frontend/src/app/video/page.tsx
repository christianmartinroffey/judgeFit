'use client'
import VideoList from './components/VideoList';
import Link from 'next/link';

export default function VideosPage() {
  return (
    <main className="min-h-screen bg-white">
      <div className="max-w-6xl mx-auto px-6 py-12">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 tracking-tight">Videos</h1>
            <p className="text-sm text-gray-500 mt-1">Your submitted competition videos.</p>
          </div>
          <Link
            href="/video/submit"
            className="bg-gray-900 text-white px-5 py-2.5 rounded-lg text-sm font-medium hover:bg-gray-700 transition-colors"
          >
            Submit video
          </Link>
        </div>
        <VideoList />
      </div>
    </main>
  );
}
