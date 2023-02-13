
from datetime import datetime
import pandas as pd
import time
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import numpy as np
from multiprocessing.pool import ThreadPool
from threading import Thread


def seasonality_label(select_date):
    profile_label_detail = profile_label_df[profile_label_df["Dates"] == select_date]
    return profile_label_detail

def block_site_to_site_ramp_id(BlockSite):
    site_id_detail = site_id_df[site_id_df["Site Block"] == BlockSite]
    site_id = site_id_detail["SiteID LookUp"].values[0]
    ramp_route = site_id_detail["Ramp reroute"].values[0]
    return site_id,ramp_route

def closure_type_detector(closedLane): 
    if closedLane >= n_of_lanes:
        closure_type = "Full Closure"
    else:
        closure_type = "Not Full Closure"
    return closure_type


def demand_veh_hr(profile_label_detail,SiteID,Ramp_id):
    demand_veh_hr = (seasonal_df[(seasonal_df['COVID'] == profile_label_detail["Alert Level"].values[0]) &
                 (seasonal_df['DoW'] == profile_label_detail["DoW"].values[0]) &
                 (seasonal_df['School Open'] == profile_label_detail["School Open"].values[0]) &
                 (seasonal_df['University Open'] == profile_label_detail["University Open"].values[0]) &
                 (seasonal_df['Shopping'] == profile_label_detail["Shopping"].values[0]) &
                 (seasonal_df['Site_ID'].isin([SiteID,Ramp_id]))])
    
    #convert to datetime
    #demand_veh_hr.columns = pd.to_datetime(demand_veh_hr.columns, format='%H:%M').time
   
    # site_id_demand_veh_hr = demand_veh_hr[demand_veh_hr["Site_ID"] ==SiteID].iloc[:,9:-2]
    # ramp_id_demand_veh_hr = demand_veh_hr[demand_veh_hr["Site_ID"] ==Ramp_id].iloc[:,9:-2]
    # site_id_demand_veh_hr.columns = pd.to_datetime(site_id_demand_veh_hr.columns, format='%H:%M').time
    # ramp_id_demand_veh_hr.columns = pd.to_datetime(ramp_id_demand_veh_hr.columns, format='%H:%M').time
    

    # return site_id_demand_veh_hr,ramp_id_demand_veh_hr
    column_name = demand_veh_hr.Site_ID.values
    demand_veh_hr = demand_veh_hr.iloc[:,9:-2]
    demand_veh_hr.columns = pd.to_datetime(demand_veh_hr.columns, format='%H:%M').time
    
    return demand_veh_hr,column_name
    


def demand_per_vehicle_transposed(InputData):

    demand_per_vehicle_transposed = InputData.T
    demand_per_vehicle_transposed.reset_index(inplace=True)
    demand_per_vehicle_transposed = demand_per_vehicle_transposed.rename(columns = {'index':'Time'})
    
    return demand_per_vehicle_transposed


def time_period_logic(Data, StartTime, EndTime):
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

def get_site_id_detail(site_id_list):
    global site_id_df
    site_id_detail  = site_id_df[site_id_df['SiteID LookUp'].isin(site_id_list)]
    site_id_detail = site_id_detail[["SiteID LookUp","Ramp/Mainline","Normal Total Capacity","TMP Capacity","Detour Plan Ref","Number of Lane(s)"]]
    return site_id_detail.drop_duplicates()


