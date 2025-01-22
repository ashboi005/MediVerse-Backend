###BACKEND DEPLOYED ON https://mediverse-backend.onrender.com

### MediVerse: Revolutionizing Healthcare Communication

Healthcare systems often struggle to streamline communication between patients and doctors. To address this challenge, our team, Cracked Nerds, developed MediVerse—a comprehensive Patient-Doctor communication system. Submitted for the BITS PILANI POSTMAN API Hackathon 4.0, this application is designed to simplify healthcare interactions through robust APIs and AI-powered features. Built with Flask for the backend and Next.js for the frontend, MediVerse ensures seamless and efficient user experiences.

### **Team Members**

- **Ashwath Soni (me)**
- **Sahil Chabra**
- **Gurshabad Singh**
- **Parth Kapoor**

### **Live Demo**

**Explore the live application here:** [https://medi-verse.vercel.app/](https://medi-verse.vercel.app/)

- **Frontend GitHub Repository:** [https://github.com/sahilchabra09/MediVerse](https://github.com/sahilchabra09/MediVerse)
- **Backend GitHub Repository:** [https://github.com/ashboi005/MediVerse-Backend](https://github.com/ashboi005/MediVerse-Backend)
- **Postman Documentation:** [https://documenter.getpostman.com/view/38037470/2sAYQdjVSm](https://documenter.getpostman.com/view/38037470/2sAYQdjVSm)
- **YouTube Showcase Video:** *(Link to be added)*



Here’s an in-depth look at MediVerse.

---

### Key Features of MediVerse

#### **User Dashboard**

Patients have access to a versatile dashboard that provides the following functionalities:

- **User Details Management**: Patients can input and update their detailed profiles, including medical history, allergies, and insurance details.
- **File Storage and Analysis**: Upload medical reports and leverage the Gemini API for summarization and insights.
- **Routine Generation**: Create 30-day AI-powered health routines tailored to individual goals.
- **Doctor Communication**: View all available doctors, request appointments, and send meeting links directly via SMS (powered by Twilio's API).
- **Appointment Management**: Patients can request, track, and manage their appointments seamlessly. They also receive real-time updates for appointment status.
- **Prescription View**: Access prescriptions provided by doctors in a consolidated format.

#### **Doctor Dashboard**

Doctors’ dashboards are tailored for efficient patient management and include:

- **Doctor Profile Management**: Enter and update specialization, availability, and other professional details.
- **Patient Overview**: View all registered patients and their details, including medical history, reports, and prescriptions.
- **Appointment Control**: Approve or reject appointment requests with the ability to add remarks. Additionally, mark appointments as completed or track expired ones.
- **Prescription Management**: Issue prescriptions directly to patients.

#### **AI-Enhanced Features**

- **File Summarization**: Medical reports uploaded by patients are summarized using Gemini API, providing actionable insights for doctors.
- **Health Routine Generation**: Personalized routines are generated based on patient goals to enhance overall well-being.

---

### Technical Overview

#### **Core Technologies**

MediVerse is built using:

- **Flask**: For backend API development and modular routing.

- Next.js: Provides a dynamic and responsive frontend for user interaction.

- **Neon DB**: A modern, serverless PostgreSQL database for scalable and efficient data storage and management.

- **Gunicorn**: To host the application in a production-ready environment.

- **Render**: Deployment platform with configuration via render.yaml.

- **Twilio API**: For SMS notifications and communication.

- **Gemini API**: For AI-powered features

#### **Blueprints for Modular Development**

The application is divided into modular blueprints:

1. **Auth**: Handles user authentication and role assignments.

2. **User**: Manages user details, profile updates, and personal data.

3. **AI**: Integrates Gemini API for summarization and routine generation.

4. **Meeting**: Facilitates communication between patients and doctors by sending meeting links via SMS, powered by Twilio.

5. **Doctor**: Provides endpoints for managing doctor profiles and interactions.

6. **Appointment**: Manages appointment scheduling, requests, and status updates.

7. **Prescription**: Handles medical prescriptions.

#### **Automation with APScheduler**

APScheduler ensures timely updates to appointment statuses. For instance, uncompleted appointments automatically expire once the scheduled time passes.

---

### User Journey

#### **For Patients:**

1. Register and complete their profile.
2. Upload reports for analysis and generate a personalized health routine.
3. Browse available doctors, view their details, and request an appointment.
4. Communicate with doctors via meeting links sent through SMS.
5. Track prescriptions, appointments, and health progress through the dashboard.

#### **For Doctors:**

1. Create and update professional profiles, including specializations and availability.
2. View and manage patient profiles, reports, and prescriptions.
3. Approve or reject appointment requests with added remarks.
4. Track appointment statuses and mark completed ones.

---

### Why MediVerse?

MediVerse stands out by combining traditional healthcare management with modern AI-powered tools. It bridges the communication gap between patients and doctors while ensuring data accessibility and process automation. Whether it’s generating a health routine, managing appointments, or storing medical reports, MediVerse streamlines the experience for both patients and doctors.

---

### Future Scope

1. **Enhanced AI Features**: Include predictive analytics for patient health trends.
2. **Telemedicine Integration**: Add real-time video consultations.
3. **Expanded Deployment**: Scale the application to support multiple regions and languages.
4. **Advanced Security Measures**: Strengthen data encryption and access control.

MediVerse is more than a project—it’s a vision to make healthcare accessible, efficient, and patient-centric. Together, let’s revolutionize how healthcare communication happens.

---

### Thank You!

### **Team Cracked Nerds**

