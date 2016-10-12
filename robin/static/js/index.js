$.fn.datepicker.defaults.format = "yyyy-mm-dd";
$.fn.datepicker.defaults.autoclose = true;
$.fn.datepicker.defaults.todayBtn = true;


function formatTime(timestamp, formater) {
    var date = new Date(timestamp);
    var year = date.getFullYear();
    var month = date.getMonth() + 1;
    var day = date.getDate();
    var hour = date.getHours();
    var min = date.getMinutes();
    var sec = date.getSeconds();
    if (month < 10) {
        month = "0" + month;
    }
    if (day < 10) {
        day = "0" + day;
    }
    if (hour < 10) {
        hour = "0" + hour;
    }
    if (min < 10) {
        min = "0" + min;
    }
    if (sec < 10) {
        sec = "0" + sec;
    }
    return formater.replace("Y", year).replace("M", month).replace("D", day).replace("h", hour).replace("m", min).replace("s", sec);
}


function get(url, data) {
    return $.ajax({
        type: "get",
        url: url,
        dataType: "json",
        data: data
    }).done(function(res) {
        return res;
    });
}


var reopData = new Vue({
    el: 'body',
    data: {
        repoData: {
            count: 0,
            baseUrl: null,
            nextUrl: null,
            prevUrl: null,
            repos: []
        },
        teamData: {
            count: 0,
            baseUrl: null,
            nextUrl: null,
            prevUrl: null,
            teams: [],
            checked: false
        },
        repoTmp: [],
        teamTmp: [],
        Repochecked: false,
        repository_id: 0
    },
    watch: {
        repos: function(val) {
            var self = this;
            val.forEach(function(el, index) {
                if (el.checked == undefined) {
                    alert('1111')
                    var status = _.findIndex(self.repoTmp, function(o) {
                        return o.repository_id == el.repository_id;
                    })
                    val.$set(index, {
                        repository_id: el.repository_id,
                        checked: status == -1 ? false: true
                    })
                }
            })
        }
    },
    methods: {
        chooseRepo: function(repo) {
            if (!repo.checked) {
                this.repoTmp.push(repo);
                _.sortedUniq(this.repoTmp)
                console.log(this.repoTmp[0])
            } else {
                _.remove(this.repoTmp, function(el) {
                    return el.repository_id == repo.repository_id;
                })
            }
        },
        chooseTeam: function(team) {
            console.log('123123')
            console.log(team.team_code)
            console.log('321321')
            console.log(team.members)
            if (!teamData.checked) {
                this.teamTmp.push(team);
                _.sortedUniq(this.teamTmp);
                console.log(teamTmp)
            } else {
                _.remove(this.teamTmp, function(el) {
                    return el.unique_id == product.unique_id;
                })
            }
        },
        say: function(msg){
            alert(msg)
        }
    },
    created: function() {
        var self = this;
        // this.apiUrl = '/api/repositories/';
        get('/api/repositories/').then(function(res) {
            var time = formatTime(+new Date(), 'Y-M-D');
            self.repoData.repos = res.results;
            self.repoData.count = res.count;
            self.repoData.nextUrl = res.next;
            self.repoData.prevUrl = res.previous;
        });

        get('/api/teams/').then(function(res) {
            var time = formatTime(+new Date(), 'Y-M-D');
            self.teamData.teams = res.results;
            self.teamData.count = res.count;
            self.teamData.nextUrl = res.next;
            self.teamData.prevUrl = res.previous;
            // console.log(self.teamData.teams);
        });
    }
});


// var teamData = new Vue({
//     el: '#team-panel',
//     data: {
//     	count: 0,
//         baseUrl: null,
//         nextUrl: null,
//         prevUrl: null,
//         teams: []
//     },

//     created: function() {
//         var self = this;
//         // this.apiUrl = '/api/repositories/';
//         get('/api/teams/').then(function(res) {
//             var time = formatTime(+new Date(), 'Y-M-D');
//             self.teams = res.results;
//             self.count = res.count;
//             self.nextUrl = res.next;
//             self.prevUrl = res.previous;
//             console.log(self.teams);
//         });
//     }
// });