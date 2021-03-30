$(document).ready(function () {
// jQuery.noConflict();
    $('[data-toggle="tooltip"]').tooltip();


    $("#dialog-confirm").dialog({
        autoOpen: false,
        resizable: false,
        height: "auto",
        width: 500,
        modal: true,
    });

    $('.form-control').selectmenu();

    var replenishButton = {
        "Replenish": function () {
            $(this).dialog("close");
        },
        Cancel: function () {
            $(this).dialog("close");
        }
    }

    var successButtonText = {
        "Continue": function () {
            $(this).dialog("close");
            var len = ($(this).data("len"));
            textConvert(len)
        },
        Cancel: function () {
            $(this).dialog("close");
        }
    }

    var errorButton = {
        Cancel: function () {
            $(this).dialog("close");
        }
    }

    var successButtonFile = {
        "Continue": function () {
            $(this).dialog("close");
            var file = $(this).data("file");
            var filePath = $(this).data("file_path");
            var size = $(this).data("size");
            var date = $(this).data("date");
            var _this = $(this).data("this");
            var len = $(this).data("len");
            var fileName = $(this).data("fileName")
            fileConvert(_this, file, fileName, filePath, size, date, len)
        },
        Cancel: function () {
            $(this).dialog("close");
        }
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    var csrftoken = getCookie('csrftoken');
    var textConvert = function (len) {
        var convertButton = $(".convert_button");
        var convertAnim = convertButton.next();
        convertButton.hide();
        convertAnim.show();
        var textVal = $('#input_text_form').find("textarea").val();
        var data = new FormData();
        data.append('text_input', textVal);
        data.append('text_len', len)

        $.ajax({
            headers: {"X-CSRFToken": csrftoken},
            url: 'input_text',
            type: 'POST',
            data: data,
            context: this,
            cache: false,
            processData: false,
            contentType: false,
            success: function (response, status, xhr) {
                convertAnim.hide();
                convertButton.show();
                var convertId = xhr.getResponseHeader('id');
                var outputText = $('.js-copytextarea');
                outputText.text(response);
                var urlDownload = 'ajax_open_file?id=' + convertId + "&type=d";
                var aDownload = $('.output_download_link')
                aDownload.attr({
                    href: urlDownload,
                    target: '_blank',
                });
            },
            error: function () {
                convertAnim.hide();
                convertButton.show();
            }
        })
    }


    $('.convert_button').on("click", function (event) {
        event.preventDefault();
        var len = $(this).closest('#input_text_form').find("textarea").val().length;
        var dialog = $("#dialog-confirm")


        $.ajax({
            url: "text_len",
            type: "GET",
            data: {len: len},
            context: this,
            success: function () {
                if (len === 0) {
                    dialog.text('Please fill out the form.');
                    dialog.data('len', len).dialog({buttons: errorButton});
                    dialog.dialog("open");
                } else if (len > 15000) {
                    dialog.text('The text is too long.Please use the download form');
                    dialog.data('len', len).dialog({buttons: errorButton});
                    dialog.dialog("open");
                } else {
                    dialog.text(len + " points will be deducted from your account. Continue?");
                    dialog.data('len', len).dialog({buttons: successButtonText});
                    dialog.dialog("open");
                }
            },
            error: function () {
                dialog.text("На вашем счету недостаточно средств. Пополнить?");
                dialog.dialog({buttons: replenishButton});
                dialog.dialog('open');

            }
        });
    })


    $('.upload-file__input').on('change', function () {
        var file = this.files[0];
        var spanText = $(this).next().children('.upload-file__span').text();
        var clone = $(".upload_form:last").clone(true)
        $(this).parent().next('.submit_file_form__div').children('.submit_file_form').css("display", "inline");
        $(this).next().children('.upload-file__span').text(file.name);
        $(this).next().children('.upload_svg').css("display", "none");
        $(this).next().children('.upload_svg_success').css("display", "inline");
        var i = 1;
        clone.find("input").each(function () {
            $(this).val('').attr('id', function (_, id) {
                return id + i
            });
        });
        clone.find("label").each(function () {
            $(this).val('').attr('for', function (_, e) {
                return e + i
            });
        });
        i++;
        if (spanText === 'Upload') {
            clone.css("border-top", "1px solid #ddd")
            clone.insertAfter('.upload_form:last');
        }

    });


    $('.upload_form').submit(function (event) {
        event.preventDefault();
        var dialog = $("#dialog-confirm")
        var data = new FormData($(this).get(0));
        var fileName = data.get('file').name;
        $.ajax({
            headers: {"X-CSRFToken": csrftoken},
            url: $(this).attr('action'),
            type: $(this).attr('method'),
            data: data,
            context: this,
            cache: false,
            processData: false,
            contentType: false,
            success: function (response) {
                var len = response.len;
                var filePath = response.file_path;
                var size = response.size;
                var date = response.date;
                var file = response.file_name;
                dialog.text(len + " points will be deducted from your account. Continue?");
                dialog.data({
                    'len': len,
                    'this': this,
                    "file": file,
                    "size": size,
                    "date": date,
                    "file_path": filePath,
                    "fileName": fileName
                }).dialog({buttons: successButtonFile});
                dialog.dialog("open");
            },
            error: function (response) {
                if (response.status === 403) {
                    dialog.text("You don’t have enough points in your account. Top it up?");
                    dialog.dialog({buttons: replenishButton});
                    dialog.dialog('open');
                } else {
                    dialog.text("Oops, something wrong with your file.Please reload.");
                    dialog.dialog({buttons: errorButton});
                    dialog.dialog('open');
                }


            },
        });
    })

    var fileConvert = function (_this, file, fileName, filePath, size, date, len) {
        var convertBut = $(_this).children('.submit_file_form__div').find('.submit_file_form');
        var convertAnim = $(_this).children('.submit_file_form__div').find('.bb');
        console.log(_this)
        convertBut.hide();
        convertAnim.show();
        var data = new FormData();
        data.append('file_path', filePath);
        data.append('file', file);
        data.append('size', size);
        data.append('date', date);
        data.append('len', len);
        $.ajax({
            headers: {"X-CSRFToken": csrftoken},
            url: 'convert_file',
            type: 'POST',
            data: data,
            context: this,
            cache: false,
            processData: false,
            contentType: false,
            success: function (response, status, xhr) {
                convertAnim.hide();
                console.log(response)
                console.log(xhr)
                $(_this).find('.upload-file__label').hide();
                $(_this).find('.upload-file__label').hide();
                $(_this).find('.get_file_name').text(fileName);
                var convertId = response.id;
                var urlDownload = 'ajax_open_file?id=' + convertId + "&type=d";
                var aDownload = $(_this).find('.response_download_link')
                aDownload.attr({
                    href: urlDownload,
                    target: '_blank',
                });
                aDownload.css("display", "inline-flex")

                var urlOpen = 'ajax_open_file?id=' + convertId + "&type=o";
                var aOpen = $(_this).find('.response_open_link')
                aOpen.attr({
                    href: urlOpen,
                    target: '_blank',
                });
                aOpen.show()
                console.log(urlOpen, urlDownload)

            },
            error: function () {
                convertAnim.hide();
                convertBut.show()
            }
        });
    }


    $('.options_button_copy').on('click', function copy_data(element) {
        const copy = $('.js-copytextarea').select();

        try {
            const successful = document.execCommand('copy');
            const msg = successful ? 'successful' : 'unsuccessful';
            console.log('Copying text command was ' + msg);
        } catch (err) {
            console.log('Oops, unable to copy');

        }
    });


    $('textarea').each(function () {
    }).on('input',
        function () {
            this.style.height = '420px';
            this.style.height = (this.scrollHeight) + 'px';
        });
})
