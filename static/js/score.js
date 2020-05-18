
Vue.component("program", {
    props: ["prog"],
    template: `<div class="row">
        <div class="one column">{{ prog.rank }}</div>
        <div class="one column">
            {{ prog.prev_rank == 0 ? "new" : prog.prev_rank - prog.rank == 0 ? "--" :
            prog.prev_rank - prog.rank > 0 ? "+" + (prog.prev_rank - prog.rank) : prog.prev_rank - prog.rank }}
        </div>
        <div class="six columns"><a href="">{{ prog.name }}</a></div>
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