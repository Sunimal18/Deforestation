document.addEventListener("DOMContentLoaded", function () {

    console.log("Forest AI Dashboard Loaded");

    const checkboxes = document.querySelectorAll("input[type='checkbox']");

    checkboxes.forEach(box => {
        box.addEventListener("change", function () {
            console.log(this.parentElement.textContent.trim() + " toggled");
        });
    });

});