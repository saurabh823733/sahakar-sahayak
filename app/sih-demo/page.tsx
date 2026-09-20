'use client';
import Link from 'next/link';
import { ArrowRight, BrainCircuit, CheckCircle2, Database, FileSearch, Globe2, Landmark, Mic, Network, Search, ShieldCheck, Sparkles, Users, Workflow } from 'lucide-react';

const architecture = [
  ['Citizen', Users, 'Natural-language need'],
  ['Web / Voice Interface', Globe2, 'Text + speech'],
  ['Language Detection', Sparkles, 'English • Hindi • Marathi • Romanized'],
  ['Intent + Entity Understanding', BrainCircuit, 'Need, location, occupation, purpose'],
  ['AI Orchestrator', Workflow, 'Context-aware local reasoning'],
  ['Scheme Knowledge Base', Database, 'Structured scheme information'],
  ['Eligibility Engine', ShieldCheck, 'Potential match + missing information'],
  ['Document / OCR Engine', FileSearch, 'Validation + demo extraction'],
  ['Response Generator', Network, 'Guidance + verification notes'],
  ['Official Sources', Landmark, 'Citizen verifies current rules'],
];

const pillars = [
  ['Multilingual by design', 'Understand English, Hindi, Marathi, plus Romanized Hindi/Marathi without forcing a language selector.'],
  ['Explainable matching', 'Show why a scheme may match and what information is still missing instead of fake confidence scores.'],
  ['Offline-friendly AI core', 'Deterministic local language, intent, entity and matching engines keep the prototype usable without a paid AI key.'],
  ['Human-verification boundary', 'Government eligibility and submission are never represented as guaranteed when the platform is only providing guidance.'],
];

const journey = [
  ['01', 'ASK', 'Citizen types or speaks a need.'],
  ['02', 'UNDERSTAND', 'Language, intent and useful entities are extracted.'],
  ['03', 'MATCH', 'Relevant schemes and assistance paths are identified.'],
  ['04', 'VERIFY', 'Official sources and missing information are surfaced.'],
  ['05', 'APPLY', 'The citizen receives step-by-step application guidance.'],
];

