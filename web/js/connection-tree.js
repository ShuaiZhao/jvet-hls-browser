/**
 * Interactive Connection Tree
 * Displays parameter connections as a recursive, clickable tree
 */

class ConnectionTree {
    constructor(semanticsData, connectionsData) {
        this.semanticsData = semanticsData;
        this.connectionsData = connectionsData;
        this.expandedNodes = new Set(); // Track which nodes are expanded
        this.visitedNodes = new Set(); // Prevent circular references
    }

    /**
     * Show connection tree for a parameter in a modal
     */
    showTree(parameterName) {
        // Clear visited nodes for fresh tree
        this.visitedNodes.clear();
        this.expandedNodes.clear();

        // Create modal
        const modal = document.getElementById('connectionTreeModal');
        if (!modal) {
            console.error('Connection tree modal not found');
            return;
        }

        // Set title
        document.getElementById('treeModalTitle').textContent =
            `Connection Tree: ${parameterName}`;

        // Build tree
        const treeContainer = document.getElementById('connectionTreeContainer');
        treeContainer.innerHTML = '';

        const rootNode = this.createTreeNode(parameterName, 0, null);
        treeContainer.appendChild(rootNode);

        // Show modal
        modal.classList.add('active');
    }

    /**
     * Create a tree node for a parameter
     */
    createTreeNode(parameterName, depth, parentType) {
        const nodeDiv = document.createElement('div');
        nodeDiv.className = 'tree-node';
        nodeDiv.style.marginLeft = `${depth * 20}px`;

        // Check if already visited (circular reference)
        const isVisited = this.visitedNodes.has(parameterName);
        if (isVisited) {
            nodeDiv.innerHTML = `
                <div class="tree-node-header circular">
                    <i class="fas fa-redo"></i>
                    <span class="tree-node-name">${parameterName}</span>
                    <span class="tree-node-badge circular">circular</span>
                </div>
            `;
            return nodeDiv;
        }

        // Mark as visited
        this.visitedNodes.add(parameterName);

        // Get connections for this parameter
        const connections = this.connectionsData[parameterName] || {
            references: [],
            dependencies: [],
            related_concepts: []
        };

        const totalConnections =
            connections.references.length +
            connections.dependencies.length +
            connections.related_concepts.length;

        // Create node header
        const header = document.createElement('div');
        header.className = 'tree-node-header';

        // Add parent type badge if applicable
        let parentBadge = '';
        if (parentType) {
            const badgeClass = parentType === 'reference' ? 'ref' :
                              parentType === 'dependency' ? 'dep' : 'rel';
            parentBadge = `<span class="tree-node-badge ${badgeClass}">${parentType}</span>`;
        }

        // Expand/collapse icon
        const hasConnections = totalConnections > 0;
        const expandIcon = hasConnections ?
            '<i class="fas fa-chevron-right tree-expand-icon"></i>' :
            '<i class="fas fa-circle tree-leaf-icon"></i>';

        header.innerHTML = `
            ${expandIcon}
            <span class="tree-node-name">${parameterName}</span>
            ${parentBadge}
            ${hasConnections ? `<span class="tree-node-count">${totalConnections}</span>` : ''}
        `;

        // Add click handler for parameter name (to show semantics)
        const nameSpan = header.querySelector('.tree-node-name');
        nameSpan.addEventListener('click', (e) => {
            e.stopPropagation();
            selectParameter(parameterName); // Call global function
            switchTab('semantics');
        });

        // Add expand/collapse handler
        if (hasConnections) {
            header.style.cursor = 'pointer';
            header.addEventListener('click', () => {
                this.toggleNode(nodeDiv, parameterName, depth);
            });
        }

        nodeDiv.appendChild(header);

        // Create children container (initially hidden)
        if (hasConnections) {
            const childrenDiv = document.createElement('div');
            childrenDiv.className = 'tree-node-children';
            childrenDiv.style.display = 'none';
            nodeDiv.appendChild(childrenDiv);
        }

        return nodeDiv;
    }

    /**
     * Toggle node expansion
     */
    toggleNode(nodeDiv, parameterName, depth) {
        const childrenDiv = nodeDiv.querySelector('.tree-node-children');
        const expandIcon = nodeDiv.querySelector('.tree-expand-icon');

        if (!childrenDiv) return;

        const isExpanded = childrenDiv.style.display !== 'none';

        if (isExpanded) {
            // Collapse
            childrenDiv.style.display = 'none';
            expandIcon.classList.remove('fa-chevron-down');
            expandIcon.classList.add('fa-chevron-right');
            this.expandedNodes.delete(parameterName);
        } else {
            // Expand
            if (childrenDiv.children.length === 0) {
                // First time expanding - build children
                this.buildChildren(childrenDiv, parameterName, depth + 1);
            }
            childrenDiv.style.display = 'block';
            expandIcon.classList.remove('fa-chevron-right');
            expandIcon.classList.add('fa-chevron-down');
            this.expandedNodes.add(parameterName);
        }
    }