def capacity_per_veh(time_logic, site_id_list,closed_lanes):
    global delay_table,site_id_detail_df
    colunm_name_list = []
    for site_id in site_id_list:
        site_id_detail = site_id_detail_df[site_id_detail_df['SiteID LookUp'] == site_id]
        main_ramp = site_id_detail["Ramp/Mainline"].values[0]
        assumed_cap = site_id_detail["Normal Total Capacity"].values[0]
        capacity_veh = 0
        total_lanes = site_id_detail["Number of Lane(s)"].values[0]
        if main_ramp == "Ramp":
            capacity_veh = assumed_cap
        else:
            if closed_lanes == total_lanes:
                capacity_veh = 0
            else:
                capacity_veh = (total_lanes - closed_lanes) * site_id_detail["TMP Capacity"].values[0]
        colunm_name = f"{site_id}_capacity"
        delay_table[colunm_name]  = capacity_veh
        time_logic[colunm_name] = assumed_cap
        colunm_name_list.append(colunm_name)
    delay_table.update(time_logic)
    delay_table[colunm_name_list] = delay_table[colunm_name_list].fillna(0)


def full_closure_detour_demand(site_id_list,closure_type,original_site_id):
    global delay_table,site_id_detail_df
    for site_id in site_id_list: 
        site_id_detail = site_id_detail_df[site_id_detail_df['SiteID LookUp'] == site_id]
        main_ramp = site_id_detail["Ramp/Mainline"].values[0]
        if main_ramp == "Ramp" and closure_type == "Full Closure":
            if site_id == original_site_id:
                delay_table[f'{site_id}_full_closure_detour_demand'] = delay_table[f'{site_id}_demand']*2
            else:
                delay_table[f'{site_id}_full_closure_detour_demand'] = delay_table['with_detour_flow']*2
        else:
            delay_table[f'{site_id}_full_closure_detour_demand'] = 0

def with_detour_flow(end_time,start_time,ramp_id,site_id):
    global delay_table
    with_detour_flow_list =[]
    for index,element in delay_table.iterrows():
        if start_time >= end_time:
     
            if element.Time > end_time and element.Time < start_time:
                with_detour_flow_list.append(element[f"{ramp_id}_demand"])
            else:
                with_detour_flow_list.append(element[f"{ramp_id}_demand"] + element[f"{site_id}_demand"] )
            
        else:
            if element.Time > end_time or element.Time < start_time:
                with_detour_flow_list.append(element[f"{ramp_id}_demand"])
            else:
                with_detour_flow_list.append(element[f"{ramp_id}_demand"] + element[f"{site_id}_demand"] )
   
    
    delay_table["with_detour_flow"]  = with_detour_flow_list
    


def queue_at_interval(closure_type,site_id,ramp_id,end_time,start_time):
    global delay_table,site_id_detail_df
    main_ramp = site_id_detail_df[site_id_detail_df['SiteID LookUp'] == site_id]["Ramp/Mainline"].values[0]
    delay_table['Detour Queue at Start of Interval'] = 0
    site_id_start_interval_list = []
    site_id_end_interval_list = []
    site_id_satrt_value = 0
    ramp_id_start_interval_list = []
    ramp_id_end_interval_list = []
    ramp_id_satrt_value = 0
    
    for index,element in delay_table.iterrows():
        if main_ramp == "Ramp" and closure_type == "Full Closure":
            site_id_end_value = max(element[f'{site_id}_demand']*2 + site_id_satrt_value - element[f'{site_id}_capacity'],0)
            site_id_start_interval_list.append(site_id_satrt_value)
            site_id_end_interval_list.append(site_id_end_value)
            site_id_satrt_value = site_id_end_value
        else:
            site_id_end_value = max(element[f'{site_id}_demand'] + site_id_satrt_value - element[f'{site_id}_capacity'],0)
            site_id_start_interval_list.append(site_id_satrt_value)
            site_id_end_interval_list.append(site_id_end_value)
            site_id_satrt_value = site_id_end_value
        if start_time >= end_time:
            if element.Time > end_time and element.Time < start_time:
                ramp_id_end_value = max(element[f'{ramp_id}_demand'] + ramp_id_satrt_value - element[f'{ramp_id}_ramp_capacity'],0)
                ramp_id_start_interval_list.append(ramp_id_satrt_value)
                ramp_id_end_interval_list.append(ramp_id_end_value)
                ramp_id_satrt_value = ramp_id_end_value
            else:
                ramp_id_end_value = max((element[f'{site_id}_demand'] + element[f'{ramp_id}_demand'])+ ramp_id_satrt_value - element[f'{ramp_id}_ramp_capacity'],0)
                ramp_id_start_interval_list.append(ramp_id_satrt_value)
                ramp_id_end_interval_list.append(ramp_id_end_value)
                ramp_id_satrt_value = ramp_id_end_value

        else:
            if element.Time > end_time or element.Time < start_time:
                ramp_id_end_value = max(element[f'{ramp_id}_demand'] + ramp_id_satrt_value - element[f'{ramp_id}_ramp_capacity'],0)
                ramp_id_start_interval_list.append(ramp_id_satrt_value)
                ramp_id_end_interval_list.append(ramp_id_end_value)
                ramp_id_satrt_value = ramp_id_end_value
            else:
                ramp_id_end_value = max((element[f'{site_id}_demand'] + element[f'{ramp_id}_demand'])+ ramp_id_satrt_value - element[f'{ramp_id}_ramp_capacity'],0)
                ramp_id_start_interval_list.append(ramp_id_satrt_value)
                ramp_id_end_interval_list.append(ramp_id_end_value)
                ramp_id_satrt_value = ramp_id_end_value
    delay_table["Queue at Start of Interval" ] = site_id_start_interval_list
    delay_table["Queue at End of Interval"] = site_id_end_interval_list 
    delay_table["Detour Queue at Start of Interval"] = ramp_id_start_interval_list
    delay_table["Detour Queue at End of Interval"] = ramp_id_end_interval_list


