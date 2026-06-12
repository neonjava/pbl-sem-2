// LifeSaver Registry - Client-side Database Simulation (localStorage)

const DEFAULT_DONORS = [
    {
        id: 1,
        username: "test id",
        password: "pass123",
        donor_temp_id: "TEST-ID-888",
        full_name: "test id",
        phone: "+91 9900112233",
        city: "Davangere",
        area: "Karnataka",
        blood_type: "O+",
        donations_count: 5,
        lives_saved: 15,
        last_donation: "2026-03-10",
        health_status: "Healthy",
        is_available: true,
        reg_date: "2026-01-15",
        role: "donor",
        certificate: 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200"><rect width="200" height="200" fill="lightblue"/><text x="10" y="100" font-family="sans-serif" font-size="12" fill="darkblue">Medical Fitness Certificate (Demo)</text></svg>'
    },
    {
        id: 2,
        username: "admin",
        password: "REDACTED_PASSWORD",
        donor_temp_id: "ADM-0001",
        full_name: "System Administrator",
        role: "admin"
    }
];

const DEFAULT_HOSPITALS = [
    {
        id: 1,
        hospital_id: "HSP-DC-001",
        hospital_name: "City Care Hospital",
        username: "citycare",
        password: "hospital123",
        city: "Davangere",
        contact: "+91 9876543210",
        reg_date: "2026-01-22"
    },
    {
        id: 2,
        hospital_id: "HSP-BLR-002",
        hospital_name: "Unity Blood Center",
        username: "unityblood",
        password: "hospital123",
        city: "Bengaluru",
        contact: "+91 9012345678",
        reg_date: "2026-02-10"
    }
];

const DEFAULT_STOCK = [
    { id: 1, hospital_id: 1, blood_type: "O+", units: 12, last_updated: "2026-05-22 10:00:00" },
    { id: 2, hospital_id: 1, blood_type: "A+", units: 8, last_updated: "2026-05-22 10:15:00" },
    { id: 3, hospital_id: 2, blood_type: "B+", units: 10, last_updated: "2026-05-22 10:20:00" }
];

// Initialize the Database
function initDB() {
    if (!localStorage.getItem("lifesaver_donors")) {
        localStorage.setItem("lifesaver_donors", JSON.stringify(DEFAULT_DONORS));
    }
    if (!localStorage.getItem("lifesaver_hospitals")) {
        localStorage.setItem("lifesaver_hospitals", JSON.stringify(DEFAULT_HOSPITALS));
    }
    if (!localStorage.getItem("lifesaver_stock")) {
        localStorage.setItem("lifesaver_stock", JSON.stringify(DEFAULT_STOCK));
    }
    if (!localStorage.getItem("lifesaver_sos")) {
        localStorage.setItem("lifesaver_sos", JSON.stringify([]));
    }
}

// Auto-run init on script load
initDB();

// Core DB Accessors & Mutators
function getDonors() {
    return JSON.parse(localStorage.getItem("lifesaver_donors"));
}

function saveDonors(donors) {
    localStorage.setItem("lifesaver_donors", JSON.stringify(donors));
}

function getHospitals() {
    return JSON.parse(localStorage.getItem("lifesaver_hospitals"));
}

function saveHospitals(hospitals) {
    localStorage.setItem("lifesaver_hospitals", JSON.stringify(hospitals));
}

function getStock() {
    return JSON.parse(localStorage.getItem("lifesaver_stock"));
}

function saveStock(stock) {
    localStorage.setItem("lifesaver_stock", JSON.stringify(stock));
}

function getSOS() {
    return JSON.parse(localStorage.getItem("lifesaver_sos"));
}

function saveSOS(sos) {
    localStorage.setItem("lifesaver_sos", JSON.stringify(sos));
}

// Authentication Logic
function loginUser(username, password) {
    const donors = getDonors();
    const user = donors.find(d => d.username.toLowerCase() === username.toLowerCase() && d.password === password);
    if (user) {
        localStorage.setItem("session_user_id", user.id);
        localStorage.setItem("session_role", user.role);
        return { success: true, role: user.role };
    }
    return { success: false, message: "Invalid username or password." };
}

function loginHospital(username, password) {
    const hospitals = getHospitals();
    const hospital = hospitals.find(h => h.username.toLowerCase() === username.toLowerCase() && h.password === password);
    if (hospital) {
        localStorage.setItem("session_hospital_id", hospital.id);
        localStorage.setItem("session_role", "hospital");
        return { success: true };
    }
    return { success: false, message: "Invalid hospital username or password." };
}

