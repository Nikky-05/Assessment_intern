import os
import io
import base64
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, send_file, flash
import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import RobustScaler
from sklearn.cluster import KMeans, DBSCAN
from sklearn.mixture import GaussianMixture
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

# Config
UPLOAD_FOLDER = 'uploads'
MODEL_FOLDER = 'models'
PLOT_FOLDER = 'static/plots'
ALLOWED_EXT = {'csv', 'xls', 'xlsx'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(MODEL_FOLDER, exist_ok=True)
os.makedirs(PLOT_FOLDER, exist_ok=True)

app = Flask(__name__)
app.secret_key = 'replace_this_with_a_random_secret'

# Try to load pre-trained pipeline if present
PRETRAINED_PATH = os.path.join(MODEL_FOLDER, 'kmeans_rfm_pipeline.pkl')
pretrained_pipeline = None
if os.path.exists(PRETRAINED_PATH):
    pretrained_pipeline = joblib.load(PRETRAINED_PATH)
    print("Loaded pretrained pipeline from", PRETRAINED_PATH)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXT

def compute_rfm_from_df(df):
    # Parse date (dayfirst True to match how data was created)
    df['transaction_date'] = pd.to_datetime(df['transaction_date'], dayfirst=True, infer_datetime_format=True)
    snapshot_date = df['transaction_date'].max() + pd.Timedelta(days=1)
    rfm = df.groupby('customer_id').agg(
        Recency_days = ('transaction_date', lambda x: (snapshot_date - x.max()).days),
        Frequency = ('transaction_id', 'count'),
        Monetary = ('amount', 'sum')
    ).reset_index()
    return rfm

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    file = request.files.get('file')
    use_pretrained = request.form.get('use_pretrained') == 'on'
    uploaded_model = request.files.get('model_file')
    alg = request.form.get('algorithm', 'kmeans')
    K = int(request.form.get('n_clusters', 4))
    use_R = request.form.get('use_R') == 'on'
    use_F = request.form.get('use_F') == 'on'
    use_M = request.form.get('use_M') == 'on'

    if not file or file.filename == '':
        flash("Please upload a dataset CSV/XLSX.")
        return redirect(url_for('index'))
    if not allowed_file(file.filename):
        flash("Unsupported file type.")
        return redirect(url_for('index'))

    fname = os.path.join(UPLOAD_FOLDER, f"upload_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv")
    file.save(fname)
    df = pd.read_csv(fname)
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    df = df.dropna(subset=['customer_id', 'transaction_date', 'amount'])

    rfm = compute_rfm_from_df(df)

    features = []
    if use_R: features.append('Recency_days')
    if use_F: features.append('Frequency')
    if use_M: features.append('Monetary')
    if len(features) == 0:
        flash("Select at least one R/F/M feature.")
        return redirect(url_for('index'))

    pipeline = None
    if use_pretrained and pretrained_pipeline:
        pipeline = pretrained_pipeline
        tmp = rfm.copy()
        tmp['Recency_log'] = np.log1p(tmp['Recency_days'])
        tmp['Frequency_log'] = np.log1p(tmp['Frequency'])
        tmp['Monetary_log'] = np.log1p(tmp['Monetary'])
        trnames = pipeline.get('transformed_feature_names', ['Recency_log','Frequency_log','Monetary_log'])
        X = tmp[[n for n in trnames if n in tmp.columns]].values
        X_scaled = pipeline['scaler'].transform(X)
        if alg == 'kmeans':
            labels = pipeline['kmeans'].predict(X_scaled)
        else:
            km = KMeans(n_clusters=K, random_state=42, n_init=20)
            labels = km.fit_predict(X_scaled)
            pipeline = {'scaler': pipeline['scaler'], 'pca': pipeline.get('pca'), 'kmeans': km}
    else:
        tmp = rfm.copy()
        if 'Recency_days' in tmp.columns:
            tmp['Recency_log'] = np.log1p(tmp['Recency_days'])
        if 'Frequency' in tmp.columns:
            tmp['Frequency_log'] = np.log1p(tmp['Frequency'])
        if 'Monetary' in tmp.columns:
            tmp['Monetary_log'] = np.log1p(tmp['Monetary'])
        feat_map = {'Recency_days':'Recency_log', 'Frequency':'Frequency_log', 'Monetary':'Monetary_log'}
        chosen_transformed = [feat_map[f] for f in features]
        X = tmp[chosen_transformed].values
        scaler = RobustScaler()
        X_scaled = scaler.fit_transform(X)
        if alg == 'kmeans':
            model = KMeans(n_clusters=K, random_state=42, n_init=20)
            labels = model.fit_predict(X_scaled)
        elif alg == 'dbscan':
            model = DBSCAN(eps=0.5, min_samples=5)
            labels = model.fit_predict(X_scaled)
        elif alg == 'gmm':
            model = GaussianMixture(n_components=K, random_state=42)
            labels = model.fit_predict(X_scaled)
        else:
            model = KMeans(n_clusters=K, random_state=42, n_init=20)
            labels = model.fit_predict(X_scaled)
        pca = PCA(n_components=2, random_state=42)
        pca.fit(X_scaled)
        pipeline = {'scaler': scaler, 'pca': pca, 'kmeans': model if alg=='kmeans' else None,
                    'transformed_feature_names': chosen_transformed, 'rfm_features': features}

    rfm['cluster'] = labels
    summary = rfm.groupby('cluster').agg(
        customers = ('customer_id', 'count'),
        Recency_days = ('Recency_days', 'mean'),
        Frequency = ('Frequency', 'mean'),
        Monetary = ('Monetary', 'mean')
    ).round(2).reset_index().to_dict(orient='records')

    pca = PCA(n_components=2, random_state=42)
    X_pca = pca.fit_transform(X_scaled)
    fig, ax = plt.subplots(figsize=(7,5))
    unique_clusters = sorted(rfm['cluster'].unique())
    for c in unique_clusters:
        idx = rfm['cluster'] == c
        ax.scatter(X_pca[idx,0], X_pca[idx,1], label=f'Cluster {c}', s=50, alpha=0.7)
    ax.legend()
    ax.set_title('Clusters (PCA 2D)')
    ax.set_xlabel('PC1'); ax.set_ylabel('PC2')
    plot_path = os.path.join(PLOT_FOLDER, f'cluster_plot_{datetime.now().strftime("%Y%m%d%H%M%S")}.png')
    plt.savefig(plot_path, bbox_inches='tight')
    plt.close(fig)

    out_csv = os.path.join(UPLOAD_FOLDER, f"rfm_clustered_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv")
    rfm.to_csv(out_csv, index=False)

    return render_template('results.html',
                           plot_url='/' + plot_path,
                           summary=summary,
                           n_customers=len(rfm),
                           download_path=out_csv)

if __name__ == '__main__':
    app.run(debug=True)