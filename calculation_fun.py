import numpy as np
import pandas as pd
import datetime
from datetime import datetime
import time


site_id_df,seasonal_df,profile_label_df,cluster_parameter_df,detour_plan_df = None,None,None,None,None

def read_site_id_lookup():

    #df = pd.read_csv(f"data\\site_id_lookup.csv")
    return site_id_df

def read_seasonal_data():
    #df = pd.read_csv(f"data\\Seasonal Data.csv", index_col=False)
    
    return seasonal_df

def read_detour_plan():

    #df = pd.read_csv(f"data/detour_plan.csv")
    return detour_plan_df
def read_parameter():
    #cluster_parameter = pd.read_csv(f"data\\Cluster_Sites_Params.csv", index_col=False)
    return cluster_parameter_df

def seasonality_label(select_date):
    global profile_label_df
    df=profile_label_df
    covid_situation = df[df['Dates'] == select_date].iloc[:,9].values[0]
    day_of_week = df[df['Dates'] == select_date].iloc[:,4].values[0]
    school_open = df[df['Dates'] == select_date].iloc[:,5].values[0]
    university_open = df[df['Dates'] == select_date].iloc[:,6].values[0]
    shopping_season = df[df['Dates'] == select_date].iloc[:,7].values[0]
    return covid_situation, day_of_week, school_open, university_open,shopping_season

# Extract the parameters
def parameters_Main(SiteID):
    df=read_parameter()
    
    # Main site parameters
    Free_SpeedM= (df[df['Site'] == SiteID].iloc[:,2]).values[0]
    ScM=(df[df['Site'] == SiteID].iloc[:,3]).values[0]
    N_M=(df[df['Site'] == SiteID].iloc[:,4]).values[0]

    # Off site parameters
    Free_SpeedD=(df[df['Site'] == SiteID].iloc[:,5]).values[0]
    ScD=(df[df['Site'] == SiteID].iloc[:,6]).values[0]
    N_D=(df[df['Site'] == SiteID].iloc[:,7]).values[0]
    return Free_SpeedM, ScM, N_M, Free_SpeedD, ScD, N_D 

def block_site_to_site_id(BlockSite):
    
    # change the site block to site id
    #returns site_id
    df = read_site_id_lookup()
    site_id = df[df['Site Block'] == BlockSite].iloc[:,1].values[0]
    ramp_route = df[df['Site Block'] == BlockSite].iloc[:,17].values[0]
    return site_id

def block_site_to_ramp_id(BlockSite):
    
    df = read_site_id_lookup()
    ramp_id = df[df['Site Block'] == BlockSite].iloc[:,17].values[0]
    return ramp_id

def demand_veh_hr(COVID, DoW, School, University, Shopping, SiteID):
    df = read_seasonal_data()
    demand_veh_hr = (df[(df['COVID'] == COVID) &
                 (df['DoW'] == DoW) &
                 (df['School Open'] == School) &
                 (df['University Open'] == University) &
                 (df['Shopping'] == Shopping) &
                 (df['Site_ID'] == SiteID)].iloc[:,9:-2])
    
    #convert to datetime
    demand_veh_hr.columns = pd.to_datetime(demand_veh_hr.columns, format='%H:%M').time

    return demand_veh_hr


def demand_per_vehicle_transposed(InputData):

    demand_per_vehicle_transposed = InputData.T
    demand_per_vehicle_transposed.reset_index(inplace=True)
    demand_per_vehicle_transposed = demand_per_vehicle_transposed.rename(columns = {'index':'Time'})
    
    return demand_per_vehicle_transposed

def time_period_logic(Data, StartTime, EndTime):

    #start_day = datetime.strptime("23:45", '%H:%M').time()
    #end_day = datetime.strptime("00:15", '%H:%M').time()

    if StartTime >= EndTime:
        # Filter data between two time
        time_logic = Data.loc[(Data['Time'] > EndTime) &
                            (Data['Time'] <= StartTime)]
        return time_logic
    else:
        # Filter data between two time
        time_logic = Data.loc[(Data['Time'] > EndTime) |
                            (Data['Time'] <= StartTime)]
        return time_logic

