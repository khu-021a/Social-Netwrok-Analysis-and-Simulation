var netData = null;
var centralityType = null;
var centralityColors = {
    'bc': ['#F7F4FE', '#B8A0F7', '#8D65F4', '#652FF3'],
    'cc': ['#D9F8F6', '#8ADDD7', '#4FBDB5', '#189B91'],
    'dc': ['#FFF4F3', '#FFA49A', '#FF6858', '#FF2F19'],
    'ec': ['#FFFBF3', '#FFDF9A', '#FFC958', '#FFB519']
};
var centralityTitles = {
    'bc': 'Betweenness Centrality Distributions',
    'cc': 'Closeness Centrality Distributions',
    'dc': 'Degree Centrality Distributions',
    'ec': 'Eigenvector Centrality Distributions'
};
var fileSet = {};
var layers = [];
var baseFlag = false;
var netFlag = false;
var chartData = {};
var ulrICMStates = null;

var valExists = function(v) {
    return (v !== undefined && v !== null);
};

var generateRows = function(n, initVal) {
    if (n <= 0) {
        return null;
    } else {
        var sequence = Array.apply(null, {length: n}).map(function(value, index){
        return index + 1;
    });
        if (!valExists(initVal)) {
            return sequence.map(function(n) {
                return '<tr><th scope="row">' + n + '</th><td><input type="text" class="urgency table-input" placeholder="Temporal Weight" required></td></tr>';
            }).join('');
        } else {
            return sequence.map(function(n) {
                return '<tr><th scope="row">' + n + '</th><td><input type="text" class="urgency table-input" value="' + initVal + '" placeholder="Temporal Weight" required></td></tr>';
            }).join('');
        }
    }
};

var drawCentralityChart = function(cType) {
    var anchor = cType + '-stats';
    var dataset = netData[cType];
    var colors = centralityColors[cType];
    var title = centralityTitles[cType];
    dataset = dataset.map(function(obj) {
        obj.name = '';
        obj.y = obj.ratio;
        return obj;
    });
    $('#' + anchor).empty();
    Highcharts.chart(anchor, {
        chart: {
            plotBackgroundColor: null,
            plotBorderWidth: null,
            plotShadow: false,
            type: 'pie'
        },
        title: {
            text: title
        },
        tooltip: {
            pointFormat: 'Range: {point.lower:.3f} - {point.upper:.3f}<br>Number: {point.number}<br>Ratio: {point.ratio}'
        },
        plotOptions: {
            pie: {
                allowPointSelect: true,
                cursor: 'pointer',
                colors: colors,
                dataLabels: {
                    enabled: false
                }
            }
        },
        series: [{ data: dataset }]
    });
};

var drawGraphUl = function() {
    var net = netData['net'];
    $('#ul-graph').empty();
    forceGraph({
        anchor: '#ul-graph',
        nodeRadius: 5,
        emphasisFillKey: 'seed',
        emphasisStrokeKey: 'leader'
    })(net['nodes'], net['edges']);
    if ($('#export-network').hasClass('disabled')) {
        $('#export-network').removeClass('disabled');
    }
    if ($('#export-analysis').hasClass('disabled')) {
        $('#export-analysis').removeClass('disabled');
    }
};

var setStatusGen = function() {
    if ($('#export-network').hasClass('disabled')) {
        $('#export-network').removeClass('disabled');
    }
    if ($('#export-analysis').hasClass('disabled')) {
        $('#export-analysis').removeClass('disabled');
    }
    if (!$('#centrality-stats').hasClass('hide')) {
        $('#centrality-stats').addClass('hide');
    }
};

var swHandler = function(event) {
    var nodes = parseInt($('#sw-node-num').val());
    var outDegree = parseInt($('#sw-out-degree').val());
    var rewirePb = parseFloat($('#sw-rewire-prob').val());

    if (nodes !== NaN && outDegree !== NaN && rewirePb !== NaN) {
        $.ajax({
            url: '/generator/small-world',
            type:'PUT',
            data: { 
                'nodes': nodes, 
                'out-degree': outDegree, 
                'rewire-pb': rewirePb 
            }
        }).done(function(data, status, xhr) {
            netData = JSON.parse(data);
            setStatusGen();
            drawGraphUl();
            drawCentralityChart('bc');
            drawCentralityChart('cc');
            drawCentralityChart('dc');
            drawCentralityChart('ec');
        }).fail(function(xhr, status, error) {
            console.error(status);
            console.error(error);
        });
    }
};

