//const fetch_param = {cache: "no-cache"};
const fetch_param = {};

function LoadPage() {
    var path = window.location.search;
    var file = (path == "") ? "home" : path.substring(1);
    fetch(file + ".md", fetch_param)
        .then(response => response.text())
        .then(text => {
            document.getElementById("content").innerHTML = marked.parse(text);
            hljs.highlightAll();
        });
}

function LoadHeader() {
    fetch("header.html", fetch_param)
        .then(response => response.text())
        .then(text => {
            document.getElementById("header").innerHTML = text;
        });
}

function LoadFooter() {
    fetch("footer.html", fetch_param)
        .then(response => response.text())
        .then(text => {
            document.getElementById("footer").innerHTML = text;
        });
}
