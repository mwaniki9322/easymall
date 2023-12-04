// some scripts
function showFormErrors(form, errors) {
    for (let key in errors) {
        if (errors.hasOwnProperty(key)) {
            let errorEl = $(form).find(`[data-label=${key}]`);
            errorEl.css('display', 'block');
            for (let i = 0; i < errors[key].length ; i++) {
                let errorsLi = document.createElement('li');
                errorsLi.innerText = errors[key][i];
                errorEl.append(errorsLi);
            }
        }
    }
}

function hideFormErrors(form) {
    let formErrors = form.querySelectorAll('.form-errors');
    for (let i = 0; i < formErrors.length; i++) {
        $(formErrors[i]).css('display', 'none');
        $(formErrors[i]).html('');
    }
}

// jquery ready start
$(document).ready(function() {
	// jQuery code


    /* ///////////////////////////////////////

    THESE FOLLOWING SCRIPTS ONLY FOR BASIC USAGE,
    For sliders, interactions and other

    */ ///////////////////////////////////////


	//////////////////////// Prevent closing from click inside dropdown
    $(document).on('click', '.dropdown-menu', function (e) {
      e.stopPropagation();
    });


    $('.js-check :radio').change(function () {
        var check_attr_name = $(this).attr('name');
        if ($(this).is(':checked')) {
            $('input[name='+ check_attr_name +']').closest('.js-check').removeClass('active');
            $(this).closest('.js-check').addClass('active');
           // item.find('.radio').find('span').text('Add');

        } else {
            item.removeClass('active');
            // item.find('.radio').find('span').text('Unselect');
        }
    });


    $('.js-check :checkbox').change(function () {
        var check_attr_name = $(this).attr('name');
        if ($(this).is(':checked')) {
            $(this).closest('.js-check').addClass('active');
           // item.find('.radio').find('span').text('Add');
        } else {
            $(this).closest('.js-check').removeClass('active');
            // item.find('.radio').find('span').text('Unselect');
        }
    });



	//////////////////////// Bootstrap tooltip
	if($('[data-toggle="tooltip"]').length>0) {  // check if element exists
		$('[data-toggle="tooltip"]').tooltip()
	} // end if



    // Toastr
    toastr.options.closeButton = true;

    // Forms
    function reloadSubmitCallback(form, data, success) {
        if (success) {
            location.reload();
        }
    }

    function closeModalSubmitCallback(form, data, success) {
        if (success) {
            $(`#${data['modal']}`).modal('hide');
            form.reset();
        }
    }

    function formResetSubmitCallback(form, data, success) {
        if (success) {
            form.reset();
        }
    }

    let formSubmitCallbacks = {
        'form_reset': formResetSubmitCallback,
        'close_modal': closeModalSubmitCallback,
        'reload': reloadSubmitCallback,
    }
    $('form.custom-submit').on('submit', function (event) {
        event.preventDefault();
        let form = this;
        let data = new FormData(form);

        hideFormErrors(form);

        let btn = $(form).find('.submit-btn');
        let working = btn.attr('data-working');
        let btnText = btn.text();
        btn.prop('disabled', true);

        if (working) {
            btn.text(working);
        }

        $.ajax({
            type: $(form).attr('method'),
            url: $(form).attr('action'),
            data: data,
            cache:false,
            contentType: false,
            processData: false,
            success:function(data){
                if (working) {
                    btn.text(btnText);
                }
                btn.prop('disabled', false);

                if (data.hasOwnProperty('next_url')) {
                    location.href = data['next_url']
                }
                if (data.hasOwnProperty('message')) {
                    toastr.success(data['message'], 'Success!');
                }
                if (data.hasOwnProperty('callback')) {
                    formSubmitCallbacks[data['callback']](form, data, true);
                }
            },
            error: function(data){
                if (working) {
                    btn.text(btnText);
                }
                btn.prop('disabled', false);
                data = data.responseJSON;
                if (data) {
                    if (data.hasOwnProperty('next_url')) {
                        location.href = data['next_url']
                    }
                    if (data.hasOwnProperty('errors')) {
                        showFormErrors(form, data['errors'])
                    }
                    if (data.hasOwnProperty('message')) {
                        toastr.error(data['message'], 'Error!');
                    }
                    if (data.hasOwnProperty('callback')) {
                        formSubmitCallbacks[data['callback']](form, data, false);
                    }
                } else {
                    toastr.error('An error has occurred. Please try again.', 'Error!');
                }
            }
        })
    })

    // To local datetime
    function toLocalDateTime() {
        $('.to_local_datetime').each(function(i, obj) {
            let utc_datetime = moment.utc($(this).data('utc'));
            let local_datetime = moment(utc_datetime).local();
            local_datetime = local_datetime.format("MMM. DD, YYYY, hh:mm a");
            $(this).text(local_datetime);
        });
    }
    toLocalDateTime()

});
// jquery end

setTimeout(function(){
  $('#message').fadeOut('slow')
}, 4000)
