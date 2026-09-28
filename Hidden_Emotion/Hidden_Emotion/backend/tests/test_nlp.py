import pytest
from app.services.nlp_preprocessor import nlp_preprocessor
from app.services.emotion_service import emotion_service
from app.services.intent_service import intent_service
from app.services.report_generator import report_generator
from app.services.responder_service import responder_service
from app.services.summarizer_service import summarizer_service

# Document Samples for Regression Suite
DOC_A_PRODUCT_REFUND = """
I bought this smart speaker with high expectations for home automation. 
When audio distortion and connection failures occurred, I immediately contacted customer support and performed multiple troubleshooting steps.
The support representative asked me to repeat factory resets and firmware updates that I had already attempted three times. 
After two weeks of frustrating back and forth, the hardware defect persists and the device remains completely unusable.
I would rather return the item through the proper procedure and have the amount I paid handled according to the applicable policy.
I believe returning the product and receiving the appropriate refund is the most practical resolution for this unfortunate purchase.
"""

DOC_B_PROJECT_EXTENSION = """
Our student engineering team started developing our major capstone project with immense excitement and confidence. 
We planned our architecture, set up the database, and began building the core machine learning models. 
However, as we integrated the backend APIs with the transformer pipeline, unexpected runtime exceptions and critical bugs surfaced. 
With the final submission deadline rapidly approaching, the pressure on our group increased tremendously. 
We experienced severe stress, anxiety, and sleepless nights trying to debug complex integration errors. 
After evaluating our remaining tasks, we had an urgent team discussion and decided to reach out to our project guide and faculty. 
We formally communicated the technical hurdles we encountered and requested a three-day deadline extension to complete testing. 
Our professor reviewed our progress and generously granted an extension for our final project submission. 
With the additional time provided, our team worked with renewed determination, resolved all blockers, and successfully submitted the complete project. 
We felt immense relief, pride, and satisfaction seeing our hard work reach completion.
"""

DOC_C_PAYROLL_DEDUCTION = """
I joined the new financial quarter with great excitement and high professional confidence in our department.
However, upon reviewing my monthly payslip, I was shocked and confused to discover a significant salary deduction.
I immediately checked the attendance and biometric punch-in logs and found that two working days were incorrectly marked as unexcused absences.
I felt growing anxiety, frustration, and irritation over this unjustified payroll deduction impacting my personal finances.
I gathered all supporting timesheet evidence, badge swipe logs, and project commit histories to prove my presence.
I contacted company administration and the payroll department to report the attendance discrepancy and submit my evidence.
The payroll specialist investigated the logs, confirmed the biometric system mismatch, and verified that my attendance was corrected.
Administration approved the payroll adjustment, confirming that the withheld salary amount will be fully restored in the next cycle.
I felt profound relief, satisfaction, and closure knowing that the mistake was formally rectified and my compensation will be reimbursed.
"""

DOC_D_MEDICAL_DIAGNOSTIC_REPORT = """
I have been experiencing progressive chest tightness, recurring palpitations, and shortness of breath during routine daily exertion.
Initial clinical examination at the clinic prompted the physician to order diagnostic laboratory blood tests and a cardiac MRI scan.
Upon reviewing the diagnostic findings, the pathology report indicated mildly elevated inflammatory markers and abnormal cardiac imaging patterns.
I felt profound health anxiety, fear, and vulnerability worrying about potential long-term cardiovascular prognosis.
I am consulting with the attending cardiologist and specialist team to request a detailed clinical interpretation of these scan results and a second medical opinion.
The cardiologist conducted a thorough clinical evaluation, reassured me that the findings indicate benign post-viral pericardial inflammation, and outlined an actionable pharmacotherapy treatment plan.
I felt immense relief, reassurance, and guarded hope knowing that the condition is fully manageable with targeted anti-inflammatory medication and guided recovery.
"""

DOC_E_POST_OPERATIVE_RECOVERY = """
Following my orthopedic knee ligament reconstruction surgery last Tuesday, I have been closely monitoring my post-operative recovery milestones.
During the first four days post-surgery, I developed localized swelling, incision stiffness, and moderate discomfort around the surgical site.
I felt anxious and apprehensive about whether the incision drainage and mobility restriction were normal stages of wound healing.
I contacted the surgical care team and attending orthopedic surgeon to evaluate my post-operative symptoms and review allowable physical activity.
The surgical specialist examined the knee incision, confirmed that tissue healing is progressing normally without infection, and adjusted my physical rehabilitation protocol.
I felt reassuring relief and renewed determination to follow the guided physiotherapy exercises for full mobility restoration.
"""

