const fetch_param = {cache: "no-cache"};
//const fetch_param = {};

function LoadHeader() {
  fetch("header.html", fetch_param).then(response => response.text()).then(text => {
    document.getElementById("header").innerHTML = text;
  });
}

function LoadFooter() {
  fetch("footer.html", fetch_param).then(response => response.text()).then(text => {
    document.getElementById("footer").innerHTML = text;
  });
}
