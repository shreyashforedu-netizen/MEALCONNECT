# Meal Connect 🍃

Meal Connect is an intelligent food-waste management and prediction platform that seamlessly connects hotels, restaurants, and food-serving establishments with NGOs to redistribute surplus food and prevent waste.

## 🚀 Features

- **Daily Food Entry**: Quickly log daily prepared and consumed food to auto-calculate waste.
- **Machine Learning Prediction**: Custom AI models per hotel that predict expected food waste for the next day.
- **NGO Alert System**: If a high waste threshold is breached, the platform automatically recommends routing the surplus food to registered NGOs.
- **Collection Ledger**: A secure, permanent history of all reserved and successfully collected surplus food.
- **Business Analytics**: Deep graphical insights (via Chart.js) mapping waste generation trends, prediction accuracy, and NGO distribution.
- **Rigorous Data Separation**: Secure multi-tenant architecture ensuring hotels only ever see their own proprietary data.

## ⚙️ Setup and Installation

### 1. Prerequisites
Ensure you have Python 3.8+ installed.

### 2. Install Dependencies
Install all required libraries using the provided `requirements.txt` file:
```bash
pip install -r requirements.txt
```

### 3. Add the Intro Video (Important!)
For the landing page to work perfectly, you must provide the intro background video.
1. Obtain an `.mp4` video (e.g., a high-quality video of food or a restaurant environment).
2. Rename the file exactly to: `intro.mp4`
3. Place the file inside the `static/videos/` directory:
   `static/videos/intro.mp4`
*(If the file is missing, the app will gracefully fall back to a styled green background).*

### 4. Initialize Demo Data
To instantly populate the database with realistic demo data (2 Hotels with 30-days of historical food waste and NGO collections), run the seed script:
```bash
python seed_demo.py
```
*Note: This will safely wipe and recreate the database if one already exists.*

### 5. Run the Application
Start the Flask development server:
```bash
python app.py
```
Then open your browser and navigate to: `http://127.0.0.1:5000`

## 🧪 Demo Credentials

If you ran the `seed_demo.py` script, you can log in immediately using:
- **Email:** `grand@example.com`
- **Password:** `password123`

## 🗂 Project Structure
- `app.py`: Core routing, database initialization, and session controllers.
- `ml/predictor.py`: Scikit-learn Machine Learning pipeline (RandomForest/LinearRegression).
- `seed_demo.py`: Automated demo data generator.
- `templates/`: HTML structures infused with Jinja2 templating.
- `static/`: Custom CSS styling, Vanilla JS, and multimedia assets.
