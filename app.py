import os, io, json, base64, uuid
import pandas as pd
import numpy as np
from flask import Flask, render_template, request, send_file, redirect, url_for, flash
from joblib import load
from sklearn.decomposition import PCA
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Load RFM helper from artifacts
from artifacts.rfm_utils import compute_rfm

app = Flask(__name__)
app.secret_key = "dev-key"  # change in prod
os.makedirs("uploads", exist_ok=True)

# --- Load artifacts ---
SCALER = load("artifacts/scaler.joblib")
KMEANS = load("artifacts/kmeans.joblib")
with open("artifacts/feature_cols.json") as f:
    FEATURE_COLS = json.load(f)  # ["recency","frequency","monetary"]
with open("artifacts/reference_date.json") as f:
    REF_DATE = json.load(f)["reference_date"]

def read_table(fs):
    name = fs.filename.lower()
    if name.endswith((".xlsx", ".xls")):
        return pd.read_excel(fs)
    return pd.read_csv(fs)

def fig_to_png_b64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode("utf-8")

@app.route("/", methods=["GET","POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")

    f = request.files.get("file")
    if not f or f.filename == "":
        flash("Please upload a CSV/Excel file.")
        return redirect(url_for("index"))

    # 1) Read and compute RFM exactly like in Colab (same reference date)
    df = read_table(f)
    rfm = compute_rfm(df, dayfirst=True, reference_date=REF_DATE)

    # 2) Scale with saved scaler and predict with saved KMeans
    X_full = rfm[FEATURE_COLS].values
    X_scaled = SCALER.transform(X_full)
    labels = KMEANS.predict(X_scaled)
    rfm_out = rfm.copy()
    rfm_out["cluster"] = labels

    # 3) Summary table (avg R/F/M + counts)
    summary = (rfm_out.groupby("cluster")[FEATURE_COLS]
               .mean().round(2).reset_index().sort_values("cluster"))
    counts = rfm_out["cluster"].value_counts().rename("Count_Customers")
    summary = summary.merge(counts, left_on="cluster", right_index=True)

    # 4) PCA plot (2D) on the same scaled space
    coords = PCA(n_components=2, random_state=42).fit_transform(X_scaled)
    fig = plt.figure()
    plt.scatter(coords[:,0], coords[:,1], c=labels)
    plt.title(f"K-Means Clusters (PCA 2D) — K={getattr(KMEANS,'n_clusters', None)}")
    plt.xlabel("PC1"); plt.ylabel("PC2")
    pca_png = fig_to_png_b64(fig)

    # 5) Save a downloadable CSV (customer_id + RFM + cluster)
    out_name = f"clustered_{uuid.uuid4().hex}.csv"
    out_path = os.path.join("uploads", out_name)
    rfm_out[["customer_id"] + FEATURE_COLS + ["cluster"]].to_csv(out_path, index=False)

    return render_template(
        "results.html",
        pca_img=pca_png,
        summary=summary.to_dict(orient="records"),
        cols=FEATURE_COLS,
        k=getattr(KMEANS, "n_clusters", None),
        download_name=out_name
    )

@app.route("/download/<path:fname>")
def download(fname):
    return send_file(os.path.join("uploads", fname), as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
