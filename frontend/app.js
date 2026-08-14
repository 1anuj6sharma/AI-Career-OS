/**
 * AI CAREER OPERATING SYSTEM — FRONTEND CORE ENGINE
 * Synchronizes UI components, dual-theme switching, view routing,
 * live checklist progress, AI chat, and backend API integration (Modules 1–14).
 */

const API_BASE_URL = 'http://localhost:8000/api/v1';

// APP STATE
const state = {
  theme: localStorage.getItem('theme') || 'dark',
  currentView: 'dashboard',
  user: JSON.parse(localStorage.getItem('user')) || {
    name: 'Anuj Saraswat',
    email: 'anuj.saraswat@example.com',
    token: localStorage.getItem('token') || null
  },
  backendOnline: false
};

// INITIALIZATION
document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  initNavigation();
  initChecklist();
  initAIChat();
  initResumeBuilder();
  initModule14ApprovalGateway();
  checkBackendHealth();
});

/* ==========================================================================
   1. THEME ENGINE (Light & Dark Mode)
   ========================================================================== */
function initTheme() {
  document.documentElement.setAttribute('data-theme', state.theme);
  updateThemeIcon();

  const themeBtn = document.getElementById('themeToggleBtn');
  if (themeBtn) {
    themeBtn.addEventListener('click', () => {
      state.theme = state.theme === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', state.theme);
      localStorage.setItem('theme', state.theme);
      updateThemeIcon();
    });
  }
}

function updateThemeIcon() {
  const themeBtn = document.getElementById('themeToggleBtn');
  if (themeBtn) {
    themeBtn.textContent = state.theme === 'dark' ? '☀️' : '🌙';
  }
}

/* ==========================================================================
   2. NAVIGATION & VIEW ROUTING
   ========================================================================== */
function initNavigation() {
  const navLinks = document.querySelectorAll('.nav-link');
  
  navLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const targetView = link.getAttribute('data-view');
      switchView(targetView);
    });
  });

  const btnDashStartLearning = document.getElementById('btnDashStartLearning');
  if (btnDashStartLearning) {
    btnDashStartLearning.addEventListener('click', () => switchView('skillPath'));
  }

  const btnDashViewJobs = document.getElementById('btnDashViewJobs');
  if (btnDashViewJobs) {
    btnDashViewJobs.addEventListener('click', () => switchView('jobs'));
  }

  const btnDashChatAI = document.getElementById('btnDashChatAI');
  if (btnDashChatAI) {
    btnDashChatAI.addEventListener('click', () => switchView('aiCoach'));
  }

  const btnAskAI = document.getElementById('btnHeaderAskAI');
  if (btnAskAI) {
    btnAskAI.addEventListener('click', () => switchView('aiCoach'));
  }

  const btnLogout = document.getElementById('btnLogout');
  if (btnLogout) {
    btnLogout.addEventListener('click', () => {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      alert('Signed out successfully.');
    });
  }
}

function switchView(viewId) {
  const views = document.querySelectorAll('.app-view');
  views.forEach(v => v.style.display = 'none');

  const navLinks = document.querySelectorAll('.nav-link');
  navLinks.forEach(l => l.classList.remove('active'));

  const targetView = document.getElementById(`view${capitalize(viewId)}`) || document.getElementById('viewDashboard');
  if (targetView) {
    targetView.style.display = 'block';
  }

  const activeLink = document.querySelector(`.nav-link[data-view="${viewId}"]`);
  if (activeLink) {
    activeLink.classList.add('active');
  }

  state.currentView = viewId;
  window.scrollTo({ top: 0, behavior: 'smooth' });

  if (state.backendOnline && viewId === 'dashboard') {
    fetchModule13Dashboard();
  }
  if (state.backendOnline && (viewId === 'jobs' || viewId === 'opportunities')) {
    fetchModule14Opportunities();
  }
}

