🥗 AI Diet Planner

An intelligent web application that helps users plan their diet, track workouts, and monitor fitness progress. Built using Flask, MySQL (TiDB Cloud), and SQLAlchemy.

🚀 Live Demo

https://fit-ai-ai-based-diet-planner.onrender.com

📌 Features
👤 User Registration & Login system
🍽️ Add and track daily meals
🏋️ Workout logging system
📊 Progress tracking dashboard
☁️ Cloud database using TiDB (MySQL compatible)
📁 File upload support
🔐 Secure authentication system
🛠️ Tech Stack

Frontend:

HTML
CSS
JavaScript

Backend:

Python (Flask)

Database:

TiDB Cloud (MySQL compatible)
SQLAlchemy ORM

Deployment:

Render
📂 Project Structure
AI-Diet-Planner/
│
├── app.py
├── config.py
├── requirements.txt
├── models/
├── templates/
│   ├── auth/
│   ├── dashboard/
│   ├── meals/
│   ├── workouts/
│   └── profile/
├── static/
│   ├── css/
│   ├── js/
│   └── images/
├── uploads/
└── README.md
⚙️ Setup Instructions (Run Locally)
1. Clone the repository
git clone https://github.com/your-username/ai-diet-planner.git
cd ai-diet-planner
2. Create virtual environment
python -m venv venv

Activate it:

Windows:
venv\Scripts\activate
3. Install dependencies
pip install -r requirements.txt
4. Configure database

Update config.py with your TiDB credentials:

mysql+pymysql://username:password@gateway01.ap-southeast-1.prod.aws.tidbcloud.com:4000/ai_diet_planner
5. Run the application
python app.py

Then open:

http://127.0.0.1:5000
☁️ Deployment (Render)
Push code to GitHub
Connect GitHub repo to Render
Add environment variables:
DATABASE_URL
SECRET_KEY

Set build command:

pip install -r requirements.txt

Set start command:

gunicorn app:app
🔐 Environment Variables

Create a .env file (optional for local development):

SECRET_KEY=your_secret_key
DATABASE_URL=your_tidb_connection_string
📊 Future Improvements
🤖 AI-based diet recommendations
📱 Mobile-friendly UI
📈 Advanced analytics dashboard
🥗 Calorie prediction system
📤 Export diet plans as PDF
