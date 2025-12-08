class WeatherPoint:
    def __init__(   self, mesure_name: str, sensor_id: str, time: int, value: float):

        self.mesure_name = mesure_name
        self.sensor_id = sensor_id
        self.time = time
        self.value = value

    def get(self, type):
        return self.__getattribute__(type)

    def __iter__(self):
        return iter([self.mesure_name, self.sensor_id, self.time, self.value])

    def __str__(self):
        return f"mesure_name : {self.mesure_name}\nsensor_id : {self.sensor_id}\nh : +{self.time}\n"

def data2point(data):
    mesure_name = data[0]
    sensor_id = data[1]
    time = data[2]
    value = data[3]

    return WeatherPoint(mesure_name, sensor_id, time, value)