DOC_F_PRESCRIPTION_DOSAGE_INQUIRY = """
Three weeks ago, my physician prescribed a new antihypertensive medication to manage elevated blood pressure levels.
While the medication has stabilized my arterial pressure readings, I have developed severe dizziness, lightheadedness, and morning nausea.
These adverse drug side effects have made it difficult to drive safely and perform standard workplace responsibilities.
I am reaching out to the prescribing physician and clinical pharmacist to request professional guidance regarding dosage adjustment or an alternative medication schedule.
I want to ensure my cardiovascular management remains effective while eliminating these disruptive side effects.
"""

def test_nlp_preprocessor_chunking():
    sample_text = "This is sentence one. " * 50 + "This is sentence two. " * 50
    chunks = nlp_preprocessor.create_semantic_chunks(sample_text, chunk_size=100, overlap=20)
    assert len(chunks) >= 2
    assert "text" in chunks[0]
    assert "word_count" in chunks[0]

def test_document_switching_regression_sequence_A_B_C_A_C_B():
    """
    Part 10 Regression Test:
    Execute sequential analyses in the exact sequence A -> B -> C -> A -> C -> B.
    Guarantees zero cross-document contamination, no stale state, and strictly grounded hidden emotions.
    """
    # 1. Run A (Product Return / Refund)
    rep_a1 = report_generator.generate(DOC_A_PRODUCT_REFUND, filename="Doc_A_Refund.txt", doc_id="DOC-A1")
    assert rep_a1["global_intent"] == "Product Return & Refund Request"
    assert "health" not in rep_a1["hidden_emotion"].lower()
    assert "financial" not in rep_a1["hidden_emotion"].lower()
    assert "Determination" in rep_a1["hidden_emotion"] or "Trust" in rep_a1["hidden_emotion"]
    assert "Firm Determination" in rep_a1["overall_tone"]

    # 2. Run B (Project Deadline Extension)
    rep_b1 = report_generator.generate(DOC_B_PROJECT_EXTENSION, filename="Doc_B_Project.txt", doc_id="DOC-B1")
    assert rep_b1["global_intent"] == "Project Submission Deadline Extension Request"
    assert "health" not in rep_b1["hidden_emotion"].lower()
    assert "financial" not in rep_b1["hidden_emotion"].lower()
    assert "Academic" in rep_b1["hidden_emotion"] or "Relieved Pride" in rep_b1["hidden_emotion"]
    assert "Relief, Pride and Satisfaction" in rep_b1["overall_tone"]

    # 3. Run C (Payroll Deduction Correction)
    rep_c1 = report_generator.generate(DOC_C_PAYROLL_DEDUCTION, filename="Doc_C_Payroll.txt", doc_id="DOC-C1")
    assert rep_c1["global_intent"] == "Salary/Payroll Deduction Correction Request"
    assert "health" not in rep_c1["hidden_emotion"].lower()
    assert "medical" not in rep_c1["hidden_emotion"].lower()
    assert "prognosis" not in rep_c1["hidden_emotion"].lower()
    assert "financial security" in rep_c1["hidden_emotion"].lower()
    assert rep_c1["overall_tone"] == "Relief and Satisfaction after Prolonged Anxiety and Frustration"

    # 4. Run A again
    rep_a2 = report_generator.generate(DOC_A_PRODUCT_REFUND, filename="Doc_A_Refund_2.txt", doc_id="DOC-A2")
    assert rep_a2["global_intent"] == "Product Return & Refund Request"
    assert "financial" not in rep_a2["hidden_emotion"].lower()

    # 5. Run C again
    rep_c2 = report_generator.generate(DOC_C_PAYROLL_DEDUCTION, filename="Doc_C_Payroll_2.txt", doc_id="DOC-C2")
    assert rep_c2["global_intent"] == "Salary/Payroll Deduction Correction Request"
    assert "health" not in rep_c2["hidden_emotion"].lower()
    assert "financial security" in rep_c2["hidden_emotion"].lower()

    # 6. Run B again
    rep_b2 = report_generator.generate(DOC_B_PROJECT_EXTENSION, filename="Doc_B_Project_2.txt", doc_id="DOC-B2")
    assert rep_b2["global_intent"] == "Project Submission Deadline Extension Request"
    assert "financial" not in rep_b2["hidden_emotion"].lower()

