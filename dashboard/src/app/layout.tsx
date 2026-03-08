/**
 * SadakAI Dashboard - Main Application Entry Point
 * 
 * This file initializes the Next.js application with:
 * - Toast notification provider
 * - Global layout with sidebar
 * - Mobile-responsive bottom navigation
 * 
 * @author SadakAI Team
 * @version 1.0.0
 */

import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Sidebar } from "@/components/layout/Sidebar";
import { ToastProvider } from "@/components/ui/Toast";

// Initialize Google Font with latin subset
const inter = Inter({ subsets: ["latin"] });

// Page metadata for SEO
export const metadata: Metadata = {
  title: "SadakAI - Road Hazard Detection",
  description: "Indian Road Hazard Detection & Crowdsourced Mapping Platform",
  manifest: "/manifest.json",
  viewport: "width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no",
};

/**
 * Root layout component
 * 
 * Wraps all pages with:
 * - ToastProvider for notifications
 * - Sidebar navigation (desktop)
 * - Bottom navigation (mobile)
 * 
 * @param children - Page content
 */
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <ToastProvider>
          <div className="flex h-screen overflow-hidden">
            {/* Desktop sidebar navigation */}
            <Sidebar />
            
            {/* Main content area with padding for mobile bottom nav */}
            <main className="flex-1 overflow-auto bg-background pb-16 lg:pb-0">
              {children}
            </main>
          </div>
        </ToastProvider>
      </body>
    </html>
  );
}