def mainline_or_ramp(SiteID):
    df = read_site_id_lookup()
    mainline_or_ramp = (df[df['SiteID LookUp'] == SiteID].iloc[:,3]).values[0]
    return mainline_or_ramp
def assumed_capacity(SiteID):
    #print(SiteID)
    df = read_site_id_lookup()
    #print("assumed_capacity_df")
   
    assumed_capacity = (df[df['SiteID LookUp'] == SiteID].iloc[:,9]).values[0]
    #print(assumed_capacity)
    return assumed_capacity

def number_of_lanes(SiteID):
    df = read_site_id_lookup()
    number_of_lanes = (df[df['SiteID LookUp'] == SiteID].iloc[:,8]).values[0]
    return number_of_lanes

def closure_type_detector(SiteID, ClosedLane):
    n_of_lanes = number_of_lanes(SiteID)
    if ClosedLane >= number_of_lanes(SiteID):
        closure_type = "Full Closure"
    else:
        closure_type = "Not Full Closure"
    return closure_type

def tmp_capacity(SiteID):
    df = read_site_id_lookup()
    tmp_capacity = (df[df['SiteID LookUp'] == SiteID].iloc[:,16]).values[0]
    return tmp_capacity


def detoure_plan_ref(SiteID):
    df = read_site_id_lookup()
    detoure_plan_ref = (df[df['SiteID LookUp'] == SiteID].iloc[:,18]).values[0]
    return detoure_plan_ref 

def detour_capacity(SiteID):
    detour_ref = detoure_plan_ref(SiteID)
    df = read_detour_plan()
    detour_speed = (df[df['Ref'] == detour_ref].iloc[:,21]).values[0]
    return detour_speed  

def detour_distance(SiteID):
    detour_ref = detoure_plan_ref(SiteID)
    df = read_detour_plan()
    detour_distance = (df[df['Ref'] == detour_ref].iloc[:,3]).values[0]
    return detour_distance 

def detour_speed(SiteID):
    detour_ref = detoure_plan_ref(SiteID)
    df = read_detour_plan()
    detour_capacity = (df[df['Ref'] == detour_ref].iloc[:,4]).values[0]
    return detour_capacity  

def normal_distance(SiteID):
    detour_ref = detoure_plan_ref(SiteID)
    df = read_detour_plan()
    normal_distance = (df[df['Ref'] == detour_ref].iloc[:,5]).values[0]
    return normal_distance 

# Delay Calculation function
def delay_cal(DelayTable,SiteID):
 

    Free_SpeedM, ScM, N_M, Free_SpeedD, ScD, N_D  = parameters_Main(SiteID)
    

    # Main site time caluculation
    capacity_M=assumed_capacity(SiteID) #CM
   
    distant_M=normal_distance(SiteID) #LM
    
    
    for i in range(0,len(DelayTable)):
       volume_Mi=DelayTable.loc[i,"Demand (veh/hr)"]
       if volume_Mi < capacity_M:
          DelayTable.loc[i,'Time_Main'] = (1/Free_SpeedM+(1/ScM-1/Free_SpeedM)*(volume_Mi/capacity_M)**(N_M))*distant_M*3600
       else:
          DelayTable.loc[i,'Time_Main'] = (distant_M/ScM)*3600
    
    # Off site time caluculation
    # capacity_D=detour_capacity(SiteID) #CD
    capacity_D= DelayTable.loc[0,'Ramp Capacity (veh/hr)']
    distant_D=detour_distance(SiteID) #LD
    
    for i in range(0,len(DelayTable)):
       volume_Di=DelayTable.loc[i,"With Detour Flow (veh/hr)"]
       if volume_Di < capacity_D:
          DelayTable.loc[i,'Time_Detour'] = (1/Free_SpeedD+(1/ScD-1/Free_SpeedD)*(volume_Di/capacity_D)**(N_D))*distant_D*3600
       else:
          DelayTable.loc[i,'Time_Detour'] = (distant_D/ScM)*3600
    
    DelayTable['Bench']=0
    DelayTable['Delay']=DelayTable['Time_Detour']-DelayTable['Time_Main']
    DelayTable['New_Delay']=(DelayTable[["Delay","Bench"]].max(axis=1))/60
    
    DelayTable=DelayTable.drop(['Delay','Bench'], axis=1)

    return DelayTable

