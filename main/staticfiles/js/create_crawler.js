function enableCreateButton() {
    var blocks = document.getElementsByClassName('valid-icon');
    var isValid = true;
    for (var i = 0; i < blocks.length; i++) {
        if (blocks[i].classList.contains('fa-warning')) {
            isValid = false;
            break;
        }
    }

    var button = document.getElementById('createButton');
    if (button.classList.contains('list-group-item-valid') && !isValid) {
        button.classList.remove('list-group-item-valid');
        button.classList.add('list-group-item-invalid');
    } else if (isValid) {
        button.classList.remove('list-group-item-invalid');
        button.classList.add('list-group-item-valid');
    }
}

function submit() {
    document.getElementById("myForm").submit();
}

function defineIcon(section, isValid) {
    var sectionId = '#' + section + '-valid-icon';
    if (isValid) {
        $(sectionId).removeClass('fa-warning').addClass('fa-check');
    } else {
        $(sectionId).removeClass('fa-check').addClass('fa-warning');
    }
    enableCreateButton();
}

function validateIntegerInput(input_id, can_be_empty = true, can_be_negative = false) {
    if (can_be_empty && can_be_negative) return true;

    var input = document.getElementById(input_id);
    var empty = !Boolean(input.value.trim())

    if (empty) return can_be_empty;

    var value = parseInt(input.value);
    return (value > 0 || can_be_negative);
}

function validateTextInput(input_id) {
    return document.getElementById(input_id).value.length > 0;
}

function getCheckboxState(checkbox_id) {
    return document.getElementById(checkbox_id).checked;
}

function getSelectedOptionText(select_id) {
    var select = document.getElementById(select_id);
    return select.options[select.selectedIndex].text;
}

function getSelectedOptionValue(select_id){
    var select = document.getElementById(select_id);
    return select.options[select.selectedIndex].value;
}

function setHiddenState(element_id, hidden) {
    document.getElementById(element_id).hidden = hidden;
}

function checkBasicInfo() {
    var valid =
      validateTextInput("id_source_name") &&
      validateTextInput("id_base_url") &&
      validateTextInput("id_data_path");
    defineIcon("basic-info", valid);
}

function checkAntiblock() {
    var valid = true;
    valid = (
        valid &&
        validateIntegerInput('id_antiblock_download_delay', can_be_empty = false, can_be_negative = false)
    );

    if (getCheckboxState('id_antiblock_autothrottle_enabled')) {
        valid = (
            valid &&
            validateIntegerInput('id_antiblock_autothrottle_start_delay', can_be_empty = false, can_be_negative = false) &&
            validateIntegerInput('id_antiblock_autothrottle_max_delay', can_be_empty = false, can_be_negative = false)
        );
    }

    var selected_option = getSelectedOptionValue("id_antiblock_mask_type");
    console.log("id_antiblock_mask_type", selected_option);
    if (selected_option == 'ip') {
        valid = (
            valid &&
            validateIntegerInput('id_antiblock_max_reqs_per_ip', can_be_empty = false, can_be_negative = false) &&
            validateIntegerInput('id_antiblock_max_reuse_rounds', can_be_empty = false, can_be_negative = false)
        );

        var selected_proxy = getSelectedOptionText("id_antiblock_mask_type");
        if (selected_proxy == "proxy")
            valid = validateTextInput('id_proxy_list');
    }
    else if (selected_option == 'user_agent') {
        valid = (
            validateIntegerInput('id_antiblock_reqs_per_user_agent', can_be_empty = false, can_be_negative = false) &&
            validateIntegerInput('id_antiblock_user_agents_file', can_be_empty = false, can_be_negative = false)
        );
    }
    else if (selected_option == 'cookies') {
        valid = validateTextInput('id_antiblock_cookies_file');
    }

    defineIcon("antiblock", valid);
}

function checkCaptcha() {
    var valid = true;

    if (getCheckboxState("id_has_webdriver"))
        valid = valid && validateTextInput("id_webdriver_path");

    var selected_option = getSelectedOptionValue("id_captcha");

    if (selected_option == 'image')
        valid = validateTextInput('id_img_xpath');
    else if (selected_option == 'sound')
        valid = validateTextInput('id_sound_xpath');

    defineIcon("captcha", valid);
}

function checkCrawlerType() {
}

