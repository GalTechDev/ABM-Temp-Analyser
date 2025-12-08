from flask import request
from web.devtool import Page, render_template, Log
import jinja2
import web.core.Mesure as Mesure
from web.core.weather import data2point
import random

env = jinja2.Environment(loader=jinja2.FileSystemLoader("web/page/html"))
route_view = Page.Route("/view")
route_data = Page.Route("/data")
route_station = Page.Route("/mesure/<path:path>")

route_temperature = Page.Route("/temperature")

random.seed(123)

#get
@route_view.get()
def main():
    return render_template(env, "index.html", mesures=Mesure.getMesuresID(), page="home")

@route_station.get()
def view_station(path):
    list_data_type = ["temperature"]
    return render_template(env, "mesure.html", mesures=Mesure.getMesuresID(), page="mesure", list_data_type=list_data_type)

@route_data.command()
def delete_mesure(data):
    mesure = data.get("mesure")
    mesures = data.get("mesures")
    if mesure:
        Mesure.delete_mesure(mesure)
    elif mesures:
        for mesure, sensors in mesures.items():
            for sensor in sensors:
                Mesure.delete_sensor(mesure, sensor)
    return {}

@route_data.command()
def rename_mesure(data):
    old_name = data.get("old_name")
    new_name = data.get("new_name")
    Log.print(old_name, new_name)
    if old_name and new_name:
        Mesure.rename_mesure(old_name, new_name)
    return {}

@route_data.get()
def get_data():
    random.seed(123)

    mesure = request.args.get("mesure")
    data_type = request.args.get("type")
    last_hours = request.args.get("dtime")

    if mesure:
        if last_hours:
            if int(last_hours) < 0:
                return Mesure.getLastDataFor(mesure)
            elif int(last_hours) == 0:
                points = Mesure.getAllPointsFor(mesure)
            else:
                points = Mesure.getLastHoursFor(mesure, last_hours)
        else:
            points = Mesure.getAllPointsFor(mesure)
    else:
        if last_hours:
            if int(last_hours) < 0:
                return Mesure.getLastData()
            elif int(last_hours) == 0:
                points = Mesure.getAllPoints()
            else:
                points = Mesure.getLastHours(last_hours)
        else:
            points = Mesure.getAllPoints()

    data = {}

    for point in points:
        w_point = data2point(point)

        col = ['sensor_id', 'time', 'temperature']
        if w_point.get("mesure_name") not in list(data.keys()):
            data.update({w_point.get("mesure_name"): {data_t:[] for data_t in (col if not data_type else ["time", "sensor_id", data_type])}})
        
        for key in list(data[w_point.get("mesure_name")].keys()):
            data[w_point.get("mesure_name")][key].append(w_point.get(key))

    return data

    
@route_temperature.get()
def data_page():
    return render_template(env, "type_data.html", mesures=Mesure.getMesuresID(), page=request.path.removeprefix("/"))