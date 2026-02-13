# 🌾 Crop Yield Prediction System

An AI-powered web application that predicts crop yields using multiple machine learning models. Built with Flask, this system helps farmers and agricultural professionals make data-driven decisions by analyzing various farming parameters.

![Crop Yield Prediction](static/logo.png)

## 🌟 Features

### 🤖 Multiple ML Models
- **6 Advanced Models**: Linear Regression, Random Forest, Gradient Boosting, XGBoost, LightGBM, and CatBoost
- **Ensemble Predictions**: Average predictions from all models for higher accuracy
- **Model Comparison**: Compare performance metrics (R², MAE, RMSE) across all models

### 📊 Visual Analytics
- **Interactive Charts**: Powered by Chart.js and Matplotlib
- **EDA Visualizations**: Correlation heatmaps, bar charts, box plots, and scatter plots
- **Actual vs Predicted Plots**: Visual comparison for each model's performance
- **Model Evaluation Dashboard**: Real-time performance metrics

### 💾 Data Management
- **Prediction History**: Save and track all predictions with timestamps
- **CSV Export**: Download datasets and prediction history
- **User Authentication**: Secure login/register system with session management
- **SQLite Database**: Lightweight and efficient data storage

### 🎯 User-Friendly Interface
- **Modern UI**: Clean, responsive design with gradient backgrounds
- **Landing Page**: Professional landing page with feature highlights
- **Interactive Forms**: Slider inputs for easy parameter adjustment
- **Real-time Results**: Instant predictions with visual feedback

## 🚀 Tech Stack

**Backend:**
- Flask (Python web framework)
- SQLite (Database)
- scikit-learn, XGBoost, LightGBM, CatBoost (ML models)
- Pandas, NumPy (Data processing)
- Matplotlib, Seaborn (Visualizations)

**Frontend:**
- HTML5, CSS3, JavaScript (ES6)
- Chart.js (Interactive charts)
- Responsive design (Mobile-friendly)

## 📦 Installation

### Prerequisites
- Python 3.9+
- pip (Python package manager)

### Setup Instructions

1. **Clone the repository**
```bash
git clone https://github.com/vikranth-ai/Crop-Yield-Prediction.git
cd Crop-Yield-Prediction
```

2. **Create virtual environment**
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the application**
```bash
python3 app.py
```

5. **Open in browser**
```
http://localhost:5000
```

## 📋 Requirements

Create a `requirements.txt` file with:
```
Flask==3.0.0
pandas==2.1.3
numpy==1.26.2
scikit-learn==1.3.2
xgboost==2.0.3
lightgbm==4.1.0
catboost==1.2.2
matplotlib==3.8.2
seaborn==0.13.0
joblib==1.3.2
```

## 🗂️ Project Structure

```
crop-yield-prediction/
├── app.py                      # Flask application & routes
├── database.py                 # Database operations
├── trained_models.pkl          # Saved ML models (generated)
├── crop_yield_dataset.csv      # Dataset (auto-generated)
├── crop_yield.db              # SQLite database (auto-generated)
├── templates/
│   ├── landing.html           # Landing page
│   ├── login.html             # Login/Register page
│   └── dashboard.html         # Main dashboard
├── static/
│   ├── landing.css            # Landing page styles
│   ├── landing.js             # Landing page scripts
│   ├── style.css              # Dashboard styles
│   ├── auth.js                # Authentication scripts
│   ├── dashboard.js           # Dashboard functionality
│   └── logo.png               # Application logo
├── requirements.txt           # Python dependencies
└── README.md                  # Project documentation
```

## 🎮 Usage

### 1. User Registration/Login
- Navigate to the landing page
- Click "Get Started" or "Login"
- Create an account or login with existing credentials

### 2. Train Models
- Click "🚀 Train Models" in the sidebar
- Adjust test data split percentage (10-50%)
- Wait for training to complete (~30 seconds)

### 3. Make Predictions
- Navigate to "🎯 Predict" tab
- Adjust input parameters using sliders:
  - Farm Area (1-50 acres)
  - Fertilizer Used (50-500 kg)
  - Pesticide Used (5-50 kg)
  - Water Usage (1000-10000 liters)
  - Crop Type, Irrigation Type, Soil Type, Season
