function readURL(input) {
  if (input.files && input.files[0]) {
    var reader = new FileReader();

    reader.onload = function(e) {
      $('#output').attr('src', e.target.result);
    }

    reader.readAsDataURL(input.files[0]);
  }
}

$("#photo-input").change(function() {
  readURL(this);
  $('#output').addClass('mb-4');
});

// $( ".inner" ).append( "<hr>" );