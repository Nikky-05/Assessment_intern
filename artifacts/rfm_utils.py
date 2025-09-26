import pandas as pd

def compute_rfm(df, dayfirst=True, reference_date=None):
    """
    Compute RFM (Recency, Frequency, Monetary) analysis from transaction data.
    
    Parameters:
    - df: DataFrame with columns 'customer_id', 'transaction_date', 'amount'
    - dayfirst: bool, whether to parse dates with day first
    - reference_date: reference date for recency calculation, if None uses max date
    
    Returns:
    - DataFrame with customer_id, recency, frequency, monetary columns
    """
    # Parse transaction dates
    df = df.copy()
    df['transaction_date'] = pd.to_datetime(df['transaction_date'], dayfirst=dayfirst)
    
    # If reference_date is a string, parse it
    if isinstance(reference_date, str):
        reference_date = pd.to_datetime(reference_date)
    elif reference_date is None:
        reference_date = df['transaction_date'].max()
    
    # RFM calculation
    rfm = (df.groupby('customer_id')
           .agg(last_purchase=('transaction_date', 'max'),
                frequency=('transaction_date', 'count'),
                monetary=('amount', 'sum'))
           .reset_index())
    
    # Calculate recency (days since last purchase)
    rfm['recency'] = (reference_date - rfm['last_purchase']).dt.days
    
    # Select final columns
    rfm = rfm[['customer_id', 'recency', 'frequency', 'monetary']].copy()
    
    return rfm
