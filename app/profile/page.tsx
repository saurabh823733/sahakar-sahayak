'use client';
import {useEffect,useState} from 'react';
import {Save, UserRound} from 'lucide-react';
import {api} from '@/lib/api';

const fields=[
 ['name','Name','text'],['age','Age','number'],['state','State','text'],['district','District','text'],
 ['occupation','Occupation','text'],['income_range','Income range','text'],['farmer_status','Farmer status','text'],
 ['land_ownership','Land ownership','text']
];
export default function Page(){
 const [form,setForm]=useState<any>({preferred_language:'auto'}); const [saving,setSaving]=useState(false); const [msg,setMsg]=useState('');
 useEffect(()=>{api.profile().then(setForm).catch(()=>setMsg('Could not load profile. Start the backend and retry.'))},[]);
 const update=(k:string,v:string)=>setForm((x:any)=>({...x,[k]:k==='age'?(v?Number(v):null):v}));
 const save=async()=>{setSaving(true);setMsg('');try{await api.updateProfile(form);setMsg('Profile saved. Scheme matching can now use these details.')}catch(e:any){setMsg(e.message||'Save failed.')}finally{setSaving(false)}};
 return <div className="min-h-[calc(100vh-4rem)] bg-slate-50"><div className="mx-auto max-w-5xl px-5 py-8"><div className="rounded-3xl bg-gradient-to-br from-[#0b1f3a] to-[#155eef] p-7 text-white sm:p-10"><div className="flex items-center gap-4"><div className="grid h-12 w-12 place-items-center rounded-2xl bg-white/15"><UserRound/></div><div><p className="text-xs font-bold uppercase tracking-wider text-blue-200">CITIZEN PROFILE</p><h1 className="text-3xl font-black">Your assistance profile</h1><p className="mt-2 text-sm text-blue-100">These details improve local scheme matching and conversational follow-ups.</p></div></div></div>
 <section className="card mt-6 rounded-2xl p-6"><div className="grid gap-5 sm:grid-cols-2">{fields.map(([key,label,type])=><label key={key} className="text-sm font-semibold text-slate-700">{label}<input type={type} value={form[key]??''} onChange={e=>update(key,e.target.value)} className="mt-2 w-full rounded-xl border border-slate-200 bg-white px-4 py-3 font-normal outline-none focus:border-blue-500" /></label>)}<label className="text-sm font-semibold text-slate-700">Preferred language<select value={form.preferred_language||'auto'} onChange={e=>update('preferred_language',e.target.value)} className="mt-2 w-full rounded-xl border border-slate-200 bg-white px-4 py-3 font-normal"><option value="auto">Auto detect</option><option value="English">English</option><option value="Hindi">Hindi</option><option value="Marathi">Marathi</option></select></label></div><div className="mt-6 flex items-center gap-4"><button onClick={save} disabled={saving} className="flex items-center gap-2 rounded-xl bg-[#0b1f3a] px-5 py-3 text-sm font-bold text-white disabled:opacity-60"><Save size={17}/>{saving?'Saving…':'Save profile'}</button>{msg&&<p className="text-sm text-slate-600">{msg}</p>}</div></section></div></div>
}
