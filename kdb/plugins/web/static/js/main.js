$(document).ready(function() {

    $("#navbar").find("a").each(function(i) {
        $(this).click(function() {
            var url = $(this).attr("href");
            $("#response").load(url);
            return false;
        });
    });

    $("#input > form").submit(function() {
        var message = $("input:first").val();
        $("input:field").val("");
        $("#response > #content").load("/message", {"message": message});
        return false;
    });

});

// vim: nocindent
