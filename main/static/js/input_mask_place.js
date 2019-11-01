// $('#id_place').inputmask({ mask: function () {
//     /* do stuff */
//         return ["[ан]9[-99]", "[ст]9[-999]", "[ст]9[-99/9]", "99-999"];
//     }
// });

// For info https://www.npmjs.com/package/jquery.inputmask


$('#id_place').inputmask({
    regex: "[а-яА-Я0-9/-]*"
});
