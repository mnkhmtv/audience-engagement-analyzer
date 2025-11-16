'use client';

import Link from 'next/link';
import { useRouter, usePathname } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';

export function Navigation() {
  const router = useRouter();
  const pathname = usePathname();
  const { isAuthenticated, logout } = useAuth();

  const handleLogout = () => {
    logout();
    router.push('/auth/login');
  };

  const linkClasses = (path: string) =>
    `text-sm font-medium transition ${
      pathname === path ? 'text-white' : 'text-slate-300 hover:text-white'
    }`;

  return (
    <nav className="bg-slate-950 border-b border-slate-700 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <Link href="/lectures" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-lg">LA</span>
            </div>
            <span className="text-white font-semibold hidden sm:inline">
              Lecture Analysis
            </span>
          </Link>

          {isAuthenticated && (
            <div className="flex items-center gap-4">
              <Link href="/lectures" className={linkClasses('/lectures')}>
                Lectures
              </Link>
              <Link href="/lectures/upload" className={linkClasses('/lectures/upload')}>
                Upload
              </Link>
              <button
                onClick={handleLogout}
                className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition"
              >
                Logout
              </button>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}

export default Navigation;
