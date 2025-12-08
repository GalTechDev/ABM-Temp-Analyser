from web.core.DataBase import exec_query
from datetime import datetime, timedelta, timezone

tablename = "Donnees"

def getMesuresID():
    query = f"SELECT DISTINCT mesure_name FROM {tablename} ORDER BY mesure_name"
    res = exec_query(query)
    return [r[0] for r in res]

def getAllPoints():
    query = f"SELECT * FROM {tablename} ORDER BY time"
    res = exec_query(query)
    return res

def getAllPointsFor(mesure):
    query = f"SELECT * FROM {tablename} WHERE mesure_name = ? ORDER BY time"
    res = exec_query([query], [(mesure,)])
    return res

def getLastHours(hours):
    query = f"SELECT * FROM {tablename} WHERE time >= ? ORDER BY time"
    res = exec_query([query], [(datetime.now(timezone.utc) - timedelta(hours=int(hours)-1),)])
    return res

def getLastHoursFor(mesure, hours):
    query = f"SELECT * FROM {tablename} WHERE mesure_name = ? AND time >= ? ORDER BY time"
    res = exec_query([query], [(mesure, datetime.now(timezone.utc) - timedelta(hours=int(hours)-1))])
    return res

def getLastDataFor(mesure):
    query = f"SELECT * FROM {tablename} WHERE mesure_name = ? ORDER BY time DESC LIMIT 1"
    res = exec_query([query], [(mesure,)])
    if res:
        return res[-1]
    else:
        return []

def getLastData():
    full_res = {}
    for mesure in getMesuresID():
        query = f"SELECT * FROM {tablename} WHERE mesure_name = ? ORDER BY time DESC LIMIT 1"
        res = exec_query([query], [(mesure,)])
        if res:
            full_res.update({mesure:res})
        else:
            full_res.update({mesure:[]})

    return full_res

def delete_mesure(mesure):
    query = f"DELETE FROM {tablename} WHERE mesure_name = ?"
    exec_query([query], [(mesure,)])

def delete_sensor(mesure, sensor_id):
    query = f"DELETE FROM {tablename} WHERE mesure_name = ? AND sensor_id = ?"
    exec_query([query], [(mesure, sensor_id)])

def rename_mesure(old_name, new_name):
    query = f"UPDATE {tablename} SET mesure_name = ? WHERE mesure_name = ?"
    exec_query([query], [(new_name, old_name)])

if __name__ == "__main__":
    pass