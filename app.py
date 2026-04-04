import streamlit as st
from db import run_query
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd


# page config
st.set_page_config(
    page_title='Airlines Dashboard',
    layout = 'wide',
    page_icon='✈️'
)

## sidebar
with st.sidebar:
    st.header("✈️ Airlines Dashboard")
    st.markdown("---")

    page = st.radio("Navigate" ,
                    [
        "🏠 Overview",
        "💰 Price Analysis",
        "✈️ Route & City",
        "🕐 Time Patterns",
        "🏢 Airline Comparison",
        "🔍 Data Explorer"
    ]
                    )
    
    st.markdown('---')

    # #filters
    # st.subheader('Filters')
    # st.markdown('---')

    st.success('🟢 Database Connected')


if page == "🏠 Overview":

    st.title("🏠 Overview")
    st.markdown('---')


## section 1
    st.header("Key Metrices")
    col1 , col2 ,col3 ,col4 ,col5 ,col6 = st.columns(6)

    with col1:
        df = run_query("SELECT COUNT(*) FROM flight")
        df = df.iloc[0,0]
        st.metric("Total Flights in DB" , df)

    with col2:
        df = run_query("SELECT COUNT(DISTINCT(airline)) FROM flight")
        df = df.iloc[0,0]
        st.metric("No of Airlines" , df)

    with col3:
        df = run_query("SELECT ROUND(AVG(price)) FROM flight")
        df = df.iloc[0,0]
        st.metric("Avg Price of Ticket" , df)

    with col4:
        df = run_query("SELECT (MAX(price)) FROM flight;")
        df = df.iloc[0,0]
        st.metric("Most Expensive Ticket" , df)

    with col5:
        df = run_query("SELECT (MIN(price)) FROM flight;")
        df = df.iloc[0,0]
        st.metric("Cheapest Ticket" , df)

    with col6:
        df = run_query("SELECT ROUND(AVG(duration)) FROM flight;")
        df = df.iloc[0,0]
        st.metric("Avg flight duration" , df)

    st.markdown('---')



## section 2
    st.header("Flight Distribution")
    col1 , col2 , = st.columns(2)

    #  Bar Chart — Avg price by airline (Economy vs Business side by side, grouped bar)
    with col1:
        st.subheader('Total flights per route')
        df = run_query("""SELECT source_city , destination_city ,
            CONCAT(source_city , '-' , destination_city) AS 'route',
            COUNT(*) AS 'no_of_flights' FROM flight
            GROUP BY source_city , destination_city
            ORDER BY COUNT(*) DESC""")
        fig, ax = plt.subplots()
        sns.barplot(x=df['route'] , y=df['no_of_flights'] , ax = ax)
        plt.xticks(rotation = 'vertical')
        st.pyplot(fig)

   

    # Bar Chart — Avg price by airline (Economy vs Business side by side, grouped bar)
    with col2:
        st.subheader('Avg price by airline')
        df = run_query("""SELECT airline , 
            ROUND(AVG(price)) AS 'price'
            FROM flight
            GROUP BY airline 
            ORDER BY price DESC ;""")
        fig, ax = plt.subplots()
        sns.barplot(x=df['airline'] , y=df['price'] , ax = ax)
        plt.xticks(rotation = 45)
        st.pyplot(fig)

    column1 , column2 = st.columns(2)

    ## Avg price by airline
    with column1:
        st.subheader('Avg price vs Days Left to departure')
        df = run_query("""SELECT days_left ,
                ROUND(AVG(price)) AS 'price' 
                FROM flight
                GROUP BY days_left ;""")
        fig, ax = plt.subplots()
        sns.lineplot(x=df['days_left'] , y=df['price'] , ax = ax)
        plt.xticks(rotation = 45)
        st.pyplot(fig)


    #Flight share by airline (market share %)
    with column2:
        ## using matplotlib piechart

        # st.subheader('Flight share by airline')
        # df = run_query("""SELECT airline , COUNT(*) AS 'total_flights',
        #         ( COUNT(*) * 100 / (SELECT COUNT(*) FROM flight) ) AS 'percentage_share'
        #         FROM flight
        #         GROUP BY airline;""")
        # fig, ax = plt.subplots()
        # counts = df['total_flights']
        # ax.pie(counts , labels = df['airline'],autopct='%.1f%%')
        # st.pyplot(fig)

        st.subheader('Flight share by airline')
        df = run_query("""SELECT airline , COUNT(*) AS 'total_flights',
                ( COUNT(*) * 100 / (SELECT COUNT(*) FROM flight) ) AS 'percentage_share'
                FROM flight
                GROUP BY airline;""")
        fig = px.pie(df , names = 'airline' , values='percentage_share')
        st.plotly_chart(fig)



