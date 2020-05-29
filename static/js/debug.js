const CELL_WIDTH = 20;
const PLAY_INTERVAL = 20;

/*
    lp, rp = left position, right position
    lx, rx = left code, right code
    lc, rc = left cmp, right cmp
*/

function getCmpStr(c) {
    return c === "?" ? "t!0" : c === "=" ? "t=r" : c ? "t!r" : "r!0"
}

function safeModulo(a, b){
    if(a >= 0) { return a%b; }
    else { return b+a; }
}


Vue.component("gameselect", {
    props: ["game", "winner"],
    template: `<span class="game-select">
    <button class="select-button" @click="$emit('showgame', game)">{{ winner > 0 ? ">" : winner < 0 ? "<" : "=" }}</button>
    <br v-if="game === 20"/></span>`
})
/* No longer using Vue components to load the text output
Vue.component("tape_cell", {
    props: ["cell", "is_flag", "l_pos", "r_pos"],
    template: `<span v-bind:class="[l_pos || r_pos ? 'active_cell' : is_flag ? 'flag_cell' : '']">
    {{ l_pos ? r_pos ? "X" : ">" : r_pos ? "<" : "&nbsp;"}}{{ cell < 16 ? "0" : "" }}{{ cell.toString(16).toUpperCase() }}</span>`
})

Vue.component("turn", { // this component is what's causing the slowdown, not it's sub-component
    props: ["turn", "turn_num", "tape"],
    computed: {
        spacedTurn: function() {
            return `${"\xa0".repeat(5-String(this.turn_num).length)}${this.turn_num}`;
        }
    },
    template: `<div>
        {{spacedTurn}}:
        <span class="flag_cell">{{ turn.lc === "?" ? "t!0" : turn.lc === "=" ? "t=r" : turn.lc ? "t!r" : "r!0" }}</span>
        {{ turn.lp < 0 || turn.lp >= tape.length ? "✖" : tape[1] === 0 ? "⚐" : "⚑" }}
        <tape_cell v-for="(cell, index) in tape"
            v-bind:cell="cell" v-bind:is_flag="index === 1 || index === (tape.length - 2)"
            v-bind:l_pos="turn.lp === index" v-bind:r_pos="turn.rp === index"></tape_cell>&nbsp;
        {{ turn.rp < 0 || turn.rp >= tape.length ? "✖" : tape[tape.length - 2] === 0 ? "⚐" : "⚑" }}
        <span class="flag_cell">{{ turn.rc === "?" ? "t!0" : turn.rc === "=" ? "t=r" : turn.rc ? "t!r" : "r!0" }}</span>
    </div>`
})
*/