var paHandler = function(event) {
    var nodes = parseInt($('#pa-node-num').val());
    var outDegree = parseInt($('#pa-out-degree').val());

    if (nodes !== NaN && outDegree !== NaN) {
        $.ajax({
            url: '/generator/pref-attach',
            type:'PUT',
            data: { 
                'nodes': nodes, 
                'out-degree': outDegree 
            }
        }).done(function(data, status, xhr) {
            netData = JSON.parse(data);
            setStatusGen();
            drawGraphUl();
            drawCentralityChart('bc');
            drawCentralityChart('cc');
            drawCentralityChart('dc');
            drawCentralityChart('ec');
        }).fail(function(xhr, status, error) {
            console.error(status);
            console.error(error);
        });
    }
};

var rndHandler = function(event) {
    var nodes = parseInt($('#rnd-node-num').val());
    var edges = parseInt($('#rnd-edge-num').val());

    if (nodes !== NaN && edges !== NaN) {
        $.ajax({
            url: '/generator/random',
            type:'PUT',
            data: {
                'nodes': nodes,
                'edges': edges
            }
        }).done(function(data, status, xhr) {
            netData = JSON.parse(data);
            setStatusGen();
            drawGraphUl();
            drawCentralityChart('bc');
            drawCentralityChart('cc');
            drawCentralityChart('dc');
            drawCentralityChart('ec');
        }).fail(function(xhr, status, error) {
            console.error(status);
            console.error(error);
        });
    }
};

var seedHandler = function(event) {
    if (!$('#export-ul').hasClass('disabled')) {
        $('#export-ul').addClass('disabled');
    }
    var seeds = parseInt($('#seed-num').val());
    var indicator = $('#seed-indicator').val();

    $.ajax({
        url: '/seeds',
        type:'GET',
        cache: false,
        data: {
            'seeds': seeds, 
            'indicator': indicator
        }
    }).done(function(data, status, xhr) {
        var net = JSON.parse(data);
        $('#ul-graph').empty();
        forceGraph({
            anchor: '#ul-graph',
            nodeRadius: 5,
            emphasisFillKey: 'seed',
            emphasisStrokeKey: 'leader'
        })(net['nodes'], net['edges']);
    }).fail(function(xhr, status, error) {
        console.error(status);
        console.error(error);
    });
};

var opldHandler = function(event) {
    if (!$('#export-ul').hasClass('disabled')) {
        $('#export-ul').addClass('disabled');
    }
    var scale = $('[name="scale"]:checked').val()
    var ratio = parseFloat($('#proportion').val());

    $.ajax({
        url: '/opinion-leaders',
        type:'GET',
        cache: false,
        data: { 
            'scale': scale, 
            'ratio': ratio 
        }
    }).done(function(data, status, xhr) {
        var net = JSON.parse(data);
        $('#ul-graph').empty();
        forceGraph({
            anchor: '#ul-graph',
            nodeRadius: 5,
            emphasisFillKey: 'seed',
            emphasisStrokeKey: 'leader'
        })(net['nodes'], net['edges']);
    }).fail(function(xhr, status, error) {
        console.error(status);
        console.error(error);
    });
};

