function showAlert(message,type = "success") {
    
    const wrapper = document.createElement("div");
    wrapper.innerHTML = `<div class='alert alert-${type} alert-dismissible fade show' role='alert'>`
            + message
            + "<button type='button' class='btn-close' data-bs-dismiss='alert'></button>"
            + "</div>";
    document.getElementById("alertPlaceholder").append(wrapper);
    setTimeout(() => {
            wrapper.querySelector(".alert").classList.remove("show");
            wrapper.querySelector(".alert").classList.add("hide");
            wrapper.remove();
    },3000);        
}