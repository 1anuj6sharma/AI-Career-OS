/**
 * AI CAREER OPERATING SYSTEM — AUTONOMOUS MULTI-AGENT ECOSYSTEM
 * 
 * Architecture:
 * 1. Tri-Stream Opportunity Ingestion:
 *    • JOBS: Full-Time, Remote, Internships, Government
 *    • LEARNING: Skills, Roadmaps, Projects, Certifications
 *    • BUSINESS: Freelance Gigs, Client Acquisition, Invoicing & Proposals
 * 2. User Profile: Dynamic Evidence Graph (Skills + Projects + Resume + Preferences)
 * 3. AI Decision Engine: Closed-Loop "What Should I Do Next?" Flywheel
 */

const API_BASE_URL = 'http://localhost:8000/api/v1';

// Global application state
const appState = {
  theme: localStorage.getItem('theme') || 'dark',
  currentView: 'dashboard',
  currentUser: null,
  userData: null,
  backendOnline: false,
  selectedJobIndex: 0,
  activeJobCategory: 'all',
  selectedGigId: null
};

// 1. JOBS STREAM CATALOG (Full-Time, Remote, Internships, Government)
const JOB_CATALOG = [
  {
    id: 1,
    category: 'Full-Time',
    title: 'Senior Backend Engineer',
    company: 'Stripe',
    location: 'Remote',
    type: 'Full Time',
    salary: '$150k - $190k',
    requiredSkills: ['Python', 'FastAPI', 'PostgreSQL', 'Docker', 'Redis'],
    description: 'Lead backend architecture for high-throughput distributed payment settlement pipelines.'
  },
  {
    id: 2,
    category: 'Remote',
    title: 'AI / LLM Systems Engineer',
    company: 'Anthropic',
    location: 'Remote / Global',
    type: 'Full Time',
    salary: '$165k - $220k',
    requiredSkills: ['Python', 'PyTorch', 'LLMs', 'FastAPI', 'PGVector'],
    description: 'Scale LLM inference pipelines, multi-agent frameworks, and vector search evaluation systems.'
  },
  {
    id: 3,
    category: 'Internship',
    title: 'Cloud Data Engineering Intern',
    company: 'Snowflake',
    location: 'Bengaluru / Hybrid',
    type: 'Internship',
    salary: '$4,000 / mo',
    requiredSkills: ['Python', 'SQL', 'PySpark', 'ETL', 'Azure'],
    description: 'Build real-time ETL pipelines, data structures, and analytics data models alongside senior mentors.'
  },
  {
    id: 4,
    category: 'Government',
    title: 'Senior Technical Officer (Gov AI Initiative)',
    company: 'National Cyber & Informatics Centre',
    location: 'New Delhi / Onsite',
    type: 'Government Contract',
    salary: '₹18L - ₹24L / yr',
    requiredSkills: ['Python', 'PostgreSQL', 'Docker', 'Linux', 'Security'],
    description: 'Architect secure public cloud infrastructure and national digital governance data microservices.'
  }
];

// 2. BUSINESS & FREELANCE GIGS CATALOG (High-Ticket Contracts)
const FREELANCE_GIGS_DEFAULT = [
  {
    id: 101,
    client: 'SaaS Metrics Inc.',
    title: 'FastAPI Microservice & Caching Architecture',
    budget: '$4,500 fixed',
    timeline: '3 Weeks',
    requiredTech: ['Python', 'FastAPI', 'Redis', 'Docker'],
    description: 'Build a high-performance backend microservice with Redis caching for real-time analytics aggregation.'
  },
  {
    id: 102,
    client: 'Healthcare AI Labs',
    title: 'HIPAA-Compliant Vector Search & LLM Engine',
    budget: '$8,000 fixed',
    timeline: '4 Weeks',
    requiredTech: ['Python', 'PGVector', 'LLMs', 'FastAPI', 'PostgreSQL'],
    description: 'Implement secure document indexing, semantic search, and RAG question-answering pipelines.'
  },
  {
    id: 103,
    client: 'E-Commerce Global',
    title: 'Real-Time PySpark Data Processing Pipeline',
    budget: '$90 / hr (Est. 60 hrs)',
    timeline: 'Ongoing Retainer',
    requiredTech: ['PySpark', 'SQL', 'Python', 'ETL'],
    description: 'Optimize daily streaming ETL transformations and reporting tables on cloud data lake.'
  }
];

// INITIALIZATION
document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  initAuth();
  initNavigation();
  initFormsAndModals();
  initAIChat();
  initResumeBuilder();
  initFlywheelListeners();
  checkBackendHealth();
});

/* ==========================================================================
   1. THEME ENGINE
   ========================================================================== */
function initTheme() {
  document.documentElement.setAttribute('data-theme', appState.theme);
  updateThemeIcon();

  const themeBtn = document.getElementById('themeToggleBtn');
  if (themeBtn) {
    themeBtn.addEventListener('click', () => {
      appState.theme = appState.theme === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', appState.theme);
      localStorage.setItem('theme', appState.theme);
      updateThemeIcon();
    });
  }
}

function updateThemeIcon() {
  const themeBtn = document.getElementById('themeToggleBtn');
  if (themeBtn) {
    themeBtn.textContent = appState.theme === 'dark' ? '☀️' : '🌙';
  }
}

/* ==========================================================================
   2. AUTHENTICATION & PER-USER CLEAN SLATE STATE
   ========================================================================== */
