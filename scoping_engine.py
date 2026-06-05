import json
import requests
import re
from controls_data import USE_CASES

# Expected Scope Mapping (Rule 4)
DOC_TYPE_MAPPINGS = {
    "Access Control Policy": [
        "ISO-1215 Access Control",
        "ISO-1216 Identity Management",
        "ISO-1217 Authentication Information",
        "ISO-1261 Privileged Access Rights",
        "ISO-1218 Access Rights",
        "ISO-1262 Information Access Restriction",
        "ISO-1264 Secure Authentication"
    ],
    "Asset Management Policy": [
        "ISO-1209 Inventory of Information and Other Associated Assets",
        "ISO-1210 Acceptable Use of Information and Other Associated Assets",
        "ISO-1211 Return of Assets",
        "ISO-1212 Classification of Information",
        "ISO-1213 Labelling of Information",
        "ISO-1254 Security of Assets Off-premises",
        "ISO-1259 Secure Disposal or Re-use of Equipment"
    ],
    "Risk Assessment": [
        "ISO-1201 Policies for Information Security", # Broad policy
        "ISO-1231 Legal, Statutory, Regulatory and Contractual Requirements",
        "ISO-1207 Threat Intelligence",
        "ISO-1202 Information Security Roles and Responsibilities",
        "ISO-1235 Independent Review of Information Security",
        "ISO-1236 Compliance with Policies and Standards for Information Security"
    ],
    "Incident Management Policy": [
        "ISO-1224 Information Security Incident Management Planning and Preparation",
        "ISO-1225 Assessment and Decision on Information Security Events",
        "ISO-1226 Response to Information Security Incidents",
        "ISO-1227 Learning from Information Security Incidents",
        "ISO-1228 Collection of Evidence",
        "ISO-1245 Information Security Event Reporting"
    ],
    "Business Continuity Plan": [
        "ISO-1229 Information Security During Disruption",
        "ISO-1230 Ict Readiness for Business Continuity"
    ]
}

def _get_candidate_controls(doc_types):
    """Retrieve candidate control names based on identified document types."""
    candidates = set()
    for dt in doc_types:
        for c in DOC_TYPE_MAPPINGS.get(dt, []):
            candidates.add(c)
    
    # Also add a few general ones to be safe, but restrict the total list
    if not candidates:
        # Fallback to a broader set if doc type is unknown
        for dt, controls in DOC_TYPE_MAPPINGS.items():
            for c in controls:
                candidates.add(c)
                
    return list(candidates)

def detect_scope_and_controls(context, ollama_model="qwen2.5:3b"):
    """
    Intelligent LLM-driven scope detection.
    Returns:
       selected_controls (list of use_case strings): The controls that passed the rules.
       warning (str): A warning message if the scope is too large, or None.
       doc_types (list of strings): The identified document types.
    """
    context_chunk = context[:6000]
    
    all_possible_controls = []
    for dt, controls in DOC_TYPE_MAPPINGS.items():
        all_possible_controls.extend(controls)
        
    candidate_metadata = []
    for cname in set(all_possible_controls):
        for uc in USE_CASES:
            if uc["use_case"] == cname:
                candidate_metadata.append({
                    "control": uc["use_case"],
                    "description": uc["label"]
                })
                break
                
    candidates_text = json.dumps(candidate_metadata, indent=2)

    unified_prompt = f"""You are a strict Cybersecurity Auditor. Analyze the EVIDENCE TEXT.
1. Identify the Document Types it belongs to (can be multiple):
- Access Control Policy
- Asset Management Policy
- Risk Assessment
- Incident Management Policy
- Business Continuity Plan

2. Evaluate the EVIDENCE TEXT against the CANDIDATE CONTROLS.
Assign a "relevance_score" (0 to 100). Set "evidence_exists" to true if supporting evidence is found.

EVIDENCE TEXT:
\"\"\"
{context_chunk}
\"\"\"

CANDIDATE CONTROLS:
{candidates_text}

Return ONLY valid JSON in this exact format:
{{
  "doc_types": ["..."],
  "scores": [
    {{"control": "...", "relevance_score": 85, "evidence_exists": true}}
  ]
}}
"""
    
    doc_types = []
    scored_controls = []
    
    import time
    start_time = time.time()
    print(f"\n[{time.strftime('%H:%M:%S')}] [INFO] Starting Automatic LLM Scope Detection...")
    
    try:
        r = requests.post("http://127.0.0.1:11434/api/generate",
                           json={"model": ollama_model, "prompt": unified_prompt, "stream": False, "format": "json"}, timeout=120)
        if r.status_code == 200:
            res = r.json().get("response", "{}")
            try:
                data = json.loads(res)
                dt_list = data.get("doc_types", [])
                doc_types = [dt for dt in dt_list if dt in DOC_TYPE_MAPPINGS]
                
                # Only keep scores for controls that match the identified doc types
                valid_candidates = _get_candidate_controls(doc_types)
                all_scores = data.get("scores", [])
                scored_controls = [sc for sc in all_scores if sc.get("control") in valid_candidates]
            except Exception:
                pass
    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] [ERROR] LLM Scope Detection failed: {e}")
        
    elapsed = time.time() - start_time
    print(f"[{time.strftime('%H:%M:%S')}] [SUCCESS] Scope Detection completed in {elapsed:.2f} seconds.")
    print(f"   - Identified Doc Types: {doc_types}")

    # 3. Apply Rules
    selected_controls = []
    for sc in scored_controls:
        c_name = sc.get("control")
        score = sc.get("relevance_score", 0)
        has_ev = sc.get("evidence_exists", False)
        
        # Relevance Score >= 80 -> Include Control
        if score >= 80:
            selected_controls.append(c_name)
        # Relevance Score 60-79 -> Include only if supporting evidence exists
        elif 60 <= score < 80 and has_ev:
            selected_controls.append(c_name)
        # Relevance Score < 60 -> Mark Out Of Scope (do nothing)
        
    # Remove duplicates
    selected_controls = list(set(selected_controls))
    
    # 4. Enforce Target Scope Size
    # Target Scope Size:
    # Single document type: 5-15 controls
    # Two document types: 10-25 controls
    # Three or more: max 30 controls
    
    num_dt = len(doc_types)
    max_controls = 15
    if num_dt == 2:
        max_controls = 25
    elif num_dt >= 3:
        max_controls = 30
        
    warning_msg = None
    if len(selected_controls) > max_controls:
        warning_msg = f"Scope detection may be over-selecting controls ({len(selected_controls)} found). Review relevance thresholds."
        # Cap the selection
        # To cap it smartly, we would sort by score. 
        # But we don't have the scores for all selected if they were merged, though here we do.
        # Let's sort the scored_controls and pick top max_controls
        sc_dict = {sc.get("control"): sc.get("relevance_score", 0) for sc in scored_controls}
        selected_controls = sorted(selected_controls, key=lambda c: sc_dict.get(c, 0), reverse=True)[:max_controls]
        
    return selected_controls, warning_msg, doc_types
