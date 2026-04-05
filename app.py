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

    # st.title('💰 Price Analysis"')
    # st.markdown('---')

    # # section 1
    # st.subheader('Filters')
    # df = run_query("""SELECT DISTINCT(airline) FROM flight;""")
    # airline = st.multiselect('Airline' , options=df['airline'].unique() )

    # df = run_query("""SELECT DISTINCT(source_city) FROM flight;""")
    # souce = st.multiselect('Source City' , options=df['source_city'].unique() )

    # df = run_query("""SELECT DISTINCT(destination_city) FROM flight;""")
    # destination = st.multiselect('Destination City' , options=df['destination_city'].unique() )

    # df = run_query("""SELECT DISTINCT(departure_time) FROM flight;""")
    # departure_time = st.multiselect('Departure Time' , options=df['departure_time'].unique() )

    # df = run_query("""SELECT DISTINCT(stops) FROM flight;""")
    # stops = st.multiselect('Stops' , options=df['stops'].unique() )

    # df = run_query("""SELECT DISTINCT(arrival_time) FROM flight;""")
    # arrival_time = st.multiselect('Arrival Time' , options=df['arrival_time'].unique() )

    # df = run_query("""SELECT DISTINCT(class) FROM flight;""")
    # Class = st.multiselect('Class' , options=df['class'].unique() )

    # st.markdown('---')

    # # section 2
    # col1 , col2 = st.columns(2)

    # with col1:
    #     st.subheader('Price distribution by airline')
    #     df = run_query("""SELECT airline ,price FROM flight;""")

    #     fig , ax = plt.subplots()
    #     sns.boxplot(x=df['airline'] , y = df['price'] , ax = ax)
    #     st.pyplot(fig)
        

    # with col2:
    #     st.subheader('Price distribution overall')
    #     df = run_query("""SELECT price FROM flight;""")

    #     fig , ax = plt.subplots()
    #     sns.histplot(x=df['price'],bins=20,ax=ax , kde=True)
    #     # plt.xlim(0 , 50000)
    #     st.pyplot(fig)

    # colm1 , colm2 = st.columns(2)
    #  # **Bar Chart** — Avg price by number of stops (zero vs one vs two+)
    # with colm1:
    #     st.subheader('Avg price by number of stops')
    #     df = run_query("""SELECT stops , ROUND(AVG(price)) AS 'avg_price' FROM flight
    #             GROUP BY stops ;""")

    #     fig , ax = plt.subplots()
    #     sns.barplot( x = df['stops'] , y= df['avg_price'] )
    #     st.pyplot(fig)

    # # **Scatter Plot** — Duration vs Price (colored by airline — do longer flights cost more?)
    # with colm2:
    #     st.subheader('Duration vs Price ')
    #     df = run_query("""SELECT duration , price FROM flight;""")

    #     fig , ax = plt.subplots()
    #     sns.scatterplot( x = df['duration'] , y= df['price'])
    #     st.pyplot(fig)

    # clm = st.columns(1)
    # #- **Line Chart** — Avg price vs Days Left (1–49), broken by class (Economy line vs Business line)
    # with clm[0]:
    #     st.subheader('Avg price vs Days Left')
    #     df1 = run_query("""SELECT days_left , AVG(price) AS 'avg_price' FROM flight
    #                         WHERE class = 'Economy'
    #                         GROUP BY days_left ;
    #                     """)
        
    #     df2 = run_query("""
    #                    SELECT days_left , AVG(price) AS 'avg_price' FROM flight
    #                     WHERE class = 'Business'
    #                     GROUP BY days_left ;
    #                     """)

    #     fig , ax = plt.subplots()
    #     sns.lineplot( x = df1['days_left'] , y= df1['avg_price'] )
    #     sns.lineplot( x = df2['days_left'] , y= df2['avg_price'] )
    #     st.pyplot(fig)

    # columns1 = st.columns(1)
    # with columns1[0]:
    #     st.subheader('Avg price: Source City × Destination City grid')
    #     df = run_query("""
    #             SELECT source_city , destination_city , avg(price) AS 'avg_price' FROM flight
    #             GROUP BY source_city , destination_city ;
    #             """)
        
    #     pivot_df = pd.pivot(
    #         data=df,
    #         index = 'source_city',
    #         columns='destination_city',
    #         values= 'avg_price'

    #     )

    #     fig , ax = plt.subplots()
    #     sns.heatmap(pivot_df)
    #     st.pyplot(fig)

    st.title('💰 Price Analysis')
    st.markdown('---')

    st.subheader('Filters')

    df = run_query("""SELECT DISTINCT(airline) FROM flight;""")
    airline = st.multiselect('Airline', options=df['airline'].unique(), key='pa_airline')

    df = run_query("""SELECT DISTINCT(source_city) FROM flight;""")
    source = st.multiselect('Source City', options=df['source_city'].unique(), key='pa_source')

    df = run_query("""SELECT DISTINCT(destination_city) FROM flight;""")
    destination = st.multiselect('Destination City', options=df['destination_city'].unique(), key='pa_destination')

    df = run_query("""SELECT DISTINCT(departure_time) FROM flight;""")
    departure_time = st.multiselect('Departure Time', options=df['departure_time'].unique(), key='pa_departure')

    df = run_query("""SELECT DISTINCT(stops) FROM flight;""")
    stops = st.multiselect('Stops', options=df['stops'].unique(), key='pa_stops')

    df = run_query("""SELECT DISTINCT(arrival_time) FROM flight;""")
    arrival_time = st.multiselect('Arrival Time', options=df['arrival_time'].unique(), key='pa_arrival')

    df = run_query("""SELECT DISTINCT(class) FROM flight;""")
    Class = st.multiselect('Class', options=df['class'].unique(), key='pa_class')

    # Clear button — only clears Price Analysis filters
    if st.button("🗑️ Clear All Filters", key='pa_clear'):
        for key in ['pa_airline', 'pa_source', 'pa_destination',
                    'pa_departure', 'pa_stops', 'pa_arrival', 'pa_class']:
            st.session_state[key] = []
        st.rerun()

    st.markdown('---')

    # Build WHERE clause
    conditions = []

    if airline:
        vals = ', '.join(f"'{a}'" for a in airline)
        conditions.append(f"airline IN ({vals})")

    if source:
        vals = ', '.join(f"'{s}'" for s in source)
        conditions.append(f"source_city IN ({vals})")

    if destination:
        vals = ', '.join(f"'{d}'" for d in destination)
        conditions.append(f"destination_city IN ({vals})")

    if departure_time:
        vals = ', '.join(f"'{d}'" for d in departure_time)
        conditions.append(f"departure_time IN ({vals})")

    if stops:
        vals = ', '.join(f"'{s}'" for s in stops)
        conditions.append(f"stops IN ({vals})")

    if arrival_time:
        vals = ', '.join(f"'{a}'" for a in arrival_time)
        conditions.append(f"arrival_time IN ({vals})")

    if Class:
        vals = ', '.join(f"'{c}'" for c in Class)
        conditions.append(f"class IN ({vals})")

    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

    # Charts
    col1, col2 = st.columns(2)

    with col1:
        st.subheader('Price distribution by airline')
        df = run_query(f"""SELECT airline, price FROM flight {where_clause};""")
        fig, ax = plt.subplots()
        sns.boxplot(x=df['airline'], y=df['price'], ax=ax)
        st.pyplot(fig)

    with col2:
        st.subheader('Price distribution overall')
        df = run_query(f"""SELECT price FROM flight {where_clause};""")
        fig, ax = plt.subplots()
        sns.histplot(x=df['price'], bins=20, ax=ax, kde=True)
        st.pyplot(fig)

    colm1, colm2 = st.columns(2)

    with colm1:
        st.subheader('Avg price by number of stops')
        df = run_query(f"""SELECT stops, ROUND(AVG(price)) AS 'avg_price' 
                FROM flight {where_clause} GROUP BY stops;""")
        fig, ax = plt.subplots()
        sns.barplot(x=df['stops'], y=df['avg_price'])
        st.pyplot(fig)

    with colm2:
        st.subheader('Duration vs Price')
        df = run_query(f"""SELECT duration, price FROM flight {where_clause};""")
        fig, ax = plt.subplots()
        sns.scatterplot(x=df['duration'], y=df['price'])
        st.pyplot(fig)

    clm = st.columns(1)
    with clm[0]:
        st.subheader('Avg price vs Days Left')

        if not Class or 'Economy' in Class:
            eco_conditions = conditions + ["class = 'Economy'"]
            eco_where = "WHERE " + " AND ".join(eco_conditions)
            df1 = run_query(f"""SELECT days_left, AVG(price) AS 'avg_price'
                            FROM flight {eco_where} GROUP BY days_left;""")
        else:
            df1 = None

        if not Class or 'Business' in Class:
            bus_conditions = conditions + ["class = 'Business'"]
            bus_where = "WHERE " + " AND ".join(bus_conditions)
            df2 = run_query(f"""SELECT days_left, AVG(price) AS 'avg_price'
                            FROM flight {bus_where} GROUP BY days_left;""")
        else:
            df2 = None

        fig, ax = plt.subplots()
        if df1 is not None:
            sns.lineplot(x=df1['days_left'], y=df1['avg_price'], label='Economy')
        if df2 is not None:
            sns.lineplot(x=df2['days_left'], y=df2['avg_price'], label='Business')
        plt.legend()
        st.pyplot(fig)

    columns1 = st.columns(1)
    with columns1[0]:
        st.subheader('Avg price: Source City × Destination City grid')
        df = run_query(f"""SELECT source_city, destination_city, AVG(price) AS 'avg_price'
                FROM flight {where_clause} GROUP BY source_city, destination_city;""")
        pivot_df = pd.pivot(data=df, index='source_city', columns='destination_city', values='avg_price')
        fig, ax = plt.subplots()
        sns.heatmap(pivot_df)
        st.pyplot(fig)

