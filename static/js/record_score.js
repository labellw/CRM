$(function () {
//    修改成绩事件
    $(".score").change(function () {
        var sid = $(this).attr("sid");
        var val = $(this).val();
        $.ajax({
            url:"",
            type:'post',
            data:{
                sid:sid,
                vai:val,
                action:"score"
            },
            success:function (data) {
                console.log(data)
            }

        })
    });
//    修改评语事件
    $(".note").blur(function () {
        var sid = $(this).attr("sid");
        var val = $(this).val();

        $.ajax({
            url:"",
            type:"post",
            data:{
                sid:sid,
                val:val,
                action:"homework_note",
            },
            success:function (data) {
                console.log(data)
            }
        })

    })

});