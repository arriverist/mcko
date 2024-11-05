var a = 0;

document.getElementById("remember").addEventListener("click", () => {
    a++;
    document.getElementById("remember").style.backgroundColor = "green";
        if (a % 2 == 0){
            document.getElementById("remember").style.backgroundColor = "white";
        }
    })