/**
 * D3.js Connection Graph Visualization
 * Displays parameter connections as a force-directed graph
 */

let connectionsData = null;
let currentGraph = null;

// Load connections data
async function loadConnectionsData() {
    if (!connectionsData) {
        try {
            const response = await fetch(`data/${currentCodec}/connections.json`);
            connectionsData = await response.json();
        } catch (error) {
            console.error('Error loading connections:', error);
            connectionsData = {};
        }
    }
    return connectionsData;
}

/**
 * Display connections for a parameter in the connections tab
 */
async function displayConnections(paramName) {
    const connectionsTab = document.getElementById('connectionsTab');

    // Show loading state
    connectionsTab.innerHTML = `
        <div class="connections-loading">
            <i class="fas fa-spinner fa-spin"></i>
            <p>Loading connections...</p>
        </div>
    `;

    await loadConnectionsData();

    const paramConnections = connectionsData[paramName];

    if (!paramConnections) {
        connectionsTab.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-info-circle"></i>
                <p>No connection data available for "${paramName}"</p>
            </div>
        `;
        return;
    }

    // Build connections HTML
    let html = `
        <div class="connections-header">
            <h3>${paramName}</h3>
            <button class="btn-view-graph" onclick="showConnectionGraph('${paramName}')">
                <i class="fas fa-project-diagram"></i> View Graph
            </button>
        </div>
        <div class="connections-content">
    `;

    // Dependencies
    if (paramConnections.dependencies && paramConnections.dependencies.length > 0) {
        html += `
            <div class="connection-section">
                <h4><i class="fas fa-arrow-left"></i> Dependencies (${paramConnections.dependencies.length})</h4>
                <p class="section-desc">Parameters that <strong>${paramName}</strong> depends on</p>
                <div class="connection-list">
        `;

        paramConnections.dependencies
            .sort((a, b) => b.strength - a.strength)
            .forEach(conn => {
                const strengthClass = getStrengthClass(conn.strength);
                html += `
                    <div class="connection-item ${strengthClass}">
                        <div class="connection-header">
                            <span class="connection-param clickable-param" onclick="navigateToParameter('${conn.parameter}')">${conn.parameter}</span>
                            <span class="connection-strength" title="Strength: ${(conn.strength * 100).toFixed(0)}%">${'●'.repeat(Math.ceil(conn.strength * 5))}</span>
                        </div>
                        <div class="connection-context">${conn.context}</div>
                    </div>
                `;
            });

        html += `
                </div>
            </div>
        `;
    }

    // References
    if (paramConnections.references && paramConnections.references.length > 0) {
        html += `
            <div class="connection-section">
                <h4><i class="fas fa-arrow-right"></i> References (${paramConnections.references.length})</h4>
                <p class="section-desc">Parameters referenced by <strong>${paramName}</strong></p>
                <div class="connection-list">
        `;

        paramConnections.references
            .sort((a, b) => b.strength - a.strength)
            .forEach(conn => {
                const strengthClass = getStrengthClass(conn.strength);
                html += `
                    <div class="connection-item ${strengthClass}">
                        <div class="connection-header">
                            <span class="connection-param clickable-param" onclick="navigateToParameter('${conn.parameter}')">${conn.parameter}</span>
                            <span class="connection-strength" title="Strength: ${(conn.strength * 100).toFixed(0)}%">${'●'.repeat(Math.ceil(conn.strength * 5))}</span>
                        </div>
                        <div class="connection-context">${conn.context}</div>
                    </div>
                `;
            });

        html += `
                </div>
            </div>
        `;
    }

    // Related Concepts
    if (paramConnections.related_concepts && paramConnections.related_concepts.length > 0) {
        html += `
            <div class="connection-section">
                <h4><i class="fas fa-link"></i> Related Concepts (${paramConnections.related_concepts.length})</h4>
                <p class="section-desc">Conceptually related parameters</p>
                <div class="connection-list">
        `;

        paramConnections.related_concepts
            .sort((a, b) => b.strength - a.strength)
            .forEach(conn => {
                const strengthClass = getStrengthClass(conn.strength);
                html += `
                    <div class="connection-item ${strengthClass}">
                        <div class="connection-header">
                            <span class="connection-param clickable-param" onclick="navigateToParameter('${conn.parameter}')">${conn.parameter}</span>
                            <span class="connection-strength" title="Strength: ${(conn.strength * 100).toFixed(0)}%">${'●'.repeat(Math.ceil(conn.strength * 5))}</span>
                        </div>
                        <div class="connection-context">${conn.context}</div>
                    </div>
                `;
            });

        html += `
                </div>
            </div>
        `;
    }

    html += '</div>';

    connectionsTab.innerHTML = html;
}

/**
 * Navigate to a parameter (helper function for clickable params)
 */
function navigateToParameter(paramName) {
    // Show semantics popup for the parameter
    displaySemantics(paramName);
}

/**
 * Get CSS class based on connection strength
 */
function getStrengthClass(strength) {
    if (strength >= 0.8) return 'strength-high';
    if (strength >= 0.5) return 'strength-medium';
    return 'strength-low';
}

/**
 * Show connection graph in modal
 */
async function showConnectionGraph(paramName, depth = 2) {
    await loadConnectionsData();

    const modal = document.getElementById('graphModal');
    const graphContainer = document.getElementById('connectionGraph');

    // Clear previous graph
    graphContainer.innerHTML = '';

    // Show modal
    modal.style.display = 'flex';

    // Build graph data
    const { nodes, links } = buildGraphData(paramName, depth);

    if (nodes.length === 0) {
        graphContainer.innerHTML = '<div class="empty-state"><p>No connections to visualize</p></div>';
        return;
    }

    // Create D3 force-directed graph
    createForceGraph(graphContainer, nodes, links, paramName);
}

/**
 * Build graph data (nodes and links) from connections
 */
function buildGraphData(rootParam, depth) {
    const nodes = new Map();
    const links = [];
    const visited = new Set();

    // Add root node
    nodes.set(rootParam, {
        id: rootParam,
        label: rootParam,
        level: 0,
        isRoot: true
    });

    // BFS to build graph
    const queue = [{ param: rootParam, level: 0 }];

    while (queue.length > 0) {
        const { param, level } = queue.shift();

        if (visited.has(param) || level >= depth) continue;
        visited.add(param);

        const connections = connectionsData[param];
        if (!connections) continue;

        // Add dependencies
        if (connections.dependencies) {
            connections.dependencies.forEach(conn => {
                // Add node if not exists
                if (!nodes.has(conn.parameter)) {
                    nodes.set(conn.parameter, {
                        id: conn.parameter,
                        label: conn.parameter,
                        level: level + 1,
                        isRoot: false
                    });
                    queue.push({ param: conn.parameter, level: level + 1 });
                }

                // Add link
                links.push({
                    source: conn.parameter,
                    target: param,
                    type: 'dependency',
                    strength: conn.strength,
                    context: conn.context
                });
            });
        }

        // Add references
        if (connections.references) {
            connections.references.forEach(conn => {
                // Add node if not exists
                if (!nodes.has(conn.parameter)) {
                    nodes.set(conn.parameter, {
                        id: conn.parameter,
                        label: conn.parameter,
                        level: level + 1,
                        isRoot: false
                    });
                    queue.push({ param: conn.parameter, level: level + 1 });
                }

                // Add link
                links.push({
                    source: param,
                    target: conn.parameter,
                    type: 'reference',
                    strength: conn.strength,
                    context: conn.context
                });
            });
        }

        // Add related concepts (only at depth 1 to avoid clutter)
        if (level < 1 && connections.related_concepts) {
            connections.related_concepts.forEach(conn => {
                // Add node if not exists
                if (!nodes.has(conn.parameter)) {
                    nodes.set(conn.parameter, {
                        id: conn.parameter,
                        label: conn.parameter,
                        level: level + 1,
                        isRoot: false
                    });
                }

                // Add link
                links.push({
                    source: param,
                    target: conn.parameter,
                    type: 'related',
                    strength: conn.strength,
                    context: conn.context
                });
            });
        }
    }

    return {
        nodes: Array.from(nodes.values()),
        links: links
    };
}

/**
 * Create D3 force-directed graph
 */
function createForceGraph(container, nodes, links, rootParam) {
    const width = container.clientWidth;
    const height = 600;

    // Create SVG
    const svg = d3.select(container)
        .append('svg')
        .attr('width', width)
        .attr('height', height)
        .attr('class', 'connection-graph-svg');

    // Add zoom behavior
    const g = svg.append('g');

    svg.call(d3.zoom()
        .scaleExtent([0.1, 4])
        .on('zoom', (event) => {
            g.attr('transform', event.transform);
        }));

    // Create arrow markers for directed edges
    svg.append('defs').selectAll('marker')
        .data(['dependency', 'reference', 'related'])
        .join('marker')
        .attr('id', d => `arrow-${d}`)
        .attr('viewBox', '0 -5 10 10')
        .attr('refX', 20)
        .attr('refY', 0)
        .attr('markerWidth', 6)
        .attr('markerHeight', 6)
        .attr('orient', 'auto')
        .append('path')
        .attr('d', 'M0,-5L10,0L0,5')
        .attr('fill', d => {
            if (d === 'dependency') return '#667eea';
            if (d === 'reference') return '#f093fb';
            return '#4facfe';
        });

    // Create force simulation
    const simulation = d3.forceSimulation(nodes)
        .force('link', d3.forceLink(links)
            .id(d => d.id)
            .distance(d => 100 - (d.strength * 50))
            .strength(d => d.strength))
        .force('charge', d3.forceManyBody().strength(-300))
        .force('center', d3.forceCenter(width / 2, height / 2))
        .force('collision', d3.forceCollide().radius(40));

    // Create links
    const link = g.append('g')
        .attr('class', 'links')
        .selectAll('line')
        .data(links)
        .join('line')
        .attr('class', d => `link link-${d.type}`)
        .attr('stroke-width', d => 1 + d.strength * 3)
        .attr('marker-end', d => `url(#arrow-${d.type})`)
        .append('title')
        .text(d => d.context);

    // Create nodes
    const node = g.append('g')
        .attr('class', 'nodes')
        .selectAll('g')
        .data(nodes)
        .join('g')
        .attr('class', d => `node ${d.isRoot ? 'node-root' : ''} node-level-${d.level}`)
        .call(d3.drag()
            .on('start', dragStarted)
            .on('drag', dragged)
            .on('end', dragEnded));

    // Add circles to nodes
    node.append('circle')
        .attr('r', d => d.isRoot ? 12 : 8)
        .attr('fill', d => {
            if (d.isRoot) return '#f093fb';
            if (d.level === 1) return '#667eea';
            return '#4facfe';
        });

    // Add labels to nodes
    node.append('text')
        .text(d => d.label)
        .attr('x', 15)
        .attr('y', 4)
        .attr('class', 'node-label')
        .style('font-size', d => d.isRoot ? '14px' : '12px')
        .style('font-weight', d => d.isRoot ? 'bold' : 'normal');

    // Add click handler to navigate to parameter
    node.on('click', (event, d) => {
        navigateToParameter(d.id);
    });

    // Update positions on each tick
    simulation.on('tick', () => {
        link
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);

        node.attr('transform', d => `translate(${d.x},${d.y})`);
    });

    // Drag functions
    function dragStarted(event, d) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }

    function dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }

    function dragEnded(event, d) {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }

    currentGraph = { svg, simulation };
}

/**
 * Close connection graph modal
 */
function closeGraphModal() {
    const modal = document.getElementById('graphModal');
    modal.style.display = 'none';

    // Stop simulation
    if (currentGraph && currentGraph.simulation) {
        currentGraph.simulation.stop();
    }
}

// Close modal when clicking outside
window.addEventListener('click', (event) => {
    const modal = document.getElementById('graphModal');
    if (event.target === modal) {
        closeGraphModal();
    }
});