def test_payroll_document_comprehensive_context_and_trajectory():
    """
    Verify complete grounding of payroll document:
    - Global Intent: Salary/Payroll Deduction Correction Request
    - Dominant Emotion: Concern & Anxiety transitioning into Relief
    - Grounded Hidden Emotion: Underlying Concern for Financial Security & Desire for Fair Resolution
    - Grounded Overall Tone: Relief and Satisfaction after Prolonged Anxiety and Frustration
    - Zero foreign medical or clinical terms
    """
    report = report_generator.generate(DOC_C_PAYROLL_DEDUCTION, filename="Payroll_Discrepancy.txt", doc_id="DOC-PAYROLL-001")
    
    # 1. Intent Verification (Must not be modified)
    assert report["global_intent"] == "Salary/Payroll Deduction Correction Request"
    assert report["intent_analysis"]["primary_intent"] == "Salary/Payroll Deduction Correction Request"
    assert report["intent_analysis"]["confidence"] >= 75.0
    
    # 2. Contextual Flow
    reasoning = report["contextual_flow"].lower()
    assert "attendance" in reasoning
    assert "salary" in reasoning or "payroll" in reasoning or "withheld" in reasoning
    
    # 3. Trajectory Progression (Unconcerned/Excited -> Concerned/Anxious -> Hopeful -> Relieved/Satisfied/Closure)
    traj = report["emotion_trajectory"]
    assert "Excitement" in traj["beginning_state"] or "Confidence" in traj["beginning_state"]
    assert "Anxiety" in traj["middle_state"] or "Confusion" in traj["middle_state"] or "Frustration" in traj["middle_state"]
    assert "Relief" in traj["ending_state"] or "Satisfaction" in traj["ending_state"] or "Closure" in traj["ending_state"]

    # 4. Dominant Emotion
    assert "Concern" in report["dominant_emotion"]
    assert "Relief" in report["dominant_emotion"]

    # 5. Strictly Grounded Hidden Emotion
    hidden_emo = report["hidden_emotion"]
    assert "financial security" in hidden_emo.lower()
    assert "health" not in hidden_emo.lower()
    assert "medical" not in hidden_emo.lower()
    assert "prognosis" not in hidden_emo.lower()
    assert "patient" not in hidden_emo.lower()

    # 6. Overall Tone (Reflects both prolonged anxiety and final relief)
    assert report["overall_tone"] == "Relief and Satisfaction after Prolonged Anxiety and Frustration"

    # 7. Canonical Object Keys
    for req_field in [
        "global_intent", "emotion_trajectory", "dominant_emotion", 
        "hidden_emotion", "overall_tone", "contextual_flow", "evidence_sentences"
    ]:
        assert req_field in report

def test_medical_diagnostic_and_consultation_full_flow():
    """
    Test Medical Report Analysis: Diagnostic clarification, full emotion trajectory,
    and grounded clinical synthesis.
    """
    report = report_generator.generate(DOC_D_MEDICAL_DIAGNOSTIC_REPORT, filename="Clinical_Cardiology_Report.pdf", doc_type="Medical Report", doc_id="DOC-MED-001")
    
    # 1. Global Intent
    assert ("Diagnostic Test" in report["global_intent"] or "Medical & Clinical" in report["global_intent"])
    assert report["intent_analysis"]["confidence"] >= 75.0
    
    # 2. Contextual Flow
    reasoning = report["contextual_flow"].lower()
    assert "clinical" in reasoning or "symptoms" in reasoning or "diagnostic" in reasoning or "physician" in reasoning

    # 3. Emotion Trajectory
    traj = report["emotion_trajectory"]
    assert "Apprehension" in traj["beginning_state"] or "Concern" in traj["beginning_state"]
    assert "Health Anxiety" in traj["middle_state"] or "Fear" in traj["middle_state"]
    assert "Relief" in traj["ending_state"] or "Reassurance" in traj["ending_state"] or "Hope" in traj["ending_state"]

    # 4. Hidden Emotion (Grounded in Health Vulnerability for real medical document)
    assert "health vulnerability" in report["hidden_emotion"].lower() or "prognosis" in report["hidden_emotion"].lower()
    assert "financial" not in report["hidden_emotion"].lower()

    # 5. Overall Tone
    assert "Relief and Reassurance" in report["overall_tone"]

def test_medical_post_operative_recovery_full_flow():
    report = report_generator.generate(DOC_E_POST_OPERATIVE_RECOVERY, filename="PostOp_Knee_Recovery.txt", doc_type="Medical Report", doc_id="DOC-MED-POSTOP")
    assert report["global_intent"] == "Post-Operative Recovery & Symptom Management"
    assert "Recovery" in report["hidden_emotion"] or "Resilience" in report["hidden_emotion"]
    assert "surgical" in report["intent_analysis"]["recommended_action"].lower() or "post-operative" in report["intent_analysis"]["recommended_action"].lower()

