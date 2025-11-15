'use client'
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import Login from './athletes/components/Login';

export default function HomePage() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    setIsAuthenticated(!!token);
    setIsLoading(false);
  }, []);

  const handleLoginSuccess = () => {
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setIsAuthenticated(false);
  };

  if (isLoading) {
    return <div className="min-h-screen flex items-center justify-center">Loading...</div>;
  }

  if (!isAuthenticated) {
    return <Login onLoginSuccess={handleLoginSuccess} />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-16">
        {/* Header with Logout */}
        <div className="flex justify-end mb-8">
          <button
            onClick={handleLogout}
            className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600 transition"
          >
            Logout
          </button>
        </div>

        {/* Hero Section */}
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            Welcome to JudgeFit
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Submit your video for review.
          </p>
        </div>

        {/* Feature Cards */}
        <div className="grid md:grid-cols-2 gap-6 max-w-4xl mx-auto">
          <Link
            href="/athletes"
            className="bg-white p-8 rounded-lg shadow-lg hover:shadow-xl transition group"
          >
            <h2 className="text-2xl font-bold mb-4 group-hover:text-blue-600">
              Profile
            </h2>
            <p className="text-gray-600">
              Create, view, and manage athlete profiles
            </p>
          </Link>

          <Link
            href="/competitions"
            className="bg-white p-8 rounded-lg shadow-lg hover:shadow-xl transition group"
          >
            <h2 className="text-2xl font-bold mb-4 group-hover:text-blue-600">
              Competitions
            </h2>
            <p className="text-gray-600">
              View your registered competitions
            </p>
          </Link>

        </div>
      </div>
    </div>
  );
}