let vm = new Vue({
    el: "#app",
    delimiters: ["[[", "]]"],
    data: {
        left: "",
        right: "",
        left_cache: "",
        right_cache: "",
        loaded_left: 0,
        loaded_right: 0,
        all_programs: [{
            name: "",
            content: ""
        }],
        loading: "",
        result: "",
        game_select: [],
        current_game: { tape_len: 0 },
        current_tape: [],
        canvas: "",
        ctx: "",
        text_out: "",
        current_turn: 0,
        is_playing: false, // is a game currently being played on the canvas?
        play_timer: 0, //where we save our interval timer
        play_slider: "",
    },
    methods: {
        loadProgram: function(side) {
            if(side) { //left
                this.left = this.all_programs[this.loaded_left].content;
            } else { // right
                this.right = this.all_programs[this.loaded_right].content;
            }
        },
        testFigure: function(){ //test the new way of getting the tape by comparing it to the old way
            let good = true;
            for(let i = 0; i < this.current_game.turns.length; ++i){
                for(let k = 0; k < this.current_game.tape_len; ++k){
                    if(this.current_game.turns[i].tape[k] != this.current_tape[i][k]) {
                        console.log(k);
                        good = false;
                    }
                }
                if(!good) {
                    console.log(i);
                    console.log(this.current_game.turns[i].tape);
                    console.log(this.current_tape[i]);
                    console.log(this.left_cache[this.current_game.turns[i].lx])
                    console.log(this.right_cache[this.current_game.turns[i].rx])
                    break;
                }
            }
        },
        figureGame: function(){ // create a game based on the moves given to us; will replace the need to receive and store all tape values for all games
            let tape = [];
            let temp_tape = [];
            this.current_tape = [];
            for(let i = 0; i < this.current_game.tape_len; ++i){
                if(i === 1 || i === (this.current_game.tape_len-2)) { tape.push(128); }
                else { tape.push(0); }
            }
            for(let i = 0; i < this.current_game.turns.length; ++i){
                let now = this.current_game.turns[i];
                switch(this.left_cache[now.lx]){ //left program
                    case '+': tape[now.lp] = safeModulo(++tape[now.lp], 256); break;
                    case '-': tape[now.lp] = safeModulo(--tape[now.lp], 256); break;
                    case ',': tape[0] = tape[now.lp]; break;
                    case '#': tape[0] = safeModulo(++tape[0], 256); break;
                    case '~': tape[0] = safeModulo(--tape[0], 256); break;
                }
                switch(this.right_cache[now.rx]){ //right program
                    case '+': tape[now.rp] = safeModulo(++tape[now.rp], 256); break;
                    case '-': tape[now.rp] = safeModulo(--tape[now.rp], 256); break;
                    case ',': tape[this.current_game.tape_len-1] = tape[now.rp]; break;
                    case '#': tape[this.current_game.tape_len-1] = safeModulo(++tape[this.current_game.tape_len-1], 256); break;
                    case '~': tape[this.current_game.tape_len-1] = safeModulo(--tape[this.current_game.tape_len-1], 256); break;
                }

                temp_tape.push(tape.slice());
            }
            //this.testFigure();
            this.current_tape = temp_tape;
        },
        runAlt: async function(){ //a different way of doing the run function
            this.loading = "Loading...";
            this.current_game = { tape_len: 0 };
            this.game_select = [];
            result = "";
            this.text_out = "";

            this.left_cache = this.left.length ? this.left : " ";
            this.right_cache = this.right.length ? this.right : " ";

            let axi_error = false;
            let pol = ["f", "t"];
            this.result = 0;
            for(let i = 0; i < 2; ++i){
                for(let len = 12; len <= 32; ++len){
                    await axios({
                        url: `/api/debug/${len}/${pol[i]}`,
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
                        switch(rep.error){
                            case 0:
                                this.game_select.push(rep.game);
                                this.result += rep.game.winner;
                                break;
                            case -1:
                                this.loading = `Left Program Error: ${rep.err_msg}`;
                                axi_error = true;
                                break;
                            case 1:
                                this.loading = `Right Program Error: ${rep.err_msg}`;
                                axi_error = true;
                                break;
                            default:
                                this.loading = `Error ${rep.error}: ${rep.err_msg}`;
                                axi_error = true;
                        }
                    }).catch(error => {
                        this.loading = `${error}`;
                        axi_error = true;
                    });
                    if(axi_error){ break; }
                }
                if(axi_error){ break; }
            }
            if(!axi_error) { this.loading = ""; }
        },
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
        generateText: function() { //manually write the html for the text output
            let temp = [];
            for(let i = 0; i < this.current_tape.length; ++i){
                let tape = [];
                for(let k = 0; k < this.current_game.tape_len; ++k){ // tape values
                    let position = this.current_game.turns[i].lp === k ? (this.current_game.turns[i].rp === k ? "X" : "&gt;") : (this.current_game.turns[i].rp === k ? "&lt;" : "\xa0");
                    let color = this.current_game.turns[i].lp === k || this.current_game.turns[i].rp === k;
                    let cell = `\xa0${position}${this.current_tape[i][k] < 16 ? "0" : ""}${this.current_tape[i][k].toString(16).toUpperCase()}`;
                    if(color){
                        tape.push(`<span class="active_cell">${cell}</span>`)
                    } else if(k === 1 || k === this.current_game.tape_len){
                        tape.push(`<span class="flag_cell">${cell}</span>`)
                    } else {
                        tape.push(cell);
                    }
                }
                let turn = `${"\xa0".repeat(5-String(i).length)}${i}`;
                let l_flag = this.current_game.turns[i].lp < 0 || this.current_game.turns[i].lp >= this.current_game.tape_len ? "✖" : this.current_tape[i][1] === 0 ? "⚐" : "⚑";
                let r_flag = this.current_game.turns[i].rp < 0 || this.current_game.turns[i].rp >= this.current_game.tape_len ? "✖" : this.current_tape[i][this.current_game.tape_len-2] === 0 ? "⚐" : "⚑";


                temp.push(`<div>${turn}:
                <span class="flag_cell">${getCmpStr(this.current_game.turns[i].lc)}</span>
                ${l_flag}
                ${tape.join("")}\xa0\xa0
                ${r_flag}
                <span class="flag_cell">${getCmpStr(this.current_game.turns[i].rc)}</span></div>`);
            }
            this.text_out = temp.join("");
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

                if(this.current_tape[this.current_turn][i] <= 128){//(this.current_game.turns[this.current_turn].tape[i] <= 128){
                    this.ctx.fillRect(offset, y_offset, CELL_WIDTH, -this.current_tape[this.current_turn][i])//this.current_game.turns[this.current_turn].tape[i])
                } else {
                    this.ctx.fillRect(offset, y_offset + CELL_WIDTH, CELL_WIDTH, -(this.current_tape[this.current_turn][i] - 256))//(this.current_game.turns[this.current_turn].tape[i] - 256))
                }

                offset += CELL_WIDTH;
            }

            offset = Math.floor(CELL_WIDTH/2);
            for(let i = -1; i < this.current_game.tape_len + 1; ++i){ // draw the program positions
                if(this.current_game.turns[this.current_turn].lp === i){
                    if(this.current_game.turns[this.current_turn].rp === i){
                        this.ctx.fillStyle = "#FF00FF";
                    } else {
                        this.ctx.fillStyle = "#FF0000";
                    }
                    this.ctx.fillRect(offset, y_offset, CELL_WIDTH, CELL_WIDTH);
                } else if(this.current_game.turns[this.current_turn].rp === i) {
                    this.ctx.fillStyle = "#0000FF";
                    this.ctx.fillRect(offset, y_offset, CELL_WIDTH, CELL_WIDTH);
                }
                offset += CELL_WIDTH;
            }

        },
        showGame: function(game) {
            clearInterval(this.play_timer);
            this.loading = "Loading match...";
            this.text_out = "";
            game = this.game_select[game]
            this.current_game = game;
            this.canvas.width = (game.tape_len + 3) * CELL_WIDTH;
            this.current_turn = 0;
            this.play_slider.max = game.turns.length - 1;
            this.play_slider.value = 0;
            this.is_playing = false;
            this.figureGame();
            this.draw();
            this.generateText();
            this.loading = "";
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
        },
        showTextDisplay: function(){
            return this.current_game.tape_len && (this.current_game.turns.length == this.current_tape.length);
        },
    },
    mounted: async function() {
        // canvas stuff
        this.canvas = document.getElementById("canvas");
        this.ctx = this.canvas.getContext("2d");
        this.canvas.height = 256 + CELL_WIDTH * 2;
        this.play_slider = document.getElementById("play_slider");
        this.play_slider.oninput = this.sliderMove;

        // get all programs from hill
        await axios({
            url: "/api/hill/",
            method: "get",
            headers: {
                "X-CSRFToken": document.querySelector("input[name=csrfmiddlewaretoken]").value
            }
        }).then(response => {
            this.all_programs = this.all_programs.concat(response.data);
        }).catch(error => { console.log(error.response); });

        // get all programs from current user
        if(current_user) {
            await axios({
                url: `/api/list/${current_user}`,
                method: "get",
                headers: {
                    "X-CSRFToken": document.querySelector("input[name=csrfmiddlewaretoken]").value
                }
            }).then(response => {
                this.all_programs = this.all_programs.concat(response.data);
            }).catch(error => { console.log(error.response); });
        }

        // load programs
        if(got_left_prog){
            let temp = got_left_prog.split(".");
            await axios({
                url: `/api/get/${temp[0]}/${temp[1]}/`,
                method: "get",
                headers: {
                    "X-CSRFToken": document.querySelector("input[name=csrfmiddlewaretoken]").value
                }
            }).then(response => {
                this.left = response.data.content;
                if(got_left_prog.split(".")[0] != current_user){
                    this.all_programs = this.all_programs.concat(response.data);
                    this.loaded_left = this.all_programs.length-1;
                    this.all_programs[this.loaded_left].name = "★" + this.all_programs[this.loaded_left].name;
                } else {
                    this.loaded_left = this.all_programs.findIndex(x => x.name === got_left_prog);
                }
            }).catch(error => {
                console.log(error.response);
            })
        } else if(got_tleft_prog){
            await axios({
                url: `/api/hill/${got_tleft_prog}/`,
                method: "get",
                headers: {
                    "X-CSRFToken": document.querySelector("input[name=csrfmiddlewaretoken]").value
                }
            }).then(response => {
                this.left = response.data.content;
                this.loaded_left = this.all_programs.findIndex(x => x.name === got_tleft_prog);
            }).catch(error => {
                console.log(error.response);
            })
        }
        if(got_right_prog){
            let temp = got_right_prog.split(".");
            await axios({
                url: `/api/get/${temp[0]}/${temp[1]}/`,
                method: "get",
                headers: {
                    "X-CSRFToken": document.querySelector("input[name=csrfmiddlewaretoken]").value
                }
            }).then(response => {
                this.right = response.data.content;
                if(got_right_prog.split(".")[0] != current_user){
                    this.all_programs = this.all_programs.concat(response.data);
                    this.loaded_right = this.all_programs.length-1;
                    this.all_programs[this.loaded_right].name = "★" + this.all_programs[this.loaded_right].name;
                } else {
                    this.loaded_right = this.all_programs.findIndex(x => x.name === got_right_prog);
                }
            }).catch(error => {
                console.log(error.response);
            })
        } else if(got_tright_prog){
            await axios({
                url: `/api/hill/${got_tright_prog}/`,
                method: "get",
                headers: {
                    "X-CSRFToken": document.querySelector("input[name=csrfmiddlewaretoken]").value
                }
            }).then(response => {
                this.right = response.data.content;
                this.loaded_right = this.all_programs.findIndex(x => x.name === got_tright_prog);
            }).catch(error => {
                console.log(error.response);
            })
        }
    }
})