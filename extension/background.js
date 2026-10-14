chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete' && tab.url && tab.url.includes("portal.azure.com")) {
        const pageTitle = tab.title || "Azure Portal Page";
        const timeNow = new Date().toLocaleTimeString();
        
        // Save to chrome extension local storage
        chrome.storage.local.get({ visitedPages: [] }, function(data) {
            let pages = data.visitedPages;
            if (pages.length === 0 || pages[0].title !== pageTitle) {
                pages.unshift({ title: pageTitle, time: timeNow });
                if (pages.length > 10) pages.pop();
                chrome.storage.local.set({ visitedPages: pages });
            }
        });
    }
});