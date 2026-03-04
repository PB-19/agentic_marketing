"use client";
import { AuthProvider } from "@/lib/auth";
import { PipelineProvider } from "@/lib/pipeline";
import { SidebarProvider } from "@/lib/sidebar";

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <AuthProvider>
      <SidebarProvider>
        <PipelineProvider>{children}</PipelineProvider>
      </SidebarProvider>
    </AuthProvider>
  );
}
