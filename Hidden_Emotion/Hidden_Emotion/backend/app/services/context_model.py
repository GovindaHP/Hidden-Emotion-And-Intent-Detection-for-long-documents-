import re
from typing import List, Dict, Any, Optional

TEMPORAL_MARKERS = [
    "initially", "at first", "in the beginning", "firstly", "originally",
    "then", "next", "after that", "subsequently", "the next day", "the next morning",
    "following this", "after a few hours", "several days later", "two weeks later",
    "meanwhile", "however", "furthermore", "in the meantime", "as time passed",
    "eventually", "finally", "in the end", "ultimately", "at last", "to conclude"
]

DOMAIN_PATTERNS = {
    "travel": [
        r'\b(flight|airline|airport|transit|boarding|luggage|baggage|layover|connecting flight|terminal)\b',
        r'\b(train|railway|station|itinerary|travel disruption|missed connection)\b'
    ],
    "freelance": [
        r'\b(freelance|client|project scope|scope creep|milestone|deliverables|hourly rate|invoice)\b',
        r'\b(contract|revisions|design work|development contract|upfront deposit|final payment)\b'
    ],
    "housing": [
        r'\b(tenant|landlord|apartment|rental|lease|maintenance|plumbing|leak|repair|property manager)\b',
        r'\b(security deposit|rent deduction|housing inspection|uninhabitable|water damage)\b'
    ],
    "event": [
        r'\b(concert|conference|festival|tickets|venue|organizer|postponed|postponement|rescheduled)\b',
        r'\b(event pass|non-refundable|booking fee|ticket refund|travel loss)\b'
    ],
    "banking": [
        r'\b(bank|account|transaction|unauthorized charge|credit card|debit|fraud|statement|chargeback)\b',
        r'\b(banking app|security team|disputed amount|funds restored|provisional credit)\b'
    ],
    "academic": [
        r'\b(exam|examination|grades|marks|revaluation|university|faculty|professor|transcript|evaluation)\b',
        r'\b(coursework|paper recheck|academic review|revised result|grading discrepancy)\b'
    ],
    "payroll": [
        r'\b(attendance|timesheet|biometric|punch in|payroll|salary|payslip|salary deduction|withheld|wages)\b',
        r'\b(unjustified deduction|attendance corrected|payroll adjustment|reimbursed pay)\b'
    ],
    "consumer": [
        r'\b(purchased|product|device|hardware|defect|broken|warranty|customer support|return procedure|refund)\b'
    ],
    "medical": [
        r'\b(physician|doctor|cardiologist|oncologist|clinic|hospital|biopsy|mri|ct scan|pathology|diagnosis)\b',
        r'\b(prescription|dosage|medication|side effects|surgery|post-operative|wound healing|symptoms)\b'
    ]
}

class ChunkEvent:
    def __init__(
        self,
        chunk_id: str,
        paragraph_id: int,
        sentence_range: tuple,
        text: str,
        temporal_marker: Optional[str] = None
    ):
        self.chunk_id = chunk_id
        self.paragraph_id = paragraph_id
        self.sentence_range = sentence_range
        self.text = text
        self.temporal_marker = temporal_marker
        self.event_summary: str = ""
        self.actor: str = "Author"
        self.action: str = ""
        self.object: str = ""
        self.cause: str = ""
        self.consequence: str = ""
        self.emotion_clue: str = ""
        self.problem: str = ""
        self.desired_outcome: str = ""
        self.temporal_position: str = "middle"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "paragraph_id": self.paragraph_id,
            "sentence_range": self.sentence_range,
            "temporal_marker": self.temporal_marker,
            "temporal_position": self.temporal_position,
            "event_summary": self.event_summary,
            "actor": self.actor,
            "action": self.action,
            "object": self.object,
            "cause": self.cause,
            "consequence": self.consequence,
            "emotion_clue": self.emotion_clue,
            "problem": self.problem,
            "desired_outcome": self.desired_outcome,
            "text_preview": self.text[:80] + "..." if len(self.text) > 80 else self.text
        }

