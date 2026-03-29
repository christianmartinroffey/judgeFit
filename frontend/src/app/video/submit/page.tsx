'use client'
import { useRouter } from 'next/navigation';
import SubmitVideo from '../components/SubmitVideo';
import { Video } from '../components/VideoList';
import ProtectedPage from '../../components/ProtectedPage';

export default function SubmitVideoPage() {
  const router = useRouter();

  const handleVideoSubmit = (video: Video) => {
    router.push('/video');
  };

  return (
    <ProtectedPage>
      <main className="min-h-screen bg-white">
        <div className="max-w-6xl mx-auto px-6 py-12">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 tracking-tight">Submit a video</h1>
            <p className="text-sm text-gray-500 mt-1">Your video will be analysed and scored automatically.</p>
          </div>
          <div className="max-w-xl">
            <SubmitVideo onVideoSubmit={handleVideoSubmit} />
          </div>
        </div>
      </main>
    </ProtectedPage>
  );
}
