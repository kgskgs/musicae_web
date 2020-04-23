document.addEventListener("DOMContentLoaded", function() {
    var elements = document.getElementsByTagName("INPUT");
    for (var i = 0; i < elements.length; i++) {
        elements[i].oninvalid = function(e) {
            e.target.setCustomValidity("");
            if (!e.target.validity.valid) {
                if (e.target.validity.valueMissing)
                    e.target.setCustomValidity(document.getElementById("err_blank").textContent);
                if (e.target.validity.typeMismatch)
                    e.target.setCustomValidity(document.getElementById("err_mail").textContent);
            }
        };
        elements[i].oninput = function(e) {
            e.target.setCustomValidity("");
        };
    }
})