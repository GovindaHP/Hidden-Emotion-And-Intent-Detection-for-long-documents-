class HistoryManager {
  static async loadHistory(search = '', emotion = '', intent = '') {
    const tableBody = document.getElementById('historyTableBody');
    if (!tableBody) return;

    try {
      let url = `/api/history/?limit=50`;
      if (search) url += `&search=${encodeURIComponent(search)}`;
      if (emotion) url += `&emotion=${encodeURIComponent(emotion)}`;
      if (intent) url += `&intent=${encodeURIComponent(intent)}`;

      const headers = window.AuthManager ? window.AuthManager.getAuthHeaders() : {};
      const response = await fetch(url, { headers });
      if (!response.ok) return;

      const items = await response.json();

      if (items.length === 0) {
        tableBody.innerHTML = `<tr><td colspan="7" class="text-center text-muted py-4">No analysis history found matching query.</td></tr>`;
        return;
      }

      tableBody.innerHTML = items.map(item => {
        const reportData = item.report_data || {};
        const meta = reportData.metadata || {};
        const dateStr = item.created_at ? new Date(item.created_at).toLocaleString() : 'Recent';

        return `
          <tr>
            <td><code class="text-info">${item.report_id}</code></td>
            <td class="fw-semibold text-light">${item.filename || 'Untitled'}</td>
            <td><span class="badge bg-dark border border-secondary">${meta.document_type || 'General'}</span></td>
            <td><span class="pill-badge pill-purple">${item.primary_emotion || 'N/A'}</span></td>
            <td><span class="pill-badge pill-blue">${item.primary_intent || 'N/A'}</span></td>
            <td><span class="badge bg-success-subtle text-success fw-bold">${item.confidence || 90}%</span></td>
            <td class="text-end">
              <button class="btn btn-sm btn-glass me-1" onclick="HistoryManager.viewReport('${item.report_id}')">
                <i class="fas fa-eye me-1"></i> View Report
              </button>
              <a href="/api/history/export/${item.report_id}?format=pdf" class="btn btn-sm btn-outline-danger me-1" title="Download PDF">
                <i class="fas fa-file-pdf"></i>
              </a>
              <a href="/api/history/export/${item.report_id}?format=json" class="btn btn-sm btn-outline-info" title="Download JSON">
                <i class="fas fa-code"></i>
              </a>
            </td>
          </tr>
        `;
      }).join('');
    } catch (err) {
      console.error("Error loading history:", err);
    }
  }

  static async viewReport(reportId) {
    try {
      const headers = window.AuthManager ? window.AuthManager.getAuthHeaders() : {};
      const response = await fetch(`/api/predictions/${reportId}`, { headers });
      if (!response.ok) return;

      const report = await response.json();
      
      // Switch tab to workspace
      const tabWorkspace = document.getElementById('nav-workspace-tab');
      if (tabWorkspace) {
        const tab = new bootstrap.Tab(tabWorkspace);
        tab.show();
      }

      window.ReportRenderer.render(report);
    } catch (err) {
      console.error("Error loading report details:", err);
    }
  }
}

window.HistoryManager = HistoryManager;
