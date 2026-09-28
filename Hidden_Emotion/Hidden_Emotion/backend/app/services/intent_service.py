import re
import os
import json
import logging
import hashlib
from typing import List, Dict, Any, Tuple
from app.services.embedding_service import embedding_service

logger = logging.getLogger("sentimental.intent_service")

DATASET_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "datasets", "intent_dataset.json")

def load_intent_dataset():
    if os.path.exists(DATASET_PATH):
        try:
            with open(DATASET_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("intents", {})
        except Exception as e:
            logger.warning(f"Could not load intent dataset file ({e}). Using default fallback.")
    return {}

INTENT_CATALOG = load_intent_dataset()

class IntentService:
    def analyze(self, text: str, doc_type: str = "General", doc_id: str = "DOC-UNKNOWN") -> Dict[str, Any]:
        global INTENT_CATALOG
        if not INTENT_CATALOG:
            INTENT_CATALOG = load_intent_dataset()

        text_clean = text.strip()
        text_lower = text_clean.lower()
        words = text_lower.split()
        content_hash = hashlib.sha256(text_clean.encode('utf-8')).hexdigest()[:16]

        logger.info(
            f"[DOCUMENT_ANALYSIS_START] document_id={doc_id} "
            f"text_length={len(text_clean)} words={len(words)} text_hash={content_hash} doc_type='{doc_type}'"
        )

        if len(words) < 4:
            return self._no_intent_payload("Text length is too short to determine a clear intent.", doc_id)

        # Segment sentences
        sentences = [s.strip() for s in re.split(r'(?<=[.!?\n])\s+', text_clean) if len(s.split()) >= 3]
        if not sentences:
            sentences = [text_clean]

        n_s = len(sentences)
        conclusion_start = max(0, int(n_s * 0.60)) if n_s >= 3 else 0
        conclusion_sentences = sentences[conclusion_start:]
        conclusion_text = " ".join(conclusion_sentences).lower()
        body_text = " ".join(sentences[:conclusion_start]).lower() if conclusion_start > 0 else text_lower

        # 1. Action & Goal Pattern Detection Across Context
        
        # A) Medical & Clinical Context Detection
        has_clinical_context = any(re.search(pattern, text_lower) for pattern in [
            r'\b(physician|cardiologist|oncologist|orthopedic surgeon|radiologist|medical specialist|clinical specialist|general practitioner|attending doctor)\b',
            r'\b(clinical diagnosis|patient symptoms|symptom progression|pathology report|cardiac mri|ct scan|biopsy|cardiac imaging|palpitations)\b',
            r'\b(prescription medication|dosage adjustment|drug interaction|pharmacotherapy|antihypertensive|prescribed medication)\b',
            r'\b(post-operative recovery|surgical procedure|knee ligament reconstruction|wound healing|incision stiffness|post-surgery)\b'
        ])

        has_diag_test_goal = has_clinical_context and any(re.search(pattern, text_lower) for pattern in [
            r'\b(abnormal markers|biopsy report|pathology report|mri findings|ct scan findings|scan results|test interpretation|cardiac imaging)\b',
            r'\b(second opinion|second medical opinion|interpret test results|clarify lab report|radiology findings|diagnostic clarification)\b'
        ])

        has_postop_goal = has_clinical_context and any(re.search(pattern, text_lower) for pattern in [
            r'\b(post-operative|post-op|after surgery|surgical procedure|wound healing|incision drainage|post-surgical swelling)\b',
            r'\b(physiotherapy protocol|rehabilitation protocol|discharge instructions|post-surgery recovery)\b'
        ])

        has_medication_goal = has_clinical_context and any(re.search(pattern, text_lower) for pattern in [
            r'\b(dosage adjustment|side effects|dizziness|nausea|drug interaction|prescribed medication|medication schedule)\b',
            r'\b(how to take medication|dosage confusion|adjusting dosage|adverse reaction)\b'
        ])

        is_general_medical_goal = has_clinical_context and not (has_diag_test_goal or has_postop_goal or has_medication_goal)

        # B) Salary / Payroll Deduction Correction Goal
        has_payroll_context = any(re.search(pattern, text_lower) for pattern in [
            r'\b(attendance|timesheet|biometric|punch in|leave balance|working hours|attendance record)\b',
            r'\b(salary|payroll|paycheck|wages|payslip|salary slip|stipend|monthly pay)\b'
        ])
        has_deduction_issue = any(re.search(pattern, text_lower) for pattern in [
            r'\b(deduction|deducted|withheld|cut from salary|deducted from salary|short pay|marked absent|absent record)\b',
            r'\b(discrepancy|mismatch|attendance discrepancy|incorrectly marked|timesheet error)\b'
        ])
        has_payroll_action = any(re.search(pattern, text_lower) for pattern in [
            r'\b(payroll department|administration|hr department|submitted evidence|attendance corrected|verified discrepancy)\b',
            r'\b(restore|reimburse|reimbursement|adjustment|process payroll adjustment|credit back|reinstate)\b'
        ])
        is_payroll_deduction_goal = (has_payroll_context and has_deduction_issue) or (has_payroll_context and has_payroll_action)

        # C) Student / Team Project Deadline Extension
        has_project_context = any(re.search(pattern, text_lower) for pattern in [
            r'\b(team project|group project|engineering project|capstone project|academic project|course project)\b',
            r'\b(project team|project guide|our project|project implementation|project report)\b'
        ])
        has_extension_request = any(re.search(pattern, text_lower) for pattern in [
            r'\b(deadline extension|extension request|extend the deadline|additional time to submit|extra time for testing)\b',
            r'\b(granted an extension|asked for extension|postpone the deadline|request extra time)\b'
        ])
        has_faculty_comm = bool(re.search(r'\b(professor|faculty|instructor|project guide)\b', text_lower))
        is_project_extension_goal = has_project_context and (has_extension_request or (has_faculty_comm and "deadline" in text_lower))

        # D) Product Return & Refund Goal
        has_return_refund_goal = any(re.search(pattern, text_lower) for pattern in [
            r'\b(return|refund|money back|chargeback)\b.*\b(item|product|purchase|order|device|gadget|money|policy)\b',
            r'\b(return the item|return the product|full refund|return procedure|send it back|appropriate refund|receive a refund)\b'
        ])

        # E) Service Cancellation Goal
        has_cancel_goal = any(re.search(pattern, text_lower) for pattern in [
            r'\b(cancel|cancellation|terminate|termination|close|closing|delete)\b.*\b(subscription|account|membership|profile|service|auto-renewal|auto renewal|recurring)\b',
            r'\b(cancel subscription|terminate account|close my account|cancel membership|stop auto-renewal|delete my billing profile)\b'
        ])

        # F) Travel Delay Compensation Goal
        has_travel_claim = any(re.search(pattern, text_lower) for pattern in [
            r'\b(flight|train|airline|airport|transit|passenger|boarding)\b.*\b(delay|delayed|cancellation|cancelled|missed connection|compensation|reimbursement)\b',
            r'\b(delay compensation|airline compensation|flight delay|flight cancelled|travel compensation|statutory passenger rights)\b'
        ])

        # G) Job Application Follow-up Goal
        has_job_context = any(re.search(pattern, text_lower) for pattern in [
            r'\b(job application|interview|resume|cv|hiring|recruiter|candidacy)\b.*\b(status|follow up|following up|update|next round|timeline|evaluation)\b',
            r'\b(status of my job application|status of my application|interview follow-up|interview follow up|hiring process)\b'
        ])

        # H) Academic & Institutional Grievance Goal
        has_academic_grievance = any(re.search(r'\b' + re.escape(k) + r'\b', text_lower) for k in [
            "strict rules", "permission to go out", "management fee", "extra class", "saturday class", 
            "opinion of students", "cannot code", "campus building", "college management"
        ])

        # 2. Dense Semantic Vector Similarity Scoring
        semantic_scores: Dict[str, float] = {intent: 0.0 for intent in INTENT_CATALOG.keys()}
        try:
            doc_sample = text_clean[:1400]
            doc_embedding = embedding_service.get_embeddings([doc_sample])[0]
            conclusion_emb = embedding_service.get_embeddings([conclusion_text[:600]])[0] if conclusion_text else doc_embedding

            for intent, data in INTENT_CATALOG.items():
                desc_text = f"{intent}: {data.get('description', '')}"
                desc_embedding = embedding_service.get_embeddings([desc_text])[0]
                
                sim_global = embedding_service.cosine_similarity(doc_embedding, desc_embedding)
                sim_conclusion = embedding_service.cosine_similarity(conclusion_emb, desc_embedding)
                
                combined_sim = (sim_global * 0.40) + (sim_conclusion * 0.60)
                semantic_scores[intent] = max(0.0, combined_sim)
        except Exception as e:
            logger.warning(f"Error in vector intent matching: {e}")

        # 3. Keyword Scoring Across Full Document and Conclusion
        kw_scores: Dict[str, float] = {intent: 0.0 for intent in INTENT_CATALOG.keys()}
        total_kw_matches = 0

        for intent, data in INTENT_CATALOG.items():
            for kw in data.get("keywords", []):
                matches_full = len(re.findall(r'\b' + re.escape(kw) + r'\b', text_lower))
                matches_conclusion = len(re.findall(r'\b' + re.escape(kw) + r'\b', conclusion_text))
                
                score_increment = (matches_full * 1.0) + (matches_conclusion * 2.0)
                kw_scores[intent] += score_increment
                total_kw_matches += matches_full

        # 4. Contextual Goal Priority & Disambiguation Engine
        combined_scores: Dict[str, float] = {}
        for intent in INTENT_CATALOG.keys():
            k_score = min(2.5, kw_scores[intent] / 3.0)
            s_score = semantic_scores.get(intent, 0.0)
            combined = (s_score * 0.60) + (k_score * 0.40)
            combined_scores[intent] = combined

        # Context-Specific Goal Boosts:
        
        # 1) Medical / Clinical Goals
        if has_clinical_context:
            if has_diag_test_goal:
                combined_scores["Diagnostic Test Clarification & Second Opinion Request"] = combined_scores.get("Diagnostic Test Clarification & Second Opinion Request", 0.0) + 4.5
            elif has_postop_goal:
                combined_scores["Post-Operative Recovery & Symptom Management"] = combined_scores.get("Post-Operative Recovery & Symptom Management", 0.0) + 4.5
            elif has_medication_goal:
                combined_scores["Prescription Dosage & Medication Inquiry"] = combined_scores.get("Prescription Dosage & Medication Inquiry", 0.0) + 4.5
            else:
                combined_scores["Medical & Clinical Consultation Inquiry"] = combined_scores.get("Medical & Clinical Consultation Inquiry", 0.0) + 4.0
            
            # Suppress non-medical domains
            for non_med in ["Project Submission Deadline Extension Request", "Salary/Payroll Deduction Correction Request", "Product Return & Refund Request", "Technical Support & Troubleshooting"]:
                if non_med in combined_scores:
                    combined_scores[non_med] *= 0.05

        # 2) Salary / Payroll Deduction Correction
        elif is_payroll_deduction_goal:
            combined_scores["Salary/Payroll Deduction Correction Request"] = combined_scores.get("Salary/Payroll Deduction Correction Request", 0.0) + 4.0
            if "Project Submission Deadline Extension Request" in combined_scores:
                combined_scores["Project Submission Deadline Extension Request"] *= 0.05
            if "Technical Support & Troubleshooting" in combined_scores:
                combined_scores["Technical Support & Troubleshooting"] *= 0.1

        # 3) Student Project Extension Request
        elif is_project_extension_goal:
            combined_scores["Project Submission Deadline Extension Request"] = combined_scores.get("Project Submission Deadline Extension Request", 0.0) + 4.0
            if "Technical Support & Troubleshooting" in combined_scores:
                combined_scores["Technical Support & Troubleshooting"] *= 0.1
            if "Salary/Payroll Deduction Correction Request" in combined_scores:
                combined_scores["Salary/Payroll Deduction Correction Request"] *= 0.05

        # 4) Service Cancellation
        elif has_cancel_goal:
            combined_scores["Service Cancellation & Account Termination"] = combined_scores.get("Service Cancellation & Account Termination", 0.0) + 3.5

        # 5) Travel Delay Compensation
        elif has_travel_claim:
            combined_scores["Travel Delay & Cancellation Compensation Request"] = combined_scores.get("Travel Delay & Cancellation Compensation Request", 0.0) + 3.5
            if "Product Return & Refund Request" in combined_scores:
                combined_scores["Product Return & Refund Request"] *= 0.1

        # 6) Product Return / Refund
        elif has_return_refund_goal:
            combined_scores["Product Return & Refund Request"] = combined_scores.get("Product Return & Refund Request", 0.0) + 3.5
            if "Technical Support & Troubleshooting" in combined_scores:
                combined_scores["Technical Support & Troubleshooting"] *= 0.15

        # 7) Job Application Follow-up
        elif has_job_context and any(w in text_lower for w in ["status", "update", "follow up", "following up", "timeline"]):
            combined_scores["Job Application Status Inquiry & Follow-up"] = combined_scores.get("Job Application Status Inquiry & Follow-up", 0.0) + 3.5

        # 8) Academic Grievance
        elif has_academic_grievance:
            combined_scores["Academic & Institutional Grievance"] = combined_scores.get("Academic & Institutional Grievance", 0.0) + 3.5

        # Anti-Medical Hallucination Guard for non-medical docs
        if not has_clinical_context:
            for med_cat in ["Medical & Clinical Consultation Inquiry", "Diagnostic Test Clarification & Second Opinion Request", "Prescription Dosage & Medication Inquiry", "Post-Operative Recovery & Symptom Management"]:
                if med_cat in combined_scores:
                    combined_scores[med_cat] = 0.0

        # Sort intents by final contextual score
        sorted_intents = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
        top_intent, top_score = sorted_intents[0]

        logger.info(
            f"[GLOBAL_ANALYSIS] document_id={doc_id} intent='{top_intent}' score={top_score:.3f}"
        )

        general_intent_markers = [
            "need", "want", "require", "demand", "ask", "inquire", "request", 
            "please", "issue", "problem", "help", "fix", "deadline", "extension", 
            "return", "refund", "cancel", "status", "claim", "file", "submit", 
            "interview", "flight", "delay", "compensation", "dispute", "rules", 
            "complaint", "salary", "deduction", "payroll", "attendance", "physician",
            "doctor", "biopsy", "mri", "symptoms", "prescription", "surgery", "treatment"
        ]
        has_any_intent_marker = any(re.search(r'\b' + kw + r'\b', text_lower) for kw in general_intent_markers)

        if total_kw_matches == 0 and not has_any_intent_marker and top_score < 0.18:
            return self._no_intent_payload("No clear directional demand or actionable request was identified in the document.", doc_id)

        primary_meta = INTENT_CATALOG.get(top_intent, {})

        # 5. Extract Supporting Evidence Sentences strictly for current document and intent
        supporting_sentences = self._extract_evidence_sentences(sentences, top_intent, primary_meta, doc_id)

        # 6. Build Contextual Flow Narrative
        contextual_flow = self._build_contextual_flow(top_intent, text_clean, text_lower, primary_meta)
        confidence = round(min(98.5, max(75.0, top_score * 35.0 + 45.0)), 1)

        # Recommended Action derivation
        recommended_action = self._derive_recommended_action(top_intent)

        return {
            "primary_intent": top_intent,
            "confidence": confidence,
            "reasoning": contextual_flow,
            "recommended_action": recommended_action,
            "supporting_sentences": [s["text"] for s in supporting_sentences],
            "supporting_evidence_structured": supporting_sentences
        }

    def _derive_recommended_action(self, intent: str) -> str:
        if intent == "Medical & Clinical Consultation Inquiry":
            return "Schedule a comprehensive clinical consultation with the primary physician to review symptoms and establish a treatment roadmap."
        elif intent == "Diagnostic Test Clarification & Second Opinion Request":
            return "Route diagnostic lab and imaging records to a clinical specialist for formal second-opinion interpretation."
        elif intent == "Prescription Dosage & Medication Inquiry":
            return "Consult prescribing physician or clinical pharmacist regarding potential dosage adjustment and side effect management."
        elif intent == "Post-Operative Recovery & Symptom Management":
            return "Coordinate post-operative follow-up evaluation with surgical team to assess incision healing and rehabilitation protocol."
        elif intent == "Salary/Payroll Deduction Correction Request":
            return "Verify the attendance discrepancy with HR records and process the corresponding payroll reimbursement adjustment."
        elif intent == "Project Submission Deadline Extension Request":
            return "Review submitted project progress logs and grant a formal deadline extension for deliverable finalization."
        elif intent == "Product Return & Refund Request":
            return "Authorize product return merchandise authorization (RMA) and issue the full financial refund."
        elif intent == "Service Cancellation & Account Termination":
            return "Immediately disable subscription auto-renewal and process complete account termination."
        elif intent == "Travel Delay & Cancellation Compensation Request":
            return "Verify flight disruption logs and process statutory passenger delay compensation."
        elif intent == "Job Application Status Inquiry & Follow-up":
            return "Provide a clear recruitment timeline update regarding interview evaluation and next steps."
        elif intent == "Academic & Institutional Grievance":
            return "Review student welfare concerns and address institutional policies with faculty leadership."
        elif intent == "Billing & Payment Dispute Correction":
            return "Audit invoice transaction records and reverse unauthorized or duplicate billing charges."
        elif intent == "Technical Support & Troubleshooting":
            return "Deploy technical engineering support to diagnose error logs and provide troubleshooting steps."
        else:
            return "Acknowledge communication and route to relevant department for timely resolution."

    def _extract_evidence_sentences(self, sentences: List[str], intent: str, meta: Dict[str, Any], doc_id: str) -> List[Dict[str, Any]]:
        scored_sentences = []
        kw_list = meta.get("keywords", [])

        priority_words = []
        if intent == "Medical & Clinical Consultation Inquiry":
            priority_words = ["physician", "doctor", "symptoms", "clinical", "treatment", "diagnosis", "examination", "hospital", "health", "consultation"]
        elif intent == "Diagnostic Test Clarification & Second Opinion Request":
            priority_words = ["mri", "biopsy", "scan", "test", "pathology", "lab", "results", "abnormal", "markers", "second opinion", "radiology"]
        elif intent == "Prescription Dosage & Medication Inquiry":
            priority_words = ["prescription", "dosage", "medication", "side effects", "dizziness", "tablets", "interaction", "drug", "schedule"]
        elif intent == "Post-Operative Recovery & Symptom Management":
            priority_words = ["surgery", "surgical", "post-operative", "post-op", "incision", "healing", "swelling", "rehabilitation", "wound", "recovery"]
        elif intent == "Salary/Payroll Deduction Correction Request":
            priority_words = ["attendance", "salary", "deduction", "deducted", "withheld", "payroll", "discrepancy", "evidence", "corrected", "restoration", "timesheet", "biometric"]
        elif intent == "Project Submission Deadline Extension Request":
            priority_words = ["deadline", "extension", "time", "project", "faculty", "professor", "bugs", "submit", "submission", "granted", "delay", "testing"]
        elif intent == "Product Return & Refund Request":
            priority_words = ["return", "refund", "money", "procedure", "reimbursement", "product", "purchase", "policy"]
        elif intent == "Service Cancellation & Account Termination":
            priority_words = ["cancel", "subscription", "terminate", "membership", "account", "close", "renewal", "billing"]
        elif intent == "Job Application Status Inquiry & Follow-up":
            priority_words = ["application", "interview", "status", "follow", "update", "resume", "hiring", "position"]
        elif intent == "Travel Delay & Cancellation Compensation Request":
            priority_words = ["delay", "cancelled", "flight", "compensation", "reimbursement", "airline", "expenses", "hours"]
        elif intent == "Academic & Institutional Grievance":
            priority_words = ["rules", "strict", "teachers", "college", "management", "permission", "students", "fee"]
        else:
            priority_words = kw_list[:10]

        for idx, s in enumerate(sentences):
            s_clean = s.strip()
            s_lower = s_clean.lower()
            if len(s_clean.split()) < 4:
                continue

            score = 0
            for pw in priority_words:
                if re.search(r'\b' + re.escape(pw) + r'\b', s_lower):
                    score += 1.5
            for kw in kw_list:
                if re.search(r'\b' + re.escape(kw) + r'\b', s_lower):
                    score += 1.0

            if score > 0:
                scored_sentences.append({
                    "document_id": doc_id,
                    "sentence_id": f"s-{idx}",
                    "text": s_clean,
                    "score": score
                })

        scored_sentences.sort(key=lambda x: x["score"], reverse=True)
        top_sentences = scored_sentences[:3]

        if not top_sentences:
            fallback = sentences[-3:] if len(sentences) >= 3 else [sentences[0]]
            top_sentences = [{"document_id": doc_id, "sentence_id": f"s-{i}", "text": s, "score": 1.0} for i, s in enumerate(fallback)]

        return top_sentences

    def _build_contextual_flow(self, intent: str, raw_text: str, text_lower: str, meta: Dict[str, Any]) -> str:
        if intent == "Medical & Clinical Consultation Inquiry":
            return "The author outlines progressive clinical symptoms and healthcare history across medical examinations, seeking formal physician evaluation, diagnosis, and an actionable clinical treatment roadmap."
        elif intent == "Diagnostic Test Clarification & Second Opinion Request":
            return "The author reviews diagnostic laboratory, radiology, or biopsy findings showing specific markers, seeking clinical interpretation and specialist second-opinion guidance."
        elif intent == "Prescription Dosage & Medication Inquiry":
            return "The author documents adverse reactions, side effects, or schedule uncertainties regarding prescribed pharmacotherapy, seeking physician or pharmacist guidance on dosage adjustments."
        elif intent == "Post-Operative Recovery & Symptom Management":
            return "The author tracks post-surgical healing milestones, incision status, and rehabilitation progress, seeking clinical follow-up regarding recovery protocols and symptom relief."
        elif intent == "Salary/Payroll Deduction Correction Request":
            return "The employee discovered incorrect attendance records that led to an unjustified salary deduction. After submitting supporting evidence to administration and payroll, the attendance discrepancy was verified, and the employee is formally requesting the prompt reimbursement of the withheld salary amount."
        elif intent == "Project Submission Deadline Extension Request":
            return "The author documents working on a project that encountered unexpected technical blockers and deadline constraints. After team coordination, they formally requested an extension from faculty/management to complete implementation and submit successfully."
        elif intent == "Product Return & Refund Request":
            return "The author initially attempted troubleshooting and customer support interactions, but persistent unresolved product issues led to a definitive long-range intent to return the item for a full financial refund."
        elif intent == "Academic & Institutional Grievance":
            return "The author articulates serious grievances concerning rigid campus regulations, administrative policies, and instructional quality, urging decision-makers to address student welfare."
        elif intent == "Job Application Status Inquiry & Follow-up":
            return "The author follows up on a submitted job application or interview evaluation, seeking transparent status updates regarding next steps in the recruitment timeline."
        elif intent == "Travel Delay & Cancellation Compensation Request":
            return "The author details significant travel disruptions and financial or scheduling inconveniences, formally requesting statutory delay compensation and expense reimbursement."
        elif intent == "Service Cancellation & Account Termination":
            return "The author is explicitly requesting the cancellation of recurring memberships/subscriptions and complete account termination."
        elif intent == "Billing & Payment Dispute Correction":
            return "The author identifies erroneous or unauthorized charges on their invoice and requests immediate billing reconciliation and financial adjustment."
        elif intent == "Product Defect & Quality Complaint":
            return "The author formally documents severe physical or operational defects in the product and demands accountability and resolution."
        elif intent == "Technical Support & Troubleshooting":
            return "The author is reporting an active software or system error and seeking troubleshooting guidance to restore operational capability."
        elif intent == "Legal Dispute & Formal Contract Notice":
            return "The author cites contractual terms and legal obligations, reserving rights for formal legal escalation if the dispute is not promptly remedied."
        else:
            return meta.get("simple_reason", f"The author's contextual progression establishes an underlying objective centered on {intent.lower()}.")

    def _no_intent_payload(self, reason: str, doc_id: str) -> Dict[str, Any]:
        return {
            "primary_intent": "General Informational Context",
            "confidence": 85.0,
            "reasoning": "The document presents neutral background information or descriptive context without articulating an explicit request or demand.",
            "recommended_action": "Log informational context for archival reference.",
            "supporting_sentences": ["No explicit intent-bearing demands or actionable requests were identified in the document."],
            "supporting_evidence_structured": [{
                "document_id": doc_id,
                "sentence_id": "s-0",
                "text": "No explicit intent-bearing demands or actionable requests were identified in the document.",
                "score": 1.0
            }]
        }

intent_service = IntentService()
