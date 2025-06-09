import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'NotebookLM Replica - AI-powered research assistant',
  description: 'Transform your documents into dynamic conversations with AI',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <div id="root">{children}</div>
      </body>
    </html>
  )
} 