if page == '✈️ Route & City':

    st.title('✈️ Route & City')
    st.markdown('---')
    
    st.subheader("Charts")
    # st.markdown('---')
    # **Heatmap** — Number of flights: Source City × Destination City (busiest routes)
    clm = st.columns(1)
    with clm[0]:
        st.subheader("Number of flights: Source City × Destination City")
        df = run_query("""

                    SELECT source_city , destination_city , COUNT(*) AS 'count' FROM flight
                    GROUP BY source_city , destination_city ;

                """)
        pivot_df = pd.pivot(data = df,index='source_city' , columns='destination_city' , values='count')

        fig , ax = plt.subplots()
        sns.heatmap(pivot_df)
        st.pyplot(fig)

    col1,col2 = st.columns(2)

    # **Horizontal Bar** — Top 10 routes by avg price
    with col1:

        st.subheader("Top 10 routes by avg price")
        df = run_query("""
                  SELECT  ROUND(AVG(price)) AS 'avg_price',
                    CONCAT(source_city , '-' ,destination_city) AS 'route' FROM flight
                    GROUP BY source_city , destination_city
                    ORDER BY avg_price DESC LIMIT 10;
                """)

        fig , ax = plt.subplots()
        sns.barplot(x=df['avg_price'] , y=df['route'])
        plt.xticks(rotation = 'vertical')
        st.pyplot(fig)

        ## - **Horizontal Bar** — Top 10 routes by flight count
    with col2:
        st.subheader("Top 10 routes by flight count")
        df = run_query("""
                SELECT  (COUNT(*)) AS 'count',
                CONCAT(source_city , '-' ,destination_city) AS 'route' FROM flight
                GROUP BY source_city , destination_city
                ORDER BY count DESC LIMIT 10;
                """)

        fig , ax = plt.subplots()
        sns.barplot(x=df['count'] , y=df['route'])
        plt.xticks(rotation = 'vertical')
        st.pyplot(fig)



    colm1 , colm2 = st.columns(2)

    ## - **Bar Chart** — Avg duration per route (which route takes longest)
    with colm1:
        st.subheader(" Avg duration per route ")
        df = run_query("""
                SELECT  FLOOR(AVG(duration)) AS 'avg_duration',
                CONCAT(source_city , '-' ,destination_city) AS 'route' FROM flight
                GROUP BY source_city , destination_city
                ORDER BY avg_duration DESC ;
                """)

        fig , ax = plt.subplots()
        sns.barplot(x=df['route'] , y=df['avg_duration'])
        plt.xticks(rotation = 'vertical')
        st.pyplot(fig)

    ## - - **Stacked Bar** — Stops breakdown per route (how many routes have direct flights)
    with colm2:
        st.subheader("Stops breakdown per rout")
        df = run_query("""
                SELECT stops , COUNT(*) AS 'count' FROM flight
                GROUP BY stops;
                """)

        fig , ax = plt.subplots()
        sns.barplot(x=df['stops'] , y=df['count'])
        plt.xticks(rotation = 'vertical')
        st.pyplot(fig)


