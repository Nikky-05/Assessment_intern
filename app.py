from flask import (
    Flask, render_template, request, redirect, url_for,
    send_file, flash
)
import os
from datetime import datetime
from werkzeug.utils import secure_filename
import shutil
import time

from data_processor import RFMAnalyzer

# ------------------- Flask Setup -------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['DOWNLOAD_FOLDER'] = 'static/downloads'
app.config['PLOTS_FOLDER'] = 'static/plots'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

for d in (app.config['UPLOAD_FOLDER'], app.config['DOWNLOAD_FOLDER'], app.config['PLOTS_FOLDER']):
    os.makedirs(d, exist_ok=True)

ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

# Single analyzer instance for simplicity (for production, manage per-session)
analyzer = RFMAnalyzer()


def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ------------------- Routes -------------------
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':

        # Use bundled sample
        if 'use_sample' in request.form:
            sample_file = 'customer_transactions.csv'
            if os.path.exists(sample_file) and analyzer.load_data(sample_file, mode=request.form.get('clean_mode', 'strict')):
                flash('Sample data loaded successfully.', 'success')
                return redirect(url_for('analyze'))
            msg = getattr(analyzer, 'last_error', 'Sample data missing or failed to load.')
            flash(msg, 'danger')
            return redirect(url_for('upload'))

        if 'file' not in request.files:
            flash('No file part in request.', 'warning')
            return redirect(url_for('upload'))

        file = request.files['file']
        if file.filename == '':
            flash('No file selected.', 'warning')
            return redirect(url_for('upload'))

        if file and allowed_file(file.filename):
            clean_mode = request.form.get('clean_mode', 'strict')  # strict | lenient
            name, ext = os.path.splitext(secure_filename(file.filename))
            filename = f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(path)

            if analyzer.load_data(path, mode=clean_mode):
                flash(f'File uploaded. Cleaning mode: {clean_mode}.', 'success')
                return redirect(url_for('analyze'))

            # Show the detailed reason from the loader
            msg = getattr(analyzer, 'last_error', 'Failed to parse the file. Check columns and formats.')
            flash(msg, 'danger')
            return redirect(url_for('upload'))

        flash('Invalid format. Upload CSV or Excel.', 'danger')
        return redirect(url_for('upload'))

    return render_template('upload.html')


@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    if analyzer.raw is None:
        flash('Please upload a dataset first.', 'warning')
        return redirect(url_for('upload'))

    action = request.form.get('action') if request.method == 'POST' else None

    if action == 'calculate_rfm':
        try:
            analyzer.calculate_rfm()
            flash('RFM calculated.', 'success')
        except Exception as e:
            flash(f'RFM error: {e}', 'danger')

    if action == 'cluster':
        try:
            alg = request.form.get('algorithm', 'kmeans').lower()
            n_clusters = int(request.form.get('n_clusters', 3) or 3)
            features = request.form.getlist('features') or ['Recency', 'Frequency', 'Monetary']
            eps = float(request.form.get('eps', 0.5) or 0.5)
            min_samples = int(request.form.get('min_samples', 5) or 5)

            analyzer.prepare_clustering_data(features)
            if alg == 'dbscan':
                analyzer.perform_clustering(algorithm='dbscan', eps=eps, min_samples=min_samples)
            else:
                analyzer.perform_clustering(algorithm='kmeans', n_clusters=n_clusters)

            # Save plot
            plot_path = os.path.join(
                app.config['PLOTS_FOLDER'],
                f"cluster_plot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            )
            analyzer.save_cluster_plot(plot_path)
            analyzer.last_plot_path = plot_path
            flash('Clustering complete.', 'success')
        except Exception as e:
            flash(f'Clustering error: {e}', 'danger')

    if action == 'export_csv':
        try:
            filename = f'customer_segments_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            path = os.path.join(app.config['DOWNLOAD_FOLDER'], filename)
            analyzer.export_results(path, fmt='csv')
            return send_file(path, as_attachment=True, download_name=filename, mimetype='text/csv')
        except Exception as e:
            flash(f'Export CSV failed: {e}', 'danger')

    if action == 'export_xlsx':
        try:
            filename = f'customer_segments_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
            path = os.path.join(app.config['DOWNLOAD_FOLDER'], filename)
            analyzer.export_results(path, fmt='xlsx')
            return send_file(
                path, as_attachment=True, download_name=filename,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        except Exception as e:
            flash(f'Export Excel failed: {e}', 'danger')

    ctx = analyzer.template_context()

    ctx['plot_url'] = None
    if getattr(analyzer, 'last_plot_path', None) and os.path.exists(analyzer.last_plot_path):
        rel = analyzer.last_plot_path.replace('\\', '/')
        ctx['plot_url'] = '/' + rel + f"?t={int(time.time())}"

    return render_template('analyze.html', **ctx)


@app.route('/reset')
def reset():
    global analyzer
    try:
        for folder in (app.config['UPLOAD_FOLDER'], app.config['DOWNLOAD_FOLDER'], app.config['PLOTS_FOLDER']):
            for fn in os.listdir(folder):
                fp = os.path.join(folder, fn)
                if os.path.isfile(fp):
                    try:
                        os.remove(fp)
                    except Exception:
                        pass
        analyzer = RFMAnalyzer()
        flash('Session reset.', 'info')
    except Exception as e:
        flash(f'Reset failed: {e}', 'danger')
    return redirect(url_for('index'))


@app.errorhandler(413)
def too_large(e):
    flash('File too large. Limit is 16MB.', 'warning')
    return redirect(url_for('upload')), 413


@app.errorhandler(500)
def internal_error(e):
    flash('Internal error. Please try again.', 'danger')
    return redirect(url_for('index')), 500


if __name__ == '__main__':
    # Optional: copy sample CSV
    sample_file = 'customer_transactions.csv'
    if os.path.exists(sample_file):
        try:
            shutil.copy2(sample_file, os.path.join(app.config['UPLOAD_FOLDER'], 'sample_data.csv'))
        except Exception:
            pass

    app.run(debug=True, port=5000)
