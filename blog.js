//const fetch_param = {cache: "no-cache"};
const fetch_param = {};
const postlimit = 5;
var pagenum = 0;
var pagelimit = 0;

function LoadHeader() {
    fetch("header.html")
        .then(response => response.text())
        .then(text => {
            document.getElementById("header").innerHTML = text;
        });
}

function LoadFooter() {
    fetch("footer.html")
        .then(response => response.text())
        .then(text => {
            document.getElementById("footer").innerHTML = text;
        });
}

function LoadList() {
    var path = window.location.search;
    if(path != "" && Number(path.substring(1)) != NaN) {
        pagenum = Number(path.substring(1));
    }

    fetch("posts.json", fetch_param)
        .then(response => response.json())
        .then(data => {
            pagelimit = parseInt((data.posts.length - 1) / postlimit);
            var start = pagenum * postlimit;
            var end = start + postlimit;
            if(data.posts.length < end)
            {
                end = data.posts.length;
            }

            const src = document.getElementById("posts-template").innerHTML;
            var res = "";
            for(var i = start; i < end; i++)
            {
                var s = src;
                res += s
                    .replace(/{url}/g, data.posts[i].url)
                    .replace(/{title}/g, data.posts[i].title)
                    .replace(/{date}/g, data.posts[i].date);
            }
            document.getElementById("posts").innerHTML = res;
        });
}

function PrevPage() {
    if(pagenum == 0) {
        return;
    }
    if(pagenum > 0) {
        pagenum--;
    }
    document.location.href = "index.html?" + pagenum;
}

function NextPage() {
    if(pagenum == pagelimit) {
        return;
    }
    if(pagenum < pagelimit) {
        pagenum++;
    }
    document.location.href = "index.html?" + pagenum;
}

function LoadPage() {
    var path = window.location.search;
    var file = (path == '') ? 'undefined' : path.substring(1);
    fetch("posts/" + file + ".md", fetch_param)
        .then(response => response.text())
        .then(text => {
            document.getElementById("content").innerHTML = marked.parse(text);
            hljs.highlightAll();
        });
}

function LoadPosts() {
}

function LoadTags() {
}
