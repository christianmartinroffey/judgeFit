'use client'
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

export default function ProtectedPage({ children }: { children: React.ReactNode }) {
  const [checking, setChecking] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      router.replace('/');
    } else {
      setChecking(false);
    }
  }, [router]);

  if (checking) return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="w-5 h-5 border-2 border-gray-200 border-t-gray-900 rounded-full animate-spin" />
    </div>
  );

  return <>{children}</>;
}
