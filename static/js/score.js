
Vue.component("program", {
    props: ["prog"],
    template: `<div class="row">
        <div class="one column">{{ prog.rank }}</div>
        <div class="one column">
            {{ prog.prev_rank == 0 ? "new" : prog.prev_rank - prog.rank == 0 ? "--" :
            prog.prev_rank - prog.rank > 0 ? "+" + (prog.prev_rank - prog.rank) : prog.prev_rank - prog.rank }}
        </div>
        <div class="five columns">
            <a v-bind:href="'/breakdown?prog=' + prog.name">
            {{ prog.name }}</a></div>
        <div class="one column">
            <a v-bind:href="'/raw?hill=' + prog.name"><i class="far fa-file-alt"></i></a>&nbsp;
            <a v-bind:href="'/debug?tleft=' + prog.name"><i class="fas fa-play"></i></a>
        </div>
        <div class="two columns">{{ prog.score }}</div>
        <div class="two columns">{{ prog.points }}</div>
    </div>`
})


let vm = new Vue({
    el: "#app",
    delimiters: ["[[", "]]"],
    data: {
        hill_programs: []
    },
    methods: {
        sortScores: function(sort_method){
            let sort_fun = {};
            if(sort_method === "rank_asc"){
                sort_fun = function(a, b) { return a.rank - b.rank; }
            } else if(sort_method === "rank_des"){
                sort_fun = function(a, b) { return b.rank - a.rank; }
            } else if(sort_method === "name_asc"){
                sort_fun = function(a, b) { return a.name.localeCompare(b.name); }
            } else if(sort_method === "name_des"){
                sort_fun = function(a, b) { return b.name.localeCompare(a.name); }
            } else if(sort_method === "points_asc"){
                sort_fun = function(a, b) { return b.points - a.points; }
            } else if(sort_method === "points_des"){
                sort_fun = function(a, b) { return a.points - b.points; }
            } else {
                sort_fun = function(a, b) { return 0; }
            }
            this.hill_programs.sort(sort_fun);
        }
    },
    mounted: function() {
        axios({
            url: "/api/hill/",
            method: "get",
            headers: {
                "X-CSRFToken": document.querySelector("input[name=csrfmiddlewaretoken]").value
            }
        }).then(response => {
            this.hill_programs = response.data;
            this.hill_programs.sort(function(a, b){
                return a.rank - b.rank;
            })
        }).catch(error => {
            console.log(error.response);
        })
    }
});