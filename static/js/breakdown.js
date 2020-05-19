
Vue.component("game", {
    props: ["game", "main"],
    template: `<div>
        <strong><a v-bind:href="'/debug?tleft=' + main + '&tright=' + (game.left === main ? game.right : game.left)">
            vs {{ game.left === main ? game.right : game.left }}</a></strong><br/>
        <span v-for="match in game.games">
            {{ match.winner == 0 ? "=" : ((match.winner < 0 && game.left === main)||(match.winner > 0 && game.right == main)) ? "<" : ">" }}
            <br v-if="match.tape_len === 32">
        </span>
    </div>`
})


let vm = new Vue({
    el: "#app",
    delimiters: ["[[", "]]"],
    data: {
        hill_programs: [],
        current_program: "",
        current_games: []
    },
    methods: {
        update: function() {
            this.current_games = [];
            axios({
                url: `/api/breakdown/${this.current_program}/`,
                method: "get",
                headers: {
                    "X-CSRFToken": document.querySelector("input[name=csrfmiddlewaretoken]").value
                }
            }).then(response => {
                this.current_games = response.data;
            }).catch(error => {
                console.log(error.response);
            })
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
            if(start_prog){
                this.current_program = start_prog;
            } else {
                this.current_program = this.hill_programs[0].name;
            }
            this.update();
        }).catch(error => {
            console.log(error.response);
        })

    }
})