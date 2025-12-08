import requests

def exec_query(query, parameter=None):
    url = "http://192.168.1.117:5001/api"
    res = []
    if parameter and len(parameter) == len(query):
        response = requests.post(url, json={"type": "db_query", "data":{"query":query, "parameter":parameter}})
        res = response.json().get("result")
            
    else:
        if query:
            if isinstance(query, str):
                response = requests.post(url, json={"type": "db_query", "data":{"query":query, "parameter":None}})
                res.append(response.json().get("result"))
                
            elif isinstance(query, tuple) or isinstance(query, list):
                for q in query:
                    response = requests.post(url, json={"type": "db_query", "data":{"query":q, "parameter":None}})
                    res.append(response.json().get("result"))
                    
            else:
                raise Exception("Incorrect format of bindings supplied.")
        else:
            raise Exception("Incorrect number of bindings supplied.")

    if len(res)==1:
        return res[0]
    return res



if __name__ == "__main__":
    pass
    #print(exec_query("SELECT * FROM Donnees"))