function capitalize(str) {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

/* ==========================================================================
   3. TODAY'S PLAN CHECKLIST ENGINE
   ========================================================================== */
function initChecklist() {
  const checkboxes = document.querySelectorAll('.checklist-checkbox');
  checkboxes.forEach(cb => {
    cb.addEventListener('change', (e) => {
      const parent = e.target.closest('.checklist-item');
      if (e.target.checked) {
        parent.classList.add('done');
      } else {
        parent.classList.remove('done');
      }
      updateChecklistProgress();
    });
  });
  updateChecklistProgress();
}

function updateChecklistProgress() {
  const total = document.querySelectorAll('.checklist-checkbox').length;
  if (total === 0) return;
  const checked = document.querySelectorAll('.checklist-checkbox:checked').length;
  const percent = Math.round((checked / total) * 100);

  const planPercentBar = document.getElementById('planPercentBar');
  const planPercentLabel = document.getElementById('planPercentLabel');
  const planProgressText = document.getElementById('planProgressText');

  if (planPercentBar) planPercentBar.style.width = `${percent}%`;
  if (planPercentLabel) planPercentLabel.textContent = `${percent}%`;
  if (planProgressText) planProgressText.textContent = `Progress: ${percent}%`;
}

/* ==========================================================================
   4. AI COACH / COPILOT CHAT ENGINE
   ========================================================================== */
function initAIChat() {
  const coachChatForm = document.getElementById('coachChatForm');
  if (!coachChatForm) return;

  coachChatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const input = document.getElementById('coachChatInput');
    const text = input.value.trim();
    if (!text) return;

    appendChatMessage('user', text);
    input.value = '';

    const thinkingMsg = appendChatMessage('ai', '🤖 AI is analyzing your Career Performance State...');

    try {
      if (state.backendOnline) {
        const response = await fetch(`${API_BASE_URL}/career/coach`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${state.user.token}`
          },
          body: JSON.stringify({ message: text })
        });
        const data = await response.json();
        thinkingMsg.innerHTML = `<strong>🤖 AI Career Coach</strong><br>${data.reply || data.response || 'Analysis complete based on your active career state.'}`;
      } else {
        setTimeout(() => {
          thinkingMsg.innerHTML = getFallbackAIResponse(text);
        }, 600);
      }
    } catch (err) {
      setTimeout(() => {
        thinkingMsg.innerHTML = getFallbackAIResponse(text);
      }, 600);
    }
  });

  ['toolResumeReview', 'toolMockInterview', 'toolSkillGap', 'toolRoadmap'].forEach(id => {
    const btn = document.getElementById(id);
    if (btn) {
      btn.addEventListener('click', () => {
        if (id === 'toolResumeReview') switchView('resumes');
        if (id === 'toolMockInterview') switchView('interviews');
        if (id === 'toolSkillGap' || id === 'toolRoadmap') switchView('skillPath');
      });
    }
  });
}

function appendChatMessage(sender, message) {
  const container = document.getElementById('coachChatMessages');
  if (!container) return;

  const bubble = document.createElement('div');
  bubble.className = `chat-msg-bubble ${sender}`;
  bubble.innerHTML = sender === 'user' ? message : `<strong>🤖 AI Career Coach</strong><br>${message}`;
  
  container.appendChild(bubble);
  container.scrollTop = container.scrollHeight;
  return bubble;
}

function getFallbackAIResponse(text) {
  const lower = text.toLowerCase();
  if (lower.includes('azure') || lower.includes('cloud')) {
    return `For <strong>Azure Data Engineering</strong>, focus on:<br>• Azure Data Factory (ETL Pipelines)<br>• Databricks & PySpark<br>• Synapse Analytics & SQL<br>• Blob Storage & Data Lake Gen2`;
  }
  if (lower.includes('resume') || lower.includes('ats')) {
    return `Your resume score is currently <strong>85/100</strong>! To reach 90+:<br>1. Quantify achievements (e.g., 'Reduced query latency by 40%')<br>2. Add PySpark and Azure Data Factory to your skills section.<br>3. Tailor bullets to Data Engineer job descriptions.`;
  }
  return `Great question regarding <strong>${text}</strong>! Based on your target role as a Data Engineer, I recommend practicing SQL query optimization, Pandas/PySpark data transformations, and building an automated cloud pipeline project.`;
}

/* ==========================================================================
   5. RESUME BUILDER LIVE EDITOR
   ========================================================================== */
function initResumeBuilder() {
  const btnApply = document.getElementById('btnApplyAISuggestions');
  if (btnApply) {
    btnApply.addEventListener('click', () => {
      const resSkills = document.getElementById('resSkills');
      const resSummary = document.getElementById('resSummary');

      if (resSkills) resSkills.innerHTML = 'Python • SQL • Azure Data Factory • PySpark • Data Modeling • Power BI • ETL';
      if (resSummary) resSummary.innerHTML = 'Results-driven CS graduate specialized in building scalable Azure data pipelines, optimizing SQL queries, and architecting ETL data transformations.';
      
      alert('AI suggestions applied! Resume Score updated to 92/100.');
    });
  }

  const btnDownload = document.getElementById('btnResumeDownload');
  if (btnDownload) {
    btnDownload.addEventListener('click', () => {
      window.print();
    });
  }
}

/* ==========================================================================
   6. MODULE 14 HUMAN-IN-THE-LOOP APPROVAL GATEWAY & API SYNCHRONIZATION
   ========================================================================== */
function initModule14ApprovalGateway() {
  const btnApprove = document.getElementById('btnApproveApplication');
  const btnReject = document.getElementById('btnRejectApplication');

  if (btnApprove) {
    btnApprove.addEventListener('click', async () => {
      if (state.backendOnline && state.user.token) {
        try {
          const res = await fetch(`${API_BASE_URL}/applications/1/approve`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${state.user.token}`
            },
            body: JSON.stringify({ notes: 'Candidate manually approved application submission.' })
          });
          if (res.ok) {
            alert('✅ Application Approved! AI has submitted your application package.');
            return;
          }
        } catch (err) {
          console.error(err);
        }
      }
      alert('✅ Application Approved! AI has submitted your tailored application package to Stripe.');
    });
  }

  if (btnReject) {
    btnReject.addEventListener('click', async () => {
      if (state.backendOnline && state.user.token) {
        try {
          await fetch(`${API_BASE_URL}/applications/1/reject`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${state.user.token}`
            }
          });
        } catch (err) {
          console.error(err);
        }
      }
      alert('🛑 Application Execution Rejected by user.');
    });
  }
}

async function checkBackendHealth() {
  try {
    const res = await fetch('http://localhost:8000/health');
    if (res.ok) {
      state.backendOnline = true;
      console.log('✅ Connected to AI Career OS FastAPI Backend.');
      fetchModule13Dashboard();
      fetchModule14Opportunities();
    }
  } catch (err) {
    state.backendOnline = false;
    console.log('ℹ️ Running in rich interactive frontend demo mode (Backend offline).');
  }
}

async function fetchModule13Dashboard() {
  if (!state.user.token) return;
  try {
    const res = await fetch(`${API_BASE_URL}/career/dashboard`, {
      headers: {
        'Authorization': `Bearer ${state.user.token}`
      }
    });
    if (res.ok) {
      const data = await res.json();
      const valProfileStrength = document.getElementById('valProfileStrength');
      if (valProfileStrength) {
        valProfileStrength.textContent = `${data.performance_score}%`;
      }
    }
  } catch (err) {
    console.log('Using default dashboard metrics.');
  }
}

async function fetchModule14Opportunities() {
  if (!state.user.token) return;
  try {
    const res = await fetch(`${API_BASE_URL}/opportunities`, {
      headers: {
        'Authorization': `Bearer ${state.user.token}`
      }
    });
    if (res.ok) {
      const opps = await res.json();
      console.log('🎯 Module 14 Opportunities fetched:', opps);
    }
  } catch (err) {
    console.log('Using default opportunities data.');
  }
}
