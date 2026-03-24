import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Arabic PDF Suite',
  description: 'Browser-only Arabic PDF tools with a clean single-page experience.',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>{children}</body>
    </html>
  );
}
