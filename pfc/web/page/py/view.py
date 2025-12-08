from web.devtool import Page, render_template
import jinja2
from web.core.weather import WeatherPoint
from web.core.Mesure import getAllPoints
from web.core.DataBase import exec_query
from .data_api import insert_table, drop_table, create_table
from time import sleep


env = jinja2.Environment(loader=jinja2.FileSystemLoader("web/page/html"))
route_api = Page.Route("/api")
route_api_data = Page.Route("/api/data")
route_db = Page.Route("/clear_db")
new_data = False
wss = {}

@route_db.get()
def clear_db():
    drop_table()
    create_table()
    return "DBClear !"

#get
@route_api_data.get()
def main():
    p = getAllPoints()
    p.reverse()
    return render_template(env, "index.html", points=p)

@route_api_data.command()
def upload(data):
    """_summary_

    Args:
        data (dict): {"points": [{"mesure_name":"", "time":1, "temperatures":[{"sensor_id":"", "value":20}, ]}, ]}

    Returns:
        dict: {}
    """
    global new_data
    points = data.get("points")
    for point in points:
        mesure_name = point.get("mesure_name", "name_not_found")
        h = point.get("time", -1)
        temperatures = point.get("temperatures")

        for temperature in temperatures:
            sensor_id = temperature.get("sensor_id")
            value = temperature.get("value")

            insert_table(WeatherPoint(mesure_name, sensor_id, h, value))
            new_data = True
    return {}

@Page.websocket("/api/data_ws", subdomain="abm")
def handle_connect(ws):
    global new_data
    print("Client connecté")

    while True:
        if new_data:
            ws.send("new_data") 
            new_data = False
        sleep(2)

@route_api.command()
def db_query(data):
    global new_data
    new_data = False
    query = data.get("query")
    parameter = data.get("parameter")
    result = exec_query(query, parameter)

    return {"result": result}