export default function Page(){
  return <div className="gradient-civic min-h-[calc(100vh-4rem)]">
    <section className="grid-bg border-b">
      <div className="mx-auto max-w-7xl px-5 py-14 lg:py-20">
        <div className="flex flex-wrap items-center gap-2 text-xs font-bold uppercase tracking-wider text-blue-700">
          <span className="rounded-full border border-blue-200 bg-white px-3 py-1.5">Smart India Hackathon Demo</span>
          <span className="rounded-full border border-amber-200 bg-amber-50 px-3 py-1.5 text-amber-700">DEMO / SIMULATED SERVICES</span>
        </div>
        <div className="mt-7 grid gap-10 lg:grid-cols-[1.1fr_.9fr] lg:items-end">
          <div>
            <p className="text-sm font-semibold text-slate-500">AI-POWERED MULTILINGUAL GOVERNMENT & COOPERATIVE ASSISTANCE</p>
            <h1 className="mt-3 text-4xl font-black tracking-tight text-[#0b1f3a] sm:text-6xl">SAHAKAR <span className="text-blue-600">SAHAYAK</span></h1>
            <p className="mt-5 max-w-3xl text-xl font-semibold text-slate-700">A citizen-first layer for understanding schemes, eligibility, documents and public-service guidance.</p>
            <p className="mt-4 max-w-3xl text-base leading-7 text-slate-600">The prototype combines multilingual conversation, explainable scheme matching, eligibility guidance, document assistance, grievance guidance and cooperative-service discovery in one workflow.</p>
            <div className="mt-7 flex flex-wrap gap-3">
              <Link href="/assistant" className="inline-flex items-center gap-2 rounded-xl bg-[#0b1f3a] px-5 py-3.5 font-semibold text-white">Run live demo <ArrowRight size={18}/></Link>
              <Link href="/schemes" className="inline-flex items-center gap-2 rounded-xl border bg-white px-5 py-3.5 font-semibold text-slate-800">Explore scheme engine</Link>
            </div>
          </div>
          <div className="card rounded-3xl bg-white p-6">
            <div className="flex items-center justify-between"><div><p className="font-bold text-[#0b1f3a]">Prototype status</p><p className="text-xs text-slate-500">Local-first SIH demonstration</p></div><span className="rounded-full bg-green-50 px-3 py-1 text-xs font-bold text-green-700">RUNNABLE</span></div>
            <div className="mt-5 grid grid-cols-2 gap-3">
              {['18 user-facing routes','FastAPI REST backend','SQLite + SQLAlchemy','English / Hindi / Marathi','Context-aware assistant','Demo OCR workflow'].map(x=><div key={x} className="rounded-xl border bg-slate-50 p-3 text-sm font-semibold text-slate-700"><CheckCircle2 className="mb-2 text-green-600" size={17}/>{x}</div>)}
            </div>
          </div>
        </div>
      </div>
    </section>

    <section className="mx-auto max-w-7xl px-5 py-16">
      <div className="max-w-2xl"><p className="text-sm font-bold uppercase tracking-wider text-blue-600">Problem → solution</p><h2 className="mt-2 text-3xl font-black text-[#0b1f3a]">Turn fragmented information into guided citizen journeys.</h2></div>
      <div className="mt-8 grid gap-5 md:grid-cols-2">
        <div className="card rounded-2xl p-6"><p className="font-bold text-slate-800">Current challenges</p><ul className="mt-4 space-y-3 text-sm leading-6 text-slate-600">{['Scheme information can be difficult to discover and understand.','Citizens may not know which documents or next steps are relevant.','Language and literacy differences can make digital services harder to navigate.','Different assistance needs often require moving between separate information sources.'].map(x=><li key={x} className="flex gap-3"><span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-amber-500"/>{x}</li>)}</ul></div>
        <div className="rounded-2xl bg-[#0b1f3a] p-6 text-white shadow-xl"><p className="font-bold">Proposed solution</p><p className="mt-4 text-sm leading-7 text-blue-100">Sahakar Sahayak acts as an intelligent guidance layer: citizens describe their need naturally, the system interprets it, connects it to structured scheme knowledge, asks only necessary questions, and presents explainable next steps with official verification reminders.</p><div className="mt-5 grid grid-cols-2 gap-3 text-xs font-semibold"><div className="rounded-xl bg-white/10 p-3">Understand</div><div className="rounded-xl bg-white/10 p-3">Match</div><div className="rounded-xl bg-white/10 p-3">Explain</div><div className="rounded-xl bg-white/10 p-3">Guide</div></div></div>
      </div>
    </section>

    <section className="border-y bg-white"><div className="mx-auto max-w-7xl px-5 py-16"><div className="max-w-2xl"><p className="text-sm font-bold uppercase tracking-wider text-green-700">Key innovation</p><h2 className="mt-2 text-3xl font-black text-[#0b1f3a]">Designed for understanding, not just searching.</h2></div><div className="mt-8 grid gap-4 md:grid-cols-2 lg:grid-cols-4">{pillars.map(([title,desc])=><div key={title} className="card rounded-2xl p-5"><div className="grid h-10 w-10 place-items-center rounded-xl bg-blue-50 text-blue-700"><Sparkles size={19}/></div><h3 className="mt-4 font-bold text-slate-800">{title}</h3><p className="mt-2 text-sm leading-6 text-slate-500">{desc}</p></div>)}</div></div></section>

    <section className="mx-auto max-w-7xl px-5 py-16"><div className="max-w-2xl"><p className="text-sm font-bold uppercase tracking-wider text-blue-600">System architecture</p><h2 className="mt-2 text-3xl font-black text-[#0b1f3a]">From citizen voice to verified guidance.</h2></div><div className="mt-8 grid gap-3 sm:grid-cols-2 lg:grid-cols-5">{architecture.map(([name,Icon,desc],i)=><div key={String(name)} className="relative"><div className="card h-full rounded-2xl p-4"><div className="flex items-start justify-between"><div className="grid h-9 w-9 place-items-center rounded-lg bg-blue-50 text-blue-700"><Icon size={18}/></div><span className="text-xs font-bold text-slate-400">{String(i+1).padStart(2,'0')}</span></div><p className="mt-4 font-bold text-slate-800">{String(name)}</p><p className="mt-1 text-xs leading-5 text-slate-500">{String(desc)}</p></div>{i<architecture.length-1&&<div className="hidden lg:block absolute -right-3 top-12 z-10 text-slate-300">→</div>}</div>)}</div></section>

    <section className="border-y bg-slate-50"><div className="mx-auto max-w-7xl px-5 py-16"><div className="max-w-2xl"><p className="text-sm font-bold uppercase tracking-wider text-blue-600">Citizen journey</p><h2 className="mt-2 text-3xl font-black text-[#0b1f3a]">One continuous assistance flow.</h2></div><div className="mt-9 grid gap-4 md:grid-cols-5">{journey.map(([num,title,desc])=><div key={num} className="rounded-2xl border bg-white p-5"><span className="text-xs font-black text-blue-600">{num}</span><h3 className="mt-3 font-black text-[#0b1f3a]">{title}</h3><p className="mt-2 text-sm leading-6 text-slate-500">{desc}</p></div>)}</div></div></section>

    <section className="mx-auto max-w-7xl px-5 py-16"><div className="grid gap-5 lg:grid-cols-3"><div className="card rounded-2xl p-6 lg:col-span-2"><p className="text-sm font-bold uppercase tracking-wider text-green-700">Impact & scalability</p><h2 className="mt-2 text-3xl font-black text-[#0b1f3a]">A foundation that can grow beyond the demo.</h2><div className="mt-6 grid gap-4 sm:grid-cols-2">{['Add verified scheme sources and scheduled content updates.','Introduce stronger OCR and document validation integrations.','Connect authorized government/cooperative APIs where available.','Expand languages and regional service knowledge.'].map(x=><div key={x} className="flex gap-3 rounded-xl bg-slate-50 p-4 text-sm text-slate-600"><CheckCircle2 className="mt-0.5 shrink-0 text-green-600" size={18}/>{x}</div>)}</div></div><div className="rounded-2xl bg-gradient-to-br from-[#0b1f3a] to-[#155eef] p-6 text-white"><p className="font-bold">Demo boundary</p><p className="mt-4 text-sm leading-7 text-blue-100">OCR, application tracking and analytics are simulated where no live service is connected. The prototype never represents those simulated operations as an actual government submission.</p><p className="mt-5 rounded-xl bg-white/10 p-4 text-xs font-semibold leading-5">Verify current eligibility, documents and application rules on the relevant official government portal.</p></div></div></section>

    <section className="border-t bg-white"><div className="mx-auto max-w-7xl px-5 py-10"><div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between"><div><p className="font-bold text-[#0b1f3a]">Ready to demonstrate Sahakar Sahayak?</p><p className="text-sm text-slate-500">Start with the multilingual assistant or run the eligibility workflow.</p></div><div className="flex flex-wrap gap-3"><Link href="/assistant" className="rounded-xl bg-[#0b1f3a] px-4 py-3 text-sm font-semibold text-white">Open Assistant</Link><Link href="/eligibility" className="rounded-xl border px-4 py-3 text-sm font-semibold text-slate-800">Open Eligibility</Link></div></div></div></section>
  </div>
}
