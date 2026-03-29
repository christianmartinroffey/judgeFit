'use client'
import { useEffect, useState } from 'react';
import Link from 'next/link';
import Login from './athletes/components/Login';
import Register from './athletes/components/Register';

type View = 'landing' | 'login' | 'register';

export default function HomePage() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [view, setView] = useState<View>('landing');

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    setIsAuthenticated(!!token);
    setIsLoading(false);
  }, []);

  const handleAuthSuccess = () => setIsAuthenticated(true);

  if (isLoading) return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="w-5 h-5 border-2 border-gray-300 border-t-gray-900 rounded-full animate-spin" />
    </div>
  );

  if (!isAuthenticated) {
    if (view === 'login') {
      return <Login onLoginSuccess={handleAuthSuccess} onBack={() => setView('landing')} />;
    }
    if (view === 'register') {
      return <Register onRegisterSuccess={handleAuthSuccess} onBack={() => setView('landing')} />;
    }

    // Landing
    return (
      <div className="min-h-[calc(100vh-64px)] bg-white flex flex-col">
        <section className="flex-1 max-w-6xl mx-auto px-6 pt-28 pb-20 w-full">
          <div className="max-w-2xl">
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-6">JudgeFit</p>
            <h1 className="text-5xl font-bold text-gray-900 leading-tight tracking-tight mb-5">
              AI-powered judging for competitive fitness.
            </h1>
            <p className="text-lg text-gray-500 mb-10 leading-relaxed">
              Submit your workout video and get instant, accurate rep counting and movement-standard scoring.
            </p>
            <div className="flex items-center gap-3">
              <button
                onClick={() => setView('login')}
                className="bg-gray-900 text-white px-6 py-3 rounded-lg text-sm font-medium hover:bg-gray-700 transition-colors"
              >
                Sign in
              </button>
              <button
                onClick={() => setView('register')}
                className="px-6 py-3 rounded-lg text-sm font-medium text-gray-600 border border-gray-200 hover:border-gray-900 hover:text-gray-900 transition-colors"
              >
                Register
              </button>
            </div>
          </div>
        </section>

        <footer className="border-t border-gray-100 py-6">
          <div className="max-w-6xl mx-auto px-6">
            <p className="text-xs text-gray-400">© {new Date().getFullYear()} JudgeFit</p>
          </div>
        </footer>
      </div>
    );
  }

  // Authenticated dashboard
  const cards = [
    { href: '/athletes', label: 'Profile', description: 'View and update your athlete profile.' },
    { href: '/video', label: 'Videos', description: 'Submit your competition video for AI judging.' },
    { href: '/competitions', label: 'Competitions', description: 'View and manage your registered competitions.' },
  ];

  return (
    <div className="min-h-screen bg-white">
      <section className="max-w-6xl mx-auto px-6 pt-24 pb-20">
        <div className="max-w-2xl">
          <h1 className="text-5xl font-bold text-gray-900 leading-tight tracking-tight mb-5">
            AI-powered judging for competitive fitness.
          </h1>
          <p className="text-lg text-gray-500 mb-8 leading-relaxed">
            Submit your workout video and get instant, accurate rep counting and movement-standard scoring.
          </p>
          <Link
            href="/video/submit"
            className="inline-flex items-center gap-2 bg-gray-900 text-white px-6 py-3 rounded-lg text-sm font-medium hover:bg-gray-700 transition-colors"
          >
            Submit a video
          </Link>
        </div>
      </section>

      <div className="border-t border-gray-100" />

      <section className="max-w-6xl mx-auto px-6 py-16">
        <p className="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-8">Quick access</p>
        <div className="grid md:grid-cols-3 gap-5">
          {cards.map((card) => (
            <Link
              key={card.href}
              href={card.href}
              className="group border border-gray-100 rounded-xl p-6 hover:border-gray-300 hover:shadow-sm transition-all"
            >
              <h2 className="text-base font-semibold text-gray-900 mb-2 group-hover:text-gray-700">{card.label}</h2>
              <p className="text-sm text-gray-500 leading-relaxed">{card.description}</p>
              <span className="mt-4 inline-block text-xs text-gray-400 group-hover:text-gray-700 transition-colors">
                Go to {card.label} →
              </span>
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}
