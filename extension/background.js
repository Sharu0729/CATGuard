let usageTime = 0;
let timer = null;
let currentSite = null;

const trackedSites = [
    "instagram.com",
    "youtube.com"
];


// Get website name
function getSite(url) {

    if (!url) {
        return null;
    }

    for (const site of trackedSites) {

        if (url.includes(site)) {
            return site;
        }
    }

    return null;
}


// Load previously saved usage time
function loadUsage(site) {

    chrome.storage.local.get([site])
        .then((result) => {

            usageTime = result[site] || 0;

            console.log(
                "CATGuard: loaded",
                site,
                usageTime,
                "seconds"
            );

        });
}


// Save usage time
function saveUsage() {

    if (!currentSite) {
        return;
    }

    chrome.storage.local.set({
        [currentSite]: usageTime
    });

    console.log(
        "CATGuard: saved",
        currentSite,
        usageTime,
        "seconds"
    );
}


// Start timer
function startTimer(site) {

    // Same website already running
    if (timer !== null && currentSite === site) {
        return;
    }

    // Stop previous timer
    if (timer !== null) {

        clearInterval(timer);
        timer = null;

        saveUsage();
    }

    currentSite = site;

    loadUsage(site);

    console.log(
        "CATGuard timer started:",
        site
    );

    timer = setInterval(() => {

        usageTime++;

        console.log(
            "CATGuard:",
            currentSite,
            "Usage:",
            usageTime,
            "seconds"
        );

        // Save every 10 seconds
        if (usageTime % 10 === 0) {
            saveUsage();
        }

    }, 1000);
}


// Stop timer
function stopTimer() {

    if (timer !== null) {

        clearInterval(timer);
        timer = null;

        saveUsage();
    }

    console.log(
        "CATGuard timer stopped"
    );

    currentSite = null;
    usageTime = 0;
}


// Check active tab
function checkTab(tabId) {

    chrome.tabs.get(tabId)
        .then((tab) => {

            const site = getSite(tab.url);

            if (site) {

                startTimer(site);

            } else {

                stopTimer();
            }

        })
        .catch(() => {

            console.log(
                "CATGuard: tab no longer exists"
            );

        });
}


// User changes tab
chrome.tabs.onActivated.addListener((activeInfo) => {

    checkTab(activeInfo.tabId);

});


// Website finished loading
chrome.tabs.onUpdated.addListener(
    (tabId, changeInfo, tab) => {

        if (changeInfo.status !== "complete") {
            return;
        }

        const site = getSite(tab.url);

        if (site) {

            startTimer(site);

        } else {

            stopTimer();
        }

    }
);


// Tab closed
chrome.tabs.onRemoved.addListener((tabId) => {

    console.log(
        "CATGuard: tab closed",
        tabId
    );

});