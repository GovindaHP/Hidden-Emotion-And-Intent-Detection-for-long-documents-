from typing import Dict, Any

class ResponderService:
    def generate_response_script(
        self, 
        primary_emotion: str, 
        hidden_emotion: str, 
        intent: str, 
        doc_type: str, 
        summary: str
    ) -> Dict[str, str]:
        """
        Generates an empathetic AI de-escalation response script tailored to 
        the author's explicit primary emotion and implicit hidden emotion.
        """
        summary_clean = summary.rstrip('.').strip()
        
        # Subject line and Salutation generation
        if "Diagnostic" in intent or "Test" in intent or "Opinion" in intent:
            subject = "Clinical Follow-up: Diagnostic Test Results & Second Opinion Review"
            salutation = "Dear Patient / Member,"
            opening = f"Thank you for sharing your diagnostic reports and clinical inquiries with us. We note that {summary_clean.lower()}."
        elif "Prescription" in intent or "Dosage" in intent or "Medication" in intent:
            subject = "Pharmacotherapy Guidance: Medication Schedule & Dosage Clarification"
            salutation = "Dear Patient / Member,"
            opening = f"Thank you for reaching out regarding your prescribed pharmacotherapy and dosage queries. We understand that {summary_clean.lower()}."
        elif "Post-Operative" in intent or "Post-Op" in intent or "Surgery" in intent or "Recovery" in intent:
            subject = "Post-Operative Care Coordination & Surgical Recovery Review"
            salutation = "Dear Patient,"
            opening = f"Thank you for contacting the surgical care team regarding your recovery progress and healing milestones. We note that {summary_clean.lower()}."
        elif "Medical" in intent or "Clinical" in intent:
            subject = "Clinical Consultation Guidance & Healthcare Roadmap"
            salutation = "Dear Patient / Member,"
            opening = f"Thank you for sharing your health history and clinical consultation inquiry. We acknowledge that {summary_clean.lower()}."
        elif "Salary" in intent or "Payroll" in intent or "Deduction" in intent:
            subject = "Payroll Adjustment & Attendance Record Correction Review"
            salutation = "Dear Colleague / Employee,"
            opening = f"Thank you for contacting payroll and administration regarding your attendance records and salary reconciliation. We note that {summary_clean.lower()}."
        elif "Extension" in intent or "Project" in intent:
            subject = "Official Update: Project Submission Deadline & Support Review"
            salutation = "Dear Student / Project Team,"
            opening = f"Thank you for sharing your project progress and submission details with us. We understand from your communication that {summary_clean.lower()}."
        elif "Academic" in intent or "Grievance" in intent:
            subject = "Official Response & Institutional Grievance Review"
            salutation = "Dear Student / Member,"
            opening = f"We confirm receipt of your institutional communication regarding: {summary_clean}."
        elif "Return" in intent or "Refund" in intent:
            subject = "Return Authorization & Priority Refund Confirmation"
            salutation = "Dear Customer,"
            opening = f"Thank you for reaching out regarding your purchase. We note that {summary_clean.lower()}."
        elif "Job" in intent or "Interview" in intent:
            subject = "Application Status & Recruitment Process Update"
            salutation = "Dear Applicant,"
            opening = f"Thank you for following up regarding your application. We appreciate your interest and understand that {summary_clean.lower()}."
        elif "Travel" in intent or "Flight" in intent:
            subject = "Travel Disruption Claim Review & Compensation Update"
            salutation = "Dear Traveler,"
            opening = f"We have received your travel disruption claim. We acknowledge that {summary_clean.lower()}."
        elif "Cancellation" in intent:
            subject = "Account Cancellation & Subscription Termination Notice"
            salutation = "Dear Member,"
            opening = f"We have received your request regarding account and service cancellation: {summary_clean.lower()}."
        elif "Technical" in intent:
            subject = "Technical Support Escalation & Immediate Action Plan"
            salutation = "Dear User,"
            opening = f"Thank you for reaching out regarding your technical issue. We recognize that {summary_clean.lower()}."
        elif "Legal" in intent:
            subject = "Acknowledgment of Formal Legal Communication"
            salutation = "Dear Sir / Madam,"
            opening = f"We confirm receipt of your formal communication regarding: {summary_clean}."
        else:
            subject = "Official Follow-up & Response regarding your submission"
            salutation = "Dear Correspondent,"
            opening = f"Thank you for reaching out to us. We have reviewed your communication regarding {summary_clean.lower()}."

        # Empathy Body customized to emotions
        if "Health Anxiety" in primary_emotion or "Apprehension" in primary_emotion:
            empathy_block = (
                "We understand the deep anxiety, concern, and vulnerability that medical uncertainties and symptoms can bring. "
                "Please rest assured that our clinical review team is dedicated to providing thorough, compassionate clarity and timely guidance."
            )
        elif "Relief" in primary_emotion or "Pride" in primary_emotion or "Satisfaction" in primary_emotion:
            empathy_block = (
                "We appreciate your proactive communication and patience throughout this resolution process. "
                "Ensuring complete accuracy, fairness, and prompt adjustment remains our highest priority."
            )
        elif "Frustration" in primary_emotion or "Anger" in primary_emotion:
            empathy_block = (
                "We sincerely regret the frustration and difficulty this situation has caused. "
                "Your experience is extremely important to us, and we are committed to providing a transparent, prompt resolution."
            )
        elif "Disappointment" in primary_emotion or "Sadness" in primary_emotion:
            empathy_block = (
                "We deeply appreciate you sharing your experience with us. "
                "We recognize the challenges and disappointment involved, and we want to ensure your concerns receive comprehensive care."
            )
        elif "Anxiety" in primary_emotion or "Fear" in primary_emotion or "Concern" in primary_emotion:
            empathy_block = (
                "We understand the stress, worry, and uncertainty surrounding this situation. "
                "Please rest assured that we are taking active steps to provide complete clarity, accommodation, and support."
            )
        else:
            empathy_block = (
                "We appreciate the detailed context you have provided. "
                "Our objective is to ensure your communication receives dedicated attention and a constructive outcome."
            )

        # Addressing Hidden Emotion Cues
        if "health vulnerability" in hidden_emotion.lower() or "prognosis" in hidden_emotion.lower():
            hidden_block = (
                "We recognize that behind clinical questions lies natural health apprehension. "
                "Note: This analysis is for organizational preparation and does not substitute direct medical consultation with your attending physician."
            )
        elif "financial security" in hidden_emotion.lower() or "fairness" in hidden_emotion.lower():
            hidden_block = "We recognize how critical accurate compensation is to your peace of mind and are prioritizing this adjustment immediately."
        elif "Relieved Pride" in hidden_emotion or "Resilience" in hidden_emotion:
            hidden_block = "We acknowledge the intense effort and persistence demonstrated throughout this process and stand ready to assist with any further steps."
        elif "Repressed Frustration" in hidden_emotion or "Civility" in hidden_emotion:
            hidden_block = "We also recognize the ongoing friction behind this matter, even where expressed with formal civility, and are addressing the underlying root causes directly."
        elif "Masked Panic" in hidden_emotion or "Anxiety" in hidden_emotion:
            hidden_block = "We understand the time-sensitive urgency and have expedited your file for immediate review."
        elif "Cautious Hope" in hidden_emotion or "Optimism" in hidden_emotion:
            hidden_block = "We share your focus on achieving a positive, constructive resolution and are actively working to finalize next steps."
        else:
            hidden_block = "We are treating your file with priority to deliver a seamless resolution."

        closing = (
            "Our team is actively reviewing the details. You will receive a direct follow-up update within 24 hours. "
            "If you have additional context or questions, please reply directly to this communication.\n\n"
            "Sincerely,\n"
            "Care Coordination & Support Team"
        )

        full_script = f"{salutation}\n\n{opening}\n\n{empathy_block} {hidden_block}\n\n{closing}"

        return {
            "subject": subject,
            "response_script": full_script,
            "target_intent": intent,
            "primary_emotion_addressed": primary_emotion,
            "hidden_emotion_addressed": hidden_emotion
        }

responder_service = ResponderService()