def capacity_per_veh(TimeLogic, DelayTable, SiteID,closed_lanes):
    # site_id = block_site_to_site_id(block_site)
    main_ramp = mainline_or_ramp(SiteID)
    assumed_cap = assumed_capacity(SiteID)
    lanes = number_of_lanes(SiteID)
    tmp_cap = tmp_capacity(SiteID)


    if main_ramp == "Ramp":
        capacity_veh = assumed_cap
    else:
        if closed_lanes >= lanes:
            capacity_veh = 0
        else:
            capacity_veh = (lanes - closed_lanes)*tmp_cap

    DelayTable.loc[:,'Capacity (veh)'] = capacity_veh
    TimeLogic.loc[:,'Capacity (veh)'] = assumed_cap

    DelayTable.update(TimeLogic)
    DelayTable.loc[:,'Capacity (veh)'] = DelayTable.loc[:,'Capacity (veh)'].replace(np.nan, 0)

    # DelayTable_update.to_csv('data/DelayTable.csv', index=False)
    return DelayTable

def full_closure_detour_demand(DelayTable, SiteID,closure_type):

    # site_id = block_site_to_site_id(block_site)
    main_ramp = mainline_or_ramp(SiteID)

    if main_ramp == "Ramp" and closure_type == "Full Closure":
        DelayTable.loc[:,'Full Closure Detour Demand'] = DelayTable.loc[:,'Demand (veh/hr)']*2
    else:
        DelayTable.loc[:,'Full Closure Detour Demand'] = 0
    return DelayTable

def queue_at_interval(DelayTable, SiteID,closure_type):

    # site_id = block_site_to_site_id(block_site)
    main_ramp = mainline_or_ramp(SiteID)

    DelayTable.loc[0,'Queue at Start of Interval'] = 0

    for x in range(len(DelayTable.index)):
        if DelayTable.loc[x,'Queue at Start of Interval'] >= 0:
            if main_ramp == "Ramp" and closure_type == "Full Closure":
                DelayTable.loc[x,'Queue at End of Interval'] = max((DelayTable.loc[x,'Demand (veh/hr)']*2) + DelayTable.loc[x,'Queue at Start of Interval'] - DelayTable.loc[x,'Capacity (veh)'],0)
                DelayTable.loc[x+1,'Queue at Start of Interval'] = max(DelayTable.loc[x,'Queue at End of Interval'],0)
            else:
                DelayTable.loc[x,'Queue at End of Interval'] = max((DelayTable.loc[x,'Demand (veh/hr)']) + DelayTable.loc[x,'Queue at Start of Interval'] - DelayTable.loc[x,'Capacity (veh)'],0)
                DelayTable.loc[x+1,'Queue at Start of Interval'] = max(DelayTable.loc[x,'Queue at End of Interval'],0)
        else:
            DelayTable.loc[x,'Queue at End of Interval'] = 0
            DelayTable.loc[x-1,'Queue at End of Interval'] = 0
            DelayTable.loc[x+1,'Queue at Start of Interval'] = 0
            DelayTable.loc[x,'Queue at Start of Interval'] = 0
    DelayTable = DelayTable.iloc[:-1 , :]

    return DelayTable

def total_average_delay(DelayTable, SiteID,closure_type):
    
    # site_id = block_site_to_site_id(block_site)
    main_ramp = mainline_or_ramp(SiteID)
    print(main_ramp)

    if main_ramp == "Mainline" and closure_type == "Full Closure":
        DelayTable.loc[:,'Total Average Delay (veh-mins)'] = 0
    else:
        DelayTable.loc[:,'Total Average Delay (veh-mins)'] = 15*DelayTable[['Queue at Start of Interval', 'Queue at End of Interval']].mean(axis=1)
    print(DelayTable["Queue at Start of Interval"])
    print()
    print(DelayTable["Queue at End of Interval"])
    print()
    if main_ramp == "Ramp" and closure_type == "Full Closure":
        DelayTable.loc[:,'Average Delay per Vehicle (min/veh)'] = DelayTable.loc[:,'Total Average Delay (veh-mins)']/(DelayTable.loc[:,'Demand (veh/hr)']*2)
    else:
        DelayTable.loc[:,'Average Delay per Vehicle (min/veh)'] = DelayTable.loc[:,'Total Average Delay (veh-mins)']/(DelayTable.loc[:,'Demand (veh/hr)'])

    # DelayTable = DelayTable.drop('Full Closure Detour Demand', axis=1)
    # DelayTable = DelayTable.drop('Queue at Start of Interval', axis=1)
    # DelayTable = DelayTable.drop('Queue at End of Interval', axis=1)
    # DelayTable = DelayTable.drop('Total Average Delay (veh-mins)', axis=1)

    return DelayTable

