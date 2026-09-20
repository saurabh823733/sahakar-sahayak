const API_BASE = process.env.NEXT_PUBLIC_API_URL || '/api';

export type Scheme = {
  id:number; name:string; category:string; description:string; benefits:string[]; eligibility:string[];
  documents:string[]; application_procedure:string[]; state_scope:string; official_url:string; verification_notes:string;
};

async function request<T>(path:string, init?:RequestInit):Promise<T>{
  const res=await fetch(`${API_BASE}${path}`,{...init,headers:{'Content-Type':'application/json',...(init?.headers||{})},cache:'no-store'});
  if(!res.ok){const msg=await res.text(); throw new Error(msg || `API error ${res.status}`)}
  return res.json();
}
export const api={
  health:()=>request<{status:string;mode:string;database:string}>('/health'),
  schemes:(params='')=>request<Scheme[]>(`/schemes${params}`),
  scheme:(id:number)=>request<Scheme>(`/schemes/${id}`),
  chat:(body:{message:string;conversation_id?:number;profile?:Record<string,unknown>})=>request<any>('/chat',{method:'POST',body:JSON.stringify(body)}),
  language:(text:string)=>request<any>(`/language?text=${encodeURIComponent(text)}`),
  intent:(text:string)=>request<any>(`/intent?text=${encodeURIComponent(text)}`),
  profile:()=>request<any>('/profile'),
  updateProfile:(body:any)=>request<any>('/profile',{method:'PUT',body:JSON.stringify(body)}),
  save:(id:number)=>request<any>(`/saved/${id}`,{method:'POST'}),
  unsave:(id:number)=>request<any>(`/saved/${id}`,{method:'DELETE'}),
  saved:()=>request<any[]>('/saved'),
  conversations:()=>request<any[]>('/conversations'),
  conversation:(id:number)=>request<any>(`/conversations/${id}`),
  deleteConversation:(id:number)=>request<any>(`/conversations/${id}`,{method:'DELETE'}),
  dashboard:()=>request<any>('/dashboard'),
  eligibility:(body:{session_id?:number;answers:Record<string,unknown>})=>request<any>('/eligibility',{method:'POST',body:JSON.stringify(body)}),
  eligibilitySession:(id:number)=>request<any>(`/eligibility/${id}`),
  uploadDocument: async (file:File)=>{ const form=new FormData(); form.append('file',file); const res=await fetch(`${API_BASE}/documents/upload`,{method:'POST',body:form}); if(!res.ok){const msg=await res.text(); throw new Error(msg||`Upload failed (${res.status})`)} return res.json(); },

};

// Stage 7 citizen state APIs