class DocumentContextMemory:
    """
    Maintains persistent, sequential long-document context across chunks.
    Ensures zero cross-document contamination by strictly instantiating per-document state.
    """
    def __init__(self, doc_id: str):
        self.doc_id = doc_id
        self.domain: str = "general"
        self.entities: set = set()
        self.events: List[Dict[str, Any]] = []
        self.problems: List[str] = []
        self.actions: List[str] = []
        self.emotions: List[str] = []
        self.unresolved_issues: List[str] = []
        self.desired_outcomes: List[str] = []
        self.resolution_status: str = "unresolved"
        self.resolution_details: str = ""
        self.goal_chain: List[Dict[str, Any]] = []
        self.causal_chain: List[str] = []

    def update_with_chunk(self, chunk_event: ChunkEvent):
        evt_dict = chunk_event.to_dict()
        self.events.append(evt_dict)

        if chunk_event.problem and chunk_event.problem not in self.problems:
            self.problems.append(chunk_event.problem)
            self.unresolved_issues.append(chunk_event.problem)

        if chunk_event.action and chunk_event.action not in self.actions:
            self.actions.append(chunk_event.action)

        if chunk_event.emotion_clue and chunk_event.emotion_clue not in self.emotions:
            self.emotions.append(chunk_event.emotion_clue)

        if chunk_event.desired_outcome:
            if not self.desired_outcomes or self.desired_outcomes[-1] != chunk_event.desired_outcome:
                self.desired_outcomes.append(chunk_event.desired_outcome)
                self.goal_chain.append({
                    "stage": chunk_event.temporal_position,
                    "goal": chunk_event.desired_outcome,
                    "action": chunk_event.action
                })

        # Check resolution clues
        lower_text = chunk_event.text.lower()
        has_resolution_clues = any(re.search(r'\b' + re.escape(w) + r'\b', lower_text) for w in [
            "refunded", "reimbursed", "credited back", "restored", "approved the adjustment",
            "revised my score", "updated my grade", "revaluation was successful", "sent final payment",
            "settled the invoice", "repair was completed", "repaired the damage", "agreed to compensate",
            "finally resolved", "closure reached", "formally rectified", "reassurance provided"
        ])
        if has_resolution_clues:
            self.resolution_status = "resolved"
            self.unresolved_issues = [p for p in self.unresolved_issues if "resolved" not in p.lower()]
            self.resolution_details = chunk_event.text[:120]

        # Build causal step
        if chunk_event.cause and chunk_event.consequence:
            causal_step = f"{chunk_event.cause} -> {chunk_event.consequence}"
            if causal_step not in self.causal_chain:
                self.causal_chain.append(causal_step)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "domain": self.domain,
            "problems": self.problems,
            "actions": self.actions,
            "emotions": self.emotions,
            "unresolved_issues": self.unresolved_issues,
            "desired_outcomes": self.desired_outcomes,
            "resolution_status": self.resolution_status,
            "resolution_details": self.resolution_details,
            "goal_chain": self.goal_chain,
            "causal_chain": self.causal_chain,
            "total_events": len(self.events)
        }