def total_average_delay(site_id,ramp_id,closure_type):
    global delay_table,site_id_detail_df
    site_main_ramp = site_id_detail_df[site_id_detail_df['SiteID LookUp'] == site_id]["Ramp/Mainline"].values[0]
    ram_main_ramp = site_id_detail_df[site_id_detail_df['SiteID LookUp'] == ramp_id]["Ramp/Mainline"].values[0]

    if site_main_ramp == "Mainline" and closure_type == "Full Closure":
        delay_table['Total Average Delay (veh-mins)'] = 0
    else:
        delay_table['Total Average Delay (veh-mins)'] = 15 * delay_table[['Queue at Start of Interval', 'Queue at End of Interval']].mean(axis=1)
    if site_main_ramp == "Ramp" and closure_type == "Full Closure":
        delay_table['Average Delay per Vehicle (min/veh)'] = delay_table['Total Average Delay (veh-mins)']/(delay_table[f'{site_id}_demand'] * 2)
    else:
        delay_table['Average Delay per Vehicle (min/veh)'] = delay_table['Total Average Delay (veh-mins)']/(delay_table[f'{site_id}_demand'])


    if ram_main_ramp == "Mainline" and closure_type == "Full Closure":
        delay_table['Detour Total Average Delay (veh-mins)'] = 0
    else:
        delay_table['Detour Total Average Delay (veh-mins)'] = 15* (delay_table['Detour Queue at Start of Interval'] + delay_table['Detour Queue at End of Interval'])/2
    if ram_main_ramp == "Ramp" and closure_type == "Full Closure":
        delay_table['Detour Average Delay per Vehicle (min/veh)'] = delay_table['Detour Total Average Delay (veh-mins)']/(delay_table[f'{ramp_id}_demand'] + delay_table[f'{site_id}_demand'])
    else:
        delay_table['Detour Average Delay per Vehicle (min/veh)'] = 0
    delay_table.drop([f'{ramp_id}_full_closure_detour_demand','Detour Queue at Start of Interval','Detour Queue at End of Interval','Detour Total Average Delay (veh-mins)'],axis = 1)

