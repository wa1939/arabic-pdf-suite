'use client';

import { useEffect, useState } from 'react';
import AdBanner from '@/components/AdBanner';
import Footer from '@/components/Footer';
import ToolCard from '@/components/ToolCard';

const tools = [
  {
    id: 'merge',
    icon: '🧩',
    name: 'Merge PDF',
    description: 'Combine multiple Arabic PDFs into one clean final file.',
  },
  {
    id: 'split',
    icon: '✂️',
    name: 'Split PDF',
    description: 'Extract pages or split long documents into smaller parts.',
  },
  {
    id: 'compress',
    icon: '🗜️',
    name: 'Compress PDF',
    description: 'Reduce file size while keeping Arabic text readable.',
  },
  {
    id: 'word',
    icon: '📝',
    name: 'PDF to Word',
    description: 'Convert Arabic PDF content into editable Word documents.',
  },
  {
    id: 'excel',
    icon: '📊',
    name: 'PDF to Excel',
    description: 'Pull Arabic tables into spreadsheet-ready Excel files.',
  },
  {
    id: 'powerpoint',
    icon: '📽️',
    name: 'PDF to PowerPoint',
    description: 'Turn PDFs into slides you can actually edit.',
  },
  {
    id: 'jpg',
    icon: '🖼️',
    name: 'PDF to JPG',
    description: 'Export sharp page previews as images for sharing.',
  },
  {
    id: 'ocr',
    icon: '🔎',
    name: 'Arabic OCR',
    description: 'Extract searchable Arabic text from scanned pages.',
  },
  {
    id: 'watermark',
    icon: '💧',
    name: 'Add Watermark',
    description: 'Apply branded text or logo watermarks in seconds.',
  },
  {
    id: 'rotate',
    icon: '🔄',
    name: 'Rotate PDF',
    description: 'Fix sideways scans and awkward page orientation.',
  },
  {
    id: 'unlock',
    icon: '🔓',
    name: 'Unlock PDF',
    description: 'Remove open-password restrictions from your own files.',
  },
  {
    id: 'protect',
    icon: '🛡️',
    name: 'Protect PDF',
    description: 'Add passwords and simple access control to documents.',
  },
  {
    id: 'number',
    icon: '🔢',
    name: 'Page Numbers',
    description: 'Add neat page numbering without mangling the layout.',
  },
  {
    id: 'organize',
    icon: '🗂️',
    name: 'Organize PDF',
    description: 'Reorder, delete, and tidy pages with a cleaner workflow.',
  },
  {
    id: 'html',
    icon: '🌐',
    name: 'PDF to HTML',
    description: 'Convert documents into lightweight web-ready pages.',
  },
] as const;

export default function HomePage() {
  const [selectedTool, setSelectedTool] = useState<string>(tools[0].id);
  const [theme, setTheme] = useState<'light' | 'dark'>('light');

  useEffect(() => {
    const storedTheme = window.localStorage.getItem('arabic-pdf-theme');
    const preferredDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const nextTheme = storedTheme === 'dark' || (!storedTheme && preferredDark) ? 'dark' : 'light';

    setTheme(nextTheme);
    document.documentElement.classList.toggle('dark', nextTheme === 'dark');
  }, []);

  const toggleTheme = () => {
    const nextTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(nextTheme);
    document.documentElement.classList.toggle('dark', nextTheme === 'dark');
    window.localStorage.setItem('arabic-pdf-theme', nextTheme);
  };

  return (
    <main className="min-h-screen bg-slate-50 text-slate-900 transition-colors dark:bg-slate-950 dark:text-white">
      <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        <header className="mb-8 flex items-center justify-between gap-4 rounded-3xl border border-slate-200 bg-white/90 px-6 py-4 shadow-soft backdrop-blur dark:border-slate-800 dark:bg-slate-900/85">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.3em] text-cyan-600 dark:text-cyan-400">
              Arabic PDF Suite
            </p>
            <h1 className="mt-1 text-2xl font-bold tracking-tight">Fast Arabic PDF tools, all on one page.</h1>
          </div>
          <button
            type="button"
            onClick={toggleTheme}
            aria-label="Toggle dark mode"
            className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-slate-50 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:border-primary hover:text-primary dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200"
          >
            <span>{theme === 'light' ? '🌙' : '☀️'}</span>
            {theme === 'light' ? 'Dark' : 'Light'}
          </button>
        </header>

        <AdBanner label="Top banner ad · sponsor the highest-converting spot" size="top" />

        <section className="mt-8 grid gap-8 lg:grid-cols-[minmax(0,1fr)_300px]">
          <div>
            <div className="mb-6 max-w-3xl">
              <h2 className="text-3xl font-bold tracking-tight">Every tool visible. Zero clutter.</h2>
              <p className="mt-3 text-base leading-7 text-slate-600 dark:text-slate-400">
                Pick a tool and upload inline. No detours, no nonsense. No data saved, 100% private,
                browser-only.
              </p>
            </div>

            <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
              {tools.map((tool) => (
                <ToolCard
                  key={tool.id}
                  tool={tool}
                  isSelected={selectedTool === tool.id}
                  onSelect={setSelectedTool}
                />
              ))}
            </div>
          </div>

          <aside>
            <AdBanner label="Sidebar ad · 300×600 premium placement" size="side" />
          </aside>
        </section>

        <div className="mt-10">
          <AdBanner label="Bottom banner ad · final high-visibility slot" size="bottom" />
        </div>

        <Footer />
      </div>
    </main>
  );
}