    /**
     * Build child nodes for a parameter
     */
    buildChildren(container, parameterName, depth) {
        const connections = this.connectionsData[parameterName];
        if (!connections) return;

        // Add references
        if (connections.references && connections.references.length > 0) {
            const refGroup = this.createConnectionGroup(
                'References',
                connections.references,
                'reference',
                depth
            );
            container.appendChild(refGroup);
        }

        // Add dependencies
        if (connections.dependencies && connections.dependencies.length > 0) {
            const depGroup = this.createConnectionGroup(
                'Dependencies',
                connections.dependencies,
                'dependency',
                depth
            );
            container.appendChild(depGroup);
        }

        // Add related concepts
        if (connections.related_concepts && connections.related_concepts.length > 0) {
            const relGroup = this.createConnectionGroup(
                'Related',
                connections.related_concepts,
                'related',
                depth
            );
            container.appendChild(relGroup);
        }
    }

    /**
     * Create a group of connections
     */
    createConnectionGroup(title, connections, type, depth) {
        const group = document.createElement('div');
        group.className = 'tree-connection-group';

        // Group header
        const groupHeader = document.createElement('div');
        groupHeader.className = `tree-group-header ${type}`;
        groupHeader.style.marginLeft = `${depth * 20}px`;
        groupHeader.innerHTML = `
            <i class="fas fa-folder"></i>
            <span>${title}</span>
            <span class="tree-node-count">${connections.length}</span>
        `;
        group.appendChild(groupHeader);

        // Add each connection as a child node
        connections.forEach(conn => {
            const childNode = this.createTreeNode(conn.parameter, depth + 1, type);

            // Add connection context as tooltip
            const header = childNode.querySelector('.tree-node-header');
            if (conn.context) {
                header.title = `${conn.context} (${Math.round(conn.strength * 100)}%)`;
            }

            // Add strength indicator
            if (conn.strength) {
                const strengthBar = document.createElement('div');
                strengthBar.className = 'tree-strength-bar';
                strengthBar.style.width = `${conn.strength * 100}%`;
                header.appendChild(strengthBar);
            }

            group.appendChild(childNode);
        });

        return group;
    }

    /**
     * Close the tree modal
     */
    close() {
        const modal = document.getElementById('connectionTreeModal');
        if (modal) {
            modal.classList.remove('active');
        }
    }

    /**
     * Expand all nodes in the tree
     */
    expandAll() {
        const allHeaders = document.querySelectorAll('.tree-node-header');
        allHeaders.forEach(header => {
            const nodeDiv = header.parentElement;
            const paramName = header.querySelector('.tree-node-name').textContent;
            const depth = parseInt(nodeDiv.style.marginLeft) / 20;

            if (header.querySelector('.tree-expand-icon')) {
                const childrenDiv = nodeDiv.querySelector('.tree-node-children');
                if (childrenDiv && childrenDiv.style.display === 'none') {
                    this.toggleNode(nodeDiv, paramName, depth);
                }
            }
        });
    }

    /**
     * Collapse all nodes in the tree
     */
    collapseAll() {
        const allHeaders = document.querySelectorAll('.tree-node-header');
        allHeaders.forEach(header => {
            const nodeDiv = header.parentElement;
            const childrenDiv = nodeDiv.querySelector('.tree-node-children');

            if (childrenDiv && childrenDiv.style.display !== 'none') {
                const expandIcon = header.querySelector('.tree-expand-icon');
                childrenDiv.style.display = 'none';
                if (expandIcon) {
                    expandIcon.classList.remove('fa-chevron-down');
                    expandIcon.classList.add('fa-chevron-right');
                }
            }
        });
        this.expandedNodes.clear();
    }
}

// Global connection tree instance
let connectionTreeInstance = null;

// Initialize connection tree
function initConnectionTree(semanticsData, connectionsData) {
    connectionTreeInstance = new ConnectionTree(semanticsData, connectionsData);
}

// Show connection tree for a parameter
function showConnectionTree(parameterName) {
    if (connectionTreeInstance) {
        connectionTreeInstance.showTree(parameterName);
    }
}

// Close connection tree modal
function closeConnectionTree() {
    if (connectionTreeInstance) {
        connectionTreeInstance.close();
    }
}

// Expand all connections
function expandAllConnections() {
    if (connectionTreeInstance) {
        connectionTreeInstance.expandAll();
    }
}

// Collapse all connections
function collapseAllConnections() {
    if (connectionTreeInstance) {
        connectionTreeInstance.collapseAll();
    }
}