if page == '🕐 Time Patterns':

    st.title("🕐 Time Patterns")
    st.markdown('---')

    col1 , col2 = st.columns(2)
    # - **Bar Chart** — Flights count by Departure Time slot (Morning, Evening, etc.)
    with col1:
        st.subheader("Flights count by Departure Time slot")
        df = run_query("""
                SELECT departure_time , COUNT(*) AS 'count'
                FROM flight
                GROUP BY departure_time ;
                """)

        fig , ax = plt.subplots()
        sns.barplot(x=df['departure_time'] , y=df['count'])
        plt.xticks(rotation = 'vertical')
        st.pyplot(fig)

    # - **Bar Chart** — Avg price by Departure Time slot (is Early Morning cheapest?)
    with col2:
        st.subheader("Avg price by Departure Time slot ")
        df = run_query("""
                SELECT departure_time , ROUND(AVG(price)) AS 'avg_price'
                FROM flight
                GROUP BY departure_time ;
                """)

        fig , ax = plt.subplots()
        sns.barplot(x=df['departure_time'] , y=df['avg_price'])
        plt.xticks(rotation = 'vertical')
        st.pyplot(fig)

    clm = st.columns(1)
    # - **Heatmap** — Departure Time × Arrival Time → flight count (which combos are most common)

    with clm[0]:
        st.subheader("Departure Time × Arrival Time → flight count")
        df = run_query("""
                    SELECT departure_time , arrival_time , COUNT(*) AS 'count'
                    FROM flight
                    GROUP BY departure_time , arrival_time;
                """)
        pivot_df = pd.pivot(data = df,index='departure_time' , columns='arrival_time' , values='count')

        fig , ax = plt.subplots()
        sns.heatmap(pivot_df)
        st.pyplot(fig)


    colm1 , colm2 = st.columns(2)
    # -- **Bar Chart** — Avg price by Arrival Time slot
    with colm1:
        st.subheader("Avg price by Arrival Time slot")
        df = run_query("""
                SELECT arrival_time , ROUND(AVG(price)) AS 'avg_price'
                FROM flight
                GROUP BY arrival_time;
                """)

        fig , ax = plt.subplots()
        sns.barplot(x=df['arrival_time'] , y=df['avg_price'])
        plt.xticks(rotation = 'vertical')
        st.pyplot(fig)

    # - **Grouped Bar** — Departure time breakdown per airline (does Indigo fly more at night?)
    with colm2:
        st.subheader("Departure time breakdown per airline")
        df = run_query("""
                SELECT  COUNT(*) AS 'count',
                CONCAT(airline ,'-' ,departure_time) AS 'airline-departureTime'
                FROM flight
                GROUP BY departure_time , airline ;
                """)

        fig , ax = plt.subplots()
        sns.barplot(x=df['airline-departureTime'] , y=df['count'])
        plt.xticks(rotation = 'vertical')
        st.pyplot(fig)

