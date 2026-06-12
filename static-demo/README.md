# LifeSaver Network - Static Demo (Netlify-Ready)

This is a fully interactive, client-side version of the LifeSaver Network application. It does not require any backend database or Python environment, making it perfect for hosting on static web hosts like **Netlify**, **GitHub Pages**, or **Vercel**.

## 🚀 How to Run Locally

You can open `index.html` directly in any web browser! Double-click it or right-click and select "Open with Browser".

Alternatively, run a local web server:
```bash
# Using Python
python3 -m http.server 8000
```
Then visit `http://127.0.0.1:8000` in your web browser.

---

## ☁️ How to Deploy to Netlify

1. Drag and drop the `static-demo` folder directly into the **Netlify Drop** panel (https://app.netlify.com/drop).
2. Alternatively, push this folder to a GitHub repository and link it to Netlify for continuous deployment.

---

## 💾 Client-Side Database Simulation (localStorage)

All data is stored in your browser's `localStorage`. When you first visit the page, the database is automatically seeded with demo accounts, blood stock, and profiles:

### 🔑 Demo Login Credentials

#### 1. Donor Accounts
* **Username:** `test id`
* **Password:** `pass123`
* **Profile:** Naveen R (TEST-ID-888)

#### 2. Administrative Accounts
* **Username:** `admin`
* **Password:** `REDACTED_PASSWORD`
* **Dashboard:** Allows updating donor statistics (lives saved, donation counts) and health status. Displays flashing red/white SOS alerts dynamically.

#### 3. Hospital Control Centers
* **City Care Hospital (Davangere):**
  * **Username:** `citycare`
  * **Password:** `hospital123`
  * **ID:** `HSP-DC-001`
* **Unity Blood Center (Bengaluru):**
  * **Username:** `unityblood`
  * **Password:** `hospital123`
  * **ID:** `HSP-BLR-002`

---

## 🛠️ Interactive Features Added

* **Database Seeding:** Automatically creates mock donors, hospitals, and blood stocks on first run.
* **Full Login & Registration:** Simulates donor registrations (generates unique Donor IDs), donor login, admin login, and hospital login.
* **Donor Dashboard:** View next eligibility date, donation history, and toggle health status ("Healthy" / "Non-Healthy") to update availability.
* **Emergency SOS Module:** Form to request emergency blood donor alerts. Adds requests to the global list.
* **Admin Flashing Alerts:** When an SOS is active, a red-and-white flashing alert banner appears on `/admin_dashboard.html` with real-time polling (every 5 seconds) to catch new requests.
* **Hospital Control Panel:**
  * **Live Blood Stock CRUD:** Add, edit, or delete blood stock availability records.
  * **SOS Resolution:** View all emergency alerts and click "Resolve" to clear them.
