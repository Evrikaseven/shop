
$('.custom-file-input').on('change', function() {
   let fileName = $(this).val().split('\\');
   console.log($(this).val());
   $(this).next('.custom-file-label').addClass("selected").html(fileName);
});


// $(function() {
//   $('#order').change(function(){
//     let sum =  parseInt($("#price-input").val(), 10) * parseInt($("#count-input").val(), 10);
//     $('#check_sum').html( sum + sum / 10);
//   });
// });
