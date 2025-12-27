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
      <body className="antialiased">
        <ToastContainer />
        <SidebarLayout>{children}</SidebarLayout>
      </body>
    </html>
  );
}
