import type { Metadata } from 'next';
import './globals.css';
import { SiteHeader } from '../components/site-header';

export const metadata: Metadata = {
  title: 'CaseFlow AI 审查工作台',
  description: '面向 NZ Property Settlement 的案件审查与人工审批工作台。'
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <div className="app-frame">
          <SiteHeader />
          {children}
          <footer className="footer">
            <span>当前页面可在 Synthetic Demo 与 Live Backend 之间切换。</span>
            <span>所有外部动作必须经过人工审批后执行。</span>
          </footer>
        </div>
      </body>
    </html>
  );
}
