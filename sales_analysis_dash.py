# premium_sales_dashboard.py
import pandas as pd
import numpy as np
from dash import Dash, dcc, html, Input, Output, callback
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ------------------ Load & Clean ------------------
file_path = "cleaned_sales_data.csv"
df = pd.read_csv(file_path)
df = df.drop_duplicates()
df['PurchaseDate'] = pd.to_datetime(df['PurchaseDate'], errors='coerce')
df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce').fillna(0).astype(int)
df['Price'] = pd.to_numeric(df['Price'], errors='coerce').fillna(0.0)
df['FeedbackScore'] = pd.to_numeric(df['FeedbackScore'], errors='coerce')
df['FeedbackScore'] = df['FeedbackScore'].fillna(df['FeedbackScore'].median())
df['Returned'] = df['Returned'].map(
    {True: True, 'True': True, 'true': True, 'Yes': True, 'Y': True,
     False: False, 'False': False, 'false': False, 'No': False, 'N': False}
).astype('boolean')
df['Sales'] = df['Quantity'] * df['Price']
df['Year'] = df['PurchaseDate'].dt.year
df['Month'] = df['PurchaseDate'].dt.month
df['MonthName'] = df['PurchaseDate'].dt.strftime('%Y-%m')
df['Weekday'] = df['PurchaseDate'].dt.day_name()
df['Quarter'] = df['PurchaseDate'].dt.quarter

# Get unique countries for dropdown
countries = ['All Countries'] + sorted(df['Country'].unique().tolist())

# ------------------ Dash App ------------------
app = Dash(__name__)
app.title = "Power BI Style Sales Analytics"

# Premium Power BI inspired styling
CARD_STYLE = {
    'padding': '20px 15px',
    'border-radius': '12px',
    'box-shadow': '0 6px 20px rgba(0,0,0,0.15)',
    'color': 'white',
    'textAlign': 'center',
    'margin': '10px',
    'flex': '1',
    'minWidth': '180px',
    'border': '1px solid rgba(255,255,255,0.15)',
    'background': 'rgba(255,255,255,0.08)',
    'backdropFilter': 'blur(12px)',
    'transition': 'all 0.3s ease',
    'minHeight': '100px'
}

CHART_CARD_STYLE = {
    'padding': '15px',
    'border-radius': '12px',
    'border': '1px solid rgba(255,255,255,0.15)',
    'margin': '12px',
    'backgroundColor': 'rgba(255,255,255,0.05)',
    'boxShadow': '0 4px 15px rgba(0,0,0,0.1)',
    'backdropFilter': 'blur(10px)'
}

HEADER_STYLE = {
    'background': 'linear-gradient(135deg, rgba(30,60,114,0.9), rgba(42,82,152,0.9))',
    'padding': '25px',
    'borderRadius': '12px',
    'marginBottom': '25px',
    'border': '1px solid rgba(255,255,255,0.2)',
    'boxShadow': '0 8px 25px rgba(0,0,0,0.2)'
}

# Function to remove chart background with Power BI style
def powerbi_style_chart(fig):
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        title_font_color='white',
        legend_font_color='white',
        legend=dict(
            bgcolor='rgba(255,255,255,0.1)',
            bordercolor='rgba(255,255,255,0.2)',
            borderwidth=1
        ),
        xaxis=dict(
            showgrid=True, 
            gridcolor='rgba(255,255,255,0.1)',
            linecolor='rgba(255,255,255,0.3)',
            tickfont=dict(color='white')
        ),
        yaxis=dict(
            showgrid=True, 
            gridcolor='rgba(255,255,255,0.1)',
            linecolor='rgba(255,255,255,0.3)',
            tickfont=dict(color='white')
        ),
        margin=dict(l=60, r=40, t=70, b=60),
        title_x=0.05,
        title_font_size=16,
        title_font_family='Segoe UI'
    )
    return fig

# Custom CSS styles
custom_css = """
<style>
    @keyframes gradientShift {
        0% { background-position: 0% 50% }
        50% { background-position: 100% 50% }
        100% { background-position: 0% 50% }
    }
    
    .kpi-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 30px rgba(0,0,0,0.25) !important;
    }
    
    .chart-container {
        transition: all 0.3s ease;
    }
    
    .chart-container:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.2) !important;
    }
</style>
"""