def with_detour_flow(DelayTable,end_time,start_time):

    if start_time >= end_time:
        for x in range(len(DelayTable.index)):
            if DelayTable.loc[x,'Time'] > end_time and DelayTable.loc[x,'Time'] < start_time :
                DelayTable.loc[x:,'With Detour Flow (veh/hr)'] = DelayTable.loc[x:,'Detour Demand (veh/hr)']
            else:
                DelayTable.loc[x:,'With Detour Flow (veh/hr)'] = DelayTable.loc[x:,'Demand (veh/hr)'] + DelayTable.loc[x:,'Detour Demand (veh/hr)']
        return DelayTable
    else:
        for x in range(len(DelayTable.index)):
            if DelayTable.loc[x,'Time'] > end_time or DelayTable.loc[x,'Time'] < start_time :
                DelayTable.loc[x:,'With Detour Flow (veh/hr)'] = DelayTable.loc[x:,'Detour Demand (veh/hr)']
            else:
                DelayTable.loc[x:,'With Detour Flow (veh/hr)'] = DelayTable.loc[x:,'Demand (veh/hr)'] + DelayTable.loc[x:,'Detour Demand (veh/hr)']
        return DelayTable


def capacity_per_veh_detour (TimeLogic, DelayTable, SiteID,closed_lanes):
    # site_id = block_site_to_site_id(block_site)
    main_ramp = mainline_or_ramp(SiteID)
    assumed_cap = assumed_capacity(SiteID)
    lanes = number_of_lanes(SiteID)
    tmp_cap = tmp_capacity(SiteID)


    if main_ramp == "Ramp":
        capacity_veh = assumed_cap
    else:
        if closed_lanes >= lanes:
            capacity_veh = 0
        else:
            capacity_veh = (lanes - closed_lanes)*tmp_cap

    DelayTable.loc[:,'Detour Capacity (veh)'] = capacity_veh
    TimeLogic.loc[:,'Detour Capacity (veh)'] = assumed_cap

    DelayTable.update(TimeLogic)
    DelayTable.loc[:,'Detour Capacity (veh)'] = DelayTable.loc[:,'Detour Capacity (veh)'].replace(np.nan, 0)

    # DelayTable_update.to_csv('data/DelayTable.csv', index=False)
    return DelayTable


def full_closure_detour_demand_detour(DelayTable, SiteID,closure_type):

    # site_id = block_site_to_site_id(block_site)
    main_ramp = mainline_or_ramp(SiteID)

    if main_ramp == "Ramp" and closure_type == "Full Closure":
        DelayTable.loc[:,'Detour Full Closure Detour Demand'] = DelayTable.loc[:,'With Detour Flow (veh/hr)']*2
    else:
        DelayTable.loc[:,'Detour Full Closure Detour Demand'] = 0
    return DelayTable