if page == "💰 Price Analysis":

    st.title('💰 Price Analysis"')
    st.markdown('---')

    # section 1
    st.subheader('Filters')
    df = run_query("""SELECT DISTINCT(airline) FROM flight;""")
    airline = st.multiselect('Airline' , options=df['airline'].unique() )

    df = run_query("""SELECT DISTINCT(source_city) FROM flight;""")
    souce = st.multiselect('Source City' , options=df['source_city'].unique() )

    df = run_query("""SELECT DISTINCT(destination_city) FROM flight;""")
    destination = st.multiselect('Destination City' , options=df['destination_city'].unique() )

    df = run_query("""SELECT DISTINCT(departure_time) FROM flight;""")
    departure_time = st.multiselect('Departure Time' , options=df['departure_time'].unique() )

    df = run_query("""SELECT DISTINCT(stops) FROM flight;""")
    stops = st.multiselect('Stops' , options=df['stops'].unique() )

    df = run_query("""SELECT DISTINCT(arrival_time) FROM flight;""")
    arrival_time = st.multiselect('Arrival Time' , options=df['arrival_time'].unique() )

    df = run_query("""SELECT DISTINCT(class) FROM flight;""")
    Class = st.multiselect('Class' , options=df['class'].unique() )

    st.markdown('---')

    # section 2
    col1 , col2 = st.columns(2)

    with col1:
        st.subheader('Price distribution by airline')
        df = run_query("""SELECT airline ,price FROM flight;""")

        fig , ax = plt.subplots()
        sns.boxplot(x=df['airline'] , y = df['price'] , ax = ax)
        st.pyplot(fig)
        

    with col2:
        st.subheader('Price distribution overall')
        df = run_query("""SELECT price FROM flight;""")

        fig , ax = plt.subplots()
        sns.histplot(x=df['price'],bins=20,ax=ax , kde=True)
        # plt.xlim(0 , 50000)
        st.pyplot(fig)

    colm1 , colm2 = st.columns(2)
     # **Bar Chart** — Avg price by number of stops (zero vs one vs two+)
    with colm1:
        st.subheader('Avg price by number of stops')
        df = run_query("""SELECT stops , ROUND(AVG(price)) AS 'avg_price' FROM flight
                GROUP BY stops ;""")

        fig , ax = plt.subplots()
        sns.barplot( x = df['stops'] , y= df['avg_price'] )
        st.pyplot(fig)

    # **Scatter Plot** — Duration vs Price (colored by airline — do longer flights cost more?)
    with colm2:
        st.subheader('Duration vs Price ')
        df = run_query("""SELECT duration , price FROM flight;""")

        fig , ax = plt.subplots()
        sns.scatterplot( x = df['duration'] , y= df['price'])
        st.pyplot(fig)

    clm = st.columns(1)
    #- **Line Chart** — Avg price vs Days Left (1–49), broken by class (Economy line vs Business line)
    with clm[0]:
        st.subheader('Avg price vs Days Left')
        df1 = run_query("""SELECT days_left , AVG(price) AS 'avg_price' FROM flight
                            WHERE class = 'Economy'
                            GROUP BY days_left ;
                        """)
        
        df2 = run_query("""
                       SELECT days_left , AVG(price) AS 'avg_price' FROM flight
                        WHERE class = 'Business'
                        GROUP BY days_left ;
                        """)

        fig , ax = plt.subplots()
        sns.lineplot( x = df1['days_left'] , y= df1['avg_price'] )
        sns.lineplot( x = df2['days_left'] , y= df2['avg_price'] )
        st.pyplot(fig)

    columns1 = st.columns(1)
    with columns1[0]:
        st.subheader('Avg price: Source City × Destination City grid')
        df = run_query("""
                SELECT source_city , destination_city , avg(price) AS 'avg_price' FROM flight
                GROUP BY source_city , destination_city ;
                """)
        
        pivot_df = pd.pivot(
            data=df,
            index = 'source_city',
            columns='destination_city',
            values= 'avg_price'

        )

        fig , ax = plt.subplots()
        sns.heatmap(pivot_df)
        st.pyplot(fig)




    




    


    















    



    

    





