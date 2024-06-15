document.querySelectorAll('.plus-cart').forEach(function(button) {
    button.addEventListener('click', function() {
        console.log('clicked');
        var id = this.getAttribute("pid");
        console.log(id);
        var quantity = this.parentNode.children[2];
        
        var xhr = new XMLHttpRequest();
        xhr.open("GET", `/pluscart?prod_id=${id}`, true);
        xhr.onreadystatechange = function() {
            if (xhr.readyState == 4 && xhr.status == 200) {
                var data = JSON.parse(xhr.responseText);
                console.log(data);
                quantity.innerText = data.quantity;
                document.getElementById(`product${id}`).innerText = data.quantity;
                document.getElementById(`amount_tt`).innerText = data.amount;
                document.getElementById("totalamount").innerText = data.total;
            }
        };
        xhr.send();
    });
});

document.querySelectorAll('.minus-cart').forEach(function(button) {
    button.addEventListener('click', function() {
        console.log('clicked');
        var id = this.getAttribute("pid");
        var quantity = this.parentNode.children[2];
        
        var xhr = new XMLHttpRequest();
        xhr.open("GET", `/minuscart?prod_id=${id}`, true);
        xhr.onreadystatechange = function() {
            if (xhr.readyState == 4 && xhr.status == 200) {
                var data = JSON.parse(xhr.responseText);
                console.log(data);
                quantity.innerText = data.quantity;
                document.getElementById(`product${id}`).innerText = data.quantity;
                document.getElementById(`amount_tt`).innerText = data.amount;
                document.getElementById("totalamount").innerText = data.total;
            }
        };
        xhr.send();
    });
});















// $('.plus-cart').click(function(){
//     console.log('clicked');
//     var id = $(this).attr("pid").toString();
//     console.log(id);
//     var quantity = this.parentNode.children[2];
//     $.ajax({
//         type: "GET",
//         url: "/pluscart",
//         data: {
//             prod_id: id
//         },
//         success: function(data) {
//             console.log(data);
//             quantity.innerText = data.quantity;
//             document.getElementById(`quantity${id}`).innerText = data.quantity;
//             document.getElementById(`amount_tt`).innerText = data.amount;
//             document.getElementById("totalamount").innerText = data.total;
//         }
//     });
// });

// $('.minus-cart').click(function(){
//     console.log('clicked');
//     var id = $(this).attr("pid").toString();
//     var quantity = this.parentNode.children[2];
//     $.ajax({
//         type: "GET",
//         url: "/minuscart",
//         data: {
//             prod_id: id
//         },
//         success: function(data) {
//             console.log(data);
//             quantity.innerText = data.quantity;
//             document.getElementById(`quantity${id}`).innerText = data.quantity;
//             document.getElementById(`amount_tt`).innerText = data.amount;
//             document.getElementById("totalamount").innerText = data.total;
//         }
//     });
// });



// $('.remove-cart').click(function(){
//     var id = $(this).attr("pid").toString();
//     var to_remove_element = this.parentNode.parentNode.parentNode.parentNode;


//     $.ajax({
//         type: "GET",
//         url: "/remove_cart_item",
//         data: {
//             prod_id: id
//         },
//         success: function(data){
        
//                 console.log(data);
//                 document.getElementById(`amount_tt`).innerText = data.amount;
//                 document.getElementById(`quantity${id}`).innerText = data.quantity;
//                 document.getElementById("totalamount").innerText = data.total;
//                 to_remove_element.remove();
//         }
// })
// })