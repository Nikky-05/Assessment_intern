# Customer Segmentation Flask Web Application

A comprehensive web application for customer behavior analysis using RFM (Recency, Frequency, Monetary) analysis and machine learning clustering. Upload your customer transaction data and get actionable insights through interactive visualizations and downloadable reports.

## 🚀 Key Features

### Core Functionality
- **RFM Analysis**: Complete customer behavior analysis based on Recency, Frequency, and Monetary values
- **Multiple Clustering Algorithms**: 
  - K-Means clustering with configurable cluster count
  - DBSCAN clustering with epsilon and min-samples parameters
- **Interactive Web Interface**: No-JavaScript design for maximum compatibility
- **Flexible Feature Selection**: Choose which RFM components to use for clustering

### Analytics & Visualization
- **PCA 2D Scatter Plots**: Visualize customer clusters in reduced dimensional space
- **Cluster Summary Statistics**: Detailed metrics for each customer segment
- **Customer Segment Classification**: Automatic classification into Champions, Loyal, Potential, At Risk, and Hibernating segments
- **Data Overview Dashboard**: Transaction statistics, customer counts, date ranges, and revenue totals

### Data & Export
- **Multiple File Formats**: Support for CSV, Excel (.xlsx, .xls) files
- **Sample Data Integration**: Built-in sample dataset for testing
- **Export Options**: Download results as CSV or Excel files
- **Secure File Handling**: Automatic cleanup of temporary files

## 📋 Prerequisites

- Python 3.8 or higher (recommended)
- pip (Python package installer)
- Virtual environment (strongly recommended)

## 🛠️ Installation & Setup

### 1. Navigate to Project Directory
```bash
cd C:\Users\Asus\Downloads\Test\Assessment_intern
# Or wherever you extracted/cloned the project
```

### 2. Create Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
.\venv\Scripts\Activate.ps1

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python app.py
```

### 5. Access the Web Interface
Open your web browser and navigate to:
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

### 2. Application Workflow

#### Step 1: Upload Data
- Navigate to the upload page
- Choose your CSV/Excel file or use the sample dataset
- Files are automatically validated for required columns

#### Step 2: RFM Analysis
- Click "Calculate RFM" to compute customer metrics
- View RFM statistics and customer segment distribution
- Review the customer segment preview table

#### Step 3: Configure Clustering
- Select clustering algorithm (K-Means or DBSCAN)
- Choose features to include (Recency, Frequency, Monetary)
- Set algorithm-specific parameters:
  - **K-Means**: Number of clusters (default: 3)
  - **DBSCAN**: Epsilon value (default: 0.5) and minimum samples (default: 5)

#### Step 4: View Results
- **PCA Visualization**: Interactive 2D scatter plot showing customer clusters
- **Cluster Summary**: Mean RFM values and customer count per cluster
- **Data Overview**: Complete dataset statistics and insights

#### Step 5: Export Results
- Download clustered customer data as CSV or Excel
- Files include all original data plus RFM scores and cluster assignments

## 📁 Project Architecture

```
Assessment_intern/
├── app.py                     # Main Flask web application
├── data_processor.py          # RFMAnalyzer class with core analytics logic
├── requirements.txt           # Python package dependencies
├── README.md                  # Project documentation
├── customer_transactions.csv  # Sample dataset for testing
├── Exam.ipynb                 # Jupyter notebook for exploratory analysis
│
├── templates/                 # Jinja2 HTML templates
│   ├── base.html             # Base template with Bootstrap styling
│   ├── index.html            # Landing page
│   ├── upload.html           # File upload interface
│   ├── analyze.html          # Main analysis dashboard
│   
│
├── outputs/                  # Generated analysis results
│   ├── cluster_summary.csv   # Cluster statistics and summaries
│   └── rfm_with_clusters.csv # Complete customer data with clusters
│
├── uploads/                  # Temporary file upload storage
│   └── clustered_*.csv       # User-uploaded datasets with results
│
├── static/                   # Static web assets (auto-generated)
│   ├── uploads/              # User file uploads
│   ├── downloads/            # Generated export files
│   └── plots/                # Generated visualization images
│
└── venv/                     # Python virtual environment
    ├── Lib/                  # Installed packages
    ├── Scripts/              # Environment activation scripts
    └── pyvenv.cfg            # Virtual environment configuration
