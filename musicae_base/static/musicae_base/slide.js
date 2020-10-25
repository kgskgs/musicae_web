var slideIndex = {};

window.onload = function(){ 

  var parents = document.getElementsByClassName("newsGrpParent")
  for (var i = 0; i < parents.length; i++) {
    var id = parents[i].id.split("_")[1]
    slideIndex[id] = 1;

    showDivs(1, id);
  }
    
}

function plusDivs(n, ind) {
  showDivs(slideIndex[ind] += n, ind);
}

function showDivs(n, ind) {
  
  var i;
  var x = document.getElementsByClassName("slide_container"+ind);

  console.log(ind, x, slideIndex)

  if (n > x.length) {slideIndex[ind] = 1}
  if (n < 1) {slideIndex[ind] = x.length} ;
  for (i = 0; i < x.length; i++) {
    x[i].style.display = "none";
  }
  x[slideIndex[ind]-1].style.display = "block";
}


