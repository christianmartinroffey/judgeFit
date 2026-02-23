'use client'
import SubmitVideo from '../components/SubmitVideo';

export default function VideosPage() {

  const handleVideoSubmit = () => {
  };

  return (
    <main className="min-h-screen p-8">
      <div className="container mx-auto max-w-4xl">
        <h1 className="text-4xl font-bold mb-8">Videos</h1>
        <SubmitVideo onVideoSubmit={handleVideoSubmit} />
      </div>
    </main>
  );
}