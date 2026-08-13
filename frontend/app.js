// AI Career OS — Module 3 Frontend App Logic

const API_BASE = "/api/v1";

// State
let token = localStorage.getItem("career_os_token") || null;
let currentUser = null;
let currentView = "dashboard";
let jobsData = [];
let applicationsData = [];
let contactsData = [];
let currentPage = 1;
let totalPages = 1;
let currentSelectedJob = null;
let currentSelectedApp = null;

// DOM Elements
const authSection = document.getElementById("authSection");
const appSection = document.getElementById("appSection");
const userMenu = document.getElementById("userMenu");
const navLinks = document.getElementById("navLinks");
const userGreeting = document.getElementById("userGreeting");

const authForm = document.getElementById("authForm");
const authEmail = document.getElementById("authEmail");
const authPassword = document.getElementById("authPassword");
const authFirstName = document.getElementById("authFirstName");
const authLastName = document.getElementById("authLastName");
const groupName = document.getElementById("groupName");
const tabLogin = document.getElementById("tabLogin");
const tabRegister = document.getElementById("tabRegister");
const btnAuthSubmit = document.getElementById("btnAuthSubmit");
const authError = document.getElementById("authError");

const viewDashboard = document.getElementById("viewDashboard");
const viewKanban = document.getElementById("viewKanban");
const viewContacts = document.getElementById("viewContacts");

const searchInput = document.getElementById("searchInput");
const filterStatus = document.getElementById("filterStatus");
const filterRemote = document.getElementById("filterRemote");
const filterFavorite = document.getElementById("filterFavorite");

const jobsGrid = document.getElementById("jobsGrid");
const jobsLoading = document.getElementById("jobsLoading");
const jobsEmpty = document.getElementById("jobsEmpty");
const paginationBar = document.getElementById("paginationBar");
const pageInfo = document.getElementById("pageInfo");
const btnPrevPage = document.getElementById("btnPrevPage");
const btnNextPage = document.getElementById("btnNextPage");

const countSaved = document.getElementById("countSaved");
const countApplied = document.getElementById("countApplied");
const countInterview = document.getElementById("countInterview");
const countOffer = document.getElementById("countOffer");

const kanbanBoard = document.getElementById("kanbanBoard");
const contactsGrid = document.getElementById("contactsGrid");

// Modals
const jobModal = document.getElementById("jobModal");
const jobForm = document.getElementById("jobForm");
const detailsModal = document.getElementById("detailsModal");
const contactModal = document.getElementById("contactModal");
const contactForm = document.getElementById("contactForm");

// Initialization
document.addEventListener("DOMContentLoaded", () => {
  setupEventListeners();
  if (token) {
    checkAuthAndInit();
  } else {
    showAuthView();
  }
});

// Auth Handlers
let isRegisterMode = false;

tabLogin.addEventListener("click", () => {
  isRegisterMode = false;
  tabLogin.classList.add("active");
  tabRegister.classList.remove("active");
  groupName.style.display = "none";
  btnAuthSubmit.textContent = "Sign In";
  authError.style.display = "none";
});

tabRegister.addEventListener("click", () => {
  isRegisterMode = true;
  tabRegister.classList.add("active");
  tabLogin.classList.remove("active");
  groupName.style.display = "block";
  btnAuthSubmit.textContent = "Create Account";
  authError.style.display = "none";
});

authForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  authError.style.display = "none";
  btnAuthSubmit.disabled = true;
  btnAuthSubmit.textContent = "Processing...";

  try {
    if (isRegisterMode) {
      const regRes = await fetch(`${API_BASE}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: authEmail.value,
          password: authPassword.value,
          first_name: authFirstName.value || "User",
          last_name: authLastName.value || "Member",
        }),
      });
      if (!regRes.ok) {
        const err = await regRes.json();
        throw new Error(err.error?.message || err.detail || "Registration failed");
      }
    }

    // Login
    const formData = new URLSearchParams();
    formData.append("username", authEmail.value);
    formData.append("password", authPassword.value);

    const loginRes = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: formData,
    });

    if (!loginRes.ok) {
      const err = await loginRes.json();
      throw new Error(err.error?.message || err.detail || "Invalid login credentials");
    }

    const data = await loginRes.json();
    token = data.access_token;
    localStorage.setItem("career_os_token", token);
    await checkAuthAndInit();
  } catch (err) {
    authError.textContent = err.message;
    authError.style.display = "block";
  } finally {
    btnAuthSubmit.disabled = false;
    btnAuthSubmit.textContent = isRegisterMode ? "Create Account" : "Sign In";
  }
});

document.getElementById("btnLogout").addEventListener("click", () => {
  token = null;
  localStorage.removeItem("career_os_token");
  showAuthView();
});

async function checkAuthAndInit() {
  try {
    const res = await apiRequest("/auth/me");
    currentUser = res;
    userGreeting.textContent = `${currentUser.first_name || "User"} (${currentUser.email})`;
    showAppView();
    loadDashboardData();
  } catch (err) {
    token = null;
    localStorage.removeItem("career_os_token");
    showAuthView();
  }
}

function showAuthView() {
  authSection.style.display = "flex";
  appSection.style.display = "none";
  userMenu.style.display = "none";
  navLinks.style.display = "none";
}

function showAppView() {
  authSection.style.display = "none";
  appSection.style.display = "block";
  userMenu.style.display = "flex";
  navLinks.style.display = "flex";
}

// API Helper
async function apiRequest(endpoint, options = {}) {
  const headers = options.headers || {};
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  if (options.body && !(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    token = null;
    localStorage.removeItem("career_os_token");
    showAuthView();
    throw new Error("Unauthorized");
  }

  if (response.status === 204) {
    return null;
  }

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error?.message || data.detail || "API request failed");
  }
  return data;
}

// Event Listeners & Navigation
function setupEventListeners() {
  document.querySelectorAll(".nav-btn").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      const view = e.target.dataset.view;
      switchView(view);
    });
  });

  searchInput.addEventListener("input", debounce(() => loadDashboardData(), 300));
  filterStatus.addEventListener("change", () => loadDashboardData());
  filterRemote.addEventListener("change", () => loadDashboardData());
  filterFavorite.addEventListener("change", () => loadDashboardData());

  btnPrevPage.addEventListener("click", () => {
    if (currentPage > 1) {
      currentPage--;
      loadDashboardData();
    }
  });

  btnNextPage.addEventListener("click", () => {
    if (currentPage < totalPages) {
      currentPage++;
      loadDashboardData();
    }
  });

  // Modal Triggers
  document.getElementById("btnOpenAddJobModal").addEventListener("click", () => openJobModal());
  document.getElementById("btnEmptyAddJob").addEventListener("click", () => openJobModal());
  document.getElementById("btnCloseJobModal").addEventListener("click", closeJobModal);
  document.getElementById("btnCancelJobModal").addEventListener("click", closeJobModal);
  document.getElementById("btnCloseDetailsModal").addEventListener("click", closeDetailsModal);
  document.getElementById("btnOpenAddContactModal").addEventListener("click", openContactModal);
  document.getElementById("btnCloseContactModal").addEventListener("click", closeContactModal);
  document.getElementById("btnCancelContactModal").addEventListener("click", closeContactModal);

  jobForm.addEventListener("submit", handleSaveJob);
  contactForm.addEventListener("submit", handleSaveContact);
  document.getElementById("detailStatusSelect").addEventListener("change", handleStatusChange);
}

function switchView(view) {
  currentView = view;
  document.querySelectorAll(".nav-btn").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.view === view);
  });

  const viewAI = document.getElementById("viewAI");
  const viewResumes = document.getElementById("viewResumes");
  const viewInterviews = document.getElementById("viewInterviews");
  const viewCareer = document.getElementById("viewCareer");

  viewDashboard.style.display = view === "dashboard" ? "block" : "none";
  viewKanban.style.display = view === "kanban" ? "block" : "none";
  viewContacts.style.display = view === "contacts" ? "block" : "none";
  if (viewAI) viewAI.style.display = view === "ai" ? "block" : "none";
  if (viewResumes) viewResumes.style.display = view === "resumes" ? "block" : "none";
  if (viewInterviews) viewInterviews.style.display = view === "interviews" ? "block" : "none";
  if (viewCareer) viewCareer.style.display = view === "career" ? "block" : "none";

  if (view === "dashboard") loadDashboardData();
  if (view === "kanban") loadKanbanData();
  if (view === "contacts") loadContactsData();
  if (view === "resumes") loadResumesData();
  if (view === "interviews") loadInterviewsData();
  if (view === "career") loadCareerData();
}

// CAREER EXECUTION & ADAPTIVE GROWTH (Module 7)
document.getElementById("btnGenerateCareerRoadmap")?.addEventListener("click", async () => {
  const role = prompt("Enter Target Career Role (e.g. 'Senior Python Backend Engineer'):");
  try {
    const url = role ? `/career/roadmaps/generate?target_role=${encodeURIComponent(role)}` : "/career/roadmaps/generate";
    await apiRequest(url, { method: "POST" });
    loadCareerData();
  } catch (err) {
    alert("Error generating roadmap: " + err.message);
  }
});

document.getElementById("btnAdaptCareerStrategy")?.addEventListener("click", async () => {
  try {
    await apiRequest("/career/roadmaps/adapt", { method: "POST" });
    loadCareerData();
    alert("Roadmap successfully adapted to new execution strategy version!");
  } catch (err) {
    alert("Error adapting strategy: " + err.message);
  }
});

async function loadCareerData() {
  try {
    const metrics = await apiRequest("/career/progress");
    document.getElementById("gaugeTaskRate").textContent = `${metrics.task_completion_rate}% (${metrics.completed_tasks}/${metrics.total_tasks})`;
    document.getElementById("gaugeAppRate").textContent = `${metrics.application_response_rate}%`;
    document.getElementById("gaugeInterviewScore").textContent = `${metrics.interview_score_avg}/100`;

    const active = await apiRequest("/career/roadmaps/active");
    if (active) {
      document.getElementById("roadmapTitle").textContent = `${active.target_role} (Roadmap v${active.version})`;
      document.getElementById("roadmapObjective").textContent = active.objective;

      const milestonesEl = document.getElementById("roadmapMilestones");
      milestonesEl.innerHTML = "";

      const msList = active.milestones || [];
      msList.forEach((m) => {
        const item = document.createElement("div");
        item.style.padding = "1rem";
        item.style.background = "rgba(15, 23, 42, 0.5)";
        item.style.borderRadius = "8px";
        item.style.border = "1px solid var(--border-color)";

        item.innerHTML = `
          <div style="font-weight: 600; color: var(--primary);">${escapeHtml(m.title)} <span style="font-size: 0.75rem; color: var(--text-muted);">(${escapeHtml(m.target_date || 'Ongoing')})</span></div>
          <div style="font-size: 0.85rem; color: var(--text-muted); margin-top: 0.4rem;">${escapeHtml(m.description)}</div>
        `;
        milestonesEl.appendChild(item);
      });
    }
  } catch (err) {
    console.log("Career roadmap loading notice:", err.message);
  }
}


// INTERVIEWS & MOCK COACH (Module 6)
const interviewsList = document.getElementById("interviewsList");

document.getElementById("btnOpenScheduleInterviewModal")?.addEventListener("click", async () => {
  const title = prompt("Enter Interview Title (e.g. 'Backend Engineer Interview'):");
  if (!title) return;
  const company = prompt("Enter Company Name (e.g. 'Amazon'):");

  try {
    await apiRequest("/interviews", {
      method: "POST",
      body: JSON.stringify({
        title: title,
        company_name: company || "Tech Company",
        interview_type: "TECHNICAL",
      }),
    });
    loadInterviewsData();
  } catch (err) {
    alert("Could not schedule interview: " + err.message);
  }
});

async function loadInterviewsData() {
  if (!interviewsList) return;
  interviewsList.innerHTML = '<div class="loading-spinner"><div class="spinner"></div></div>';
  try {
    const interviews = await apiRequest("/interviews");
    renderInterviewsList(interviews);
  } catch (err) {
    interviewsList.innerHTML = '<div class="alert alert-error">Failed to load interview sessions</div>';
  }
}

function renderInterviewsList(interviews) {
  interviewsList.innerHTML = "";
  if (!interviews || interviews.length === 0) {
    interviewsList.innerHTML = '<div class="empty-state"><h3>No interviews scheduled</h3><p>Schedule your upcoming interview to generate preparation strategy, practice questions, and Module 3 tasks.</p></div>';
    return;
  }

  interviews.forEach((inv) => {
    const card = document.createElement("div");
    card.className = "interview-card";
    const scoreText = inv.overall_score ? `${inv.overall_score}/100` : "Not Scored";

    card.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.75rem;">
        <div>
          <h3>${escapeHtml(inv.title)}</h3>
          <span style="font-size: 0.85rem; color: var(--primary); font-weight: 500;">${escapeHtml(inv.company_name || "Company")}</span>
        </div>
        <span class="score-badge">${scoreText}</span>
      </div>

      <div style="font-size: 0.8rem; color: var(--text-muted); margin: 0.5rem 0;">
        Status: <strong>${inv.status}</strong> • Type: <strong>${inv.interview_type}</strong>
      </div>

      <div style="display: flex; gap: 0.5rem; flex-wrap: wrap; margin-top: 1rem; border-top: 1px solid var(--border-color); padding-top: 0.75rem;">
        <button class="btn btn-sm btn-primary btn-prep-interview" data-id="${inv.id}">📅 Prepare & Tasks</button>
        <button class="btn btn-sm btn-outline btn-report-interview" data-id="${inv.id}">📊 Final Report</button>
      </div>
    `;

    card.querySelector(".btn-prep-interview").addEventListener("click", () => runInterviewPreparation(inv.id));
    card.querySelector(".btn-report-interview").addEventListener("click", () => runInterviewReport(inv.id));

    interviewsList.appendChild(card);
  });
}

