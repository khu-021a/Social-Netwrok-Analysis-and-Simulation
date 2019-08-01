let forceGraph = (options) => {
    let anchor = options['anchor']
    let nodeRadius = options['nodeRadius']
    let emphasisFillKey = options['emphasisFillKey']
    let emphasisStrokeKey = options['emphasisStrokeKey']

    let svg = d3.select(anchor).append('svg')
    let shapes = svg.append('g')
    let zoom = (zoomView, minExtent, maxExtent) => d3.zoom().scaleExtent([minExtent, maxExtent]).on('zoom', () => zoomView.attr('transform', d3.event.transform))
    svg.call(zoom(shapes, .25, 8))

    let w = svg.node().parentNode.clientWidth
    let h = svg.node().parentNode.clientHeight

    let simulation = d3.forceSimulation()
        .force('charge', d3.forceManyBody())
        .force('center', d3.forceCenter(w / 2, h / 2))
        .force('collide', d3.forceCollide(1))
    let draggable = d3.drag()
        .on('start', datum => {
        if (!d3.event.active) simulation.alphaTarget(.3).restart()
        datum.fx = datum.x
        datum.fy = datum.y
        })
        .on('drag', datum => {
        datum.fx = d3.event.x
        datum.fy = d3.event.y
        })
        .on('end', datum => {
        if (!d3.event.active) simulation.alphaTarget(0)
        datum.fx = null
        datum.fy = null
        })

    let bindLinks = (dataset, anchor) => {
        let slots = anchor.selectAll('line').data(dataset)
        slots.exit().remove()
        let gLinks = slots.enter().append('line').merge(slots).attr('id', datum => 'l' + datum['id']).classed('link-normal', true)
        return gLinks
    }

    let bindNodes = (dataset, anchor) => {
        let slots = anchor.selectAll('g').data(dataset)
        slots.exit().remove()
        let gNodes = slots.enter().append('g')
        gNodes.append('circle').attr('r', nodeRadius)
        .classed('opinion', d => d[emphasisStrokeKey])
        .classed('node-normal', d => !d[emphasisFillKey])
        .classed('node-seed', d => d[emphasisFillKey])
        .classed('bc-1', d => d['bc'] === 1)
        .classed('bc-2', d => d['bc'] === 2)
        .classed('bc-3', d => d['bc'] === 3)
        .classed('bc-4', d => d['bc'] === 4)
        .classed('cc-1', d => d['cc'] === 1)
        .classed('cc-2', d => d['cc'] === 2)
        .classed('cc-3', d => d['cc'] === 3)
        .classed('cc-4', d => d['cc'] === 4)
        .classed('dc-1', d => d['dc'] === 1)
        .classed('dc-2', d => d['dc'] === 2)
        .classed('dc-3', d => d['dc'] === 3)
        .classed('dc-4', d => d['dc'] === 4)
        .classed('ec-1', d => d['ec'] === 1)
        .classed('ec-2', d => d['ec'] === 2)
        .classed('ec-3', d => d['ec'] === 3)
        .classed('ec-4', d => d['ec'] === 4)
        .classed('community-0', d => d['community'] % 20 === -1)
        .classed('community-1', d => d['community'] % 20 === 0)
        .classed('community-2', d => d['community'] % 20 === 1)
        .classed('community-3', d => d['community'] % 20 === 2)
        .classed('community-4', d => d['community'] % 20 === 3)
        .classed('community-5', d => d['community'] % 20 === 4)
        .classed('community-6', d => d['community'] % 20 === 5)
        .classed('community-7', d => d['community'] % 20 === 6)
        .classed('community-8', d => d['community'] % 20 === 7)
        .classed('community-9', d => d['community'] % 20 === 8)
        .classed('community-10', d => d['community'] % 20 === 9)
        .classed('community-11', d => d['community'] % 20 === 10)
        .classed('community-12', d => d['community'] % 20 === 11)
        .classed('community-13', d => d['community'] % 20 === 12)
        .classed('community-14', d => d['community'] % 20 === 13)
        .classed('community-15', d => d['community'] % 20 === 14)
        .classed('community-16', d => d['community'] % 20 === 15)
        .classed('community-17', d => d['community'] % 20 === 16)
        .classed('community-18', d => d['community'] % 20 === 17)
        .classed('community-19', d => d['community'] % 20 === 18)
        .classed('community-20', d => d['community'] % 20 === 19)
        gNodes = gNodes.merge(slots).attr('id', datum => datum.id).call(draggable)
        return gNodes
    }

    let linkAnchor = shapes.append('g').classed('links', true)

    let nodeAnchor = shapes.append('g').classed('nodes', true)

    let importData = (nodeArr, linkArr) => {

        let nodes = bindNodes(nodeArr, nodeAnchor)
        let links = bindLinks(linkArr, linkAnchor)
        
        let ticked = () => {
        links.attr('x1', (datum) => datum['source'].x)
        .attr('y1', (datum) => datum['source'].y)
        .attr('x2', (datum) => datum['target'].x)
        .attr('y2', (datum) => datum['target'].y)

        nodes.attr('transform', datum => `translate(${datum.x}, ${datum.y})`)
        }

        simulation.nodes(nodeArr).on('tick', ticked)
        simulation.force('link', d3.forceLink(linkArr).id(datum => datum['id']))
        simulation.alphaTarget(.3).restart()
    }
    return importData
}
