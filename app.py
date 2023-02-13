#from dash import dcc
import dash_deck
import pydeck as pdk
import geopandas as gpd
import dash

import pandas as pd

from datetime import date

import dash_bootstrap_components as dbc
from dash_iconify import DashIconify
from dash_extensions.enrich import Output, DashProxy, Input, MultiplexerTransform, html,State,dcc

from plotly.graph_objs import *
from datetime import datetime as dt
import calculation2 as cf
#from plotly.subplots import make_subplots
import dash_auth
import dash_mantine_components as dmc
import re
import date_value as dv


def ReadMapData(path):
    
    geo_map_df = gpd.read_file(path)
    map_df = gpd.GeoDataFrame()
    map_df["name"] = geo_map_df.FID
    map_df["geometry"] = geo_map_df.geometry
    map_df["distance"] = geo_map_df.distance_value

    if str(geo_map_df.map_type[0]) == "Closure":
        color = [50,168,82] 
        color_list = [color]*len(map_df["name"])
        map_df["color"] = color_list
    elif str(geo_map_df.map_type[0]) == "Detour":
        color = [209,42,33] 
        color_list = [color]*len(map_df["name"])
        map_df["color"] = color_list
    return map_df
    


#Global valuable
assets_path = "assets"
data_path ="data"
VALID_USERNAME_PASSWORD_PAIRS = {
    'Ali': '1234',
    'Dan': "890",
    'Sam': "345",
    
}
mapbox_api_token = "pk.eyJ1Ijoicml2aW5kdSIsImEiOiJjazZpZXo0amUwMGJ1M21zYXpzZGMzczdiIn0.eoArFYnhz0jEPQEnF0vdKQ"

closure_data_df = ReadMapData(f"{data_path}/Closure_2.geojson") # map data set
detour_data_df = ReadMapData(f"{data_path}/Detour_2.geojson") # map data set
original_block_closure_data_df = ReadMapData(f"{data_path}/Block_Closure2.geojson") # map data set
original_block_detour_data_df = ReadMapData(f"{data_path}/Block_Detour2.geojson") # map data set
original_closure_data_df = ReadMapData(f"{data_path}/Closure_2.geojson") # map data set
original_detour_data_df = ReadMapData(f"{data_path}/Detour_2.geojson") # map data set

site_id_df = pd.read_csv(f"{data_path}/site_id_lookup.csv")
original_site_id_df = pd.read_csv(f"{data_path}/site_id_lookup.csv")
site_id_df = site_id_df[site_id_df["Ramp/Mainline"] == "Mainline"] # we only care about mainline
#original_site_id_df = original_site_id_df[original_site_id_df["Ramp/Mainline"] == "Mainline"]
seasonal_data_df = pd.read_csv(f"{data_path}/Seasonal Data.csv", index_col=False)
seasonal_data_df = seasonal_data_df[seasonal_data_df.columns[0:9].tolist()+seasonal_data_df.columns[56:105].tolist()+seasonal_data_df.columns[9:56].tolist()+['Total','Max']]
profile_label = pd.read_csv(f"{data_path}/profile_label3.csv")
profile_label['Dates']= pd.to_datetime(profile_label['Dates'])
cluster_parameter = pd.read_csv(f"{data_path}/Cluster_Sites_Params.csv", index_col=False)
detour_plan = pd.read_csv(f"{data_path}/detour_plan.csv")
direction_list = list(set(site_id_df["Direction"].values))
direction_list.sort()
site_id_df = site_id_df[site_id_df["Site Block"].str.contains(f"^.*_.*")]
siteblock_list =list(set(site_id_df["Site Block"].values))
siteblock_list.sort()
road_name_drop_box_options = siteblock_list
closure_data_df = original_closure_data_df[original_closure_data_df["name"].isin(road_name_drop_box_options)]
detour_data_df = original_detour_data_df[original_detour_data_df["name"].isin(road_name_drop_box_options)]
closure_layout_data = None
detour_layout_data = None
total_lanes =0
sh_list = list(set(site_id_df["SH"].values))
sh_list.sort()
sh_drop_box_options = []
for element in sh_list:
    sh_name = ""
    if element == "1N":
        sh_name = "SH1"
    else:
        sh_name = "SH"+element
    sh_drop_box_options.append({"label": sh_name, "value": element})