function checkTemplatedURL() {
    var valid = true;

    // Validate all entries with the HTML specified rules

    // Parameter configurations
    $('.templated-url-param-step:not(.subform-deleted) input')
        .each((index, entry) => {
        valid = valid && entry.checkValidity();
    });

    // Response validation configurations
    $('.templated-url-resp-step:not(.subform-deleted) input')
        .each((index, entry) => {
        valid = valid && entry.checkValidity();
    });

    // Validate ordering constraints between fields
    $('.templated-url-param-step:not(.subform-deleted)')
        .each((index, entry) => {
        entry = $(entry);

        let param_type = entry.find('select[name$="parameter_type"]').val();

        let error_msg = ""
        if (param_type == 'process_code') {
            let first_year = entry.find('input[name$="first_year_proc_param"]');
            let last_year = entry.find('input[name$="last_year_proc_param"]');

            let first_value = parseInt(first_year.val());
            let last_value = parseInt(last_year.val());

            if (first_year.val() != "" && last_year.val() != "" &&
                first_value > last_value) {
                valid = false;
                error_msg = 'O primeiro ano deve ser menor que o último.'
            }
            first_year[0].setCustomValidity(error_msg);
            last_year[0].setCustomValidity(error_msg);
        } else if (param_type == 'number_seq'){
            let first_num = entry.find('input[name$="first_num_param"]');
            let last_num = entry.find('input[name$="last_num_param"]');

            let first_value = parseInt(first_num.val());
            let last_value = parseInt(last_num.val());

            if (first_num.val() != "" && last_num.val() != "" &&
                first_value > last_value) {
                valid = false;
                error_msg = 'O primeiro número deve ser menor que o último.'
            }
            first_num[0].setCustomValidity(error_msg);
            last_num[0].setCustomValidity(error_msg);
        } else if (param_type == 'date_seq'){
            let first_date = entry.find('input[name$="start_date_date_param"]');
            let last_date = entry.find('input[name$="end_date_date_param"]');

            let first_value = new Date(first_date.val());
            let last_value = new Date(last_date.val());

            if (first_date.val() != "" && last_date.val() != "" &&
                first_value > last_value) {
                valid = false;
                error_msg = 'A primeira data deve ser menor que a última.'
            }
            first_date[0].setCustomValidity(error_msg);
            last_date[0].setCustomValidity(error_msg);
        }
    });

    defineIcon("templated-url", valid);
}

function checkRelatedFields() {
    var input_name = $(this).attr('name');

    if (input_name.length >= 11 && input_name.substring(0, 10) == "antiblock_") {
        checkAntiblock();
    }

    if (input_name.length >= 13 && input_name.substring(0, 13) == "templated-url") {
        checkTemplatedURL();
    }

    // TODO: make all variables from same section have the same prefix and check like antiblock
    switch (input_name) {
        case 'source_name':
        case 'base_url':
        case 'data_path':
            checkBasicInfo();
            break;
        case 'has_webdriver':
        case 'webdriver_path':
        case 'img_xpath':
        case 'sound_xpath':
            checkCaptcha();
            break;
        case 'crawler_type':
        case 'explore_links':
        case 'link_extractor_max_depth':
        case 'link_extractor_allow':
        case 'link_extractor_allow_extensions':
            checkCrawlerType();
            break;
    }
}

$(document).ready(function () {
    setNavigation();

    $('input').on('blur keyup', checkRelatedFields);
});

function showBlock(clicked_id) {

    var blocks = document.getElementsByClassName('block');
    for (var i = 0; i < blocks.length; i++)
        blocks[i].setAttribute('hidden', true);

    var blockId = clicked_id + "-block";
    var block = document.getElementById(blockId);
    block.removeAttribute('hidden');


    var buttons = document.getElementsByClassName('button-block');
    for (var i = 0; i < buttons.length; i++)
        buttons[i].classList.remove('active');
    document.getElementById(clicked_id).classList.add('active');
}

function detailBaseUrl() {
    const base_url = $("#id_base_url").val();

    // Check if a Templated URL is being used (if there is at least one
    // occurrence of the substring "{}")
    if (base_url.includes("{}")){
        $("#templated-url-item").removeClass("disabled");
        // count number of placeholders
        let num_placeholders = (base_url.match(/\{\}/g) || []).length;
        $('#templated-url-param').formset('setNumForms', num_placeholders);
    } else {
        $("#templated-url-item").addClass("disabled");

        // remove all parameter and response forms
        $('#templated-url-param').formset('setNumForms', 0);
        $('#templated-url-response').formset('setNumForms', 0);
    }

    // Update information for selected parameters/response handlers
    $('#templated-url-param .templated-url-param-step > .form-group select').each(
        (index, entry) => detailTemplatedUrlParamType({ 'target': entry})
    );

    $('#templated-url-response .templated-url-resp-step > .form-group select').each(
        (index, entry) => detailTemplatedUrlResponseType({ 'target': entry})
    );

    // Update range-filtering sub-parameters
    $('.templated-url-filter-config > .form-group input').each(
        (index, entry) => detailTemplatedURLParamFilter({'target': entry})
    );

    checkTemplatedURL();
}


