import requests
from time import sleep

with open("Maxence CR1000_TAB_Tempe.csv") as f:
    data = [d.split(",") for d in f.readlines()]

i=0
for d in data:
    requests.post("https://dev.galtech.cc/api/data", json={"type":"upload", "data":{"points": [{"mesure_name":"étalonage", "time":i, "temperatures":[{"sensor_id":"PT100 ET. 4W", "value":d[5]}, {"sensor_id":"PT100 Test 3W", "value":d[6]}, {"sensor_id":"PT100 ET. 3W", "value":d[7]}]}]}})
    i+=1
    sleep(5)
