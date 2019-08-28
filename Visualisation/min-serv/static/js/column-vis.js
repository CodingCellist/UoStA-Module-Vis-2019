/**
 * Visualisation of the modules and requisites of the University of St Andrews
 * using D3JS. Each module is represented as a rectangle with text inside and
 * each requisite as a cubic bezier curve connecting two rects. Pre-, Co-, and
 * Anti-requisites are coloured green, blue, and red respectively. On mouse-
 * over, the visualisation highlights the links and nodes relevant to the node
 * being moused-over.
 *
 * @summary Column-oriented visualisation of the UoStA modules and requisites
 * @author Thomas E. Hansen
 */


/**
 * Node object to associate the `returnNodes` function with.
 *
 * @param id The id of the node -- The module code.
 * @param group DEPRECATED. Used for the force-directed graphs.
 */
function Node(id, group) {
    this.id = id;
    this.group = group;
    // FixMe: if the force-directed drafts are discarded, the `group` field
    // FixMe: should be removed from here and lines 19 and 20
}

// make sure each `Node` has the `returnNodes` function, used to find ancestors
Node.prototype.returnNodes = returnNodes;

// print the data put into `index.html` by jinja2
console.log(MY_DATA);

////////////////////
// PRE-PROCESSING //
////////////////////

// turn all the nodes, which are currently `Object`, into `Node` objects
MY_DATA.nodes = _.map(MY_DATA.nodes, function ({id, group}) {
    return new Node(id, group);
});

// calculate all the connected nodes and paths
MY_DATA.nodes.forEach(function (node) {
    let nodeList = [],
        linkList = [];
    node.returnNodes(nodeList, linkList);
    node.ancestorOf = nodeList;
    node.ancestorLinks = linkList;
});

console.log(MY_DATA.nodes);

// nest the modules by their level, i.e. the 3rd char in their name
let nestedModules = d3.nest()
    .key(function (d) {
        return d.id[2];
    })
    .entries(MY_DATA.nodes);

console.log(nestedModules);

// nest the links by their type, i.e. "pre", "anti", and "co"
let nestedLinks = d3.nest()
    .key(function (d) {
        return d.type.toLowerCase();
    })
    .entries(MY_DATA.links);

console.log(nestedLinks);

///////////
// SETUP //
///////////

// attrs of svg
const width = 960;
const height = 2000;

const xMargin = width / 15;
const yMargin = height / 100;

// D3 stuff
let svg = d3.select("body")
            .select("#svgContainer")
            .append("svg")
            .attr("width", width)
            .attr("height", height);

const nodeRadius = 5;

let xScale = d3.scaleBand(
    _.map(nestedModules, 'key'),
    [xMargin, width - xMargin]
)
    .paddingInner(0.5);
let yScale = d3.scaleBand(
    _.range(_.max(_.map(_.map(nestedModules, 'values'), arr => arr.length))),
    [yMargin, height - yMargin]
)
    .paddingInner(0.15);

// colour-coding the groups
let schoolCodes = _.uniqBy(MY_DATA.nodes, function (n) {
    return n.id.substring(0, 2);
});
let colours = d3.scaleOrdinal(schoolCodes, d3.schemeCategory10);

///////////////////
// NODE CREATION //
///////////////////

let levelGroups = svg.selectAll("myGroups")
    .data(nestedModules)
    .enter()
    .append("g")
        .attr("transform", function (d) {
            // translate wrt. the scale defined through d3
            return "translate(" + xScale(d.key) + ", 0)";
        });

// DRAWING RECTS AS NODES
let rects = levelGroups.selectAll("myRects")
    .data(function (d) {
        return d.values;
    })
    .enter()
    .append("rect")
        .attr("id", function (d) {
            return d.id;
        })
        .attr("class", ancestorClasses)
        .attr("y", function (d, i) {
            return yScale(i);
        })
        .attr("width", xScale.bandwidth())
        .attr("height", yScale.bandwidth())
        .attr("fill", function (d) {
            return colours(d.id.substring(0, 2))
        })
        .on("mouseover", mouseover)
        .on("mouseout", mouseout)
    .append("title")
        .text(function (d) {
            return d.id;
        });
// text in the rects
levelGroups.selectAll("myText")
    .data(function (d) {
        return d.values;
    })
    .enter()
    .append("text")
        .attr("text-anchor", "middle")
        .attr("x", xScale.bandwidth() / 2)
        .attr("y", function (d, i) {
            let bdw = yScale.bandwidth();
            return yScale(i) + bdw - yScale.paddingInner() * bdw;
        })
        // .attr("font-size", yScale.bandwidth() + "px")
        .text(function (d) {
            return d.id;
        })
        .on("mouseover", mouseover)
        .on("mouseout", mouseout);

