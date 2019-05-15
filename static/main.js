// CLIENT FUNCTIONS
function getClientName() {
  var cName = $('#clientName').val()
  window.location = "/" + cName
}

function reRun() {
  var cName = $('#clientName').val()
  $.ajax({
      url: "/run/" + cName,
      context: document.body
  }).done(function() {
      window.location = "/" + cName
  });
}

var url = window.location.href;
var client = url.substr(url.lastIndexOf('/') + 1);
if (client != '') {
    $('#clientName').val(client)
}
