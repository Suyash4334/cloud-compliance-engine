console.log("[Azure Watchdog] Background Worker Active.");

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "logPage") {
        fetch("http://127.0.0.1:8000/api/log-activity", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ action: request.page })
        })
        .then(res => res.json())
        .then(data => sendResponse({ status: "success" }))
        .catch(err => sendResponse({ status: "error" }));
        
        return true;
    }
});