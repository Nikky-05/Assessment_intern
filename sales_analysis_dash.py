# # app.py
# import pandas as pd
# import numpy as np
# from dash import Dash, dcc, html
# import plotly.express as px

# # ------------------ Load & Clean ------------------
# file_path = "cleaned_sales_data.csv"  # Update path
# df = pd.read_csv(file_path)

# # Drop duplicates
# df = df.drop_duplicates()

# # Convert date
# df['PurchaseDate'] = pd.to_datetime(df['PurchaseDate'], errors='coerce')

# # Numeric conversions
# df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce').fillna(0).astype(int)
# df['Price'] = pd.to_numeric(df['Price'], errors='coerce').fillna(0.0)

# # Feedback
# df['FeedbackScore'] = pd.to_numeric(df['FeedbackScore'], errors='coerce')
# df['FeedbackScore'] = df['FeedbackScore'].fillna(df['FeedbackScore'].median())

# # Returned → boolean
# df['Returned'] = df['Returned'].map(
#     {True: True, 'True': True, 'true': True, 'Yes': True, 'Y': True,
#      False: False, 'False': False, 'false': False, 'No': False, 'N': False}
# ).astype('boolean')

# # Sales amount
# df['Sales'] = df['Quantity'] * df['Price']

# # Date parts
# df['Year'] = df['PurchaseDate'].dt.year
# df['Month'] = df['PurchaseDate'].dt.month
# df['MonthName'] = df['PurchaseDate'].dt.strftime('%Y-%m')
# df['Weekday'] = df['PurchaseDate'].dt.day_name()

# # ------------------ Insights ------------------
# total_sales = df['Sales'].sum()
# unique_customers = df['CustomerID'].nunique()
# avg_order_value = df.groupby('CustomerID')['Sales'].sum().mean()
# return_rate = df['Returned'].mean()

# # Top products and categories
# top_products = df.groupby('Product')['Sales'].sum().sort_values(ascending=False).head(10)
# top_categories = df.groupby('Category')['Sales'].sum().sort_values(ascending=False)

# # Monthly trend
# monthly_sales = df.groupby('MonthName')['Sales'].sum().reset_index()
# monthly_sales['MonthName'] = pd.to_datetime(monthly_sales['MonthName'])
# monthly_sales = monthly_sales.sort_values('MonthName')

# # City distribution
# city_sales = df.groupby('City')['Sales'].sum().sort_values(ascending=False).head(10)

# # Heatmap: Category vs Weekday
# pivot = df.pivot_table(index='Category', columns='Weekday', values='Sales',
#                        aggfunc='sum', fill_value=0)

# # Correlation matrix
# num_cols = ['Quantity','Price','Sales','FeedbackScore']
# corr = df[num_cols].corr()

# # ------------------ Dash App ------------------
# app = Dash(__name__)
# app.title = "Sales Dashboard"

# app.layout = html.Div([
#     html.H1("📊 Sales Analysis Dashboard", style={'textAlign':'center'}),
    
#     html.Div([
#         html.Div([
#             html.H3("Total Sales"),
#             html.P(f"${total_sales:,.2f}")
#         ], className="card"),
#         html.Div([
#             html.H3("Unique Customers"),
#             html.P(f"{unique_customers}")
#         ], className="card"),
#         html.Div([
#             html.H3("Avg Order Value"),
#             html.P(f"${avg_order_value:,.2f}")
#         ], className="card"),
#         html.Div([
#             html.H3("Return Rate"),
#             html.P(f"{return_rate*100:.2f}%")
#         ], className="card"),
#     ], style={'display':'flex', 'justifyContent':'space-around', 'margin':'20px 0'}),

#     dcc.Tabs([
#         dcc.Tab(label='Top Products', children=[
#             dcc.Graph(
#                 figure=px.bar(top_products, x=top_products.index, y=top_products.values,
#                               title="Top 10 Products by Sales")
#             )
#         ]),
#         dcc.Tab(label='Top Categories', children=[
#             dcc.Graph(
#                 figure=px.pie(top_categories, values=top_categories.values, names=top_categories.index,
#                               title="Sales Share by Category")
#             )
#         ]),
#         dcc.Tab(label='Monthly Sales', children=[
#             dcc.Graph(
#                 figure=px.line(monthly_sales, x='MonthName', y='Sales', markers=True,
#                                title="Monthly Sales Trend")
#             )
#         ]),
#         dcc.Tab(label='City Sales', children=[
#             dcc.Graph(
#                 figure=px.bar(city_sales, x=city_sales.index, y=city_sales.values,
#                               title="Top 10 Cities by Sales")
#             )
#         ]),
#         dcc.Tab(label='Category vs Weekday', children=[
#             dcc.Graph(
#                 figure=px.imshow(pivot, text_auto=True, aspect="auto",
#                                  title="Category vs Weekday Sales Heatmap")
#             )
#         ]),
#         dcc.Tab(label='Correlation Matrix', children=[
#             dcc.Graph(
#                 figure=px.imshow(corr, text_auto=True, title="Correlation Matrix")
#             )
#         ]),
#     ])
# ])

# if __name__ == "__main__":
#     app.run(debug=True)

#######################################################Complete  Dashboard code #################################################

# dashboard_no_bg_with_border.py
import pandas as pd
import numpy as np
from dash import Dash, dcc, html
import plotly.express as px

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