def queue_at_interval_detour(DelayTable, SiteID,end_time,start_time):

    # site_id = block_site_to_site_id(block_site)
    main_ramp = mainline_or_ramp(SiteID)

    DelayTable.loc[0,'Detour Queue at Start of Interval'] = 0

    if start_time >= end_time:
        for x in range(len(DelayTable.index)):
            if DelayTable.loc[x,'Time'] > end_time and DelayTable.loc[x,'Time'] < start_time :
                DelayTable.loc[x,'Detour Queue at End of Interval'] = max((DelayTable.loc[x,'Detour Demand (veh/hr)']) + DelayTable.loc[x,'Detour Queue at Start of Interval'] - DelayTable.loc[x,'Ramp Capacity (veh/hr)'],0)
                DelayTable.loc[x+1,'Detour Queue at Start of Interval'] = max(DelayTable.loc[x,'Detour Queue at End of Interval'],0)
            else:
                DelayTable.loc[x,'Detour Queue at End of Interval'] = max((DelayTable.loc[x,'Demand (veh/hr)'] + DelayTable.loc[x,'Detour Demand (veh/hr)']) + DelayTable.loc[x,'Detour Queue at Start of Interval'] - DelayTable.loc[x,'Ramp Capacity (veh/hr)'],0)
                DelayTable.loc[x+1,'Detour Queue at Start of Interval'] = max(DelayTable.loc[x,'Detour Queue at End of Interval'],0)

        DelayTable = DelayTable.iloc[:-1 , :]

        return DelayTable
    else:
        for x in range(len(DelayTable.index)):
            if DelayTable.loc[x,'Time'] > end_time or DelayTable.loc[x,'Time'] < start_time :
                DelayTable.loc[x,'Detour Queue at End of Interval'] = max((DelayTable.loc[x,'Detour Demand (veh/hr)']) + DelayTable.loc[x,'Detour Queue at Start of Interval'] - DelayTable.loc[x,'Ramp Capacity (veh/hr)'],0)
                DelayTable.loc[x+1,'Detour Queue at Start of Interval'] = max(DelayTable.loc[x,'Detour Queue at End of Interval'],0)
            else:
                DelayTable.loc[x,'Detour Queue at End of Interval'] = max((DelayTable.loc[x,'Demand (veh/hr)'] + DelayTable.loc[x,'Detour Demand (veh/hr)']) + DelayTable.loc[x,'Detour Queue at Start of Interval'] - DelayTable.loc[x,'Ramp Capacity (veh/hr)'],0)
                DelayTable.loc[x+1,'Detour Queue at Start of Interval'] = max(DelayTable.loc[x,'Detour Queue at End of Interval'],0)

        DelayTable = DelayTable.iloc[:-1 , :]

        return DelayTable  

def total_average_delay_detour(DelayTable, SiteID,closure_type):
    
    # site_id = block_site_to_site_id(block_site)
    main_ramp = mainline_or_ramp(SiteID)

    if main_ramp == "Mainline" and closure_type == "Full Closure":
        DelayTable.loc[:,'Detour Total Average Delay (veh-mins)'] = 0
    else:
        DelayTable.loc[:,'Detour Total Average Delay (veh-mins)'] = 15* (DelayTable['Detour Queue at Start of Interval'] + DelayTable['Detour Queue at End of Interval'])/2
        # DelayTable.loc[:,'Detour Total Average Delay (veh-mins)'] = 15*DelayTable[['Detour Queue at Start of Interval', 'Detour Queue at End of Interval']].mean(axis=1)

    if main_ramp == "Ramp" and closure_type == "Full Closure":
        DelayTable.loc[:,'Detour Average Delay per Vehicle (min/veh)'] = DelayTable.loc[:,'Detour Total Average Delay (veh-mins)']/(DelayTable.loc[:,'Detour Demand (veh/hr)'] + DelayTable.loc[:,'Demand (veh/hr)'])
    else:
        DelayTable.loc[:,'Detour Average Delay per Vehicle (min/veh)'] = 0
        # DelayTable.loc[:,'Detour Average Delay per Vehicle (min/veh)'] = DelayTable.loc[:,'Detour Total Average Delay (veh-mins)']/(DelayTable.loc[:,'Detour Demand (veh/hr)'])

    DelayTable = DelayTable.drop('Detour Full Closure Detour Demand', axis=1)
    DelayTable = DelayTable.drop('Detour Queue at Start of Interval', axis=1)
    DelayTable = DelayTable.drop('Detour Queue at End of Interval', axis=1)
    DelayTable = DelayTable.drop('Detour Total Average Delay (veh-mins)', axis=1)
    # DelayTable = DelayTable.drop('Ramp Capacity (veh/hr)', axis=1)

    return DelayTable