def delay_cal(site_id,ramp_id):
    global parameter_main,site_id_detail_df,detour_plan_df,delay_table
    Free_SpeedM = parameter_main["Free SpeedM"].values[0]
    ScM = parameter_main["ScM"].values[0]
    N_M = parameter_main["NM"].values[0]
    Free_SpeedD = parameter_main["Free SpeedD"].values[0]
    ScD = parameter_main["ScD"].values[0]
    N_D = parameter_main["ND"].values[0]
    detoure_plan_ref = site_id_detail_df[site_id_detail_df['SiteID LookUp'] == site_id]["Detour Plan Ref"].values[0]
    capacity_M = site_id_detail_df[site_id_detail_df['SiteID LookUp'] == site_id]["Normal Total Capacity"].values[0]
    distant_M = detour_plan_df[detour_plan_df["Ref"] == detoure_plan_ref]["Normal Distance "].values[0]
    time_main_list = []
    time_detour_list = []
    distant_D=detour_plan_df[detour_plan_df["Ref"] == detoure_plan_ref]["Detour Distance (km)"].values[0]
    for index, element in delay_table.iterrows():
        volume_Mi=element[f"{site_id}_demand"]
        volume_Di=element["with_detour_flow"]
        if volume_Mi < capacity_M:
          time_main_list.append((1/Free_SpeedM+(1/ScM-1/Free_SpeedM)*(volume_Mi/capacity_M)**(N_M))*distant_M*3600) 
        else:
            time_main_list.append((distant_M/ScM)*3600)
        capacity_D= element[f'{ramp_id}_ramp_capacity']
        if volume_Di < capacity_D:
            time_detour_list.append((1/Free_SpeedD+(1/ScD-1/Free_SpeedD)*(volume_Di/capacity_D)**(N_D))*distant_D*3600)
        else:
            time_detour_list.append((distant_D/ScM)*3600)
    delay_table["Time_Detour"] = time_detour_list
    delay_table["Time_Main"] = time_main_list
    delay_table['Bench']=0
    delay_table['Delay']=delay_table['Time_Detour']-delay_table['Time_Main']
    delay_table['New_Delay']=(delay_table[["Delay","Bench"]].max(axis=1))/60
    delay_table.drop(['Delay','Bench'], axis=1)



def plot_closure_route(start_time,end_time,site_id,ramp_id):
    global delay_table
    Max_average_delay = delay_table['Average Delay per Vehicle (min/veh)'].max()
    Max_capacity = delay_table[f'{site_id}_capacity'].max()
    Max_flow = delay_table[f'{site_id}_demand'].max()  
    colors = ""
    if Max_average_delay >= 15 or Max_flow > Max_capacity:
         colors = 'red'
    elif Max_average_delay >= 5 and Max_average_delay < 15 and Max_flow > Max_capacity:
         colors = 'red'
    elif Max_average_delay >= 5 and Max_average_delay < 15 and Max_flow < Max_capacity:
         colors = 'orange'
    elif Max_average_delay < 5 and Max_flow > Max_capacity:
         colors = 'red'   
    else:
         colors = 'green'
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    delay_table['Time2'] = delay_table['Time'].apply(lambda x: x.strftime('%H:%M'))

    # Adding condition: When capicity == 0, demand ==0
    conditions = [delay_table[f'{site_id}_capacity']==0,delay_table[f'{site_id}_capacity']>0]
    choices=[0,delay_table[f'{site_id}_demand']]
    delay_table["Demand (veh/hr)2"]=np.select(conditions,choices, default=0)
    fig.add_trace(
        go.Scatter(x=delay_table['Time2'], y=delay_table["Demand (veh/hr)2"], name="Demand (veh/hr)"),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=delay_table['Time2'], y=delay_table[f'{site_id}_capacity'], name="Capacity (veh)"),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x = delay_table['Time2'], y = delay_table["Average Delay per Vehicle (min/veh)"], name="Average Delay per Vehicle (min/veh)"),
        secondary_y=True,
    )
    y_axis=max([Max_average_delay,Max_capacity,Max_flow])+500
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
    fig.update_xaxes(title_text="Time Period Ending (15 mins interval)",showline=True,linewidth=3,linecolor=colors, mirror=True)

    # Set y-axes titles
    fig.update_yaxes(title_text="Flow(veh/hr)",
    rangemode="nonnegative",
    secondary_y=False)
    fig.update_yaxes(title_text="Average Delay (min/veh)",
    rangemode="nonnegative",
    secondary_y=True,
    showline=True,linewidth=3,linecolor=colors, mirror=True)
   
    return


    
