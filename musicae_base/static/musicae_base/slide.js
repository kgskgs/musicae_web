var slideIndex = [];

window.onload = function(){ 

  for (var i = 0; i < document.getElementsByClassName("newsGrpParent").length; i++) {
    slideIndex.push(1);
    showDivs(1, i);
  }
    
}

function plusDivs(n, ind) {
  showDivs(slideIndex[ind] += n, ind);
}

function showDivs(n, ind) {
  
  var i;
  var x = document.getElementsByClassName("slide_container"+ind);

  console.log(x, slideIndex)

  if (n > x.length) {slideIndex[ind] = 1}
  if (n < 1) {slideIndex[ind] = x.length} ;
  for (i = 0; i < x.length; i++) {
    x[i].style.display = "none";
  }
  x[slideIndex[ind]-1].style.display = "block";
}
