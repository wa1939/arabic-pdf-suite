type AdBannerProps = {
  label: string;
  size?: 'top' | 'side' | 'bottom';
};

const sizeClasses: Record<NonNullable<AdBannerProps['size']>, string> = {
  top: 'min-h-[96px]',
  side: 'min-h-[420px] sticky top-24',
  bottom: 'min-h-[120px]',
};

export default function AdBanner({ label, size = 'top' }: AdBannerProps) {
  return (
    <div
      className={`flex w-full items-center justify-center rounded-2xl border border-dashed border-sky-200 bg-white/85 p-6 text-center shadow-soft dark:border-slate-700 dark:bg-slate-900/80 ${sizeClasses[size]}`}
    >
      <div>
        <p className="text-xs font-semibold uppercase tracking-[0.3em] text-sky-600 dark:text-sky-400">
          Ad Space
        </p>
        <p className="mt-2 text-sm text-slate-600 dark:text-slate-300">{label}</p>
      </div>
    </div>
  );
}
