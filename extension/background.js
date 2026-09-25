let usageTime = 0;
let timer = null;
let currentSite = null;

const trackedSites = [
    "instagram.com",
    "youtube.com"
];

// TEST LIMITS
// Instagram = 30 seconds
// YouTube = 45 seconds
const siteLimits = {
    "instagram.com": 30,
    "youtube.com": 45
};

let alertedSites = {};


// ==========================================
// GET WEBSITE NAME
// ==========================================

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


// ==========================================
// LOAD SAVED USAGE
// ==========================================

async function loadUsage(site) {

    try {

        const result = await chrome.storage.local.get([site]);

        usageTime = result[site] || 0;

        console.log(
            "CATGuard: loaded",
            site,
            usageTime,
            "seconds"
        );

    } catch (error) {

        console.error(
            "CATGuard: failed to load usage",
            error
        );

        usageTime = 0;
    }
}


// ==========================================
// SAVE USAGE
// ==========================================

async function saveUsage() {

    if (!currentSite) {
        return;
    }

    try {

        await chrome.storage.local.set({
            [currentSite]: usageTime
        });

        console.log(
            "CATGuard: saved",
            currentSite,
            usageTime,
            "seconds"
        );

    } catch (error) {

        console.error(
            "CATGuard: failed to save usage",
            error
        );
    }
}


// ==========================================
// SHOW LIMIT NOTIFICATION
// ==========================================

function showLimitNotification(site) {

    console.log(
        "CATGuard LIMIT REACHED:",
        site
    );

    chrome.notifications.create(
        "catguard-" + site,
        {
            type: "basic",
            iconUrl: "icon128.png",
            title: "🐱 CATGuard Alert",
            message: site + " usage limit reached!"
        }
    );
}


// ==========================================
// START TIMER
// ==========================================

async function startTimer(site) {

    // Same website already running
    if (
        timer !== null &&
        currentSite === site
    ) {
        return;
    }

    // Stop previous timer
    if (timer !== null) {

        clearInterval(timer);
        timer = null;

        await saveUsage();
    }

    currentSite = site;

    // Load saved time BEFORE starting timer
    await loadUsage(site);

    console.log(
        "CATGuard timer started:",
        site
    );

    // ======================================
    // START COUNTING
    // ======================================

    timer = setInterval(async () => {

        usageTime++;

        console.log(
            "CATGuard:",
            currentSite,
            "Usage:",
            usageTime,
            "seconds"
        );


        // ==================================
        // SAVE EVERY 10 SECONDS
        // ==================================

        if (usageTime % 10 === 0) {

            await saveUsage();
        }


        // ==================================
        // CHECK USAGE LIMIT
        // ==================================

        const limit = siteLimits[currentSite];

        if (
            limit &&
            usageTime >= limit &&
            !alertedSites[currentSite]
        ) {

            alertedSites[currentSite] = true;

            showLimitNotification(currentSite);
        }

    }, 1000);
}


// ==========================================
// STOP TIMER
// ==========================================

async function stopTimer() {

    if (timer !== null) {

        clearInterval(timer);
        timer = null;

        await saveUsage();
    }

    console.log(
        "CATGuard timer stopped"
    );

    currentSite = null;
    usageTime = 0;
}


// ==========================================
// CHECK ACTIVE TAB SAFELY
// ==========================================

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


// ==========================================
// USER CHANGES TAB
// ==========================================

chrome.tabs.onActivated.addListener(
    (activeInfo) => {

        checkTab(activeInfo.tabId);

    }
);


// ==========================================
// WEBSITE FINISHED LOADING
// ==========================================

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


// ==========================================
// TAB CLOSED
// ==========================================

chrome.tabs.onRemoved.addListener(
    (tabId) => {

        console.log(
            "CATGuard: tab closed",
            tabId
        );

    }
);