if page == '🏢 Airline Comparison':
    
    st.title("🏢 Airline Comparison")
    st.markdown('---')

    clm  = st.columns(1)
    # - **Radar Chart** — Airline comparison across: avg price, avg duration, % direct flights, % business class, flight count (normalized) — this is a premium, portfolio-worthy chart

    with clm[0]:
        st.subheader('Airline comparison across: avg price, avg duration, % direct flights, % business class, flight count')
        df = run_query("""SELECT airline , AVG(price) AS 'avg_price' , CEIL(AVG(duration)) AS 'avg_duration',
                        COUNT(*) * 100 / (SELECT COUNT(*) FROM flight) AS 'percentage_share',
                        COUNT(*) AS 'flight_count'  ,
                        SUM(CASE WHEN class = 'Economy' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) 
                                AS economy_percentage,
                        SUM(CASE WHEN class = 'Business' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) 
                                AS business_percentage
                        FROM flight
                        GROUP BY airline ;""")
        
        cols = ['avg_price', 'avg_duration', 'percentage_share', 
        'flight_count', 'economy_percentage', 'business_percentage']

        # Normalize (Min-Max scaling)
        df_norm = df.copy()
        for col in cols:
            df_norm[col] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())

        df_long = df_norm.melt(id_vars='airline' , var_name='category' , value_name='value')

        # radar chart
        fig = px.line_polar(df_long , r = 'value' , theta='category' , color='airline' , line_close=True)
        fig.update_traces(fill = 'toself')
        st.plotly_chart(fig)


    st.markdown('---')
    col1 , col2 = st.columns(2)

    # - **Stacked Bar** — Stops distribution per airline (who runs most direct flights)
    with col1:
        st.subheader('Stops distribution per airline')
        df = run_query("""SELECT airline , stops , count(*) AS 'no_of_flights' FROM flight
                    GROUP BY airline , stops ;""")
        df= pd.pivot(
            data = df,
            index='airline' , 
            columns='stops',
            values='no_of_flights'
        )

        fig , ax = plt.subplots()

        df.plot(
            kind = 'bar',
            stacked = True,
            ax = ax
        )
        st.pyplot(fig)

    # - **Grouped Bar** — Class split per airline (Economy vs Business count)
    with col2 :
        st.subheader('Class split per airline (Economy vs Business)')
        df = run_query("""SELECT class , airline , COUNT(*) AS 'no_of_flights'  
                    FROM flight
                    GROUP BY class , airline ;""")
        df= pd.pivot(
            data = df,
            index='airline' , 
            columns='class',
            values='no_of_flights'
        )

        fig , ax = plt.subplots()

        df.plot(
            kind = 'bar',
            ax = ax
        )
        st.pyplot(fig)

    st.markdown('---')
    colm = st.columns(1)
 
    # **Bar Chart** — Avg duration per airline
    with colm[0]:
        st.subheader('Avg duration per airline')
        df = run_query("""SELECT airline , AVG(duration) AS 'avg_duration'  
                    FROM flight
                    GROUP BY  airline ;""")

        fig , ax = plt.subplots()
        sns.barplot(x=df['airline'] , y = df['avg_duration'])
        st.pyplot(fig)


    st.markdown('---')
    # - **Table** — Summary stats table: airline | total flights | avg price | avg duration | % direct | % business
    colm1 = st.columns(1)
    with colm1[0]:
        st.subheader("📊 Airline Summary Table")

        df = run_query("""SELECT airline , COUNT(*) AS 'total_flights' , ROUND(AVG(price)) AS 'avg_price' , FLOOR(AVG       (duration)) AS 'avg_duration' ,
                        ROUND(COUNT(*) * 100 / (SELECT COUNT(*) FROM flight),2) AS 'market_cap_percentage',
                       SUM(CASE WHEN class = 'Economy' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) 
                                AS economy_percentage,
                        SUM(CASE WHEN class = 'Business' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) 
                                AS business_percentage,
                       MAX(price) AS 'max_ticket_price',
                       MIN(price) AS 'min_ticket_price'
                        FROM flight
                        GROUP BY airline;
                        """)
        
        df = df.rename(columns={
            'airline': 'Airline',
            'total_flights': 'Total Flights',
            'avg_price': 'Avg Price',
            'min_price': 'Min Price',
            'max_price': 'Max Price',
            'avg_duration': 'Avg Duration',
            'economy_percentage': '% Economy',
            'business_percentage': '% Business',
            'direct_percentage': '% Direct Flights',
            'market_share': 'Market Share'
            })
        
        st.dataframe(df)

