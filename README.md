# Customer Segmentation Flask App

A web application for customer segmentation using RFM (Recency, Frequency, Monetary) analysis and K-Means clustering. Upload your customer transaction data and get actionable insights through interactive visualizations.

## 🚀 Features

- **RFM Analysis**: Analyze customer behavior based on Recency, Frequency, and Monetary values
- **K-Means Clustering**: Automatic customer segmentation using machine learning
- **Visual Analytics**: 
  - PCA 2D scatter plot for cluster visualization
  - HTML/CSS bar charts for cluster distribution
  - Summary tables with cluster statistics
- **File Support**: Upload CSV or Excel files
- **Export Results**: Download clustered customer data as CSV
- **Responsive Design**: Works on desktop, tablet, and mobile devices

## 📋 Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

## 🛠️ Installation

### 1. Clone or Download the Project
```bash
# If using git
git clone <your-repo-url>
cd Test

# Or download and extract the zip file to a folder named 'Test'
```

### 2. Create Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

## 🏃‍♂️ How to Run

### 1. Navigate to Project Directory
```bash
cd C:\Users\Asus\Downloads\Test
# Or wherever you extracted/cloned the project
```

### 2. Activate Virtual Environment
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Run the Flask Application
```bash
python app.py
```

### 4. Open in Browser
Open your web browser and go to:
```
http://127.0.0.1:5000
```

## 📊 Usage Instructions

### 1. Prepare Your Data
Your CSV/Excel file should contain these columns:
- `customer_id`: Unique identifier for each customer
- `transaction_date`: Date of transaction (format: DD/MM/YYYY or MM/DD/YYYY)
- `amount`: Transaction amount (numeric)

**Example data format:**
```csv
customer_id,transaction_date,amount
CUST001,01/01/2023,150.50
CUST001,15/01/2023,200.00
CUST002,05/01/2023,75.25
```

### 2. Upload and Analyze
1. Click "Choose File" and select your data file
2. Optionally select which RFM features to use for clustering
3. Click "Analyze" to process your data

### 3. View Results
- **Cluster Visualization**: See your customers plotted in 2D PCA space
- **Distribution Chart**: View the number of customers in each cluster
- **Summary Table**: Analyze average RFM values for each cluster
- **Download**: Export the clustered data for further analysis

## 📁 Project Structure

```
Test/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── artifacts/            # Pre-trained models and utilities
│   ├── feature_cols.json # Feature column names
│   ├── kmeans.joblib     # Pre-trained K-Means model
│   ├── model_meta.json   # Model metadata
│   ├── reference_date.json # Reference date for RFM calculation
│   ├── rfm_utils.py      # RFM calculation utilities
│   └── scaler.joblib     # Pre-trained data scaler
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── index.html        # Upload page
│   └── results.html      # Results page
├── outputs/              # Sample output files
│   ├── cluster_summary.csv
│   └── rfm_with_clusters.csv
├── uploads/              # Temporary upload directory
└── Exam.ipynb           # Jupyter notebook with analysis
```

## 🔧 Dependencies

- **Flask**: Web framework
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computing
- **scikit-learn**: Machine learning library
- **joblib**: Model serialization
- **matplotlib**: Plotting library

## 🎯 Understanding RFM Analysis

**RFM** stands for:
- **Recency**: How recently a customer made a purchase
- **Frequency**: How often they make purchases  
- **Monetary**: How much money they spend

This analysis helps identify:
- **Champions**: Best customers (recent, frequent, high-value)
- **Loyal Customers**: Regular buyers
- **Big Spenders**: High-value but infrequent buyers
- **At-Risk**: Previously good customers who haven't bought recently
- **Lost**: Customers who haven't purchased in a long time

## 🚨 Troubleshooting

### Common Issues:

1. **Port already in use**: If port 5000 is busy, the app will automatically try the next available port
2. **File upload errors**: Ensure your file has the required columns (`customer_id`, `transaction_date`, `amount`)
3. **Date format issues**: The app supports both DD/MM/YYYY and MM/DD/YYYY formats
4. **Virtual environment**: Always activate your virtual environment before running

### Error Messages:
- **"Please upload a CSV/Excel file"**: Select a valid file before clicking Analyze
- **Import errors**: Run `pip install -r requirements.txt` to install missing packages

## 💡 Tips

- **Sample Data**: Use the files in the `outputs/` directory to test the application
- **Large Files**: The app can handle large datasets, but processing time will increase
- **Feature Selection**: Experiment with different RFM feature combinations
- **Results**: Use the downloaded CSV file in your CRM or marketing tools

## 🆘 Support

If you encounter any issues:
1. Check that all dependencies are installed: `pip install -r requirements.txt`
2. Ensure your data file has the correct format
3. Verify your Python version is 3.7 or higher
4. Make sure the virtual environment is activated

## 📝 License

This project is for educational and commercial use. Feel free to modify and distribute as needed.

---

**Happy Analyzing! 📈**
