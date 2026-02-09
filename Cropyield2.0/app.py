from flask import Flask, render_template, request, jsonify, session, send_file, redirect
import pandas as pd
import numpy as np
import os
import json
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from catboost import CatBoostRegressor
import joblib
from database import db
from functools import wraps
import io
import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

DATASET_PATH = "crop_yield_dataset.csv"
MODELS_PATH = "trained_models.pkl"

# =====================================================
# DATASET GENERATION
# =====================================================
def generate_dataset(n=500):
    np.random.seed(42)
    data = pd.DataFrame({
        "Farm_Area": np.random.uniform(1, 50, n),
        "Fertilizer_Used": np.random.uniform(50, 500, n),
        "Pesticide_Used": np.random.uniform(5, 50, n),
        "Water_Usage": np.random.uniform(1000, 10000, n),
        "Crop_Type": np.random.choice(["Wheat", "Rice", "Cotton"], n),
        "Irrigation_Type": np.random.choice(["Drip", "Manual", "Flood"], n),
        "Soil_Type": np.random.choice(["Loamy", "Sandy", "Clay"], n),
        "Season": np.random.choice(["Kharif", "Rabi", "Zaid"], n)
    })
    
    base = (
        0.1 * data["Farm_Area"]
        + 0.015 * data["Fertilizer_Used"]
        + 0.0005 * data["Water_Usage"]
        - 0.05 * data["Pesticide_Used"]
    )
    
    data["Yield"] = (
        base
        + data["Crop_Type"].map({"Wheat": 2.5, "Rice": 3.0, "Cotton": 2.0})
        + data["Irrigation_Type"].map({"Drip": 1.5, "Manual": 1.0, "Flood": 0.8})
        + data["Soil_Type"].map({"Loamy": 1.4, "Clay": 1.1, "Sandy": 0.9})
        + np.random.normal(0, 1, n)
    )
    
    data.to_csv(DATASET_PATH, index=False)
    return data

# Load dataset
if not os.path.exists(DATASET_PATH):
    df = generate_dataset()
else:
    df = pd.read_csv(DATASET_PATH)

df_raw = df.copy()
for col in ["Farm_Area", "Fertilizer_Used", "Pesticide_Used", "Water_Usage", "Yield"]:
    df_raw[col] = pd.to_numeric(df_raw[col], errors="coerce")
df_raw.dropna(inplace=True)

# Encoding
encoders = {}
for col in ["Crop_Type", "Irrigation_Type", "Soil_Type", "Season"]:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    encoders[col] = le

X = df.drop("Yield", axis=1)
y = df["Yield"]

# =====================================================
# MODEL TRAINING
# =====================================================
def train_models(test_size=0.2):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
    
    models = {
        "Linear Regression": LinearRegression(),
        "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42),
        "Gradient Boosting": GradientBoostingRegressor(random_state=42),
        "XGBoost": XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42),
        "LightGBM": LGBMRegressor(n_estimators=100, learning_rate=0.1, random_state=42),
        "CatBoost": CatBoostRegressor(iterations=100, learning_rate=0.1, depth=5, verbose=False, random_state=42)
    }
    
    results = {}
    for name, model in models.items():
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        results[name] = {
            "model": model,
            "r2": float(r2_score(y_test, preds)),
            "mae": float(mean_absolute_error(y_test, preds)),
            "rmse": float(np.sqrt(mean_squared_error(y_test, preds)))
        }
    
    # Save models
    joblib.dump({
        'results': results,
        'X_test': X_test,
        'y_test': y_test
    }, MODELS_PATH)
    
    return results, X_test, y_test

# =====================================================
# DECORATORS
# =====================================================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Login required'}), 401
        return f(*args, **kwargs)
    return decorated_function

# =====================================================
# ROUTES
# =====================================================
@app.route('/')
def index():
    return render_template('landing.html')

@app.route('/auth')
def auth():
    if 'user_id' in session:
        return render_template('dashboard.html', username=session.get('username'))
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/')
    return render_template('dashboard.html', username=session.get('username'))

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    success, user_id = db.authenticate_user(username, password)
    if success:
        session['user_id'] = user_id
        session['username'] = username
        return jsonify({'success': True, 'username': username})
    return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    
    if not email or email.strip() == "":
        return jsonify({'success': False, 'message': 'Email is required'}), 400
    
    success, message = db.register_user(username, password, email)
    return jsonify({'success': success, 'message': message})