full_closure = False


def get_deck(map_data_df,closure_layout_data,detour_layout_data):
    #print(map_data_df)
    #print(closure_layout_data)
    #print(detour_layout_data)
    # Set the viewport location
    view_state = pdk.ViewState(latitude=-36.859067426240394, longitude=174.76020812611904, zoom=12)

    # Define a layer to display on a map
    base_layout = pdk.Layer(
        type = "PathLayer",
        data = map_data_df,
        pickable = True,
        get_color="color",
        width_scale = 2.5,
        width_min_pixels = 2,
        get_path = "geometry.coordinates",
        get_width = 3,
    )
    closure_layout= pdk.Layer(
        type = "PathLayer",
        data = closure_layout_data,
        pickable = True,
        get_color="color",
        width_scale = 2.5,
        width_min_pixels = 2,
        get_path = "geometry.coordinates",
        get_width = 4,
    )
    detour_layout = pdk.Layer(
        type = "PathLayer",
        data = detour_layout_data,
        pickable = True,
        get_color="color",
        width_scale = 2.5,
        width_min_pixels = 2,
        get_path = "geometry.coordinates",
        get_width = 4,
    )
    # Render
    # Start building the layout here
    r = pdk.Deck(layers=[base_layout,closure_layout,detour_layout], initial_view_state=view_state,map_provider='mapbox',map_style=pdk.map_styles.CARTO_DARK)
    return r
def update_color(h):
    return[70,88,219]

dash_app = DashProxy(__name__, assets_folder = assets_path,prevent_initial_callbacks=True, transforms=[MultiplexerTransform()])
dash_app.title = "CIA Tool Development"
auth = dash_auth.BasicAuth(
    dash_app,
    VALID_USERNAME_PASSWORD_PAIRS
)
app = dash_app.server


