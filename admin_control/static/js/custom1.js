// Function to retrieve the CSRF token from the cookie
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


setTimeout(function(){
    $('#messages').fadeOut('slow')
}, 4000)








// #CHANGE ORDER STATUS
function showSelectedOption(selectElement,order_number) {
    // var selectedOption = selectElement.options[selectElement.selectedIndex];
    var selectedOption = selectElement.value
    console.log (selectedOption);
    var data = {
        order_number: order_number,
        selected_option: selectedOption
    };
    $.ajax({
        type: "POST",
        url: "change/status",  // Replace with the actual URL for your view
        dataType: "json", 
        data: JSON.stringify(data),
        headers: {
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": getCookie("csrftoken"), 
          },
        success: (data) => {
            console.log(data);
          },
        error: (error) => {
            console.log(error);
            alert(error)
          }
    });
}


function send_data(inputid, variant_slug, image_id='thumbnail') {
    url = `/admin-control/product/variant/update/additional-images/${variant_slug}/`
    var formData = new FormData();
    var files = $('#photo'+ inputid)[0].files[0]
    formData.append('file', files);
    formData.append('image_id', image_id);

    $.ajax({
      type: "POST",
      url: url,  // Replace with the actual URL for your view
      dataType: "json", 
      data: formData,
      processData: false,
      contentType: false,
      headers: {
          // "X-Requested-With": "XMLHttpRequest",
          "X-CSRFToken": getCookie("csrftoken"), 
        },
      success: (data) => {
        console.log(data);
        document.getElementById('image'+ inputid).setAttribute('src', data['new_image'])
        },
      error: (error) => {
          console.log(error);
          alert(error)
        }
    });
  }



  // Brand control

  function brand_control(brand_id){

    let checkboxValue = brand_id;
    console.log(checkboxValue)
    $.ajax({
        type: 'POST',
        url: `/admin-control/brand/brandcontrol/`,
        headers: {
          "X-CSRFToken": csrftoken
        },

        data: JSON.stringify({checkboxValue: checkboxValue,}),
        success: (data) => {
          console.log(data)
        },
        error: (error) => {
            console.log(error);
          }
    });
}


function attribute_control(brand_id){

  let checkboxValue = brand_id;
  console.log(checkboxValue)
  $.ajax({
      type: 'POST',
      url: `/admin-control/attribute/attributecontrol/`,
      headers: {
        "X-CSRFToken": csrftoken
      },

      data: JSON.stringify({checkboxValue: checkboxValue,}),
      success: (data) => {
        console.log(data)
      },
      error: (error) => {
          console.log(error);
        }
  });
}
function attribute_value_control(attribute_value_id){

  let checkboxValue = attribute_value_id;
  console.log(checkboxValue)
  $.ajax({
      type: 'POST',
      url: `/admin-control/attribute-value/attribute-value-control/`,
      headers: {
        "X-CSRFToken": csrftoken
      },

      data: JSON.stringify({checkboxValue: checkboxValue,}),
      success: (data) => {
        console.log(data)
      },
      error: (error) => {
          console.log(error);
        }
  });
}



