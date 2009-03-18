Ext.onReady(function() {

	var input = new Ext.form.Form({
		hideLabels: true
	});

	var message = new Ext.form.TextField({
		id: "message",
		name: "message"
	});

	message.addListener("specialkey", function(form, e) {
		if (e.getKey() == 13) {
			getResponse();
		}
	});

	function checkResponse(el, success) {
		if (el.dom.childNodes.length == 0) {
			Ext.Msg.alert("Status", "No reponse returned");
		}
	}

	function getResponse() {
		var reply = Ext.get("reply");

		reply.load({
			url: "/message",
			params: "message=" + Ext.get("message").dom.value,
			text: "Retrieving response...",
			callback: checkResponse
		});

		reply.show();
		message.reset();
		message.focus();
	}

	input.add(message);
	message.autoSize();
	input.render("input");
	message.focus();

});