async function runInterviewPreparation(interviewId) {
  try {
    const res = await apiRequest(`/interviews/${interviewId}/prepare`, { method: "POST" });
    alert(`Interview Preparation Strategy Generated!\n\nPriority Topics:\n- ${res.priority_topics.join("\n- ")}\n\nModule 3 Tasks Created: ${res.preparation_tasks_created}`);
    loadInterviewsData();
  } catch (err) {
    alert("Preparation error: " + err.message);
  }
}

async function runInterviewReport(interviewId) {
  try {
    const res = await apiRequest(`/interviews/${interviewId}/report`);
    alert(`Final Interview Report (${res.title})\n\nOverall Score: ${res.overall_score}/100\nTechnical: ${res.technical_score}\nCommunication: ${res.communication_score}\n\nKey Strengths:\n- ${res.strengths.join("\n- ")}\n\nNext Steps:\n- ${res.recommended_next_steps.join("\n- ")}`);
  } catch (err) {
    alert("Report error: " + err.message);
  }
}


// RESUMES MANAGEMENT (Module 5)
const uploadResumeForm = document.getElementById("uploadResumeForm");
const resumeFileInput = document.getElementById("resumeFileInput");
const resumesList = document.getElementById("resumesList");

if (uploadResumeForm) {
  uploadResumeForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!resumeFileInput.files[0]) return;

    const formData = new FormData();
    formData.append("file", resumeFileInput.files[0]);

    try {
      document.getElementById("btnUploadResume").disabled = true;
      document.getElementById("btnUploadResume").textContent = "Uploading & Parsing...";

      await apiRequest("/resumes/upload", {
        method: "POST",
        body: formData,
      });

      uploadResumeForm.reset();
      loadResumesData();
    } catch (err) {
      alert("Error uploading resume: " + err.message);
    } finally {
      document.getElementById("btnUploadResume").disabled = false;
      document.getElementById("btnUploadResume").textContent = "Upload Resume";
    }
  });
}