function initAuth() {
  const authSection = document.getElementById('authSection');
  const tabLogin = document.getElementById('tabLogin');
  const tabRegister = document.getElementById('tabRegister');
  const groupName = document.getElementById('groupName');
  const authSubtitle = document.getElementById('authSubtitle');
  const btnAuthSubmit = document.getElementById('btnAuthSubmit');
  const authForm = document.getElementById('authForm');
  const authError = document.getElementById('authError');
  const btnLogout = document.getElementById('btnLogout');

  let isRegisterMode = false;

  tabLogin.addEventListener('click', (e) => {
    e.preventDefault();
    isRegisterMode = false;
    tabLogin.classList.add('active');
    tabLogin.style.background = 'var(--primary)';
    tabLogin.style.color = 'white';
    tabRegister.classList.remove('active');
    tabRegister.style.background = 'transparent';
    tabRegister.style.color = 'var(--text-muted)';
    groupName.style.display = 'none';
    authSubtitle.textContent = 'Sign in to your account';
    btnAuthSubmit.textContent = 'Sign In';
    authError.style.display = 'none';
  });

  tabRegister.addEventListener('click', (e) => {
    e.preventDefault();
    isRegisterMode = true;
    tabRegister.classList.add('active');
    tabRegister.style.background = 'var(--primary)';
    tabRegister.style.color = 'white';
    tabLogin.classList.remove('active');
    tabLogin.style.background = 'transparent';
    tabLogin.style.color = 'var(--text-muted)';
    groupName.style.display = 'block';
    authSubtitle.textContent = 'Create a new account (Starts with 0 data)';
    btnAuthSubmit.textContent = 'Create Account & Start';
    authError.style.display = 'none';
  });

  authForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    authError.style.display = 'none';

    const email = document.getElementById('authEmail').value.trim().toLowerCase();
    const password = document.getElementById('authPassword').value;
    const name = document.getElementById('authName').value.trim() || email.split('@')[0];

    if (!email || !password) return;

    btnAuthSubmit.disabled = true;
    btnAuthSubmit.textContent = isRegisterMode ? 'Creating Account...' : 'Signing In...';

    try {
      if (isRegisterMode) {
        let token = null;
        let userId = null;

        if (appState.backendOnline) {
          try {
            const nameParts = name.split(' ');
            const firstName = nameParts[0] || 'User';
            const lastName = nameParts.slice(1).join(' ') || 'Account';

            const regRes = await fetch(`${API_BASE_URL}/auth/register`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                first_name: firstName,
                last_name: lastName,
                email: email,
                password: password
              })
            });

            if (regRes.ok) {
              const loginRes = await fetch(`${API_BASE_URL}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
              });
              if (loginRes.ok) {
                const loginData = await loginRes.json();
                token = loginData.tokens?.access_token;
                userId = loginData.user?.id;
              }
            }
          } catch (backendErr) {
            console.warn('Backend register fallback to local store:', backendErr.message);
          }
        }

        const newUser = {
          id: userId || Date.now(),
          name: name,
          email: email,
          token: token || 'local-token-' + Date.now()
        };

        const initialData = getEmptyUserData(newUser);
        saveUserData(email, initialData);
        setCurrentUser(newUser);

        authSection.style.display = 'none';
        logActivity('Account created with clean slate.');
        showToast(`Welcome, ${name}! Your AI Career Agent is ready.`);
      } else {
        let loggedInName = name;
        let token = null;

        if (appState.backendOnline) {
          try {
            const loginRes = await fetch(`${API_BASE_URL}/auth/login`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ email, password })
            });

            if (loginRes.ok) {
              const loginData = await loginRes.json();
              token = loginData.tokens?.access_token;
              if (loginData.user) {
                loggedInName = `${loginData.user.first_name || ''} ${loginData.user.last_name || ''}`.trim() || loggedInName;
              }
            }
          } catch (backendErr) {
            console.warn('Backend login fallback to local account:', backendErr.message);
          }
        }

        let existingData = loadUserData(email);
        if (!existingData) {
          existingData = getEmptyUserData({ name: loggedInName, email });
          saveUserData(email, existingData);
        } else if (existingData.profile?.name) {
          loggedInName = existingData.profile.name;
        }

        const user = {
          name: loggedInName,
          email: email,
          token: token || 'local-token-' + Date.now()
        };

        setCurrentUser(user);
        authSection.style.display = 'none';
        showToast(`Welcome back, ${loggedInName}!`);
      }
    } catch (err) {
      authError.textContent = err.message || 'Authentication failed.';
      authError.style.display = 'block';
    } finally {
      btnAuthSubmit.disabled = false;
      btnAuthSubmit.textContent = isRegisterMode ? 'Create Account & Start' : 'Sign In';
    }
  });

  btnLogout.addEventListener('click', () => {
    if (confirm('Are you sure you want to sign out?')) {
      signOut();
    }
  });

  const storedUser = localStorage.getItem('ai_career_current_user');
  if (storedUser) {
    try {
      const user = JSON.parse(storedUser);
      if (user && user.email) {
        setCurrentUser(user);
        authSection.style.display = 'none';
        return;
      }
    } catch (e) {
      localStorage.removeItem('ai_career_current_user');
    }
  }

  authSection.style.display = 'flex';
}

function getEmptyUserData(user) {
  return {
    profile: {
      name: user.name || 'User',
      email: user.email,
      targetRole: '',
      location: '',
      bio: ''
    },
    tasks: [],
    skills: [],
    applications: [],
    projects: [],
    contacts: [],
    freelanceGigs: [...FREELANCE_GIGS_DEFAULT],
    clientPipeline: [],
    decisionMemory: [],
    strategyVersion: 1.0,
    resume: {
      name: user.name || 'User',
      title: '',
      contact: `${user.email} • Location • LinkedIn`,
      summary: '',
      skills: '',
      experience: [],
      education: []
    },
    activities: []
  };
}

function loadUserData(email) {
  if (!email) return null;
  const raw = localStorage.getItem(`ai_career_data_${email}`);
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch (e) {
    return null;
  }
}

function saveUserData(email, data) {
  if (!email || !data) return;
  localStorage.setItem(`ai_career_data_${email}`, JSON.stringify(data));
}

function setCurrentUser(user) {
  appState.currentUser = user;
  localStorage.setItem('ai_career_current_user', JSON.stringify(user));
  
  let data = loadUserData(user.email);
  if (!data) {
    data = getEmptyUserData(user);
    saveUserData(user.email, data);
  }
  // Ensure default structures exist
  if (!data.freelanceGigs) data.freelanceGigs = [...FREELANCE_GIGS_DEFAULT];
  if (!data.clientPipeline) data.clientPipeline = [];
  if (!data.decisionMemory) data.decisionMemory = [];
  if (!data.strategyVersion) data.strategyVersion = 1.0;

  appState.userData = data;
  renderAll();
}

function signOut() {
  appState.currentUser = null;
  appState.userData = null;
  localStorage.removeItem('ai_career_current_user');
  
  const authSection = document.getElementById('authSection');
  if (authSection) authSection.style.display = 'flex';
  showToast('Signed out successfully.');
}

function persistState() {
  if (appState.currentUser && appState.userData) {
    saveUserData(appState.currentUser.email, appState.userData);
  }
}

function logActivity(text) {
  if (!appState.userData) return;
  if (!appState.userData.activities) appState.userData.activities = [];
  
  appState.userData.activities.unshift({
    id: Date.now(),
    text: text,
    time: 'Just now',
    timestamp: new Date().toISOString()
  });

  if (appState.userData.activities.length > 25) {
    appState.userData.activities.pop();
  }

  persistState();
  renderActivities();
}

/* ==========================================================================
   3. GLOBAL RENDER ENGINE (DYNAMIC REACTIVITY)
   ========================================================================== */
function renderAll() {
  if (!appState.userData) return;

  renderUserProfile();
  renderDecisionEngineHero();
  renderDashboardMetrics();
  renderChecklist();
  renderSkills();
  renderActivities();
  renderResume();
  renderJobs();
  renderLearningStream();
  renderBusinessStream();
  renderKanban();
  renderProjects();
  renderNetwork();
  renderAnalytics();
  renderSettings();
}

function renderUserProfile() {
  const user = appState.currentUser;
  const data = appState.userData;
  if (!user) return;

  const displayName = data.profile?.name || user.name || 'User';
  const initials = getInitials(displayName);

  const avatarInitials = document.getElementById('avatarInitials');
  const userNameDisplay = document.getElementById('userNameDisplay');
  const greetingName = document.getElementById('greetingName');
  const userRoleBadge = document.getElementById('userRoleBadge');

  if (avatarInitials) avatarInitials.textContent = initials;
  if (userNameDisplay) userNameDisplay.textContent = displayName;
  if (greetingName) greetingName.textContent = displayName.split(' ')[0] || displayName;
  if (userRoleBadge) {
    userRoleBadge.textContent = data.profile?.targetRole || 'Active Account';
  }
}

function getInitials(name) {
  if (!name) return '?';
  const parts = name.trim().split(' ').filter(Boolean);
  if (parts.length === 1) return parts[0].substring(0, 2).toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}

/* ==========================================================================
   4. AUTONOMOUS "WHAT SHOULD I DO NEXT?" CLOSED-LOOP DECISION ENGINE
   ========================================================================== */
function calculateNextBestAction() {
  const data = appState.userData;
  if (!data) return null;

  const skills = (data.skills || []).map(s => s.name.toLowerCase());
  const applications = data.applications || [];
  const clientPipeline = data.clientPipeline || [];
  const strategyVer = (data.strategyVersion || 1.0).toFixed(1);

  // Scenario 1: Clean slate / No skills
  if (skills.length === 0) {
    return {
      pillar: '📚 LEARNING STREAM',
      pillarClass: 'learning',
      strategyVersion: `Strategy: Adaptive v${strategyVer}`,
      title: 'Initialize Technical Evidence & Add 3 Core Skills',
      score: 'Score: 96/100',
      reason: 'Your verified evidence graph is empty. Adding at least 3 skills unlocks tailored AI matching across Jobs and High-Ticket Client Gigs.',
      impact: 'MAXIMUM (Foundational)',
      actionText: '⚡ Add Core Skills (Dashboard)',
      targetView: 'dashboard',
      actionPayload: { type: 'focus_skills' }
    };
  }

  // Scenario 2: Skills exist, but resume summary empty
  if (!data.resume?.summary || data.resume.summary.length < 35) {
    return {
      pillar: '📄 RESUME INTELLIGENCE',
      pillarClass: 'resume',
      strategyVersion: `Strategy: Adaptive v${strategyVer}`,
      title: 'Craft ATS-Optimized Resume Summary',
      score: 'Score: 92/100',
      reason: `You have added ${skills.length} skills! Next high-ROI action: build your professional summary to reach 85+ ATS score.`,
      impact: 'HIGH (Application Readiness)',
      actionText: '⚡ Build Resume with AI',
      targetView: 'resumes',
      actionPayload: { type: 'apply_resume_template' }
    };
  }

  // Scenario 3: High match freelance contract available
  const matchingGig = (data.freelanceGigs || []).find(gig => 
    gig.requiredTech.some(t => skills.includes(t.toLowerCase())) &&
    !clientPipeline.some(cp => cp.gigId === gig.id)
  );

  if (matchingGig) {
    return {
      pillar: '🚀 BUSINESS & FREELANCE',
      pillarClass: 'business',
      strategyVersion: `Strategy: Adaptive v${strategyVer}`,
      title: `Pitch ${matchingGig.client} (${matchingGig.budget})`,
      score: 'Score: 94.5/100',
      reason: `High match contract detected! Your background in ${matchingGig.requiredTech.join(', ')} aligns with ${matchingGig.title}. Generate a grounded AI proposal now.`,
      impact: 'VERY HIGH (Immediate Revenue)',
      actionText: '⚡ Generate Grounded Proposal',
      targetView: 'business',
      actionPayload: { type: 'generate_proposal', gigId: matchingGig.id }
    };
  }

  // Scenario 4: Target role application discovery
  const matchingJob = JOB_CATALOG.find(job => 
    job.requiredSkills.some(r => skills.includes(r.toLowerCase())) &&
    !applications.some(a => a.company.toLowerCase() === job.company.toLowerCase())
  );

  if (matchingJob) {
    return {
      pillar: '💼 JOBS STREAM',
      pillarClass: 'jobs',
      strategyVersion: `Strategy: Adaptive v${strategyVer}`,
      title: `Apply to ${matchingJob.title} at ${matchingJob.company}`,
      score: 'Score: 91/100',
      reason: `High alignment with ${matchingJob.company} (${matchingJob.salary}). Your profile meets key skill criteria.`,
      impact: 'HIGH (Career Advancement)',
      actionText: `⚡ Apply to ${matchingJob.company}`,
      targetView: 'jobs',
      actionPayload: { type: 'apply_job', job: matchingJob }
    };
  }

  // Scenario 5: Interview practice
  return {
    pillar: '🎤 INTERVIEW INTELLIGENCE',
    pillarClass: 'interview',
    strategyVersion: `Strategy: Adaptive v${strategyVer}`,
    title: 'Complete Technical System Design Mock Interview',
    score: 'Score: 89/100',
    reason: 'Refine system design STAR responses to maximize interview conversion rates.',
    impact: 'MEDIUM-HIGH (Conversion)',
    actionText: '⚡ Start AI Mock Interview',
    targetView: 'interviews',
    actionPayload: { type: 'start_interview' }
  };
}

function renderDecisionEngineHero() {
  const nba = calculateNextBestAction();
  if (!nba) return;

  const nbaPillarBadge = document.getElementById('nbaPillarBadge');
  const nbaStrategyVersion = document.getElementById('nbaStrategyVersion');
  const nbaTitle = document.getElementById('nbaTitle');
  const nbaScoreBadge = document.getElementById('nbaScoreBadge');
  const nbaReason = document.getElementById('nbaReason');
  const nbaImpactText = document.getElementById('nbaImpactText');
  const btnExecuteNBA = document.getElementById('btnExecuteNextBestAction');

  if (nbaPillarBadge) nbaPillarBadge.textContent = nba.pillar;
  if (nbaStrategyVersion) nbaStrategyVersion.textContent = nba.strategyVersion;
  if (nbaTitle) nbaTitle.textContent = nba.title;
  if (nbaScoreBadge) nbaScoreBadge.textContent = nba.score;
  if (nbaReason) nbaReason.textContent = nba.reason;
  if (nbaImpactText) nbaImpactText.innerHTML = `Impact: <strong style="color: var(--success);">${nba.impact}</strong>`;

  if (btnExecuteNBA) {
    btnExecuteNBA.textContent = nba.actionText;
    btnExecuteNBA.onclick = () => {
      executeActionPayload(nba);
    };
  }
}

function executeActionPayload(nba) {
  if (!nba) return;
  switchView(nba.targetView);

  const payload = nba.actionPayload;
  if (!payload) return;

  if (payload.type === 'generate_proposal' && payload.gigId) {
    openProposalModal(payload.gigId);
  } else if (payload.type === 'apply_job' && payload.job) {
    addApplication(payload.job.company, payload.job.title, 'Applied');
    showToast(`Applied to ${payload.job.title} at ${payload.job.company}!`);
  } else if (payload.type === 'apply_resume_template') {
    const btn = document.getElementById('btnApplyAISuggestions');
    if (btn) btn.click();
  }
}

function initFlywheelListeners() {
  document.querySelectorAll('.btn-flywheel-outcome').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const outcome = e.target.dataset.outcome;
      trackDecisionOutcome(outcome);
    });
  });
}

function trackDecisionOutcome(outcome) {
  const data = appState.userData;
  if (!data) return;

  const currentNba = calculateNextBestAction();
  if (!currentNba) return;

  if (!data.decisionMemory) data.decisionMemory = [];
  data.strategyVersion = (data.strategyVersion || 1.0) + 0.1;

  const entry = {
    id: Date.now(),
    title: currentNba.title,
    pillar: currentNba.pillar,
    outcome: outcome,
    timestamp: new Date().toISOString()
  };

  data.decisionMemory.unshift(entry);
  persistState();

  if (outcome === 'completed') {
    logActivity(`Closed-Loop: Completed action "${currentNba.title}". Strategy adapted.`);
    showToast('✅ Outcome recorded! Closed-loop adapted to next best action.');
  } else if (outcome === 'interview') {
    logActivity(`Closed-Loop Signal: Interview / Client response on "${currentNba.title}".`);
    showToast('💬 Signal recorded! Recalibrating matching weights.');
  } else {
    logActivity(`Closed-Loop: Postponed "${currentNba.title}". Strategy re-ranked.`);
    showToast('⏭️ Skipped. Recalculating alternative high-ROI action.');
  }

  renderAll();
}

function renderDashboardMetrics() {
  const data = appState.userData;
  if (!data) return;

  const profileStrength = calculateProfileStrength();
  const valProfileStrength = document.getElementById('valProfileStrength');
  const trendProfileStrength = document.getElementById('trendProfileStrength');
  if (valProfileStrength) valProfileStrength.textContent = `${profileStrength}%`;
  if (trendProfileStrength) {
    trendProfileStrength.textContent = profileStrength === 0 ? 'Clean Slate' : (profileStrength >= 70 ? '🟢 Strong' : '🟡 In Progress');
  }

  const valApplications = document.getElementById('valApplications');
  if (valApplications) valApplications.textContent = (data.applications || []).length;

  const valSkills = document.getElementById('valSkills');
  if (valSkills) valSkills.textContent = (data.skills || []).length;

  // Freelance pipeline value
  const valFreelancePipeline = document.getElementById('valFreelancePipeline');
  const pitchedCount = (data.clientPipeline || []).length;
  if (valFreelancePipeline) {
    valFreelancePipeline.textContent = pitchedCount > 0 ? `$${pitchedCount * 4500}` : '$0';
  }

  // Decisions executed
  const valDecisionsExecuted = document.getElementById('valDecisionsExecuted');
  if (valDecisionsExecuted) valDecisionsExecuted.textContent = (data.decisionMemory || []).length;
}

function calculateProfileStrength() {
  const data = appState.userData;
  if (!data) return 0;

  let score = 0;
  if (data.profile?.name && data.profile.name !== 'User') score += 15;
  if (data.profile?.targetRole) score += 15;
  if (data.profile?.location) score += 10;
  if ((data.skills || []).length > 0) score += Math.min(25, data.skills.length * 8);
  if (data.resume?.summary && data.resume.summary.length > 20) score += 15;
  if ((data.projects || []).length > 0) score += 10;
  if ((data.applications || []).length > 0 || (data.clientPipeline || []).length > 0) score += 10;

  return Math.min(100, Math.round(score));
}

/* ==========================================================================
   5. CHECKLIST ENGINE
   ========================================================================== */
function renderChecklist() {
  const data = appState.userData;
  const container = document.getElementById('checklistTasks');
  if (!container || !data) return;

  const tasks = data.tasks || [];

  if (tasks.length === 0) {
    container.innerHTML = `
      <div class="empty-state" style="padding: 1.25rem 1rem;">
        <div class="empty-state-icon" style="font-size: 1.5rem;">📋</div>
        <div class="empty-state-text">No daily tasks scheduled. Add your first goal below!</div>
      </div>
    `;
  } else {
    container.innerHTML = tasks.map(task => `
      <div class="checklist-item ${task.done ? 'done' : ''}" data-id="${task.id}">
        <div class="checklist-left">
          <input type="checkbox" class="checklist-checkbox" ${task.done ? 'checked' : ''} data-id="${task.id}">
          <span class="checklist-title">${escapeHtml(task.title)}</span>
        </div>
        <div style="display: flex; align-items: center; gap: 0.5rem;">
          <span class="checklist-time">${escapeHtml(task.time || '30m')}</span>
          <button class="btn-delete btn-delete-task" data-id="${task.id}" title="Delete Task">✕</button>
        </div>
      </div>
    `).join('');
  }

  container.querySelectorAll('.checklist-checkbox').forEach(cb => {
    cb.addEventListener('change', (e) => {
      const taskId = Number(e.target.dataset.id);
      const task = (appState.userData.tasks || []).find(t => t.id === taskId);
      if (task) {
        task.done = e.target.checked;
        persistState();
        renderChecklist();
        if (task.done) logActivity(`Completed task: "${task.title}"`);
      }
    });
  });

  container.querySelectorAll('.btn-delete-task').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const taskId = Number(e.target.dataset.id);
      appState.userData.tasks = (appState.userData.tasks || []).filter(t => t.id !== taskId);
      persistState();
      renderChecklist();
    });
  });

  updateChecklistProgress();
}

function updateChecklistProgress() {
  const tasks = appState.userData?.tasks || [];
  const total = tasks.length;
  const completed = tasks.filter(t => t.done).length;
  const percent = total === 0 ? 0 : Math.round((completed / total) * 100);

  const planPercentBar = document.getElementById('planPercentBar');
  const planPercentLabel = document.getElementById('planPercentLabel');
  const planProgressText = document.getElementById('planProgressText');

  if (planPercentBar) planPercentBar.style.width = `${percent}%`;
  if (planPercentLabel) planPercentLabel.textContent = `${percent}%`;
  if (planProgressText) planProgressText.textContent = `Progress: ${percent}%`;
}

/* ==========================================================================
   6. SKILL PROGRESS ENGINE
   ========================================================================== */
function renderSkills() {
  const data = appState.userData;
  const container = document.getElementById('skillProgressList');
  const skillCountLabel = document.getElementById('skillCountLabel');
  if (!container || !data) return;

  const skills = data.skills || [];
  if (skillCountLabel) skillCountLabel.textContent = `${skills.length} Skill${skills.length === 1 ? '' : 's'}`;

  if (skills.length === 0) {
    container.innerHTML = `
      <div class="empty-state" style="padding: 1.25rem 1rem;">
        <div class="empty-state-icon" style="font-size: 1.5rem;">🎓</div>
        <div class="empty-state-text">No skills in evidence graph. Add your core programming stack!</div>
      </div>
    `;
  } else {
    container.innerHTML = skills.map(s => `
      <div class="skill-item-card" data-id="${s.id}">
        <div style="flex: 1; margin-right: 1rem;">
          <div class="progress-header" style="margin-bottom: 0.25rem;">
            <span style="font-weight: 600;">${escapeHtml(s.name)}</span>
            <span style="color: var(--primary); font-weight: 700;">${s.level}%</span>
          </div>
          <div class="progress-track" style="height: 6px;">
            <div class="progress-fill" style="width: ${s.level}%;"></div>
          </div>
        </div>
        <button class="btn-delete btn-delete-skill" data-id="${s.id}" title="Remove Skill">✕</button>
      </div>
    `).join('');
  }

  container.querySelectorAll('.btn-delete-skill').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const skillId = Number(e.target.dataset.id);
      const skill = (appState.userData.skills || []).find(s => s.id === skillId);
      appState.userData.skills = (appState.userData.skills || []).filter(s => s.id !== skillId);
      persistState();
      renderSkills();
      renderDashboardMetrics();
      renderDecisionEngineHero();
      if (skill) logActivity(`Removed skill: ${skill.name}`);
    });
  });
}

/* ==========================================================================
   7. RECENT ACTIVITIES FEED
   ========================================================================== */
function renderActivities() {
  const container = document.getElementById('activityFeed');
  if (!container || !appState.userData) return;

  const activities = appState.userData.activities || [];
  if (activities.length === 0) {
    container.innerHTML = `
      <div class="empty-state" style="padding: 1.25rem 1rem;">
        <div class="empty-state-icon" style="font-size: 1.4rem;">⚡</div>
        <div class="empty-state-text">No activity recorded yet. Start exploring your 3 career streams!</div>
      </div>
    `;
    return;
  }

  container.innerHTML = activities.slice(0, 5).map(act => `
    <div style="display: flex; justify-content: space-between; padding-bottom: 0.5rem; border-bottom: 1px solid var(--border-color);">
      <span>${escapeHtml(act.text)}</span>
      <span style="color: var(--text-muted); font-size: 0.75rem;">${escapeHtml(act.time || 'Recently')}</span>
    </div>
  `).join('');
}

/* ==========================================================================
   8. PILLAR 1 — JOBS STREAM (Full-Time, Remote, Internships, Govt)
   ========================================================================== */
function renderJobs() {
  const container = document.getElementById('jobListCards');
  if (!container) return;

  const searchQuery = (document.getElementById('jobSearchQuery')?.value || '').toLowerCase();
  const userSkillNames = (appState.userData?.skills || []).map(s => s.name.toLowerCase());

  const filteredJobs = JOB_CATALOG.filter(job => {
    if (appState.activeJobCategory !== 'all' && job.category !== appState.activeJobCategory) return false;
    if (!searchQuery) return true;
    return job.title.toLowerCase().includes(searchQuery) ||
           job.company.toLowerCase().includes(searchQuery) ||
           job.requiredSkills.some(s => s.toLowerCase().includes(searchQuery));
  });

  if (filteredJobs.length === 0) {
    container.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">🔍</div>
        <div class="empty-state-text">No opportunities found in category "${appState.activeJobCategory}".</div>
      </div>
    `;
    return;
  }

  container.innerHTML = filteredJobs.map((job, idx) => {
    const matchedCount = job.requiredSkills.filter(req => userSkillNames.includes(req.toLowerCase())).length;
    const matchPct = Math.round((matchedCount / job.requiredSkills.length) * 100);

    return `
      <div class="job-card-selectable ${idx === appState.selectedJobIndex ? 'active' : ''}" data-index="${idx}">
        <div style="display: flex; justify-content: space-between;">
          <h5 style="font-size: 0.95rem; font-weight: 600;">${escapeHtml(job.title)}</h5>
          <span class="match-score-badge">${matchPct}% Match</span>
        </div>
        <p style="font-size: 0.8rem; color: var(--primary); margin-top: 0.2rem;">${escapeHtml(job.company)} • ${escapeHtml(job.location)}</p>
        <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: var(--text-muted); margin-top: 0.3rem;">
          <span>${escapeHtml(job.type)}</span>
          <span style="font-weight: 700; color: var(--success);">${escapeHtml(job.salary)}</span>
        </div>
      </div>
    `;
  }).join('');

  container.querySelectorAll('.job-card-selectable').forEach(card => {
    card.addEventListener('click', () => {
      appState.selectedJobIndex = Number(card.dataset.index);
      renderJobs();
      renderJobDetail(filteredJobs[appState.selectedJobIndex]);
    });
  });

  renderJobDetail(filteredJobs[appState.selectedJobIndex] || filteredJobs[0]);
}

function renderJobDetail(job) {
  if (!job) return;

  const userSkillNames = (appState.userData?.skills || []).map(s => s.name.toLowerCase());
  const matchedCount = job.requiredSkills.filter(req => userSkillNames.includes(req.toLowerCase())).length;
  const matchPct = Math.round((matchedCount / job.requiredSkills.length) * 100);

  const oppDetailTitle = document.getElementById('oppDetailTitle');
  const oppDetailCompany = document.getElementById('oppDetailCompany');
  const oppDetailScore = document.getElementById('oppDetailScore');
  const oppDetailPriority = document.getElementById('oppDetailPriority');
  const jobDetailBody = document.getElementById('jobDetailBody');
  const btnApplyJobAction = document.getElementById('btnApplyJobAction');
  const btnSaveJobAction = document.getElementById('btnSaveJobAction');

  if (oppDetailTitle) oppDetailTitle.textContent = job.title;
  if (oppDetailCompany) oppDetailCompany.textContent = `${job.company} — ${job.location} • [${job.category}]`;
  if (oppDetailScore) oppDetailScore.innerHTML = `${matchPct} <span style="font-size: 0.8rem; color: var(--text-muted);">/100</span>`;
  if (oppDetailPriority) {
    oppDetailPriority.textContent = matchPct >= 70 ? 'High Priority Match' : 'Potential Match';
    oppDetailPriority.style.color = matchPct >= 70 ? 'var(--success)' : 'var(--accent)';
  }

  if (jobDetailBody) {
    jobDetailBody.innerHTML = `
      <p style="font-size: 0.88rem; line-height: 1.5; margin-bottom: 1rem;">${escapeHtml(job.description)}</p>
      
      <div style="border-top: 1px solid var(--border-color); padding-top: 0.75rem; margin-top: 0.5rem;">
        <h4 style="font-size: 0.9rem; font-weight: 600; margin-bottom: 0.5rem;">Required Skills & Readiness</h4>
        <div style="font-size: 0.8rem; display: flex; flex-wrap: wrap; gap: 0.4rem; margin-bottom: 1rem;">
          ${job.requiredSkills.map(s => {
            const hasSkill = userSkillNames.includes(s.toLowerCase());
            return `<span style="background: ${hasSkill ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.12)'}; color: ${hasSkill ? 'var(--success)' : 'var(--danger)'}; padding: 3px 8px; border-radius: 4px; font-weight: 600;">
              ${hasSkill ? '✓' : '!'} ${escapeHtml(s)}
            </span>`;
          }).join('')}
        </div>
      </div>
    `;
  }

  if (btnApplyJobAction) {
    btnApplyJobAction.style.display = 'inline-flex';
    btnApplyJobAction.onclick = () => {
      addApplication(job.company, job.title, 'Applied');
      showToast(`Applied to ${job.title} at ${job.company}!`);
    };
  }

  if (btnSaveJobAction) {
    btnSaveJobAction.style.display = 'inline-flex';
    btnSaveJobAction.onclick = () => {
      addApplication(job.company, job.title, 'Saved');
      showToast(`Saved ${job.title} at ${job.company}!`);
    };
  }
}

/* ==========================================================================
   9. PILLAR 2 — LEARNING & ROADMAP STREAM
   ========================================================================== */
function renderLearningStream() {
  const timeline = document.getElementById('skillPathTimeline');
  const pathTitle = document.getElementById('skillPathTitle');
  const pathFocus = document.getElementById('skillPathCurrentFocus');
  const pathPct = document.getElementById('skillPathOverallPct');
  const certContainer = document.getElementById('certListContainer');

  if (!timeline || !appState.userData) return;

  const targetRole = appState.userData.profile?.targetRole || 'Software Engineering';
  const skills = appState.userData.skills || [];
  
  if (pathTitle) pathTitle.textContent = `${targetRole} Roadmap`;

  if (skills.length === 0) {
    timeline.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">📈</div>
        <div class="empty-state-text">Add your current technical skills to unlock interactive learning modules.</div>
      </div>
    `;
    if (pathFocus) pathFocus.textContent = 'Add skills to unlock roadmap';
    if (pathPct) pathPct.textContent = '0%';
  } else {
    const steps = [
      { title: 'Core Programming & Data Structures', desc: 'Master fundamentals, algorithm performance, and clean modular code.', completed: skills.length >= 1 },
      { title: 'Frameworks & Database Schema Design', desc: 'Build reliable APIs, caching layers, and database models.', completed: skills.length >= 3 },
      { title: 'System Design & Cloud Architecture', desc: 'Distributed messaging, microservices, and container deployments.', completed: skills.length >= 5 },
      { title: 'Autonomous Execution & Production Benchmarking', desc: 'Production observability, rate limiting, and AI workflow integration.', completed: skills.length >= 7 }
    ];

    timeline.innerHTML = steps.map((s, idx) => `
      <div class="roadmap-step ${s.completed ? 'completed' : ''}">
        <div class="roadmap-step-header">
          <h5 style="font-size: 0.95rem; font-weight: 600;">${idx + 1}. ${escapeHtml(s.title)}</h5>
          <span class="badge-status ${s.completed ? 'completed' : 'in-progress'}">${s.completed ? 'Completed' : 'In Progress'}</span>
        </div>
        <p style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.3rem;">${escapeHtml(s.desc)}</p>
      </div>
    `).join('');

    const completedSteps = steps.filter(s => s.completed).length;
    const pct = Math.round((completedSteps / steps.length) * 100);
    if (pathPct) pathPct.textContent = `${pct}%`;
    if (pathFocus) pathFocus.textContent = steps.find(s => !s.completed)?.title || 'All Core Modules Mastered!';
  }

  if (certContainer) {
    certContainer.innerHTML = `
      <div style="padding: 0.5rem; background: var(--bg-surface); border-radius: 6px; border: 1px solid var(--border-color); font-size: 0.8rem;">
        <strong>AWS Certified Solutions Architect</strong><br>
        <span style="color: var(--primary); font-size: 0.75rem;">Status: Recommended</span>
      </div>
      <div style="padding: 0.5rem; background: var(--bg-surface); border-radius: 6px; border: 1px solid var(--border-color); font-size: 0.8rem;">
        <strong>Databricks Certified Data Engineer</strong><br>
        <span style="color: var(--accent); font-size: 0.75rem;">Status: In Preparation</span>
      </div>
    `;
  }
}

/* ==========================================================================
   10. PILLAR 3 — BUSINESS & FREELANCING STREAM
   ========================================================================== */
function renderBusinessStream() {
  const container = document.getElementById('freelanceGigsContainer');
  const pipelineList = document.getElementById('clientPipelineList');
  const valGigsCount = document.getElementById('valBusinessGigsCount');
  const valPitchesCount = document.getElementById('valBusinessPitchesCount');
  const valCalculatedRate = document.getElementById('valCalculatedRate');

  if (!container || !appState.userData) return;

  const gigs = appState.userData.freelanceGigs || FREELANCE_GIGS_DEFAULT;
  const pipeline = appState.userData.clientPipeline || [];
  const userSkillNames = (appState.userData.skills || []).map(s => s.name.toLowerCase());

  if (valGigsCount) valGigsCount.textContent = gigs.length;
  if (valPitchesCount) valPitchesCount.textContent = pipeline.length;

  // Rate calculator based on skills count
  const baseRate = 60 + Math.min(60, userSkillNames.length * 10);
  if (valCalculatedRate) valCalculatedRate.textContent = `$${baseRate}/hr`;

  container.innerHTML = gigs.map(gig => {
    const matchedSkills = gig.requiredTech.filter(t => userSkillNames.includes(t.toLowerCase()));
    const isPitched = pipeline.some(p => p.gigId === gig.id);

    return `
      <div class="gig-card-item" data-id="${gig.id}">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
          <div>
            <h3 style="font-size: 1.05rem; font-weight: 700;">${escapeHtml(gig.title)}</h3>
            <span style="font-size: 0.82rem; color: var(--primary); font-weight: 600;">Client: ${escapeHtml(gig.client)}</span>
          </div>
          <span class="gig-budget-badge">${escapeHtml(gig.budget)}</span>
        </div>

        <p style="font-size: 0.85rem; color: var(--text-muted); line-height: 1.4;">${escapeHtml(gig.description)}</p>

        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.4rem; flex-wrap: wrap; gap: 0.5rem;">
          <div style="display: flex; flex-wrap: wrap; gap: 0.35rem;">
            ${gig.requiredTech.map(t => `<span class="pill" style="font-size: 0.72rem;">${escapeHtml(t)}</span>`).join('')}
          </div>
          <button class="btn btn-primary btn-sm btn-generate-gig-proposal" data-id="${gig.id}">
            ${isPitched ? '✓ Pitched (View Proposal)' : '⚡ Generate AI Proposal'}
          </button>
        </div>
      </div>
    `;
  }).join('');

  container.querySelectorAll('.btn-generate-gig-proposal').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const gigId = Number(e.target.dataset.id);
      openProposalModal(gigId);
    });
  });

  // Client deal pipeline
  if (pipelineList) {
    if (pipeline.length === 0) {
      pipelineList.innerHTML = `
        <div class="empty-state" style="padding: 1rem 0.5rem; font-size: 0.78rem;">
          No client pitches sent yet. Click "Generate AI Proposal" on any contract!
        </div>
      `;
    } else {
      pipelineList.innerHTML = pipeline.map(deal => `
        <div style="padding: 0.6rem; background: var(--bg-surface); border-radius: 6px; border: 1px solid var(--border-color); font-size: 0.82rem;">
          <div style="display: flex; justify-content: space-between; font-weight: 700;">
            <span>${escapeHtml(deal.client)}</span>
            <span style="color: var(--success);">${escapeHtml(deal.budget)}</span>
          </div>
          <div style="color: var(--text-muted); font-size: 0.75rem; margin-top: 0.2rem;">Stage: <strong>${escapeHtml(deal.stage)}</strong></div>
        </div>
      `).join('');
    }
  }
}

function openProposalModal(gigId) {
  const data = appState.userData;
  if (!data) return;

  const gig = (data.freelanceGigs || FREELANCE_GIGS_DEFAULT).find(g => g.id === gigId) || FREELANCE_GIGS_DEFAULT[0];
  appState.selectedGigId = gig.id;

  const candidateName = data.profile?.name || appState.currentUser?.name || 'Senior Consultant';
  const candidateEmail = data.profile?.email || appState.currentUser?.email || 'consultant@example.com';
  const skillsStr = (data.skills || []).map(s => s.name).join(', ') || gig.requiredTech.join(', ');
  const projectsEvidence = (data.projects || []).map(p => `• ${p.title}: ${p.desc}`).join('\n') || `• Scalable Architecture Project: Engineered high-concurrency services with ${skillsStr}.`;

  const proposalText = 
`Subject: Proposal for ${gig.title} — ${candidateName}

Dear Hiring Team at ${gig.client},

I am writing to submit my proposal for your project: "${gig.title}".

Why I Am uniquely Qualified:
With hands-on production expertise in ${skillsStr}, I specialize in delivering robust, high-performance architectures on budget.

Relevant Verified Portfolio Evidence:
${projectsEvidence}

Scope & Deliverables:
1. Technical Architecture & Schema Specification (Week 1)
2. Core Service Implementation & Integration with ${gig.requiredTech.join(', ')} (Week 2)
3. Automated Testing, Dockerization & Knowledge Handoff (Week 3)

Budget: ${gig.budget}
Timeline: ${gig.timeline}

I would welcome a 15-minute intro call to discuss your exact performance requirements and kick off execution.

Best regards,
${candidateName}
${candidateEmail}`;

  const proposalTextContent = document.getElementById('proposalTextContent');
  if (proposalTextContent) proposalTextContent.textContent = proposalText;

  const modal = document.getElementById('modalProposal');
  if (modal) modal.style.display = 'flex';
}

/* ==========================================================================
   11. KANBAN APPLICATIONS PIPELINE
   ========================================================================== */
function renderKanban() {
  const data = appState.userData;
  if (!data) return;

  const applications = data.applications || [];
  const stages = ['Saved', 'Applied', 'Interview', 'Offer'];

  stages.forEach(stage => {
    const listEl = document.getElementById(`kanban${stage}List`);
    const countEl = document.getElementById(`count${stage}`);
    const stageApps = applications.filter(a => a.status === stage);

    if (countEl) countEl.textContent = stageApps.length;

    if (listEl) {
      if (stageApps.length === 0) {
        listEl.innerHTML = `
          <div style="text-align: center; padding: 1rem 0.5rem; color: var(--text-muted); font-size: 0.78rem;">
            No applications in ${stage}
          </div>
        `;
      } else {
        listEl.innerHTML = stageApps.map(app => `
          <div class="kanban-item-card" data-id="${app.id}">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
              <strong style="font-size: 0.85rem;">${escapeHtml(app.role)}</strong>
              <button class="btn-delete btn-delete-app" data-id="${app.id}" title="Remove Application">✕</button>
            </div>
            <span style="font-size: 0.78rem; color: var(--primary); font-weight: 600;">${escapeHtml(app.company)}</span>
            
            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.4rem;">
              <select class="app-status-select" data-id="${app.id}" style="font-size: 0.72rem; padding: 2px 4px; width: auto;">
                ${stages.map(st => `<option value="${st}" ${st === app.status ? 'selected' : ''}>Move: ${st}</option>`).join('')}
              </select>
            </div>
          </div>
        `).join('');
      }
    }
  });

  document.querySelectorAll('.app-status-select').forEach(sel => {
    sel.addEventListener('change', (e) => {
      const appId = Number(e.target.dataset.id);
      const newStatus = e.target.value;
      const app = (appState.userData.applications || []).find(a => a.id === appId);
      if (app) {
        app.status = newStatus;
        persistState();
        renderKanban();
        renderDashboardMetrics();
        logActivity(`Moved application for ${app.role} at ${app.company} to ${newStatus}`);
      }
    });
  });

  document.querySelectorAll('.btn-delete-app').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const appId = Number(e.target.dataset.id);
      appState.userData.applications = (appState.userData.applications || []).filter(a => a.id !== appId);
      persistState();
      renderKanban();
      renderDashboardMetrics();
    });
  });
}

function addApplication(company, role, status = 'Applied') {
  if (!appState.userData) return;
  if (!appState.userData.applications) appState.userData.applications = [];

  const newApp = {
    id: Date.now(),
    company: company,
    role: role,
    status: status,
    dateAdded: new Date().toLocaleDateString()
  };

  appState.userData.applications.push(newApp);
  persistState();
  renderKanban();
  renderDashboardMetrics();
  renderDecisionEngineHero();
  logActivity(`Added application: ${role} at ${company} (${status})`);
}

/* ==========================================================================
   12. RESUME BUILDER, PROJECTS, CRM & ANALYTICS
   ========================================================================== */
function initResumeBuilder() {
  const resName = document.getElementById('resName');
  const resTitle = document.getElementById('resTitle');
  const resContact = document.getElementById('resContact');
  const resSummary = document.getElementById('resSummary');
  const resSkills = document.getElementById('resSkills');
  const btnApplySuggestions = document.getElementById('btnApplyAISuggestions');
  const btnResumeDownload = document.getElementById('btnResumeDownload');
  const btnResumePreview = document.getElementById('btnResumePreview');

  [resName, resTitle, resContact, resSummary, resSkills].forEach(field => {
    if (!field) return;
    field.addEventListener('input', () => {
      syncResumeDataFromDOM();
      calculateResumeScore();
    });
  });

  if (btnApplySuggestions) {
    btnApplySuggestions.addEventListener('click', () => {
      const data = appState.userData;
      if (!data) return;

      const targetRole = data.profile?.targetRole || 'Software Engineer';
      const userSkills = (data.skills || []).map(s => s.name).join(' • ') || 'Python • SQL • FastAPI • Docker • Git';

      if (resTitle) resTitle.textContent = targetRole;
      if (resSummary) resSummary.textContent = `Results-driven ${targetRole} with proven expertise in high-concurrency microservices, scalable system design, and continuous delivery. Strong engineering leadership and client execution.`;
      if (resSkills) resSkills.textContent = userSkills;

      syncResumeDataFromDOM();
      calculateResumeScore();
      renderDecisionEngineHero();
      showToast('AI Suggestions Applied to Resume!');
      logActivity('Applied AI suggestions to resume.');
    });
  }

  if (btnResumeDownload || btnResumePreview) {
    const handler = () => window.print();
    if (btnResumeDownload) btnResumeDownload.addEventListener('click', handler);
    if (btnResumePreview) btnResumePreview.addEventListener('click', handler);
  }
}

function renderResume() {
  const data = appState.userData;
  if (!data) return;

  const res = data.resume || {};
  const resName = document.getElementById('resName');
  const resTitle = document.getElementById('resTitle');
  const resContact = document.getElementById('resContact');
  const resSummary = document.getElementById('resSummary');
  const resSkills = document.getElementById('resSkills');

  const userName = data.profile?.name || appState.currentUser?.name || 'Your Full Name';
  const userEmail = data.profile?.email || appState.currentUser?.email || 'email@example.com';
  const userRole = data.profile?.targetRole || 'Target Engineering Role';

  if (resName && (!res.name || res.name === 'User')) res.name = userName;
  if (resName) resName.textContent = res.name || userName;
  if (resTitle) resTitle.textContent = res.title || userRole;
  if (resContact) resContact.textContent = res.contact || `${userEmail} • Location • LinkedIn`;
  if (resSummary) resSummary.textContent = res.summary || 'Click here to write your professional career summary and key technical strengths...';
  if (resSkills) {
    const skillList = (data.skills || []).map(s => s.name).join(' • ');
    resSkills.textContent = res.skills || (skillList || 'Add your skills separated by dots (e.g. Python • SQL • Docker)...');
  }

  calculateResumeScore();
}

function syncResumeDataFromDOM() {
  if (!appState.userData) return;
  if (!appState.userData.resume) appState.userData.resume = {};

  const resName = document.getElementById('resName');
  const resTitle = document.getElementById('resTitle');
  const resContact = document.getElementById('resContact');
  const resSummary = document.getElementById('resSummary');
  const resSkills = document.getElementById('resSkills');

  if (resName) appState.userData.resume.name = resName.textContent.trim();
  if (resTitle) appState.userData.resume.title = resTitle.textContent.trim();
  if (resContact) appState.userData.resume.contact = resContact.textContent.trim();
  if (resSummary) appState.userData.resume.summary = resSummary.textContent.trim();
  if (resSkills) appState.userData.resume.skills = resSkills.textContent.trim();

  persistState();
}

function calculateResumeScore() {
  const data = appState.userData;
  if (!data) return;

  const res = data.resume || {};
  let contentScore = 0;
  let formatScore = 0;
  let skillsScore = 0;
  let impactScore = 0;

  if (res.name && res.name !== 'Your Name' && res.name.length > 2) contentScore += 25;
  if (res.title && res.title !== 'Target Role / Title') contentScore += 25;
  if (res.summary && res.summary.length > 40) contentScore += 50;

  if (res.contact && res.contact.includes('@')) formatScore += 50;
  if (res.contact && (res.contact.includes('linkedin') || res.contact.includes('•'))) formatScore += 50;

  if (res.skills && res.skills.length > 10 && !res.skills.includes('Add your skills')) {
    const count = res.skills.split(/[•,;]/).filter(Boolean).length;
    skillsScore = Math.min(100, count * 20);
  }

  const summaryText = (res.summary || '').toLowerCase();
  const actionVerbs = ['built', 'architected', 'developed', 'optimized', 'led', 'engineered', 'designed', 'scaled', 'automated'];
  const matchedVerbs = actionVerbs.filter(v => summaryText.includes(v)).length;
  impactScore = Math.min(100, matchedVerbs * 25 + (summaryText.length > 80 ? 25 : 0));

  const totalScore = Math.round((contentScore * 0.3) + (formatScore * 0.2) + (skillsScore * 0.25) + (impactScore * 0.25));

  const resScoreVal = document.getElementById('resScoreVal');
  const resScoreStatus = document.getElementById('resScoreStatus');
  const scoreContentPct = document.getElementById('scoreContentPct');
  const scoreFormatPct = document.getElementById('scoreFormatPct');
  const scoreSkillsPct = document.getElementById('scoreSkillsPct');
  const scoreImpactPct = document.getElementById('scoreImpactPct');

  const barScoreContent = document.getElementById('barScoreContent');
  const barScoreFormat = document.getElementById('barScoreFormat');
  const barScoreSkills = document.getElementById('barScoreSkills');
  const barScoreImpact = document.getElementById('barScoreImpact');

  if (resScoreVal) resScoreVal.innerHTML = `${totalScore} <span style="font-size: 1rem; color: var(--text-muted);">/100</span>`;
  if (resScoreStatus) {
    if (totalScore === 0) resScoreStatus.textContent = 'Fill details to boost score';
    else if (totalScore < 60) resScoreStatus.textContent = '🟡 Needs improvement';
    else if (totalScore < 85) resScoreStatus.textContent = '🟢 Good ATS foundation';
    else resScoreStatus.textContent = '🌟 Excellent high-impact resume!';
  }

  if (scoreContentPct) scoreContentPct.textContent = `${contentScore}%`;
  if (scoreFormatPct) scoreFormatPct.textContent = `${formatScore}%`;
  if (scoreSkillsPct) scoreSkillsPct.textContent = `${skillsScore}%`;
  if (scoreImpactPct) scoreImpactPct.textContent = `${impactScore}%`;

  if (barScoreContent) barScoreContent.style.width = `${contentScore}%`;
  if (barScoreFormat) barScoreFormat.style.width = `${formatScore}%`;
  if (barScoreSkills) barScoreSkills.style.width = `${skillsScore}%`;
  if (barScoreImpact) barScoreImpact.style.width = `${impactScore}%`;
}

function renderProjects() {
  const container = document.getElementById('projectsListContainer');
  if (!container || !appState.userData) return;

  const projects = appState.userData.projects || [];

  if (projects.length === 0) {
    container.innerHTML = `
      <div class="empty-state" style="grid-column: 1 / -1; padding: 2.5rem 1rem;">
        <div class="empty-state-icon" style="font-size: 2rem;">📁</div>
        <h3 style="font-size: 1.1rem; margin-bottom: 0.3rem;">No Portfolio Evidence Added</h3>
        <p class="empty-state-text">Add your software engineering projects, open source repos, and architectural case studies.</p>
        <button class="btn btn-primary" id="btnEmptyAddProject">+ Add First Project</button>
      </div>
    `;
    const btn = document.getElementById('btnEmptyAddProject');
    if (btn) btn.onclick = () => openModal('modalAddProject');
    return;
  }

  container.innerHTML = projects.map(proj => `
    <div class="project-card-item">
      <div style="display: flex; justify-content: space-between; align-items: flex-start;">
        <h3 style="font-size: 1rem; font-weight: 700;">${escapeHtml(proj.title)}</h3>
        <button class="btn-delete btn-delete-project" data-id="${proj.id}" title="Remove Project">✕</button>
      </div>
      <p style="font-size: 0.85rem; color: var(--text-muted); line-height: 1.4;">${escapeHtml(proj.desc)}</p>
      
      ${proj.tech ? `
        <div style="display: flex; flex-wrap: wrap; gap: 0.35rem; margin-top: 0.4rem;">
          ${proj.tech.split(',').map(t => `<span class="pill" style="font-size: 0.72rem;">${escapeHtml(t.trim())}</span>`).join('')}
        </div>
      ` : ''}
    </div>
  `).join('');

  container.querySelectorAll('.btn-delete-project').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const projId = Number(e.target.dataset.id);
      appState.userData.projects = (appState.userData.projects || []).filter(p => p.id !== projId);
      persistState();
      renderProjects();
      renderDashboardMetrics();
    });
  });
}

function renderNetwork() {
  const container = document.getElementById('networkDirectoryContainer');
  if (!container || !appState.userData) return;

  const contacts = appState.userData.contacts || [];

  if (contacts.length === 0) {
    container.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">👥</div>
        <div class="empty-state-text">No network connections recorded yet. Add hiring managers, team alumni, or recruiters!</div>
      </div>
    `;
    return;
  }

  container.innerHTML = contacts.map(c => `
    <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.65rem; background: var(--bg-surface); border-radius: 6px; border: 1px solid var(--border-color);">
      <div>
        <strong>${escapeHtml(c.name)}</strong> — <span style="color: var(--primary);">${escapeHtml(c.role)} at ${escapeHtml(c.company)}</span><br>
        <span style="font-size: 0.75rem; color: var(--text-muted);">Tier: ${escapeHtml(c.tier || 'COLD')}</span>
      </div>
      <button class="btn-delete btn-delete-contact" data-id="${c.id}" title="Remove Contact">✕</button>
    </div>
  `).join('');

  container.querySelectorAll('.btn-delete-contact').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const contactId = Number(e.target.dataset.id);
      appState.userData.contacts = (appState.userData.contacts || []).filter(c => c.id !== contactId);
      persistState();
      renderNetwork();
    });
  });
}