var ulHandler = function(event) {
    if (!$('#centrality-stats').hasClass('hide')) {
        $('#centrality-stats').addClass('hide');
    }

    var seeds = parseInt($('#seed-num').val()) || 1;
    var indicator = $('#seed-indicator').val();
    var model = $('[name="model"]:checked').val();

    var obj = {
        type: 'ul',
        seeds: seeds,
        indicator: indicator,
        model: model
    };

    if (model === 'ltm') {
        obj['threshold'] = parseFloat($('#ltm-threshold').val()) || 0.4;
    } else if (model === 'icm') {
        obj ['pb-leaders'] = parseFloat($('#pb-opinion-leaders').val()) || 0.2;
        obj ['pb-normal'] = parseFloat($('#pb-normal-people').val()) || 0.3;
        obj ['scale'] = $('[name="scale"]:checked').val();
        obj ['ratio'] = parseFloat($('#proportion').val()) || 0.0;
    }

    $.ajax({
        url: '/diffusion-ul',
        type:'GET',
        cache: false,
        data: obj,
    }).done(function(data, status, xhr) {
        if ($('#export-ul').hasClass('disabled')) {
            $('#export-ul').removeClass('disabled');
        }
        var net = JSON.parse(data);
        $('#ul-graph').empty();
        forceGraph({
            anchor: '#ul-graph',
            nodeRadius: 5,
            emphasisFillKey: 'seed',
            emphasisStrokeKey: 'leader'
        })(net['nodes'], net['edges']);
        var nodesToChange = net['nodes'].filter(function(node) {
            return node['diffused'] > 0;
        });
        nodesToChange.forEach(function(node) {
            (function(obj) {
                setTimeout(function() {
                    var objID = obj['id'];
                    var objEl = $('g.nodes g#' + objID + ' circle');
                    objEl.removeClass('node-normal');
                    objEl.addClass('node-seed');
                }, obj['diffused'] * 1000);
            })(node);
        });
    }).fail(function(xhr, status, error) {
        console.error(status);
        console.error(error);
    });
};

var basemapHandler = function (event) {
    if (!$('#results-cl').prop('disabled')) {
        $('#results-cl').prop('disabled', true);
    }
    var data = new FormData();
    $.each(fileSet['map-layers'], function(k, v) {
        data.append(k, v);
    });

    $.ajax({
        url: "/map-layers",
        type: "PUT",
        data: data,
        cache: false,
        processData: false,
        contentType: false
    }).done(function(data, status, xhr) {
        var obj = JSON.parse(data);
        if (baseFlag) {
            layers.pop();
            baseFlag = false;
        }
        layers.push(obj);
        baseFlag = true;
        
        $('#cl-graph').empty();
        createLayers('#cl-graph', layers, {
            width: 960,
            height: 600
        });
    }).fail(function(xhr, status, error) {
        console.error(status);
        console.error(error);
    });
};

var netFileHandler = function(event) {
    if (!$('#results-cl').prop('disabled')) {
        $('#results-cl').prop('disabled', true);
    }
    var data = new FormData();
    $.each(fileSet['network'], function(k, v) {
        data.append(k, v);
    });     

    $.ajax({
        url: "/net-file",
        type: "PUT",
        data: data,
        cache: false,
        processData: false,
        contentType: false
    }).done(function(data, status, xhr) {
        var obj = JSON.parse(data);
        var lineFeatures = obj['line'];
        var pointFeatures = obj['point'];
        if (netFlag) {
            layers.shift();
            layers.shift();
            netFlag = false;
        }
        layers.unshift(lineFeatures);
        layers.unshift(pointFeatures);
        netFlag = true;
        
        $('#cl-graph').empty();
        createLayers('#cl-graph', layers, {
            width: 960,
            height: 600
        });
    }).fail(function(xhr, status, error) {
        console.error(status);
        console.error(error);
    });
};

var weightFileHandler = function(event) {
    if (!$('#results-cl').prop('disabled')) {
        $('#results-cl').prop('disabled', true);
    }
    var data = new FormData();
    $.each(fileSet['weights'], function(k, v) {
        data.append(k, v);
    });     

    $.ajax({
        url: "/weight-file",
        type: "PUT",
        data: data,
        cache: false,
        processData: false,
        contentType: false
    }).done(function(data, status, xhr) {
        console.log(status);  
        console.log(data);
    }).fail(function(xhr, status, error) {
        console.error(status);
        console.error(error);
    });
};

