# 📦 DataShareApp (Prototype)
A Django-based web application that simulates a data transfer system, allowing users to sign up, log in, and transfer data between accounts. This project is built as a prototype/demo to showcase authentication workflows, UI design, and basic transaction handling.

## 🚀 Features
- 🔐 User Authentication (Signup/Login/Logout)
- 📱 Mobile-based OTP Verification
- 🔑 Forgot Password with OTP Reset
- 📊 User Dashboard
- 🔄 Data Transfer Simulation
- 📜 Transaction History (basic implementation)
- 🎨 Responsive UI (Tailwind CSS-based)

## 🛠️ Tech Stack
* **Backend**: Django (Python)
* **Frontend**: HTML, Tailwind CSS, JavaScript
* **Database**: SQLite (default Django DB)
* **Authentication**: Custom logic with OTP verification

## ⚙️ Installation & Setup
1. **Clone and repository**:

   git clone https://github.com/Disheta006/DataShare.git
   
   cd DataShareApp
2. **Create virtual environment**:
   
   python -m venv venv
   
   venv\Scripts\activate   # Windows
3. **Install dependencies**:
   
    pip install -r requirements.txt
4. **Run migrations**:
   
    python manage.py migrate
5. **Start the server**:
    
    python manage.py runserver
6. **Open in browser**:
    
    http://127.0.0.1:8000/
   
## 🧪 How to Use
- Register using mobile number
- Verify OTP
- Login to dashboard
- Perform data transfer
- View transaction history

## ⚠️ Disclaimer

🚨 This project is strictly a prototype/demo application.

It is NOT intended for real-world or production use

Security mechanisms (OTP, authentication, transactions) are simplified

No real data transfer or financial logic is implemented

Sensitive operations are production-grade

**This project should only be used for**:
Demonstrations

## 📌 Future Improvements
- Proper API-based OTP service (Twilio/Firebase)
- Secure authentication (JWT/OAuth)
- Real transaction handling logic
- Database optimization
- Deployment-ready configuration
- Role-based access control

## 👩‍💻 Author
- **Name**: Isheta Dhanavada
- **LinkedIn**: Isheta Dhanavada
- **GitHub**: Disheta006

Developed as a prototype project for demonstration purposes.


