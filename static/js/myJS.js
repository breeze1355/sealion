// 用户上传照片点击上传按钮后不可再点击
$('#saveButton').on('click', function () {
let $btn = $(this).button('loading');
$btn.attr("disable","true")
});

// 签到摄像头关闭后刷新页面
$('#signModal').on('hidden.bs.modal', function () {
    window.location.reload();
});