var clHandler = function(event) {
    if (!$('#centrality-stats').hasClass('hide')) {
        $('#centrality-stats').addClass('hide');
    }

    var sources = $('#sources').val().split(',').map(function(el) {
        return parseInt(el.trim());
    });
    var terminationType = $('[name="termination"]:checked').val();
    var terminationParam = (terminationType === 'step') ? parseInt($('#step-num').val()) : (parseFloat($('#cover-ratio').val()) / 100);
    var urgencyVals = $('.urgency').map(function() {
        return parseFloat(this.value);
    }).get()
    var urgencyType = $('[name="spatial-weights"]:checked').val();
    var decayParams = null;
    if (urgencyType === 'R') {
        decayParams = [parseFloat($('#decay-radius').val()), (parseFloat($('#decay-ratio').val()) / 100)];
    }

    var data = {
        'sources': sources,
        'termination': {
            'type': terminationType,
            'param': terminationParam
        },
        'urgency-values': urgencyVals,
        'urgency-type': urgencyType,
        'decay-params': decayParams
    };

    $.ajax({
        url: '/diffusion-cl',
        type:'GET',
        cache: false,
        data: {
            type: 'cl',
            data: JSON.stringify(data)
        }
    }).done(function(data, status, xhr) {
        if ($('#results-cl').prop('disabled')) {
            $('#results-cl').prop('disabled', false);
        }
        var obj = JSON.parse(data);
        var diffusion = obj['diffusion'];

        chartData['num'] = {
            name: 'Active Node Number',
            data: obj['statistics']['num_in_step']
        };
        chartData['ratio'] = {
            name: 'Accumulated Active Node Ratio',
            data: obj['statistics']['ratio_in_step']
        };

        var points = layers.shift();
        var pointFeatures = points['features'];
        var newPoints = {
            type: 'FeatureCollection',
            features: []
        };
        
        for (var i = 0; i < pointFeatures.length; i++) {
            var pointID = pointFeatures[i]['id'];
            var newFeature = {
                id: pointID,
                type: "Feature",
                geometry: pointFeatures[i]['geometry'],
                properties: {}
            };
            var pointStatus = diffusion[pointID];
            if (pointStatus === 0) {
                newFeature['properties']['seed'] = true;
                newFeature['properties']['diffused'] =  0;
            } else if (pointStatus > 0) {
                newFeature['properties']['seed'] = false;
                newFeature['properties']['diffused'] =  pointStatus;
            } else {
                newFeature['properties']['seed'] = false;
                newFeature['properties']['diffused'] =  -1;
            }
            newPoints['features'].push(newFeature);
        }
        layers.unshift(newPoints);
        
        $('#cl-graph').empty();
        createLayers('#cl-graph', layers, {});

        var nodesToChange = layers[0]['features'].filter(function(feature) {
            return feature['properties']['diffused'] > 0;
        });
        nodesToChange.forEach(function(node) {
            (function(obj) {
                setTimeout(function() {
                    var objID = obj['id'];
                    var objEl = $('svg.geo-svg g.point #point' + objID);
                    objEl.removeClass('point-cl-normal');
                    objEl.addClass('point-cl-diffused');
                }, obj['properties']['diffused'] * 1000);
            })(node);
        });
    }).fail(function(xhr, status, error) {
        console.error(status);
        console.error(error);
    });
};

