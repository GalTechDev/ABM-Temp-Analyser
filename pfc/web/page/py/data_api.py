from web.core.DataBase import exec_query

def clear_db():
    drop_table()
    create_table()
            
def create_table():
    query = """
    CREATE TABLE Donnees
    (
        mesure_name VARCHAR(10),
        sensor_id VARCHAR(10),
        time NUMBER,
        T FLOAT
    );
    """
    res = exec_query(query)
    return res

def drop_table():

    query = "DROP TABLE Donnees"

    res = exec_query(query)
    return res

def insert_table(Point):

    query = """
    
    INSERT INTO Donnees
    VALUES (?, ?, ?, ?);
    """
    
    res = exec_query([query], [(*Point,)])
    return res