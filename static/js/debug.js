const CELL_WIDTH = 20;


Vue.component("gameselect", {
    props: ["game"],
    template: `<span class="game-select">
    <button @click="$emit('showgame', game)">{{ game.winner > 0 ? ">" : game.winner < 0 ? "<" : "=" }}</button>
    <br v-if="game.tape_len === 32"/></span>`
})

Vue.component("tape_cell", {
    props: ["cell", "is_flag", "l_pos", "r_pos"],
    template: `<span v-bind:class="[l_pos || r_pos ? 'active_cell' : is_flag ? 'flag_cell' : '']">
    {{ l_pos ? r_pos ? "X" : ">" : r_pos ? "<" : "&nbsp;"}}{{ cell < 16 ? "0" : "" }}{{ cell.toString(16).toUpperCase() }}</span>`
})

Vue.component("turn", {
    props: ["turn", "turn_num"],
    template: `<div class="turn">
        {{ !Math.floor(turn_num/10000) ? "&nbsp;" : "" }}{{ !Math.floor(turn_num/1000) ? "&nbsp;" : "" }}
        {{ !Math.floor(turn_num/100) ? "&nbsp;" : "" }}{{ !Math.floor(turn_num/10) ? "&nbsp;" : "" }}{{turn_num}}:
        <span class="flag_cell">{{ turn.l_cmp === "?" ? "t!0" : turn.l_cmp === "=" ? "t=r" : turn.l_cmp ? "t!r" : "r!0" }}</span>
        {{ turn.l_pos < 0 || turn.l_pos >= turn.tape.length ? "✖" : turn.tape[1] === 0 ? "⚐" : "⚑" }}
        <tape_cell v-for="(cell, index) in turn.tape"
        v-bind:cell="cell" v-bind:is_flag="index === 1 || index === (turn.tape.length - 2)"
        v-bind:l_pos="turn.l_pos === index" v-bind:r_pos="turn.r_pos === index"></tape_cell>&nbsp;
        {{ turn.r_pos < 0 || turn.r_pos >= turn.tape.length ? "✖" : turn.tape[turn.tape.length - 2] === 0 ? "⚐" : "⚑" }}
        <span class="flag_cell">{{ turn.r_cmp === "?" ? "t!0" : turn.r_cmp === "=" ? "t=r" : turn.r_cmp ? "t!r" : "r!0" }}</span>
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
        current_game: { tape_len: 0 },
        canvas: "",
        ctx: "",
        current_turn: 0
    },
    methods: {
        run: function() {
            this.loading = "Loading...";
            this.current_game = { tape_len: 0 };
            this.game_select = [];
            result = "";
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
                // console.log(rep);
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
        draw: function() {
            this.ctx.fillStyle = "#000000";
            this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
            let offset = Math.floor(CELL_WIDTH / 2);
            for(let i = -1; i < this.current_game.tape_len + 1; ++i){
                if(this.current_game.turns[this.current_turn].l_pos){
                    if(this.current_game.turns[this.current_turn].r_pos){
                        this.ctx.fillStyle = "#FF00FF";
                        this.ctx.fillRect(offset, this.canvas.height - Math.floor(CELL_WIDTH/2), CELL_WIDTH, CELL_WIDTH);
                    } else {

                    }
                }
            }
        },
        showGame: function(game) {
            this.current_game = game;
            this.canvas.width = (game.tape_len + 3) * CELL_WIDTH;
            this.ctx.fillStyle = "#000000";
            this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
            // this.ctx.clearRect(10, 10, CELL_WIDTH, CELL_WIDTH);
        }
    },
    mounted: function() {
        this.canvas = document.getElementById("canvas");
        this.ctx = this.canvas.getContext("2d");
        this.canvas.height = 256 + CELL_WIDTH * 2;
    }
})