///////////////////
// LINK CREATION //
///////////////////

let linkGroups = svg.selectAll("linkGroups")
    .data(nestedLinks)
    .enter()
    .append("g")
        .attr("class", function (d) {
            return d.key + "-req";
        });

// cubic bezier links
let horizontalLinkGenerator = d3.linkHorizontal();
let cubicLinks = linkGroups.selectAll("myCubicLinks")
    .data(function (d) {
        return d.values;
    })
    .enter()
    .append("path")
        .attr("id", function (d) {
            return d.source + "--" + d.target;
        })
        .attr("class", function (d) {
            // this link dictates ancestors for its source node
            const srcNode = MY_DATA.nodes.filter(function (node) {
                return node.id === d.source;
            })[0];
            return ancestorClasses(srcNode);
        })
        .attr("d", function (d) {
            // find the coordinates, with translation
            let x1 = xScale(parseInt(d.source[2])),
                // y1 = parseFloat(d3.select("#" + d.source).attr("cy")),   // circle
                y1 = parseFloat(d3.select("#" + d.source).attr("y")),       // rect
                x2 = xScale(parseInt(d.target[2])),
                // y2 = parseFloat(d3.select("#" + d.target).attr("cy"));   // circle
                y2 = parseFloat(d3.select("#" + d.target).attr("y"));       // rect

            // FOR RECTS: center the y-point
            y1 += yScale.bandwidth() / 2;
            y2 += yScale.bandwidth() / 2;

            if (x1 === x2) {
                // if the link is vertical do things manually
                let diff = xScale(2) - xScale(1);
                // calculate the control point
                let cpX = x1 - diff / 2,
                    cpY = y1 > y2
                            ? y2 + (y1 - y2) / 2
                            : y1 + (y2 - y1) / 2;
                return "M" + x1 + "," + y1
                    + " Q" + cpX + "," + cpY
                    + " " + x2 + "," + y2;
            } else {
                // FOR RECTS: change x-coordinate wrt. the width of the rect
                if (x1 < x2) {
                    x1 += xScale.bandwidth();
                } else {
                    x2 += xScale.bandwidth();
                }

                // store the coordinates in an object for D3
                let coords = {
                    "source": [x1, y1],
                    "target": [x2, y2]
                };
                return horizontalLinkGenerator(coords);
            }
        });

/////////////
// HELPERS //
/////////////

// helper function to find all children of the given node
function returnNodes(nodeList, linkList) {
    if (!nodeList.includes(this)) {
        // add the current node to the nodeList
        nodeList.push(this);
        const nodeID = this.id;
        // find all links leading to this node
        let connectedLinks =
            MY_DATA.links
                .filter(function (link) {
                    return link.target === nodeID;  // finds the paths ending here
                    // return link.source === nodeID;  // finds the links starting here
                });
        // add the connected links not already in the linkList to it
        connectedLinks.forEach(function (link) {
            if (!linkList.includes(link)) {
                linkList.push(link);
            }
        });
        // find the ids of the origin-nodes of the connected links
        let connectedIds =
            connectedLinks
                .map(function (link) {
                    return link.source;     // w. "finds the paths ending here"
                    // return link.target;  // w. "finds the links starting here"
                })
        ;
        // find the `Node` objects the connectedIds refer to
        let connectedNodes =
            MY_DATA.nodes
                .filter(function (node) {
                    return connectedIds.includes(node.id)
                })
        ;
        // call this function for each of those nodes, repeating the process
        connectedNodes.forEach(function (connected) {
            connected.returnNodes(nodeList, linkList);
        });
    }
}

// helper function returning a string of `ancestor-of-` classes for a given
// node
function ancestorClasses(node) {
    if (node === undefined || node === null) return "";
    const prefix = "ancestor-of-";
    let classes = "";
    let ancestorClasses = _.map(node.ancestorOf, function (ancestor) {
        return prefix + ancestor.id + " ";
    });
    ancestorClasses.forEach(function (ancestorClass) {
        classes = classes + ancestorClass;
    });
    return classes;
}

////////////
// EVENTS //
////////////

// highlight all the ancestors on mouseover
function mouseover(d) {
    svg.selectAll(".ancestor-of-" + d.id)
        .classed("highlighted", true)
}

// remove all highlighting on mouseout
function mouseout() {
    svg.selectAll(".highlighted")
        .classed("highlighted", false);
}