@app.route('/logout')
def logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/train-models', methods=['POST'])
@login_required
def train_models_route():
    data = request.json
    test_size = data.get('test_size', 0.2)
    
    try:
        results, X_test, y_test = train_models(test_size)
        
        # Convert models to serializable format
        eval_data = {
            name: {'r2': info['r2'], 'mae': info['mae'], 'rmse': info['rmse']}
            for name, info in results.items()
        }
        
        return jsonify({
            'success': True,
            'results': eval_data
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/predict', methods=['POST'])
@login_required
def predict():
    try:
        data = request.json
        
        # Load models
        if not os.path.exists(MODELS_PATH):
            return jsonify({'success': False, 'message': 'Models not trained yet'}), 400
        
        saved_data = joblib.load(MODELS_PATH)
        results = saved_data['results']
        
        # Prepare input
        input_df = pd.DataFrame([{
            "Farm_Area": float(data['farm_area']),
            "Fertilizer_Used": float(data['fertilizer']),
            "Pesticide_Used": float(data['pesticide']),
            "Water_Usage": float(data['water']),
            "Crop_Type": encoders["Crop_Type"].transform([data['crop']])[0],
            "Irrigation_Type": encoders["Irrigation_Type"].transform([data['irrigation']])[0],
            "Soil_Type": encoders["Soil_Type"].transform([data['soil']])[0],
            "Season": encoders["Season"].transform([data['season']])[0]
        }])
        
        input_df = input_df[X.columns].astype(X.dtypes)
        
        # Make predictions
        predictions = {}
        for name, info in results.items():
            pred = info['model'].predict(input_df)
            predictions[name] = float(pred[0])
        
        avg_pred = np.mean(list(predictions.values()))
        predictions['average'] = float(avg_pred)
        
        # Save to database if requested
        if data.get('save', False):
            db.save_prediction(
                session['user_id'],
                {
                    'farm_area': data['farm_area'],
                    'fertilizer': data['fertilizer'],
                    'pesticide': data['pesticide'],
                    'water': data['water'],
                    'crop': data['crop'],
                    'irrigation': data['irrigation'],
                    'soil': data['soil'],
                    'season': data['season']
                },
                predictions
            )
        
        return jsonify({
            'success': True,
            'predictions': predictions
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/get-predictions')
@login_required
def get_predictions():
    history = db.get_user_predictions(session['user_id'])
    return jsonify({'success': True, 'predictions': history})

@app.route('/get-dataset')
def get_dataset():
    data = df_raw.head(100).to_dict('records')
    return jsonify({'success': True, 'data': data})

@app.route('/download-dataset')
def download_dataset():
    return send_file(
        DATASET_PATH,
        mimetype='text/csv',
        as_attachment=True,
        download_name='crop_yield_dataset.csv'
    )

@app.route('/download-predictions')
@login_required
def download_predictions():
    history = db.get_user_predictions(session['user_id'])
    if history:
        df = pd.DataFrame(history)
        output = io.BytesIO()
        df.to_csv(output, index=False)
        output.seek(0)
        return send_file(
            output,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'{session["username"]}_predictions.csv'
        )
    return jsonify({'success': False, 'message': 'No predictions found'}), 404

@app.route('/get-evaluation-charts')
@login_required
def get_evaluation_charts():
    try:
        if not os.path.exists(MODELS_PATH):
            return jsonify({'success': False, 'message': 'Models not trained yet'}), 400
        
        saved_data = joblib.load(MODELS_PATH)
        results = saved_data['results']
        X_test = saved_data['X_test']
        y_test = saved_data['y_test']
        
        charts = {}
        for name, info in results.items():
            model = info['model']
            y_pred = model.predict(X_test)
            r2 = info['r2']
            
            fig, ax = plt.subplots(figsize=(6, 6))
            ax.scatter(y_test, y_pred, alpha=0.6, s=50, color='steelblue')
            ax.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], "r--", lw=2)
            ax.set_xlabel("Actual Yield")
            ax.set_ylabel("Predicted Yield")
            ax.set_title(f"{name} - R²={r2:.3f}")
            
            charts[name] = fig_to_base64(fig)
            plt.close(fig)
        
        return jsonify({'success': True, 'charts': charts})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# NEW SEPARATE ROUTE FOR EDA
@app.route('/get-charts')
@login_required
def get_eda_charts():
    try:
        charts = {}
        # Chart 1: Crop Type vs Yield
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.barplot(data=df_raw, x="Crop_Type", y="Yield", ax=ax)
        ax.set_title("Yield by Crop Type")
        charts['crop_yield'] = fig_to_base64(fig)
        plt.close(fig)
        
        # Chart 2: Soil Type vs Yield
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.boxplot(data=df_raw, x="Soil_Type", y="Yield", ax=ax)
        ax.set_title("Yield Distribution by Soil Type")
        charts['soil_yield'] = fig_to_base64(fig)
        plt.close(fig)
        
        # Chart 3: Correlation Heatmap
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(
            df_raw[["Farm_Area", "Fertilizer_Used", "Pesticide_Used", "Water_Usage", "Yield"]].corr(),
            annot=True, cmap="coolwarm", ax=ax
        )
        ax.set_title("Feature Correlation")
        charts['correlation'] = fig_to_base64(fig)
        plt.close(fig)
        
        return jsonify({'success': True, 'charts': charts})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

def fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode()
    return f'data:image/png;base64,{img_str}'

if __name__ == '__main__':
    app.run(debug=True)