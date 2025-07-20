import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


df = pd.read_csv("Online_Retail.csv", encoding='ISO-8859-1')
df.head()

df = df[df['CustomerID'].notna()]
df = df[~df['InvoiceNo'].astype(str).str.startswith('C')]
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
df['TotalPrice'] = df['Quantity'] * df['UnitPrice']

# Monthly Revenue
df['Month'] = df['InvoiceDate'].dt.to_period('M')
monthly_revenue = df.groupby('Month')['TotalPrice'].sum()

monthly_revenue.plot(kind='line', title='Monthly Revenue', figsize=(10, 4))
plt.ylabel("Revenue")
plt.xlabel("Month")
plt.grid(True)
plt.tight_layout()
plt.show()


# Top Products
top_products = df.groupby('Description')['TotalPrice'].sum().sort_values(ascending=False).head(10)

# Plot
top_products.plot(kind='bar', title='Top 10 Products by Revenue', figsize=(10, 4))
plt.ylabel("Revenue")
plt.xlabel("Product")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

# Sales by Country
sales_by_country = df.groupby('Country')['TotalPrice'].sum().sort_values(ascending=False)

# Filter for reasonable quantity range to avoid extreme outliers
sns.histplot(df[df['Quantity'] < 100]['Quantity'], bins=50, kde=True)
plt.title('Distribution of Quantity Ordered')
plt.xlabel('Quantity')
plt.ylabel('Frequency')
plt.tight_layout()
plt.show()

snapshot_date = df['InvoiceDate'].max() + pd.Timedelta(days=1)

rfm = df.groupby('CustomerID').agg({
    'InvoiceDate': lambda x: (snapshot_date - x.max()).days,
    'InvoiceNo': 'nunique',
    'TotalPrice': 'sum'
}).rename(columns={
    'InvoiceDate': 'Recency',
    'InvoiceNo': 'Frequency',
    'TotalPrice': 'Monetary'
})

rfm['R'] = pd.qcut(rfm['Recency'], 5, labels=[5,4,3,2,1])
rfm['F'] = pd.qcut(rfm['Frequency'].rank(method='first'), 5, labels=[1,2,3,4,5])
rfm['M'] = pd.qcut(rfm['Monetary'], 5, labels=[1,2,3,4,5])

rfm['RFM_Score'] = rfm['R'].astype(str) + rfm['F'].astype(str) + rfm['M'].astype(str)

def segment_customer(score):
    if score >= '555':
        return 'Champions'
    elif score[0] == '5':
        return 'Loyal Customers'
    elif score[1] == '5':
        return 'Frequent Buyers'
    elif score[2] == '5':
        return 'Big Spenders'
    else:
        return 'Others'

rfm['Segment'] = rfm['RFM_Score'].apply(segment_customer)

rfm.to_csv("rfm_segments.csv", index=True)