def plot_closure_route(DelayTable,start_time,end_time):

    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    start_time=start_time.strftime('%H:%M')
    end_time=end_time.strftime('%H:%M')

    # Define colors and warning text for main 
    Max_average_delay=DelayTable['Average Delay per Vehicle (min/veh)'].max()
    Max_capacity=DelayTable['Capacity (veh)'].max()  
    Max_flow=DelayTable['Demand (veh/hr)'].max()  
    colors = []
    if Max_average_delay >= 15 or Max_flow > Max_capacity:
         colors = 'red'
        #  title_colors = colors
        #  text1 = ": delay exceed 15 mins"
        #  text2 = " & max flow exceed the max capacity"
    elif Max_average_delay >= 5 and Max_average_delay < 15 and Max_flow > Max_capacity:
         colors = 'red'
        #  title_colors = colors
        #  text1 = ": delay between 5 to 15 mins"
        #  text2 = " & max flow exceed the max capacity"    
    elif Max_average_delay >= 5 and Max_average_delay < 15 and Max_flow < Max_capacity:
         colors = 'orange'
        #  title_colors = colors
        #  text1 = ": delay between 5 to 15 mins"
        #  text2 = " & max flow exceed the max capacity"
    elif Max_average_delay < 5 and Max_flow > Max_capacity:
         colors = 'red'   
        #  title_colors = colors
        #  text1 = ':'
        #  text2 = " max flow exceed the max capacity"
    else:
          # colors = 'rgba(0,0,0,0)'
         colors = 'green'
        #  title_colors = 'white'
        #  text1 = '' 
        #  text2 = ''     

    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.layout.template = 'plotly_dark'

    # Changing time format to hh:mm 
    DelayTable['Time2']=DelayTable['Time'].apply(lambda x: x.strftime('%H:%M'))

    # Adding condition: When capicity == 0, demand ==0
    conditions = [DelayTable["Capacity (veh)"]==0, DelayTable["Capacity (veh)"]>0]
    choices=[0,DelayTable["Demand (veh/hr)"]]
    DelayTable["Demand (veh/hr)2"]=np.select(conditions,choices, default=0)
    
    # Add traces
    fig.add_trace(
        go.Scatter(x=DelayTable['Time2'], y=DelayTable["Demand (veh/hr)2"], name="Demand (veh/hr)"),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=DelayTable['Time2'], y=DelayTable["Capacity (veh)"], name="Capacity (veh)"),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=DelayTable['Time2'], y=DelayTable["Average Delay per Vehicle (min/veh)"], name="Average Delay per Vehicle (min/veh)"),
        secondary_y=True,
    )


    # Add figure layout
    y_axis=max([Max_average_delay,Max_capacity,Max_flow])+500

    # Add figure layout
    fig.update_layout(
    title_text="Closure Route", #+ str(text1) + str(text2),
    font_family="Rockwell",
    # title_font_color=title_colors,
    legend=dict(
        title=None, orientation="h", y=1.02, yanchor="bottom", x=0.5, xanchor="center"
        ),       
    shapes=[
        dict(
        type="rect",xref="x",yref="y",
        x0=start_time, y0="0", x1=end_time, y1=y_axis,
        fillcolor="gray",opacity=0.4,line_width=0,layer="below"),
        ]   
    )


    # fig.update_layout(template="plotly_dark")

    # Set x-axis title
    fig.update_xaxes(title_text="Time Period Ending (15 mins interval)",showline=True,linewidth=3,linecolor=colors, mirror=True)

    # Set y-axes titles
    fig.update_yaxes(title_text="Flow(veh/hr)",
    rangemode="nonnegative",
    secondary_y=False)
    fig.update_yaxes(title_text="Average Delay (min/veh)",
    rangemode="nonnegative",
    secondary_y=True,
    showline=True,linewidth=3,linecolor=colors, mirror=True)

    
    return fig