app.layout = html.Div(style={
        'background': 'linear-gradient(135deg, #0c0c0c 0%, #1a1a2e 25%, #16213e 50%, #0f3460 75%, #1e3c72 100%)',
        'minHeight': '100vh',
        'padding': '25px',
        'fontFamily': 'Segoe UI, Arial, sans-serif',
        'backgroundSize': '400% 400%',
        'animation': 'gradientShift 15s ease infinite'
    }, children=[
    
    # Custom CSS for animations
    html.Div([
        dcc.Markdown(custom_css, dangerously_allow_html=True)
    ]),

    # Header Section with Power BI Style
    html.Div(style=HEADER_STYLE, children=[
        html.Div(style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center', 'flexWrap': 'wrap'}, children=[
            html.Div(children=[
                html.H1("📊 Sales Analytics", style={
                    'color': 'white', 
                    'marginBottom': '8px', 
                    'fontSize': '36px',
                    'fontWeight': '600',
                    'background': 'linear-gradient(45deg, #00ffff, #00bfff)',
                    'backgroundClip': 'text',
                    'textFillColor': 'transparent',
                    'WebkitBackgroundClip': 'text',
                    'WebkitTextFillColor': 'transparent'
                }),
                html.P("Enterprise Sales Performance Dashboard • Real-time Analytics", style={
                    'color': 'rgba(255,255,255,0.8)',
                    'fontSize': '16px',
                    'marginBottom': '0'
                })
            ]),
            
            # Filter Section
            html.Div(style={'textAlign': 'right', 'marginTop': '10px'}, children=[
                html.Label("COUNTRY FILTER", style={
                    'color': 'rgba(255,255,255,0.7)', 
                    'fontSize': '12px', 
                    'fontWeight': 'bold',
                    'marginBottom': '5px',
                    'display': 'block',
                    'textTransform': 'uppercase',
                    'letterSpacing': '1px'
                }),
                dcc.Dropdown(
                    id='country-dropdown',
                    options=[{'label': country, 'value': country} for country in countries],
                    value='All Countries',
                    style={
                        'width': '280px',
                        'backgroundColor': 'rgba(255,255,255,0.95)',
                        'borderRadius': '8px',
                        'border': '2px solid rgba(255,255,255,0.3)'
                    },
                    clearable=False
                )
            ])
        ])
    ]),

    # KPI Cards Row - Power BI Style
    html.Div(style={
        'display': 'flex',
        'flexWrap': 'wrap',
        'justifyContent': 'space-around',
        'gap': '15px',
        'marginBottom': '30px'
    }, children=[
        html.Div(className='kpi-card', style={**CARD_STYLE, 
            'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'}, children=[
            html.Div("💰", style={'fontSize': '32px', 'marginBottom': '10px', 'opacity': '0.9'}),
            html.H3("TOTAL SALES", style={'margin': '8px 0', 'fontSize': '12px', 'fontWeight': '600', 'letterSpacing': '1px', 'opacity': '0.8'}),
            html.H2(id="total-sales-kpi", style={'margin': '8px 0', 'fontSize': '24px', 'fontWeight': '700'})
        ]),
        html.Div(className='kpi-card', style={**CARD_STYLE, 
            'background': 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)'}, children=[
            html.Div("👥", style={'fontSize': '32px', 'marginBottom': '10px', 'opacity': '0.9'}),
            html.H3("CUSTOMERS", style={'margin': '8px 0', 'fontSize': '12px', 'fontWeight': '600', 'letterSpacing': '1px', 'opacity': '0.8'}),
            html.H2(id="unique-customers-kpi", style={'margin': '8px 0', 'fontSize': '24px', 'fontWeight': '700'})
        ]),
        html.Div(className='kpi-card', style={**CARD_STYLE, 
            'background': 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)'}, children=[
            html.Div("📦", style={'fontSize': '32px', 'marginBottom': '10px', 'opacity': '0.9'}),
            html.H3("AVG ORDER VALUE", style={'margin': '8px 0', 'fontSize': '12px', 'fontWeight': '600', 'letterSpacing': '1px', 'opacity': '0.8'}),
            html.H2(id="avg-order-value-kpi", style={'margin': '8px 0', 'fontSize': '24px', 'fontWeight': '700'})
        ]),
        html.Div(className='kpi-card', style={**CARD_STYLE, 
            'background': 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)'}, children=[
            html.Div("🔄", style={'fontSize': '32px', 'marginBottom': '10px', 'opacity': '0.9'}),
            html.H3("RETURN RATE", style={'margin': '8px 0', 'fontSize': '12px', 'fontWeight': '600', 'letterSpacing': '1px', 'opacity': '0.8'}),
            html.H2(id="return-rate-kpi", style={'margin': '8px 0', 'fontSize': '24px', 'fontWeight': '700'})
        ]),
        html.Div(className='kpi-card', style={**CARD_STYLE, 
            'background': 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)'}, children=[
            html.Div("⭐", style={'fontSize': '32px', 'marginBottom': '10px', 'opacity': '0.9'}),
            html.H3("AVG RATING", style={'margin': '8px 0', 'fontSize': '12px', 'fontWeight': '600', 'letterSpacing': '1px', 'opacity': '0.8'}),
            html.H2(id="avg-rating-kpi", style={'margin': '8px 0', 'fontSize': '24px', 'fontWeight': '700'})
        ]),
    ]),

    # First Row of Charts
    html.Div(style={
        'display': 'flex',
        'flexWrap': 'wrap',
        'gap': '20px',
        'marginBottom': '20px'
    }, children=[
        # Sales Trend Chart
        html.Div(className='chart-container', style={**CHART_CARD_STYLE, 'flex': '2', 'minWidth': '600px'}, children=[
            dcc.Graph(id="sales-trend-chart")
        ]),
        # Satisfaction Gauge
        html.Div(className='chart-container', style={**CHART_CARD_STYLE, 'flex': '1', 'minWidth': '300px'}, children=[
            dcc.Graph(id="satisfaction-chart")
        ]),
    ]),

    # Second Row of Charts
    html.Div(style={
        'display': 'flex',
        'flexWrap': 'wrap',
        'gap': '20px',
        'marginBottom': '20px'
    }, children=[
        # Category Distribution
        html.Div(className='chart-container', style={**CHART_CARD_STYLE, 'flex': '1', 'minWidth': '300px'}, children=[
            dcc.Graph(id="category-distribution-chart")
        ]),
        # Top Products
        html.Div(className='chart-container', style={**CHART_CARD_STYLE, 'flex': '1', 'minWidth': '300px'}, children=[
            dcc.Graph(id="top-products-chart")
        ]),
        # Weekday Sales
        html.Div(className='chart-container', style={**CHART_CARD_STYLE, 'flex': '1', 'minWidth': '300px'}, children=[
            dcc.Graph(id="weekday-sales-chart")
        ]),
    ]),

    # Third Row of Charts
    html.Div(style={
        'display': 'flex',
        'flexWrap': 'wrap',
        'gap': '20px'
    }, children=[
        # Geographic Performance
        html.Div(className='chart-container', style={**CHART_CARD_STYLE, 'flex': '1', 'minWidth': '500px'}, children=[
            dcc.Graph(id="geographic-performance-chart")
        ]),
        # Return Analysis
        html.Div(className='chart-container', style={**CHART_CARD_STYLE, 'flex': '1', 'minWidth': '500px'}, children=[
            dcc.Graph(id="return-analysis-chart")
        ]),
    ])
])

