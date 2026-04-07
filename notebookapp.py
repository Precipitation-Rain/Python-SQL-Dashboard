import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title='Airline Dashboard',
    page_icon='✈️',
    layout='wide'
)

with st.sidebar:

    #  upload the file
    file = st.file_uploader('Upload the File' , type=['csv'])

    if file is  not None:
        st.markdown('---')


        # radio buttons
        button = st.radio('Navigate' ,
                options=[
                "🏠 Overview",
                "💰 Price Analysis",
                "✈️ Route & City",
                "🕐 Time Patterns",
                "🏢 Airline Comparison",
                "🔍 Data Explorer" 
                ])
        
        # page "🏠 Overview"

        df = pd.read_csv(file)


if file is not None:

    if button == '🏠 Overview':

        # can add info
        st.header('🏠 Overview')

        col1 , col2 , col3 , col4 ,col5,col6 = st.columns(6)


        # calculating total no of flights in datset
        with col1:
            no_of_flights = df.shape[0]
            st.metric("No of Flights" , value=no_of_flights)

        # no of airline
        with col2 :
            no_of_airlines = df['airline'].nunique()
            st.metric("No of airlines" , value=no_of_airlines)

        # no of airline
        with col3 :
            avg_duration = round(df['duration'].mean())
            st.metric("Avg Duration" , value=avg_duration)

        # no of airline
        with col4 :
            avg_ticket_price = round(df['price'].mean())
            st.metric("Avg Ticket Price" , value=avg_ticket_price)

        # no of airline
        with col5 :
            most_expensive = df['price'].max()
            st.metric("Most Expensive Ticket" , value=most_expensive)

        # no of airline
        with col6 :
            cheapest_ticket = df['price'].min()
            st.metric("Chepest Ticket" , value=cheapest_ticket)


        st.markdown('---')

        col1 , col2 = st.columns(2)
        with col1:
            #Flight share by airline
            flight_share = df.groupby('airline')['class'].count().reset_index(name='airline_share')
            flight_share['airline_share'] = flight_share['airline_share'] * 100 / no_of_flights

            fig = px.pie(flight_share , names= 'airline' , values= 'airline_share' , title='Flight share by airline')
            st.plotly_chart(fig)
        
        # Avg price by airline
        with col2:
            avg_price_by_airline = df.groupby('airline')['price'].mean().reset_index(name = 'avg_price')

            fig = px.bar(avg_price_by_airline , x = 'airline' , y = 'avg_price' , title='Avg price by airline')
            st.plotly_chart(fig)


        colm1 =  st.columns(1)

        # Avg price vs Days Left to departure
        with colm1[0]:
            avg_price_by_day_left = df.groupby('days_left')['price'].mean().reset_index(name = 'avg_price')

            fig = px.line(avg_price_by_day_left , x = 'days_left' , y = 'avg_price' , title='Avg price vs Days Left to departure')
            st.plotly_chart(fig)


        clm = st.columns(1)
        
        # Total flights per route
        with clm[0]:
            total_flight_per_route = df
            total_flight_per_route['route'] = df['source_city'] + '-' + df['destination_city']
            total_flight_per_route_count = total_flight_per_route.groupby('route')['class'].count().reset_index(name='count')

            fig = px.bar(total_flight_per_route_count , x = 'route' , y = 'count' , title = 'Total flights per route')
            st.plotly_chart(fig)

    elif button == '💰 Price Analysis':
        
        st.header('💰 Price Analysis')


        # Price distribution by airline
        fig = px.box(df , x = 'airline' , y='price' , title='Price distribution by airline')
        fig.update_layout(
        width=1000,
        height=700
        )
        st.plotly_chart(fig)


        # Histogram** — Price distribution overall
        fig = px.histogram(df , x='price' , title = 'Price distribution overall',nbins=90 )
        fig.update_layout(
        width=1000,
        height=700
        )
        st.plotly_chart(fig)


        # Avg price by number of stops
        avg_price_by_no_of_stops = df.groupby('stops')['price'].mean().reset_index()
        fig = px.bar(avg_price_by_no_of_stops , x = 'stops' , y='price' , title = 'Avg price by number of stops' )
        st.plotly_chart(fig)

        # Duration vs Price
        fig = px.scatter(df , x='duration' , y='price' , title = 'Duration vs Price',color='airline')
        fig.update_layout(
        width=1000,
        height=700
        )
        st.plotly_chart(fig,use_container_width=True)

        # Avg price: Source City × Destination City
        
        pivot_df = df.pivot_table(
            index = 'source_city' , 
            columns='destination_city',
            values= 'price',
            aggfunc='mean'
        )

        fig = px.imshow(pivot_df , title= 'Avg price: Source City × Destination City' , text_auto=True , color_continuous_scale='rainbow')
        fig.update_layout(
        width=1000,
        height=700
        )
        st.plotly_chart(fig , use_container_width=True)

    
    elif button == '✈️ Route & City':
        
        st.header('✈️ Route & City Analysis')

        # Number of flights: Source City × Destination City

        pivot_df = df.pivot_table(
            index = 'source_city' , 
            columns='destination_city',
            values= 'price',
            aggfunc='count'
        )

        fig = px.imshow(pivot_df , title= 'Number of flights: Source City × Destination City' , text_auto=True , color_continuous_scale='electric')
        fig.update_layout(
        width=1000,
        height=700
        )
        st.plotly_chart(fig , use_container_width=True)

        st.markdown('---')

        # Top 10 routes by avg price

        route_by_count = df
        route_by_count['route'] = df['source_city'] + '-' + df['destination_city']

        route_by_count = route_by_count.groupby('route')['class'].count().reset_index(name='count').sort_values(by = 'count' , ascending=True).head(10)

        fig = px.bar(route_by_count , x = 'count' , y='route' , title = 'Top 10 routes by avg price')
        fig.update_layout(
            width=1000,
            height=700
            )
        st.plotly_chart(fig)

        st.markdown('---')

        # Top 10 routes by flight count

        route_by_price = df
        route_by_price['route'] = df['source_city'] + '-' + df['destination_city']

        route_by_price = route_by_price.groupby('route')['price'].mean().reset_index(name='avg_price').sort_values(by = 'avg_price',ascending=True).head(10)

        fig = px.bar(route_by_price , x = 'avg_price' , y='route' , title = 'Top 10 routes by flight count')
        fig.update_layout(
            width=1000,
            height=700
            )
        st.plotly_chart(fig)

        st.markdown('---')

        # Avg duration per route

        avg_flight_duration = df
        avg_flight_duration['route'] = df['source_city'] + '-' + df['destination_city']

        avg_flight_duration = avg_flight_duration.groupby('route')['duration'].mean().reset_index(name='avg_duration').sort_values(by = 'avg_duration',ascending=True)

        fig = px.bar(avg_flight_duration , x = 'route' , y='avg_duration' , title = 'Avg duration per route')
        fig.update_layout(
            width=800,
            height=500
            )
        st.plotly_chart(fig)

        st.markdown('---')

        #  Stops breakdown per route
        stops_breakdown = df
        stops_breakdown['route'] = df['source_city'] + '-' + df['destination_city']
        stops_breakdown = stops_breakdown.groupby('route')['class'].count().reset_index(name='count')
        st.dataframe(df)

        fig = px.bar(stops_breakdown , x = 'route' , y='count' , title = 'Stops breakdown per route' )
        st.plotly_chart(fig)

    elif button == '🕐 Time Patterns':

        st.header('🕐 Time Patterns')
        st.markdown('---')

        col1 ,col2 = st.columns(2)

        with col1:
            # Flights count by Departure Time slot
            flight_count_by_departure = df.groupby('departure_time')['class'].count().reset_index(name ='flight_count')

            fig = px.bar(flight_count_by_departure , x ='departure_time' , y='flight_count' , title = 'Flights count by Departure Time slot')
            st.plotly_chart(fig)


        with col2:
            # Avg price by Departure Time slot

            Avg_price_by_departure = df.groupby('departure_time')['price'].mean().reset_index(name ='avg_price')
            Avg_price_by_departure['avg_price'] = round(Avg_price_by_departure['avg_price'])
            fig = px.bar(Avg_price_by_departure , x ='departure_time' , y='avg_price' , title = 'Avg price by Departure Time slot')
            st.plotly_chart(fig)


        st.markdown('---')
        colm1 , colm2 = st.columns(2)


        with colm1:
            # Flights count by Arrrival Time slot

            flight_count_by_arrival = df.groupby('arrival_time')['class'].count().reset_index(name ='flight_count')

            fig = px.bar(flight_count_by_arrival , x ='arrival_time' , y='flight_count' , title = 'Flights count by Arrival Time slot')
            st.plotly_chart(fig)

        with colm2:
            # Avg price by Departure Time slot

            Avg_price_by_arrival = df.groupby('arrival_time')['price'].mean().reset_index(name ='avg_price')
            Avg_price_by_arrival['avg_price'] = round(Avg_price_by_departure['avg_price'])
            fig = px.bar(Avg_price_by_arrival , x ='arrival_time' , y='avg_price' , title = 'Avg price by Arrival Time slot')
            st.plotly_chart(fig)

        st.markdown('---')

        # Departure Time × Arrival Time → flight count

        # st.subheader('Departure Time × Arrival Time → flight count')
        pivot_df = df.pivot_table(
            index = 'arrival_time' , 
            columns='departure_time',
            values= 'price',
            aggfunc='count'
        )

        fig = px.imshow(pivot_df , title= 'Departure Time × Arrival Time → flight count' , text_auto=True , color_continuous_scale='electric')
        fig.update_layout(
        width=1000,
        height=700
        )
        st.plotly_chart(fig , use_container_width=True)

        st.markdown('---')

        # Departure time breakdown per airline 

        departrure_time_per_airline = df.groupby(['airline' , 'departure_time'])['class'].count().reset_index(name = 'flight_count')

        fig = px.bar(departrure_time_per_airline , x = 'departure_time' , y = 'flight_count' , color = 'airline' , barmode='group' , title = 'Departure time breakdown per airline')
        st.plotly_chart(fig)

    elif button == '🏢 Airline Comparison':
        st.header('🏢 Airline Comparison')
        st.markdown('---')

        # Airline comparison across: avg price, avg duration, % direct flights, % business class, flight count

        st.markdown('---')


        # Stops distribution per airline
        stop_destribution_per_airline = df.groupby(['airline' , 'stops'])['class'].count().reset_index(name = 'flight_count')
        stop_destribution_per_airline['flight_count'] = round(stop_destribution_per_airline['flight_count'],0)
        fig = px.bar(stop_destribution_per_airline , x = 'stops' , y = 'flight_count' , color = 'airline' , barmode='stack' , title = 'Stops distribution per airline')
        st.plotly_chart(fig)
        st.markdown('---')

        # Class split per airline
        class_count_by_airline = df.groupby(['class' , 'airline'])['price'].count().reset_index(name = 'flight_count')

        fig = px.bar(class_count_by_airline , x = 'class' , y='flight_count' , color = 'airline' , barmode='group' , title = 'Class split per airline')
        st.plotly_chart(fig)
        st.markdown('---')

        # Avg duration per airline

        avg_duration_per_airline = df.groupby('airline')['duration'].mean().reset_index(name = 'avg_duration')
        st.dataframe(avg_duration_per_airline)
        avg_duration_per_airline['avg_duration'] = round(avg_duration_per_airline['avg_duration'],0)
        fig = px.bar(avg_duration_per_airline , x = 'airline' , y = 'avg_duration' , title = 'Avg duration per airline')
        st.plotly_chart(fig)
        st.markdown('---')

        # Summary stats table: airline | total flights | avg price | avg duration | % direct | % business

        st.subheader('Summery Table')
        table =  df.groupby('airline')['class'].count().reset_index(name = 'total_flights')
        table['avg_price'] = pd.Series(df.groupby('airline')['price'].mean().values , name = 'avg_series')
        table['avg_duration'] = pd.Series(df.groupby('airline')['duration'].mean().values , name = 'avg_duration')
        table['percentage_share'] = table['total_flights'] * 100 / df.shape[0]
        st.dataframe(table)

    elif button == '🔍 Data Explorer':
        st.header('🔍 Data Explorer')

        col1 , col2 , col3 = st.columns(3)

        with col1 :
            airline = st.multiselect("Airline" , df['airline'].unique())

        with col2 :
            stops = st.multiselect("Stops" , df['stops'].unique())

        with col3:
            departure_time = st.multiselect("Departure Time" , df['departure_time'].unique())

        col1 , col2 , col3 = st.columns(3)

        with col1 :
            arrival_time = st.multiselect("Arrival Time" , df['arrival_time'].unique())

        with col2 :
            source_city = st.multiselect("Source City" , df['source_city'].unique())

        with col3:
            destination_city = st.multiselect("Destination City" , df['destination_city'].unique())

        col1 , col2 , col3 = st.columns(3)

        # # with col1 :
        # #     ticket_price = st.slider("Ticket Price" , max_value=df['price'].max() , min_value=df['price'].min())

        # with col2 :
        #     Class = st.multiselect("Class" , df['class'].unique())

        # # with col3:
        # #     days_left = st.multiselect("Days Left" , df['days_left'].unique())

        st.markdown('---')

        # filtering df


        filtered_df = df.copy()

        if airline:
            filtered_df = filtered_df[filtered_df['airline'].isin(airline)]

        if stops:
            filtered_df = filtered_df[filtered_df['stops'].isin(stops)]

        if departure_time:
            filtered_df = filtered_df[filtered_df['departure_time'].isin(departure_time)]

        if arrival_time:
            filtered_df = filtered_df[filtered_df['arrival_time'].isin(arrival_time)]

        # if Class:
        #     filtered_df = filtered_df[filtered_df['class'].isin(Class)]

        if source_city:
            filtered_df = filtered_df[filtered_df['source_city'].isin(source_city)]

        if destination_city:
            filtered_df = filtered_df[filtered_df['destination_city'].isin(destination_city)]



        col1 , col2 , col3 , col4 ,col5,col6 = st.columns(6)

        # calculating total no of flights in datset
        with col1:
            no_of_flights = filtered_df.shape[0]
            st.metric("No of Flights" , value=no_of_flights)

        # no of airline
        with col2 :
            no_of_airlines = filtered_df['airline'].nunique()
            st.metric("No of airlines" , value=no_of_airlines)

        # no of airline
        with col3 :
            avg_duration = round(filtered_df['duration'].mean())
            st.metric("Avg Duration" , value=avg_duration)

        # no of airline
        with col4 :
            avg_ticket_price = round(filtered_df['price'].mean())
            st.metric("Avg Ticket Price" , value=avg_ticket_price)

        # no of airline
        with col5 :
            most_expensive = filtered_df['price'].max()
            st.metric("Most Expensive Ticket" , value=most_expensive)

        # no of airline
        with col6 :
            cheapest_ticket = filtered_df['price'].min()
            st.metric("Chepest Ticket" , value=cheapest_ticket)

        st.markdown('---')

        st.dataframe(filtered_df)

else:
    st.info('Please enter the file')

    







        








    

    



    