function renderAnalytics() {
  const data = appState.userData;
  if (!data) return;

  const analyticsSkills = document.getElementById('analyticsSkills');
  const analyticsApps = document.getElementById('analyticsApps');
  const analyticsFreelance = document.getElementById('analyticsFreelance');
  const analyticsDecisions = document.getElementById('analyticsDecisions');

  if (analyticsSkills) analyticsSkills.textContent = (data.skills || []).length;
  if (analyticsApps) analyticsApps.textContent = (data.applications || []).length;
  if (analyticsFreelance) analyticsFreelance.textContent = (data.clientPipeline || []).length;
  if (analyticsDecisions) analyticsDecisions.textContent = (data.decisionMemory || []).length;
}

function renderSettings() {
  const data = appState.userData;
  if (!data) return;

  const settingName = document.getElementById('settingName');
  const settingEmail = document.getElementById('settingEmail');
  const settingTargetRole = document.getElementById('settingTargetRole');
  const settingTargetLocation = document.getElementById('settingTargetLocation');

  if (settingName) settingName.value = data.profile?.name || appState.currentUser?.name || '';
  if (settingEmail) settingEmail.value = data.profile?.email || appState.currentUser?.email || '';
  if (settingTargetRole) settingTargetRole.value = data.profile?.targetRole || '';
  if (settingTargetLocation) settingTargetLocation.value = data.profile?.location || '';
}

