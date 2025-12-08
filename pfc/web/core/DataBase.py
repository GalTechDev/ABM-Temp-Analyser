import sqlite3
import threading

class DB:
    bdd: sqlite3.Connection = ...
    curseur: sqlite3.Cursor = ...
    def connect(self): ...
    def close(self): ...
    

class DataBase:
    def __init__(self):
        self.bdd = None
        self.curseur = None

    def connect(self):
        self.bdd = sqlite3.connect('station/data.db')
        self.curseur = self.bdd.cursor()

    def close(self):
        if self.bdd is not None:
            self.bdd.close()

    def __enter__(self) -> DB:
        if not hasattr(threading.current_thread(), 'db'):
            threading.current_thread().db = DataBase()
            threading.current_thread().db.connect()
        return threading.current_thread().db

    def __exit__(self, exc_type, exc_value, traceback):
        if hasattr(threading.current_thread(), 'db'):
            threading.current_thread().db.close()
            del threading.current_thread().db

def exec_query(query, parameter=None):
    res = []

    with DataBase() as db:
        if parameter and len(parameter) == len(query):
            for i in range(len(query)):
                db.curseur.execute(query[i], parameter[i])
                res.append(db.curseur.fetchall())
                
        else:
            if query:
                if isinstance(query, str):
                    db.curseur.execute(query)
                    res.append(db.curseur.fetchall())
                    
                elif isinstance(query, tuple) or isinstance(query, list):
                    for q in query:
                        db.curseur.execute(q)
                        res.append(db.curseur.fetchall())
                        
                else:
                    raise Exception("Incorrect format of bindings supplied.")
            else:
                raise Exception("Incorrect number of bindings supplied.")

        db.bdd.commit()

    if len(res)==1:
        return res[0]
    return res

if __name__ == "__main__":
    database = DataBase()
    database.connect()

    #exec_query("CREATE TABLE Donnees (IDmesure TEXT, datesyst TEXT, temperature FLOAT)")