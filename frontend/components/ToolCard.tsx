'use client';

import FileUpload from './FileUpload';

type Tool = {
  id: string;
  icon: string;
  name: string;
  description: string;
};

type ToolCardProps = {
  tool: Tool;
  isSelected: boolean;
  onSelect: (toolId: string) => void;
};

export default function ToolCard({ tool, isSelected, onSelect }: ToolCardProps) {
  return (
    <article className="rounded-3xl border border-slate-200 bg-white p-6 shadow-soft transition hover:-translate-y-0.5 hover:shadow-lg dark:border-slate-800 dark:bg-slate-900">
      <div className="flex items-start justify-between gap-4">
        <div>
          <span className="inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-50 text-2xl dark:bg-slate-800">
            {tool.icon}
          </span>
          <h3 className="mt-4 text-lg font-semibold text-slate-900 dark:text-white">{tool.name}</h3>
          <p className="mt-2 text-sm leading-6 text-slate-600 dark:text-slate-400">{tool.description}</p>
        </div>
      </div>

      <button
        type="button"
        onClick={() => onSelect(tool.id)}
        className={`mt-6 inline-flex items-center rounded-full px-4 py-2 text-sm font-semibold transition ${
          isSelected
            ? 'bg-cyan-600 text-white hover:bg-cyan-700'
            : 'bg-primary text-white hover:bg-blue-700'
        }`}
      >
        {isSelected ? 'Selected' : 'Select'}
      </button>

      {isSelected ? <FileUpload toolName={tool.name} /> : null}
    </article>
  );
}
