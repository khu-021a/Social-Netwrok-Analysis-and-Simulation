$(document).ajaxSend(function() {
    $('#loading-dialog').modal('show');
});

$(document).ajaxComplete(function() {
    $('#loading-dialog').on('shown.bs.modal', function(e) {
        $('#loading-dialog').modal('hide');
    });
});


$('#cl-dialog').on('shown.bs.modal', function() {
    Highcharts.chart('num-chart', {
        title: {
            text: 'Active Node in Each Step'
        },
        xAxis: {
            title: {
                text: 'Steps'
            }
        },
        yAxis: {
            title: {
                text: 'Quantities'
            }
        },
        series: [chartData['num']]
    });

    Highcharts.chart('ratio-chart', {
        chart: {
            type: 'column'
        },
        title: {
            text: 'Accumulated Active Node Ratio in Each Step'
        },
        xAxis: {
            title: {
                text: 'Steps'
            }
        },
        yAxis: {
            title: {
                text: 'Percentages'
            }
        },
        series: [chartData['ratio']]
    });
});

$('#dc-option, #bc-option, #cc-option, #ec-option').on('click', function(event) {
    if ($('#centrality-stats').hasClass('hide')) {
        $('#centrality-stats').removeClass('hide');
    }
    if (centralityType !== null) {
        $('#ul-graph g.nodes circle.' + centralityType + '-' + 1).removeClass(centralityType + '-color-' + 1);
        $('#ul-graph g.nodes circle.' + centralityType + '-' + 2).removeClass(centralityType + '-color-' + 2);
        $('#ul-graph g.nodes circle.' + centralityType + '-' + 3).removeClass(centralityType + '-color-' + 3);
        $('#ul-graph g.nodes circle.' + centralityType + '-' + 4).removeClass(centralityType + '-color-' + 4);
        $('#' + centralityType + '-stats').addClass('hide');
    }
    centralityType = $(event.target).data('type');
    $('#' + centralityType + '-stats').removeClass('hide');
    $('#ul-graph g.nodes circle.' + centralityType + '-' + 1).addClass(centralityType + '-color-' + 1);
    $('#ul-graph g.nodes circle.' + centralityType + '-' + 2).addClass(centralityType + '-color-' + 2);
    $('#ul-graph g.nodes circle.' + centralityType + '-' + 3).addClass(centralityType + '-color-' + 3);
    $('#ul-graph g.nodes circle.' + centralityType + '-' + 4).addClass(centralityType + '-color-' + 4);
});

$('[name="model"]').on('click', function(event) {
    var checkedClass = $('[name="model"]:checked').attr('class');
    var uncheckedClass = $('[name="model"]:not(:checked)').attr('class');
    $('.' + checkedClass + '[name!="model"]').attr('disabled', false);
    $('.' + uncheckedClass + '[name!="model"]').attr('disabled', true);
});

$('[name="termination"]').on('click', function() {
    var checkedClass = $('[name="termination"]:checked').attr('class');
    var uncheckedClass = $('[name="termination"]:not(:checked)').attr('class');
    $('.' + checkedClass + '[name!="termination"]').attr('disabled', false);
    $('.' + uncheckedClass + '[name!="termination"]').attr('disabled', true);
});

$('[name="spatial-weights"]').on('click', function() {
    var checkedClass = $('input[name="spatial-weights"]:checked').attr('class');
    var uncheckedClass = $('input[name="spatial-weights"]:not(:checked)').attr('class');
    $('.' + checkedClass + '[name!="spatial-weights"]').attr('disabled', false);
    $('.' + uncheckedClass + '[name!="spatial-weights"]').attr('disabled', true);
});

$('.with-form').on('click', function(event) {
    var anchor = $(event.target).data('ref');
    $(anchor).siblings(':not([class~="hide"])').addClass('hide');
    if ($(anchor).hasClass('hide')) {
        $(anchor).removeClass('hide');
    }
});

$('.ulr-model').on('click', function(event) {
    if (!$('.ulr-options').hasClass('hide')) {
        $('.ulr-options').addClass('hide');
    }
    var anchor = $(event.target).data('ref');
    var modelType = $(event.target).val();
    if (modelType === 'ltm') {
        $('#ulr-config').prop('disabled', false);
    } else {
        $('#ulr-config').prop('disabled', true);
    }
    if ($(anchor).hasClass('hide')) {
        $(anchor).removeClass('hide');
    }
});

$('.ulr-icm-arg').on('click', function(event) {
    var argsLimit = 2;
    var checkedNum = $('.ulr-icm-arg:checked').length;
    if (checkedNum < argsLimit) {
        $('.ulr-icm-arg:disabled').prop('disabled', false);
        $('#ulr-config').prop('disabled', true);
    } else {
        $('.ulr-icm-arg:not(:checked)').prop('disabled', true);
        $('#ulr-config').prop('disabled', false);
    }
});

