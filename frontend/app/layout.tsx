import './globals.css'
import ToastContainer from '../components/ToastContainer';

export const metadata = {
  title: 'AI Copilot - Enterprise Assistant',
  description: 'Modern AI Copilot interface with enterprise-grade design',
}

import SidebarLayout from './SidebarLayout';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head>
        <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png" />
        <link rel="icon" type="image/png" sizes="192x192" href="/icon-192.png" />
        <link rel="icon" type="image/png" sizes="512x512" href="/icon-512.png" />
        <link rel="icon" href="/favicon.ico" />
        <link rel="manifest" href="/site.webmanifest" />
        <meta name="theme-color" content="#ffffff" />
      </head>
      <body className="antialiased">
        <ToastContainer />
        <SidebarLayout>{children}</SidebarLayout>
      </body>
    </html>
  );
}
