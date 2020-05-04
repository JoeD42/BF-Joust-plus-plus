let vm = new Vue({
    el: "#app",
    delimiters: ["[[", "]]"],
    data: {
        left: "",
        right: ":+|-;>(-)*6>(+)*7>-(+)*17>(-)*12>(+)*8>(-)*7>(+)*8>(+)*3>[(-)*5[+]]>>[(+)*7[-]]>>([(+)*14[-]]>)*3([(-)*14[+]]>)*3[(-)*7[+]]>>[(+)*6[-]]>>([(+)*14[-]]>)*3[(-)*14[+]]>[(+)*14[-]]>[(-)*16[+]]>[(-)*7[+]]",
        out: "",
        loading: ""
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
            }).then(response => {this.out = JSON.parse(response); this.loading = this.out.error;}); //This should make this.out a json object
        }
    }
})