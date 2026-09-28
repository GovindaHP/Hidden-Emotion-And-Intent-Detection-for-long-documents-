class ReportRenderer {
  static render(report) {
    const container = document.getElementById('reportOutputContainer');
    if (!container) return;

    container.classList.remove('d-none');

    // 1. Document Metadata Header
    if (document.getElementById('metaDocName')) document.getElementById('metaDocName').innerText = report.metadata.document_name;
    if (document.getElementById('metaDocType')) document.getElementById('metaDocType').innerText = report.metadata.document_type;
    if (document.getElementById('metaUploadTime')) document.getElementById('metaUploadTime').innerText = report.metadata.upload_time;
    if (document.getElementById('metaWordCount')) document.getElementById('metaWordCount').innerText = `${report.metadata.word_count} words`;
    if (document.getElementById('metaReadingTime')) document.getElementById('metaReadingTime').innerText = `~${report.metadata.reading_time_minutes} min read`;
    if (document.getElementById('metaReportId')) document.getElementById('metaReportId').innerText = report.report_id;

    // 1.5 Executive 30-Second Glance Summary (3 Pillars)
    if (document.getElementById('execWhatHappened')) document.getElementById('execWhatHappened').innerText = report.summary_insight.what_happened;
    if (document.getElementById('execAuthorFeels')) document.getElementById('execAuthorFeels').innerText = `${report.emotion_analysis.primary_emotion} — Hidden: ${report.emotion_analysis.hidden_emotion}`;
    if (document.getElementById('execAuthorWants')) document.getElementById('execAuthorWants').innerText = report.intent_analysis.reasoning;

    // 2. Emotion Analysis (Single Unified Detected Emotion)
    if (document.getElementById('primaryEmotionBadge')) document.getElementById('primaryEmotionBadge').innerText = report.emotion_analysis.primary_emotion;
    if (document.getElementById('hiddenEmotionBadge')) document.getElementById('hiddenEmotionBadge').innerText = report.emotion_analysis.hidden_emotion;
    if (document.getElementById('overallToneBadge')) document.getElementById('overallToneBadge').innerText = report.emotion_analysis.overall_tone;
    if (document.getElementById('emotionConfidenceVal')) document.getElementById('emotionConfidenceVal').innerText = `${report.emotion_analysis.confidence}% Confidence`;
    if (document.getElementById('emotionReasoningText')) document.getElementById('emotionReasoningText').innerText = report.emotion_analysis.emotion_reasoning;

    // Progress Bars
    if (document.getElementById('posBar')) {
      document.getElementById('posBar').style.width = `${report.emotion_analysis.positive_percentage}%`;
      document.getElementById('posVal').innerText = `${report.emotion_analysis.positive_percentage}%`;
      
      document.getElementById('neuBar').style.width = `${report.emotion_analysis.neutral_percentage}%`;
      document.getElementById('neuVal').innerText = `${report.emotion_analysis.neutral_percentage}%`;
      
      document.getElementById('negBar').style.width = `${report.emotion_analysis.negative_percentage}%`;
      document.getElementById('negVal').innerText = `${report.emotion_analysis.negative_percentage}%`;
    }

    // Evidence Sentences
    const evidenceList = document.getElementById('emotionEvidenceList');
    if (evidenceList) {
      evidenceList.innerHTML = report.emotion_analysis.supporting_evidence.map(s => 
        `<li class="list-group-item bg-transparent text-body-primary border-secondary-subtle py-2">
          <i class="fas fa-quote-left me-2 text-primary opacity-75"></i>${s}
         </li>`
      ).join('');
    }

    // Render Emotion Doughnut Chart
    if (window.ChartRenderer && report.emotion_analysis.distribution) {
      window.ChartRenderer.renderEmotionChart('emotionChartCanvas', report.emotion_analysis.distribution);
    }

    // 3. Intent Analysis
    if (document.getElementById('primaryIntentBadge')) document.getElementById('primaryIntentBadge').innerText = report.intent_analysis.primary_intent;
    if (document.getElementById('intentConfidenceVal')) document.getElementById('intentConfidenceVal').innerText = `${report.intent_analysis.confidence}% Confidence`;
    if (document.getElementById('intentReasoningText')) document.getElementById('intentReasoningText').innerText = report.intent_analysis.reasoning;

    const intentSentences = document.getElementById('intentSupportingSentences');
    if (intentSentences) {
      intentSentences.innerHTML = (report.intent_analysis.supporting_sentences || []).map(s => 
        `<li class="list-group-item bg-transparent text-body-primary border-secondary-subtle py-2">
          <i class="fas fa-bullseye me-2 text-warning opacity-75"></i>${s}
         </li>`
      ).join('');
    }

    // 3.5 Unique Feature: De-escalation Response Script
    if (report.deescalation_response) {
      if (document.getElementById('deescalationTargetIntent')) document.getElementById('deescalationTargetIntent').innerText = report.deescalation_response.target_intent;
      if (document.getElementById('deescalationPrimaryEmotion')) document.getElementById('deescalationPrimaryEmotion').innerText = report.deescalation_response.primary_emotion_addressed;
      if (document.getElementById('deescalationHiddenEmotion')) document.getElementById('deescalationHiddenEmotion').innerText = report.deescalation_response.hidden_emotion_addressed;
      if (document.getElementById('deescalationSubject')) document.getElementById('deescalationSubject').value = report.deescalation_response.subject;
      if (document.getElementById('deescalationScript')) document.getElementById('deescalationScript').value = report.deescalation_response.response_script;

      const btnCopy = document.getElementById('btnCopyDeescalation');
      if (btnCopy) {
        btnCopy.onclick = () => {
          const scriptText = report.deescalation_response.response_script;
          navigator.clipboard.writeText(scriptText).then(() => {
            btnCopy.innerHTML = '<i class="fas fa-check me-1"></i> Copied!';
            setTimeout(() => {
              btnCopy.innerHTML = '<i class="fas fa-copy me-1"></i> Copy Response Script';
            }, 2000);
          });
        };
      }
    }

    // 4. Summary Insight Box (Concise Synthesized Human Reader Synthesis)
    if (document.getElementById('insightWhatHappened')) document.getElementById('insightWhatHappened').innerText = report.summary_insight.what_happened;
    if (document.getElementById('insightWhyFeels')) document.getElementById('insightWhyFeels').innerText = report.summary_insight.why_feels_this_way;
    if (document.getElementById('insightWhatWants')) document.getElementById('insightWhatWants').innerText = report.summary_insight.what_user_wants;
    if (document.getElementById('insightProblem')) document.getElementById('insightProblem').innerText = report.summary_insight.problem_identified;
    if (document.getElementById('insightNarrative')) document.getElementById('insightNarrative').innerText = report.summary_insight.narrative_paragraph;

    // 5. Multi-Summary
    if (document.getElementById('shortSummaryText')) document.getElementById('shortSummaryText').innerText = report.summaries.short_summary;
    if (document.getElementById('mediumSummaryText')) document.getElementById('mediumSummaryText').innerText = report.summaries.medium_summary;
    if (document.getElementById('detailedSummaryText')) document.getElementById('detailedSummaryText').innerText = report.summaries.detailed_summary;
    if (document.getElementById('bulletSummaryList')) document.getElementById('bulletSummaryList').innerHTML = report.summaries.bullet_summary.map(b => `<li>${b}</li>`).join('');

    // 6. Main & Sub topics
    if (document.getElementById('mainTopicBadge')) document.getElementById('mainTopicBadge').innerText = report.main_topic;
    if (document.getElementById('subTopicsContainer')) {
      document.getElementById('subTopicsContainer').innerHTML = report.sub_topics.map(t => 
        `<span class="pill-badge pill-blue">${t}</span>`
      ).join('');
    }

    // 7. Important Sentences (Top 10)
    if (document.getElementById('importantSentencesList')) {
      document.getElementById('importantSentencesList').innerHTML = report.important_sentences.map((s, idx) => 
        `<li class="list-group-item bg-transparent text-body-primary border-secondary-subtle py-2">
          <span class="badge bg-secondary me-2">${idx + 1}</span> ${s}
         </li>`
      ).join('');
    }

    // 8. Emotional Timeline
    if (window.ChartRenderer && report.emotional_timeline) {
      window.ChartRenderer.renderTimelineChart('timelineChartCanvas', report.emotional_timeline);
    }
    
    if (document.getElementById('timelineNodesContainer')) {
      document.getElementById('timelineNodesContainer').innerHTML = report.emotional_timeline.map(node => 
        `<div class="phase-card ms-2 mb-3">
          <div class="d-flex justify-content-between align-items-center mb-2 flex-wrap gap-1">
            <span class="fw-bold brand-gradient fs-6"><i class="fas fa-layer-group me-1"></i> ${node.phase} Phase <small class="text-secondary opacity-75">(${node.phase_label || ''})</small></span>
            <div>
              <span class="pill-badge pill-pink"><i class="fas fa-heart-pulse text-danger"></i> ${node.dominant_emotion}</span>
              <span class="pill-badge pill-blue"><i class="fas fa-bullseye text-warning"></i> ${node.phase_intent || 'General Context'}</span>
            </div>
          </div>
          <div class="p-2.5 rounded-3 mb-2" style="background: rgba(255,255,255,0.03); border: 1px solid var(--glass-border)">
            <p class="text-body-primary small mb-1"><strong><i class="fas fa-wave-square text-danger me-1"></i> Emotion Flow:</strong> ${node.emotion_flow_description || ''}</p>
            <p class="text-body-primary small mb-0"><strong><i class="fas fa-compass text-info me-1"></i> Intent Flow:</strong> ${node.intent_flow_description || ''}</p>
          </div>
          <p class="text-secondary small fst-italic mb-0"><i class="fas fa-quote-left me-1 text-primary opacity-50"></i>"${node.excerpt}"</p>
         </div>`
      ).join('');
    }

    // 9. Confidence Scores
    if (document.getElementById('confScoreEmotion')) document.getElementById('confScoreEmotion').innerText = `${report.confidence_scores.emotion_detection}%`;
    if (document.getElementById('confScoreIntent')) document.getElementById('confScoreIntent').innerText = `${report.confidence_scores.intent_detection}%`;
    if (document.getElementById('confScoreSummary')) document.getElementById('confScoreSummary').innerText = `${report.confidence_scores.summary}%`;
    if (document.getElementById('confScoreFlow')) document.getElementById('confScoreFlow').innerText = `${report.confidence_scores.contextual_flow || 92}%`;
    if (document.getElementById('confScoreOverall')) document.getElementById('confScoreOverall').innerText = `${report.confidence_scores.overall_prediction}%`;

    // 12. Final Conclusion Assessment
    if (document.getElementById('finalConclusionText')) {
      document.getElementById('finalConclusionText').innerText = report.final_conclusion;
    }

    // Attach export listeners
    if (document.getElementById('btnExportJson')) document.getElementById('btnExportJson').onclick = () => window.location.href = `/api/history/export/${report.report_id}?format=json`;
    if (document.getElementById('btnExportCsv')) document.getElementById('btnExportCsv').onclick = () => window.location.href = `/api/history/export/${report.report_id}?format=csv`;
    if (document.getElementById('btnExportPdf')) document.getElementById('btnExportPdf').onclick = () => window.location.href = `/api/history/export/${report.report_id}?format=pdf`;

    // Smooth scroll to report output
    container.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  static _renderEntityCategory(elementId, items, pillClass, iconClass) {
    const el = document.getElementById(elementId);
    if (!el) return;
    if (!items || items.length === 0) {
      el.innerHTML = '<span class="text-muted small">None detected</span>';
      return;
    }
    el.innerHTML = items.map(item => 
      `<span class="pill-badge ${pillClass}">
        <i class="fas ${iconClass} opacity-75"></i> ${item}
       </span>`
    ).join('');
  }
}

window.ReportRenderer = ReportRenderer;