- Click "Predict Yield"
- View results from all 6 models + average prediction
- Save prediction to history (optional)

### 4. View Analytics
- **📊 Dataset**: View and download the dataset
- **📈 EDA**: Explore data visualizations
- **📊 Evaluation**: Compare model performance metrics
- **📊 Comparison**: Compare predictions across models
- **📥 History**: View and download prediction history

## 🧪 Model Performance

The system uses 6 machine learning models with the following typical performance:

| Model | R² Score | MAE | RMSE |
|-------|----------|-----|------|
| Linear Regression | ~0.85 | ~1.2 | ~1.5 |
| Random Forest | ~0.92 | ~0.8 | ~1.0 |
| Gradient Boosting | ~0.91 | ~0.9 | ~1.1 |
| XGBoost | ~0.93 | ~0.7 | ~0.9 |
| LightGBM | ~0.92 | ~0.8 | ~1.0 |
| CatBoost | ~0.93 | ~0.7 | ~0.9 |

*Note: Actual performance may vary based on dataset and training parameters.*

## 📊 Dataset Features

The system analyzes the following parameters:

**Numerical Features:**
- Farm Area (acres)
- Fertilizer Used (kg)
- Pesticide Used (kg)
- Water Usage (liters)

**Categorical Features:**
- Crop Type (Wheat, Rice, Cotton)
- Irrigation Type (Drip, Manual, Flood)
- Soil Type (Loamy, Sandy, Clay)
- Season (Kharif, Rabi, Zaid)

**Target Variable:**
- Yield (tons)

## 🔒 Security Features

- **Password Hashing**: SHA256 encryption (upgrade to bcrypt recommended)
- **Session Management**: Secure Flask sessions
- **Login Required Decorators**: Protected routes
- **SQL Injection Prevention**: Parameterized queries
- **User Data Isolation**: Each user can only access their own predictions

## 🌐 API Endpoints

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/` | GET | Landing page | No |
| `/auth` | GET | Login/Register page | No |
| `/login` | POST | User authentication | No |
| `/register` | POST | User registration | No |
| `/logout` | GET | User logout | Yes |
| `/dashboard` | GET | Main dashboard | Yes |
| `/train-models` | POST | Train ML models | Yes |
| `/predict` | POST | Make yield prediction | Yes |
| `/get-predictions` | GET | Get user's prediction history | Yes |
| `/get-dataset` | GET | Get dataset preview | No |
| `/download-dataset` | GET | Download full dataset CSV | No |
| `/download-predictions` | GET | Download prediction history CSV | Yes |
| `/get-charts` | GET | Get EDA charts | Yes |
| `/get-evaluation-charts` | GET | Get model evaluation charts | Yes |

## 🎨 Screenshots

### Landing Page
Beautiful gradient hero section with feature highlights and call-to-action.

### Dashboard
Interactive dashboard with tabs for dataset, predictions, analytics, and history.

### Model Evaluation
Compare all 6 models with visual charts and performance metrics.

### Prediction Interface
User-friendly sliders and dropdowns for input parameters with real-time results.

## 🚧 Future Enhancements

- [ ] Add weather data integration
- [ ] Implement hyperparameter tuning
- [ ] Add more crop types and soil types
- [ ] Real-time data visualization
- [ ] Mobile app (React Native)
- [ ] API for third-party integrations
- [ ] Advanced user analytics dashboard
- [ ] Email notifications for predictions
- [ ] Multi-language support
- [ ] Dark mode theme

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Your Name**
- GitHub: [@yourusername](https://github.com/vikranth-ai)
- LinkedIn: [Vikranth](https://www.linkedin.com/in/vikranth-chary-721128303/)
- Email: vikranth.vicky0116@gmail.com

## 🙏 Acknowledgments

- Thanks to the scikit-learn, XGBoost, LightGBM, and CatBoost teams
- Agricultural data inspired by real-world farming parameters
- UI/UX design inspired by modern web applications
- Special thanks to the open-source community

## 📞 Support

For support, email vikranth.vicky0116@gmail.com or open an issue in the GitHub repository.

---

⭐ **Star this repository** if you found it helpful!

🌾 **Happy Farming with AI!** 🌾