/* ==========================================================================
   13. FORM SUBMISSIONS & MODALS
   ========================================================================== */
function initFormsAndModals() {
  // Add Task
  const formAddTask = document.getElementById('formAddTask');
  if (formAddTask) {
    formAddTask.addEventListener('submit', (e) => {
      e.preventDefault();
      const titleInput = document.getElementById('inputNewTaskTitle');
      const timeInput = document.getElementById('inputNewTaskTime');
      const title = titleInput.value.trim();
      const time = timeInput.value.trim() || '30m';
      if (!title) return;

      if (!appState.userData.tasks) appState.userData.tasks = [];
      appState.userData.tasks.push({ id: Date.now(), title, time, done: false });

      titleInput.value = '';
      timeInput.value = '';
      persistState();
      renderChecklist();
      logActivity(`Added task: "${title}"`);
    });
  }

  // Add Skill
  const formAddSkill = document.getElementById('formAddSkill');
  if (formAddSkill) {
    formAddSkill.addEventListener('submit', (e) => {
      e.preventDefault();
      const nameInput = document.getElementById('inputNewSkillName');
      const levelSelect = document.getElementById('inputNewSkillLevel');
      const name = nameInput.value.trim();
      const level = Number(levelSelect.value) || 75;
      if (!name) return;

      if (!appState.userData.skills) appState.userData.skills = [];
      appState.userData.skills.push({ id: Date.now(), name, level });

      nameInput.value = '';
      persistState();
      renderSkills();
      renderDashboardMetrics();
      renderLearningStream();
      renderBusinessStream();
      renderDecisionEngineHero();
      showToast(`Added skill: ${name}`);
      logActivity(`Added skill to evidence: ${name}`);
    });
  }

  // Settings Save
  const formSettings = document.getElementById('formSettings');
  if (formSettings) {
    formSettings.addEventListener('submit', (e) => {
      e.preventDefault();
      const name = document.getElementById('settingName').value.trim();
      const targetRole = document.getElementById('settingTargetRole').value.trim();
      const location = document.getElementById('settingTargetLocation').value.trim();

      if (!appState.userData.profile) appState.userData.profile = {};
      appState.userData.profile.name = name;
      appState.userData.profile.targetRole = targetRole;
      appState.userData.profile.location = location;

      if (appState.currentUser) appState.currentUser.name = name;
      localStorage.setItem('ai_career_current_user', JSON.stringify(appState.currentUser));

      persistState();
      renderUserProfile();
      renderDashboardMetrics();
      renderDecisionEngineHero();
      showToast('Settings saved successfully!');
      logActivity('Updated profile preferences.');
    });
  }

  // Stream category tabs in Jobs view
  const jobTabs = document.querySelectorAll('#jobStreamCategoryTabs .stream-tab-btn');
  jobTabs.forEach(btn => {
    btn.addEventListener('click', (e) => {
      jobTabs.forEach(t => t.classList.remove('active'));
      e.currentTarget.classList.add('active');
      appState.activeJobCategory = e.currentTarget.dataset.cat;
      appState.selectedJobIndex = 0;
      renderJobs();
    });
  });

  const btnFilterJobs = document.getElementById('btnFilterJobs');
  const jobSearchQuery = document.getElementById('jobSearchQuery');
  if (btnFilterJobs) btnFilterJobs.addEventListener('click', renderJobs);
  if (jobSearchQuery) jobSearchQuery.addEventListener('input', renderJobs);

  // Proposal Quick Action
  const btnQuickGen = document.getElementById('btnQuickGenerateProposal');
  if (btnQuickGen) {
    btnQuickGen.addEventListener('click', () => {
      const gigId = appState.userData?.freelanceGigs?.[0]?.id || 101;
      openProposalModal(gigId);
    });
  }

  // Copy proposal button
  const btnCopyProposal = document.getElementById('btnCopyProposal');
  if (btnCopyProposal) {
    btnCopyProposal.addEventListener('click', () => {
      const text = document.getElementById('proposalTextContent')?.textContent;
      if (text) {
        navigator.clipboard.writeText(text);
        showToast('📋 Proposal copied to clipboard!');
      }
    });
  }

  // Mark proposal pitched button
  const btnMarkProposalSent = document.getElementById('btnMarkProposalSent');
  if (btnMarkProposalSent) {
    btnMarkProposalSent.addEventListener('click', () => {
      if (!appState.selectedGigId || !appState.userData) return;
      const gig = (appState.userData.freelanceGigs || FREELANCE_GIGS_DEFAULT).find(g => g.id === appState.selectedGigId);
      if (gig) {
        if (!appState.userData.clientPipeline) appState.userData.clientPipeline = [];
        if (!appState.userData.clientPipeline.some(p => p.gigId === gig.id)) {
          appState.userData.clientPipeline.push({
            gigId: gig.id,
            client: gig.client,
            title: gig.title,
            budget: gig.budget,
            stage: 'Pitched Proposal',
            date: new Date().toLocaleDateString()
          });
          persistState();
          renderBusinessStream();
          renderDashboardMetrics();
          renderDecisionEngineHero();
          logActivity(`Pitched proposal to ${gig.client} (${gig.budget})`);
          showToast(`✓ Proposal marked as Pitched to ${gig.client}!`);
        }
      }
      closeModal('modalProposal');
    });
  }

  // Modals setup
  setupModal('btnOpenAddAppModal', 'modalAddApp', 'btnCloseAddAppModal', 'formAddApplication', () => {
    const comp = document.getElementById('appCompany').value.trim();
    const role = document.getElementById('appRole').value.trim();
    const status = document.getElementById('appStatus').value;
    if (comp && role) addApplication(comp, role, status);
  });

  setupModal('btnOpenAddProjectModal', 'modalAddProject', 'btnCloseAddProjectModal', 'formAddProject', () => {
    const title = document.getElementById('projTitle').value.trim();
    const desc = document.getElementById('projDesc').value.trim();
    const tech = document.getElementById('projTech').value.trim();
    if (title && desc) {
      if (!appState.userData.projects) appState.userData.projects = [];
      appState.userData.projects.push({ id: Date.now(), title, desc, tech });
      persistState();
      renderProjects();
      renderDashboardMetrics();
      renderDecisionEngineHero();
      showToast(`Added project: ${title}`);
      logActivity(`Added portfolio project: "${title}"`);
    }
  });

  setupModal('btnOpenAddContactModal', 'modalAddContact', 'btnCloseAddContactModal', 'formAddContact', () => {
    const name = document.getElementById('contactName').value.trim();
    const comp = document.getElementById('contactCompany').value.trim();
    const role = document.getElementById('contactRole').value.trim();
    const tier = document.getElementById('contactTier').value;
    if (name && comp) {
      if (!appState.userData.contacts) appState.userData.contacts = [];
      appState.userData.contacts.push({ id: Date.now(), name, company: comp, role, tier });
      persistState();
      renderNetwork();
      showToast(`Added connection: ${name}`);
      logActivity(`Added network connection: ${name} (${comp})`);
    }
  });

  setupModal('btnOpenAddGigModal', 'modalAddGig', 'btnCloseAddGigModal', 'formAddGig', () => {
    const client = document.getElementById('gigClient').value.trim();
    const title = document.getElementById('gigTitle').value.trim();
    const budget = document.getElementById('gigBudget').value.trim();
    const techStr = document.getElementById('gigTech').value.trim();
    if (client && title) {
      const techArr = techStr ? techStr.split(',').map(t => t.trim()) : ['Python', 'Cloud'];
      if (!appState.userData.freelanceGigs) appState.userData.freelanceGigs = [];
      appState.userData.freelanceGigs.unshift({
        id: Date.now(),
        client,
        title,
        budget,
        timeline: 'Flexible',
        requiredTech: techArr,
        description: `Client consulting contract with ${client}.`
      });
      persistState();
      renderBusinessStream();
      renderDecisionEngineHero();
      showToast(`Posted client gig: ${title}`);
      logActivity(`Posted client gig: ${title} for ${client}`);
    }
  });

  const btnCloseProposal = document.getElementById('btnCloseProposalModal');
  if (btnCloseProposal) btnCloseProposal.onclick = () => closeModal('modalProposal');

  const btnStartMock = document.getElementById('btnStartMockInterview');
  if (btnStartMock) {
    btnStartMock.addEventListener('click', () => {
      switchView('aiCoach');
      const input = document.getElementById('coachChatInput');
      if (input) input.value = `Start a mock technical interview for ${appState.userData?.profile?.targetRole || 'Software Engineer'}`;
    });
  }
}

