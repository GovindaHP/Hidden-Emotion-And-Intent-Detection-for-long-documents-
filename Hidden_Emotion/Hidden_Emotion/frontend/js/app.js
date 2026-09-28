document.addEventListener('DOMContentLoaded', () => {
  initThemeToggle();
  initDropzone();
  initFormSubmissions();
  initNavigation();
  initAuthUI();
});

let selectedFile = null;

function initDropzone() {
  const dropzone = document.getElementById('fileDropzone');
  const fileInput = document.getElementById('fileInput');

  if (!dropzone || !fileInput) return;

  dropzone.addEventListener('click', () => fileInput.click());

  dropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropzone.classList.add('dragover');
  });

  dropzone.addEventListener('dragleave', () => dropzone.classList.remove('dragover'));

  dropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropzone.classList.remove('dragover');
    if (e.dataTransfer.files.length > 0) {
      handleFileSelected(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
      handleFileSelected(e.target.files[0]);
    }
  });
}

function handleFileSelected(file) {
  selectedFile = file;
  const fileNameDisplay = document.getElementById('selectedFileName');
  if (fileNameDisplay) {
    fileNameDisplay.innerHTML = `<i class="fas fa-file-alt me-2 text-primary"></i> <strong>Selected:</strong> ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
    fileNameDisplay.classList.remove('d-none');
  }
}

function initFormSubmissions() {
  const btnProcessFile = document.getElementById('btnProcessFile');
  const btnProcessText = document.getElementById('btnProcessText');

  if (btnProcessFile) {
    btnProcessFile.addEventListener('click', async () => {
      if (!selectedFile) {
        alert("Please select a document file (PDF, DOCX, or TXT) first.");
        return;
      }

      const docType = document.getElementById('fileDocTypeSelect').value;
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('doc_type', docType);

      await runAnalysisPipeline('/api/documents/upload', formData, true);
    });
  }

  if (btnProcessText) {
    btnProcessText.addEventListener('click', async () => {
      const text = document.getElementById('rawTextInput').value.trim();
      const title = document.getElementById('textTitleInput').value.trim() || 'Pasted Document Input';
      const docType = document.getElementById('textDocTypeSelect').value;

      if (!text || text.length < 10) {
        alert("Please enter a document text of at least 10 characters.");
        return;
      }

      const payload = { title, text, doc_type: docType };
      await runAnalysisPipeline('/api/documents/analyze-text', payload, false);
    });
  }
}

async function runAnalysisPipeline(endpoint, bodyData, isFormData) {
  const stepperModal = new bootstrap.Modal(document.getElementById('processingModal'));
  stepperModal.show();
  resetStepper();

  try {
    // Animate stepper stages
    await animateStep('stepExtract', 300);
    await animateStep('stepClean', 300);
    await animateStep('stepChunk', 400);

    const headers = window.AuthManager ? window.AuthManager.getAuthHeaders() : {};
    if (!isFormData) {
      headers['Content-Type'] = 'application/json';
    }

    const fetchOptions = {
      method: 'POST',
      headers: headers,
      body: isFormData ? bodyData : JSON.stringify(bodyData)
    };

    const response = await fetch(endpoint, fetchOptions);

    await animateStep('stepEmbed', 300);
    await animateStep('stepPredict', 400);
    await animateStep('stepReport', 200);

    if (!response.ok) {
      let errMsg = 'Analysis request failed';
      try {
        const err = await response.json();
        errMsg = err.detail || errMsg;
      } catch (e) {
        const txt = await response.text();
        errMsg = txt || `Server Error (${response.status})`;
      }
      throw new Error(errMsg);
    }

    const report = await response.json();

    setTimeout(() => {
      stepperModal.hide();
      window.ReportRenderer.render(report);
    }, 400);

  } catch (err) {
    alert(`Analysis Error: ${err.message}`);
    stepperModal.hide();
  }
}

function resetStepper() {
  const steps = ['stepExtract', 'stepClean', 'stepChunk', 'stepEmbed', 'stepPredict', 'stepReport'];
  steps.forEach(s => {
    const el = document.getElementById(s);
    if (el) {
      el.classList.remove('completed', 'active');
    }
  });
}

function animateStep(stepId, delayMs) {
  return new Promise(resolve => {
    const el = document.getElementById(stepId);
    if (el) {
      el.classList.add('active');
      setTimeout(() => {
        el.classList.remove('active');
        el.classList.add('completed');
        resolve();
      }, delayMs);
    } else {
      resolve();
    }
  });
}

function initNavigation() {
  const historyTabBtn = document.getElementById('nav-history-tab');
  if (historyTabBtn) {
    historyTabBtn.addEventListener('shown.bs.tab', () => {
      window.HistoryManager.loadHistory();
    });
  }

  const analyticsTabBtn = document.getElementById('nav-analytics-tab');
  if (analyticsTabBtn) {
    analyticsTabBtn.addEventListener('shown.bs.tab', async () => {
      const headers = window.AuthManager ? window.AuthManager.getAuthHeaders() : {};
      const res = await fetch('/api/analytics/dashboard', { headers });
      if (res.ok) {
        const data = await res.json();
        document.getElementById('analyticsTotalDocs').innerText = data.total_documents;
        document.getElementById('analyticsAvgConf').innerText = `${data.avg_confidence}%`;
        window.ChartRenderer.renderAnalyticsCharts(data);
      }
    });
  }

  const adminTabBtn = document.getElementById('nav-admin-tab');
  if (adminTabBtn) {
    adminTabBtn.addEventListener('shown.bs.tab', () => {
      window.AdminManager.loadAdminDashboard();
    });
  }

  // History search filter listeners
  const searchInput = document.getElementById('historySearchInput');
  const emotionFilter = document.getElementById('historyEmotionFilter');
  const intentFilter = document.getElementById('historyIntentFilter');

  const triggerHistorySearch = () => {
    window.HistoryManager.loadHistory(searchInput.value, emotionFilter.value, intentFilter.value);
  };

  if (searchInput) searchInput.addEventListener('input', triggerHistorySearch);
  if (emotionFilter) emotionFilter.addEventListener('change', triggerHistorySearch);
  if (intentFilter) intentFilter.addEventListener('change', triggerHistorySearch);
}

function initAuthUI() {
  const user = window.AuthManager ? window.AuthManager.getUser() : null;
  const userBtn = document.getElementById('userProfileBtn');
  if (userBtn) {
    if (user) {
      userBtn.innerHTML = `<i class="fas fa-user-circle me-1"></i> ${user.username} <span class="badge bg-primary ms-1">${user.role}</span>`;
      userBtn.onclick = () => {
        if (confirm("Log out of session?")) {
          window.AuthManager.logout();
        }
      };
    } else {
      userBtn.innerHTML = `<i class="fas fa-sign-in-alt me-1"></i> Login / Register`;
      userBtn.onclick = () => {
        const modal = new bootstrap.Modal(document.getElementById('authModal'));
        modal.show();
      };
    }
  }

  const btnLoginSubmit = document.getElementById('btnLoginSubmit');
  if (btnLoginSubmit) {
    btnLoginSubmit.addEventListener('click', async () => {
      const email = document.getElementById('authEmail').value;
      const pwd = document.getElementById('authPassword').value;
      try {
        await window.AuthManager.login(email, pwd);
        window.location.reload();
      } catch (err) {
        alert(err.message);
      }
    });
  }

  const btnRegisterSubmit = document.getElementById('btnRegisterSubmit');
  if (btnRegisterSubmit) {
    btnRegisterSubmit.addEventListener('click', async () => {
      const username = document.getElementById('authRegUsername').value;
      const email = document.getElementById('authRegEmail').value;
      const pwd = document.getElementById('authRegPassword').value;
      const role = document.getElementById('authRegRole').value;
      try {
        await window.AuthManager.register(username, email, pwd, role);
        window.location.reload();
      } catch (err) {
        alert(err.message);
      }
    });
  }
}

function initThemeToggle() {
  const toggleBtn = document.getElementById('themeToggleBtn');
  const toggleIcon = document.getElementById('themeToggleIcon');
  const toggleLabel = document.getElementById('themeToggleLabel');

  const savedTheme = localStorage.getItem('theme') || 'dark';
  applyTheme(savedTheme);

  if (toggleBtn) {
    toggleBtn.addEventListener('click', () => {
      const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
      const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
      applyTheme(newTheme);
    });
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    document.body.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);

    if (toggleIcon && toggleLabel) {
      if (theme === 'light') {
        toggleIcon.className = 'fas fa-moon text-primary me-1';
        toggleLabel.innerText = 'Dark Mode';
      } else {
        toggleIcon.className = 'fas fa-sun text-warning me-1';
        toggleLabel.innerText = 'Light Mode';
      }
    }
  }
}