$('#ulr-config').on('click', function(event) {
    var formID = $(event.target).data('ref');
    $(formID).siblings(':not([class~="hide"])').addClass('hide');
    if ($(formID).hasClass('hide')) {
        $(formID).removeClass('hide');
    }
    if (!$('#network-analyst').hasClass('disabled')) {
        $('#network-analyst').addClass('disabled');
    }
    if (!$('#export-option').hasClass('disabled')) {
        $('#export-option').addClass('disabled');
    }
    if (!$('#ul-vis').hasClass('hide')) {
        $('#ul-vis').addClass('hide');
    }
    if ($('#ulr-vis').hasClass('hide')) {
        $('#ulr-vis').removeClass('hide');
    }
    if (!$('#cl-vis').hasClass('hide')) {
        $('#cl-vis').addClass('hide');
    }
    var modelAnchor = $('[name="models"]:checked').data('form');
    var modelType = $('[name="models"]:checked').val();
    $(modelAnchor).parent().siblings().children(':not([class~="hide"])').addClass('hide');
    if ($(modelAnchor).hasClass('hide')) {
        $(modelAnchor).removeClass('hide');
    }
    if (modelType === 'icm') {
        var argRefs = $('.ulr-icm-arg').toArray().map(function(id) {
            return $(id).data('ref');
        });
        var argsChecked = $('.ulr-icm-arg').toArray().map(function(id) {
            return $(id).prop('checked');
        });
        ulrICMStates = argRefs.map(function(e, i) {
            return [e, argsChecked[i]];
        });
        ulrICMStates.forEach(function(el) {
            var currentID = el[0];
            var currentState = el[1];
            if ($(currentID).hasClass('hide')) {
                $(currentID).removeClass('hide');
            }
            var defaultForm = $(currentID).find('.ulr-default');
            var rangedForm = $(currentID).find('.ulr-ranged');
            if (currentState) {
                if (!defaultForm.hasClass('hide')) {
                    defaultForm.addClass('hide');
                }
                if (rangedForm.hasClass('hide')) {
                    rangedForm.removeClass('hide');
                }
            } else {
                if (defaultForm.hasClass('hide')) {
                    defaultForm.removeClass('hide');
                }
                if (!rangedForm.hasClass('hide')) {
                    rangedForm.addClass('hide');
                }
            }
        });
    }
});

$('#clear-weights').on('click', function(event) {
    $('.urgency-values').empty();
    if (!$('#param-table').hasClass('hide')) {
        $('#param-table').addClass('hide');
    }
});

$('#slot-weights').on('click', function(event) {
    $('.urgency-values').empty();
    var checkedOption = $('input[name="termination"]:checked').val();
    var children = null;
    if (checkedOption === 'step') {
        children = generateRows(parseInt($('#step-num').val()), null);
    } else {
        children = generateRows(1, null);
    }
    $('.urgency-values').append(children);
    if ($('#param-table').hasClass('hide')) {
        $('#param-table').removeClass('hide');
    }
});

$('#set-weights').on('click', function(event) {
    $('.urgency-values').empty();
    var checkedOption = $('input[name="termination"]:checked').val();
    var urgencyVal = $('#fixed-weight').val();
    var children = null;
    if (checkedOption === 'step') {
        children = generateRows(parseInt($('#step-num').val()), urgencyVal);
    } else {
        children = generateRows(1, urgencyVal);
    }
    $('.urgency-values').append(children);
    if ($('#param-table').hasClass('hide')) {
        $('#param-table').removeClass('hide');
    }
});

$('#sw-option, #pa-option, #rnd-option, #user-level').on('click', function(event) {
    if ($('#network-analyst').hasClass('disabled')) {
        $('#network-analyst').removeClass('disabled');
    }
    if ($('#ul-vis').hasClass('hide')) {
        $('#ul-vis').removeClass('hide');
    }
    if (!$('#ulr-vis').hasClass('hide')) {
        $('#ulr-vis').addClass('hide');
    }
    if (!$('#cl-vis').hasClass('hide')) {
        $('#cl-vis').addClass('hide');
    }
});

$('#city-level').on('click', function(event) {
    if (!$('#network-analyst').hasClass('disabled')) {
        $('#network-analyst').addClass('disabled');
    }
    if (!$('#export-option').hasClass('disabled')) {
        $('#export-option').addClass('disabled');
    }
    if (!$('#ul-vis').hasClass('hide')) {
        $('#ul-vis').addClass('hide');
    }
    if (!$('#ulr-vis').hasClass('hide')) {
        $('#ulr-vis').addClass('hide');
    }
    if ($('#cl-vis').hasClass('hide')) {
        $('#cl-vis').removeClass('hide');
    }
});      

$('#small-world').on('click', swHandler);

$('#pref-attach').on('click', paHandler);

$('#random').on('click', rndHandler);

$('#community').on('click', commHandler);

$('#get-seeds').on('click', seedHandler);

$('#get-opinion-leaders').on('click', opldHandler);

$('#diffuse-ul').on('click', ulHandler);

$('#map-layers').on('change', function(event) {
    fileSet['map-layers'] = event.target.files;
});

$('#weight-matrix').on('change', function(event) {
    fileSet['weights'] = event.target.files;
});  

$('#net-file').on('change', function(event) {
    fileSet['network'] = event.target.files;
});  

$('#upload-layers').on('click', basemapHandler);

$('#upload-net').on('click', netFileHandler);

$('#upload-weight').on('click', weightFileHandler);

$('#diffuse-cl').on('click', clHandler);

$('#ulr-ltm-run').on('click', ulrLTMHandler);

$('#ulr-icm-run').on('click', ulrICMHandler);