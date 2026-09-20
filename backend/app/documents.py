from pathlib import Path
import re
from typing import Optional

ALLOWED_EXTENSIONS={'.pdf','.jpg','.jpeg','.png'}
ALLOWED_MIME={'application/pdf','image/jpeg','image/png'}
MAX_BYTES=10*1024*1024

DOC_RULES={
    'Aadhaar': ['aadhaar','uidai','unique identification'],
    'Income Certificate': ['income certificate','annual income','income certificate'],
    'Land Record': ['7/12','7 12','land record','survey number','ferfar','property record'],
    'Bank Document': ['bank account','ifsc','account number','passbook','bank statement'],
    'Caste Certificate': ['caste certificate','scheduled caste','scheduled tribe','other backward'],
    'Residence Certificate': ['residence certificate','domicile','residential address'],
    'Government Letter': ['government of india','government letter','department','notice'],
    'Application Receipt': ['application receipt','acknowledgement','acknowledgment','application number'],
}

def classify_document(text:str, filename:str)->str:
    hay=(text+' '+filename).lower()
    scores={k:sum(1 for p in pats if p in hay) for k,pats in DOC_RULES.items()}
    best=max(scores,key=scores.get)
    return best if scores[best] else 'Unknown / Needs Review'

def detect_text_language(text:str)->str:
    if not text.strip(): return 'Unknown'
    dev=re.findall(r'[\u0900-\u097F]',text)
    if not dev:
        lower=text.lower()
        marathi=['mala','aahe','havi','shetkari','shetkaryansathi','maharashtra']
        hindi=['mujhe','hai','chahiye','kisan','yojana','sarkari']
        ms=sum(w in lower.split() for w in marathi); hi=sum(w in lower.split() for w in hindi)
        if ms>hi and ms: return 'Marathi (Roman)'
        if hi: return 'Hindi (Roman)'
        return 'English'
    marathi_chars='ळऱऍऑऒआइईउऊएऐओऔ'
    if any(c in text for c in marathi_chars): return 'Marathi'
    return 'Hindi'

def extract_pdf_text(path:Path)->Optional[str]:
    try:
        from pypdf import PdfReader
        reader=PdfReader(str(path))
        return '\n'.join((page.extract_text() or '') for page in reader.pages).strip()[:12000]
    except Exception:
        return None

def extract_image_text(path:Path)->Optional[str]:
    try:
        import pytesseract
        from PIL import Image
        return pytesseract.image_to_string(Image.open(path)).strip()[:12000]
    except Exception:
        return None

def demo_text(filename:str, kind:str)->str:
    return (
        f'DEMO OCR\nDocument filename: {filename}\nDetected document type: {kind}\n'
        'No reliable text extraction engine was available for this file in the local environment. '
        'Review the uploaded document manually before using this information for any application.'
    )
