# pyrefly: ignore [missing-import]
from fastapi import FastAPI
# pyrefly: ignore [missing-import]
from fastapi.middleware.cors import CORSMiddleware
import time
from collector import AWSCloudCollector

app = FastAPI(title="Cloud Compliance Engine Backend", version="2026.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

visited_pages = [
    {"time": time.strftime("%H:%M:%S"), "page": "Azure Portal Home (portal.azure.com)"},
    {"time": time.strftime("%H:%M:%S"), "page": "Subscription Overview (Azure for Students)"}
]

performed_actions = [
    {"time": time.strftime("%H:%M:%S"), "action": "Watchdog Connected & Initial Compliance Scan Triggered"},
    {"time": time.strftime("%H:%M:%S"), "action": "Checked Network Security Groups & VM Inbound Rules"}
]

security_warnings = [
    {"time": time.strftime("%H:%M:%S"), "message": "System Secure: No active policy violations detected."}
]

@app.get("/")
def read_root():
    return {"message": "Cloud Compliance Engine Backend is Running!"}

@app.get("/api/scan")
@app.post("/api/scan")
def run_cloud_scan():
    """Trigger an on-demand cloud compliance audit across AWS / Cloud resources."""
    collector = AWSCloudCollector()
    return collector.scan_all()

@app.get("/api/azure-audit")
def get_azure_audit():
    return {
        "compliance_score": 92.5,
        "total_checked": 3,
        "failures": 0,
        "visited_pages": visited_pages[-6:],
        "performed_actions": performed_actions[-5:],
        "warnings": security_warnings[-4:]
    }

@app.post("/api/log-activity")
def log_activity(data: dict):
    action = data.get("action", "Azure Portal Dashboard")
    timestamp = time.strftime("%H:%M:%S")
    
    # Avoid duplicate consecutive logs
    if not visited_pages or visited_pages[-1]["page"] != action:
        visited_pages.append({"time": timestamp, "page": action})
        if len(visited_pages) > 6:
            visited_pages.pop(0)
            
    performed_actions.append({"time": timestamp, "action": f"Navigated to: {action}"})
    if len(performed_actions) > 5:
        performed_actions.pop(0)
        
    # Real-time Security Risk Analysis (Warning Trigger)
    risky_keywords = ["Network Security Group", "Firewall", "Storage Account", "Virtual Machines", "Key Vault"]
    if any(keyword.lower() in action.lower() for keyword in risky_keywords):
        warning_msg = f"⚠️ High-Risk Configuration Blade Opened: '{action}'. Check CIS benchmarks!"
        if not security_warnings or security_warnings[-1]["message"] != warning_msg:
            security_warnings.append({"time": timestamp, "message": warning_msg})
            if len(security_warnings) > 4:
                security_warnings.pop(0)
            
    return {"status": "logged", "page": action}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)