let createLayers = (anchor, layers, options) => {
    let slot = d3.select(anchor)
    slot.selectAll('.geo-svg').remove()
    let svg = slot.append('svg').classed('geo-svg', true)
    let w = svg.node().parentNode.clientWidth
    let h = svg.node().parentNode.clientHeight
    svg.attr('width', w).attr('height', h)
    let entire = svg.append('g').classed('entire', true)

    layers.reverse()
    let projection = d3.geoMercator().scale(1).translate([0, 0])
    let path = d3.geoPath(projection)
    let bboxes = layers.map(layer => path.bounds(layer))
    let xMins = [], yMins = [], xMaxes = [], yMaxes = []
    for (let bbox of bboxes) {
        let [[x0, y0], [x1, y1]] = bbox
        xMins.push(x0)
        yMins.push(y0)
        xMaxes.push(x1)
        yMaxes.push(y1)
    }
    let b = [[Math.min(...xMins), Math.min(...yMins)], [Math.max(...xMaxes), Math.max(...yMaxes)]]
    let s = .95 / Math.max((b[1][0] - b[0][0]) / w, (b[1][1] - b[0][1]) / h)
    let t = [(w - s * (b[1][0] + b[0][0])) / 2, (h - s * (b[1][1] + b[0][1])) / 2]
    projection.scale(s).translate(t)

    let zoom = (zoomView, minExtent, maxExtent) => d3.zoom().scaleExtent([minExtent, maxExtent]).on('zoom', () => zoomView.attr('transform', d3.event.transform))
    
    svg.call(zoom(entire, .125, 32))

    layers.forEach(layer => {
        let features = layer.features;
        let featureType = features[0]['geometry']['type'];
        let className = null;
        switch (featureType) {
            case 'Point': 
                className = 'point'
                break
            case 'MultiPoint': 
                className = 'multi-point'
                break
            case 'LineString': 
                className = 'line'
                break
            case 'MultiLineString': 
                className = 'multi-line'
                break
            case 'Polygon': 
                className = 'polygon'
                break
            case 'MultiPolygon': 
                className = 'multi-polygon'
                break
            default: 
                className = 'other'
                break
        }
        let map = entire.append('g').classed(className, true).selectAll('path').data(features)
        if (featureType === 'Point') {
            map.enter().append('path').attr('id', d => (className + d.id)).classed('point-cl-normal', d => !d['properties']['seed']).classed('point-cl-diffused', d => d['properties']['seed']).attr('d', path)
        } else {
            map.enter().append('path').attr('id', d => (className + d.id)).attr('d', path)
        }
        
        map.exit().remove()
    })
    layers.reverse()
}