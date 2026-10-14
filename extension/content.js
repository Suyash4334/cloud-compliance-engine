console.log("SecOps Azure Telemetry Bridge Active.");

// Function to send current Azure page info to chrome storage
function reportAzureActivity() {
    const pageTitle = document.title || window.location.pathname;
    const pageUrl = window.location.href;
    
    // Save to chrome local storage so dashboard can read it
    chrome.storage.local.get({ visitedPages: [] }, function(data) {
        let pages = data.visitedPages;
        const newEntry = { title: pageTitle, url: pageUrl, time: new Date().toLocaleTimeString() };
        
        // Avoid duplicate consecutive entries
        if (pages.length === 0 || pages[0].title !== pageTitle) {
            pages.unshift(newEntry);
            if (pages.length > 10) pages.pop(); // keep last 10
            chrome.storage.local.set({ visitedPages: pages });
        }
    });
}

// Run every 3 seconds while browsing Azure Portal
setInterval(reportAzureActivity, 3000);