var ulrLTMHandler = function(event) {
    var minSeeds = parseInt($('#ulr-ltm-seed-min').val());
    var maxSeeds = parseInt($('#ulr-ltm-seed-max').val());
    var seedRangeNum = parseInt($('#ulr-ltm-seed-range-num').val());
    var seedAlg = $('#ulr-ltm-indicator').val();
    var minThres = parseFloat($('#ulr-ltm-threshold-min').val());
    var maxThres = parseFloat($('#ulr-ltm-threshold-max').val());
    var thresRangeNum = parseInt($('#ulr-ltm-threshold-range-num').val());
    var ltmData = {
        type: 'ulr', 
        model:'icm',
        minSeeds: minSeeds,
        maxSeeds: maxSeeds,
        seedRangeNum: seedRangeNum,
        seedAlg: seedAlg,
        minThres: minThres,
        maxThres: maxThres,
        thresRangeNum: thresRangeNum
    };

    $.ajax({
        url: '/diffusion-ulr/ltm',
        type:'GET',
        cache: false,
        data: ltmData,
    }).done(function(data, status, xhr) {
        if ($('#export-ulr-ltm').hasClass('disabled')) {
            $('#export-ulr-ltm').removeClass('disabled');
        }
        var ulrResults = JSON.parse(data);
        console.log(ulrResults);
        var ulrInfo = ulrResults['info'];
        var ulrData = ulrResults['data']
        $('#ulr-graph').empty();
        var chart = new Highcharts.Chart({
            chart: {
                renderTo: 'ulr-graph',
                margin: 100,
                type: 'scatter3d',
                animation: false,
                options3d: {
                    enabled: true,
                    alpha: 10,
                    beta: 30,
                    depth: 250,
                    viewDistance: 5,
                    fitToPlot: false,
                    frame: {
                        bottom: { size: 1, color: 'rgba(0,0,0,0.02)' },
                        back: { size: 1, color: 'rgba(0,0,0,0.04)' },
                        side: { size: 1, color: 'rgba(0,0,0,0.06)' }
                    }
                }
            },
            title: {
                text: 'Linear Threshold Model Results'
            },
            subtitle: {
                text: 'X Axis: ' + ulrInfo['x-field'] + ', ' + 'Y Axis: ' + ulrInfo['y-field'] + ', ' + 'Z Axis: Ratio of Influenced Nodes'
            },
            plotOptions: {
                scatter: {
                    width: 10,
                    height: 10,
                    depth: 10
                }
            },
            xAxis: {
                min: ulrInfo['x']['min'],
                max: ulrInfo['x']['max'],
                title: {
                    text: 'X'
                }
            },
            yAxis: {
                min: ulrInfo['y']['min'],
                max: ulrInfo['y']['max'],
                title: {
                    text: 'Y'
                }
            },
            zAxis: {
                min: 0.0,
                max: 1.0,
                title: {
                text: 'Z'
                }
            },
            legend: {
                enabled: false
            },
            series: [{
                name: 'Coverage',
                colorByPoint: true,
                data: ulrData
            }]
        });

        (function (H) {
            function dragStart(eStart) {
                eStart = chart.pointer.normalize(eStart);

                var posX = eStart.chartX,
                posY = eStart.chartY,
                alpha = chart.options.chart.options3d.alpha,
                beta = chart.options.chart.options3d.beta,
                sensitivity = 5,
                handlers = [];

                function drag(e) {
                e = chart.pointer.normalize(e);

                chart.update({
                    chart: {
                    options3d: {
                        alpha: alpha + (e.chartY - posY) / sensitivity,
                        beta: beta + (posX - e.chartX) / sensitivity
                    }
                    }
                }, undefined, undefined, false);
                }

                function unbindAll() {
                handlers.forEach(function (unbind) {
                    if (unbind) {
                    unbind();
                    }
                });
                handlers.length = 0;
                }

                handlers.push(H.addEvent(document, 'mousemove', drag));
                handlers.push(H.addEvent(document, 'touchmove', drag));


                handlers.push(H.addEvent(document, 'mouseup', unbindAll));
                handlers.push(H.addEvent(document, 'touchend', unbindAll));
            }
            H.addEvent(chart.container, 'mousedown', dragStart);
            H.addEvent(chart.container, 'touchstart', dragStart);
        }(Highcharts));
        
    }).fail(function(xhr, status, error) {
        console.error(status);
        console.error(error);
    });
};

