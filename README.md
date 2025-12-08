WaterConnect - Smart Water Management System

WaterConnect is a web-based platform designed to help communities and administrators manage water resources efficiently. It allows residents to locate safe water sources, report malfunctions, and track maintenance while providing administrators with data-driven insights to improve service delivery.

## Live Demo
**[View the Live Site](https://water-management-system-ouep.onrender.com)**

---

## Key Features

### For the Community (Public & Users)
* **Interactive Map:** View all registered water sources on a live map (Leaflet.js) with status indicators (Green = Operational, Red = Contaminated, Brown = Broken and Yellow = Maintenance).
* **Search & Filter:** Easily find water sources by name or location.
* **Issue Reporting:** Registered users can report broken pumps, leaks, or contamination directly to authorities.
* **User Dashboard:** Track the status of reported issues and receive notifications when they are resolved.
* **Contact Support:** Communicate directly with system administrators via email.

### For Administrators (Staff)
* **Analytics Dashboard:** Visual charts (Chart.js) showing network status distribution and issue priority levels.
* **Data Management:** Full CRUD capabilities for Water Sources and Repair Logs.
* **Verification System:** Admins verify user-submitted sources to ensure data integrity (Blue Verified Badge).
* **Report Management:** Track, prioritize, and resolve community-submitted issue reports.
* **Data Export:** Export open issues to CSV for offline analysis and reporting.

---

## Tech Stack
* **Backend:** Django 5 (Python)
* **Frontend:** Bootstrap 5, HTML5, CSS3, JavaScript
* **Database:** PostgreSQL (Production), SQLite (Local Development)
* **Mapping:** Leaflet.js & OpenStreetMap
* **Visualization:** Chart.js
* **Deployment:** Render Cloud Hosting

---

## Local Installation Guide

### 1. Clone the Repository
```bash
git clone [https://github.com/MorganWambulwa/Water-Management-System.git](https://github.com/MorganWambulwa/Water-Management-System.git)
cd Water-Management-System
2. Create a Virtual Environment
Bash

python -m venv venv
source venv/bin/activate  # Windows: venv/Scripts/activate
3. Install Dependencies
Bash

pip install -r requirements.txt
4. Configure Environment Variables
Create a .env file in the root directory and add your secrets:

Code snippet

SECRET_KEY=your_secret_key_here
DEBUG=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
5. Setup Database
Bash

python manage.py makemigrations
python manage.py migrate
6. Create an Admin User
Bash

python manage.py createsuperuser
7. Run the Server
Bash

python manage.py runserver
Visit http://127.0.0.1:8000 in your browser. """