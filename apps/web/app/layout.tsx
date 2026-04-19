import type { Metadata } from 'next';
import './globals.css';
import { SiteHeader } from '../components/site-header';

export const metadata: Metadata = {
  title: 'CaseFlow AI Demo',
  description: 'Synthetic demo shell for the CaseFlow workflow and approval queue.'
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <div className="app-frame">
          <SiteHeader />
          {children}
          <footer className="footer">
            <span>Synthetic demo only.</span>
            <span>Human review required before any external action.</span>
          </footer>
        </div>
      </body>
    </html>
  );
}
