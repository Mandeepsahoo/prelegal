"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import type { AuthResponse } from "@/lib/auth/api";
import { setToken } from "@/lib/auth/api";
import { useAuth } from "@/lib/auth/AuthContext";

const inputClass =
  "rounded-md border border-zinc-300 bg-white px-3 py-2 text-sm text-zinc-900 shadow-sm focus:border-[#209dd7] focus:outline-none focus:ring-1 focus:ring-[#209dd7] dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100";

interface AuthFormProps {
  mode: "login" | "signup";
  onSubmit: (email: string, password: string) => Promise<AuthResponse>;
}

export function AuthForm({ mode, onSubmit }: AuthFormProps) {
  const router = useRouter();
  const { refresh } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      const result = await onSubmit(email, password);
      setToken(result.access_token);
      refresh();
      router.push("/");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const isLogin = mode === "login";

  return (
    <div className="flex flex-1 flex-col items-center justify-center bg-zinc-50 px-6 py-12 dark:bg-black">
      <div className="w-full max-w-sm overflow-hidden rounded-xl border border-zinc-200 bg-white shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
        <div className="h-1.5 bg-[#ecad0a]" />
        <div className="flex flex-col gap-6 px-8 py-8">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wide text-[#209dd7]">Prelegal</p>
            <h1 className="mt-1 text-2xl font-semibold text-[#032147] dark:text-zinc-50">
              {isLogin ? "Log in" : "Create an account"}
            </h1>
          </div>
          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <label className="flex flex-col gap-1 text-sm">
              <span className="font-medium text-zinc-700 dark:text-zinc-300">Email</span>
              <input
                type="email"
                required
                autoComplete="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                className={inputClass}
              />
            </label>
            <label className="flex flex-col gap-1 text-sm">
              <span className="font-medium text-zinc-700 dark:text-zinc-300">Password</span>
              <input
                type="password"
                required
                minLength={8}
                autoComplete={isLogin ? "current-password" : "new-password"}
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                className={inputClass}
              />
            </label>
            {error && <p className="text-sm text-red-600 dark:text-red-400">{error}</p>}
            <button
              type="submit"
              disabled={isSubmitting}
              className="rounded-md bg-[#753991] px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-[#5f2d75] disabled:cursor-not-allowed disabled:opacity-60"
            >
              {isSubmitting ? "Please wait..." : isLogin ? "Log in" : "Sign up"}
            </button>
          </form>
          <p className="text-sm text-[#888888]">
            {isLogin ? (
              <>
                Don&apos;t have an account?{" "}
                <Link href="/signup" className="text-[#209dd7] hover:underline">
                  Sign up
                </Link>
              </>
            ) : (
              <>
                Already have an account?{" "}
                <Link href="/login" className="text-[#209dd7] hover:underline">
                  Log in
                </Link>
              </>
            )}
          </p>
        </div>
      </div>
    </div>
  );
}
