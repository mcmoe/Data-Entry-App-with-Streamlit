"""
@Created on: Sunday, 19 March 2023, 03:38:53 WAT

@author: Telrich Data
"""
# Importing required libraries
import psycopg2
import streamlit as st
import pandas as pd
import plotly.express as px
import base64
import io


# setting the page size and title
st.set_page_config(layout="wide", page_title='Database Data Entry Application')

# Function to connect to the database
def connect_db():
    # Set up a connection string
    username = st.secrets['user']
    password = st.secrets['pw']
    host = 'telrichserver.postgres.database.azure.com'
    database = 'phone_db'
    port = '5432'  # or your specified port number
    sslmode = 'require'  # or 'prefer' if you don't want to use SSL encryption
    conn_str = f"postgresql://{username}:{password}@{host}:{port}/{database}?sslmode={sslmode}"
    return conn_str

# Connecting to the database and initializing cursor
conn = psycopg2.connect(connect_db())
cur = conn.cursor()
connect_db()

# App Setup
st.markdown("<h1 style='text-align:center;'>Streamlit Data Entry App with Azure Postgres Database and Power BI Visualization</h1>", unsafe_allow_html=True)
st.markdown('<center><h2>A sample data entry application created for business purpose.</center></h2>', unsafe_allow_html=True)


# Split the page into two column
col1, col2 = st.columns([2, 8], gap='large')

# Creating Phone Brands and model
brand = {
    'Apple':[
        'iPhone 7', 'iPhone 8', 'iPhone X', 'iPhone 11', 'iPhone 12', 'iPhone 13', 'iPhone 14'
    ],
    'Oppo':[
        'Oppo Reno8', 'Oppo Reno7', 'Oppo Reno5', 'Oppo A96', 'Oppo A77', 'Oppo A57', 'Oppo A16'
    ],
    'Samsung': [
        'Galaxy F14', 'Galaxy S23', 'Galaxy Z Flip', 'Samsung S8', 'Samsung S9', 'Galaxy M14', 'Galaxy A54' 
    ],
    'Xiaomi': [
        'Xiaomi 13', 'Xiaomi 12T', 'Xiaomi 11', 'Xiaomi Mix 4', 'Redmi Note 12S', 'Redmi K60', 'Redmi Note 10'
    ]
}

# Sales Entry 
with col1.expander(label='', expanded=True):
    st.header('Sales Entry')
    phone_brand = st.selectbox('Select Brand', brand.keys())
    phone_model =  st.selectbox('Select Model', brand[phone_brand])
    purchase_date = st.date_input('Enter purchase date')
    sold_date = st.date_input('Enter sold date')
    cost_price = st.number_input('Enter cost price')
    sold_price = st.number_input('Enter sold price')

    # Saving the entry to the database.
    if st.button('Save Details'):
        query = f'''INSERT INTO phone_sales (phone_brand, phone_model, purchase_date, sold_date, sold_price, cost_price)
        VALUES ('{phone_brand}', '{phone_model}', '{purchase_date}', '{sold_date}', '{sold_price}', '{cost_price}')'''
        cur.execute(query)
        conn.commit()

# Counting the number of rows in the database table
row_count = '''
SELECT 
    COUNT(*) table_rows
FROM
    phone_sales
'''
table_rw = pd.read_sql_query(row_count, conn)
rw_num= table_rw['table_rows'][0]
col1.write(f'There are now {rw_num} rows in the table')

if rw_num >= 55:
    query = """
    DELETE FROM phone_sales
    WHERE id IN (
        SELECT id
        FROM phone_sales
        ORDER BY id 
        LIMIT 5
        );
    """
    cur.execute(query)
    conn.commit()

# Hiding the numbers on the table
hide = """
  <style>
  thead tr th:first-child {display:none}
  tbody th {display:none}
  </style>
  """
st.markdown(hide, True)
# Displaying the last five entries in the table
query = 'SELECT * FROM phone_sales ORDER BY id DESC LIMIT 5'
df2 = pd.read_sql_query(query, conn)

# VISUALIZING THE ENTRIES
# Query the database
query3 = '''
SELECT 
    phone_brand,
    SUM(profit) profit, 
    SUM(cost_price) cost_price, 
    SUM(sold_price) 
    sold_price 
FROM 
    phone_sales 
GROUP BY 
    phone_brand'''
                
# Profit By Brand
df3 = pd.read_sql_query(query3, conn)
fig1 = px.bar(df3, 'phone_brand', 'profit', text_auto=True, title='<b>Profit by Brand<b>', 
              labels={'profit':'', 'phone_brand':''})
fig1.update_yaxes(showticklabels=False)
fig1.update_traces(textposition='outside', cliponaxis=False)