def plot_closure_detour(DelayTable,start_time,end_time):

    start_time=start_time.strftime('%H:%M')
    end_time=end_time.strftime('%H:%M')

    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    # Define colors and warning text for detour
    Max_average_delay=DelayTable['Detour Average Delay per Vehicle (min/veh)'].max()
    Max_capacity=DelayTable['Ramp Capacity (veh/hr)'].max()  
    Max_flow=DelayTable['With Detour Flow (veh/hr)'].max()  
    colors = []
   
    if Max_average_delay >= 15 or Max_flow > Max_capacity:
         colors = 'red'
        #  title_colors = colors
        #  text1 = ": delay exceed 15 mins"
        #  text2 = " & max flow exceed the max capacity"
    elif Max_average_delay >= 5 and Max_average_delay < 15 and Max_flow > Max_capacity:
         colors = 'red'
        #  title_colors = colors
        #  text1 = ": delay between 5 to 15 mins"
        #  text2 = " & max flow exceed the max capacity"    
    elif Max_average_delay >= 5 and Max_average_delay < 15 and Max_flow < Max_capacity:
         colors = 'orange'
        #  title_colors = colors
        #  text1 = ": delay between 5 to 15 mins"
        #  text2 = " & max flow exceed the max capacity"
    elif Max_average_delay < 5 and Max_flow > Max_capacity:
         colors = 'red'   
        #  title_colors = colors
        #  text1 = ':'
        #  text2 = " max flow exceed the max capacity"
    else:
          # colors = 'rgba(0,0,0,0)'
         colors = 'green'
        #  title_colors = 'white'
        #  text1 = '' 
        #  text2 = ''        

    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.layout.template = 'plotly_dark'

    # Changing time format to hh:mm 
    DelayTable['Time2']=DelayTable['Time'].apply(lambda x: x.strftime('%H:%M'))

    # Add traces
    fig.add_trace(
        go.Scatter(x=DelayTable['Time2'], y=DelayTable["With Detour Flow (veh/hr)"], name="With Detour Flow (veh/hr)"),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=DelayTable['Time2'], y=DelayTable["Ramp Capacity (veh/hr)"], name="Ramp Capacity (veh/hr)"),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=DelayTable['Time2'], y=DelayTable["Detour Average Delay per Vehicle (min/veh)"], name="Detour Average Delay per Vehicle (min/veh)"),
        secondary_y=True,
    )
    # fig.add_trace(
    #     go.Scatter(x=DelayTable['Time'], y=DelayTable["New_Delay"], name="New Detour Average Delay per Vehicle (min/veh)"),
    #     secondary_y=True,
    # )

    # Add figure layout
    y_axis=max([Max_average_delay,Max_capacity,Max_flow])+500
     # Add figure layout
    fig.update_layout(
        title_text="Closure Route", #+ str(text1) + str(text2),
        font_family="Rockwell",
        # title_font_color=title_colors,
        legend=dict(
            title=None, orientation="h", y=1.02, yanchor="bottom", x=0.5, xanchor="center"
        ),       
        shapes=[
        dict(
           type="rect",xref="x",yref="y",
           x0=start_time, y0="0",x1=end_time, y1=y_axis,
           fillcolor="gray",opacity=0.4,line_width=0,layer="below"),
        ]   
    )

    # fig.update_layout(template="plotly_dark")  

    # Set x-axis title
    fig.update_xaxes(title_text="Time Period Ending (15 mins interval)",showline=True,linewidth=3,linecolor=colors, mirror=True)

    # Set y-axes titles
    fig.update_yaxes(title_text="Flow(veh/hr)",
    rangemode="nonnegative",
    secondary_y=False)
    fig.update_yaxes(title_text="Average Delay (min/veh)",
    rangemode="nonnegative",
    secondary_y=True,
    showline=True,linewidth=3,linecolor=colors, mirror=True)

  
    return fig


