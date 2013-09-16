/**
 * For page user_add
 *
 * User: delin
 * Date: 15.09.13
 * Time: 22:02
 */

$(document).ready(function() {
  $("input[name='view_advanced']").click(function() {
    $('#div-advanced').toggleClass('hidden');
  });

  $("input[name='create_home']").click(function() {
    $('#group-home').toggleClass('hidden');
  });

  $("input[name='set_other_shell']").click(function() {
    $('#group-shell').toggleClass('hidden');
    $('#group-other_shell').toggleClass('hidden');
  });

    $("#input-login").keyup(function () {
        var login = $(this).val();
        var value = "";

        if (login.length > 0) {
            value = "/home/" + login;
        }
        $("#input-home").val(value);
    }).keyup();
});