dash_app.layout = html.Div(
    children=[
        dcc.ConfirmDialog(
            message='We strive to provide you with accurate information. However, because the information presented is gathered from various sources, we can not guarantee that the information is accurate and comprehensive. Use of this information is conditional upon your agreement that WSP is not liable for any consequences resulting from your reliance on the information on this website. Before you rely on the accuracy of the information provided on this website, we strongly recommend you check the information yourself or contact us (ali.marz@wsp.com) to help you make the most reasonable decision.',
            displayed=True
        ),
        html.Div(
            className="four columns div-user-controls",
            children=[
                html.Div(
                    children=[
                        # Header
                        html.A(
                            html.Img(
                                className="logo",
                                src=dash_app.get_asset_url(
                                    "wsp_white.png")
                            ),
                            href="https://www.wsp.com/en-nz/"
                        ),
                        html.A(
                            html.Img(
                                className="logo",
                                src=dash_app.get_asset_url(
                                    "wakakotahi_white.png")
                            ),
                            href="https://www.nzta.govt.nz/"
                        ),
                        html.P(html.B("CLOSURE IMPACT ASSESSMENT TOOL"), style={
                            "font-family": "Monospace", "font-size": "24px"}),
                        html.Hr()
                    ]
                ),
                html.Div(
                    dbc.Alert(
                        id="error_alert",
                        is_open=False,
                        color="#f03508"

                    )
                ),
                html.Div(
                    className="block_style",
                    children=[
                        html.Label("Closure Type: "),
                        dcc.RadioItems(
                            id="closure_type",
                            options=[
                                {"label": "Block Closure", "value": "block_closure"}, 
                                {"label": "Single Closure", "value": "single_closure"}
                                ],
                            value="single_closure",
                            inline=True
                        )
                    ]
                ),
                  html.Div(
                    className="block_style",
                    children=[
                        html.Div(
                            style = {"display": "inline-block", "text-align": "center", "overflow-x": "auto"},
                            children = [html.Label("SH Number: ")]
                        ),
                        html.Div(
                            style={
                                "display": "inline-block",
                                'margin-left': '10px', 
                                "width": "25%"
                                },
                            children=[
                                dcc.Dropdown(
                                    id="sh_drop_box",
                                    options = sh_drop_box_options,
                                    placeholder = "SH Number",
                                    multi = False,
                                )

                            ]
                        ),
                        html.Div(
                            style = {"display": "inline-block", "text-align": "center", "overflow-x": "auto",'margin-left': '10px',},
                            children = [html.Label("Direction: ")]
                        ),
                        html.Div(
                            style={
                                "display": "inline-block",
                                'margin-left': '10px', 
                                "width": "25%"
                                },
                            children=[
                                dcc.Dropdown(
                                    id = "direction_drop_box",
                                    options = direction_list,
                                    placeholder="Direction",
                                    multi = False,
                                )
                            ]
                        ),  
                    ]
                ),
                html.Div(
                    className="block_style",
                    children=[
                        html.Label(
                            "Location (Required): "),
                        dcc.Dropdown(
                            id="road_name_drop_box",
                            options=road_name_drop_box_options,
                            placeholder="Select location",
                            multi=False,
                        )
                    ]
                ),
                html.Div(
                    className="block_style",
                    children=[
                        html.Label(
                            "Closed Lanes (Required): "),
                        dcc.Dropdown(
                            id="closed_lanes_drop_box",
                            options=[],
                            placeholder="Select Number of Closed Lanes",
                            multi=False,
                        )
                    ]
                ),
                html.Div(
                    className="block_style",
                    children=[
                        html.Label(
                            "Closure Dates (Required): ", style = {"display": "inline-block"}),
                            
                        dmc.ActionIcon(
                            DashIconify(icon="ri:information-line", width=20, color="gray"),
                            id="check_condition",
                            n_clicks=0,
                            style={"display": "inline-block"}),
                        dmc.Alert(
                            # show query
                            "",
                            title="Condition",
                            id="condition_msg",
                            color="blue",
                            hide=True,
                            withCloseButton=True,
                            style={
                                "margin-bottom": "10px"},
                        ),
                        dcc.DatePickerSingle(
                            id="date_picker",
                            min_date_allowed=dt(
                                2022, 1, 1),
                            max_date_allowed=dt(
                                2030, 12, 30),
                            initial_visible_month=date.today(),
                            date=date.today(),
                            disabled_days = dv.get_nz_holidays(),
                            clearable=False,
                            placeholder="Select Closure Date",
                            display_format="MMMM D, YYYY",
                            style={
                                "border": "0px solid black",
                                "display": "block",
                                "width": "25%"},
                        )
                    ]
                ),
                html.Div(
                    className="block_style",
                    children=[
                        html.Label("Start Time (Required):"),
                        html.Div(
                            style={"display": "inline-block",
                                    "width": "20%",
                                    'margin-right': '10px'
                                    },
                            children=[
                                dcc.Dropdown(
                                    id="start_time_hour",
                                    options=["00", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10",
                                             "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21",
                                             "22", "23"],
                                    multi=False,
                                    placeholder="Select Hour",
                                    value = "21"
                                   

                                ),
                                
                            ]

                        ),
                        html.Div(
                            style = {"display": "inline-block", "text-align": "center", "overflow-x": "auto"},
                            children = [

                                html.Label(":",style = {"font-weight": "bold"}),

                            ]
                        ),
                        html.Div(
                            style={"display": "inline-block",
                                    'margin-left': '10px', 
                                    "width": "23%",
                                     
                                    },
                            children=[
                                dcc.Dropdown(
                                    id="start_time_minute",
                                    options=["00", "15", "30", "45"],
                                    multi=False,
                                    placeholder="Select Minute",
                                    value = "00"
                                    

                                ),
                                
                            ]

                        ),
                        
                    ],
                ),
                html.Div(
                    className="block_style",
                    children=[
                        html.Label("End Time (Required):"),
                        html.Div(
                            style={"display": "inline-block",
                                    "width": "20%",
                                    'margin-right': '10px'
                                    },
                            children=[
                                dcc.Dropdown(
                                    id="end_time_hour",
                                    options=["00", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10",
                                             "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21",
                                             "22", "23"],
                                    multi=False,
                                    placeholder="Select Hour",
                                    value = "23"
                                   

                                ),
                                
                            ]

                        ),
                        html.Div(
                            style = {"display": "inline-block", "text-align": "center", "overflow-x": "auto"},
                            children = [

                                html.Label(":",style = {"font-weight": "bold"}),

                            ]
                        ),
                        html.Div(
                            style={"display": "inline-block",
                                    'margin-left': '10px', 
                                    "width": "23%",
                                     
                                    },
                            children=[
                                dcc.Dropdown(
                                    id="end_time_minute",
                                    options=["00", "15", "30", "45"],
                                    multi=False,
                                    placeholder="Select Minute",
                                    value = "00"
                                    

                                ),
                                
                            ]

                        ),
                        
                    ],
                ),
                



                html.Div(
                    className= "block_style",
                    children=[
                        html.Button(
                            "Calculation", 
                            id="calculation_btn", 
                            n_clicks=0),
                    ]
                )
            ]
        ),
        html.Div(
            className = "eight columns div-for-charts bg-grey",
            children = [
                html.Div(
                    id = "map_container",
                    style={
                        "height": "100%",
                        "float": "left",
                        "position": "relative",  
                    },
                    children = [
                        dash_deck.DeckGL(
                                    #get_deck(closure_data_df,None,None).to_json(), # div section for map display
                                    get_deck(closure_data_df,None,None).to_json(),
                                    id="deck_map",
                                    tooltip={"text": "{name}"},
                                    mapboxKey = mapbox_api_token,
                                    enableEvents=['click']
                                )
                    ]
                ),
                html.Div(
                    id = "graph_container",
                    style={
                        "height": "100%",
                        "float": "left",
                        "position": "relative",
                        "background-color": "#111111"
                    },
                    children = [
                        dcc.Tabs(
                            id = "graph_tabs",
                            colors = {"border":"black"},
                            children = [
                                dcc.Tab(
                                    label = "Detour Route",
                                    value = "detour_graph",
                                    children = [
                                        dmc.LoadingOverlay(
                                            dcc.Graph(
                                                id = "detour_histogram",
                                                figure = {
                                                    "layout": {
                                                        "paper_bgcolor": "#111111",
                                                        "plot_bgcolor": "#111111",
                                                        'font': {
                                                            'color': "#111111"
                                                        }
                                                    }
                                                }
                                            ),
                                        )
                                    ]
                                ),
                                dcc.Tab(
                                    label="Closure Route",
                                    value="closure_graph",
                                    children=[
                                        dmc.LoadingOverlay(
                                            dcc.Graph(
                                                id="closur_histogram",
                                                figure={
                                                    "layout": {
                                                        "paper_bgcolor": "#111111",
                                                        "plot_bgcolor": "#111111",
                                                        'font': {
                                                            'color': "#111111"
                                                        }
                                                    }
                                                }
                                            ),
                                        )
                                    ]
                                )
                            ],
                            value = "detour_graph"
                        )
                       
                    ]
                )
                    
                
            ]
        )

    ]
)
@dash_app.callback(
    Output("map_container","children"),
    Output("sh_drop_box","options"),
    Output("road_name_drop_box","options"),
    Output("sh_drop_box","value"),
    Output("road_name_drop_box","value"),
    Output("direction_drop_box","options"),
    Output("direction_drop_box","value"),

    Input("closure_type","value"),
    prevent_initial_call=True,
)
def UpdateMapTypeData(closure_type):
    global original_block_closure_data_df,original_block_detour_data_df,original_closure_data_df,original_detour_data_df, closure_data_df,detour_data_df,road_name_drop_box_options,site_id_df,siteblock_list,direction_list
    if closure_type == "block_closure":
        site_id_df = original_site_id_df[original_site_id_df["Site Block"].str.contains(f"^.* .*")]
        site_id_df = site_id_df[site_id_df["Ramp/Mainline"] == "Mainline"]
        siteblock_list =list(set(site_id_df["Site Block"].values))
        siteblock_list.sort()
        road_name_drop_box_options = siteblock_list
        sh_list = list(set(site_id_df["SH"].values))
        closure_data_df = original_block_closure_data_df[original_block_closure_data_df["name"].isin(road_name_drop_box_options)]
        detour_data_df = original_block_detour_data_df[original_block_detour_data_df["name"].isin(road_name_drop_box_options)]
      
    else:
        site_id_df = original_site_id_df[original_site_id_df["Site Block"].str.contains(f"^.*_.*")]
        site_id_df = site_id_df[site_id_df["Ramp/Mainline"] == "Mainline"]
        siteblock_list =list(set(site_id_df["Site Block"].values))
        siteblock_list.sort()
        road_name_drop_box_options = siteblock_list

        closure_data_df = original_closure_data_df[original_closure_data_df["name"].isin(road_name_drop_box_options)]
        detour_data_df = original_detour_data_df[original_detour_data_df["name"].isin(road_name_drop_box_options)]
    direction_list = list(set(site_id_df["Direction"].values))
    direction_list.sort()
    sh_list = list(set(site_id_df["SH"].values))
    sh_list.sort()
    sh_drop_box_options=[]
    for element in sh_list:
        sh_name =""
        if element == "1N":
            sh_name = "SH1"
        else:
            sh_name = "SH"+element
        sh_drop_box_options.append({"label": sh_name, "value": element})
    return dash_deck.DeckGL(
        get_deck(closure_data_df, None, None).to_json(),
        id="deck_map",
        tooltip={"text": "{name}"},
        mapboxKey=mapbox_api_token,
        enableEvents=['click']
    ), sh_drop_box_options, road_name_drop_box_options,None,None,direction_list,None

