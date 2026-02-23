'use client'
import VideoList from './components/VideoList';
import Link from "next/link";

export default function VideosPage() {

  // this is video overview page
  // should have summaries -> scores, competitions, state of submission etc
  // fetch the list of videos here

    return (
        <main className="min-h-screen p-8">
            <div className="container mx-auto max-w-4xl">
                <h1 className="text-4xl font-bold mb-8">Videos</h1>
                <VideoList/>

            </div>
            <div className="grid md:grid-cols-2 gap-6 max-w-4xl mx-auto">
                <Link
                    href="/video/submit"
                    className="bg-white p-8 rounded-lg shadow-lg hover:shadow-xl transition group"
                >
                    <h2 className="text-2xl font-bold mb-4 group-hover:text-blue-600">
                        Submit your video here
                    </h2>
                    <p className="text-gray-600"></p>
                </Link>
            </div>
        </main>
    );
}