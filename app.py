from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder, StandardScaler
import zipfile

app = Flask(__name__)

DATA_PATH = "data.csv"
PROCESSED_PATH = "processed.csv"
IMG_FOLDER = "static/charts"
os.makedirs(IMG_FOLDER, exist_ok=True)

# ===== Home =====
@app.route('/')
def home():
    return render_template("preprocessing.html")


# ===== Upload =====
@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    df = pd.read_csv(file)
    df.to_csv(DATA_PATH, index=False)

    return jsonify({
        "html": df.head().to_html(classes="table")
    })


# ===== Load Data =====
def load_data():
    if not os.path.exists(DATA_PATH):
        return None
    return pd.read_csv(DATA_PATH)

@app.route('/inspect')
def inspect():
    df = load_data()
    if df is None:
        return jsonify({"error": "Upload file first"})

    report = {}

    # Basic Info
    report["rows"] = df.shape[0]
    report["columns"] = df.shape[1]

    # Column Info
    report["columns_list"] = list(df.columns)

    # Data Types
    report["dtypes"] = df.dtypes.astype(str).to_dict()

    # Missing Values
    report["missing"] = df.isnull().sum().to_dict()

    # Statistics
    report["describe"] = df.describe().to_html(classes="table")

    return jsonify(report)


# ===== Auto Preprocessing =====
@app.route('/auto_preprocess')
def auto_preprocess():
    df = load_data()
    if df is None:
        return jsonify({"error": "Upload file first"})

    # Missing values
    df.fillna(df.mean(numeric_only=True), inplace=True)
    for col in df.select_dtypes(include='object'):
        df[col].fillna(df[col].mode()[0], inplace=True)

    # Remove duplicates
    df.drop_duplicates(inplace=True)

    # Encode
    for col in df.select_dtypes(include='object'):
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))

    # Scale
    scaler = StandardScaler()
    num_cols = df.select_dtypes(include=['int64', 'float64']).columns
    df[num_cols] = scaler.fit_transform(df[num_cols])

    df.to_csv(DATA_PATH, index=False)

    return jsonify({
        "html": df.head().to_html(classes="table")
    })


# ===== Visualization =====
@app.route('/visualize')
def visualize():
    df = load_data()
    if df is None:
        return jsonify({"error": "Upload file first"})

    images = []

    # Histogram
    for col in df.select_dtypes(include=['int64', 'float64']).columns[:3]:
        plt.figure(figsize=(6,4))
        sns.histplot(df[col], kde=True, color='blue')
        plt.title(f"{col} Distribution")

        path = f"{IMG_FOLDER}/{col}_hist.png"
        plt.savefig(path)
        plt.close()
        images.append(path)

    # Boxplot
    for col in df.select_dtypes(include=['int64', 'float64']).columns[:2]:
        plt.figure(figsize=(6,4))
        sns.boxplot(x=df[col], color='orange')
        plt.title(f"{col} Boxplot")

        path = f"{IMG_FOLDER}/{col}_box.png"
        plt.savefig(path)
        plt.close()
        images.append(path)

    # Heatmap
    plt.figure(figsize=(7,5))
    sns.heatmap(df.corr(), annot=True, cmap="coolwarm")
    plt.title("Correlation Heatmap")

    heatmap_path = f"{IMG_FOLDER}/heatmap.png"
    plt.savefig(heatmap_path)
    plt.close()
    images.append(heatmap_path)

    return jsonify({"images": images})

# ===== Download =====
@app.route('/download')
def download():
    df = load_data()
    df.to_csv(PROCESSED_PATH, index=False)
    return send_file(PROCESSED_PATH, as_attachment=True)


@app.route('/download_charts')
def download_charts():
    zip_path = "charts.zip"

    with zipfile.ZipFile(zip_path, 'w') as z:
        for file in os.listdir("static/charts"):
            z.write(f"static/charts/{file}")

    return send_file(zip_path, as_attachment=True)


#if __name__ == '__main__':
    #app.run(debug=True)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)