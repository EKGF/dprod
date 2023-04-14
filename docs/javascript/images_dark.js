const paletteSwitcher1 = document.getElementById("__palette_1");
const paletteSwitcher2 = document.getElementById("__palette_2");

paletteSwitcher1.addEventListener("change", function () {
    documentFromDarkToLight(document)
});

paletteSwitcher2.addEventListener("change", function () {
    documentFromLightToDark(document)
});

if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    alert("you're in dark mode")    // dark mode
} else {
    alert("you're in light mode")
}

window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
    const newColorScheme = e.matches ? "dark" : "light";
    alert("zzzzz " + newColorScheme)
});

document.addEventListener("DOMContentLoaded", function(){
    alert('The page has fully loaded');
    const palette = __md_get("__palette");
    alert("palette: " + palette)
    if (palette && typeof palette.color === "object")
        if (palette.color.scheme === "slate") {
            alert("dark: " + palette.color.scheme)
        }
    }
});


// if (window.matchMedia('(prefers-color-scheme: dark)').matches === true) {
//     documentFromLightToDark(document)
// }

const darkModeMediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
darkModeMediaQuery.addListener((e) => {
    const darkModeOn = e.matches;

    if (darkModeOn)
        documentFromLightToDark(document)
    else
        documentFromDarkToLight(document)
    console.log(`Dark mode is ${darkModeOn ? '🌒 on' : '☀️ off'}.`);
});

function documentFromDarkToLight(document) {
    imagesFromDarkToLight(document.querySelectorAll('img[src$="darkable"'));
    objectsFromDarkToLight(document.querySelectorAll('object[data$="darkable"'));
}

function documentFromLightToDark(document) {
    imagesFromLightToDark(document.querySelectorAll('img[src$="darkable"'));
    objectsFromLightToDark(document.querySelectorAll('object[data$="darkable"'));
}

function imagesFromLightToDark(images) {
    images.forEach(image => {
        const idx = image.src.lastIndexOf('.');
        if (idx > -1) {
            const add = "_dark";
            image.src = [image.src.slice(0, idx), add, image.src.slice(idx)].join('');
        }
    });
}

function imagesFromDarkToLight(images) {
    images.forEach(image => {
        image.src = image.src.replace("_dark", "");
    });
}

function objectsFromLightToDark(objects) {
    objects.forEach(object => {
        const idx = object.data.lastIndexOf('.');
        if (idx > -1) {
            const add = "_dark";
            object.data = [object.data.slice(0, idx), add, object.data.slice(idx)].join('');
        }
    });
}

function objectsFromDarkToLight(objects) {
    objects.forEach(object => {
        object.data = object.data.replace("_dark", "");
    });
}

