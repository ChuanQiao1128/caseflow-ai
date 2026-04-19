import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'CaseFlow Demo',
  description: 'Synthetic demo shell for the CaseFlow workflow and approval queue.'
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
