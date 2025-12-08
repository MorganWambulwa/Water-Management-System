WaterConnect - Smart Water Management System

**WaterConnect** is a comprehensive web platform designed to bridge the gap between communities and water service providers. It empowers residents to locate safe water sources and report issues, while providing administrators with data-driven tools and funding mechanisms to maintain infrastructure.

## Live Demo
**[View the Live Site on Render](https://water-management-system-ouep.onrender.com)**

---

## Key Features

### Public & Community Features
* **Interactive Map:** Visualizes all water sources with status indicators:
    * 🟢 **Green:** Operational
    * 🟡 **Yellow:** Maintenance
    * 🔴 **Red:** Contaminated
    * 🟤 **Brown:** Broken/Non-Operational
* **Report Issues:** Residents can report broken pumps or leaks (requires login to prevent spam).
* **M-Pesa Donations:** Integrated **Safaricom Daraja API** (STK Push) allows community members to donate funds directly for repairs.
* **User Dashboard:** A personalized hub where users track their reported issues, receive "Resolved" notifications, and see nearby working sources.
* **Contact Support:** Professional HTML email form via Brevo SMTP for direct inquiries.

### Admin & Technician Features
* **Analytics Dashboard:** Real-time charts showing network health and issue priority distribution.
* **Verification System:** Only Admins can mark a source as "Verified" (adds a Blue Badge), ensuring data trust.
* **Data Management:** Full CRUD (Create, Read, Update, Delete) for water sources.
    * *Security Note:* Regular users can only delete sources *they* created.
* **CSV Export:** Admins can download a report of all "Open Issues" for offline analysis.

---

## Tech Stack
* **Backend:** Django 5 (Python)
* **Frontend:** Bootstrap 5, HTML5, CSS3 (Custom Responsive Design)
* **Database:** PostgreSQL (Production), SQLite (Local)
* **Payments:** Django-Daraja (M-Pesa API)
* **Email:** Brevo SMTP (Port 2525) with HTML Templates
* **Mapping:** Leaflet.js
* **Deployment:** Render Cloud Hosting

---

## 💻 Local Installation Guide

### 1. Clone the Repository
```bash
git clone [https://github.com/MorganWambulwa/Water-Management-System.git](https://github.com/MorganWambulwa/Water-Management-System.git)
cd Water-Management-System
2. Create Virtual Environment
Bash

python -m venv venv
# Windows
source venv/Scripts/activate
# Mac/Linux
source venv/bin/activate
3. Install Dependencies
Bash

pip install -r requirements.txt
4. Set Up Environment Variables
Create a .env file in the root directory:

Code snippet

# Django Security
SECRET_KEY=your_secret_key
DEBUG=True

EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password

MPESA_ENVIRONMENT=sandbox
MPESA_CONSUMER_KEY=your_key
MPESA_CONSUMER_SECRET=your_secret
5. Run Migrations & Server
Bash

python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
Visit http://127.0.0.1:8000 to start.