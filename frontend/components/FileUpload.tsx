type FileUploadProps = {
  toolName: string;
};

export default function FileUpload({ toolName }: FileUploadProps) {
  return (
    <div className="mt-5 rounded-2xl border border-blue-100 bg-slate-50 p-4 dark:border-slate-700 dark:bg-slate-950/50">
      <div className="rounded-2xl border-2 border-dashed border-blue-200 bg-white px-4 py-8 text-center transition hover:border-cyan-400 dark:border-slate-600 dark:bg-slate-900">
        <p className="text-sm font-semibold text-slate-900 dark:text-white">Upload files for {toolName}</p>
        <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">
          Drag & drop or choose files. No data saved, 100% private, browser-only.
        </p>
        <label className="mt-4 inline-flex cursor-pointer items-center rounded-full bg-primary px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-700">
          Choose files
          <input className="hidden" type="file" multiple />
        </label>
      </div>
    </div>
  );
}
