function accordeonFlip(id) {
  var content = document.getElementById("sem"+id);
  var arrowR = document.getElementById("arrowR"+id);
  var arrowD = document.getElementById("arrowD"+id);
  if (content.className.indexOf("w3-hide") != -1) {
    content.className = content.className.replace("w3-hide", "w3-show");
    arrowR.className = arrowR.className.replace("w3-hide", "w3-show-inline");
    arrowD.className = arrowD.className.replace("w3-show-inline", "w3-hide");
  } else {
    content.className = content.className.replace("w3-show", "w3-hide");
    arrowR.className = arrowR.className.replace("w3-show-inline", "w3-hide");
    arrowD.className = arrowD.className.replace("w3-hide", "w3-show-inline");
  }
}