function flipMenu() {
  var menu = document.getElementById("menu");
  if (menu.className.indexOf("w3-show") == -1) {
    menu.className = menu.className.replace("w3-hide-small", "w3-show");
  } else { 
    menu.className = menu.className.replace("w3-show", "w3-hide-small");
  }
}

function setLang(lang){
  document.cookie = "django_language="+lang+";path=/"; 
  location.reload();
}

// Get the modal
var modal = document.getElementById('tos_modal');

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
  if (event.target == modal) {
    modal.style.display = "none";
  }
}