# ------------------ Insights ------------------
total_sales = df['Sales'].sum()
unique_customers = df['CustomerID'].nunique()
avg_order_value = df.groupby('CustomerID')['Sales'].sum().mean()
return_rate = df['Returned'].mean()

top_products = df.groupby('Product')['Sales'].sum().sort_values(ascending=False).head(10)
top_categories = df.groupby('Category')['Sales'].sum().sort_values(ascending=False)
monthly_sales = df.groupby('MonthName')['Sales'].sum().reset_index()
monthly_sales['MonthName'] = pd.to_datetime(monthly_sales['MonthName'])
monthly_sales = monthly_sales.sort_values('MonthName')
city_sales = df.groupby('City')['Sales'].sum().sort_values(ascending=False).head(10)
pivot = df.pivot_table(index='Category', columns='Weekday', values='Sales',
                       aggfunc='sum', fill_value=0)
num_cols = ['Quantity','Price','Sales','FeedbackScore']
corr = df[num_cols].corr()

# ------------------ Dash App ------------------
app = Dash(__name__)
app.title = "Sales Dashboard"

CARD_STYLE = {
    'padding': '20px',
    'border-radius': '15px',
    'box-shadow': '0 8px 20px rgba(0,0,0,0.3)',
    'color': 'white',
    'textAlign': 'center',
    'margin': '10px',
    'flex': '1',
    'minWidth': '180px'
}

CHART_CARD_STYLE = {
    'padding': '15px',
    'border-radius': '15px',
    'border': '2px solid #ffffff',  # white boundary
    'margin': '15px',
    'backgroundColor': 'transparent'
}

# Function to remove chart background
def transparent_chart(fig):
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white'
    )
    return fig

app.layout = html.Div(style={
        'background': 'linear-gradient(135deg, #667eea, #764ba2)',
        'minHeight': '100vh',
        'padding': '20px',
        'font-family': 'Arial, sans-serif'
    }, children=[

    html.H1("📊 Sales Dashboard", style={
        'textAlign':'center', 
        'color':'white', 
        'margin-bottom':'30px', 
        'text-shadow':'2px 2px 4px rgba(0,0,0,0.3)'
    }),

    # KPI Cards
    html.Div(style={'display':'flex', 'justifyContent':'space-around', 'flex-wrap':'wrap'}, children=[
        html.Div(style={**CARD_STYLE, 'background':'linear-gradient(45deg, #1abc9c, #16a085)'}, children=[
            html.H3("Total Sales"), html.H2(f"${total_sales:,.2f}")
        ]),
        html.Div(style={**CARD_STYLE, 'background':'linear-gradient(45deg, #3498db, #2980b9)'}, children=[
            html.H3("Unique Customers"), html.H2(f"{unique_customers}")
        ]),
        html.Div(style={**CARD_STYLE, 'background':'linear-gradient(45deg, #f39c12, #d35400)'}, children=[
            html.H3("Avg Order Value"), html.H2(f"${avg_order_value:,.2f}")
        ]),
        html.Div(style={**CARD_STYLE, 'background':'linear-gradient(45deg, #e74c3c, #c0392b)'}, children=[
            html.H3("Return Rate"), html.H2(f"{return_rate*100:.2f}%")
        ]),
    ]),

    # Charts in grid layout
    html.Div(style={'display':'flex', 'flex-wrap':'wrap', 'justifyContent':'space-around'}, children=[

        html.Div(style={**CHART_CARD_STYLE, 'flex':'1 1 45%'}, children=[
            dcc.Graph(
                figure=transparent_chart(
                    px.bar(top_products, x=top_products.index, y=top_products.values,
                           title="Top 10 Products by Sales", color=top_products.values)
                )
            )
        ]),

        html.Div(style={**CHART_CARD_STYLE, 'flex':'1 1 45%'}, children=[
            dcc.Graph(
                figure=transparent_chart(
                    px.pie(top_categories, values=top_categories.values, names=top_categories.index,
                           title="Sales Share by Category")
                )
            )
        ]),

        html.Div(style={**CHART_CARD_STYLE, 'flex':'1 1 45%'}, children=[
            dcc.Graph(
                figure=transparent_chart(
                    px.line(monthly_sales, x='MonthName', y='Sales', markers=True,
                            title="Monthly Sales Trend", color_discrete_sequence=["#ff0505"])
                )
            )
        ]),

        html.Div(style={**CHART_CARD_STYLE, 'flex':'1 1 45%'}, children=[
            dcc.Graph(
                figure=transparent_chart(
                    px.bar(city_sales, x=city_sales.index, y=city_sales.values,
                           title="Top 10 Cities by Sales", color=city_sales.values)
                )
            )
        ]),

        html.Div(style={**CHART_CARD_STYLE, 'flex':'1 1 45%'}, children=[
            dcc.Graph(
                figure=transparent_chart(
                    px.imshow(pivot, text_auto=True, aspect="auto",
                              title="Category vs Weekday Sales Heatmap", color_continuous_scale='Viridis')
                )
            )
        ]),

        html.Div(style={**CHART_CARD_STYLE, 'flex':'1 1 45%'}, children=[
            dcc.Graph(
                figure=transparent_chart(
                    px.imshow(corr, text_auto=True, color_continuous_scale='Cividis',
                              title="Correlation Matrix")
                )
            )
        ]),

    ])
])

if __name__ == "__main__":
    app.run(debug=True)
