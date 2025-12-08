from web.core.DataBase import exec_query

tablename = "Donnees"

def getAllPoints():
    query = f"SELECT * FROM {tablename}"
    res = exec_query(query)
    return res

if __name__ == "__main__":
    pass