function accordeonFlipSearch(id) {
  var content = document.getElementById("filter"+id);
  var arrowR = document.getElementById("arrowR"+id);
  var arrowD = document.getElementById("arrowD"+id);
  var btn1 = document.getElementById("search1");
  var btn2 = document.getElementById("search2");
  var stitle = document.getElementsByName("title")[0];
  var detailed = document.getElementById("detailed");
  if (content.className.indexOf("w3-hide") != -1) {
    content.className = content.className.replace("w3-hide", "w3-show");
    arrowR.className = arrowR.className.replace("w3-hide", "w3-show-inline");
    arrowD.className = arrowD.className.replace("w3-show-inline", "w3-hide");
    btn2.className = btn2.className.replace("w3-hide", "w3-show");
    btn1.className = btn1.className.replace("w3-show", "w3-hide");
    stitle.className = stitle.className.replace("w3-show", "w3-hide");
    detailed.value = 1;
  } else {
    content.className = content.className.replace("w3-show", "w3-hide");
    arrowR.className = arrowR.className.replace("w3-show-inline", "w3-hide");
    arrowD.className = arrowD.className.replace("w3-hide", "w3-show-inline");
    btn1.className = btn1.className.replace("w3-hide", "w3-show");
    btn2.className = btn2.className.replace("w3-show", "w3-hide");
    stitle.className = stitle.className.replace("w3-hide", "w3-show");
    detailed.value = 0;
  }
}

function checkAll(name){
  var boxes = document.getElementsByName(name);
  var set = false

  for (var i=0; i < boxes.length; i++){
    if (boxes[i].checked == false){
      set = true;
      break;
    }
  }

  boxes.forEach(function (item, index){
    item.checked = set;
  });
}

function sortTable(n, tableId) {
  //https://www.w3schools.com/howto/howto_js_sort_table.asp
  var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
  table = document.getElementById(tableId);
  ths = table.getElementsByTagName("TH").length;
  switching = true;
  // Set the sorting direction to ascending:
  dir = "asc";
  /* Make a loop that will continue until
  no switching has been done: */
  while (switching) {
    // Start by saying: no switching is done:
    switching = false;
    rows = table.rows;
    /* Loop through all table rows (except the
    first, which contains table headers): */
    for (i = 1; i < (rows.length - 1); i++) {
      // Start by saying there should be no switching:
      shouldSwitch = false;
      /* Get the two elements you want to compare,
      one from current row and one from the next: */
      x = rows[i].getElementsByTagName("TD")[n];
      y = rows[i + 1].getElementsByTagName("TD")[n];
      /* Check if the two rows should switch place,
      based on the direction, asc or desc: */
      if (dir == "asc") {
        if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
          // If so, mark as a switch and break the loop:
          shouldSwitch = true;
          break;
        }
      } else if (dir == "desc") {
        if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
          // If so, mark as a switch and break the loop:
          shouldSwitch = true;
          break;
        }
      }
    }
    if (shouldSwitch) {
      /* If a switch has been marked, make the switch
      and mark that a switch has been done: */
      rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
      switching = true;
      // Each time a switch is done, increase this count by 1:
      switchcount ++;
    } else {
      /* If no switching has been done AND the direction is "asc",
      set the direction to "desc" and run the while loop again. */
      if (switchcount == 0 && dir == "asc") {
        dir = "desc";
        switching = true;
      }
    }
  }

  console.log(dir)

  for (var i = 0; i < ths; i++){
    var arrowU = document.getElementById("thArrowU"+i);
    var arrowD = document.getElementById("thArrowD"+i);
    if (i != n){
      arrowU.className = arrowU.className.replace("w3-show-inline", "w3-hide")
      arrowD.className = arrowD.className.replace("w3-show-inline", "w3-hide")
    } else {
      if (dir == 'asc'){
        arrowU.className = arrowU.className.replace("w3-hide", "w3-show-inline")
        arrowD.className = arrowD.className.replace("w3-show-inline", "w3-hide")
      } else {
        arrowU.className = arrowU.className.replace("w3-show-inline", "w3-hide")
        arrowD.className = arrowD.className.replace("w3-hide", "w3-show-inline")
      }
    }
  }

}