@dash_app.callback(
    Output("road_name_drop_box","options"),
    Output("road_name_drop_box","value"),
    Output("direction_drop_box","options"),

    Input("sh_drop_box","value"),
    State("direction_drop_box","value"),
    prevent_initial_call=True,
)
def UpdateLocationOptions(sh_drop_box_value,direction_drop_box_value):
    global road_name_drop_box_options,site_id_df,direction_list
    print(sh_drop_box_value)
    if sh_drop_box_value != None and sh_drop_box_value != "":
       
        if direction_drop_box_value != None and direction_drop_box_value != "":
            copy_site_id_df = site_id_df[site_id_df["Direction"] == direction_drop_box_value]
            copy_siteblock_list =list(set(copy_site_id_df["Site Block"].values))
            copy_siteblock_list.sort()
            if sh_drop_box_value == "1N":
                sh_drop_box_value = "SH1"
            else:
                sh_drop_box_value = "SH" + sh_drop_box_value
            
            r = re.compile(f"^{sh_drop_box_value}_.*|^{sh_drop_box_value} .*") 
            road_name_drop_box_options = list(filter(r.match,copy_siteblock_list))
            return road_name_drop_box_options,None,direction_list
        else:
            copy_site_id_df = site_id_df[site_id_df["SH"] == sh_drop_box_value]
            direction_list = list(set(copy_site_id_df["Direction"].values))
            direction_list.sort()
            if sh_drop_box_value == "1N":
                sh_drop_box_value = "SH1"
            else:
                sh_drop_box_value = "SH" + sh_drop_box_value
           
            r = re.compile(f"^{sh_drop_box_value}_.*|^{sh_drop_box_value} .*")  
            road_name_drop_box_options = list(filter(r.match,siteblock_list))
            return road_name_drop_box_options,None,direction_list
    else:
       
        if direction_drop_box_value != None and direction_drop_box_value != "":
            
            direction_list = list(set(site_id_df["Direction"].values))
            direction_list.sort()
            copy_site_id_df = site_id_df[site_id_df["Direction"] == direction_drop_box_value]
            copy_siteblock_list =list(set(copy_site_id_df["Site Block"].values))
            copy_siteblock_list.sort()
            road_name_drop_box_options = copy_siteblock_list
           
            return road_name_drop_box_options,None,direction_list

        direction_list = list(set(site_id_df["Direction"].values))
        direction_list.sort()
        road_name_drop_box_options = siteblock_list
        
        return road_name_drop_box_options,None,direction_list
    

