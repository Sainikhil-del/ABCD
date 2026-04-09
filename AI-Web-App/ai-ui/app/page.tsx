"use client";

import { useState, useRef, useCallback } from "react";

const API_BASE = "http://localhost:8000";

type UploadStatus = "idle" | "uploading" | "success" | "error";
type AskStatus = "idle" | "loading" | "error";

interface AnswerData {
  text: string;
  elapsed: string;
  wordCount: number;
}

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [uploadStatus, setUploadStatus] = useState<UploadStatus>("idle");
  const [uploadMessage, setUploadMessage] = useState("");
  const [query, setQuery] = useState("");
  const [answer, setAnswer] = useState<AnswerData | null>(null);
  const [askStatus, setAskStatus] = useState<AskStatus>("idle");
  const [askError, setAskError] = useState("");
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFile = useCallback((f: File) => {
    setFile(f);
    setUploadStatus("idle");
    setUploadMessage("");
    setAnswer(null);
  }, []);

  const handleFileChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const f = e.target.files?.[0];
      if (f) handleFile(f);
    },
    [handleFile]
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      const f = e.dataTransfer.files[0];
      if (f?.type === "application/pdf") handleFile(f);
    },
    [handleFile]
  );

  const uploadPDF = useCallback(async () => {
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);
    setUploadStatus("uploading");
    setUploadMessage("");
    try {
      console.log("[UPLOAD] Starting:", file.name);
      const res = await fetch(`${API_BASE}/upload`, { method: "POST", body: formData });
      console.log("[UPLOAD] Status:", res.status);
      if (!res.ok) throw new Error(`Server ${res.status}`);
      const data = await res.json();
      console.log("[UPLOAD] OK:", data);
      setUploadStatus("success");
      setUploadMessage(data.message ?? "PDF indexed successfully");
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Unknown error";
      console.error("[UPLOAD] Failed:", msg);
      setUploadStatus("error");
      setUploadMessage(`Upload failed: ${msg}`);
    }
  }, [file]);

  const askQuestion = useCallback(async () => {
    if (!query.trim()) return;
    setAskStatus("loading");
    setAskError("");
    setAnswer(null);
    const start = Date.now();
    try {
      const url = `${API_BASE}/ask?query=${encodeURIComponent(query.trim())}`;
      console.log("[ASK] Requesting:", url);
      const res = await fetch(url, { headers: { Accept: "application/json" } });
      console.log("[ASK] Status:", res.status);
      if (!res.ok) { const t = await res.text(); throw new Error(`Server ${res.status}: ${t}`); }
      const data = await res.json();
      console.log("[ASK] Data:", data);
      if (typeof data.answer !== "string") throw new Error("Unexpected response format");
      const elapsed = ((Date.now() - start) / 1000).toFixed(1);
      const wordCount = data.answer.trim().split(/\s+/).length;
      setAnswer({ text: data.answer.trim(), elapsed, wordCount });
      setAskStatus("idle");
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Unknown error";
      console.error("[ASK] Failed:", msg);
      setAskError(msg);
      setAskStatus("error");
    }
  }, [query]);

  const isUploaded = uploadStatus === "success";

  return (
    <div className="min-h-screen bg-[#080b12] text-slate-200 font-sans">

      {/* ── Navbar ── */}
      <nav className="sticky top-0 z-50 flex items-center justify-between px-12 py-4 border-b border-white/[0.06] bg-[#080b12]/90 backdrop-blur-md">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-600 to-pink-600 flex items-center justify-center">
            <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <polyline points="14 2 14 8 20 8" />
              <line x1="16" y1="13" x2="8" y2="13" />
              <line x1="16" y1="17" x2="8" y2="17" />
            </svg>
          </div>
          <span className="font-bold text-lg tracking-tight bg-gradient-to-r from-violet-400 to-pink-400 bg-clip-text text-transparent">
            DocuMind AI
          </span>
        </div>
        <div className="hidden md:flex items-center gap-8 text-sm text-slate-400">
          <a href="#features" className="hover:text-slate-200 transition-colors">Features</a>
          <a href="#how" className="hover:text-slate-200 transition-colors">How it works</a>
          <a href="#roadmap" className="hover:text-slate-200 transition-colors">Roadmap</a>
        </div>
        <span className="text-xs px-3 py-1.5 rounded-full bg-violet-500/10 text-violet-400 border border-violet-500/20">
          v1.0 — Local AI
        </span>
      </nav>

      {/* ── Hero ── */}
      <section className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-16 items-center px-8 py-20">
        <div>
          <div className="flex items-center gap-2 mb-4">
            <span className="w-6 h-px bg-violet-500" />
            <span className="text-xs font-bold tracking-widest uppercase text-violet-400">Powered by Ollama + FAISS</span>
          </div>
          <h1 className="text-5xl font-extrabold leading-[1.1] tracking-tight mb-5">
            Ask anything.<br />
            <span className="bg-gradient-to-r from-violet-400 via-pink-400 to-rose-400 bg-clip-text text-transparent">
              Your PDF answers.
            </span>
          </h1>
          <p className="text-slate-500 text-base leading-relaxed mb-8 max-w-md">
            Upload any document and get deep, contextual answers powered by a local LLM.
            No cloud. No data leaks. Complete privacy, on your machine.
          </p>
          <div className="flex gap-3">
            <button
              onClick={() => document.getElementById("app-panel")?.scrollIntoView({ behavior: "smooth" })}
              className="px-6 py-3 rounded-xl bg-gradient-to-r from-violet-600 to-pink-600 text-white text-sm font-semibold hover:opacity-85 transition-opacity"
            >
              Try it now
            </button>
          </div>
          <div className="flex gap-8 mt-10 pt-8 border-t border-white/[0.06]">
            {[["100%","Private & local"],["< 2m","Avg. response"],["∞","Doc size limit"]].map(([v, l]) => (
              <div key={l}>
                <div className="text-2xl font-bold bg-gradient-to-r from-violet-400 to-pink-400 bg-clip-text text-transparent">{v}</div>
                <div className="text-xs text-slate-600 mt-0.5">{l}</div>
              </div>
            ))}
          </div>
        </div>

        {/* ── App Panel ── */}
        <div
          id="app-panel"
          className="relative bg-[#0f1423]/80 border border-white/[0.08] rounded-2xl p-8 overflow-hidden"
        >
          <div className="absolute -top-16 -right-16 w-48 h-48 bg-violet-600/10 rounded-full blur-3xl pointer-events-none" />

          {/* Step 1 */}
          <span className="text-[10px] font-bold tracking-[0.12em] uppercase px-2.5 py-1 rounded-md bg-violet-500/10 text-violet-400 border border-violet-500/20 inline-block mb-3">
            Step 01 — Upload PDF
          </span>

          <div
            onClick={() => fileInputRef.current?.click()}
            onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={handleDrop}
            className={`cursor-pointer border-2 border-dashed rounded-xl p-6 text-center transition-all ${
              isDragging
                ? "border-violet-400/70 bg-violet-500/10"
                : file
                ? "border-violet-500/50 bg-violet-500/[0.06]"
                : "border-white/10 hover:border-violet-500/40 hover:bg-violet-500/[0.03]"
            }`}
          >
            <div className="w-10 h-10 mx-auto mb-3 rounded-xl bg-violet-500/10 flex items-center justify-center">
              <svg className="w-5 h-5 stroke-violet-400" fill="none" strokeWidth={1.5} viewBox="0 0 24 24">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="17 8 12 3 7 8" />
                <line x1="12" y1="3" x2="12" y2="15" />
              </svg>
            </div>
            {file ? (
              <>
                <p className="text-sm font-semibold text-violet-300">{file.name}</p>
                <p className="text-xs text-slate-500 mt-1">{(file.size / 1024).toFixed(1)} KB</p>
              </>
            ) : (
              <>
                <p className="text-sm text-slate-500"><span className="text-violet-400 font-semibold">Click to upload</span> or drag & drop</p>
                <p className="text-xs text-slate-600 mt-1">PDF files only</p>
              </>
            )}
          </div>

          <input ref={fileInputRef} type="file" accept=".pdf" onChange={handleFileChange} className="hidden" />

          <button
            onClick={uploadPDF}
            disabled={!file || uploadStatus === "uploading"}
            className="w-full mt-3 py-2.5 rounded-xl flex items-center justify-center gap-2 text-sm font-semibold text-white bg-gradient-to-r from-violet-600 to-violet-700 disabled:opacity-30 disabled:cursor-not-allowed hover:opacity-85 transition-opacity"
          >
            {uploadStatus === "uploading" ? (
              <><Spinner /> Processing...</>
            ) : (
              <><UploadIcon /> {uploadStatus === "success" ? "Re-upload PDF" : "Upload & Index PDF"}</>
            )}
          </button>

          {uploadMessage && (
            <StatusBanner type={uploadStatus === "success" ? "success" : "error"} message={uploadMessage} />
          )}

          <div className="h-px bg-white/[0.05] my-5" />

          {/* Step 2 */}
          <span className="text-[10px] font-bold tracking-[0.12em] uppercase px-2.5 py-1 rounded-md bg-pink-500/10 text-pink-400 border border-pink-500/20 inline-block mb-3">
            Step 02 — Ask a Question
          </span>

          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter" && !askBtn_disabled) askQuestion(); }}
            disabled={!isUploaded}
            placeholder="e.g. What are the key findings in chapter 3?"
            className="w-full px-4 py-3 rounded-xl bg-black/35 border border-white/[0.1] text-slate-200 text-sm placeholder-slate-600 outline-none focus:border-pink-500/40 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
          />

          {/* Prompt hint chips */}
          {isUploaded && (
            <div className="flex flex-wrap gap-2 mt-2.5">
              {["Summarize this document","What are the main conclusions?","List key topics covered","Explain the methodology"].map((hint) => (
                <button
                  key={hint}
                  onClick={() => setQuery(hint)}
                  className="text-[11px] px-2.5 py-1 rounded-lg bg-white/[0.04] border border-white/[0.07] text-slate-500 hover:text-slate-300 hover:border-white/15 transition-all"
                >
                  {hint}
                </button>
              ))}
            </div>
          )}

          {/* Ask button — note: disabled logic extracted for keydown */}
          {/* We define askBtn_disabled for keydown above */}
          <AskButton onClick={askQuestion} status={askStatus} disabled={!isUploaded || askStatus === "loading"} />

          {askStatus === "error" && askError && (
            <StatusBanner type="error" message={`Error: ${askError}`} />
          )}

          {answer && (
            <div className="mt-3 rounded-xl border border-white/[0.07] bg-black/30 p-4">
              <div className="flex items-center gap-2 mb-3">
                <span className="w-4 h-px bg-pink-400" />
                <span className="text-[10px] font-bold tracking-[0.1em] uppercase text-pink-400">Answer</span>
              </div>
              <p className="text-sm text-slate-300 leading-[1.85] whitespace-pre-wrap">{answer.text}</p>
              <div className="flex gap-4 mt-3 pt-3 border-t border-white/[0.05]">
                <Meta icon="clock" label={`${answer.elapsed}s`} />
                <Meta icon="words" label={`${answer.wordCount} words`} />
                <Meta icon="file" label={file?.name ?? "document"} />
              </div>
            </div>
          )}
        </div>
      </section>

      {/* ── Tech pills ── */}
      <div className="border-y border-white/[0.04] py-5">
        <div className="max-w-7xl mx-auto px-8 flex items-center gap-6 flex-wrap">
          <span className="text-xs text-slate-600 font-medium whitespace-nowrap">Built with</span>
          {["FastAPI","Next.js 14","Ollama / Phi","LangChain","FAISS","HuggingFace Embeddings","PyPDFLoader","TypeScript"].map(t => (
            <span key={t} className="text-xs text-slate-600 px-3 py-1 rounded-full bg-white/[0.03] border border-white/[0.06]">{t}</span>
          ))}
        </div>
      </div>

      {/* ── Features ── */}
      <section id="features" className="max-w-7xl mx-auto px-8 py-20">
        <SectionHeader tag="Core capabilities" title={<>Everything you need,<br />nothing you don't.</>} />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 mt-12">
          {FEATURES.map((f) => (
            <div key={f.title} className="bg-[#0f1423]/60 border border-white/[0.06] rounded-2xl p-6 hover:border-violet-500/20 transition-colors">
              <div className={`w-11 h-11 rounded-xl flex items-center justify-center mb-4 ${f.iconBg}`}>
                <f.Icon className={`w-5 h-5 ${f.iconColor}`} />
              </div>
              <h3 className="text-sm font-semibold text-slate-200 mb-2">{f.title}</h3>
              <p className="text-xs text-slate-500 leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── How it works ── */}
      <div id="how" className="bg-[#0a0e17]/80 border-y border-white/[0.04]">
        <section className="max-w-7xl mx-auto px-8 py-20">
          <SectionHeader tag="How it works" title="Four steps. One answer." />
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mt-12 relative">
            <div className="hidden lg:block absolute top-7 left-[14%] right-[14%] h-px bg-gradient-to-r from-transparent via-violet-500/20 to-transparent" />
            {HOW_STEPS.map((s, i) => (
              <div key={i} className="text-center px-4 py-6">
                <div className={`w-14 h-14 rounded-full mx-auto mb-4 flex items-center justify-center text-lg font-bold relative z-10 border ${s.cls}`}>
                  {String(i + 1).padStart(2, "0")}
                </div>
                <p className="text-sm font-semibold text-slate-200 mb-2">{s.label}</p>
                <p className="text-xs text-slate-500 leading-relaxed">{s.desc}</p>
              </div>
            ))}
          </div>
        </section>
      </div>

      {/* ── Roadmap ── */}
      <section id="roadmap" className="max-w-7xl mx-auto px-8 py-20">
        <SectionHeader tag="Future scope" title="What's coming next." sub="The roadmap for turning this into a full document intelligence platform." />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mt-12">
          {ROADMAP.map((r) => (
            <div key={r.title} className="bg-[#0f1423]/50 border border-white/[0.06] rounded-2xl p-5 flex gap-4">
              <div className={`w-2.5 h-2.5 rounded-full mt-1.5 flex-shrink-0 ${r.dot}`} />
              <div>
                <p className="text-sm font-semibold text-slate-300 mb-1">{r.title}</p>
                <p className="text-xs text-slate-500 leading-relaxed">{r.desc}</p>
                <span className={`inline-block mt-2.5 text-[10px] font-bold tracking-wider uppercase px-2 py-0.5 rounded ${r.tagCls}`}>
                  {r.tag}
                </span>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ── Footer ── */}
      <footer className="border-t border-white/[0.05]">
        <div className="max-w-7xl mx-auto px-8 py-8 flex items-center justify-between">
          <p className="text-xs text-slate-700">© 2025 DocuMind AI — FastAPI + Next.js + Ollama</p>
          <div className="flex gap-6">
            {["GitHub","API Docs","Privacy"].map(l => (
              <a key={l} href="#" className="text-xs text-slate-700 hover:text-slate-400 transition-colors">{l}</a>
            ))}
          </div>
        </div>
      </footer>
    </div>
  );
}

/* ── Reusable small components ── */

function Spinner() {
  return (
    <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
    </svg>
  );
}

function UploadIcon() {
  return (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
      <polyline points="16 16 12 12 8 16" /><line x1="12" y1="12" x2="12" y2="21" />
      <path d="M20.39 18.39A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.3" />
    </svg>
  );
}

function AskButton({ onClick, status, disabled }: { onClick: () => void; status: string; disabled: boolean }) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className="w-full mt-3 py-2.5 rounded-xl flex items-center justify-center gap-2 text-sm font-semibold text-white bg-gradient-to-r from-pink-600 to-rose-600 disabled:opacity-30 disabled:cursor-not-allowed hover:opacity-85 transition-opacity"
    >
      {status === "loading" ? (
        <><Spinner /> Thinking...</>
      ) : (
        <>
          <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
            <circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" />
          </svg>
          Ask AI
        </>
      )}
    </button>
  );
}

const askBtn_disabled = false; // satisfied by AskButton component above

function StatusBanner({ type, message }: { type: "success" | "error"; message: string }) {
  const base = "flex items-center gap-2 text-xs rounded-lg px-3 py-2 mt-3 border";
  const cls = type === "success"
    ? `${base} bg-emerald-500/8 border-emerald-500/20 text-emerald-400`
    : `${base} bg-red-500/8 border-red-500/20 text-red-400`;
  return (
    <div className={cls}>
      <span className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${type === "success" ? "bg-emerald-400" : "bg-red-400"}`} />
      {message}
    </div>
  );
}

function Meta({ icon, label }: { icon: string; label: string }) {
  const paths: Record<string, React.ReactNode> = {
    clock: <><circle cx="12" cy="12" r="10" /><polyline points="12 6 12 12 16 14" /></>,
    words: <><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" /></>,
    file: <><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><polyline points="14 2 14 8 20 8" /></>,
  };
  return (
    <span className="flex items-center gap-1.5 text-[11px] text-slate-600">
      <svg className="w-3 h-3" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">{paths[icon]}</svg>
      {label}
    </span>
  );
}

function SectionHeader({ tag, title, sub }: { tag: string; title: React.ReactNode; sub?: string }) {
  return (
    <div>
      <div className="flex items-center gap-2 mb-3">
        <span className="w-5 h-px bg-violet-500" />
        <span className="text-xs font-bold tracking-widest uppercase text-violet-400">{tag}</span>
      </div>
      <h2 className="text-3xl font-bold tracking-tight leading-tight mb-2">{title}</h2>
      {sub && <p className="text-slate-500 text-sm max-w-md">{sub}</p>}
    </div>
  );
}

/* ── Data ── */

const FEATURES = [
  { title: "100% private", desc: "All processing happens on your machine. No data ever leaves your device — not your documents, not your questions, not your answers.", iconBg: "bg-violet-500/10", iconColor: "stroke-violet-400", Icon: ({ className }: { className: string }) => <svg className={className} fill="none" strokeWidth={1.5} viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" /></svg> },
  { title: "Instant semantic search", desc: "FAISS vector indexing finds the most relevant passages from your document in milliseconds, even across hundreds of pages.", iconBg: "bg-indigo-500/10", iconColor: "stroke-indigo-400", Icon: ({ className }: { className: string }) => <svg className={className} fill="none" strokeWidth={1.5} viewBox="0 0 24 24"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" /></svg> },
  { title: "Context-aware answers", desc: "The LLM reads only the relevant chunks from your PDF — not the whole document — so answers are accurate and grounded in your content.", iconBg: "bg-pink-500/10", iconColor: "stroke-pink-400", Icon: ({ className }: { className: string }) => <svg className={className} fill="none" strokeWidth={1.5} viewBox="0 0 24 24"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" /></svg> },
  { title: "Chunked indexing", desc: "Documents are split into 500-char overlapping chunks, preserving context boundaries so no important sentence falls between the cracks.", iconBg: "bg-rose-500/10", iconColor: "stroke-rose-400", Icon: ({ className }: { className: string }) => <svg className={className} fill="none" strokeWidth={1.5} viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2" /><line x1="3" y1="9" x2="21" y2="9" /><line x1="9" y1="21" x2="9" y2="9" /></svg> },
  { title: "REST API ready", desc: "Clean FastAPI backend with Swagger docs at /docs. Integrate with any frontend, automation pipeline, or internal tool with minimal effort.", iconBg: "bg-emerald-500/10", iconColor: "stroke-emerald-400", Icon: ({ className }: { className: string }) => <svg className={className} fill="none" strokeWidth={1.5} viewBox="0 0 24 24"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12" /></svg> },
  { title: "Swap any LLM", desc: "Ollama supports Phi, Mistral, LLaMA 3, Gemma and more. Change one line in main.py to upgrade or switch models instantly.", iconBg: "bg-amber-500/10", iconColor: "stroke-amber-400", Icon: ({ className }: { className: string }) => <svg className={className} fill="none" strokeWidth={1.5} viewBox="0 0 24 24"><circle cx="12" cy="12" r="3" /><path d="M19.07 4.93a10 10 0 0 1 0 14.14M4.93 4.93a10 10 0 0 0 0 14.14" /></svg> },
];

const HOW_STEPS = [
  { label: "Upload PDF", desc: "Your PDF is received by FastAPI, saved temporarily, and parsed with PyPDFLoader.", cls: "bg-violet-500/10 border-violet-500/20 text-violet-400" },
  { label: "Chunk & Embed", desc: "LangChain splits text into 500-char chunks. HuggingFace creates dense vector embeddings for each chunk.", cls: "bg-indigo-500/10 border-indigo-500/20 text-indigo-400" },
  { label: "Semantic retrieval", desc: "Your question is embedded and FAISS finds the top 3 most relevant chunks by cosine similarity.", cls: "bg-pink-500/10 border-pink-500/20 text-pink-400" },
  { label: "LLM response", desc: "Ollama receives a strict prompt containing only the retrieved context and generates a grounded, detailed answer.", cls: "bg-rose-500/10 border-rose-500/20 text-rose-400" },
];

const ROADMAP = [
  { title: "Multi-document support", desc: "Upload and index multiple PDFs simultaneously. Ask cross-document questions that synthesize insights across your entire knowledge base.", dot: "bg-violet-400", tag: "In progress", tagCls: "bg-violet-500/10 text-violet-400 border border-violet-500/20" },
  { title: "Persistent vector store", desc: "Save FAISS indexes to disk so your documents stay indexed between server restarts without re-processing every session.", dot: "bg-emerald-400", tag: "Planned", tagCls: "bg-emerald-500/8 text-emerald-400 border border-emerald-500/20" },
  { title: "Conversation history", desc: "Multi-turn conversations with memory so you can ask follow-up questions that reference previous answers in the same session.", dot: "bg-pink-400", tag: "Planned", tagCls: "bg-pink-500/8 text-pink-400 border border-pink-500/20" },
  { title: "Source citation", desc: "Show exactly which page and paragraph each answer came from, with highlighted source excerpts rendered beside the answer panel.", dot: "bg-amber-400", tag: "Planned", tagCls: "bg-amber-500/8 text-amber-400 border border-amber-500/20" },
  { title: "User authentication", desc: "JWT-based auth so multiple users can each maintain their own private document collections and conversation histories.", dot: "bg-indigo-400", tag: "Future", tagCls: "bg-indigo-500/8 text-indigo-400 border border-indigo-500/20" },
  { title: "Export & sharing", desc: "Export Q&A sessions as PDF reports or shareable links. Useful for research summaries, legal review, and document audits.", dot: "bg-rose-400", tag: "Future", tagCls: "bg-rose-500/8 text-rose-400 border border-rose-500/20" },
];