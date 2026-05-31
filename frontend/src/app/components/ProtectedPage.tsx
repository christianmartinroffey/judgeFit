'use client'
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { isTokenValid } from '@/lib/auth';
import { attemptRefresh } from '@/lib/api';

export default function ProtectedPage({ children }: { children: React.ReactNode }) {
  const [checking, setChecking] = useState(true);
  const router = useRouter();

  useEffect(() => {
    async function check() {
      const token = localStorage.getItem('access_token');
      if (token && isTokenValid(token)) {
        setChecking(false);
        return;
      }

      const refreshed = await attemptRefresh();
      if (refreshed) {
        setChecking(false);
      } else {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        router.replace('/');
      }
    }

    check();
  }, [router]);

  if (checking) return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="w-5 h-5 border-2 border-gray-200 border-t-gray-900 rounded-full animate-spin" />
    </div>
  );

  return <>{children}</>;
}