async function loadResumesData() {
  if (!resumesList) return;
  resumesList.innerHTML = '<div class="loading-spinner"><div class="spinner"></div></div>';
  try {
    const resumes = await apiRequest("/resumes");
    renderResumesList(resumes);
  } catch (err) {
    resumesList.innerHTML = '<div class="alert alert-error">Failed to load resumes</div>';
  }
}

function renderResumesList(resumes) {
  resumesList.innerHTML = "";
  if (!resumes || resumes.length === 0) {
    resumesList.innerHTML = '<div class="empty-state"><h3>No resumes uploaded</h3><p>Upload a PDF or DOCX resume to get AI analysis, ATS scanning, and tailoring.</p></div>';
    return;
  }

  resumes.forEach((r) => {
    const card = document.createElement("div");
    card.className = "resume-card";
    const activeVersion = r.versions.find((v) => v.is_active) || r.versions[0];

    card.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.75rem;">
        <div>
          <h3>${escapeHtml(r.name)}</h3>
          <span style="font-size: 0.8rem; color: var(--text-muted);">${escapeHtml(r.original_filename)}</span>
        </div>
        <span class="version-tag">${activeVersion ? activeVersion.version_name : "v1.0"}</span>
      </div>

      <div style="margin: 0.75rem 0; font-size: 0.85rem; color: var(--text-muted); max-height: 80px; overflow: hidden;">
        ${escapeHtml(activeVersion ? activeVersion.content.substring(0, 180) : "No content")}...
      </div>

      <div style="display: flex; gap: 0.5rem; flex-wrap: wrap; margin-top: 1rem; border-top: 1px solid var(--border-color); padding-top: 0.75rem;">
        <button class="btn btn-sm btn-outline btn-analyze-resume" data-id="${r.id}">📊 Quality Analysis</button>
        <button class="btn btn-sm btn-outline btn-ats-resume" data-id="${r.id}">🎯 ATS Scan</button>
        <button class="btn btn-sm btn-outline btn-delete-resume" data-id="${r.id}" style="color: #fca5a5;">Delete</button>
      </div>
    `;

    card.querySelector(".btn-analyze-resume").addEventListener("click", () => runResumeAnalysis(r.id));
    card.querySelector(".btn-ats-resume").addEventListener("click", () => runATSScan(r.id));
    card.querySelector(".btn-delete-resume").addEventListener("click", () => deleteResume(r.id));

    resumesList.appendChild(card);
  });
}

async function runResumeAnalysis(resumeId) {
  try {
    const res = await apiRequest(`/resumes/${resumeId}/analyze`, { method: "POST" });
    alert(`Resume Quality Score: ${res.overall_score}/100\n\nStrengths:\n- ${res.strengths.join("\n- ")}\n\nWeaknesses:\n- ${res.weaknesses.join("\n- ")}`);
  } catch (err) {
    alert("Analysis error: " + err.message);
  }
}

async function runATSScan(resumeId) {
  const jobDesc = prompt("Enter Target Job Description to run ATS Keyword Scan:");
  if (!jobDesc) return;
  try {
    const res = await apiRequest(`/resumes/${resumeId}/ats-analysis?job_description=${encodeURIComponent(jobDesc)}`, { method: "POST" });
    alert(`ATS Keyword Match Coverage: ${res.keyword_coverage_percent}%\n\nMatched Keywords:\n${res.matched_keywords.join(", ")}\n\nMissing Keywords:\n${res.missing_keywords.join(", ")}`);
  } catch (err) {
    alert("ATS Scan error: " + err.message);
  }
}

async function deleteResume(resumeId) {
  if (!confirm("Are you sure you want to delete this resume?")) return;
  try {
    await apiRequest(`/resumes/${resumeId}`, { method: "DELETE" });
    loadResumesData();
  } catch (err) {
    alert("Could not delete resume");
  }
}


// AI COPILOT CHAT
const chatForm = document.getElementById("chatForm");
const chatInput = document.getElementById("chatInput");
const chatMessages = document.getElementById("chatMessages");

if (chatForm) {
  chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const msg = chatInput.value.trim();
    if (!msg) return;

    appendChatMessage("user", msg);
    chatInput.value = "";

    try {
      const res = await apiRequest("/ai/chat", {
        method: "POST",
        body: JSON.stringify({ message: msg }),
      });
      appendChatMessage("assistant", res.reply);
    } catch (err) {
      appendChatMessage("system", "Error communicating with AI Copilot: " + err.message);
    }
  });
}

document.getElementById("btnAiAnalyzeCareer")?.addEventListener("click", async () => {
  appendChatMessage("system", "Running Career Strategist Agent analysis...");
  try {
    const res = await apiRequest("/ai/career/analyze", { method: "POST" });
    appendChatMessage("assistant", res.summary);
  } catch (err) {
    appendChatMessage("system", "Error: " + err.message);
  }
});

document.getElementById("btnAiPlanDaily")?.addEventListener("click", async () => {
  appendChatMessage("system", "Synthesizing Daily Action Plan via Planner Agent...");
  try {
    const res = await apiRequest("/ai/career/plan", { method: "POST" });
    appendChatMessage("assistant", res.daily_plan);
  } catch (err) {
    appendChatMessage("system", "Error: " + err.message);
  }
});

function appendChatMessage(sender, text) {
  if (!chatMessages) return;
  const msgEl = document.createElement("div");
  msgEl.className = `chat-msg ${sender}-msg`;
  msgEl.innerHTML = `<strong>${sender === "user" ? "You" : sender === "assistant" ? "🤖 AI Copilot" : "System"}</strong>: ${escapeHtml(text)}`;
  chatMessages.appendChild(msgEl);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}


// DASHBOARD
async function loadDashboardData() {
  jobsLoading.style.display = "flex";
  jobsGrid.style.display = "none";
  jobsEmpty.style.display = "none";

  try {
    const params = new URLSearchParams({
      page: currentPage,
      page_size: 9,
    });

    if (searchInput.value) params.append("search", searchInput.value);
    if (filterStatus.value) params.append("status", filterStatus.value);
    if (filterRemote.value) params.append("remote_type", filterRemote.value);
    if (filterFavorite.checked) params.append("is_favorite", "true");

    const res = await apiRequest(`/jobs?${params.toString()}`);
    jobsData = res.items;
    totalPages = res.total_pages;

    renderJobsGrid(jobsData);
    updatePaginationControls(res.page, res.total_pages);
    await updateMetrics();
  } catch (err) {
    console.error("Error loading jobs:", err);
  } finally {
    jobsLoading.style.display = "none";
  }
}

async function updateMetrics() {
  try {
    const appsRes = await apiRequest("/applications?page_size=100");
    const apps = appsRes.items || [];
    
    let saved = 0, applied = 0, interview = 0, offer = 0;
    apps.forEach(a => {
      if (a.status === "SAVED") saved++;
      if (a.status === "APPLIED" || a.status === "UNDER_REVIEW") applied++;
      if (a.status === "INTERVIEW" || a.status === "HR_ROUND" || a.status === "ASSESSMENT") interview++;
      if (a.status === "OFFER") offer++;
    });

    countSaved.textContent = saved;
    countApplied.textContent = applied;
    countInterview.textContent = interview;
    countOffer.textContent = offer;
  } catch (err) {
    console.error("Error loading metrics:", err);
  }
}

function renderJobsGrid(jobs) {
  jobsGrid.innerHTML = "";
  if (!jobs || jobs.length === 0) {
    jobsEmpty.style.display = "block";
    paginationBar.style.display = "none";
    return;
  }

  jobsEmpty.style.display = "none";
  jobsGrid.style.display = "grid";

  jobs.forEach((job) => {
    const card = document.createElement("div");
    card.className = "job-card";

    const salaryText = job.salary_min || job.salary_max
      ? `${job.currency || "$"} ${job.salary_min || 0} - ${job.salary_max || "Max"}`
      : "Salary N/A";

    card.innerHTML = `
      <div>
        <div class="job-card-header">
          <div>
            <h3 class="job-title">${escapeHtml(job.title)}</h3>
            <span class="company-name">${escapeHtml(job.company_name || "Company")}</span>
          </div>
          <button class="fav-btn ${job.is_favorite ? "active" : ""}" data-id="${job.id}">
            ${job.is_favorite ? "★" : "☆"}
          </button>
        </div>
        
        <div class="job-tags">
          <span class="tag">📍 ${escapeHtml(job.location || "Remote")}</span>
          <span class="tag">🌐 ${escapeHtml(job.remote_type || "REMOTE")}</span>
          <span class="tag">💼 ${escapeHtml(job.employment_type || "FULL_TIME")}</span>
        </div>
      </div>

      <div class="job-card-footer">
        <span class="salary-tag">${salaryText}</span>
        <button class="btn btn-sm btn-outline btn-view-details" data-id="${job.id}">Details →</button>
      </div>
    `;

    // Event listeners inside card
    card.querySelector(".fav-btn").addEventListener("click", (e) => {
      e.stopPropagation();
      toggleFavorite(job.id, !job.is_favorite);
    });

    card.querySelector(".btn-view-details").addEventListener("click", () => {
      openDetailsModal(job.id);
    });

    jobsGrid.appendChild(card);
  });
}

function updatePaginationControls(page, total) {
  if (total <= 1) {
    paginationBar.style.display = "none";
    return;
  }
  paginationBar.style.display = "flex";
  pageInfo.textContent = `Page ${page} of ${total}`;
  btnPrevPage.disabled = page <= 1;
  btnNextPage.disabled = page >= total;
}

async function toggleFavorite(jobId, isFavorite) {
  try {
    await apiRequest(`/jobs/${jobId}`, {
      method: "PATCH",
      body: JSON.stringify({ is_favorite: isFavorite }),
    });
    loadDashboardData();
  } catch (err) {
    alert("Could not update favorite state");
  }
}

// KANBAN BOARD
async function loadKanbanData() {
  kanbanBoard.innerHTML = '<div class="loading-spinner"><div class="spinner"></div></div>';
  try {
    const res = await apiRequest("/applications?page_size=100");
    applicationsData = res.items || [];
    renderKanbanBoard(applicationsData);
  } catch (err) {
    kanbanBoard.innerHTML = '<div class="alert alert-error">Failed to load pipeline data</div>';
  }
}

function renderKanbanBoard(applications) {
  const columns = [
    { key: "SAVED", label: "Saved" },
    { key: "APPLIED", label: "Applied" },
    { key: "UNDER_REVIEW", label: "Under Review" },
    { key: "SHORTLISTED", label: "Shortlisted" },
    { key: "INTERVIEW", label: "Interview" },
    { key: "OFFER", label: "Offer" },
    { key: "REJECTED", label: "Rejected" },
  ];

  kanbanBoard.innerHTML = "";

  columns.forEach((col) => {
    const colApps = applications.filter((a) => a.status === col.key);
    const colEl = document.createElement("div");
    colEl.className = "kanban-column";
    
    colEl.innerHTML = `
      <div class="kanban-header">
        <span>${col.label}</span>
        <span class="kanban-count">${colApps.length}</span>
      </div>
      <div class="kanban-cards" id="kanban-col-${col.key}"></div>
    `;

    const cardsContainer = colEl.querySelector(".kanban-cards");

    colApps.forEach((app) => {
      const card = document.createElement("div");
      card.className = "kanban-card";
      card.innerHTML = `
        <div class="job-title" style="font-size: 0.95rem;">${escapeHtml(app.job?.title || "Job")}</div>
        <div class="company-name" style="font-size: 0.8rem;">${escapeHtml(app.job?.company_name || "")}</div>
        <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.4rem;">
          📍 ${escapeHtml(app.job?.location || "Remote")}
        </div>
      `;

      card.addEventListener("click", () => {
        if (app.job?.id) openDetailsModal(app.job.id);
      });

      cardsContainer.appendChild(card);
    });

    kanbanBoard.appendChild(colEl);
  });
}

// JOB DETAILS MODAL
async function openDetailsModal(jobId) {
  try {
    const job = await apiRequest(`/jobs/${jobId}`);
    currentSelectedJob = job;

    // Get or Create Application
    let app = null;
    const appsRes = await apiRequest("/applications?page_size=100");
    app = (appsRes.items || []).find((a) => a.job_id === jobId);

    if (!app) {
      app = await apiRequest(`/jobs/${jobId}/applications`, {
        method: "POST",
        body: JSON.stringify({ status: "SAVED" }),
      });
    }

    currentSelectedApp = app;

    // Populate Modal
    document.getElementById("detailJobTitle").textContent = job.title;
    document.getElementById("detailJobSub").textContent = `${job.company_name || "Company"} • ${job.location || "Remote"}`;
    document.getElementById("detailDescription").textContent = job.description || "No job description provided.";
    document.getElementById("detailStatusSelect").value = app.status;

    // Badges
    const badgesEl = document.getElementById("detailBadges");
    badgesEl.innerHTML = `
      <span class="tag">Work: ${job.remote_type || "REMOTE"}</span>
      <span class="tag">Type: ${job.employment_type || "FULL_TIME"}</span>
      <span class="tag">Salary: ${job.currency || "$"} ${job.salary_min || 0} - ${job.salary_max || "Max"}</span>
    `;

    renderTimeline(app.events || []);
    renderTasks(app.tasks || []);

    detailsModal.style.display = "flex";
  } catch (err) {
    alert("Could not load job details: " + err.message);
  }
}

function closeDetailsModal() {
  detailsModal.style.display = "none";
}

async function handleStatusChange(e) {
  if (!currentSelectedApp) return;
  const newStatus = e.target.value;
  try {
    const updated = await apiRequest(`/applications/${currentSelectedApp.id}/status`, {
      method: "PATCH",
      body: JSON.stringify({
        status: newStatus,
        description: `Status changed to ${newStatus}`,
      }),
    });
    currentSelectedApp = updated;
    renderTimeline(updated.events || []);
    if (currentView === "dashboard") loadDashboardData();
    if (currentView === "kanban") loadKanbanData();
  } catch (err) {
    alert("Could not update status: " + err.message);
  }
}

function renderTimeline(events) {
  const container = document.getElementById("detailTimeline");
  container.innerHTML = "";
  if (!events || events.length === 0) {
    container.innerHTML = '<p class="muted">No events yet.</p>';
    return;
  }

  events.sort((a, b) => new Date(b.event_date) - new Date(a.event_date)).forEach((evt) => {
    const item = document.createElement("div");
    item.className = "timeline-item";
    const dateStr = new Date(evt.event_date).toLocaleDateString();
    item.innerHTML = `
      <div><strong>${escapeHtml(evt.event_type)}</strong>: ${escapeHtml(evt.description)}</div>
      <div class="timeline-date">${dateStr}</div>
    `;
    container.appendChild(item);
  });
}

function renderTasks(tasks) {
  const container = document.getElementById("detailTasksList");
  container.innerHTML = "";
  if (!tasks || tasks.length === 0) {
    container.innerHTML = '<p class="muted" style="font-size: 0.85rem;">No action tasks yet.</p>';
    return;
  }

  tasks.forEach((t) => {
    const item = document.createElement("div");
    item.style.display = "flex";
    item.style.alignItems = "center";
    item.style.gap = "0.5rem";
    item.style.fontSize = "0.85rem";
    item.style.margin = "0.4rem 0";

    item.innerHTML = `
      <input type="checkbox" ${t.status === "COMPLETED" ? "checked" : ""} data-id="${t.id}">
      <span style="${t.status === "COMPLETED" ? "text-decoration: line-through; color: var(--text-muted);" : ""}">${escapeHtml(t.title)}</span>
    `;

    item.querySelector("input").addEventListener("change", async (e) => {
      const isDone = e.target.checked;
      await apiRequest(`/tasks/${t.id}`, {
        method: "PATCH",
        body: JSON.stringify({ status: isDone ? "COMPLETED" : "PENDING" }),
      });
      openDetailsModal(currentSelectedJob.id);
    });

    container.appendChild(item);
  });
}

document.getElementById("btnAddDetailTask").addEventListener("click", async () => {
  const title = prompt("Enter task title (e.g. Prepare DSA graphs):");
  if (!title || !currentSelectedApp) return;
  try {
    await apiRequest(`/applications/${currentSelectedApp.id}/tasks`, {
      method: "POST",
      body: JSON.stringify({ title, priority: "HIGH" }),
    });
    openDetailsModal(currentSelectedJob.id);
  } catch (err) {
    alert("Could not add task");
  }
});

// JOB MODAL
function openJobModal(jobToEdit = null) {
  jobForm.reset();
  if (jobToEdit) {
    document.getElementById("jobModalTitle").textContent = "Edit Job";
    document.getElementById("jobEditId").value = jobToEdit.id;
    document.getElementById("jobTitle").value = jobToEdit.title;
    document.getElementById("jobCompanyName").value = jobToEdit.company_name || "";
    document.getElementById("jobLocation").value = jobToEdit.location || "";
    document.getElementById("jobRemoteType").value = jobToEdit.remote_type || "REMOTE";
    document.getElementById("jobSalaryMin").value = jobToEdit.salary_min || "";
    document.getElementById("jobSalaryMax").value = jobToEdit.salary_max || "";
    document.getElementById("jobUrl").value = jobToEdit.job_url || "";
    document.getElementById("jobDescription").value = jobToEdit.description || "";
  } else {
    document.getElementById("jobModalTitle").textContent = "Add New Job";
    document.getElementById("jobEditId").value = "";
  }
  jobModal.style.display = "flex";
}

function closeJobModal() {
  jobModal.style.display = "none";
}

async function handleSaveJob(e) {
  e.preventDefault();
  const editId = document.getElementById("jobEditId").value;
  const payload = {
    title: document.getElementById("jobTitle").value,
    company_name: document.getElementById("jobCompanyName").value,
    location: document.getElementById("jobLocation").value,
    remote_type: document.getElementById("jobRemoteType").value,
    salary_min: document.getElementById("jobSalaryMin").value ? parseInt(document.getElementById("jobSalaryMin").value) : null,
    salary_max: document.getElementById("jobSalaryMax").value ? parseInt(document.getElementById("jobSalaryMax").value) : null,
    currency: document.getElementById("jobCurrency").value || "USD",
    job_url: document.getElementById("jobUrl").value || null,
    source: document.getElementById("jobSource").value || null,
    description: document.getElementById("jobDescription").value || null,
  };

  try {
    if (editId) {
      await apiRequest(`/jobs/${editId}`, { method: "PATCH", body: JSON.stringify(payload) });
    } else {
      await apiRequest("/jobs", { method: "POST", body: JSON.stringify(payload) });
    }
    closeJobModal();
    loadDashboardData();
  } catch (err) {
    alert("Error saving job: " + err.message);
  }
}

// CONTACTS DIRECTORY
async function loadContactsData() {
  contactsGrid.innerHTML = '<div class="loading-spinner"><div class="spinner"></div></div>';
  try {
    const contacts = await apiRequest("/contacts");
    contactsData = contacts;
    renderContactsGrid(contacts);
  } catch (err) {
    contactsGrid.innerHTML = '<div class="alert alert-error">Failed to load contacts</div>';
  }
}

function renderContactsGrid(contacts) {
  contactsGrid.innerHTML = "";
  if (!contacts || contacts.length === 0) {
    contactsGrid.innerHTML = '<div class="empty-state"><h3>No recruiter contacts saved</h3></div>';
    return;
  }

  contacts.forEach((c) => {
    const card = document.createElement("div");
    card.className = "glass-card";
    card.style.padding = "1.25rem";
    card.innerHTML = `
      <h3>${escapeHtml(c.name)}</h3>
      <p style="color: var(--primary); font-size: 0.85rem; margin-bottom: 0.5rem;">${escapeHtml(c.designation || "Recruiter")}</p>
      <div style="font-size: 0.85rem; color: var(--text-muted);">
        <div>📧 ${escapeHtml(c.email || "N/A")}</div>
        <div>📞 ${escapeHtml(c.phone || "N/A")}</div>
      </div>
    `;
    contactsGrid.appendChild(card);
  });
}

function openContactModal() {
  contactForm.reset();
  contactModal.style.display = "flex";
}

function closeContactModal() {
  contactModal.style.display = "none";
}

async function handleSaveContact(e) {
  e.preventDefault();
  const payload = {
    name: document.getElementById("contactName").value,
    designation: document.getElementById("contactDesignation").value || null,
    email: document.getElementById("contactEmail").value || null,
    phone: document.getElementById("contactPhone").value || null,
    linkedin_url: document.getElementById("contactLinkedin").value || null,
  };
  try {
    await apiRequest("/contacts", { method: "POST", body: JSON.stringify(payload) });
    closeContactModal();
    loadContactsData();
  } catch (err) {
    alert("Error saving contact: " + err.message);
  }
}

// Helpers
function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}