# import streamlit as st

# st.set_page_config(page_title="Airlines Dashboard", layout="wide")

# # SIDEBAR
# with st.sidebar:
#     st.title("✈️ Airlines Dashboard")
#     st.markdown("---")
    
#     page = st.radio("Navigate", [
#         "🏠 Overview",
#         "💰 Price Analysis",
#         "✈️ Route & City",
#         "🕐 Time Patterns",
#         "🏢 Airline Comparison",
#         "🔍 Data Explorer"
#     ])
    
#     st.markdown("---")
    
#     # filters only on relevant pages
#     if page in ["💰 Price Analysis", "🔍 Data Explorer"]:
#         st.subheader("Filters")
        
#         airline = st.multiselect("Airline",
#             ["SpiceJet", "AirAsia", "Vistara", "GO_FIRST", "Indigo", "Air_India"])
        
#         flight_class = st.selectbox("Class", ["All", "Economy", "Business"])
        
#         stops = st.multiselect("Stops", ["zero", "one", "two_or_more"])
        
#         source = st.multiselect("Source City",
#             ["Delhi", "Mumbai", "Bangalore", "Kolkata", "Hyderabad", "Chennai"])
        
#         destination = st.multiselect("Destination City",
#             ["Delhi", "Mumbai", "Bangalore", "Kolkata", "Hyderabad", "Chennai"])

#     st.markdown("---")
#     st.success("🟢 DB Connected")


# # PAGE 1 — OVERVIEW
# if page == "🏠 Overview":
#     st.title("🏠 Overview")
#     # KPI cards
#     # Donut chart
#     # Bar chart - flights per route
#     # Grouped bar - price by airline+class
#     # Line - price vs days left


# # PAGE 2 — PRICE ANALYSIS
# elif page == "💰 Price Analysis":
#     st.title("💰 Price & Airline Analysis")
#     # Box plot - price by airline
#     # Histogram - price distribution
#     # Bar - price by stops
#     # Scatter - duration vs price
#     # Line - price vs days left by class
#     # Heatmap - route price


# # PAGE 3 — ROUTE & CITY
# elif page == "✈️ Route & City":
#     st.title("✈️ Route & City Analysis")
#     # Heatmap - flights per route
#     # Horizontal bar - top 10 routes by price
#     # Horizontal bar - top 10 routes by count
#     # Bar - avg duration per route
#     # Stacked bar - stops per route


# # PAGE 4 — TIME PATTERNS
# elif page == "🕐 Time Patterns":
#     st.title("🕐 Time Patterns")
#     # Bar - flights by departure time
#     # Bar - avg price by departure time
#     # Bar - avg price by arrival time
#     # Heatmap - departure x arrival time
#     # Grouped bar - departure time per airline


# # PAGE 5 — AIRLINE COMPARISON
# elif page == "🏢 Airline Comparison":
#     st.title("🏢 Airline Comparison")
#     # Radar chart - airline comparison
#     # Stacked bar - stops per airline
#     # Grouped bar - class split per airline
#     # Bar - avg duration per airline
#     # Summary stats table


# # PAGE 6 — DATA EXPLORER
# elif page == "🔍 Data Explorer":
#     st.title("🔍 Data Explorer")
#     # Filter summary metrics
#     # st.dataframe
#     # Download CSV button