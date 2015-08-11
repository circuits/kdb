$(document).ready(function() {
    $("#terminal").terminal("/wapi", {
        login: false,
        greetings: "For help type: help",
        onBlur: function() {
            // the height of the body is only 2 lines initialy
            return false;
        }
    });
});