# Sales and Cost Price by Brand
fig2 = px.bar(df3, 'phone_brand', ['cost_price', 'sold_price'], barmode='group', title='<b>Cost and Sales by Brand<b>',
              labels={'value':'', 'phone_brand':''}, text_auto=True)
fig2.update_traces(textposition='outside', cliponaxis=False)
fig2.update_yaxes(showticklabels=False)
fig2.update_layout(legend = dict(
                        orientation='v',
                        title='',
                        font = dict(
                        family="Courier",
                        size=12,
                        ),
                        bgcolor='olive',
                        bordercolor='blue',
                        borderwidth=.5
                    ))

# Display table latest entry and visualization
with col2.expander(label='', expanded=True):
    st.header('The last five entries in the table')
    st.table(df2)
    # newTableRw = pd.read_sql_query(row_count, conn)
    # newRwNum = newTableRw['table_rows'][0]
    # text1 = f'There are a total of {newRwNum} rows in the database'
    # st.write(text1)
    
    st.header('Entries Visualization')
    col21, col22 = st.columns(2)
    with col21:
        st.plotly_chart(fig1, use_container_width=True)
    with col22:
        st.plotly_chart(fig2, use_container_width=True)

# Download the data in the table        
all_data = '''
SELECT *
FROM phone_sales
'''
data = pd.read_sql_query(all_data, conn)

@st.cache_data        
# Function to download Excel file
def download_excel(df):
    excel_file = io.BytesIO()
    writer = pd.ExcelWriter(excel_file, engine='xlsxwriter')
    df.to_excel(writer, index=False)
    writer.save()
    b64 = base64.b64encode(excel_file.getvalue()).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="mydata.xlsx">Download Excel</a>'
    return href   

@st.cache_data
# Function to download JSON file
def download_json(df):
    json = df.to_json(indent=2)
    b64 = base64.b64encode(json.encode()).decode()
    href = f'<a href="data:application/json;base64,{b64}" download="mydata.json">Download JSON</a>'
    return href    
        
# Create a download button that downloads the DataFrame as a CSV file
with col1.expander('Download Data'):
    # Download csv file
    csv = data.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="mydata.csv">Download CSV</a>'
    # Download options
    st.markdown(href, unsafe_allow_html=True)
    st.markdown(download_excel(data), unsafe_allow_html=True)
    st.markdown(download_json(data), unsafe_allow_html=True)
    
with col1.expander('Contact', expanded=True):
    st.image('telrich_logo.png', width=100)
    st.markdown("[LinkedIn](https://www.linkedin.com/in/goodrichokoro/) \
        | [Twitter](https://twitter.com/OkoroGoodrich) \
        | [GitHub](https://github.com/TelRich)", unsafe_allow_html=True)

with col2.expander('Documentation'):
    st.markdown("""
             Title: Streamlit Data Entry App with Azure Postgres Database and Power BI Visualization

            >**Introduction**:
            
            This documentation provides an overview of a data entry application developed using Streamlit and connected to an Azure Postgres database. 
            The app enables users to enter data that is stored in the database, and it includes a dynamic visualization that updates based on the latest entry. 
            Additionally, Power BI is connected to the same database to generate data visualizations.

            >**Technologies**:
            
            * Streamlit
            * Python
            * Azure Postgres Database
            * Power BI
            
            >**Functionality**:
            
            1. The data entry app allows users to input data and save it to an Azure Postgres database. The app provides a user-friendly interface for data entry, with input fields for various data points. 
            Once the user submits the data, it is stored in the database.

            2. The app also includes a dynamic visualization that updates in real-time based on the latest data entry. This provides users with immediate feedback on the data that they enter and allows for quick analysis.

            3. Furthermore, Power BI is connected to the same Azure Postgres database to generate data visualizations. This allows for more in-depth analysis of the data collected through the app, and provides additional insights for decision making.

            > **Conclusion**:
            
            The Streamlit data entry app with an Azure Postgres database and Power BI visualization provides a robust and user-friendly solution for data collection and analysis. The app's interface and dynamic visualization make data entry and analysis quick and efficient, 
            while the connection to Power BI allows for more in-depth analysis and visualization. Overall, this app provides a comprehensive solution for data collection and analysis needs.
             
             """)

st.markdown('<iframe title="Report Section" width="600" height="373.5" src="https://app.powerbi.com/view?r=eyJrIjoiNjI2MTYzNTMtOGZmZC00ZDA3LThkYTktYjJjN2U0MGQzYjYxIiwidCI6ImNlMzBlNGMzLWM4NjItNGVlZC1hMzdjLWU3NmJjODNhY2ZmYSJ9" frameborder="0" allowFullScreen="true"></iframe>', unsafe_allow_html=True)
    

# Close the database connection
cur.close()
conn.close()
