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

function confirmBox(somefunc) {
        bootbox.confirm({
        title: 'Confirm Delete',
        message: 'Are you sure you want to delete this? This cannot be undone.',
        buttons: {
                cancel: {
                label: '<i class="fa fa-times"></i> Cancel'
                },
                confirm: {
                label: '<i class="fa fa-check"></i> Confirm'
                }
        },
        callback: function (result) {
                console.log('This was logged in the callback: ' + result);
                somefunc(result);
        }
        });
}