class EventExtractorService:
    """
    Extracts structured event models from semantic chunks and builds context memory.
    """
    @staticmethod
    def extract_chunk_event(
        chunk_dict: Dict[str, Any], 
        idx: int, 
        total_chunks: int,
        domain: str
    ) -> ChunkEvent:
        text = chunk_dict.get("text", "").strip()
        lower = text.lower()
        chunk_id = f"chk-{idx}"
        para_id = chunk_dict.get("paragraph_id", idx)
        s_range = (chunk_dict.get("start_sent", idx), chunk_dict.get("end_sent", idx))

        # Detect temporal marker
        found_marker = None
        for tm in TEMPORAL_MARKERS:
            if re.search(r'\b' + re.escape(tm) + r'\b', lower):
                found_marker = tm
                break

        # Assign relative position
        if idx == 0:
            pos = "beginning"
        elif idx == total_chunks - 1:
            pos = "ending"
        elif idx >= total_chunks * 0.5:
            pos = "peak_later"
        else:
            pos = "middle"

        event = ChunkEvent(
            chunk_id=chunk_id,
            paragraph_id=para_id,
            sentence_range=s_range,
            text=text,
            temporal_marker=found_marker
        )
        event.temporal_position = pos

        # Extract Actor & Object
        if any(w in lower for w in ["i ", "my ", "we ", "our "]):
            event.actor = "Author"

        # Domain-aware Event, Problem, Action, Desired Outcome extraction
        if domain == "travel":
            if any(w in lower for w in ["delay", "delayed", "grounded", "snowstorm", "technical glitch", "maintenance problem"]):
                event.problem = "Flight delay and transit interruption"
                event.cause = "Operational disruption or mechanical delay"
                event.consequence = "Risk of missed connection and schedule disruption"
            if any(w in lower for w in ["missed connection", "stranded", "overnight", "hotel", "food expenses", "taxi"]):
                event.problem = "Missed connection and incurred out-of-pocket expenses"
                event.cause = "Flight connection failure"
                event.consequence = "Unplanned accommodation and transit expenses"
            if any(w in lower for w in ["contacted", "spoke to agent", "submitted receipts", "filed claim", "emailed airline"]):
                event.action = "Contacted carrier and submitted receipts for reimbursement"
            if any(w in lower for w in ["reimbursement", "compensation", "cover expenses", "pay back", "refund"]):
                event.desired_outcome = "Full reimbursement of delay-related expenses and statutory compensation"

        elif domain == "freelance":
            if any(w in lower for w in ["initial agreement", "agreed upon", "scope", "contract started"]):
                event.event_summary = "Initial freelance contract established"
            if any(w in lower for w in ["scope expansion", "extra features", "additional requests", "added tasks", "beyond scope"]):
                event.problem = "Client requested additional work exceeding agreed contract scope"
                event.cause = "Scope creep and uncompensated revisions"
                event.consequence = "Extra engineering/design hours without confirmed budget"
            if any(w in lower for w in ["refused to pay", "dispute", "disagreement", "withholding final payment"]):
                event.problem = "Payment dispute regarding completed out-of-scope work"
            if any(w in lower for w in ["negotiated", "itemized invoice", "sent documentation", "discussed terms"]):
                event.action = "Provided itemized hours and engaged in settlement negotiation"
            if any(w in lower for w in ["release payment", "pay the invoice", "settle balance", "remit remaining"]):
                event.desired_outcome = "Payment settlement for delivered out-of-scope milestones"

        elif domain == "housing":
            if any(w in lower for w in ["leak", "water damage", "plumbing", "heating", "mold", "broken window", "repair needed"]):
                event.problem = "Severe rental property maintenance defects and water leakage"
                event.cause = "Unaddressed structural or plumbing failures"
                event.consequence = "Damaged personal property and uninhabitable living space"
            if any(w in lower for w in ["ignored", "delayed repair", "landlord refused", "no response"]):
                event.problem = "Landlord failure to execute timely property repairs"
            if any(w in lower for w in ["hired professional", "paid for repair", "withheld rent", "notified landlord", "deducted cost"]):
                event.action = "Commissioned emergency repairs and requested rent adjustment"
            if any(w in lower for w in ["rent reduction", "reimburse repair", "adjust rent", "compensate damage"]):
                event.desired_outcome = "Reimbursement of out-of-pocket repair costs and rental fee adjustment"

        elif domain == "event":
            if any(w in lower for w in ["postponed", "cancelled", "rescheduled", "schedule change", "date shifted"]):
                event.problem = "Event cancellation or indefinite date postponement"
                event.cause = "Organizer rescheduling or logistical changes"
                event.consequence = "Inability to attend new date and wasted travel arrangements"
            if any(w in lower for w in ["contacted organizer", "requested refund", "disputed non-refundable policy"]):
                event.action = "Requested ticket refund and submitted non-attendance notice"
            if any(w in lower for w in ["refund", "full refund", "cover travel", "hotel voucher", "ticket fee"]):
                event.desired_outcome = "Full refund of ticket fees and compensation for non-recoverable travel losses"

        elif domain == "banking":
            if any(w in lower for w in ["unauthorized", "unknown transaction", "fraudulent charge", "not recognized", "statement error"]):
                event.problem = "Unauthorized fraudulent transaction detected on bank statement"
                event.cause = "Compromised card or erroneous debit processing"
                event.consequence = "Financial balance deduction and security risk"
            if any(w in lower for w in ["blocked card", "called fraud department", "filed dispute", "freeze"]):
                event.action = "Frozen payment card and filed formal banking fraud dispute"
            if any(w in lower for w in ["restore funds", "credit back", "reimbursement", "chargeback", "reverse charge"]):
                event.desired_outcome = "Reversal of unauthorized charge and restoration of account balance"

        elif domain == "academic":
            if any(w in lower for w in ["unexpected result", "low grade", "marks discrepancy", "scoring error", "failed practical"]):
                event.problem = "Unexpectedly low examination score or grading discrepancy"
                event.cause = "Potential evaluation omission or administrative tallying error"
                event.consequence = "Negative impact on academic transcript and degree progression"
            if any(w in lower for w in ["applied for revaluation", "submitted appeal", "requested answer script", "spoke to faculty"]):
                event.action = "Submitted formal answer script re-evaluation request with supporting coursework evidence"
            if any(w in lower for w in ["revised grade", "revaluation", "recalculate marks", "grade adjustment"]):
                event.desired_outcome = "Objective re-evaluation and formal grade score correction"

        elif domain == "payroll":
            if any(w in lower for w in ["salary deduction", "deducted", "withheld", "marked absent", "timesheet mismatch"]):
                event.problem = "Erroneous attendance record causing unjustified salary deduction"
                event.cause = "Biometric punch-in failure or administrative timesheet mismatch"
                event.consequence = "Withheld monthly wages affecting personal financial security"
            if any(w in lower for w in ["gathered timesheets", "contacted payroll", "emailed hr", "submitted logs"]):
                event.action = "Submitted biometric verification logs to HR and payroll department"
            if any(w in lower for w in ["restore salary", "reimburse deduction", "reimbursement", "payroll adjustment"]):
                event.desired_outcome = "Correction of attendance logs and full reimbursement of withheld salary"

        elif domain == "consumer":
            if any(w in lower for w in ["defective", "stopped working", "hardware defect", "hardware failure"]):
                event.problem = "Product hardware malfunction and failure to perform as advertised"
                event.cause = "Defective manufacturing or component failure"
                event.consequence = "Unusable device and wasted purchase expenditure"
            if any(w in lower for w in ["troubleshot", "called support", "reset device", "returned"]):
                event.action = "Completed troubleshooting steps and initiated return procedure"
            if any(w in lower for w in ["refund", "money back", "return item"]):
                event.desired_outcome = "Return of defective merchandise and full purchase price refund"

        elif domain == "medical":
            if any(w in lower for w in ["symptoms", "pain", "tightness", "shortness of breath", "abnormal markers"]):
                event.problem = "Unexplained physical symptoms and alarming diagnostic test markers"
                event.cause = "Underlying medical condition or post-viral inflammation"
                event.consequence = "Severe health anxiety and impaired physical wellbeing"
            if any(w in lower for w in ["consulted doctor", "underwent mri", "blood tests", "saw specialist"]):
                event.action = "Underwent diagnostic imaging and consulted medical specialist"
            if any(w in lower for w in ["treatment plan", "second opinion", "reassurance", "recovery roadmap"]):
                event.desired_outcome = "Accurate medical diagnosis, specialist clarification, and effective treatment roadmap"

        # Emotional clues extraction
        if any(w in lower for w in ["anxious", "anxiety", "worried", "fear", "stress", "nervous"]):
            event.emotion_clue = "Anxiety & Concern"
        elif any(w in lower for w in ["frustrated", "irritated", "furious", "angry", "annoyed", "unacceptable"]):
            event.emotion_clue = "Frustration & Irritation"
        elif any(w in lower for w in ["disappointed", "exhausted", "hopeless", "drained"]):
            event.emotion_clue = "Disappointment & Exhaustion"
        elif any(w in lower for w in ["relieved", "relief", "satisfied", "closure", "grateful"]):
            event.emotion_clue = "Relief & Satisfaction"
        elif any(w in lower for w in ["hopeful", "optimistic", "eager"]):
            event.emotion_clue = "Hope & Anticipation"

        return event

    @staticmethod
    def identify_domain(text: str, custom_hints: str = None) -> str:
        text_lower = text.lower()
        if custom_hints:
            hint_lower = custom_hints.lower()
            for dom in DOMAIN_PATTERNS.keys():
                if dom in hint_lower:
                    return dom

        domain_scores = {dom: 0 for dom in DOMAIN_PATTERNS.keys()}
        for dom, patterns in DOMAIN_PATTERNS.items():
            for pat in patterns:
                matches = len(re.findall(pat, text_lower))
                domain_scores[dom] += matches

        sorted_doms = sorted(domain_scores.items(), key=lambda x: x[1], reverse=True)
        if sorted_doms[0][1] >= 2:
            return sorted_doms[0][0]
        return "general"

context_model_service = EventExtractorService()