function setupModal(openBtnId, modalId, closeBtnId, formId, onSubmit) {
  const openBtn = document.getElementById(openBtnId);
  const modal = document.getElementById(modalId);
  const closeBtn = document.getElementById(closeBtnId);
  const form = document.getElementById(formId);

  if (openBtn && modal) openBtn.addEventListener('click', () => openModal(modalId));
  if (closeBtn && modal) closeBtn.addEventListener('click', () => closeModal(modalId));
  if (modal) {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) closeModal(modalId);
    });
  }
  if (form && modal) {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      onSubmit(e);
      form.reset();
      closeModal(modalId);
    });
  }
}

function openModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) modal.style.display = 'flex';
}

function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) modal.style.display = 'none';
}

/* ==========================================================================
   14. NAVIGATION & VIEW ROUTING
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

  const btnDashGoJobs = document.getElementById('btnDashGoJobs');
  if (btnDashGoJobs) btnDashGoJobs.addEventListener('click', () => switchView('jobs'));

  const btnDashGoLearning = document.getElementById('btnDashGoLearning');
  if (btnDashGoLearning) btnDashGoLearning.addEventListener('click', () => switchView('learning'));

  const btnDashGoBusiness = document.getElementById('btnDashGoBusiness');
  if (btnDashGoBusiness) btnDashGoBusiness.addEventListener('click', () => switchView('business'));

  const btnDashChatAI = document.getElementById('btnDashChatAI');
  if (btnDashChatAI) btnDashChatAI.addEventListener('click', () => switchView('aiCoach'));

  const btnAskAI = document.getElementById('btnHeaderAskAI');
  if (btnAskAI) btnAskAI.addEventListener('click', () => switchView('dashboard'));
}

function switchView(viewId) {
  const views = document.querySelectorAll('.app-view');
  views.forEach(v => v.style.display = 'none');

  const navLinks = document.querySelectorAll('.nav-link');
  navLinks.forEach(l => l.classList.remove('active'));

  const targetView = document.getElementById(`view${capitalize(viewId)}`) || document.getElementById('viewDashboard');
  if (targetView) targetView.style.display = 'block';

  const activeLink = document.querySelector(`.nav-link[data-view="${viewId}"]`);
  if (activeLink) activeLink.classList.add('active');

  appState.currentView = viewId;
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function capitalize(str) {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

/* ==========================================================================
   15. AI COACH & MASTER ORCHESTRATOR CHAT
   ========================================================================== */