function detailWebdriverType() {
    setHiddenState("webdriver_path_div", !getCheckboxState("id_has_webdriver"));
}

function detailCaptcha() {
    var mainSelect = document.getElementById("id_captcha");
    const captcha_type = mainSelect.options[mainSelect.selectedIndex].value;

    setHiddenState('webdriver', captcha_type == 'none' ? true : false);

    var contents = document.getElementsByClassName("captcha-content-div");
    for (const i in contents)
        contents[i].hidden = true;
    setHiddenState(captcha_type, false);

    checkCaptcha();
}

function hideUnselectedSiblings(input, parentPath, siblingPath) {
    const parentDiv = $(input).closest(parentPath);
    const selectedVal = input.options[input.selectedIndex].value;

    parentDiv.find(siblingPath).each(function() {
        this.hidden = true;
    });

    if (selectedVal != "") {
        parentDiv.find("[data-option-type=" + selectedVal + "]")
                 .attr('hidden', false);
    }

    // Remove 'required' constraint from all inputs for this parameter
    $(input).closest(parentPath)
            .find(siblingPath + ' input:not([type="checkbox"])')
            .removeAttr('required');

    const paramType = input.options[input.selectedIndex].value

    if (paramType != "") {
        // Add 'required' constraint to inputs for this parameter type
        $(input).closest(parentPath)
                .find(siblingPath + '[data-option-type=' + paramType + '] ' +
                                    'input:not([type="checkbox"])')
                .attr('required', '');
    }
}

function detailTemplatedUrlResponseType(e) {
    hideUnselectedSiblings(e.target, '.templated-url-resp-step:not(.subform-deleted)',
        '.templated-url-response-params');

}

function detailTemplatedUrlParamType(e) {
    const input = e.target;
    hideUnselectedSiblings(e.target, '.templated-url-param-step:not(.subform-deleted)',
        '.templated-url-param-config');

    const filterDiv = $(input).closest('.templated-url-param-step')
                              .find('.templated-url-filter-config')[0];

    switch (input.options[input.selectedIndex].value) {
        case 'process_code':
        case 'number_seq':
        case 'date_seq':
            // Display filtering options
            filterDiv.hidden = false
            break;
        default:
            // Hide filtering options
            filterDiv.hidden = true
    }

    // Update cons_misses parameter
    const filterCheckbox = $(filterDiv).find('> .form-group input')[0]
    detailTemplatedURLParamFilter({ 'target':  filterCheckbox })

}

function detailTemplatedURLParamFilter(e) {
    const input = e.target;
    const consMissesInput = $(input).closest(".templated-url-param-step")
         .find('.templated-url-cons-misses')[0]
    consMissesInput.hidden = !input.checked
    $(consMissesInput).find('input').prop('required', input.checked)
}

function detailIpRotationType() {
    var ipSelect = document.getElementById("id_ip_type");

    const ip_rotation_type = ipSelect.options[ipSelect.selectedIndex].value;

    setHiddenState("tor_div", true);
    setHiddenState("proxy_div", true);

    var id = ip_rotation_type + "_div";
    setHiddenState(id, false);
}

function detailAntiblock() {
    var mainSelect = document.getElementById("id_antiblock_mask_type");
    const antiblock_type = mainSelect.options[mainSelect.selectedIndex].value;

    var contents = document.getElementsByClassName("antiblock-mask-div");
    for (const i in contents)
        contents[i].hidden = true;
    setHiddenState(antiblock_type, false);

    checkAntiblock();
}

function detailCrawlerType() {
    var mainSelect = document.getElementById("id_crawler_type");
    const crawler_type = mainSelect.options[mainSelect.selectedIndex].value;

    var contents = document.getElementsByClassName("crawler-type-content-div");
    for (const i in contents)
        contents[i].hidden = true;
    setHiddenState(crawler_type, false);
    

    if(crawler_type == "form_page"){
        interface_root_element = document.getElementById("form_page");
        if(interface_root_element.type != "root" ){
            
            steps_output_element = interface_root_element.children[0].children[1].children[0]
            load_steps(interface_root_element, steps_output_element);
        }
    }

    checkCrawlerType();
}

function autothrottleEnabled() {
    setHiddenState("autothrottle-options-div", !getCheckboxState("id_antiblock_autothrottle_enabled"));
}


// TODO add new fields to validation
