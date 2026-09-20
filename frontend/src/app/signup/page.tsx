"use client";

import { AuthForm } from "@/components/AuthForm";
import { signup } from "@/lib/auth/api";

export default function SignupPage() {
  return <AuthForm mode="signup" onSubmit={signup} />;
}
