export default function Footer() {
  return (
    <footer className="mt-16 border-t border-slate-200/80 py-8 dark:border-slate-800">
      <div className="flex flex-col gap-3 text-center text-sm text-slate-600 dark:text-slate-400 md:flex-row md:items-center md:justify-between md:text-left">
        <p>No data saved, 100% private, browser-only.</p>
        <p>
          Built by Waleed ·{' '}
          <a
            href="https://walhamed.com"
            target="_blank"
            rel="noreferrer"
            className="font-semibold text-primary transition hover:text-accent"
          >
            walhamed.com
          </a>
        </p>
      </div>
    </footer>
  );
}