@dash_app.callback(
    Output("sh_drop_box","options"),
    Output("sh_drop_box","value"),
    Input("direction_drop_box","value"),
    State("sh_drop_box","value"),
    prevent_initial_call=True,
)
def UpdateSHnumber(direction_drop_box_value,sh_drop_box_value):
    global road_name_drop_box_options,site_id_df,sh_drop_box_options
    if direction_drop_box_value != None and direction_drop_box_value != "":
        if sh_drop_box_value != None and sh_drop_box_value != "":
            copy_site_id_df = site_id_df[site_id_df["Direction"] == direction_drop_box_value]
            sh_list = list(set(copy_site_id_df["SH"].values))
            sh_list.sort()
            sh_drop_box_options=[]
            for element in sh_list:
                sh_name =""
                if element == "1N":
                    sh_name = "SH1"
                else:
                    sh_name = "SH"+element
                sh_drop_box_options.append({"label": sh_name, "value": element})
            return sh_drop_box_options,sh_drop_box_value
        else:
            copy_site_id_df = site_id_df[site_id_df["Direction"] == direction_drop_box_value]
            sh_list =list(set(copy_site_id_df["SH"].values))
            sh_list.sort()
            sh_drop_box_options = []
            for element in sh_list:
                sh_name =""
                if element == "1N":
                    sh_name = "SH1"
                else:
                    sh_name = "SH"+element
                sh_drop_box_options.append({"label": sh_name, "value": element})
            return sh_drop_box_options,None
    else:
        if sh_drop_box_value != None and sh_drop_box_value != "":
            sh_list = list(set(site_id_df["SH"].values))
            sh_list.sort()
            sh_drop_box_options=[]
            for element in sh_list:
                sh_name =""
                if element == "1N":
                    sh_name = "SH1"
                else:
                    sh_name = "SH"+element
                sh_drop_box_options.append({"label": sh_name, "value": element})
           
            
           
            
            return sh_drop_box_options,sh_drop_box_value
        else:
            sh_list = list(set(site_id_df["SH"].values))
            sh_list.sort()
            sh_drop_box_options=[]
            for element in sh_list:
                sh_name =""
                if element == "1N":
                    sh_name = "SH1"
                else:
                    sh_name = "SH"+element
                sh_drop_box_options.append({"label": sh_name, "value": element})
            

            return sh_drop_box_options,None




