'use client';
import { useState } from 'react';
import { Upload, FileText, CheckCircle2, AlertTriangle, Loader2, ShieldCheck } from 'lucide-react';
import { api } from '@/lib/api';
import AppShell from '@/components/AppShell';

export default function DocumentsPage(){
  const [file,setFile]=useState<File|null>(null); const [busy,setBusy]=useState(false); const [result,setResult]=useState<any>(null); const [error,setError]=useState('');
  async function process(){
    if(!file) return; setBusy(true); setError(''); setResult(null);
    try { setResult(await api.uploadDocument(file)); } catch(e:any){ setError(e.message||'Unable to process document.'); } finally { setBusy(false); }
  }
  return <AppShell>
    <div className="mx-auto max-w-5xl space-y-6 p-4 md:p-8">
      <div><div className="mb-2 inline-flex rounded-full border border-amber-200 bg-amber-50 px-3 py-1 text-xs font-semibold text-amber-800">DEMO OCR / LOCAL PROCESSING</div><h1 className="text-3xl font-bold tracking-tight">Document & OCR Assistant</h1><p className="mt-2 max-w-2xl text-slate-600">Upload a document to validate it, attempt local text extraction, detect language and classify the document type.</p></div>
      <div className="grid gap-6 lg:grid-cols-[1.15fr_.85fr]">
        <section className="rounded-3xl border bg-white p-6 shadow-sm">
          <div className="rounded-2xl border-2 border-dashed border-slate-300 bg-slate-50 p-10 text-center">
            <Upload className="mx-auto h-10 w-10 text-slate-500"/><h2 className="mt-4 font-semibold">Upload document</h2><p className="mt-1 text-sm text-slate-500">PDF, JPG, JPEG or PNG · Maximum 10 MB</p>
            <input className="mx-auto mt-6 block max-w-full text-sm" type="file" accept=".pdf,.jpg,.jpeg,.png" onChange={e=>setFile(e.target.files?.[0]||null)}/>
            {file && <div className="mt-4 rounded-xl bg-white p-3 text-left text-sm"><b>{file.name}</b><span className="ml-2 text-slate-500">{(file.size/1024/1024).toFixed(2)} MB</span></div>}
            <button onClick={process} disabled={!file||busy} className="mt-5 inline-flex items-center gap-2 rounded-xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white disabled:opacity-50">{busy?<Loader2 className="h-4 w-4 animate-spin"/>:<FileText className="h-4 w-4"/>}{busy?'Processing…':'Validate & Process'}</button>
          </div>
          {error && <div className="mt-4 flex gap-2 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700"><AlertTriangle className="h-5 w-5 shrink-0"/>{error}</div>}
        </section>
        <section className="rounded-3xl border bg-white p-6 shadow-sm"><h2 className="font-semibold">Workflow</h2><div className="mt-5 space-y-4">{['UPLOAD','VALIDATE','TEXT EXTRACTION','LANGUAGE DETECTION','DOCUMENT CLASSIFICATION','DISPLAY RESULTS'].map((x,i)=><div className="flex items-center gap-3" key={x}><div className="flex h-8 w-8 items-center justify-center rounded-full bg-slate-100 text-xs font-bold">{i+1}</div><span className="text-sm font-medium">{x}</span></div>)}</div><div className="mt-6 rounded-xl bg-amber-50 p-4 text-xs text-amber-800">OCR output is assistive only. Always verify the original document.</div></section>
      </div>
      {result && <section className="rounded-3xl border bg-white p-6 shadow-sm"><div className="flex flex-wrap items-center justify-between gap-3"><div><div className="flex items-center gap-2"><CheckCircle2 className="h-5 w-5 text-emerald-600"/><h2 className="font-semibold">Processing result</h2></div><p className="mt-1 text-xs text-slate-500">{result.mode}</p></div><div className="flex items-center gap-2 rounded-full bg-slate-100 px-3 py-1 text-xs"><ShieldCheck className="h-4 w-4"/>{result.document_type}</div></div><div className="mt-5 grid gap-3 sm:grid-cols-2"><div className="rounded-xl bg-slate-50 p-4"><span className="text-xs text-slate-500">Language</span><p className="font-semibold">{result.language}</p></div><div className="rounded-xl bg-slate-50 p-4"><span className="text-xs text-slate-500">File size</span><p className="font-semibold">{(result.size_bytes/1024/1024).toFixed(2)} MB</p></div></div><div className="mt-5"><h3 className="text-sm font-semibold">Extracted text</h3><pre className="mt-2 max-h-80 overflow-auto whitespace-pre-wrap rounded-xl bg-slate-950 p-4 text-xs text-slate-100">{result.extracted_text}</pre></div></section>}
    </div>
  </AppShell>
}
