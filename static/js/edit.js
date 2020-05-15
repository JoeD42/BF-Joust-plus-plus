


let vm = new Vue({
    el: "#app",
    delimiters: ["[[", "]]"],
    data: {
        private: true,
        name: "",
        content: "",
        pk: 0,
        err_msg: "",

    },
    methods: {
        save: function() {
            this.err_msg = ""; // reset error message
            if(is_new_program){ // create new program
                axios({
                    url: "/api/new/",
                    method: "post",
                    headers: {
                        "X-CSRFToken": document.querySelector("input[name=csrfmiddlewaretoken]").value
                    },
                    data: {
                        private: this.private,
                        name: this.name,
                        content: this.content
                    }
                }).then(response => {
                    is_new_program = false; //once we save, this is out program now
                    this.err_msg = "Program saved";
                    this.pk = response.data;
                }).catch(error => {
                    console.log(error.response);
                    if(error.response.data === "Already exists!"){
                        this.err_msg = "One of your programs already has that name!";
                    } else {
                        this.err_msg = "An error occurred while trying to save!"
                    }
                });
            } else { // edit existing program
                axios({
                    url: `/api/edit/${this.pk}/`,
                    method: "put",
                    headers: {
                        "X-CSRFToken": document.querySelector("input[name=csrfmiddlewaretoken]").value
                    },
                    data: {
                        private: this.private,
                        name: this.name,
                        content: this.content
                    }
                }).then(response => {
                    this.err_msg = "Program saved";
                }).catch(error => {
                    console.log(error.response);
                    if(error.response.data === "Already exists!"){
                        this.err_msg = "One of your programs already has that name!";
                    } else {
                        this.err_msg = "An error occurred while trying to save!";
                    }
                })
            }
        },
        remove: function() {
            this.err_msg = "";
            if(this.pk == 0){
                this.err_msg = "This program has not been saved, and therefore cannot be deleted!";
            } else if(confirm("Are you sure you want to delete this program?")){
                axios({
                    url: `/api/delete/${this.pk}/`,
                    method: "delete",
                    headers: {
                        "X-CSRFToken": document.querySelector("input[name=csrfmiddlewaretoken]").value
                    }
                }).then(response => {
                    window.location.assign(`/user/${response.data}/`);
                }).catch(error => {
                    console.log(error.response);
                    this.err_msg = "An error occurred while trying to delete!";
                });
            }
        },
        verify: function() {
            axios({
                url: "/api/verify/",
                method: "post", //I would prefer get, but post is the only way to get the data through without dumping it in the url
                headers: {
                    "X-CSRFToken": document.querySelector("input[name=csrfmiddlewaretoken]").value
                },
                data: {
                    raw: this.content
                }
            }).then(response => {
                if(response.data.success){
                    this.err_msg = "No Errors found.";
                } else {
                    this.err_msg = response.data.msg;
                }
            }).catch(error => {
                console.log(error.response);
                this.err_msg = "An error occurred while trying to verify!";
            });
        }

    },
    mounted: function() {
        if(!is_new_program){ //load program
            axios({
                url: `/api/get/${current_author}/${load_name}`,
                method: "get",
                headers: {
                    "X-CSRFToken": document.querySelector("input[name=csrfmiddlewaretoken]").value
                }
            }).then(response => {
                this.private = response.data.private;
                this.name = response.data.name;
                this.content = response.data.content;
                this.pk = response.data.pk;
            }).catch(error => {
                console.log(error);
                this.err_msg = "Error loading the program"
            });
        }
    }
});