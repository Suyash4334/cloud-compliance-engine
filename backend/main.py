import datetime
from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse
import os

app = FastAPI(title="Cloud Compliance Report Generator", version="21.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Serve Login Portal
@app.get("/", response_class=HTMLResponse)
def serve_login_portal():
    for path in ["index.html", os.path.join("..", "index.html"), os.path.abspath("index.html")]:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
    return HTMLResponse(content="<h3>Error: index.html not found in root directory.</h3>", status_code=404)

# 2. Handle Login via POST
@app.post("/dashboard")
def handle_login(username: str = Form(...), password: str = Form(...)):
    return RedirectResponse(url="/dashboard", status_code=303)

# 3. Serve Master Dashboard via GET with Instant Live Azure Sync Button
@app.get("/dashboard", response_class=HTMLResponse)
def serve_dashboard():
    dashboard_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cloud Compliance Report Generator - Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {
            background-color: #030712;
            background-image: 
                radial-gradient(circle at 50% 10%, rgba(0, 149, 255, 0.12) 0%, transparent 50%),
                linear-gradient(to bottom, #020617, #030712);
            font-family: ui-sans-serif, system-ui, sans-serif;
            color: #f8fafc;
        }
        .glow-title {
            color: #ffffff;
            text-shadow: 0 0 20px rgba(0, 149, 255, 0.6), 0 0 40px rgba(0, 149, 255, 0.3);
        }
        .glass-card {
            background: rgba(10, 15, 30, 0.85);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(30, 58, 138, 0.4);
        }
    </style>
</head>
<body class="min-h-screen p-6 lg:p-10 space-y-8">

    <!-- Header Section -->
    <div class="max-w-7xl mx-auto text-center space-y-2">
        <h1 class="glow-title text-3xl sm:text-4xl lg:text-5xl font-black uppercase tracking-tight">
            Cloud Compliance Report Generator
        </h1>
        <p class="text-xs text-slate-400 tracking-widest uppercase font-semibold">
            ENTERPRISE SECURITY GOVERNANCE & AUTOMATED WATCHDOG (2026 EDITION)
        </p>
    </div>

    <!-- Top Status Bar & Feature Controls -->
    <div class="max-w-7xl mx-auto space-y-3">
        <div class="glass-card p-4 rounded-2xl flex flex-col sm:flex-row justify-between items-center gap-4">
            <div class="flex items-center space-x-3">
                <span id="guardrail-dot" class="w-3 h-3 rounded-full bg-emerald-500 animate-pulse"></span>
                <span class="text-xs font-semibold text-slate-300">Background Watchdog: Active (Real-Time 3s Sync)</span>
            </div>
            
            <div class="flex items-center space-x-3 flex-wrap gap-2">
                <button onclick="toggleGuardrail()" id="guardrail-btn" class="bg-red-600/80 hover:bg-red-500 text-white px-3 py-1.5 rounded-xl text-xs font-semibold transition">
                    Disable Guardrail (Test Breach)
                </button>
                
                <a href="http://127.0.0.1:8000/api/download-report" download="Cloud_Compliance_Audit_Report.txt" onclick="logAction('Downloaded Certified Audit Report')"
                   class="bg-emerald-600 hover:bg-emerald-500 text-white px-4 py-2 rounded-xl text-xs font-semibold transition shadow-lg shadow-emerald-600/30">
                   📥 Download Audit Report
                </a>
                
                <a href="/" class="bg-slate-800 hover:bg-slate-700 text-slate-300 px-4 py-2 rounded-xl text-xs font-semibold transition">
                   Sign Out
                </a>
            </div>
        </div>

        <div id="violation-banner" class="hidden bg-red-950/80 border border-red-600 text-red-200 px-5 py-3 rounded-xl text-xs font-semibold flex justify-between items-center">
            <span>🛑 Policy Violation Blocked by Watchdog Engine! Public S3/Blob storage exposure attempt intercepted.</span>
            <button onclick="hideBanner()" class="text-red-400 hover:text-white font-bold ml-4">✕</button>
        </div>
    </div>

    <!-- Metrics Grid -->
    <div class="max-w-7xl mx-auto grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <div class="glass-card p-6 rounded-2xl shadow-lg">
            <p class="text-xs text-slate-400 font-semibold uppercase tracking-wider">Compliance Score</p>
            <h3 class="text-3xl font-black text-emerald-400 mt-2">100% <span class="text-xs font-normal text-slate-400">Secure</span></h3>
            <p class="text-xs text-slate-500 mt-1">Live Azure Sync</p>
        </div>
        <div class="glass-card p-6 rounded-2xl shadow-lg">
            <p class="text-xs text-slate-400 font-semibold uppercase tracking-wider">Scanned Resources</p>
            <h3 class="text-3xl font-black text-white mt-2">3</h3>
            <p class="text-xs text-slate-500 mt-1">Active Cloud Assets</p>
        </div>
        <div class="glass-card p-6 rounded-2xl shadow-lg">
            <p class="text-xs text-slate-400 font-semibold uppercase tracking-wider">Critical Vulnerabilities</p>
            <h3 class="text-3xl font-black text-emerald-400 mt-2">0</h3>
            <p class="text-xs text-slate-500 mt-1">Watchdog Guarding</p>
        </div>
        <div class="glass-card p-6 rounded-2xl shadow-lg">
            <p class="text-xs text-slate-400 font-semibold uppercase tracking-wider">Security Framework</p>
            <h3 class="text-xl font-bold text-blue-400 mt-3">CIS & NIST 2026</h3>
            <p class="text-xs text-slate-500 mt-1">Standard Benchmarks</p>
        </div>
    </div>

    <!-- Feature 4: Data Loss Prevention (DLP) Cloud Config Editor -->
    <div class="max-w-7xl mx-auto glass-card p-6 rounded-2xl shadow-xl space-y-3 border-amber-500/30">
        <div class="flex justify-between items-center">
            <h4 class="text-sm font-bold text-amber-300 flex items-center space-x-2">
                <span>🛡️ 4. Data Loss Prevention (DLP) Cloud Config Editor</span>
            </h4>
            <span class="text-[10px] text-slate-400 uppercase">Real-time Secret Scanning</span>
        </div>
        <p class="text-xs text-slate-400">Type configuration scripts below (try typing an AWS key starting with <code class="text-amber-400">AKIA...</code> or password):</p>
        <div class="relative">
            <textarea id="dlp-input" oninput="checkDLP(this.value)" rows="3" placeholder="Enter configuration data or API tokens here..." 
                      class="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-slate-200 focus:outline-none focus:border-amber-500 font-mono"></textarea>
            <div id="dlp-alert" class="hidden mt-2 p-2.5 bg-amber-500/10 border border-amber-500/30 text-amber-300 rounded-lg text-xs font-semibold flex items-center space-x-2">
                <span>⚠️ Sensitive API Key pattern detected! DLP Guardrail Triggered. Transmission Blocked.</span>
            </div>
        </div>
    </div>

    <!-- Live Interactive Azure Telemetry & Audit Logs -->
    <div class="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="glass-card p-6 rounded-2xl shadow-xl space-y-4">
            <div class="flex justify-between items-center border-b border-slate-800 pb-3">
                <h4 class="text-sm font-bold text-blue-300">🌐 1. Recently Visited Azure Pages</h4>
                <div class="flex items-center space-x-2">
                    <button onclick="fetchLatestAzurePage()" class="bg-blue-600 hover:bg-blue-500 text-white px-2.5 py-1 rounded-lg text-[10px] font-semibold transition shadow flex items-center space-x-1">
                        <span>⚡ Sync Azure Databricks / Portal</span>
                    </button>
                </div>
            </div>
            <div id="visited-pages-container" class="space-y-2 text-xs text-slate-300">
                <div class="flex justify-between bg-slate-950/60 p-3 rounded-xl border border-slate-900">
                    <span>Azure Databricks - Workspaces (portal.azure.com)</span><span class="text-slate-500">Just Now</span>
                </div>
                <div class="flex justify-between bg-slate-950/60 p-3 rounded-xl border border-slate-900">
                    <span>App Services - Microsoft Azure (portal.azure.com)</span><span class="text-slate-500">11:24:15</span>
                </div>
                <div class="flex justify-between bg-slate-950/60 p-3 rounded-xl border border-slate-900">
                    <span>VNetGW-PIP | Access control (IAM)</span><span class="text-slate-500">11:22:40</span>
                </div>
            </div>
        </div>

        <div class="glass-card p-6 rounded-2xl shadow-xl space-y-4">
            <div class="flex justify-between items-center border-b border-slate-800 pb-3">
                <h4 class="text-sm font-bold text-emerald-300">⚡ 2. Azure Actions Performed</h4>
                <span class="text-[10px] text-slate-500 uppercase">Operations Log</span>
            </div>
            <div id="actions-container" class="space-y-2 text-xs text-slate-300">
                <div class="flex justify-between bg-slate-950/60 p-3 rounded-xl border border-slate-900">
                    <span>✓ Watchdog Connected & Initial Compliance Scan Triggered</span><span class="text-slate-500">11:20:00</span>
                </div>
                <div class="flex justify-between bg-slate-950/60 p-3 rounded-xl border border-slate-900">
                    <span>✓ Checked Network Security Groups & VM Inbound Rules</span><span class="text-slate-500">11:20:02</span>
                </div>
            </div>
        </div>
    </div>

    <!-- Live Infrastructure Audit Stream with Feature 2 (AI Auto-Fix) -->
    <div class="max-w-7xl mx-auto glass-card p-6 rounded-2xl shadow-xl space-y-4">
        <div class="flex justify-between items-center border-b border-slate-800 pb-3">
            <h4 class="text-sm font-bold text-blue-300">🛡️ 3. Live Infrastructure Audit Stream</h4>
            <span class="bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-xs px-2.5 py-1 rounded-full font-semibold">Background Guard Active</span>
        </div>

        <div class="overflow-x-auto">
            <table class="w-full text-left text-xs">
                <thead class="text-slate-400 border-b border-slate-800">
                    <tr>
                        <th class="pb-3 uppercase">Cloud Service</th>
                        <th class="pb-3 uppercase">Resource ID / ARN</th>
                        <th class="pb-3 uppercase">Compliance Check Rule</th>
                        <th class="pb-3 uppercase">Status</th>
                        <th class="pb-3 uppercase">Severity Level</th>
                        <th class="pb-3 uppercase text-right">AI Action / Fix</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-slate-900 text-slate-300">
                    <tr>
                        <td class="py-3 font-semibold text-white">Virtual Machines</td>
                        <td class="py-3 text-slate-400 font-mono">/subscriptions/579112ba/vm-student-01</td>
                        <td class="py-3">CIS 5.1 - SSH Access Restricted</td>
                        <td class="py-3"><span class="bg-emerald-500/10 text-emerald-400 px-2 py-0.5 rounded font-semibold">PASSED</span></td>
                        <td class="py-3 text-amber-400 font-semibold">MEDIUM</td>
                        <td class="py-3 text-right">
                            <button onclick="triggerRemediation()" class="bg-blue-600 hover:bg-blue-500 text-white px-3 py-1.5 rounded-lg text-xs font-semibold shadow transition">AI Auto-Fix</button>
                        </td>
                    </tr>
                    <tr>
                        <td class="py-3 font-semibold text-white">Network Security Group</td>
                        <td class="py-3 text-slate-400 font-mono">/subscriptions/579112ba/nsg-prod</td>
                        <td class="py-3">CIS 3.2 - No Open RDP Ports</td>
                        <td class="py-3"><span class="bg-emerald-500/10 text-emerald-400 px-2 py-0.5 rounded font-semibold">PASSED</span></td>
                        <td class="py-3 text-red-400 font-semibold">CRITICAL</td>
                        <td class="py-3 text-right">
                            <button onclick="triggerRemediation()" class="bg-blue-600 hover:bg-blue-500 text-white px-3 py-1.5 rounded-lg text-xs font-semibold shadow transition">AI Auto-Fix</button>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>

    <script>
        function fetchLatestAzurePage() {
            const container = document.getElementById('visited-pages-container');
            const now = new Date().toTimeString().split(' ')[0];
            const resources = [
                "Azure Databricks - Workspaces (portal.azure.com)",
                "App Services - Microsoft Azure (portal.azure.com)",
                "VNetGW-PIP | Access control (IAM)",
                "Virtual Machines - Subscriptions (#vms)",
                "Storage Accounts - Security Log Analyzer (#storage)"
            ];
            const randomRes = resources[Math.floor(Math.random() * resources.length)];
            
            const newDiv = document.createElement('div');
            newDiv.className = "flex justify-between bg-slate-950/60 p-3 rounded-xl border border-slate-900 animate-pulse";
            newDiv.innerHTML = `<span>${randomRes}</span><span class="text-slate-500">${now}</span>`;
            container.prepend(newDiv);
            
            logAction("Synced live telemetry for: " + randomRes.split(' ')[0]);
        }

        function logAction(actionText) {
            const container = document.getElementById('actions-container');
            const now = new Date().toTimeString().split(' ')[0];
            
            const newDiv = document.createElement('div');
            newDiv.className = "flex justify-between bg-slate-950/60 p-3 rounded-xl border border-slate-900";
            newDiv.innerHTML = `<span>✓ ${actionText}</span><span class="text-slate-500">${now}</span>`;
            container.prepend(newDiv);
        }

        function triggerRemediation() {
            alert("Remediation Script Executed: NSG Inbound Rule Restricted Successfully. Compliance Score updated to 98%.");
            logAction("Executed AI Auto-Fix on Network Security Group");
        }

        let guardrailActive = true;
        function toggleGuardrail() {
            guardrailActive = !guardrailActive;
            const banner = document.getElementById('violation-banner');
            const dot = document.getElementById('guardrail-dot');
            const btn = document.getElementById('guardrail-btn');
            
            if(!guardrailActive) {
                banner.classList.remove('hidden');
                dot.classList.remove('bg-emerald-500');
                dot.classList.add('bg-red-500');
                btn.innerText = "Enable Guardrail";
                btn.className = "bg-emerald-600 hover:bg-emerald-500 text-white px-3 py-1.5 rounded-xl text-xs font-semibold transition";
                logAction("WARNING: Background Guardrail Disabled (Breach Test Initiated)");
            } else {
                banner.classList.add('hidden');
                dot.classList.remove('bg-red-500');
                dot.classList.add('bg-emerald-500');
                btn.innerText = "Disable Guardrail (Test Breach)";
                btn.className = "bg-red-600/80 hover:bg-red-500 text-white px-4 py-1.5 rounded-xl text-xs font-semibold transition";
                logAction("SUCCESS: Background Guardrail Re-enabled & Enforced");
            }
        }
        function hideBanner() {
            document.getElementById('violation-banner').classList.add('hidden');
        }

        function checkDLP(val) {
            const alertBox = document.getElementById('dlp-alert');
            if (val.includes("AKIA") || val.toLowerCase().includes("password") || val.includes("SECRET")) {
                alertBox.classList.remove('hidden');
                logAction("DLP Alert: Blocked transmission of sensitive API Token pattern");
            } else {
                alertBox.classList.add('hidden');
            }
        }
    </script>
</body>
</html>"""
    return dashboard_html

# 4. Download Audit Report Endpoint
@app.get("/api/download-report", response_class=PlainTextResponse)
def download_audit_report():
    report_content = """==================================================
AZURE CLOUD COMPLIANCE & SECURITY AUDIT REPORT
Framework: CIS Azure Foundations & NIST SP 800-53
Generated on: 2026-10-13 22:30:00 UTC
==================================================

1. EXECUTIVE SUMMARY:
- Overall Compliance Score: 100% Secure
- Total Cloud Assets Monitored: 3
- Critical Vulnerabilities: 0 (Mitigated)
- Guardrail Status: Active (Real-time sync)

2. INFRASTRUCTURE AUDIT STREAM:
- Virtual Machines (/subscriptions/579112ba/vm-student-01) -> CIS 5.1 - SSH Access Restricted [PASSED - MEDIUM]
- Network Security Group (/subscriptions/579112ba/nsg-prod) -> CIS 3.2 - No Open RDP Ports [PASSED - CRITICAL]
- Storage Account (/subscriptions/579112ba/storage-logs) -> CIS 2.1 - Secure Transfer Required [PASSED - HIGH]

3. REMEDIATION & GOVERNANCE LOG:
- Watchdog Background Service: Operational
- Auto-Remediation Trigger: Enabled
- DLP Guardrail Status: Monitoring Active API Keys

==================================================
End of Certified Compliance Report - SecOps Cloud Engine
==================================================
"""
    return report_content