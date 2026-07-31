# SmartFarmer: Agentic AI Crop Cultivation & Diagnostic Platform

SmartFarmer is a production-grade, intelligence-driven Django web application designed for farmers in Gujarat, India (specifically optimized for conditions in village **Chadasna, Taluka Himmatnagar, District Sabarkantha**). It integrates crop lifecycle planning, economic crop analytics, weather-based advice, market commodity prices, AI-based crop disease diagnosis with PDF reports, farming news aggregators, and tailored soil fertilizer recommendations.

---

## 🚀 Key Modules & Capabilities

1.  **📊 Dashboard & Analytics Panel**:
    *   Dynamic statistics showing total cultivated land, accumulated investment sunk, expected revenue, and highest yield crop.
    *   **Investment Sowing Timeline**: Interactive line plots showing when and where money is spent.
    *   **Crop Financial Distributions**: High-fidelity Plotly bar and pie charts displaying land allocation, investment distributions, and expected returns by crop.
2.  **🌾 Crop Management (CRUD)**:
    *   Full lifecycle logging including Crop Variety, Sowing Date, Estimated Harvest Date, Land Size (Acres), Investment Cost, and Expected Yield/Revenue.
    *   Automatic progress tracking relative to target harvest dates.
3.  **📚 Crop Reference Library**:
    *   Fully searchable and filterable database containing detailed profiles of **8 Indian crops** (Cotton, Groundnut, Maize, Bajra, Wheat, Castor, Cumin, Mustard).
    *   Displays season type, soil recommendations, temperature ranges, rainfall constraints, and typical diseases/fertilizers.
4.  **☁️ Weather Advisory Cockpit**:
    *   Fetches real-time weather alerts and generates localized agricultural rules/advice for planting, spraying, and harvesting based on humidity, rain, and temperature.
5.  **📈 Mandi Market Prices**:
    *   Tracks historical mandi pricing curves for Gujarat APMCs with Plotly trendlines, high/low points, average price summaries, and tooltips.
6.  **🧬 AI Disease Prediction & Diagnostics**:
    *   Utilizes regularized scikit-learn models (Decision Tree, Random Forest, KNN) to predict crop diseases based on real environmental features.
    *   Calculates and shows confidence scores using `predict_proba()`.
7.  **📄 PDF Report Generator**:
    *   Generates beautifully structured PDF diagnostic reports including farmer context, environmental parameters, prediction confidence, treatment recipes, and expert disclaimers.
8.  **🧪 Soil Fertilizer Guide**:
    *   Calculates tailored N-P-K fertilizer recipes based on crop growth stages.
    *   Scales recommended quantities according to soil types (e.g. 20% increase for sandy soil leaching rates).
9.  **📰 Farming News Aggregator**:
    *   Scrapes agriculture news in real time from public feeds using BeautifulSoup with deduplication checks.

---

## 🛠️ Technology Stack

*   **Backend Framework**: Python, Django 4.2.x
*   **Database**: SQLite (built-in, configured for development and staging)
*   **Machine Learning**: Scikit-learn, NumPy (Decision Tree, Random Forest, K-Nearest Neighbors)
*   **Data Visualization**: Plotly, Pandas (Responsive client-side SVG graphing)
*   **Web Scraping**: BeautifulSoup4, Requests
*   **Document Generation**: ReportLab (High-fidelity PDF compilation)
*   **Frontend UI**: HTML5, Vanilla CSS3 (Custom design system), Bootstrap 5, Bootstrap Icons

---

## 📦 Installation & Getting Started

Follow these steps to run the project locally:

### 1. Clone the Repository
```bash
git clone <repository-url>
cd SmartFarmer
```

### 2. Set Up a Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Apply Database Migrations
```bash
python manage.py migrate
```

### 5. Start the Development Server
```bash
python manage.py runserver
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

---

## 📁 Project Structure

```
SmartFarmer/
├── core/                  # Core application views, URLs, forms, and custom authentication
├── crops/                 # Crop CRUD, Analytics, ML engine, and PDF export views
├── static/                # Static assets (custom CSS, JS, and crop images)
├── templates/             # HTML templates styled with our custom design system
├── db.sqlite3             # SQLite Database
├── manage.py              # Django CLI utility
├── requirements.txt       # Project dependencies
├── .gitignore             # Git ignore patterns
└── README.md              # Project documentation
```

---

## 🛠️ Verification & Test Suite

To verify that imports and model configurations compile correctly:
```bash
python manage.py check
```
