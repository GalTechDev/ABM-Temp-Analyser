function post_command(name, data, url = window.location.pathname) {
  return post({ "type": name, "data": data }, url);
}

function post(json = {}, url = window.location.pathname) {
  json["arguments"] = {}//getParameters(document.URL);

  return fetch(url, { "method": "POST", "headers": { "Content-Type": "application/json" }, "body": JSON.stringify(json), redirect: "follow" })
    .then(function (response) {
      if (response.redirected) {
        document.location.href = response.url;
      } else {
        return response.json().then(r_json => {
          return r_json;
        }).catch(error => {
          return response;
        });
      }
    })
}

function get(url = window.location.pathname) {

  return fetch(url, { "method": "GET", "headers": { "Content-Type": "application/json" }, redirect: "follow" })
    .then(function (response) {
      if (response.redirected) {
        document.location.href = response.url;
      } else {
        return response.json().then(r_json => {
          return r_json;
        }).catch(error => {
          return response;
        });
      }
    })
}

const colors = ["blue", "red", "green", "yellow", "brown"]

function randomColor(color_seed) { 
  return colors[color_seed];
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}