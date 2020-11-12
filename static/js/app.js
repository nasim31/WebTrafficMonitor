    //Here we listen for Pusher events from backend API and use the date to update traffic monitor dashboard pages in realtime
    // Configure Pusher instance
    const pusher = new Pusher(os.environ.get('PUSHER_APP_KEY'), { //first we register new instane of Pusher
        cluster: os.environ.get('PUSHER_APP_CLUSTER'),
        encrypted: true
      });
  
      var months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  
      $(document).ready(function(){
          var dataTable = $("#dataTable").DataTable()
          // var userSessions = $("#userSessions").DataTable()
          var pages = $("#pages").DataTable()
  
          axios.get('/get-all-sessions') //we use axios to get all session saved to database when document is ready
          .then(response => {
                response.data.forEach((data) => {
                    insertDatatable(data)
                })
            var d = new Date();
            var updatedAt = `${d.getFullYear()}/${months[d.getMonth()]}/${d.getDay()} ${d.getHours()}:${d.getMinutes()}:${d.getSeconds()}`
            document.getElementById('session-update-time').innerText = updatedAt
          })
  
          var sessionChannel = pusher.subscribe('session'); //created new pusher cahnnel and subcrbed to a session event
          sessionChannel.bind('new', function(data) {
              insertDatatable(data)
          });
  
          var d = new Date();
          var updatedAt = `${d.getFullYear()}/${months[d.getMonth()]}/${d.getDay()} ${d.getHours()}:${d.getMinutes()}:${d.getSeconds()}`
          document.getElementById('session-update-time').innerText = updatedAt
      });
  
      function insertDatatable(data){ //this function isnerts a new user record whenver Pusher sends an update
          var dataTable = $("#dataTable").DataTable()
          dataTable.row.add([
              data.time,
              data.ip,
              data.continent,
              data.country,
              data.city,
              data.os,
              data.browser,
              `<a href=${"/dashboard/"+data.session}>View pages visited</a>`
            ]);
            dataTable.order([0, 'desc']).draw();
      }