const CELL_WIDTH = 20;
const PLAY_INTERVAL = 20;


Vue.component("gameselect", {
    props: ["game"],
    template: `<span class="game-select">
    <button class="select-button" @click="$emit('showgame', game)">{{ game.winner > 0 ? ">" : game.winner < 0 ? "<" : "=" }}</button>
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
        current_turn: 0,
        is_playing: false, // is a game currently being played on the canvas?
        play_timer: 0, //where we save our interval timer
        play_slider: "",
    },
    methods: {
        run: function() {
            this.loading = "Loading...";
            this.current_game = { tape_len: 0 };
            this.game_select = [];
            result = "";
            axios({
                url: "/api/debug/",
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
            }).catch(error => {this.loading = `${error}`;});
        },
        draw: function() {
            this.ctx.fillStyle = "#000000";
            this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height); // clear canvas
            let offset = Math.floor(CELL_WIDTH / 2) + CELL_WIDTH;
            let y_offset = Math.floor(this.canvas.height/2) - Math.floor(CELL_WIDTH/2);

            for(let i = 0; i < this.current_game.tape_len; ++i){ // draw the tape
                switch(i){ //color the flags
                    case 1: this.ctx.fillStyle = "#FF6060"; break;
                    case (this.current_game.tape_len-2): this.ctx.fillStyle = "#6060FF"; break;
                    default: this.ctx.fillStyle = "#FFFFFF";
                }

                if(this.current_game.turns[this.current_turn].tape[i] <= 128){
                    this.ctx.fillRect(offset, y_offset, CELL_WIDTH, -this.current_game.turns[this.current_turn].tape[i])
                } else {
                    this.ctx.fillRect(offset, y_offset + CELL_WIDTH, CELL_WIDTH, -(this.current_game.turns[this.current_turn].tape[i] - 256))
                }

                offset += CELL_WIDTH;
            }

            offset = Math.floor(CELL_WIDTH/2);
            for(let i = -1; i < this.current_game.tape_len + 1; ++i){ // draw the program positions
                if(this.current_game.turns[this.current_turn].l_pos === i){
                    if(this.current_game.turns[this.current_turn].r_pos === i){
                        this.ctx.fillStyle = "#FF00FF";
                    } else {
                        this.ctx.fillStyle = "#FF0000";
                    }
                    this.ctx.fillRect(offset, y_offset, CELL_WIDTH, CELL_WIDTH);
                } else if(this.current_game.turns[this.current_turn].r_pos === i) {
                    this.ctx.fillStyle = "#0000FF";
                    this.ctx.fillRect(offset, y_offset, CELL_WIDTH, CELL_WIDTH);
                }
                offset += CELL_WIDTH;
            }

        },
        showGame: function(game) {
            clearInterval(this.play_timer);
            this.current_game = game;
            this.canvas.width = (game.tape_len + 3) * CELL_WIDTH;
            this.current_turn = 0;
            this.play_slider.max = game.turns.length - 1;
            this.play_slider.value = 0;
            this.is_playing = false;
            this.draw();
        },
        stepGame: function() {
            // step to next turn
            if(this.current_turn >= this.current_game.turns.length - 1){
                this.current_turn = this.current_game.turns.length - 1;
                clearInterval(this.play_timer);
                this.is_playing = false;
            } else { this.current_turn += 1; }
            this.play_slider.value = this.current_turn;

            this.draw();
        },
        playGame: function() {
            if(this.is_playing) { //stop playing
                this.is_playing = false;
                clearInterval(this.play_timer);
            } else { //play
                if(this.current_turn >= this.current_game.turns.length - 1) { this.current_turn = 0; } //restart when finished
                this.is_playing = true;
                this.play_timer = setInterval(this.stepGame, PLAY_INTERVAL);
            }
        },
        sliderMove: function() {
            this.current_turn = parseInt(this.play_slider.value);
            if(!this.is_playing) { this.draw(); } //if the game is not playing, draw the new board
        }
    },
    mounted: function() {
        // canvas stuff
        this.canvas = document.getElementById("canvas");
        this.ctx = this.canvas.getContext("2d");
        this.canvas.height = 256 + CELL_WIDTH * 2;
        this.play_slider = document.getElementById("play_slider");
        this.play_slider.oninput = this.sliderMove;

        // load programs
        if(got_left_prog){
            let temp = got_left_prog.split(".");
            axios({
                url: `/api/get/${temp[0]}/${temp[1]}/`,
                method: "get",
                headers: {
                    "X-CSRFToken": document.querySelector("input[name=csrfmiddlewaretoken]").value
                }
            }).then(response => {
                this.left = response.data.content;
            }).catch(error => {
                console.log(error.response);
            })
        } else if(got_tleft_prog){
            axios({
                url: `/api/hill/${got_tleft_prog}/`,
                method: "get",
                headers: {
                    "X-CSRFToken": document.querySelector("input[name=csrfmiddlewaretoken]").value
                }
            }).then(response => {
                this.left = response.data.content;
            }).catch(error => {
                console.log(error.response);
            })
        }
        if(got_right_prog){
            let temp = got_right_prog.split(".");
            axios({
                url: `/api/get/${temp[0]}/${temp[1]}/`,
                method: "get",
                headers: {
                    "X-CSRFToken": document.querySelector("input[name=csrfmiddlewaretoken]").value
                }
            }).then(response => {
                this.right = response.data.content;
            }).catch(error => {
                console.log(error.response);
            })
        } else if(got_tright_prog){
            axios({
                url: `/api/hill/${got_tright_prog}/`,
                method: "get",
                headers: {
                    "X-CSRFToken": document.querySelector("input[name=csrfmiddlewaretoken]").value
                }
            }).then(response => {
                this.right = response.data.content;
            }).catch(error => {
                console.log(error.response);
            })
        }
    }
})