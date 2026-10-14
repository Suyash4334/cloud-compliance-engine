console.log("[Azure Watchdog] Risk Analyzer Active.");

let lastSentTitle = "";

function checkAzureTitle() {
    let title = document.title || "";
    let cleanName = title
        .replace(" - Microsoft Azure", "")
        .replace(" | Microsoft Azure", "")
        .replace("Microsoft Azure", "")
        .trim();

    if (cleanName && cleanName !== lastSentTitle && cleanName !== "Home" && cleanName !== "Azure portal" && cleanName.length > 1) {
        lastSentTitle = cleanName;
        
        chrome.runtime.sendMessage({ action: "logPage", page: cleanName }, (response) => {
            console.log("[Watchdog Analyzed]:", cleanName);
        });
    }
}

setInterval(checkAzureTitle, 1500);