# ------------------ Callbacks ------------------
@callback(
    [Output('total-sales-kpi', 'children'),
     Output('unique-customers-kpi', 'children'),
     Output('avg-order-value-kpi', 'children'),
     Output('return-rate-kpi', 'children'),
     Output('avg-rating-kpi', 'children'),
     Output('sales-trend-chart', 'figure'),
     Output('category-distribution-chart', 'figure'),
     Output('top-products-chart', 'figure'),
     Output('weekday-sales-chart', 'figure'),
     Output('satisfaction-chart', 'figure'),
     Output('geographic-performance-chart', 'figure'),
     Output('return-analysis-chart', 'figure')],
    [Input('country-dropdown', 'value')]
)
def update_dashboard(selected_country):
    # Filter data based on country selection
    if selected_country == 'All Countries':
        filtered_df = df
        title_suffix = "All Countries"
    else:
        filtered_df = df[df['Country'] == selected_country]
        title_suffix = selected_country
    
    # Calculate KPIs
    total_sales = filtered_df['Sales'].sum()
    unique_customers = filtered_df['CustomerID'].nunique()
    avg_order_value = filtered_df.groupby('CustomerID')['Sales'].sum().mean() if unique_customers > 0 else 0
    return_rate = filtered_df['Returned'].mean() if len(filtered_df) > 0 else 0
    avg_rating = filtered_df['FeedbackScore'].mean() if len(filtered_df) > 0 else 0
    
    # Format KPI values
    total_sales_formatted = f"${total_sales:,.0f}" if total_sales > 0 else "$0"
    unique_customers_formatted = f"{unique_customers:,}" if unique_customers > 0 else "0"
    avg_order_value_formatted = f"${avg_order_value:,.0f}" if avg_order_value > 0 else "$0"
    return_rate_formatted = f"{return_rate*100:.1f}%" if len(filtered_df) > 0 else "0.0%"
    avg_rating_formatted = f"{avg_rating:.1f}" if avg_rating > 0 else "0.0"
    
    # Chart 1: Sales Trend by Month (Professional Area Chart)
    monthly_data = filtered_df.groupby('MonthName').agg({
        'Sales': 'sum',
        'Quantity': 'sum',
        'CustomerID': 'nunique'
    }).reset_index()
    
    if not monthly_data.empty:
        monthly_data['MonthName'] = pd.to_datetime(monthly_data['MonthName'])
        monthly_data = monthly_data.sort_values('MonthName')
        monthly_data['MonthFormatted'] = monthly_data['MonthName'].dt.strftime('%b %Y')
        
        fig_trend = go.Figure()
        
        # Add area trace
        fig_trend.add_trace(go.Scatter(
            x=monthly_data['MonthFormatted'],
            y=monthly_data['Sales'],
            fill='tozeroy',
            mode='lines+markers',
            line=dict(width=4, color='#00ffff'),
            marker=dict(size=8, color='#00ffff'),
            fillcolor='rgba(0, 255, 255, 0.2)',
            name='Sales'
        ))
        
        fig_trend.update_layout(
            title=f"📈 Monthly Sales Trend - {title_suffix}",
            xaxis_title="Month",
            yaxis_title="Sales Amount",
            showlegend=False
        )
    else:
        fig_trend = go.Figure()
        fig_trend.add_annotation(text=f"No Sales Data Available for {title_suffix}", 
                               x=0.5, y=0.5, xref="paper", yref="paper", showarrow=False)
    
    # Chart 2: Category Distribution (Professional Donut Chart)
    category_data = filtered_df.groupby('Category').agg({
        'Sales': 'sum',
        'Quantity': 'sum'
    }).reset_index()
    
    if not category_data.empty:
        colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#feca57']
        
        fig_category = go.Figure(data=[go.Pie(
            labels=category_data['Category'],
            values=category_data['Sales'],
            hole=0.6,
            marker=dict(colors=colors),
            textinfo='percent+label',
            textposition='inside',
            hovertemplate='<b>%{label}</b><br>Sales: $%{value:,.0f}<br>Share: %{percent}<extra></extra>'
        )])
        
        fig_category.update_layout(
            title=f"📊 Sales Distribution by Category - {title_suffix}",
            showlegend=False
        )
    else:
        fig_category = go.Figure()
        fig_category.add_annotation(text=f"No Category Data for {title_suffix}", 
                                  x=0.5, y=0.5, xref="paper", yref="paper", showarrow=False)
    
    # Chart 3: Top Products (Professional Horizontal Bar)
    top_products = filtered_df.groupby('Product').agg({
        'Sales': 'sum',
        'Quantity': 'sum',
        'CustomerID': 'nunique'
    }).nlargest(8, 'Sales').reset_index()
    
    if not top_products.empty:
        fig_products = px.bar(
            top_products, 
            y='Product', 
            x='Sales',
            orientation='h',
            color='Sales',
            color_continuous_scale='viridis',
            labels={'Sales': 'Total Sales', 'Product': ''}
        )
        fig_products.update_layout(
            title=f"🏆 Top Performing Products - {title_suffix}",
            yaxis={'categoryorder':'total ascending'},
            showlegend=False
        )
    else:
        fig_products = go.Figure()
        fig_products.add_annotation(text=f"No Product Data for {title_suffix}", 
                                  x=0.5, y=0.5, xref="paper", yref="paper", showarrow=False)
    
    # Chart 4: Sales by Weekday (Professional Bar Chart)
    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekday_data = filtered_df.groupby('Weekday').agg({
        'Sales': 'sum',
        'Quantity': 'sum'
    }).reset_index()
    weekday_data['Weekday'] = pd.Categorical(weekday_data['Weekday'], categories=weekday_order, ordered=True)
    weekday_data = weekday_data.sort_values('Weekday')
    
    if not weekday_data.empty:
        fig_weekday = px.bar(
            weekday_data, 
            x='Weekday', 
            y='Sales',
            color='Sales',
            color_continuous_scale='plasma',
            labels={'Sales': 'Total Sales', 'Weekday': 'Day of Week'}
        )
        fig_weekday.update_layout(
            title=f"📅 Sales Performance by Weekday - {title_suffix}",
            showlegend=False
        )
    else:
        fig_weekday = go.Figure()
        fig_weekday.add_annotation(text=f"No Weekday Data for {title_suffix}", 
                                 x=0.5, y=0.5, xref="paper", yref="paper", showarrow=False)
    
    # Chart 5: Customer Satisfaction (Professional Gauge)
    if len(filtered_df) > 0:
        fig_satisfaction = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = avg_rating,
            domain = {'x': [0, 1], 'y': [0, 1]},
            number = {'suffix': "/5", 'font': {'size': 28}},
            delta = {'reference': 3.5, 'increasing': {'color': "#00ff00"}},
            gauge = {
                'axis': {'range': [None, 5], 'tickwidth': 2, 'tickcolor': "white"},
                'bar': {'color': "gold", 'thickness': 0.3},
                'bgcolor': "rgba(255,255,255,0.1)",
                'borderwidth': 2,
                'bordercolor': "rgba(255,255,255,0.3)",
                'steps': [
                    {'range': [0, 2], 'color': '#ff6b6b'},
                    {'range': [2, 4], 'color': '#feca57'},
                    {'range': [4, 5], 'color': '#48dbfb'}
                ],
                'threshold': {
                    'line': {'color': "white", 'width': 4},
                    'thickness': 0.75,
                    'value': 4.2
                }
            }
        ))
        
        fig_satisfaction.update_layout(
            title=f"⭐ Customer Satisfaction Score - {title_suffix}",
            font={'color': "white", 'family': "Segoe UI"},
            margin=dict(t=100, b=50)
        )
    else:
        fig_satisfaction = go.Figure()
        fig_satisfaction.add_annotation(text=f"No Rating Data for {title_suffix}", 
                                      x=0.5, y=0.5, xref="paper", yref="paper", showarrow=False)
    
    # Chart 6: Geographic Performance
    city_data = filtered_df.groupby('City').agg({
        'Sales': 'sum',
        'CustomerID': 'nunique'
    }).nlargest(10, 'Sales').reset_index()
    
    if not city_data.empty:
        fig_geographic = px.bar(
            city_data, 
            x='Sales', 
            y='City',
            orientation='h',
            color='CustomerID',
            color_continuous_scale='thermal',
            labels={'Sales': 'Total Sales', 'City': '', 'CustomerID': 'Customers'}
        )
        fig_geographic.update_layout(
            title=f"🌍 Top Performing Cities - {title_suffix}",
            yaxis={'categoryorder':'total ascending'},
            showlegend=True
        )
    else:
        fig_geographic = go.Figure()
        fig_geographic.add_annotation(text=f"No Geographic Data for {title_suffix}", 
                                    x=0.5, y=0.5, xref="paper", yref="paper", showarrow=False)
    
    # Chart 7: Return Analysis (Professional Scatter)
    return_data = filtered_df.groupby('Product').agg({
        'Returned': 'sum',
        'Quantity': 'sum',
        'Sales': 'sum'
    }).reset_index()
    return_data['Return Rate'] = (return_data['Returned'] / return_data['Quantity'] * 100).fillna(0)
    
    if not return_data.empty and len(return_data) > 1:
        fig_return = px.scatter(
            return_data,
            x='Quantity',
            y='Return Rate',
            size='Sales',
            color='Product',
            hover_name='Product',
            size_max=40,
            labels={'Quantity': 'Units Sold', 'Return Rate': 'Return Rate (%)', 'Sales': 'Total Sales'}
        )
        fig_return.update_layout(
            title=f"🔄 Product Return Analysis - {title_suffix}",
            showlegend=True
        )
    else:
        fig_return = go.Figure()
        fig_return.add_annotation(text=f"Insufficient Return Data for {title_suffix}", 
                                x=0.5, y=0.5, xref="paper", yref="paper", showarrow=False)
    
    # Apply Power BI styling to all charts
    charts = [fig_trend, fig_category, fig_products, fig_weekday, fig_geographic, fig_return, fig_satisfaction]
    for chart in charts:
        powerbi_style_chart(chart)
    
    return (
        total_sales_formatted,
        unique_customers_formatted,
        avg_order_value_formatted,
        return_rate_formatted,
        avg_rating_formatted,
        fig_trend,
        fig_category,
        fig_products,
        fig_weekday,
        fig_satisfaction,
        fig_geographic,
        fig_return
    )

if __name__ == "__main__":
    app.run(debug=True)