@dash_app.callback(
    Output("map_container","children"),
    Output("closed_lanes_drop_box","options"),
    Output("closed_lanes_drop_box","value"),
    Input("road_name_drop_box","value"),
    State("closure_type","value"),
    prevent_initial_call=True,
)
def UpdateLanesOptionaAndMapColor(road_name_drop_box_value,closure_type):
    global road_name_drop_box_options,closure_data_df,detour_data_df,closure_layout_data,detour_layout_data,total_lanes
    if closure_type == "block_closure":
        closure_data_df = original_block_closure_data_df[original_block_closure_data_df["name"].isin(road_name_drop_box_options)]
        detour_data_df = original_block_detour_data_df[original_block_detour_data_df["name"].isin(road_name_drop_box_options)]
    else:
        closure_data_df = original_closure_data_df[original_closure_data_df["name"].isin(road_name_drop_box_options)]
        detour_data_df = original_detour_data_df[original_detour_data_df["name"].isin(road_name_drop_box_options)]
    if road_name_drop_box_value == None or road_name_drop_box_value == "":
        return dash_deck.DeckGL(
            get_deck(closure_data_df, None, None).to_json(),
            id="deck_map",
            tooltip={"text": "{name}"},
            mapboxKey=mapbox_api_token,
            enableEvents=['click']), [],None
    else:
        closure_layout_data = gpd.GeoDataFrame()
        detour_layout_data = gpd.GeoDataFrame()
        closure_value = closure_data_df[closure_data_df.name == road_name_drop_box_value]
        closure_detail = site_id_df[site_id_df["Site Block"] == road_name_drop_box_value]
        total_lanes = int(closure_detail["Number of Lane(s)"].values[0])
        lanes_options = [i+1 for i in range(total_lanes)]
        closure_value["color"] =  closure_value["color"].apply(update_color)
        #closure_layout_data = closure_layout_data.append(closure_value,ignore_index  = True)
        closure_layout_data = pd.concat([closure_layout_data,closure_value], ignore_index = True)
        detour_value = detour_data_df[detour_data_df.name == road_name_drop_box_value]
        #detour_layout_data = detour_layout_data.append(detour_value, ignore_index = True)
        detour_layout_data = pd.concat([detour_layout_data,detour_value], ignore_index = True)

        return dash_deck.DeckGL(
                        get_deck(closure_data_df,closure_layout_data,None).to_json(),
                        id = "deck_map",
                        tooltip = {"text": "{name}"}, 
                        mapboxKey = mapbox_api_token,
                        enableEvents=['click']
                    ),lanes_options,None
    
