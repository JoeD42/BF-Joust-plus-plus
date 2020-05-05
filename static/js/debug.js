Vue.component("gameselect", {
    props: ["game"],
    template: `<span class="game-select">
    <button @click="$emit('showgame', game)">{{ game.winner > 0 ? ">" : game.winner < 0 ? "<" : "=" }}</button>
    <br v-if="game.tape_len === 32"/></span>`
})

Vue.component("tape_cell", {
    props: ["cell", "is_flag", "l_pos", "r_pos"],
    template: `<span>{{ l_pos ? r_pos ? "X" : ">" : r_pos ? "<" : " "}}{{ cell.toString(16).toUpperCase() }}</span>`
})

Vue.component("turn", {
    props: ["turn", "turn_num"],
    template: `<div class="turn">
        {{turn_num}}:
        {{ turn.l_pos < 0 || turn.l_pos >= turn.tape.length ? "☠" : turn.tape[1] === 0 ? "⚐" : "⚑" }}
        <tape_cell v-for="(cell, index) in turn.tape"
        v-bind:cell="cell" v-bind:is_flag="index === 1 || index === (turn.tape.length - 2)"
        v-bind:l_pos="turn.l_pos === index" v-bind:r_pos="turn.r_pos === index"></tape_cell>
        {{ turn.r_pos < 0 || turn.r_pos >= turn.tape.length ? "☠" : turn.tape[turn.tape.length - 2] === 0 ? "⚐" : "⚑" }}
    </div>`
})


let vm = new Vue({
    el: "#app",
    delimiters: ["[[", "]]"],
    data: {
        left: "",
        right: ":+|-;>(-)*6>(+)*7>-(+)*17>(-)*12>(+)*8>(-)*7>(+)*8>(+)*3>[(-)*5[+]]>>[(+)*7[-]]>>([(+)*14[-]]>)*3([(-)*14[+]]>)*3[(-)*7[+]]>>[(+)*6[-]]>>([(+)*14[-]]>)*3[(-)*14[+]]>[(+)*14[-]]>[(-)*16[+]]>[(-)*7[+]]",
        loading: "",
        result: "",
        game_select: [],
        current_game: {}
    },
    methods: {
        run: function() {
            this.loading = "Loading..."
            axios({
                url: "../api/debug/",
                method: "post",
                headers: {
                    "X-CSRFToken": document.querySelector("input[name=csrfmiddlewaretoken]").value
                },
                data: {
                    left: this.left,
                    right: this.right
                }
            }).then(response => {
                let rep = response.data;
                console.log(rep);
                switch(rep.error){
                    case 0:
                        this.loading = "";
                        this.game_select = rep.games;
                        this.result = 0;
                        this.game_select.forEach(game => {
                            this.result += game.winner;
                        });
                        break;
                    case -1:
                        this.loading = `Left Program Error: ${rep.err_msg}`;
                        break;
                    case 1:
                        this.loading = `Right Program Error: ${rep.err_msg}`;
                        break;
                    default:
                        this.loading = `Error ${rep.error}: ${rep.err_msg}`;
                }
            }).catch(error => {this.loading = `Error: ${error}`;});
        },
        showGame: function(game) {
            this.current_game = game;
        }
    }
})