function initAIChat() {
  const coachChatForm = document.getElementById('coachChatForm');
  const commandCenterForm = document.getElementById('commandCenterForm');

  if (coachChatForm) {
    coachChatForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const input = document.getElementById('coachChatInput');
      const text = input.value.trim();
      if (!text) return;

      appendChatMessage('user', text, 'coachChatMessages');
      input.value = '';

      const thinkingMsg = appendChatMessage('ai', '🤖 AI Career Agent analyzing tri-stream opportunities...', 'coachChatMessages');
      const reply = await getAIResponse(text, 'coach');
      thinkingMsg.innerHTML = `<strong>🤖 AI Career Agent</strong><br>${reply}`;
    });
  }

  if (commandCenterForm) {
    commandCenterForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const input = document.getElementById('commandCenterInput');
      const text = input.value.trim();
      if (!text) return;

      appendChatMessage('user', text, 'commandCenterMessages');
      input.value = '';

      const thinkingMsg = appendChatMessage('ai', '🧠 Master Orchestrator evaluating closed-loop graph...', 'commandCenterMessages');
      const reply = await getAIResponse(text, 'orchestrator');
      thinkingMsg.innerHTML = `<strong>🧠 Master Career Orchestrator</strong><br>${reply}`;
    });
  }
}

