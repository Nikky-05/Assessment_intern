import os
import re
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import PCA
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


class RFMAnalyzer:
    """
    Handles:
      - Loading and cleaning data
      - Enforcing consistent date format (YYYY-MM-DD)
      - RFM analysis
      - Clustering
      - Plotting and exporting
    """

    def __init__(self):
        self.raw = None
        self.data = None
        self.clean_mode = 'strict'
        self.quality = {}
        self.rfm_data = None
        self._X = None
        self.features = ['Recency', 'Frequency', 'Monetary']
        self.scaler = None
        self.last_plot_path = None
        self.last_error = None

    # ---------- helpers ----------
    def _norm(self, s: str) -> str:
        return re.sub(r'[\s_\-\/]+', '', str(s).strip().lower())

    def _find_col(self, cols, candidates):
        norm_cols = {self._norm(c): c for c in cols}
        for cand in candidates:
            key = self._norm(cand)
            if key in norm_cols:
                return norm_cols[key]
        return None

    # ---------- loader ----------
    def load_data(self, path_or_buffer, mode='strict') -> bool:
        self.last_error = None
        self.clean_mode = mode if mode in ('strict', 'lenient') else 'strict'
        try:
            # --- read file into df ---
            if isinstance(path_or_buffer, str):
                ext = os.path.splitext(path_or_buffer)[1].lower()
                if ext in ('.xlsx', '.xls'):
                    df = pd.read_excel(path_or_buffer)
                else:
                    df = pd.read_csv(path_or_buffer, sep=None, engine='python', encoding='utf-8-sig')
            else:
                df = pd.read_csv(path_or_buffer, sep=None, engine='python', encoding='utf-8-sig')

            # normalize headers
            df.columns = [str(c).strip() for c in df.columns]

            # map synonyms
            cust_syn = ['customer_id','customer id','customerid','cust_id','custid','user_id']
            date_syn = ['transaction_date','transaction date','date','order_date','invoice_date']
            amt_syn  = ['amount','total','price','value','sales','revenue','transaction_amount']

            c_col = self._find_col(df.columns, cust_syn)
            d_col = self._find_col(df.columns, date_syn)
            a_col = self._find_col(df.columns, amt_syn)

            if not (c_col and d_col and a_col):
                raise ValueError(f"Required columns not found. Detected: {list(df.columns)}")

            df = df.rename(columns={c_col: 'customer_id', d_col: 'transaction_date', a_col: 'amount'})

            # type coercion
            df['customer_id'] = df['customer_id'].astype(str).str.strip()
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce')

            # ✅ enforce consistent date format
            df['transaction_date'] = pd.to_datetime(
                df['transaction_date'],
                errors='coerce',
                dayfirst=True,                # handle DD-MM-YYYY and DD/MM/YYYY
                infer_datetime_format=True    # auto-detect mixed styles
            )
            df['transaction_date'] = df['transaction_date'].dt.strftime('%Y-%m-%d')

            # diagnostics BEFORE cleaning
            q = {}
            q['original_rows'] = int(len(df))
            q['missing_customer_id'] = int(((df['customer_id'] == '') | df['customer_id'].isna()).sum())
            q['invalid_date'] = int(df['transaction_date'].isna().sum())
            q['missing_amount'] = int(df['amount'].isna().sum())
            q['negative_amount'] = int((df['amount'] < 0).sum())

            # cleaning
            if self.clean_mode == 'lenient':
                df = df[df['customer_id'] != '']
                df.loc[df['amount'].isna(), 'amount'] = 0.0
            else:
                df = df[df['customer_id'] != '']
                df = df.dropna(subset=['transaction_date', 'amount'])
                df = df[df['amount'] >= 0]

            q['usable_rows'] = int(len(df))
            q['dropped_rows'] = int(q['original_rows'] - q['usable_rows'])

            self.raw = df.copy()
            self.data = df.reset_index(drop=True)
            self.quality = q
            self.rfm_data = None
            self._X = None
            self.last_plot_path = None
            return True

        except Exception as e:
            self.last_error = f"Parse error: {e}"
            return False

    # ---------------- RFM ----------------
    def calculate_rfm(self) -> pd.DataFrame:
        if self.data is None or self.data.empty:
            raise ValueError("No usable data. Upload a file first.")

        df = self.data.copy()
        df['transaction_date'] = pd.to_datetime(df['transaction_date'], errors='coerce')

        ref_date = df['transaction_date'].max() + pd.Timedelta(days=1)
        rfm = (
            df.groupby('customer_id')
              .agg({
                  'transaction_date': lambda x: (ref_date - x.max()).days,
                  'amount': ['count', 'sum']
              })
        )
        rfm.columns = ['Recency', 'Frequency', 'Monetary']
        rfm = rfm.reset_index()

        r_labels = f_labels = m_labels = [1, 2, 3, 4]
        r_quart = pd.qcut(rfm['Recency'], 4, labels=r_labels, duplicates='drop')
        f_quart = pd.qcut(rfm['Frequency'].rank(method='first'), 4, labels=f_labels, duplicates='drop')
        m_quart = pd.qcut(rfm['Monetary'].rank(method='first'), 4, labels=m_labels, duplicates='drop')

        r_score = 5 - r_quart.astype(int)
        f_score = f_quart.astype(int)
        m_score = m_quart.astype(int)

        rfm['R_Score']  = r_score
        rfm['F_Score']  = f_score
        rfm['M_Score']  = m_score
        rfm['RFM_Score'] = rfm['R_Score'] + rfm['F_Score'] + rfm['M_Score']

        def segment(row):
            if row['RFM_Score'] >= 10: return 'Champions'
            if row['RFM_Score'] >= 8:  return 'Loyal'
            if row['RFM_Score'] >= 6:  return 'Potential'
            if row['RFM_Score'] >= 4:  return 'At Risk'
            return 'Hibernating'

        rfm['Customer_Segment'] = rfm.apply(segment, axis=1)

        self.rfm_data = rfm
        return rfm

    # ---------------- Clustering ----------------
    def prepare_clustering_data(self, features=None):
        if self.rfm_data is None:
            raise ValueError("Calculate RFM first.")
        if features is None:
            features = ['Recency', 'Frequency', 'Monetary']
        self.features = features

        X = self.rfm_data[features].copy()
        self.scaler = StandardScaler()
        self._X = self.scaler.fit_transform(X)

    def perform_clustering(self, algorithm='kmeans', n_clusters=3, **kwargs):
        if self._X is None:
            self.prepare_clustering_data(self.features)

        if algorithm == 'dbscan':
            eps = float(kwargs.get('eps', 0.5))
            min_samples = int(kwargs.get('min_samples', 5))
            model = DBSCAN(eps=eps, min_samples=min_samples)
            labels = model.fit_predict(self._X)
        else:
            model = KMeans(n_clusters=int(n_clusters), n_init='auto', random_state=42)
            labels = model.fit_predict(self._X)

        self.rfm_data['Cluster'] = labels
        return model, labels, None

    def get_cluster_summary(self) -> pd.DataFrame:
        if self.rfm_data is None or 'Cluster' not in self.rfm_data.columns:
            raise ValueError("Run clustering first.")
        cols = ['Recency', 'Frequency', 'Monetary']
        summary = self.rfm_data.groupby('Cluster')[cols].mean().round(2)
        summary['Customers'] = self.rfm_data.groupby('Cluster').size()
        return summary.sort_index()

    # ---------------- Plot ----------------
    def _pca_2d(self):
        if self._X is None:
            self.prepare_clustering_data(self.features)
        pca = PCA(n_components=2, random_state=42)
        return pca.fit_transform(self._X)

    def save_cluster_plot(self, path: str):
        if self.rfm_data is None or 'Cluster' not in self.rfm_data.columns:
            raise ValueError("Run clustering first.")
        coords = self._pca_2d()
        labels = self.rfm_data['Cluster'].values

        plt.figure(figsize=(6.2, 4.6), dpi=140)
        for k in np.unique(labels):
            mask = labels == k
            plt.scatter(coords[mask, 0], coords[mask, 1], label=f'Cluster {k}', s=20, alpha=0.85)
        plt.title('Customer Clusters (PCA of RFM features)')
        plt.xlabel('PC1')
        plt.ylabel('PC2')
        plt.legend(loc='best', fontsize=8, frameon=True)
        plt.tight_layout()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        plt.savefig(path)
        plt.close()

    # ---------------- Export ----------------
    def export_results(self, path: str, fmt: str = 'xlsx'):
        if self.rfm_data is None:
            raise ValueError("Nothing to export. Calculate RFM first.")
        df = self.rfm_data.copy()
        if fmt == 'csv':
            df.to_csv(path, index=False)
        else:
            df.to_excel(path, index=False)

    # ---------------- Template Context ----------------
    def template_context(self):
        data_info = {}
        if self.raw is not None:
            data_info['original_records'] = int(len(self.raw))
            if 'transaction_date' in self.raw.columns:
                td = pd.to_datetime(self.raw['transaction_date'], errors='coerce')
                dmin, dmax = td.min(), td.max()
                data_info['date_range'] = f"{dmin.date()} to {dmax.date()}" if pd.notna(dmin) and pd.notna(dmax) else None
            if 'amount' in self.raw.columns:
                data_info['total_revenue'] = float(pd.to_numeric(self.raw['amount'], errors='coerce').sum())
            if 'customer_id' in self.raw.columns:
                data_info['unique_customers'] = int(self.raw['customer_id'].astype(str).nunique())
        if self.data is not None:
            data_info['usable_records'] = int(len(self.data))

        rfm_stats, rfm_preview, segment_dist, cluster_summary = None, None, None, None
        if self.rfm_data is not None:
            rfm = self.rfm_data
            rfm_stats = {
                'recency_mean': round(float(rfm['Recency'].mean()), 2),
                'frequency_mean': round(float(rfm['Frequency'].mean()), 2),
                'monetary_mean': round(float(rfm['Monetary'].mean()), 2),
                'total_customers': int(len(rfm))
            }
            cols = ['customer_id', 'Recency', 'Frequency', 'Monetary', 'Customer_Segment']
            cols = [c for c in cols if c in rfm.columns]
            rfm_preview = rfm[cols].head(20)
            segment_dist = rfm['Customer_Segment'].value_counts(dropna=False).to_dict()
            if 'Cluster' in rfm.columns:
                cluster_summary = self.get_cluster_summary()

        return {
            'data_info': data_info,
            'quality': self.quality or {},
            'rfm_stats': rfm_stats,
            'rfm_preview': rfm_preview,
            'segment_dist': segment_dist,
            'cluster_summary': cluster_summary
        }
