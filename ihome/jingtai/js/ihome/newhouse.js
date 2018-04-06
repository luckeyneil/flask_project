function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function () {
    // $('.popup_con').fadeIn('fast');
    // $('.popup_con').fadeOut('fast');
    // 向后端获取城区的信息
    $.get("/api/v1_0/areas", function (resp) {
        if (resp.errno == 0) {
            // 获取到了城区信息
            var areas = resp.data.areas;
            for (i = 0; i < areas.length; i++) {
                var area = areas[i];
                $("#area-id").append('<option value="' + area.aid + '">' + area.aname + '</option>')
            }
            ;
        } else {
            alert(resp.errmsg);
        }
    });


})