function appendChatMessage(sender, message, containerId) {
  const container = document.getElementById(containerId);
  if (!container) return;

  const bubble = document.createElement('div');
  bubble.className = `chat-msg-bubble ${sender}`;
  bubble.innerHTML = sender === 'user' ? escapeHtml(message) : message;
  
  container.appendChild(bubble);
  container.scrollTop = container.scrollHeight;
  return bubble;
}

async function getAIResponse(query, mode = 'coach') {
  const user = appState.currentUser;
  const data = appState.userData;
  const userName = data?.profile?.name || user?.name || 'there';
  const targetRole = data?.profile?.targetRole || 'Software Engineer';
  const skills = (data?.skills || []).map(s => s.name).join(', ') || 'No skills listed yet';

  if (appState.backendOnline && user?.token) {
    try {
      const endpoint = mode === 'orchestrator' 
        ? `${API_BASE_URL}/master-orchestrator/chat`
        : `${API_BASE_URL}/career/coach`;

      const res = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${user.token}`
        },
        body: JSON.stringify({ message: query })
      });

      if (res.ok) {
        const json = await res.json();
        return json.reply || json.response || 'Analysis complete.';
      }
    } catch (e) {
      console.warn('AI backend fallback:', e);
    }
  }

  const q = query.toLowerCase();
  if (q.includes('freelance') || q.includes('client') || q.includes('gig')) {
    return `Hi <strong>${userName}</strong>! For high-ticket freelance gigs in <strong>${skills}</strong>, focus on generating tailored, milestone-based proposals with verified architectural evidence. Check out the <strong>Business & Freelance Stream</strong> to pitch active clients.`;
  }
  if (q.includes('resume') || q.includes('ats')) {
    return `For <strong>${targetRole}</strong>, ensure your resume highlights quantified metrics (e.g. <em>"Reduced latency by 40%"</em>) and matches keywords with active skills (${skills}).`;
  }
  if (q.includes('what should i do') || q.includes('next')) {
    const nba = calculateNextBestAction();
    return `Based on your verified profile graph, your single highest-value action right now is: <strong>${nba.title}</strong> (${nba.score}) in the <strong>${nba.pillar}</strong>.`;
  }
  return `Great question, <strong>${userName}</strong>! As an aspiring <strong>${targetRole}</strong>, your AI Career OS is continuously calibrating actions across Full-Time Jobs, Skill Roadmaps, and Freelance Consulting.`;
}

/* ==========================================================================
   16. BACKEND HEALTH & UTILITIES
   ========================================================================== */
async function checkBackendHealth() {
  try {
    const res = await fetch('http://localhost:8000/health');
    if (res.ok) {
      appState.backendOnline = true;
      console.log('✅ Connected to AI Career OS FastAPI Backend.');
    }
  } catch (err) {
    appState.backendOnline = false;
    console.log('ℹ️ Running in client-side autonomous engine mode.');
  }
}

function showToast(message) {
  const existing = document.querySelector('.toast-msg');
  if (existing) existing.remove();

  const toast = document.createElement('div');
  toast.className = 'toast-msg';
  toast.textContent = message;
  document.body.appendChild(toast);

  setTimeout(() => {
    toast.remove();
  }, 3500);
}

function escapeHtml(str) {
  if (typeof str !== 'string') return '';
  return str.replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
}
