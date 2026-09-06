import React, { useEffect } from 'react';
import './index.css';
import './legacy-app.js'; // Import the legacy logic temporarily while we modularize
import AICoach from './components/AICoach';

function App() {
  useEffect(() => {
    // Dispatch an event to let the legacy script know React is ready
    document.dispatchEvent(new Event('react-mounted'));
  }, []);

  return (
    <div className="app-container">
      {/* Content ported from index.html */}
      
  {/*  AUTH SECTION (Modal shown if not signed in)  */}
  <div id="authSection" className="modal-overlay">
    <div className="modal-content" style={{ "maxWidth": "420px" }}>
      <div style={{ "textAlign": "center", "marginBottom": "1.25rem" }}>
        <div className="logo-icon-box" style={{ "margin": "0 auto 0.75rem", "width": "48px", "height": "48px", "fontSize": "1.5rem" }}>💼</div>
        <h2 style={{ "fontSize": "1.35rem", "fontWeight": "700" }}>AI Career Operating System</h2>
        <p style={{ "fontSize": "0.85rem", "color": "var(--text-muted)", "marginTop": "0.2rem" }} id="authSubtitle">Sign in to your account</p>
      </div>

      <div style={{ "display": "flex", "background": "var(--bg-input)", "padding": "3px", "borderRadius": "8px", "marginBottom": "1.25rem" }}>
        <button className="btn btn-block active" id="tabLogin" style={{ "fontSize": "0.82rem", "padding": "0.45rem" }}>Sign In</button>
        <button className="btn btn-block" id="tabRegister" style={{ "fontSize": "0.82rem", "padding": "0.45rem", "background": "transparent", "color": "var(--text-muted)" }}>Create Account</button>
      </div>

      <form id="authForm">
        <div className="form-group" id="groupName" style={{ display: "none" }}>
          <label>Full Name</label>
          <input type="text" id="authName" placeholder="e.g. Alex Johnson" />
        </div>
        <div className="form-group">
          <label>Email Address</label>
          <input type="email" id="authEmail" required placeholder="e.g. alex@example.com" />
        </div>
        <div className="form-group">
          <label>Password</label>
          <input type="password" id="authPassword" required placeholder="••••••••" />
        </div>
        <button type="submit" className="btn btn-primary btn-block" id="btnAuthSubmit" style={{ "marginTop": "0.5rem" }}>Sign In</button>
      </form>
      <div id="authError" style={{ "marginTop": "0.75rem", "fontSize": "0.8rem", "color": "var(--danger)", "textAlign": "center", "display": "none" }}></div>
    </div>
  </div>

  {/*  MAIN APP SHELL  */}
  <div id="appSection" className="app-shell" style={{ display: "flex" }}>
    
    {/*  LEFT SIDEBAR  */}
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="brand-logo">
          <div className="logo-icon-box">🧠</div>
          <span>AI Career <span style={{ "color": "var(--primary)" }}>OS</span></span>
        </div>
      </div>

      <nav className="sidebar-nav">
        <button className="nav-link active" data-view="dashboard">
          <span className="nav-icon">🏠</span> Dashboard (Command Center)
        </button>
        <button className="nav-link" data-view="commandCenter">
          <span className="nav-icon">🧠</span> AI Decision Engine
        </button>
        <button className="nav-link" data-view="jobs">
          <span className="nav-icon">💼</span> Opportunity Intelligence
        </button>
        <button className="nav-link" data-view="kanban">
          <span className="nav-icon">📋</span> Applications Pipeline
        </button>
        <button className="nav-link" data-view="interviews">
          <span className="nav-icon">🎤</span> Interview Intelligence
        </button>
        <button className="nav-link" data-view="learning">
          <span className="nav-icon">📚</span> Learning & Skill Gaps
        </button>
        <button className="nav-link" data-view="projects">
          <span className="nav-icon">🧩</span> Project Evidence Graph
        </button>
        <button className="nav-link" data-view="resumes">
          <span className="nav-icon">📄</span> Resume Intelligence
        </button>
        <button className="nav-link" data-view="business">
          <span className="nav-icon">🚀</span> Freelance & Client Gigs
        </button>
        <button className="nav-link" data-view="network">
          <span className="nav-icon">🌐</span> Network & Referrals
        </button>
        <button className="nav-link" data-view="offers">
          <span className="nav-icon">⭐</span> Personal Brand & Offers
        </button>
        <button className="nav-link" data-view="aiCoach">
          <span className="nav-icon">🤖</span> AI Career Coach
        </button>
        <button className="nav-link" data-view="integrations">
          <span className="nav-icon">🔌</span> Connected Accounts & Tools
        </button>
        <button className="nav-link" data-view="analytics">
          <span className="nav-icon">📊</span> Career Analytics & Telemetry
        </button>
        <button className="nav-link" data-view="settings">
          <span className="nav-icon">⚙️</span> Settings
        </button>
      </nav>

      {/*  SIDEBAR USER PROFILE FOOTER  */}
      <div className="sidebar-user-card">
        <div className="user-info">
          <div className="user-avatar" id="avatarInitials">?</div>
          <div className="user-details">
            <h5 id="userNameDisplay">User</h5>
            <span id="userRoleBadge">Active Account</span>
          </div>
        </div>
        <button className="btn-signout" id="btnLogout" title="Sign Out">🚪</button>
      </div>
    </aside>

    {/*  MAIN RIGHT WRAPPER  */}
    <div className="main-wrapper">
      
      {/*  TOP HEADER BAR  */}
      {/*  TOP HEADER BAR  */}
      <header className="top-header">
        <div className="header-search">
          <span className="search-icon">🔍</span>
          <input type="text" id="globalSearch" placeholder="Search across Jobs, Learning & Freelance Gigs..." />
        </div>

        <div className="header-actions">
          <div className="live-pulse-badge">
            <span className="pulse-dot"></span>
            <span>Live AI Pulse: Active</span>
          </div>
          <button className="theme-toggle-btn" id="themeToggleBtn" title="Toggle Light/Dark Theme">🌙</button>
          <button className="btn-ask-ai" id="btnHeaderAskAI">
            <span>⚡</span> "What Should I Do Next?"
          </button>
        </div>
      </header>

      {/*  PAGE CONTENT AREA  */}
      <main className="page-content">
        
        {/*  VIEW 1: AI CAREER COMMAND CENTER (REARCHITECTED DASHBOARD)  */}
        <section id="viewDashboard" className="app-view">
          
          {/*  1. 🧠 AI CAREER STATE (The most important part)  */}
          <div className="command-center-header">
            <div style={{ "display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "1.5rem", "flexWrap": "wrap", "gap": "1rem" }}>
              <h1 className="cmd-title" style={{ "fontSize": "1.75rem", "fontWeight": "800", "margin": "0", "letterSpacing": "-0.03em" }}>YOUR <span style={{ "color": "var(--primary)" }}>CAREER STATE</span></h1>
              <span className="live-pulse-badge" style={{ "fontSize": "0.85rem", "padding": "0.4rem 1rem" }}>
                <span className="pulse-dot"></span>
                AI Orchestrator Online
              </span>
            </div>

            {/*  MAIN METRICS BOX (Glassmorphic, Spacious)  */}
            <div className="career-state-box">
              <div className="state-goal-section">
                <div>
                  <div className="state-label">Goal</div>
                  <div className="state-value highlight">Senior AI/ML Systems Engineer</div>
                </div>
                <div>
                  <div className="state-label">Target</div>
                  <div className="state-value">90 Days</div>
                </div>
              </div>

              <div className="state-metrics-grid">
                <div className="metric-item">
                  <span className="metric-label">Career Health</span>
                  <span className="metric-value">78<span className="metric-sub">/100</span></span>
                </div>
                <div className="metric-item">
                  <span className="metric-label">Goal Progress</span>
                  <span className="metric-value">64%</span>
                </div>
                <div className="metric-item">
                  <span className="metric-label">Readiness</span>
                  <span className="metric-value">72%</span>
                </div>
                <div className="metric-item">
                  <span className="metric-label">Opportunity Fit</span>
                  <span className="metric-value">86%</span>
                </div>
                <div className="metric-item">
                  <span className="metric-label">Execution</span>
                  <span className="metric-value">60%</span>
                </div>
              </div>
              
              <div className="state-bottleneck-section">
                <div className="bottleneck-alert">
                  <span className="icon">⚠</span>
                  <div>
                    <strong style={{ "color": "#fff" }}>Current Bottleneck:</strong> <span style={{ "color": "rgba(255,255,255,0.85)" }}>LangGraph Production Evidence</span>
                  </div>
                </div>
                <div className="ai-priority-alert">
                  <span className="icon">⚡</span>
                  <div>
                    <strong style={{ "color": "#fff" }}>AI Priority:</strong> <span style={{ "color": "rgba(255,255,255,0.85)" }}>→ Build 1 production-grade agent workflow</span>
                  </div>
                </div>
                <div className="state-actions">
                  <button className="btn btn-primary" id="btnExecuteNextBestAction" style={{ "fontSize": "1.05rem", "padding": "0.85rem 1.75rem", "boxShadow": "0 4px 20px rgba(99, 102, 241, 0.5)", "fontWeight": "700" }}>🚀 Execute Priority Action</button>
                  <button className="btn btn-outline" id="btnHeroShowReasoning" style={{ "fontSize": "1rem", "padding": "0.8rem 1.5rem", "background": "rgba(255,255,255,0.05)", "color": "#fff", "borderColor": "rgba(255,255,255,0.2)" }}>🧠 Show Reasoning</button>
                  <button className="btn btn-outline" id="btnHeroChangeGoal" style={{ "fontSize": "1rem", "padding": "0.8rem 1.5rem", "background": "rgba(255,255,255,0.05)", "color": "#fff", "borderColor": "rgba(255,255,255,0.2)" }}>🎯 Calibrate Goal</button>
                </div>
              </div>
            </div>
          </div>

          {/*  2. DASHBOARD GRID (Clean, separated boxes)  */}
          <div className="dashboard-grid" style={{ "display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "1.75rem", "marginTop": "2rem" }}>
            
            {/*  LEFT COLUMN  */}
            <div className="dash-column" style={{ "display": "flex", "flexDirection": "column", "gap": "1.75rem" }}>
              
              {/*  APPROVAL CENTER  */}
              <div className="premium-card approval-center">
                <div className="card-header">
                  <h2>🔐 Human-in-the-Loop Approval Center</h2>
                  <span className="badge warning">3 Pending</span>
                </div>
                <p className="card-desc">Review and approve high-stakes actions before AI agents execute them.</p>
                
                <div className="approval-list spaced" id="approvalQueueList">
                  <div className="approval-item">
                    <div className="app-info">
                      <span className="app-title">Apply to Anthropic</span>
                      <span className="app-desc">Custom tailored resume ready for Senior AI Engineer role.</span>
                    </div>
                    <div className="app-actions">
                      <button className="btn btn-sm btn-success">Approve & Submit</button>
                      <button className="btn btn-sm btn-outline">Review</button>
                      <button className="btn btn-sm btn-danger-outline">Reject</button>
                    </div>
                  </div>
                  <div className="approval-item">
                    <div className="app-info">
                      <span className="app-title">Warm Referral Message</span>
                      <span className="app-desc">To Engineering Director at Stripe.</span>
                    </div>
                    <div className="app-actions">
                      <button className="btn btn-sm btn-success">Approve & Send</button>
                      <button className="btn btn-sm btn-outline">Edit Pitch</button>
                    </div>
                  </div>
                  <div className="approval-item">
                    <div className="app-info">
                      <span className="app-title">Freelance Proposal</span>
                      <span className="app-desc">For $4,500 FastAPI microservice on Upwork.</span>
                    </div>
                    <div className="app-actions">
                      <button className="btn btn-sm btn-success">Approve & Send</button>
                      <button className="btn btn-sm btn-outline">Modify</button>
                    </div>
                  </div>
                </div>
              </div>

              {/*  AI EXECUTION MATRIX  */}
              <div className="premium-card execution-matrix">
                <div className="card-header">
                  <h2>⚡ Today's AI Execution Plan</h2>
                  <span className="badge success">60% Complete</span>
                </div>
                <div className="table-responsive">
                  <table className="premium-table">
                    <thead>
                      <tr>
                        <th>Action</th>
                        <th>Reason</th>
                        <th>Status</th>
                        <th>Execute</th>
                      </tr>
                    </thead>
                    <tbody id="executionMatrixBody">
                      <tr>
                        <td><strong>Build LangGraph Agent</strong></td>
                        <td>Solves critical bottleneck</td>
                        <td><span className="status-badge ready">Ready</span></td>
                        <td><button className="btn btn-sm btn-primary">Start</button></td>
                      </tr>
                      <tr>
                        <td><strong>Review Resume v2</strong></td>
                        <td>Matched for Stripe role</td>
                        <td><span className="status-badge review">Review</span></td>
                        <td><button className="btn btn-sm btn-outline">View</button></td>
                      </tr>
                      <tr>
                        <td><strong>Complete FastAPI Module</strong></td>
                        <td>Daily upskilling goal</td>
                        <td><span className="status-badge done">Done</span></td>
                        <td><button className="btn btn-sm btn-ghost" disabled>✓</button></td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

            </div>

            {/*  RIGHT COLUMN  */}
            <div className="dash-column" style={{ "display": "flex", "flexDirection": "column", "gap": "1.75rem" }}>
              
              {/*  OPPORTUNITY RADAR  */}
              <div className="premium-card opportunity-radar">
                <div className="card-header">
                  <h2>🔎 Opportunity Intelligence Radar</h2>
                  <span className="badge primary">18 Matches</span>
                </div>
                <div className="opp-cards-spaced" id="oppItemsGrid">
                  <div className="opp-premium-card">
                    <div className="opp-main">
                      <div className="opp-title">Senior ML Engineer <span className="match-score">91% Match</span></div>
                      <div className="opp-company">Anthropic • San Francisco (Hybrid)</div>
                    </div>
                    <div className="opp-gaps">
                      <span className="tag verified">✅ Python</span>
                      <span className="tag verified">✅ FastAPI</span>
                      <span className="tag gap">❌ LangGraph</span>
                    </div>
                    <button className="btn btn-block btn-primary-light">AI Recommendation: High Probability</button>
                  </div>
                  <div className="opp-premium-card">
                    <div className="opp-main">
                      <div className="opp-title">Agentic AI Workflows <span className="match-score">88% Match</span></div>
                      <div className="opp-company">Upwork Contract • $4,500 Budget</div>
                    </div>
                    <div className="opp-gaps">
                      <span className="tag verified">✅ FastAPI</span>
                      <span className="tag verified">✅ API Design</span>
                    </div>
                    <button className="btn btn-block btn-primary-light">AI Recommendation: Easy Win</button>
                  </div>
                </div>
              </div>

              {/*  LIVE MULTI-AGENT TELEMETRY  */}
              <div className="premium-card agent-telemetry">
                <div className="card-header">
                  <h2>🤖 Multi-Agent Activity Telemetry</h2>
                  <span className="live-pulse-badge" style={{ "fontSize": "0.7rem" }}>Live Stream</span>
                </div>
                <div className="telemetry-feed">
                  <div className="log-entry">
                    <span className="log-time">Just now</span>
                    <span className="log-agent">Opportunity Agent</span>
                    <span className="log-action">Scanned 126 new roles.</span>
                  </div>
                  <div className="log-entry">
                    <span className="log-time">2m ago</span>
                    <span className="log-agent">Matching Agent</span>
                    <span className="log-action">Ranked top 18 fits for Senior ML.</span>
                  </div>
                  <div className="log-entry">
                    <span className="log-time">15m ago</span>
                    <span className="log-agent">Resume Agent</span>
                    <span className="log-action">Optimized resume for Stripe application.</span>
                  </div>
                  <div className="log-entry">
                    <span className="log-time">1h ago</span>
                    <span className="log-agent">Master Orchestrator</span>
                    <span className="log-action">Calibrated closed-loop plan. Bottleneck identified.</span>
                  </div>
                </div>
              </div>

              {/*  APPLICATION FUNNEL COMMAND CENTER  */}
              <div className="premium-card app-funnel">
                <div className="card-header">
                  <h2>📋 Application Funnel Command Center</h2>
                  <span className="badge accent">Visual Pipeline</span>
                </div>
                <div className="funnel-visual">
                  <div className="f-step"><span className="f-num">42</span><span className="f-lbl">Disc</span></div>
                  <div className="f-arrow">→</div>
                  <div className="f-step"><span className="f-num">18</span><span className="f-lbl">Short</span></div>
                  <div className="f-arrow">→</div>
                  <div className="f-step"><span className="f-num">8</span><span className="f-lbl">App</span></div>
                  <div className="f-arrow">→</div>
                  <div className="f-step highlight"><span className="f-num">3</span><span className="f-lbl">Assess</span></div>
                  <div className="f-arrow">→</div>
                  <div className="f-step"><span className="f-num">2</span><span className="f-lbl">Intv</span></div>
                </div>
                <p className="funnel-insight" style={{ "marginTop": "1rem", "fontSize": "0.85rem", "color": "var(--text-muted)", "background": "var(--bg-input)", "padding": "0.75rem", "borderRadius": "8px", "borderLeft": "3px solid var(--accent)" }}>
                  <strong>🧠 AI Rejection Learning:</strong> Adapting to low conversion from Assessment to Interview. Recommending interview prep simulations.
                </p>
              </div>

            </div>
          </div>

        </section>

        {/*  VIEW 2: PILLAR 1 — JOBS STREAM (Full-Time, Remote, Internships, Govt)  */}
        <section id="viewJobs" className="app-view" style={{ display: "none" }}>
          <div className="page-greeting">
            <h1>💼 Jobs & Opportunities Stream</h1>
            <p>Full-Time, Remote, Internships, and Government / Public Sector discovery.</p>
          </div>

          {/*  JOB STREAM CATEGORY TABS  */}
          <div className="stream-tabs-bar" id="jobStreamCategoryTabs">
            <button className="stream-tab-btn active" data-cat="all">🌐 All Roles</button>
            <button className="stream-tab-btn" data-cat="Full-Time">🏢 Full-Time</button>
            <button className="stream-tab-btn" data-cat="Remote">🌍 Remote</button>
            <button className="stream-tab-btn" data-cat="Internship">🎓 Internships</button>
            <button className="stream-tab-btn" data-cat="Government">🏛️ Government / Public</button>
          </div>

          <div className="job-finder-split">
            <div>
              <div style={{ "display": "flex", "gap": "0.5rem", "marginBottom": "1rem" }}>
                <input type="text" id="jobSearchQuery" placeholder="Search by title, company or skill..." style={{ "flex": "1" }} />
                <button className="btn btn-primary" id="btnFilterJobs">Search</button>
              </div>

              <div id="jobListCards">
                {/*  Populated dynamically  */}
              </div>
            </div>

            <div className="card" id="jobDetailPane">
              <div style={{ "display": "flex", "justifyContent": "space-between", "alignItems": "flex-start", "marginBottom": "1rem" }}>
                <div>
                  <h2 style={{ "fontSize": "1.3rem" }} id="oppDetailTitle">Select a Job Opportunity</h2>
                  <p style={{ "color": "var(--primary)", "fontWeight": "600" }} id="oppDetailCompany">Click any role to view detailed match breakdown</p>
                </div>
                <div style={{ "textAlign": "right" }}>
                  <div style={{ "fontSize": "1.5rem", "fontWeight": "800", "color": "var(--primary)" }} id="oppDetailScore">-- <span style={{ "fontSize": "0.8rem", "color": "var(--text-muted)" }}>/100</span></div>
                  <span style={{ "fontSize": "0.75rem", "color": "var(--text-muted)", "fontWeight": "600" }} id="oppDetailPriority">AI Match Score</span>
                </div>
              </div>

              <div id="jobDetailBody">
                <p style={{ "fontSize": "0.85rem", "color": "var(--text-muted)" }}>Select any opportunity from the list to view requirements, match score, and apply.</p>
              </div>

              <div style={{ "display": "flex", "gap": "0.5rem", "marginTop": "1rem" }}>
                <button className="btn btn-primary" id="btnApplyJobAction" style={{ display: "none" }}>Apply & Add to Applications</button>
                <button className="btn btn-outline" id="btnSaveJobAction" style={{ display: "none" }}>Save Job</button>
              </div>
            </div>
          </div>
        </section>

        {/*  VIEW 3: PILLAR 2 — LEARNING & SKILLS STREAM  */}
        <section id="viewLearning" className="app-view" style={{ display: "none" }}>
          <div className="page-greeting">
            <h1>📚 Learning, Skills & Certifications Stream</h1>
            <p>Personalized skill gap roadmaps, interactive challenges, and project portfolios.</p>
          </div>

          <div style={{ "display": "grid", "gridTemplateColumns": "1fr 320px", "gap": "1.25rem" }}>
            <div className="card">
              <div className="card-title">🎯 Personalized Skill Gap Roadmap</div>
              <h3 style={{ "fontSize": "1.1rem", "fontWeight": "700", "marginBottom": "1rem" }} id="skillPathTitle">Engineering Progression Path</h3>
              
              <div className="roadmap-timeline" id="skillPathTimeline">
                {/*  Rendered dynamically  */}
              </div>
            </div>

            <div style={{ "display": "flex", "flexDirection": "column", "gap": "1.25rem" }}>
              <div className="card">
                <div className="card-title">Roadmap Velocity</div>
                <div style={{ "textAlign": "center", "margin": "1.5rem 0" }}>
                  <div style={{ "fontSize": "2.8rem", "fontWeight": "700", "color": "var(--primary)" }} id="skillPathOverallPct">0%</div>
                  <p style={{ "fontSize": "0.8rem", "color": "var(--text-muted)" }}>Competency Score</p>
                </div>
                <div style={{ "background": "var(--bg-input)", "padding": "1rem", "borderRadius": "var(--radius-sm)", "border": "1px solid var(--border-color)" }}>
                  <span style={{ "fontSize": "0.75rem", "color": "var(--primary)", "fontWeight": "700", "textTransform": "uppercase" }}>Current Priority</span>
                  <h6 style={{ "fontSize": "0.9rem", "marginTop": "0.2rem" }} id="skillPathCurrentFocus">Add skills to generate custom modules</h6>
                </div>
              </div>

              <div className="card">
                <div className="card-title">Certifications & Credentials</div>
                <p style={{ "fontSize": "0.82rem", "color": "var(--text-muted)" }}>Verified credentials boost your ATS Match Score by +25%.</p>
                <div id="certListContainer" style={{ "display": "flex", "flexDirection": "column", "gap": "0.5rem", "marginTop": "0.75rem" }}>
                  {/*  Dynamic certs  */}
                </div>
              </div>
            </div>
          </div>
        </section>

        {/*  VIEW 4: PILLAR 3 — BUSINESS & FREELANCE STREAM  */}
        <section id="viewBusiness" className="app-view" style={{ display: "none" }}>
          <div className="page-greeting" style={{ "display": "flex", "justifyContent": "space-between", "alignItems": "flex-start" }}>
            <div>
              <h1>🚀 Business, Freelance & Client Gigs Stream</h1>
              <p>High-ticket gigs, client acquisition, rate calculator, and grounded AI proposal generation.</p>
            </div>
            <button className="btn btn-primary" id="btnOpenAddGigModal">+ Post Client Gig</button>
          </div>

          {/*  FREELANCE METRICS  */}
          <div className="metrics-row" style={{ "marginBottom": "1.5rem" }}>
            <div className="stat-card">
              <div className="stat-info">
                <span>Active Gigs</span>
                <div className="stat-value" id="valBusinessGigsCount">0</div>
                <div className="stat-trend">High-Ticket Opportunities</div>
              </div>
              <div style={{ "fontSize": "1.8rem" }}>💼</div>
            </div>

            <div className="stat-card">
              <div className="stat-info">
                <span>Client Pipeline</span>
                <div className="stat-value" id="valBusinessPitchesCount">0</div>
                <div className="stat-trend">Proposals Pitched</div>
              </div>
              <div style={{ "fontSize": "1.8rem" }}>📬</div>
            </div>

            <div className="stat-card">
              <div className="stat-info">
                <span>Recommended Hourly Rate</span>
                <div className="stat-value" id="valCalculatedRate">$85/hr</div>
                <div className="stat-trend">Market Value Calculator</div>
              </div>
              <div style={{ "fontSize": "1.8rem" }}>💰</div>
            </div>
          </div>

          {/*  BUSINESS SPLIT: GIG DISCOVERY & CLIENT CRM  */}
          <div style={{ "display": "grid", "gridTemplateColumns": "2fr 1fr", "gap": "1.25rem" }}>
            
            {/*  LEFT: GIG OPPORTUNITIES & 1-CLICK PROPOSAL GENERATOR  */}
            <div className="card">
              <div className="card-title">🎯 High-Ticket Freelance & Consulting Opportunities</div>
              <div id="freelanceGigsContainer" style={{ "display": "flex", "flexDirection": "column", "gap": "0.85rem" }}>
                {/*  Populated dynamically  */}
              </div>
            </div>

            {/*  RIGHT: CLIENT PROPOSAL WORKSPACE & CRM  */}
            <div style={{ "display": "flex", "flexDirection": "column", "gap": "1.25rem" }}>
              <div className="card">
                <div className="card-title">⚡ AI Grounded Proposal Engine</div>
                <p style={{ "fontSize": "0.82rem", "color": "var(--text-muted)", "lineHeight": "1.4", "marginBottom": "0.75rem" }}>
                  Generate tailored, evidence-backed client proposals using your verified skills and portfolio projects.
                </p>
                <button className="btn btn-primary btn-block" id="btnQuickGenerateProposal">Generate Proposal for Selected Gig</button>
              </div>

              <div className="card">
                <div className="card-title">📊 Client Deal Pipeline</div>
                <div id="clientPipelineList" style={{ "display": "flex", "flexDirection": "column", "gap": "0.5rem" }}>
                  {/*  Dynamic deals  */}
                </div>
              </div>
            </div>

          </div>
        </section>

        {/*  VIEW 5: DECISION ENGINE / COMMAND CENTER  */}
        <section id="viewCommandCenter" className="app-view" style={{ display: "none" }}>
          <div className="page-greeting">
            <h1>🧠 Autonomous AI Decision Engine & Orchestrator</h1>
            <p>Closed-loop multi-agent reasoning answering "What Should I Do Next?".</p>
          </div>

          <div style={{ "display": "grid", "gridTemplateColumns": "2fr 1fr", "gap": "1.25rem" }}>
            <div className="card chat-box-card">
              <div className="card-title">💬 Master Orchestrator Conversational Interface</div>
              <div className="chat-messages-area" id="commandCenterMessages" style={{ "height": "280px" }}>
                <div className="chat-msg-bubble ai" id="commandCenterWelcomeMsg">
                  <strong>🧠 Master Career Orchestrator</strong><br />
                  Welcome to your AI Career Agent Ecosystem. I coordinate across Jobs, Learning, and Freelancing to calculate your highest-value Next Best Action. Ask me anything!
                </div>
              </div>

              <form id="commandCenterForm" className="chat-input-row">
                <input type="text" id="commandCenterInput" placeholder="Command your AI Career OS..." required />
                <button type="submit" className="btn btn-primary">Execute</button>
              </form>
            </div>

            <div className="card">
              <div className="card-title">🌐 Active Multi-Agent Nodes</div>
              <div style={{ "fontSize": "0.78rem", "display": "flex", "flexDirection": "column", "gap": "0.45rem" }}>
                <div>🟢 Jobs & Application Agent (Online)</div>
                <div>🟢 Learning & Skill Graph Agent (Online)</div>
                <div>🟢 Business & Freelance Proposal Agent (Online)</div>
                <div>🟢 Memory & Feedback Loop Agent (Online)</div>
                <div>🟢 Closed-Loop Adaptation Strategy (Online)</div>
              </div>
            </div>
          </div>
        </section>

        {/*  VIEW 6: RESUME INTELLIGENCE STUDIO & ATS DIAGNOSTIC ENGINE  */}
        <section id="viewResumes" className="app-view" style={{ display: "none" }}>
          <div className="page-greeting" style={{ "display": "flex", "justifyContent": "space-between", "alignItems": "flex-start", "flexWrap": "wrap", "gap": "0.75rem" }}>
            <div>
              <h1 style={{ "display": "flex", "alignItems": "center", "gap": "0.5rem" }}>📄 Resume Intelligence & ATS Studio</h1>
              <p>Build, tailor, and score production-grade ATS resumes grounded in real evidence.</p>
            </div>
            <div style={{ "display": "flex", "gap": "0.5rem", "flexWrap": "wrap" }}>
              <button className="btn btn-outline" id="btnResumeCopyText" title="Copy clean text formatted for ATS submission">📋 Copy Raw Text</button>
              <button className="btn btn-outline" id="btnResumePreview" title="Toggle Fullscreen View">👁️ Preview Fullscreen</button>
              <button className="btn btn-primary" id="btnResumeDownload" title="Print or Save PDF">📥 Download ATS PDF</button>
            </div>
          </div>

          <div className="resume-studio-layout">
            
            {/*  LEFT COLUMN: INTERACTIVE RESUME STUDIO EDITOR  */}
            <div className="resume-editor-card">
              <div style={{ "display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "0.75rem" }}>
                <span style={{ "fontWeight": "700", "fontSize": "0.9rem", "color": "var(--text-main)" }}>✏️ Resume Studio Editor</span>
                <button className="btn btn-outline btn-sm" id="btnResetResumeDefault" style={{ "fontSize": "0.72rem", "padding": "0.2rem 0.5rem" }}>Reset</button>
              </div>

              {/*  EDITOR SECTION TABS  */}
              <div className="resume-editor-tabs" id="resumeEditorTabs">
                <button className="resume-tab-btn active" data-tab="tabResBasics">👤 Basics</button>
                <button className="resume-tab-btn" data-tab="tabResSummary">✨ Summary</button>
                <button className="resume-tab-btn" data-tab="tabResExp">💼 Work</button>
                <button className="resume-tab-btn" data-tab="tabResEdu">🎓 Education</button>
                <button className="resume-tab-btn" data-tab="tabResSkills">⚡ Skills</button>
                <button className="resume-tab-btn" data-tab="tabResTailor">🎯 Tailor</button>
              </div>

              {/*  TAB 1: BASICS  */}
              <div className="resume-tab-panel active" id="tabResBasics">
                <div className="form-group" style={{ "marginBottom": "0.6rem" }}>
                  <label style={{ "fontSize": "0.76rem" }}>Full Name</label>
                  <input type="text" id="inputResName" placeholder="e.g. Alex Johnson" style={{ "fontSize": "0.82rem", "padding": "0.45rem 0.65rem" }} />
                </div>
                <div className="form-group" style={{ "marginBottom": "0.6rem" }}>
                  <label style={{ "fontSize": "0.76rem" }}>Professional Headline / Target Role</label>
                  <input type="text" id="inputResTitle" placeholder="e.g. Senior Backend Engineer" style={{ "fontSize": "0.82rem", "padding": "0.45rem 0.65rem" }} />
                </div>
                <div className="form-group" style={{ "marginBottom": "0.6rem" }}>
                  <label style={{ "fontSize": "0.76rem" }}>Email Address</label>
                  <input type="email" id="inputResEmail" placeholder="alex.johnson@example.com" style={{ "fontSize": "0.82rem", "padding": "0.45rem 0.65rem" }} />
                </div>
                <div className="form-group" style={{ "marginBottom": "0.6rem" }}>
                  <label style={{ "fontSize": "0.76rem" }}>Phone Number</label>
                  <input type="text" id="inputResPhone" placeholder="+1 (555) 234-5678" style={{ "fontSize": "0.82rem", "padding": "0.45rem 0.65rem" }} />
                </div>
                <div className="form-group" style={{ "marginBottom": "0.6rem" }}>
                  <label style={{ "fontSize": "0.76rem" }}>Location</label>
                  <input type="text" id="inputResLocation" placeholder="San Francisco, CA (or Remote)" style={{ "fontSize": "0.82rem", "padding": "0.45rem 0.65rem" }} />
                </div>
                <div className="form-group" style={{ "marginBottom": "0.6rem" }}>
                  <label style={{ "fontSize": "0.76rem" }}>LinkedIn Profile URL / Handle</label>
                  <input type="text" id="inputResLinkedIn" placeholder="linkedin.com/in/alex-johnson" style={{ "fontSize": "0.82rem", "padding": "0.45rem 0.65rem" }} />
                </div>
                <div className="form-group" style={{ "marginBottom": "0.6rem" }}>
                  <label style={{ "fontSize": "0.76rem" }}>GitHub / Portfolio URL</label>
                  <input type="text" id="inputResGitHub" placeholder="github.com/alex-dev" style={{ "fontSize": "0.82rem", "padding": "0.45rem 0.65rem" }} />
                </div>
              </div>

              {/*  TAB 2: SUMMARY  */}
              <div className="resume-tab-panel" id="tabResSummary">
                <div style={{ "display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "0.4rem" }}>
                  <label style={{ "fontSize": "0.76rem", "fontWeight": "600" }}>Executive Summary</label>
                  <button className="btn btn-outline btn-sm" id="btnAiEnhanceSummary" style={{ "fontSize": "0.72rem", "padding": "0.2rem 0.45rem", "color": "var(--primary)" }}>✨ AI STAR Polish</button>
                </div>
                <textarea id="inputResSummary" rows="6" placeholder="Engineered high-throughput distributed systems..." style={{ "fontSize": "0.82rem", "width": "100%", "lineHeight": "1.4", "padding": "0.5rem" }}></textarea>
                <div style={{ "fontSize": "0.72rem", "color": "var(--text-muted)", "marginTop": "0.35rem" }}>
                  💡 <strong>ATS Rule:</strong> Include your core domain, years of hands-on stack experience, and 1 standout quantified achievement.
                </div>
              </div>

              {/*  TAB 3: WORK EXPERIENCE  */}
              <div className="resume-tab-panel" id="tabResExp">
                <div style={{ "display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "0.5rem" }}>
                  <span style={{ "fontSize": "0.78rem", "fontWeight": "700" }}>Experience Entries</span>
                  <button className="btn btn-primary btn-sm" id="btnAddExpEntry" style={{ "fontSize": "0.72rem", "padding": "0.25rem 0.55rem" }}>+ Add Position</button>
                </div>
                <div id="editorExpList" style={{ "display": "flex", "flexDirection": "column", "gap": "0.65rem" }}>
                  {/*  Dynamic Exp Inputs  */}
                </div>
              </div>

              {/*  TAB 4: EDUCATION  */}
              <div className="resume-tab-panel" id="tabResEdu">
                <div style={{ "display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "0.5rem" }}>
                  <span style={{ "fontSize": "0.78rem", "fontWeight": "700" }}>Education & Certifications</span>
                  <button className="btn btn-primary btn-sm" id="btnAddEduEntry" style={{ "fontSize": "0.72rem", "padding": "0.25rem 0.55rem" }}>+ Add Degree</button>
                </div>
                <div id="editorEduList" style={{ "display": "flex", "flexDirection": "column", "gap": "0.65rem" }}>
                  {/*  Dynamic Edu Inputs  */}
                </div>
              </div>

              {/*  TAB 5: SKILLS  */}
              <div className="resume-tab-panel" id="tabResSkills">
                <div className="form-group" style={{ "marginBottom": "0.6rem" }}>
                  <label style={{ "fontSize": "0.76rem" }}>Languages & Core</label>
                  <input type="text" id="inputResSkillsLang" placeholder="Python, Go, TypeScript, SQL" style={{ "fontSize": "0.82rem", "padding": "0.45rem 0.65rem" }} />
                </div>
                <div className="form-group" style={{ "marginBottom": "0.6rem" }}>
                  <label style={{ "fontSize": "0.76rem" }}>Frameworks & Libraries</label>
                  <input type="text" id="inputResSkillsFrameworks" placeholder="FastAPI, Django, React, LangChain, PyTorch" style={{ "fontSize": "0.82rem", "padding": "0.45rem 0.65rem" }} />
                </div>
                <div className="form-group" style={{ "marginBottom": "0.6rem" }}>
                  <label style={{ "fontSize": "0.76rem" }}>Cloud, DevOps & Databases</label>
                  <input type="text" id="inputResSkillsCloud" placeholder="Docker, Kubernetes, AWS, PostgreSQL, Redis, Kafka" style={{ "fontSize": "0.82rem", "padding": "0.45rem 0.65rem" }} />
                </div>
                <button className="btn btn-outline btn-sm btn-block" id="btnSyncVerifiedSkills" style={{ "fontSize": "0.75rem", "marginTop": "0.5rem" }}>🔄 Sync from Evidence Graph</button>
              </div>

              {/*  TAB 6: JOB TAILORING & KEYWORDS  */}
              <div className="resume-tab-panel" id="tabResTailor">
                <label style={{ "fontSize": "0.76rem", "fontWeight": "600" }}>Select Target Job to Optimize For</label>
                <select id="selectTargetJobTailor" style={{ "fontSize": "0.82rem", "width": "100%", "padding": "0.45rem", "marginTop": "0.25rem", "marginBottom": "0.75rem" }}>
                  <option value="0">Anthropic — AI / LLM Systems Engineer</option>
                  <option value="1">Stripe — Senior Backend Engineer (Distributed)</option>
                  <option value="2">Scale AI — AI Pipeline Engineer</option>
                  <option value="3">Datadog — Distributed Systems Engineer</option>
                </select>
                <button className="btn btn-primary btn-sm btn-block" id="btnRunAITailorScan">⚡ Run ATS Keyword Alignment</button>
                <div id="tailorScanResults" style={{ "marginTop": "0.75rem", "fontSize": "0.76rem", "color": "var(--text-muted)" }}>
                  {/*  Match results rendered dynamically  */}
                </div>
              </div>

            </div>

            {/*  CENTER COLUMN: ATS DOCUMENT CANVAS  */}
            <div className="resume-canvas-wrapper">
              
              {/*  TEMPLATE SWITCHER TOOLBAR  */}
              <div className="resume-template-bar">
                <div style={{ "display": "flex", "gap": "0.4rem", "alignItems": "center" }}>
                  <span style={{ "fontSize": "0.78rem", "fontWeight": "700", "color": "var(--text-muted)" }}>ATS Style:</span>
                  <button className="template-pill-btn active" data-template="template-modern">💼 Modern Tech</button>
                  <button className="template-pill-btn" data-template="template-harvard">🏛️ Harvard Executive</button>
                  <button className="template-pill-btn" data-template="template-minimal">⚡ Silicon Valley</button>
                </div>
                <div style={{ "fontSize": "0.72rem", "color": "#94a3b8" }}>Standard A4 / Letter ATS-Safe</div>
              </div>

              {/*  PRINTABLE / RENDERED RESUME CANVAS  */}
              <div className="resume-paper-canvas template-modern" id="resumePaperCanvas">
                
                {/*  HEADER  */}
                <div id="canvasHeader">
                  <div className="res-header-name" id="cvName">Alex Johnson</div>
                  <div className="res-header-title" id="cvTitle">Senior Backend & AI Systems Engineer</div>
                  <div className="res-header-contact" id="cvContact">
                    <span id="cvEmail">alex.johnson@example.com</span> •
                    <span id="cvPhone">+1 (555) 234-5678</span> •
                    <span id="cvLocation">San Francisco, CA</span> •
                    <span id="cvLinkedIn">linkedin.com/in/alex-johnson</span> •
                    <span id="cvGitHub">github.com/alex-dev</span>
                  </div>
                </div>

                {/*  PROFESSIONAL SUMMARY  */}
                <div id="canvasSummarySection">
                  <div className="res-section-title">Professional Summary</div>
                  <p id="cvSummary" style={{ "fontSize": "0.84rem", "lineHeight": "1.45", "color": "#334155", "marginBottom": "0.75rem" }}>
                    High-impact Software Engineer with 4+ years of experience architecting distributed backend services, high-throughput APIs, and multi-agent AI pipelines. Proven track record reducing latency by 42% and managing production deployments serving 50k+ daily users.
                  </p>
                </div>

                {/*  TECHNICAL SKILLS  */}
                <div id="canvasSkillsSection">
                  <div className="res-section-title">Technical Skills</div>
                  <div style={{ "fontSize": "0.84rem", "lineHeight": "1.5", "color": "#334155", "marginBottom": "0.75rem" }}>
                    <div><strong>Languages & Core:</strong> <span id="cvSkillsLang">Python, TypeScript, SQL, Go</span></div>
                    <div><strong>Frameworks:</strong> <span id="cvSkillsFrameworks">FastAPI, Django, React, LangChain, PyTorch</span></div>
                    <div><strong>Infrastructure & Tools:</strong> <span id="cvSkillsCloud">Docker, PostgreSQL, Redis, AWS, Git, Kafka</span></div>
                  </div>
                </div>

                {/*  WORK EXPERIENCE  */}
                <div id="canvasExperienceSection">
                  <div className="res-section-title">Professional Experience</div>
                  <div id="cvExperienceList">
                    {/*  Dynamic Experience Nodes  */}
                  </div>
                </div>

                {/*  KEY PROJECTS (PORTFOLIO EVIDENCE)  */}
                <div id="canvasProjectsSection">
                  <div className="res-section-title">Key Engineering Projects</div>
                  <div id="cvProjectsList">
                    {/*  Dynamic Projects  */}
                  </div>
                </div>

                {/*  EDUCATION  */}
                <div id="canvasEducationSection">
                  <div className="res-section-title">Education & Certifications</div>
                  <div id="cvEducationList">
                    {/*  Dynamic Education  */}
                  </div>
                </div>

              </div>

            </div>

            {/*  RIGHT COLUMN: LIVE ATS DIAGNOSTIC SCORER  */}
            <div className="ats-diagnostic-card">
              <div style={{ "fontWeight": "700", "fontSize": "0.95rem", "marginBottom": "0.75rem", "color": "var(--text-main)" }}>
                📊 Live ATS Diagnostic Scorer
              </div>

              {/*  REAL ATS SCORE METER  */}
              <div className="ats-score-meter-box">
                <div style={{ "fontSize": "2.5rem", "fontWeight": "800", "color": "var(--primary)", "lineHeight": "1" }} id="liveAtsScoreVal">0</div>
                <div style={{ "fontSize": "0.75rem", "fontWeight": "700", "marginTop": "0.35rem", "color": "var(--text-muted)" }} id="liveAtsScoreLabel">Evaluating Content...</div>
              </div>

              {/*  4 REAL ATS DIMENSIONS  */}
              <div style={{ "marginBottom": "1.25rem" }}>
                <div className="ats-metric-dim-row">
                  <div className="dim-head"><span>Completeness & Layout</span><strong id="dimCompletenessVal">0/25</strong></div>
                  <div className="progress-track"><div className="progress-fill" id="barDimCompleteness" style={{ "width": "0%" }}></div></div>
                </div>
                <div className="ats-metric-dim-row">
                  <div className="dim-head"><span>Strong Action Verbs</span><strong id="dimActionVerbsVal">0/25</strong></div>
                  <div className="progress-track"><div className="progress-fill" id="barDimActionVerbs" style={{ "width": "0%" }}></div></div>
                </div>
                <div className="ats-metric-dim-row">
                  <div className="dim-head"><span>Quantified Impact Metrics</span><strong id="dimMetricsVal">0/25</strong></div>
                  <div className="progress-track"><div className="progress-fill" id="barDimMetrics" style={{ "width": "0%" }}></div></div>
                </div>
                <div className="ats-metric-dim-row">
                  <div className="dim-head"><span>Target Skill Alignment</span><strong id="dimKeywordsVal">0/25</strong></div>
                  <div className="progress-track"><div className="progress-fill" id="barDimKeywords" style={{ "width": "0%" }}></div></div>
                </div>
              </div>

              {/*  DIAGNOSTIC CHECKLIST  */}
              <div style={{ "fontSize": "0.8rem", "fontWeight": "700", "marginBottom": "0.4rem", "color": "var(--text-main)" }}>
                🔍 ATS Parsing Audit Checklist
              </div>
              <div id="atsAuditChecklist" style={{ "display": "flex", "flexDirection": "column", "marginBottom": "1rem" }}>
                {/*  Dynamically audited checklist  */}
              </div>

              {/*  1-CLICK QUICK FIX BUTTONS  */}
              <div style={{ "display": "flex", "flexDirection": "column", "gap": "0.4rem" }}>
                <button className="btn btn-outline btn-sm btn-block" id="btnAutoInjectMetrics" style={{ "fontSize": "0.75rem" }}>⚡ Auto-Inject Quantified Metrics</button>
                <button className="btn btn-primary btn-sm btn-block" id="btnSyncProfileToResume" style={{ "fontSize": "0.75rem" }}>🔄 Load Full Profile to Resume</button>
              </div>

            </div>

          </div>
        </section>

        {/*  VIEW 7: PROJECTS PORTFOLIO  */}

        {/*  VIEW 7: PROJECTS PORTFOLIO  */}
        <section id="viewProjects" className="app-view" style={{ display: "none" }}>
          <div className="page-greeting" style={{ "display": "flex", "justifyContent": "space-between", "alignItems": "flex-start" }}>
            <div>
              <h1>Projects & Portfolio Evidence</h1>
              <p>Track and showcase real-world engineering project work.</p>
            </div>
            <button className="btn btn-primary" id="btnOpenAddProjectModal">+ Add Project</button>
          </div>

          <div id="projectsListContainer" style={{ "display": "grid", "gridTemplateColumns": "repeat(auto-fill, minmax(320px, 1fr))", "gap": "1.25rem" }}>
            {/*  Rendered dynamically  */}
          </div>
        </section>

        {/*  VIEW 8: KANBAN APPLICATIONS BOARD  */}
        <section id="viewKanban" className="app-view" style={{ display: "none" }}>
          <div className="page-greeting" style={{ "display": "flex", "justifyContent": "space-between", "alignItems": "flex-start" }}>
            <div>
              <h1>Applications Pipeline Board</h1>
              <p>Organize and track your active job applications across all stages.</p>
            </div>
            <button className="btn btn-primary" id="btnOpenAddAppModal">+ Add Application</button>
          </div>

          <div style={{ "display": "flex", "gap": "1rem", "overflowX": "auto", "paddingBottom": "1rem" }} id="kanbanBoardContainer">
            <div className="kanban-column" id="colSaved">
              <div className="kanban-column-header"><span>Saved</span><span className="pill" id="countSaved">0</span></div>
              <div className="kanban-card-list" id="kanbanSavedList"></div>
            </div>
            <div className="kanban-column" id="colApplied">
              <div className="kanban-column-header"><span>Applied</span><span className="pill" id="countApplied">0</span></div>
              <div className="kanban-card-list" id="kanbanAppliedList"></div>
            </div>
            <div className="kanban-column" id="colInterview">
              <div className="kanban-column-header"><span>Interview</span><span className="pill" id="countInterview">0</span></div>
              <div className="kanban-card-list" id="kanbanInterviewList"></div>
            </div>
            <div className="kanban-column" id="colOffer">
              <div className="kanban-column-header"><span>Offer</span><span className="pill" id="countOffer">0</span></div>
              <div className="kanban-card-list" id="kanbanOfferList"></div>
            </div>
          </div>
        </section>

        {/*  VIEW 9: INTERVIEW PREP  */}
        <section id="viewInterviews" className="app-view" style={{ display: "none" }}>
          <div className="page-greeting">
            <h1>Interview Preparation & Practice</h1>
            <p>Sharpen your technical, behavioral, and system design readiness.</p>
          </div>
          <div className="card">
            <div className="card-title">AI Mock Interview Generator</div>
            <p style={{ "fontSize": "0.85rem", "color": "var(--text-muted)", "marginBottom": "1rem" }}>Practice tailored interview scenarios based on your target role and skills.</p>
            <button className="btn btn-primary" id="btnStartMockInterview">Start AI Mock Interview Session</button>
          </div>
        </section>

        {/*  VIEW 10: AI COACH  */}
        <AICoach />

        {/*  VIEW 11: NETWORKING & CRM  */}
        <section id="viewNetwork" className="app-view" style={{ display: "none" }}>
          <div className="page-greeting" style={{ "display": "flex", "justifyContent": "space-between", "alignItems": "flex-start" }}>
            <div>
              <h1>🌐 Networking CRM & Personal Brand</h1>
              <p>Manage key industry connections and referral outreach.</p>
            </div>
            <button className="btn btn-primary" id="btnOpenAddContactModal">+ Add Contact</button>
          </div>

          <div className="card">
            <div className="card-title">👥 Network CRM Directory</div>
            <div id="networkDirectoryContainer" style={{ "display": "flex", "flexDirection": "column", "gap": "0.6rem" }}>
              {/*  Rendered dynamically  */}
            </div>
          </div>
        </section>

        {/*  VIEW 12: OFFERS & RETAINERS  */}
        <section id="viewOffers" className="app-view" style={{ display: "none" }}>
          <div className="page-greeting">
            <h1>Offer & Retainer Management</h1>
            <p>Evaluate job offers, client retainer contracts, and compensation packages.</p>
          </div>
          <div className="card" id="offersCard">
            <div className="card-title">Active Offers & Retainers</div>
            <div id="offersListContainer">
              <div className="empty-state">
                <div className="empty-state-icon">💰</div>
                <div className="empty-state-text">No active offers or retainers recorded yet.</div>
              </div>
            </div>
          </div>
        </section>

        {/*  VIEW 13: ANALYTICS  */}
        <section id="viewAnalytics" className="app-view" style={{ display: "none" }}>
          <div className="page-greeting">
            <h1>Career Performance & Flywheel Analytics</h1>
            <p>Track your closed-loop conversion rates across all 3 pillars.</p>
          </div>

          <div className="metrics-row">
            <div className="stat-card">
              <div className="stat-info">
                <span>Skills Tracked</span>
                <div className="stat-value" id="analyticsSkills">0</div>
                <div className="stat-trend">Evidence Base</div>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-info">
                <span>Job Applications</span>
                <div className="stat-value" id="analyticsApps">0</div>
                <div className="stat-trend">Pillar 1</div>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-info">
                <span>Freelance Deals</span>
                <div className="stat-value" id="analyticsFreelance">0</div>
                <div className="stat-trend">Pillar 3</div>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-info">
                <span>Closed Decisions</span>
                <div className="stat-value" id="analyticsDecisions">0</div>
                <div className="stat-trend">Flywheel Loops</div>
              </div>
            </div>
          </div>
        </section>

        {/*  VIEW 14: CONNECTED ACCOUNTS & DATA INTEGRATIONS HUB  */}
        <section id="viewIntegrations" className="app-view" style={{ display: "none" }}>
          <div className="page-greeting" style={{ "display": "flex", "justifyContent": "space-between", "alignItems": "flex-start", "flexWrap": "wrap", "gap": "0.75rem" }}>
            <div>
              <h1 style={{ "display": "flex", "alignItems": "center", "gap": "0.5rem" }}>🔌 Connected Accounts & Data Integrations</h1>
              <p>Connect your developer platforms, coding practice hubs, and job mailboxes to power real-time AI telemetry.</p>
            </div>
            <div style={{ "display": "flex", "gap": "0.5rem" }}>
              <button className="btn btn-outline" id="btnSyncAllIntegrations">🔄 Sync All Accounts</button>
            </div>
          </div>

          {/*  Cards are rendered from GET /api/v1/integrations — the provider
               catalog, connection state and metrics all come from the backend,
               so there is no hardcoded card, statistic or status here.  */}
          <div className="integration-grid" id="integrationCardsGrid">
            <div className="empty-state" style={{ gridColumn: "1 / -1", padding: "2.5rem 1rem" }}>
              <div className="pulse-dot" style={{ display: "inline-block", marginRight: "0.5rem" }}></div>
              <span style={{ fontSize: "0.9rem", color: "var(--text-muted)" }}>Loading connected accounts...</span>
            </div>
          </div>
        </section>


        {/*  VIEW 15: SETTINGS  */}
        <section id="viewSettings" className="app-view" style={{ display: "none" }}>
          <div className="page-greeting">
            <h1>Account & Career Profile Settings</h1>
            <p>Configure your personal profile, target career role, and preferences.</p>
          </div>
          <div className="card" style={{ maxWidth: "540px" }}>
            <form id="formSettings">
              <div className="form-group">
                <label>Full Name</label>
                <input type="text" id="settingName" placeholder="Your Name" required />
              </div>
              <div className="form-group">
                <label>Email Address</label>
                <input type="email" id="settingEmail" placeholder="email@example.com" disabled style={{ "opacity": "0.7" }} />
              </div>
              <div className="form-group">
                <label>Target Role Preference</label>
                <input type="text" id="settingTargetRole" placeholder="e.g. Senior Backend Engineer, Data Scientist, Full Stack Developer" />
              </div>
              <div className="form-group">
                <label>Target Location</label>
                <input type="text" id="settingTargetLocation" placeholder="e.g. Remote / New York / Bengaluru / Hybrid" />
              </div>
              <button type="submit" className="btn btn-primary">Save Settings</button>
            </form>
          </div>
        </section>

      </main>
    </div>
  </div>

  {/*  MODAL: ADD APPLICATION  */}
  <div id="modalAddApp" className="modal-overlay" style={{ display: "none" }}>
    <div className="modal-content" style={{ "maxWidth": "440px" }}>
      <div className="modal-header">
        <h3 style={{ "fontSize": "1.1rem", "fontWeight": "700" }}>Add Job Application</h3>
        <button className="btn-close" id="btnCloseAddAppModal">✕</button>
      </div>
      <form id="formAddApplication">
        <div className="form-group">
          <label>Company Name</label>
          <input type="text" id="appCompany" placeholder="e.g. Google, Stripe, Microsoft" required />
        </div>
        <div className="form-group">
          <label>Job Title</label>
          <input type="text" id="appRole" placeholder="e.g. Senior Backend Engineer" required />
        </div>
        <div className="form-group">
          <label>Stage / Status</label>
          <select id="appStatus">
            <option value="Saved">Saved</option>
            <option value="Applied" selected>Applied</option>
            <option value="Interview">Interview</option>
            <option value="Offer">Offer</option>
          </select>
        </div>
        <button type="submit" className="btn btn-primary btn-block">Add Application</button>
      </form>
    </div>
  </div>

  {/*  MODAL: ADD PROJECT  */}
  <div id="modalAddProject" className="modal-overlay" style={{ display: "none" }}>
    <div className="modal-content" style={{ "maxWidth": "460px" }}>
      <div className="modal-header">
        <h3 style={{ "fontSize": "1.1rem", "fontWeight": "700" }}>Add Portfolio Project</h3>
        <button className="btn-close" id="btnCloseAddProjectModal">✕</button>
      </div>
      <form id="formAddProject">
        <div className="form-group">
          <label>Project Title</label>
          <input type="text" id="projTitle" placeholder="e.g. Distributed Cache & KV Store" required />
        </div>
        <div className="form-group">
          <label>Description & Evidence</label>
          <textarea id="projDesc" rows="3" placeholder="Engineered high throughput API pipeline using Python, Redis and PostgreSQL..." required></textarea>
        </div>
        <div className="form-group">
          <label>Technologies Used (comma separated)</label>
          <input type="text" id="projTech" placeholder="e.g. Python, FastAPI, Docker, PostgreSQL" />
        </div>
        <button type="submit" className="btn btn-primary btn-block">Save Project</button>
      </form>
    </div>
  </div>

  {/*  MODAL: ADD CONTACT  */}
  <div id="modalAddContact" className="modal-overlay" style={{ display: "none" }}>
    <div className="modal-content" style={{ "maxWidth": "440px" }}>
      <div className="modal-header">
        <h3 style={{ "fontSize": "1.1rem", "fontWeight": "700" }}>Add Network Connection</h3>
        <button className="btn-close" id="btnCloseAddContactModal">✕</button>
      </div>
      <form id="formAddContact">
        <div className="form-group">
          <label>Contact Name</label>
          <input type="text" id="contactName" placeholder="e.g. Sarah Connor" required />
        </div>
        <div className="form-group">
          <label>Company</label>
          <input type="text" id="contactCompany" placeholder="e.g. Stripe" required />
        </div>
        <div className="form-group">
          <label>Role</label>
          <input type="text" id="contactRole" placeholder="e.g. Engineering Director" required />
        </div>
        <div className="form-group">
          <label>Relationship Tier</label>
          <select id="contactTier">
            <option value="WARM">Warm (Alumni / Ex-Colleague)</option>
            <option value="RECRUITER">Recruiter</option>
            <option value="COLD">New Connection</option>
          </select>
        </div>
        <button type="submit" className="btn btn-primary btn-block">Save Contact</button>
      </form>
    </div>
  </div>

  {/*  MODAL: ADD FREELANCE GIG  */}
  <div id="modalAddGig" className="modal-overlay" style={{ display: "none" }}>
    <div className="modal-content" style={{ maxWidth: "480px" }}>
      <div className="modal-header">
        <h3 style={{ "fontSize": "1.1rem", "fontWeight": "700" }}>Add Client Gig / Freelance Contract</h3>
        <button className="btn-close" id="btnCloseAddGigModal">✕</button>
      </div>
      <form id="formAddGig">
        <div className="form-group">
          <label>Client / Company Name</label>
          <input type="text" id="gigClient" placeholder="e.g. FinTech Global" required />
        </div>
        <div className="form-group">
          <label>Project Scope / Title</label>
          <input type="text" id="gigTitle" placeholder="e.g. Scalable FastAPI Microservice & Vector DB" required />
        </div>
        <div className="form-group">
          <label>Budget / Retainer</label>
          <input type="text" id="gigBudget" placeholder="e.g. $4,500 fixed or $90/hr" required />
        </div>
        <div className="form-group">
          <label>Required Tech Stack (comma separated)</label>
          <input type="text" id="gigTech" placeholder="e.g. Python, FastAPI, Docker, PGVector" />
        </div>
        <button type="submit" className="btn btn-primary btn-block">Post Gig to Pipeline</button>
      </form>
    </div>
  </div>
    {/*  MODAL: AI PROPOSAL VIEWER  */}
  <div id="modalProposal" className="modal-overlay" style={{ display: "none" }}>
    <div className="modal-content" style={{ "maxWidth": "600px" }}>
      <div className="modal-header">
        <h3 style={{ "fontSize": "1.1rem", "fontWeight": "700" }}>🚀 Grounded AI Client Pitch Proposal</h3>
        <button className="btn-close" id="btnCloseProposalModal">✕</button>
      </div>
      <div className="proposal-preview-box" id="proposalTextContent"></div>
      <div style={{ "display": "flex", "gap": "0.5rem", "marginTop": "1rem" }}>
        <button className="btn btn-primary" id="btnCopyProposal">📋 Copy Proposal</button>
        <button className="btn btn-outline" id="btnMarkProposalSent">✓ Mark as Pitched in CRM</button>
      </div>
    </div>
  </div>

  {/*  MODAL: PEER MEETUP & MOCK PAIRING  */}
  <div id="modalPeerMatch" className="modal-overlay" style={{ display: "none" }}>
    <div className="modal-content" style={{ maxWidth: "480px" }}>
      <div className="modal-header">
        <h3 style={{ "fontSize": "1.1rem", "fontWeight": "700" }}>🤝 Request 1-on-1 Peer Mock & Meetup</h3>
        <button className="btn-close" id="btnClosePeerMatchModal">✕</button>
      </div>
      <form id="formPeerMatch">
        <div className="form-group">
          <label>Connecting With Peer</label>
          <input type="text" id="peerTargetName" readOnly style={{ "background": "var(--bg-input)", "fontWeight": "600" }} />
        </div>
        <div className="form-group">
          <label>Session Type</label>
          <select id="peerSessionType">
            <option value="system_design">Technical System Design Mock (45m)</option>
            <option value="fastapi_backend">FastAPI & Python Deep Dive (30m)</option>
            <option value="resume_swap">Resume & Portfolio Review Swap (20m)</option>
            <option value="freelance_pitch">Freelance Proposal / Cold Outreach Review (20m)</option>
          </select>
        </div>
        <div className="form-group">
          <label>Preferred Time Slot</label>
          <select id="peerTimeSlot">
            <option value="now">⚡ Instant Match (Active Now)</option>
            <option value="today_evening">Today Evening (6:30 PM)</option>
            <option value="tomorrow_morning">Tomorrow Morning (10:00 AM)</option>
          </select>
        </div>
        <div className="form-group">
          <label>Note / Problem you'd like to work through</label>
          <textarea id="peerMatchNote" rows="2" placeholder="e.g. Practicing Redis caching & LangChain agent architectures..."></textarea>
        </div>
        <button type="submit" className="btn btn-primary btn-block">Request Match</button>
      </form>
    </div>
  </div>
  {/*  MODAL: CALIBRATE CAREER GOAL  */}
  <div id="modalCalibrateGoal" className="modal-overlay" style={{ display: "none" }}>
    <div className="modal-content" style={{ maxWidth: "480px" }}>
      <div className="modal-header">
        <h3 style={{ fontSize: "1.15rem", fontWeight: 700 }}>🎯 Calibrate Career Objective & Target State</h3>
        <button className="btn-close" id="btnCloseCalibrateGoalModal">✕</button>
      </div>
      <form id="formCalibrateGoal">
        <div className="form-group">
          <label>Target Role Title</label>
          <input type="text" id="goalTargetRole" placeholder="e.g. Senior AI/ML Systems Engineer" required />
        </div>
        <div className="form-group">
          <label>Target Timeline</label>
          <select id="goalTimeline">
            <option value="30">30 Days (Sprint)</option>
            <option value="60">60 Days (Standard)</option>
            <option value="90" selected>90 Days (Quarterly Objective)</option>
            <option value="180">180 Days (Long-term Transition)</option>
          </select>
        </div>
        <div className="form-group">
          <label>Target Compensation Band (Annual or Hourly)</label>
          <input type="text" id="goalSalaryBand" placeholder="e.g. $165k - $220k / yr or $90/hr" required />
        </div>
        <div className="form-group">
          <label>Workplace Preference</label>
          <select id="goalWorkplace">
            <option value="remote" selected>Remote First / Global</option>
            <option value="hybrid">Hybrid</option>
            <option value="onsite">Onsite</option>
          </select>
        </div>
        <div className="form-group">
          <label>Primary Dream Companies (comma-separated)</label>
          <input type="text" id="goalTargetCompanies" placeholder="e.g. Anthropic, Stripe, OpenAI, Snowflake" />
        </div>
        <button type="submit" className="btn btn-primary btn-block">🚀 Save & Recalibrate AI Strategy</button>
      </form>
    </div>
  </div>

  {/*  MODAL: STRATEGY REASONING DIAGNOSIS  */}
  <div id="modalReasoning" className="modal-overlay" style={{ display: "none" }}>
    <div className="modal-content" style={{ "maxWidth": "580px" }}>
      <div className="modal-header">
        <h3 style={{ fontSize: "1.15rem", fontWeight: 700 }}>🧠 Master Orchestrator Strategy Reasoning</h3>
        <button className="btn-close" id="btnCloseReasoningModal">✕</button>
      </div>
      <div style={{ "fontSize": "0.86rem", "lineHeight": "1.6", "color": "var(--text-main)", "display": "flex", "flexDirection": "column", "gap": "0.85rem" }} id="reasoningModalContent">
        {/*  Rendered dynamically  */}
      </div>
      <div style={{ "marginTop": "1.25rem", "display": "flex", "justifyContent": "flex-end" }}>
        <button className="btn btn-primary" id="btnCloseReasoningModalBtn">Understood ✓</button>
      </div>
    </div>
  </div>

  {/*  MODAL: APPROVAL ACTION REVIEW  */}
  <div id="modalActionReview" className="modal-overlay" style={{ display: "none" }}>
    <div className="modal-content" style={{ maxWidth: "540px" }}>
      <div className="modal-header">
        <h3 style={{ fontSize: "1.15rem", fontWeight: 700 }} id="actionReviewModalTitle">🔐 Action Review & Approval</h3>
        <button className="btn-close" id="btnCloseActionReviewModal">✕</button>
      </div>
      <div id="actionReviewModalBody" style={{ fontSize: "0.85rem", lineHeight: 1.55, margin: "0.85rem 0" }}>
        {/*  Rendered dynamically  */}
      </div>
    </div>
  </div>

  {/*  MODAL: CONNECT PLATFORM INTEGRATION  */}
  <div id="modalConnectIntegration" className="modal-overlay" style={{ display: "none" }}>
    <div className="modal-content" style={{ maxWidth: "480px" }}>
      <div className="modal-header">
        <h3 style={{ fontSize: "1.15rem", fontWeight: 700 }} id="modalIntegTitle">🔗 Connect Account</h3>
        <button className="btn-close" id="btnCloseIntegModal">✕</button>
      </div>
      <form id="formConnectIntegration" style={{ marginTop: "0.75rem" }}>
        <input type="hidden" id="integPlatformType" value="" />
        
        <div id="modalIntegStateDefault">
          <p style={{ fontSize: "0.84rem", color: "var(--text-muted)", marginBottom: "1rem" }} id="modalIntegDesc">
            Connect your account to synchronize evidence and telemetry into your AI Career OS.
          </p>
          <div className="form-group" id="groupIntegIdentifier">
            <label id="labelIntegIdentifier">Username / Handle / Profile URL</label>
            <input type="text" id="inputIntegIdentifier" placeholder="e.g. username" required style={{ fontSize: "0.85rem", padding: "0.5rem 0.75rem" }} />
          </div>
          <div className="form-group" id="groupIntegToken" style={{ display: "none" }}>
            <label id="labelIntegToken">API Key / Access Token (Optional)</label>
            <input type="password" id="inputIntegToken" placeholder="ghp_xxxx or API Key" style={{ fontSize: "0.85rem", padding: "0.5rem 0.75rem" }} />
          </div>
          <div style={{ display: "flex", gap: "0.5rem", justifyContent: "flex-end", marginTop: "1.25rem" }}>
            <button type="button" className="btn btn-outline" id="btnCancelIntegModal">Cancel</button>
            <button type="submit" className="btn btn-primary" id="btnSubmitIntegModal">🔗 Verify & Connect</button>
          </div>
        </div>

        <div id="modalIntegStateForgot" style={{ display: "none" }}>
          <p style={{ fontSize: "0.85rem", color: "var(--text-muted)", marginBottom: "1.25rem" }}>
            Password recovery for your GeeksforGeeks account is handled securely through GeeksforGeeks.
          </p>
          <button type="button" className="btn btn-primary btn-block" id="btnOpenGfgRecovery">Open GFG Password Recovery</button>
          <div style={{ display: "flex", gap: "0.5rem", justifyContent: "flex-end", marginTop: "1.25rem" }}>
            <button type="button" className="btn btn-outline" id="btnBackToSignIn">Back to Sign In</button>
          </div>
        </div>

        <div id="modalIntegStateConfirmReset" style={{ display: "none" }}>
          <p style={{ fontSize: "0.95rem", color: "var(--text-main)", marginBottom: "1.25rem", fontWeight: 600, textAlign: "center" }}>
            Have you reset your password?
          </p>
          <div style={{ display: "flex", gap: "0.75rem", flexDirection: "column" }}>
            <button type="button" className="btn btn-primary btn-block" id="btnYesReconnect">Yes, Reconnect GFG</button>
            <button type="button" className="btn btn-outline btn-block" id="btnNotYet">Not Yet</button>
          </div>
        </div>
        
        <div id="modalIntegStateLoading" style={{ display: "none", textAlign: "center", padding: "1.5rem 0" }}>
          <div className="pulse-dot" style={{ display: "inline-block", marginRight: "0.5rem" }}></div>
          <span style={{ fontSize: "0.9rem", color: "var(--text-main)", fontWeight: 600 }} id="modalIntegLoadingText">Verifying your account...</span>
        </div>
      </form>
    </div>
  </div>

  

    </div>
  );
}

export default App;
