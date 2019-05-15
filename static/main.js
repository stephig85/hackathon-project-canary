// CLIENT FUNCTIONS
function getClientName() {
  var cName = $('#clientName').val()
  window.location = "/" + cName
  return false;
}

function populateClient() {
  var cName = $('#clientName').val()
  $.ajax({
      url: "/run/" + cName,
      context: document.body
  }).done(function() {
      window.location = "/" + cName
  });
  return false;
}

var url = window.location.href;
var client = url.substr(url.lastIndexOf('/') + 1);
if (client != '') {
    $('#clientName').val(client)
}

$("#clientName").keyup(function(event) {
    if (event.keyCode === 13) {
        getClientName()
    }
});
