"use client";

import Link from "next/link";
import { useAuth } from "@/lib/auth/AuthContext";

interface SiteHeaderProps {
  subtitle: string;
}

export function SiteHeader({ subtitle }: SiteHeaderProps) {
  const { user, isLoading, logout } = useAuth();

  return (
    <header className="flex items-start justify-between gap-4 border-b border-zinc-200 bg-white px-6 py-5 dark:border-zinc-800 dark:bg-zinc-950">
      <div>
        <h1 className="text-xl font-semibold text-[#032147] dark:text-zinc-50">Prelegal</h1>
        <p className="mt-1 max-w-2xl text-sm text-zinc-600 dark:text-zinc-400">{subtitle}</p>
      </div>
      <nav className="flex shrink-0 items-center gap-4 pt-1 text-sm">
        <Link href="/documents" className="text-[#209dd7] hover:underline">
          My Documents
        </Link>
        {!isLoading &&
          (user ? (
            <>
              <span className="hidden text-zinc-600 sm:inline dark:text-zinc-400">{user.email}</span>
              <button type="button" onClick={logout} className="text-[#209dd7] hover:underline">
                Log out
              </button>
            </>
          ) : (
            <>
              <Link href="/login" className="text-[#209dd7] hover:underline">
                Log in
              </Link>
              <Link href="/signup" className="text-[#209dd7] hover:underline">
                Sign up
              </Link>
            </>
          ))}
      </nav>
    </header>
  );
}