```

## 🔧 Technical Dependencies

The application requires the following Python packages (see `requirements.txt` for exact versions):

- **Flask 3.0.3**: Modern web framework for the application backend
- **pandas 2.2.2**: Data manipulation, cleaning, and analysis
- **numpy 1.26.4**: Numerical computing and array operations
- **scikit-learn 1.5.1**: Machine learning algorithms (K-Means, DBSCAN, PCA, StandardScaler)
- **joblib 1.4.2**: Efficient model serialization and parallel computing
- **matplotlib 3.9.0**: Statistical plotting and visualization generation
- **openpyxl 3.1.2**: Excel file reading and writing support

## 🎯 RFM Analysis Methodology

### What is RFM?
**RFM** is a customer segmentation technique based on three key behavioral dimensions:

- **Recency (R)**: Days since the customer's last purchase
  - *Lower values = more recent = better customers*
- **Frequency (F)**: Total number of purchases made by the customer  
  - *Higher values = more loyal = better customers*
- **Monetary (M)**: Total amount spent by the customer
  - *Higher values = more valuable = better customers*

### Customer Segmentation Logic
The application automatically classifies customers into five segments based on their combined RFM scores:

1. **Champions** (RFM Score ≥ 10): Best customers - recent, frequent, high-value purchases
2. **Loyal** (RFM Score 8-9): Regular customers with good engagement
3. **Potential** (RFM Score 6-7): Customers with growth potential
4. **At Risk** (RFM Score 4-5): Previously engaged customers showing decline
5. **Hibernating** (RFM Score < 4): Inactive customers requiring re-engagement

### Machine Learning Enhancement
Beyond traditional RFM segmentation, the application uses unsupervised machine learning clustering to discover natural customer groupings:

- **K-Means Clustering**: Partitions customers into a predefined number of distinct groups
- **DBSCAN Clustering**: Automatically identifies clusters and outliers based on density
- **PCA Visualization**: Reduces multidimensional customer data to 2D for easy interpretation

## 🚨 Troubleshooting Guide

### Installation Issues

**Virtual Environment Problems:**
```bash
# If activation fails on Windows PowerShell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\venv\Scripts\Activate.ps1

# Alternative activation methods
.\venv\Scripts\activate.bat  # Command Prompt
source venv/bin/activate     # Linux/macOS
```

**Package Installation Failures:**
```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Install with verbose output for debugging
pip install -r requirements.txt --verbose

# Force reinstall if packages are corrupted
pip install -r requirements.txt --force-reinstall
```

### Application Runtime Issues

**Port Conflicts:**
- Default port 5000 may be occupied by other services
- Flask will automatically attempt to use alternative ports
- Check console output for the actual running port

**File Upload Problems:**
1. **Missing Columns**: Ensure your file contains exactly these columns:
   - `customer_id` - unique identifier for each customer
   - `transaction_date` - date in recognizable format
   - `amount` - numeric transaction value

2. **Date Format Issues**: 
   - Supported: DD/MM/YYYY, MM/DD/YYYY, YYYY-MM-DD
   - Invalid dates are automatically filtered out

3. **File Size Limits**: Maximum upload size is 16MB
   - For larger files, consider data preprocessing

**Memory Issues with Large Datasets:**
- Close unnecessary applications
- Consider sampling your data for initial analysis
- Upgrade system RAM for production use

### Data Quality Issues

**Common Data Problems:**
- **Duplicate Transactions**: Not automatically handled - clean your data first
- **Negative Amounts**: Automatically filtered out
- **Missing Customer IDs**: Rows with null customer_id are dropped
- **Invalid Dates**: Non-parseable dates are excluded from analysis

## 💡 Advanced Usage Tips

### Optimization Strategies
- **Feature Selection**: Start with all RFM features, then experiment with subsets
- **Cluster Count**: For K-Means, try 3-7 clusters initially
- **DBSCAN Parameters**: 
  - Lower `eps` values create more clusters
  - Higher `min_samples` reduces noise points

### Business Applications
- **Marketing Campaigns**: Use Champions and Loyal segments for premium offers
- **Re-engagement**: Target At-Risk customers with special promotions  
- **Customer Lifetime Value**: Prioritize resources on high Monetary value clusters
- **Retention Analysis**: Monitor customer migration between segments over time

### Data Export Usage
- **CRM Integration**: Import clustered customer data into your CRM system
- **Email Marketing**: Segment email lists based on RFM clusters
- **Business Intelligence**: Use exported data in Tableau, Power BI, or similar tools

## 🔧 Development & Customization

### Extending the Application
- **Custom Segments**: Modify the `segment()` function in `data_processor.py`
- **Additional Features**: Add new customer metrics beyond RFM
- **Algorithm Integration**: Implement other clustering algorithms (e.g., Gaussian Mixture Models)
- **UI Customization**: Modify templates in the `templates/` directory

### API Integration
The Flask application can be extended with REST API endpoints for programmatic access:
- Upload data via POST requests
- Retrieve analysis results as JSON
- Integrate with other business applications

## 🆘 Support & Contributing

### Getting Help
1. **Check Dependencies**: `pip list` to verify all packages are installed
2. **Verify Python Version**: `python --version` (must be 3.8+)  
3. **Review Console Output**: Check terminal for detailed error messages
4. **Test with Sample Data**: Use `customer_transactions.csv` for troubleshooting

### Reporting Issues
When reporting problems, include:
- Python version and operating system
- Complete error messages from console
- Sample of your input data (anonymized)
- Steps to reproduce the issue

## 📊 Performance Considerations

- **Small Datasets** (< 1K customers): Process in seconds
- **Medium Datasets** (1K-10K customers): 30 seconds to 2 minutes
- **Large Datasets** (10K+ customers): Several minutes, consider server deployment

## 📝 License & Usage

This project is designed for educational and commercial use. Feel free to:
- Modify the code for your specific needs
- Deploy in production environments
- Integrate with existing business systems
- Share improvements with the community

---

**Ready to unlock customer insights? Start analyzing! 🚀📊**