def run(road_name,start_time,end_time,closed_lanes,site_id_lookup_df,seasonal_data_df,profile_label_data_df,closure_date,cluster_parameter_data_df,detour_plan_data_df):
    global site_id_df,seasonal_df, profile_label_df, cluster_parameter_df, detour_plan_df
    site_id_df = site_id_lookup_df
    seasonal_df = seasonal_data_df
    
    profile_label_df = profile_label_data_df
    cluster_parameter_df = cluster_parameter_data_df
    detour_plan_df = detour_plan_data_df
    # covid_situation = "NONE"
    # day_of_week = "Mon-Thu"
    # school_open = True
    # university_open = True
    # shopping_season = False
    #closure_type = "Full Closure"
    closed_lanes = int(closed_lanes)
    #print(closure_date)
    closure_date = datetime.strptime(closure_date, "%Y-%m-%d").strftime("%#d/%m/%Y")
    #print(closure_date)
    


    covid_situation, day_of_week, school_open, university_open,shopping_season = seasonality_label(closure_date)
    
   

    start_time = datetime.strptime(start_time, '%H:%M').time()
    end_time = datetime.strptime(end_time, '%H:%M').time()
    site_id = block_site_to_site_id(road_name)
    ramp_id = block_site_to_ramp_id(road_name)
    closure_type = closure_type_detector(site_id, closed_lanes)

    df = demand_veh_hr(COVID = covid_situation,
                                        DoW = day_of_week,
                                        School = school_open,
                                        University = university_open,
                                        Shopping = shopping_season,
                                        SiteID = site_id)
    
    demand_veh = demand_per_vehicle_transposed(df)
   
    demand_veh.columns = ['Time', 'Demand (veh/hr)']
   
    time_logic = time_period_logic(demand_veh, start_time, end_time)
    
    delay_table = capacity_per_veh(time_logic, demand_veh, site_id,closed_lanes)
    
    delay_table = full_closure_detour_demand(delay_table, site_id,closure_type)
    
    delay_table = queue_at_interval(delay_table, site_id,closure_type)
    
    delay_table = total_average_delay(delay_table, site_id,closure_type)
    
    df2 = demand_veh_hr(COVID = covid_situation,
                                        DoW = day_of_week,
                                        School = school_open,
                                        University = university_open,
                                        Shopping = shopping_season,
                                        SiteID = ramp_id)
    demand_veh2 = demand_per_vehicle_transposed(df2)
    
    demand_veh2.columns = ['Time', 'Detour Demand (veh/hr)']
    
    time_logic2 = time_period_logic(demand_veh2, start_time, end_time)
    
    
    delay_table = delay_table.merge(demand_veh2)
    # #print("delay_table",delay_table)
    delay_table.loc[:,'Ramp Capacity (veh/hr)'] = assumed_capacity(ramp_id)    
    delay_table = with_detour_flow(delay_table,end_time,start_time)
    delay_table = capacity_per_veh_detour(time_logic2, delay_table , ramp_id,closed_lanes)
    #print(delay_table)
    
    
    
    
    delay_table = full_closure_detour_demand_detour(delay_table, ramp_id,closure_type)
    
    delay_table = queue_at_interval_detour(delay_table, ramp_id,end_time,start_time)
   
    delay_table = total_average_delay_detour(delay_table, ramp_id,closure_type)


    
    delay_table = delay_cal(delay_table,site_id)
   

    # #plot_closure_route(delay_table)
    print(delay_table["Average Delay per Vehicle (min/veh)"].values)



    return plot_closure_route(delay_table,start_time,end_time),plot_closure_detour(delay_table,start_time,end_time)


def test():
    program_start = time.time()

    road_name = "SH1_Southbound_between_East_Tamaki_Road_Off-ramp_and_273"

    closed_lanes="3"

    closure_date = "2023-01-17"

    start_time ="21:00"

    end_time = "23:00"

    data_path ="data"

    site_id_df = pd.read_csv(f"{data_path}/site_id_lookup.csv")

    original_site_id_df = pd.read_csv(f"{data_path}/site_id_lookup.csv")

    site_id_df = site_id_df[site_id_df["Ramp/Mainline"] == "Mainline"] # we only care about mainline

    #original_site_id_df = original_site_id_df[original_site_id_df["Ramp/Mainline"] == "Mainline"]

    seasonal_data_df = pd.read_csv(f"{data_path}/Seasonal Data3.csv", index_col=False)

    profile_label = pd.read_csv(f"{data_path}/profile_label2.csv")

    profile_label['Dates']= pd.to_datetime(profile_label['Dates'])

    cluster_parameter = pd.read_csv(f"{data_path}/Cluster_Sites_Params.csv", index_col=False)

    detour_plan = pd.read_csv(f"{data_path}/detour_plan.csv")

    #run(road_name,start_time,end_time,closed_lanes,original_site_id_df,seasonal_data_df,profile_label,closure_date,cluster_parameter,detour_plan)
    



    fig,fig2 = run(road_name,start_time,end_time,closed_lanes,original_site_id_df,seasonal_data_df,profile_label,closure_date,cluster_parameter,detour_plan)
    fig2.show()
    fig.show()


    print(time.time()- program_start)



test()
    