function getCurrentUser() {
    const userId = localStorage.getItem("session_user_id");
    if (!userId) return null;
    return getDonors().find(d => d.id == userId);
}

function getCurrentHospital() {
    const hospId = localStorage.getItem("session_hospital_id");
    if (!hospId) return null;
    return getHospitals().find(h => h.id == hospId);
}

function logout() {
    localStorage.removeItem("session_user_id");
    localStorage.removeItem("session_hospital_id");
    localStorage.removeItem("session_role");
}

// Donor Actions
function registerDonor(username, password, fullName, phone, bloodType, city, area, certificate) {
    const donors = getDonors();
    if (donors.some(d => d.username.toLowerCase() === username.toLowerCase())) {
        return { success: false, message: "Username already exists." };
    }

    const tempId = "DNR-" + Math.random().toString(36).substring(2, 10).toUpperCase();
    const newDonor = {
        id: Date.now(),
        username,
        password,
        donor_temp_id: tempId,
        full_name: fullName,
        phone: "+91 " + phone,
        blood_type: bloodType,
        city,
        area,
        donations_count: 0,
        lives_saved: 0,
        last_donation: null,
        health_status: "Healthy",
        is_available: true,
        reg_date: new Date().toISOString().split('T')[0],
        role: "donor",
        certificate: certificate || null
    };

    donors.push(newDonor);
    saveDonors(donors);
    return { success: true, tempId };
}

function updateDonorAvailability(userId, healthStatus) {
    const donors = getDonors();
    const donor = donors.find(d => d.id == userId);
    if (donor) {
        donor.health_status = healthStatus;
        donor.is_available = (healthStatus === "Healthy");
        saveDonors(donors);
        return true;
    }
    return false;
}

// SOS Actions
function addSOS(requesterName, bloodType, unitsNeeded, city, contact, notes) {
    const sosList = getSOS();
    const newSOS = {
        id: Date.now(),
        requester_name: requesterName,
        blood_type: bloodType,
        units_needed: parseInt(unitsNeeded),
        city,
        contact,
        notes: notes || "",
        status: "Open",
        created_at: new Date().toLocaleString()
    };
    sosList.push(newSOS);
    saveSOS(sosList);
    // Also save simple flag for backwards compatibility with the existing static page
    localStorage.setItem("sosActive", "true");
    return true;
}

function deleteSOS(sosId) {
    let sosList = getSOS();
    sosList = sosList.filter(s => s.id != sosId);
    saveSOS(sosList);
    if (sosList.length === 0) {
        localStorage.removeItem("sosActive");
    }
    return true;
}

// Hospital Blood Stock Management
function getHospitalStock(hospitalId) {
    return getStock().filter(s => s.hospital_id == hospitalId);
}

function addStockItem(hospitalId, bloodType, units) {
    const stockList = getStock();
    // Check if blood type already exists for this hospital
    const existing = stockList.find(s => s.hospital_id == hospitalId && s.blood_type === bloodType);
    if (existing) {
        existing.units += parseInt(units);
        existing.last_updated = new Date().toLocaleString();
    } else {
        stockList.push({
            id: Date.now(),
            hospital_id: parseInt(hospitalId),
            blood_type: bloodType,
            units: parseInt(units),
            last_updated: new Date().toLocaleString()
        });
    }
    saveStock(stockList);
    return true;
}

function updateStockItem(stockId, units) {
    const stockList = getStock();
    const item = stockList.find(s => s.id == stockId);
    if (item) {
        item.units = parseInt(units);
        item.last_updated = new Date().toLocaleString();
        saveStock(stockList);
        return true;
    }
    return false;
}

function deleteStockItem(stockId) {
    let stockList = getStock();
    stockList = stockList.filter(s => s.id != stockId);
    saveStock(stockList);
    return true;
}

// Admin Actions
function updateDonorStats(donorId, livesSaved, donationsCount, healthStatus) {
    const donors = getDonors();
    const donor = donors.find(d => d.id == donorId);
    if (donor) {
        donor.lives_saved = parseInt(livesSaved);
        donor.donations_count = parseInt(donationsCount);
        donor.health_status = healthStatus;
        donor.is_available = (healthStatus === "Healthy");
        saveDonors(donors);
        return true;
    }
    return false;
}