def test_medical_prescription_dosage_inquiry_full_flow():
    report = report_generator.generate(DOC_F_PRESCRIPTION_DOSAGE_INQUIRY, filename="Prescription_Clarification.txt", doc_type="Medical Report", doc_id="DOC-MED-RX")
    assert report["global_intent"] == "Prescription Dosage & Medication Inquiry"
    assert "Medication" in report["hidden_emotion"] or "Health" in report["hidden_emotion"]
    assert "dosage" in report["intent_analysis"]["recommended_action"].lower() or "physician" in report["intent_analysis"]["recommended_action"].lower()

def test_service_cancellation_scenario():
    text = """
    I have been a subscriber to your premium streaming service for six months. 
    Recently, the service quality has dropped drastically with continuous buffering and missing features. 
    I spoke with customer care twice, but no improvement was made. 
    I am writing to formally request the immediate cancellation of my recurring subscription and closure of my account. 
    Please ensure auto-renewal is disabled and delete my billing profile.
    """
    intent_res = intent_service.analyze(text, doc_type="General", doc_id="DOC-CANCEL-001")
    assert intent_res["primary_intent"] == "Service Cancellation & Account Termination"

def test_job_application_followup_scenario():
    text = """
    I recently attended the technical interview round for the Senior Software Engineer position at your company. 
    I really enjoyed discussing system architecture with the engineering team. 
    It has been two weeks since our discussion, and I am writing to follow up on the status of my job application. 
    Could you please provide an update regarding the timeline for the next steps in the hiring process?
    """
    intent_res = intent_service.analyze(text, doc_type="General", doc_id="DOC-JOB-001")
    assert intent_res["primary_intent"] == "Job Application Status Inquiry & Follow-up"

def test_travel_delay_compensation_scenario():
    text = """
    My international flight from London to New York on flight AA204 was delayed by over seven hours due to operational negligence. 
    As a result of this extreme delay, I missed my connecting flight and had to spend the night at the airport without hotel accommodation. 
    Under statutory passenger rights regulations, I am formally filing a claim for delay compensation and reimbursement of meal expenses incurred.
    """
    intent_res = intent_service.analyze(text, doc_type="General", doc_id="DOC-TRAVEL-001")
    assert intent_res["primary_intent"] == "Travel Delay & Cancellation Compensation Request"

def test_academic_institutional_grievance():
    text = """
    The person I know goes to this college. There are many rules: no permission to go out without permission.
    Very strict and irritating teachers, those who teach computer science most don't know how to code the basics.
    Management keeps college on Saturday for extra class where teachers don't teach.
    Management fee is high and there is no good management. Please take the opinion of students into consideration.
    """
    intent_res = intent_service.analyze(text, doc_type="Customer Feedback", doc_id="DOC-ACAD-001")
    assert intent_res["primary_intent"] == "Academic & Institutional Grievance"

def test_calm_ending_not_positive_emotion():
    text = """
    I am extremely disappointed and exhausted with repeated failures. Support gave useless replies and wasted hours of my time.
    However, I am willing to cooperate with the return procedure and I hope there are no further misunderstandings.
    """
    chunks = nlp_preprocessor.create_semantic_chunks(text)
    emo_res = emotion_service.analyze(text, chunks, doc_id="DOC-CALM-001")
    assert emo_res["primary_emotion"] != "Satisfaction & Optimism"
    assert "Disappointment" in emo_res["hidden_emotion"] or "Trust" in emo_res["hidden_emotion"]

def test_summarizer_anti_hallucination():
    source = "The software development lifecycle was delayed by database migration bugs. The engineering team deployed a hotfix."
    summary = summarizer_service.generate_what_happened(source, "General", "Technical Support", "Frustration")
    assert "patient" not in summary.lower()
    assert "doctor" not in summary.lower()
    assert "hospital" not in summary.lower()
    assert "salary" not in summary.lower()

def test_deescalation_responder_for_medical():
    resp = responder_service.generate_response_script(
        primary_emotion="Health Anxiety & Apprehension transitioning into Guarded Relief",
        hidden_emotion="Masked Health Vulnerability & Prognosis Apprehension Behind Clinical Inquiries",
        intent="Diagnostic Test Clarification & Second Opinion Request",
        doc_type="Medical Report",
        summary="The patient documented abnormal cardiac imaging and requested specialist second opinion consultation."
    )
    assert "subject" in resp
    assert "response_script" in resp
    assert "Diagnostic Test" in resp["subject"]
    assert "Patient" in resp["response_script"]
