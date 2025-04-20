# AI-Wealth-Bot

**AI-Wealth-Bot** is an AI-powered financial adviser and portfolio management system designed to empower users with accessible financial insights and tools — even without formal financial education.

---

## 🚀 Getting Started (Backend Phase)

1. **Clone the repository**
```bash
git clone https://github.com/Nerothenerd02/AI-Wealth-Bot.git
cd AI-Wealth-Bot

2. **Set up virtual environment**

python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

Note: Make Sure Visual C++ Build Tools Are Installed ("Desktop development with C++":MSVC v14.x build tools,Windows SDK,CMake tools,cl.exe (the C++ compiler))

3. **Install dependencies**

pip install --upgrade pip setuptools wheel
pip install cythonpip install --upgrade pip setuptools wheel
pip install -r requirements.txt

4. **Download BERT Sentiment Model**

Download the model here:
Model Download Link - (https://drive.google.com/file/d/1FPgzy4ge0ZWTrusfyDaHoHLRPI1b-YMD/view?usp=drive_link)

Place it in the directory:
AIWealthBot/basic_app/

5. **Run Migrations**

python manage.py makemigrations basic_app
python manage.py migrate

6. **Start the Server**

python manage.py runserver

7. **Open your browser and go to:**

http://localhost:8000


**📊 AI Features**

**📈 Technical Analysis**

- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- EMA / SMA (Exponential & Simple Moving Averages)
- OBV (On Balance Volume)
- Pivot Points

**🧠 AI-Based Modules**

- Sentiment Analysis: Fine-tuned BERT
- Financial Analysis: Piotroski Score
- Price Prediction: Facebook Prophet model