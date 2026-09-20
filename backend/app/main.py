from pathlib import Path
import re
import os
from fastapi import FastAPI, Depends, HTTPException, Query, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import or_
from .database import Base, engine, get_db
from .models import Scheme, Conversation, Message, User, Profile, SavedScheme, EligibilitySession, EligibilityAnswer
from .schemas import ChatRequest, ChatResponse, SchemeOut, ProfileIn, EligibilityRequest, EligibilityResponse
from .engine import detect_language, detect_intent, extract_entities, match_schemes, make_response, merge_entities, conversation_context, missing_followup, followup_response
from .seed import seed
from .eligibility import evaluate_schemes
from .documents import ALLOWED_EXTENSIONS, ALLOWED_MIME, MAX_BYTES, classify_document, detect_text_language, extract_pdf_text, extract_image_text, demo_text

Base.metadata.create_all(bind=engine)
seed()
app = FastAPI(title="Sahakar Sahayak API", version="0.2.0", description="Local-first civic assistance prototype API")
_cors_origins = [x.strip() for x in os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",") if x.strip()]
app.add_middleware(CORSMiddleware, allow_origins=_cors_origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get("/api/health")
def health(): return {"status":"ok","mode":"DEMO / LOCAL","database":"SQLite"}

@app.get("/api/language")
def language(text: str = Query(min_length=1)): return {"language": detect_language(text)}
@app.get("/api/intent")
def intent(text: str = Query(min_length=1)): return {"intent": detect_intent(text), "entities": extract_entities(text)}

@app.get("/api/schemes", response_model=list[SchemeOut])
def schemes(db: Session=Depends(get_db), q: str|None=None, category: str|None=None, state: str|None=None):
    query=db.query(Scheme).filter(Scheme.active == True)
    if q:
        term=f"%{q}%"
        query=query.filter(or_(Scheme.name.ilike(term), Scheme.description.ilike(term), Scheme.category.ilike(term)))
    if category and category.lower()!="all": query=query.filter(Scheme.category.ilike(category))
    # State filtering is intentionally conservative because this seed contains national programmes.
    return query.order_by(Scheme.name).all()

@app.get("/api/schemes/{scheme_id}", response_model=SchemeOut)
def scheme_detail(scheme_id:int, db:Session=Depends(get_db)):
    item=db.get(Scheme, scheme_id)
    if not item: raise HTTPException(404,"Scheme not found")
    return item

@app.post("/api/chat", response_model=ChatResponse)
def chat(payload:ChatRequest, db:Session=Depends(get_db)):
    user=db.get(User,1)
    if not user:
        user=User(name="Demo Citizen"); db.add(user); db.flush()
    conversation=db.get(Conversation,payload.conversation_id) if payload.conversation_id else None
    if not conversation:
        conversation=Conversation(user_id=user.id,title=payload.message[:80]); db.add(conversation); db.flush()
    lang=detect_language(payload.message); intent=detect_intent(payload.message)
    prior=conversation_context(db, conversation.id)
    entities=merge_entities(prior, payload.profile, extract_entities(payload.message))
    missing=missing_followup(intent, entities)
    schemes=[] if missing else match_schemes(db,payload.message,payload.profile,entities)
    response=followup_response(lang, missing) if missing else make_response(lang,intent,entities,schemes)
    db.add(Message(conversation_id=conversation.id,role="user",text=payload.message,language=lang))
    db.add(Message(conversation_id=conversation.id,role="assistant",text=response,language=lang)); db.commit()
    return ChatResponse(conversation_id=conversation.id,language=lang,intent=intent,entities=entities,response=response,schemes=[{"id":s.id,"name":s.name,"category":s.category} for s in schemes])


@app.post("/api/eligibility", response_model=EligibilityResponse)
def eligibility(payload: EligibilityRequest, db: Session = Depends(get_db)):
    user=db.query(User).first() or User(name="Demo Citizen")
    if not user.id: db.add(user); db.flush()
    session=db.get(EligibilitySession, payload.session_id) if payload.session_id else None
    if not session:
        session=EligibilitySession(user_id=user.id, current_step=1, answers={})
        db.add(session); db.flush()
    answers=dict(session.answers or {})
    answers.update({k:v for k,v in payload.answers.items() if v not in (None, "")})
    session.answers=answers
    fields=["name","age","state","district","occupation","income_range","farmer_status","land_ownership","purpose"]
    required=["age","state","occupation","income_range","purpose"]
    missing=[f for f in required if not answers.get(f)]
    session.current_step=min(6, max(1, len([f for f in required if answers.get(f)])+1))
    if not missing: session.status="complete"
    for field,value in payload.answers.items():
        if value not in (None, ""):
            db.add(EligibilityAnswer(session_id=session.id, field=field, value=str(value)))
    results=evaluate_schemes(db.query(Scheme).filter(Scheme.active == True).all(), answers=answers)
    db.commit()
    return {"session_id":session.id,"current_step":session.current_step,"complete":not missing,"missing_fields":missing,"results":results,"disclaimer":"You may be eligible based on the information provided. Please verify current eligibility on the official government portal."}

@app.get("/api/eligibility/{session_id}", response_model=EligibilityResponse)
def eligibility_session(session_id:int, db:Session=Depends(get_db)):
    session=db.get(EligibilitySession,session_id)
    if not session: raise HTTPException(404,"Eligibility session not found")
    required=["age","state","occupation","income_range","purpose"]
    missing=[f for f in required if not (session.answers or {}).get(f)]
    results=evaluate_schemes(db.query(Scheme).filter(Scheme.active == True).all(), answers=session.answers or {})
    return {"session_id":session.id,"current_step":session.current_step,"complete":not missing,"missing_fields":missing,"results":results,"disclaimer":"You may be eligible based on the information provided. Please verify current eligibility on the official government portal."}

@app.post("/api/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    filename=file.filename or "document"
    ext=Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400,"Unsupported file type. Upload PDF, JPG, JPEG or PNG.")
    if file.content_type and file.content_type not in ALLOWED_MIME:
        raise HTTPException(400,"Unsupported MIME type.")
    data=await file.read(MAX_BYTES+1)
    if len(data)>MAX_BYTES:
        raise HTTPException(413,"File exceeds the 10 MB limit.")
    upload_dir=(Path("/tmp") / "sahakar-sahayak-uploads") if os.getenv("VERCEL") else (Path(__file__).resolve().parents[1]/"uploads")
    upload_dir.mkdir(exist_ok=True)
    safe=re.sub(r"[^A-Za-z0-9._-]","_",filename)
    target=upload_dir/safe
    target.write_bytes(data)
    text=extract_pdf_text(target) if ext=='.pdf' else extract_image_text(target)
    extracted=bool(text)
    if not text:
        # Local DEMO OCR fallback keeps the workflow runnable without external services.
        text=demo_text(filename, classify_document('', filename))
    kind=classify_document(text, filename)
    return {
        "id": safe, "filename": filename, "size_bytes": len(data),
        "status": "processed", "mode": "REAL LOCAL EXTRACTION" if extracted else "DEMO OCR",
        "document_type": kind, "language": detect_text_language(text),
        "extracted_text": text,
        "verification_note": "OCR output is assistive only. Verify the original document before using it for a government application."
    }

@app.get("/api/conversations")
def conversations(db:Session=Depends(get_db)):
    return [{"id":c.id,"title":c.title} for c in db.query(Conversation).order_by(Conversation.id.desc()).all()]

@app.get("/api/conversations/{conversation_id}")
def conversation_detail(conversation_id:int, db:Session=Depends(get_db)):
    c=db.get(Conversation,conversation_id)
    if not c: raise HTTPException(404,"Conversation not found")
    messages=db.query(Message).filter(Message.conversation_id==conversation_id).order_by(Message.id).all()
    return {"id":c.id,"title":c.title,"messages":[{"role":m.role,"text":m.text,"language":m.language} for m in messages]}

@app.get("/api/profile")
def get_profile(db:Session=Depends(get_db)):
    p=db.query(Profile).first(); u=db.query(User).first()
    return {"name":u.name if u else "Demo Citizen", **({k:getattr(p,k) for k in ["age","state","district","occupation","income_range","farmer_status","land_ownership","preferred_language"]} if p else {})}

@app.put("/api/profile")
def update_profile(payload:ProfileIn, db:Session=Depends(get_db)):
    u=db.query(User).first() or User(name="Demo Citizen")
    if not u.id: db.add(u); db.flush()
    if payload.name: u.name=payload.name
    p=db.query(Profile).filter(Profile.user_id==u.id).first()
    if not p: p=Profile(user_id=u.id); db.add(p)
    for field in ["age","state","district","occupation","income_range","farmer_status","land_ownership","preferred_language"]:
        setattr(p,field,getattr(payload,field))
    db.commit(); return {"ok":True,"profile":payload.model_dump()}

@app.post("/api/saved/{scheme_id}")
def save_scheme(scheme_id:int, db:Session=Depends(get_db)):
    if not db.get(Scheme,scheme_id): raise HTTPException(404,"Scheme not found")
    if not db.query(SavedScheme).filter_by(user_id=1,scheme_id=scheme_id).first(): db.add(SavedScheme(user_id=1,scheme_id=scheme_id)); db.commit()
    return {"saved":True}

@app.get("/api/saved")
def saved(db:Session=Depends(get_db)):
    rows=db.query(Scheme).join(SavedScheme,SavedScheme.scheme_id==Scheme.id).filter(SavedScheme.user_id==1).all(); return rows

# ---------- Stage 6: applications, grievances & cooperative services ----------
from .models import Application, Grievance, CooperativeService

APPLICATION_STATUSES = ["Not Started", "Preparing", "Submitted", "Under Verification", "Completed"]

@app.get("/api/applications")
def list_applications(db: Session = Depends(get_db)):
    rows = db.query(Application).filter(Application.user_id == 1).order_by(Application.id.desc()).all()
    if not rows:
        # Local demo data; explicitly marked as simulated rather than a government status.
        demo = Application(user_id=1, scheme_name="PM-KISAN", status="Preparing", current_step="Review beneficiary details", documents=["Bank account details", "Land record"], next_action="Verify the required information before applying", timeline=["Profile prepared", "Documents review", "Application guidance", "Official submission"])
        db.add(demo); db.commit(); rows=[demo]
    return [{"id":r.id,"scheme_name":r.scheme_name,"status":r.status,"current_step":r.current_step,"documents":r.documents,"next_action":r.next_action,"timeline":r.timeline,"mode":"DEMO APPLICATION TRACKING"} for r in rows]

@app.post("/api/applications")
def create_application(payload: dict, db: Session = Depends(get_db)):
    scheme_id = payload.get("scheme_id")
    scheme = db.get(Scheme, scheme_id) if scheme_id else None
    name = scheme.name if scheme else str(payload.get("scheme_name") or "Selected scheme")
    docs = scheme.documents if scheme else []
    row = Application(user_id=1, scheme_id=scheme.id if scheme else None, scheme_name=name, status="Not Started", current_step="Review scheme requirements", documents=docs, next_action="Review the required documents", timeline=["Not Started", "Preparing", "Submitted", "Under Verification", "Completed"])
    db.add(row); db.commit(); db.refresh(row)
    return {"id":row.id,"scheme_name":row.scheme_name,"status":row.status,"current_step":row.current_step,"documents":row.documents,"next_action":row.next_action,"timeline":row.timeline,"mode":"DEMO APPLICATION TRACKING"}

@app.patch("/api/applications/{application_id}")
def update_application(application_id: int, payload: dict, db: Session = Depends(get_db)):
    row = db.get(Application, application_id)
    if not row: raise HTTPException(404, "Application not found")
    status = payload.get("status")
    if status and status not in APPLICATION_STATUSES: raise HTTPException(400, "Invalid application status")
    if status: row.status = status
    if payload.get("next_action"): row.next_action = str(payload["next_action"])
    if status: row.current_step = {"Not Started":"Review scheme requirements","Preparing":"Prepare required documents","Submitted":"Awaiting official processing","Under Verification":"Awaiting verification","Completed":"Guidance workflow completed"}[status]
    db.commit(); return {"id":row.id,"scheme_name":row.scheme_name,"status":row.status,"current_step":row.current_step,"documents":row.documents,"next_action":row.next_action,"timeline":row.timeline,"mode":"DEMO APPLICATION TRACKING"}

@app.post("/api/grievances")
def create_grievance(payload: dict, db: Session = Depends(get_db)):
    complaint = str(payload.get("complaint") or "").strip()
    if len(complaint) < 5: raise HTTPException(400, "Please provide a little more detail about the complaint.")
    text = complaint.lower()
    rules = [
        (("payment","money","fund","paisa","पैसे","भुगतान"), "Payment issue", "Scheme / payment department", "Keep payment or transaction evidence and verify the official grievance channel."),
        (("reject","rejected","rejection","रद्द","अस्वीकार"), "Application rejection", "Relevant scheme department", "Review the rejection reason and collect the acknowledgement/rejection notice."),
        (("document","certificate","दस्तावेज","कागदपत्र"), "Document issue", "Document issuing authority", "Keep the document and any acknowledgement showing the issue."),
        (("delay","late","pending","wait","देरी","विलंब"), "Service delay", "Relevant service department", "Keep the application/reference number and latest status acknowledgement."),
        (("cooperative","society","सहकारी","संस्था"), "Cooperative issue", "Relevant cooperative authority", "Keep membership/transaction records and correspondence."),
        (("scheme","yojana","योजना"), "Scheme issue", "Relevant scheme department", "Keep scheme application/reference details and supporting documents."),
    ]
    category, dept, step = "Other", "Relevant government/service department", "Use the official grievance channel and keep acknowledgement/reference evidence."
    for keys, c, d, s in rules:
        if any(k in text for k in keys): category, dept, step = c, d, s; break
    evidence=["Application/reference number if available","Relevant supporting document","Date and details of the incident"]
    row=Grievance(user_id=1, complaint=complaint, department=payload.get("department"), location=payload.get("location"), reference_number=payload.get("reference_number"), category=category, summary=complaint[:500], suggested_department=dept, next_step=step, required_evidence=evidence)
    db.add(row); db.commit(); db.refresh(row)
    return {"id":row.id,"summary":row.summary,"category":row.category,"suggested_department":row.suggested_department,"next_step":row.next_step,"required_evidence":row.required_evidence,"mode":"DEMO / GUIDANCE ONLY","submission_note":"This prototype does not submit the grievance to a government system."}

@app.get("/api/grievances")
def list_grievances(db: Session = Depends(get_db)):
    rows=db.query(Grievance).filter(Grievance.user_id==1).order_by(Grievance.id.desc()).all()
    return [{"id":r.id,"summary":r.summary,"category":r.category,"suggested_department":r.suggested_department,"next_step":r.next_step} for r in rows]

COOP_SERVICES = [
    ("Registration guidance","Registration","Guidance on preparing a cooperative registration workflow.",["Confirm the cooperative type and applicable authority","Prepare the required formation documents","Submit through the relevant official channel"],["Formation documents","Member details","Address/registration evidence"]),
    ("Membership guidance","Membership","Understand common membership documentation and record-keeping steps.",["Check membership eligibility and bylaws","Prepare identity/address evidence","Contact the cooperative office for current procedure"],["Identity document","Address evidence","Membership/application form"]),
    ("Documentation checklist","Documentation","Organize documents commonly used for cooperative services.",["Identify the service needed","Match the document checklist","Verify current requirements with the authority"],["Service-specific application","Identity/address evidence","Supporting records"]),
    ("Finance and loan guidance","Finance","General guidance for understanding cooperative finance and loan documentation.",["Clarify loan purpose","Review repayment and documentation requirements","Verify terms with the cooperative"],["Identity document","Income/business records","Relevant cooperative records"]),
    ("Complaint guidance","Complaints","Structure a cooperative-related complaint and identify evidence to retain.",["Write the issue clearly","Collect acknowledgement/transaction evidence","Use the official cooperative grievance route"],["Complaint details","Reference number","Supporting evidence"]),
    ("Cooperative scheme guidance","Cooperative schemes","Find general guidance about schemes and services relevant to cooperative members.",["Describe the assistance need","Check the relevant scheme information","Verify current eligibility and application channel"],["Scheme-specific documents","Member records","Identity/address evidence"]),
]

@app.get("/api/cooperatives")
def cooperative_services(q: str|None=None, category: str|None=None, db: Session = Depends(get_db)):
    if db.query(CooperativeService).count()==0:
        for title,cat,desc,steps,docs in COOP_SERVICES: db.add(CooperativeService(title=title,category=cat,description=desc,steps=steps,documents=docs))
        db.commit()
    query=db.query(CooperativeService)
    if q: query=query.filter(or_(CooperativeService.title.ilike(f"%{q}%"), CooperativeService.description.ilike(f"%{q}%"), CooperativeService.category.ilike(f"%{q}%")))
    if category and category.lower()!="all": query=query.filter(CooperativeService.category.ilike(category))
    rows=query.order_by(CooperativeService.title).all()
    return [{"id":r.id,"title":r.title,"category":r.category,"description":r.description,"steps":r.steps,"documents":r.documents,"notes":r.notes} for r in rows]

# ---------- Stage 7: citizen dashboard persistence ----------
@app.delete("/api/conversations/{conversation_id}")
def delete_conversation(conversation_id:int, db:Session=Depends(get_db)):
    c=db.get(Conversation, conversation_id)
    if not c: raise HTTPException(404, "Conversation not found")
    db.query(Message).filter(Message.conversation_id==conversation_id).delete(synchronize_session=False)
    db.delete(c); db.commit()
    return {"deleted":True,"id":conversation_id}

@app.delete("/api/saved/{scheme_id}")
def unsave_scheme(scheme_id:int, db:Session=Depends(get_db)):
    row=db.query(SavedScheme).filter_by(user_id=1, scheme_id=scheme_id).first()
    if row:
        db.delete(row); db.commit()
    return {"saved":False,"scheme_id":scheme_id}

@app.get("/api/dashboard")
def dashboard(db:Session=Depends(get_db)):
    user=db.query(User).first()
    profile=db.query(Profile).filter(Profile.user_id==1).first()
    conversations=db.query(Conversation).filter(Conversation.user_id==1).order_by(Conversation.id.desc()).all()
    saved_rows=db.query(SavedScheme).filter(SavedScheme.user_id==1).all()
    applications=db.query(Application).filter(Application.user_id==1).all()
    documents_dir=Path(__file__).resolve().parents[1]/"uploads"
    document_count=len([p for p in documents_dir.iterdir() if p.is_file()]) if documents_dir.exists() else 0
    profile_fields=["age","state","district","occupation","income_range","farmer_status","land_ownership","preferred_language"]
    completed=sum(1 for f in profile_fields if getattr(profile,f,None) not in (None,"")) if profile else 0
    return {
        "profile_completion": round(completed/len(profile_fields)*100),
        "recent_conversations":[{"id":c.id,"title":c.title} for c in conversations[:5]],
        "saved_schemes_count":len(saved_rows),
        "applications_count":len(applications),
        "documents_count":document_count,
        "potential_matches":[],
        "recent_activity":[
            *[{"type":"conversation","label":c.title,"id":c.id} for c in conversations[:3]],
            *[{"type":"saved","label":f"Saved scheme #{r.scheme_id}","id":r.scheme_id} for r in saved_rows[:3]],
        ],
        "citizen_name": user.name if user else "Demo Citizen"
    }
