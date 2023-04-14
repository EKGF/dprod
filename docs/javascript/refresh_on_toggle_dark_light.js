const paletteSwitcher1 = document.getElementById("__palette_1");
const paletteSwitcher2 = document.getElementById("__palette_2");

paletteSwitcher1.addEventListener("change", function () {
    location.reload();
});

paletteSwitcher2.addEventListener("change", function () {
    location.reload();
});