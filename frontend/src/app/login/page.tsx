"use client";

import { AuthForm } from "@/components/AuthForm";
import { login } from "@/lib/auth/api";

export default function LoginPage() {
  return <AuthForm mode="login" onSubmit={login} />;
}
