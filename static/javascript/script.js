var clicks_counter = 0;

document.getElementById("remember").addEventListener("click", () => {
    clicks_counter++;
    document.getElementById("remember").style.backgroundColor = "green";
        if (a % 2 == 0){
            document.getElementById("remember").style.backgroundColor = "rgb(200, 200, 200)";
        }
    })