if page == '🔍 Data Explorer':

    st.title("🔍 Data Explorer")
    st.markdown('---')

    st.subheader('Filters')

    df = run_query("""SELECT DISTINCT(airline) FROM flight;""")
    airline = st.multiselect('Airline', options=df['airline'].unique(), key='de_airline')

    df = run_query("""SELECT DISTINCT(source_city) FROM flight;""")
    source = st.multiselect('Source City', options=df['source_city'].unique(), key='de_source')

    df = run_query("""SELECT DISTINCT(destination_city) FROM flight;""")
    destination = st.multiselect('Destination City', options=df['destination_city'].unique(), key='de_destination')

    df = run_query("""SELECT DISTINCT(departure_time) FROM flight;""")
    departure_time = st.multiselect('Departure Time', options=df['departure_time'].unique(), key='de_departure')

    df = run_query("""SELECT DISTINCT(stops) FROM flight;""")
    stops = st.multiselect('Stops', options=df['stops'].unique(), key='de_stops')

    df = run_query("""SELECT DISTINCT(arrival_time) FROM flight;""")
    arrival_time = st.multiselect('Arrival Time', options=df['arrival_time'].unique(), key='de_arrival')

    df = run_query("""SELECT DISTINCT(class) FROM flight;""")
    Class = st.multiselect('Class', options=df['class'].unique(), key='de_class')

    df1 = run_query("""SELECT MAX(price) FROM flight;""")
    df2 = run_query("""SELECT MIN(price) FROM flight;""")
    max_price = int(df1.iloc[0, 0])
    min_price = int(df2.iloc[0, 0])
    price_range = st.slider("Price Range", min_value=min_price, max_value=max_price,
                             value=(min_price, max_price), key='de_price')

    df3 = run_query("""SELECT MAX(days_left) FROM flight;""")
    df4 = run_query("""SELECT MIN(days_left) FROM flight;""")
    max_days = int(df3.iloc[0, 0])
    min_days = int(df4.iloc[0, 0])
    days_range = st.slider("Days Left", min_value=min_days, max_value=max_days,
                            value=(min_days, max_days), key='de_days')

    # Clear button — only clears Data Explorer filters
    if st.button("🗑️ Clear All Filters", key='de_clear'):
        for key in ['de_airline', 'de_source', 'de_destination', 'de_departure',
                    'de_stops', 'de_arrival', 'de_class']:
            st.session_state[key] = []
        st.session_state['de_price'] = (min_price, max_price)
        st.session_state['de_days'] = (min_days, max_days)
        st.rerun()

    st.markdown('---')

    # Build WHERE clause
    conditions = []

    if airline:
        vals = ', '.join(f"'{a}'" for a in airline)
        conditions.append(f"airline IN ({vals})")

    if source:
        vals = ', '.join(f"'{s}'" for s in source)
        conditions.append(f"source_city IN ({vals})")

    if destination:
        vals = ', '.join(f"'{d}'" for d in destination)
        conditions.append(f"destination_city IN ({vals})")

    if departure_time:
        vals = ', '.join(f"'{d}'" for d in departure_time)
        conditions.append(f"departure_time IN ({vals})")

    if stops:
        vals = ', '.join(f"'{s}'" for s in stops)
        conditions.append(f"stops IN ({vals})")

    if arrival_time:
        vals = ', '.join(f"'{a}'" for a in arrival_time)
        conditions.append(f"arrival_time IN ({vals})")

    if Class:
        vals = ', '.join(f"'{c}'" for c in Class)
        conditions.append(f"class IN ({vals})")

    conditions.append(f"price BETWEEN {price_range[0]} AND {price_range[1]}")
    conditions.append(f"days_left BETWEEN {days_range[0]} AND {days_range[1]}")

    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

    # Filtered data
    df = run_query(f"SELECT * FROM flight {where_clause};")

    st.write(f"**{len(df)} flights found**")
    st.dataframe(df)

   
    col1 , col2 = st.columns(2)
    with col1 :
        data = df.to_csv(index=False).encode('utf-8')
        st.download_button("⬇️ Download Filtered Data", data=data, file_name='Flights_filtered.csv')

    with col2 :
        df = run_query("""SELECT * FROM flight;""")
        data = df.to_csv().encode('utf-8')
        st.download_button("⬇️ Download Entire Data" , data = data , file_name='Flights.csv')

    st.markdown('---')
    