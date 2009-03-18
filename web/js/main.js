$(document).ready(function() {

    $("#navbar").find("a").each(function(i) {
        $(this).click(function() {
            var url = $(this).attr("href");
            $("#response > pre").load(url);
            return false;
        });
    });

    $("#input > form").submit(function() {
        var message = $("input:first").val();
        $("input:field").val("");
        $("#response > pre").load("/message", {"message": message});
        return false;
    });

});

// vim: nocindent