def create_graph(data_dic):
    global delay_table
    Max_average_delay = data_dic["Max_average_delay"]
    Max_capacity = data_dic["Max_capacity"]
    Max_flow = data_dic["Max_flow"]
    start_time=data_dic["start_time"]
    end_time=data_dic["end_time"]
    site_id = data_dic["site_id"]
    colors = ""
    if Max_average_delay >= 15 or Max_flow > Max_capacity:
        colors = 'red'
    elif Max_average_delay >= 5 and Max_average_delay < 15 and Max_flow > Max_capacity:
        colors = 'red'
    elif Max_average_delay >= 5 and Max_average_delay < 15 and Max_flow < Max_capacity:
        colors = 'orange'
       
    elif Max_average_delay < 5 and Max_flow > Max_capacity:
        colors = 'red'   
    else:
        colors = 'green'
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    #fig.layout.template = 'plotly_dark'
    delay_table['Time2'] = delay_table['Time'].apply(lambda x: x.strftime('%H:%M'))
    fig.add_trace(
        go.Scatter(x=delay_table['Time2'], y=delay_table[data_dic["trace_1_data"]], name=data_dic["trace_1_name"]),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=delay_table['Time2'], y=delay_table[data_dic["trace_2_data"]], name=data_dic["trace_2_name"]),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=delay_table['Time2'], y=delay_table[data_dic["trace_3_data"]], name=data_dic["trace_3_name"]),
        secondary_y=True,
    )
    y_axis=max([Max_average_delay,Max_capacity,Max_flow])+500
     # Add figure layout
    fig.update_layout(
        title_text=data_dic["title_name"], #+ str(text1) + str(text2),
        font_family="Rockwell",
        paper_bgcolor = "black",
        font_color = "white",
        plot_bgcolor='black',

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
    fig.update_xaxes(title_text="Time Period Ending (15 mins interval)",showline=True,linewidth=3,linecolor=colors, mirror=True,gridcolor='#283442')

    # Set y-axes titles
    fig.update_yaxes(title_text="Flow(veh/hr)",
    rangemode="nonnegative",
    secondary_y=False,gridcolor='#283442')
    fig.update_yaxes(title_text="Average Delay (min/veh)",
    rangemode="nonnegative",
    secondary_y=True,
    showline=True,linewidth=3,linecolor=colors, mirror=True,gridcolor='#283442')

  
    return fig
    
     




def run(road_name,start_time,end_time,closed_lanes,site_id_lookup_df,seasonal_data_df,profile_label_data_df,closure_date,cluster_parameter_data_df,detour_plan_data_df,total_lanes):
    global site_id_df,seasonal_df, profile_label_df, cluster_parameter_df, detour_plan_df,n_of_lanes,delay_table,site_id_detail_df,parameter_main
    site_id_df = site_id_lookup_df
    seasonal_df = seasonal_data_df
    profile_label_df = profile_label_data_df
    cluster_parameter_df = cluster_parameter_data_df
    detour_plan_df = detour_plan_data_df
    
    closed_lanes = int(closed_lanes)
    n_of_lanes = int(total_lanes)
    closure_date = datetime.strptime(closure_date, "%Y-%m-%d").strftime("%#d/%m/%Y")
    start_time = datetime.strptime(start_time, '%H:%M').time()
    end_time = datetime.strptime(end_time, '%H:%M').time()

    profile_label_detail = seasonality_label(closure_date)

    site_id, ramp_id= block_site_to_site_ramp_id(road_name)
    
    parameter_main = cluster_parameter_df[cluster_parameter_df['Site'] == site_id]
    closure_type = closure_type_detector(closed_lanes)
    
    demand_veh_hr_df, site_id_list = demand_veh_hr(profile_label_detail,site_id,ramp_id)
    
    demand_veh_df = demand_per_vehicle_transposed(demand_veh_hr_df)
    
    site_id_list = list (site_id_list)
    
    columna_name = [f"{site_id_name}_demand" for site_id_name in site_id_list]
    
    demand_veh_df.columns = ['Time'] + columna_name
    delay_table = demand_veh_df
   
    time_logic = time_period_logic(demand_veh_df, start_time, end_time)

    site_id_detail_df = get_site_id_detail(site_id_list)
    capacity_per_veh(time_logic, site_id_list,closed_lanes)
   
    delay_table[f"{ramp_id}_ramp_capacity"]= site_id_detail_df[site_id_detail_df['SiteID LookUp'] == ramp_id]["Normal Total Capacity"].values[0]
    
    with_detour_flow(end_time,start_time,ramp_id,site_id)
    full_closure_detour_demand(site_id_list,closure_type,site_id)
    queue_at_interval(closure_type,site_id,ramp_id,end_time,start_time)
   
    total_average_delay(site_id,ramp_id,closure_type)

    conditions = [delay_table[f'{site_id}_capacity']==0,delay_table[f'{site_id}_capacity']>0]
    choices=[0,delay_table[f'{site_id}_demand']]
    delay_table["Demand (veh/hr)2"]=np.select(conditions,choices, default=0)
    start_time=start_time.strftime('%H:%M')
    end_time=end_time.strftime('%H:%M')
    
    graph_parameter = [{"Max_average_delay":delay_table['Average Delay per Vehicle (min/veh)'].max(),"Max_capacity":delay_table[f'{site_id}_capacity'].max(),
    "Max_flow":delay_table[f'{site_id}_demand'].max(),"start_time":start_time,"end_time":end_time,"site_id":site_id,
    "trace_1_data":"Demand (veh/hr)2","trace_1_name":"Demand (veh/hr)","trace_2_data":f'{site_id}_capacity',"trace_2_name":"Capacity (veh)","trace_3_data":"Average Delay per Vehicle (min/veh)",
    "trace_3_name":"Average Delay per Vehicle (min/veh)","title_name":"Closure Route"},

    {"Max_average_delay":delay_table['Detour Average Delay per Vehicle (min/veh)'].max(),"Max_capacity":delay_table[f"{ramp_id}_ramp_capacity"].max(),"Max_flow":delay_table["with_detour_flow"].max(),
    "start_time":start_time,"end_time":end_time,"site_id":ramp_id,
     "trace_1_data":"with_detour_flow","trace_1_name":"With Detour Flow (veh/hr)","trace_2_data":f"{ramp_id}_ramp_capacity","trace_2_name":"Ramp Capacity (veh/hr)","trace_3_data":"Detour Average Delay per Vehicle (min/veh)",
    "trace_3_name":"Detour Average Delay per Vehicle (min/veh)","title_name":"Detour Route"}]
    
    fig = create_graph(graph_parameter[0])
    fig2 = create_graph(graph_parameter[1])
    return fig,fig2
    #print(graphparamter)
   
    # fig = plot_closure_route(start_time,end_time,site_id,ramp_id)
    # return fig,fig
    # print(delay_table)

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
    total_lanes = 3

    fig,fig2=run(road_name,start_time,end_time,closed_lanes,original_site_id_df,seasonal_data_df,profile_label,closure_date,cluster_parameter,detour_plan,total_lanes)
    fig2.show()
    fig.show()
    print(time.time()- program_start)


#test()