@dash_app.callback(
    Output("map_container","children"),
    Input("closed_lanes_drop_box","value"),
   
    prevent_initial_call=True,
)
def UpdateMapDetour(closed_lanes_drop_box_value):
    global full_closure,total_lanes
    if closed_lanes_drop_box_value != None and closed_lanes_drop_box_value != "":
        closed_lanes_drop_box_value = int(closed_lanes_drop_box_value)
        
        if total_lanes == closed_lanes_drop_box_value:
            full_closure = True
            return dash_deck.DeckGL(
                            get_deck(closure_data_df,closure_layout_data,detour_layout_data).to_json(),
                            id = "deck_map",
                            tooltip = {"text": "{name}"}, 
                            mapboxKey = mapbox_api_token,
                            enableEvents=['click']
                        )
        
    return dash_deck.DeckGL(
        get_deck(closure_data_df, closure_layout_data,None).to_json(),
        id="deck_map",
        tooltip={"text": "{name}"},
        mapboxKey=mapbox_api_token,
        enableEvents=['click']
    )

@dash_app.callback(
    Output("road_name_drop_box","value"),
    Input("deck_map","clickInfo"),
    State("road_name_drop_box","value"),
    prevent_initial_call=True,
)
def UpdateRoadNameDropBox(clickInfo,closed_lanes_drop_box_value):
    if clickInfo == None:
        raise dash.exceptions.PreventUpdate
    
    elif clickInfo["object"] !=None:
        if str(clickInfo["object"]["name"]) == closed_lanes_drop_box_value:
            return None
        else:
            return str(clickInfo["object"]["name"])
        
    else:
        raise dash.exceptions.PreventUpdate


@dash_app.callback(
    Output("closur_histogram","figure"),
    Output("detour_histogram","figure"),
    Output("error_alert","is_open"),
    Output("error_alert","children"),
    Output("graph_tabs","value"),

    Input("calculation_btn","n_clicks"),
    State("road_name_drop_box","value"),
    State("closed_lanes_drop_box","value"),
    State("date_picker","date"),
    State("start_time_hour","value"),
    State("start_time_minute","value"),
    State("end_time_hour","value"),
    State("end_time_minute","value"),
    prevent_initial_call=True,
)
def ShowHistogram(n_clicks,road_name_drop_box_value,closed_lanes_drop_box_value,date_picker_date,start_time_hour,start_time_minute,end_time_hour,end_time_minute):
    global full_closure,original_block_closure_data_df,seasonal_data_df,profile_label,detour_layout_data,closure_layout_data,total_lanes
    

    try:
        start_time_value = start_time_hour + ":"+ start_time_minute
        end_time_value = end_time_hour + ":"+ end_time_minute
        closur_histogram, detour_histogram = cf.run(road_name_drop_box_value,start_time_value,end_time_value,closed_lanes_drop_box_value,original_site_id_df,seasonal_data_df,profile_label,date_picker_date,cluster_parameter,detour_plan,total_lanes)

                                                    
        show_tab = "closure_graph"
        if full_closure:
            show_tab = "detour_graph"
        return closur_histogram,detour_histogram,False,"",show_tab
    except Exception as e:
        if road_name_drop_box_value == None or closed_lanes_drop_box_value == None or date_picker_date == None == None or start_time_hour == None or start_time_minute == None or  end_time_hour == None or end_time_minute:
            msg = "Plase Check your parameters"
        else:
            msg = f"The road id is not available yet, please try it later."
        print("error msg: ", e)
        figure = {
            "layout": {
                "paper_bgcolor": "#111111",
                "plot_bgcolor": "#111111",
                'font': {
                    'color': "#111111"
                }
            }
        }
        return figure,figure,True,msg,"detour_graph"
        
if __name__ == "__main__":
    
    #serve(dash_app, host="0.0.0.0", port=8080)
    dash_app.run_server(port= 8080,debug = False)