var ulrICMHandler = function(event) {
    var icmEls = ulrICMStates.map(function(el) {
        var currentID = el[0];
        var currentState = el[1];
        var dataKey = $(currentID).data('key');
        var vals = null;
        if (currentState) {
            var rangedIDPrefix = $(currentID).data('ranged');
            var valMin = parseFloat($(rangedIDPrefix + '-min').val());
            var valMax = parseFloat($(rangedIDPrefix + '-max').val());
            var intervalNum = parseInt($(rangedIDPrefix + '-range-num').val());
            vals = {min: valMin, max: valMax, rn: intervalNum};
        } else {
            var defaultID = $(currentID).data('default');
            vals = parseFloat($(defaultID).val());
        }
        var el = {};
        el[dataKey] = vals;
        return el;
    });
    icmEls.push({alg: $('#ulr-icm-indicator').val()});
    icmEls.push({scale: $('.ulr-icm:checked').val()});

    var icmData = {};
    for (var el of icmEls ) {
        icmData = Object.assign(icmData, el);
    }

    $.ajax({
        url: '/diffusion-ulr/icm',
        type:'GET',
        cache: false,
        data: {type: 'ulr', model:'icm', data: JSON.stringify(icmData)},
    }).done(function(data, status, xhr) {
        if ($('#export-ulr-icm').hasClass('disabled')) {
            $('#export-ulr-icm').removeClass('disabled');
        }
        var ulrResults = JSON.parse(data);
        console.log(ulrResults);
        var ulrInfo = ulrResults['info'];
        var ulrData = ulrResults['data']
        $('#ulr-graph').empty();
        var chart = new Highcharts.Chart({
            chart: {
                renderTo: 'ulr-graph',
                margin: 100,
                type: 'scatter3d',
                animation: false,
                options3d: {
                    enabled: true,
                    alpha: 10,
                    beta: 30,
                    depth: 250,
                    viewDistance: 5,
                    fitToPlot: false,
                    frame: {
                        bottom: { size: 1, color: 'rgba(0,0,0,0.02)' },
                        back: { size: 1, color: 'rgba(0,0,0,0.04)' },
                        side: { size: 1, color: 'rgba(0,0,0,0.06)' }
                    }
                }
            },
            title: {
                text: 'Independent Cascade Model Results'
            },
            subtitle: {
                text: 'X Axis: ' + ulrInfo['x-field'] + ', ' + 'Y Axis: ' + ulrInfo['y-field'] + ', ' + 'Z Axis: Ratio of Influenced Nodes'
            },
            plotOptions: {
                scatter: {
                    width: 10,
                    height: 10,
                    depth: 10
                }
            },
            xAxis: {
                min: ulrInfo['x']['min'],
                max: ulrInfo['x']['max'],
                title: {
                    text: 'X'
                }
            },
            yAxis: {
                min: ulrInfo['y']['min'],
                max: ulrInfo['y']['max'],
                title: {
                    text: 'Y'
                }
            },
            zAxis: {
                min: 0.0,
                max: 1.0,
                title: {
                    text: 'Z'
                }
            },
            legend: {
                enabled: false
            },
            series: [{
                name: 'Coverage',
                colorByPoint: true,
                data: ulrData
            }]
        });

        (function (H) {
            function dragStart(eStart) {
                eStart = chart.pointer.normalize(eStart);
                var posX = eStart.chartX,
                posY = eStart.chartY,
                alpha = chart.options.chart.options3d.alpha,
                beta = chart.options.chart.options3d.beta,
                sensitivity = 5,
                handlers = [];

                function drag(e) {
                    e = chart.pointer.normalize(e);

                    chart.update({
                        chart: {
                            options3d: {
                                alpha: alpha + (e.chartY - posY) / sensitivity,
                                beta: beta + (posX - e.chartX) / sensitivity
                            }
                        }
                    }, undefined, undefined, false);
                }

                function unbindAll() {
                handlers.forEach(function (unbind) {
                    if (unbind) {
                    unbind();
                    }
                });
                handlers.length = 0;
                }

                handlers.push(H.addEvent(document, 'mousemove', drag));
                handlers.push(H.addEvent(document, 'touchmove', drag));
                handlers.push(H.addEvent(document, 'mouseup', unbindAll));
                handlers.push(H.addEvent(document, 'touchend', unbindAll));
            }
            H.addEvent(chart.container, 'mousedown', dragStart);
            H.addEvent(chart.container, 'touchstart', dragStart);
        }(Highcharts));

    }).fail(function(xhr, status, error) {
        console.error(status);
        console.error(error);
    });
};