function get_data(station = null, data_type = null, dtime = null) {
    let url = "/data?";
    if (station) {
        url += "mesure=" + station + "&";
    }
    if (data_type) {
        url += "type=" + data_type + "&";
    }
    if (dtime) {
        url += "dtime=" + dtime;
    }

    return get(url).then(function (response) {
        return response
    });
}

