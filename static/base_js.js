function like(ev, id) {
    $.get("/like/" + id, function (d) {
        if (+d)
            $(ev.target).removeClass('glyphicon-heart-empty').addClass('glyphicon-heart')
        else
            $(ev.target).addClass('glyphicon-heart-empty').removeClass('glyphicon-heart')
    })
}
function rate(ev, id) {
    $.get("/rate/" + id + '/' + $('#rating').val())
}
function updateTextInput(val) {
    document.getElementById('textInput').value=val;
}