import type { Metadata } from 'next'
import React from 'react'
import './globals.css'
import { ThemeProvider } from './context/ThemeContext'

export const metadata: Metadata = {
  title: 'Elenchus AI - Legal Research Assistant',
  description: 'AI-powered legal research and document analysis platform',
  viewport: 'width=device-width, initial-scale=1',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="min-h-screen antialiased">
        <ThemeProvider>
          {children}
        </ThemeProvider>
      </body>
    </html>
  )
} 