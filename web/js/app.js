/**
 * Interactive HLS Specification Browser
 * Main application logic
 */

// Global state
let currentCodec = 'vvc';
let syntaxData = {};
let semanticsData = {};
// connectionsData is declared in connection-graph.js
let currentStructure = null;
let currentParameter = null;
let currentSemanticsContext = null; // Syntax structure context for currently displayed semantics
let semanticsHistory = []; // History stack for back button

// Initialize application
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
    setupEventListeners();
});

/**
 * Initialize the application
 */
async function initializeApp() {
    // Load codec data
    await loadCodecData(currentCodec);

    // Populate syntax list
    populateSyntaxList();

    // Initialize connection tree after data is loaded
    if (typeof initConnectionTree === 'function') {
        initConnectionTree(semanticsData, connectionsData);
    }
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Codec selector
    document.getElementById('codecSelect').addEventListener('change', async (e) => {
        currentCodec = e.target.value;
        await loadCodecData(currentCodec);
        populateSyntaxList();
        clearDisplay();
        initConnectionTree(semanticsData, connectionsData);
    });

    // Search box
    document.getElementById('syntaxSearch').addEventListener('input', (e) => {
        filterSyntaxList(e.target.value);
    });

    // Tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            switchTab(e.target.closest('.tab-btn').dataset.tab);
        });
    });

    // Setup resize handles
    setupResizeHandles();
}

/**
 * Setup resize handles for panels
 */
function setupResizeHandles() {
    const sidebar = document.getElementById('sidebar');
    const detailsPanel = document.getElementById('detailsPanel');
    const mainContent = document.querySelector('.main-content');

    // Sidebar resize (right handle)
    const sidebarHandle = sidebar.querySelector('.resize-handle-right');
    let isResizingSidebar = false;
    let sidebarStartWidth = 0;
    let startX = 0;

    sidebarHandle.addEventListener('mousedown', (e) => {
        isResizingSidebar = true;
        sidebarStartWidth = sidebar.offsetWidth;
        startX = e.clientX;
        sidebarHandle.classList.add('resizing');
        document.body.style.cursor = 'col-resize';
        document.body.style.userSelect = 'none';
        e.preventDefault();
    });

    // Details panel resize (left handle)
    const detailsHandle = detailsPanel.querySelector('.resize-handle-left');
    let isResizingDetails = false;
    let detailsStartWidth = 0;

    detailsHandle.addEventListener('mousedown', (e) => {
        isResizingDetails = true;
        detailsStartWidth = detailsPanel.offsetWidth;
        startX = e.clientX;
        detailsHandle.classList.add('resizing');
        document.body.style.cursor = 'col-resize';
        document.body.style.userSelect = 'none';
        e.preventDefault();
    });

    // Mouse move handler
    document.addEventListener('mousemove', (e) => {
        if (isResizingSidebar) {
            const diff = e.clientX - startX;
            const newWidth = Math.max(250, Math.min(600, sidebarStartWidth + diff));
            sidebar.style.width = `${newWidth}px`;
            mainContent.style.gridTemplateColumns = `${newWidth}px 1fr 400px`;
        } else if (isResizingDetails) {
            const diff = startX - e.clientX;
            const newWidth = Math.max(300, Math.min(700, detailsStartWidth + diff));
            detailsPanel.style.width = `${newWidth}px`;
            const sidebarWidth = sidebar.offsetWidth;
            mainContent.style.gridTemplateColumns = `${sidebarWidth}px 1fr ${newWidth}px`;
        }
    });

    // Mouse up handler
    document.addEventListener('mouseup', () => {
        if (isResizingSidebar || isResizingDetails) {
            isResizingSidebar = false;
            isResizingDetails = false;
            sidebarHandle.classList.remove('resizing');
            detailsHandle.classList.remove('resizing');
            document.body.style.cursor = '';
            document.body.style.userSelect = '';
        }
    });
}

/**
 * Load codec data from JSON files
 */
async function loadCodecData(codec) {
    try {
        showLoading();

        // Load syntax data
        const syntaxResponse = await fetch(`data/${codec}/syntax.json`);
        if (syntaxResponse.ok) {
            syntaxData = await syntaxResponse.json();
        } else {
            console.warn(`Syntax data not found for ${codec}`);
            syntaxData = {};
        }

        // Load semantics data
        const semanticsResponse = await fetch(`data/${codec}/semantics.json`);
        if (semanticsResponse.ok) {
            semanticsData = await semanticsResponse.json();
        } else {
            console.warn(`Semantics data not found for ${codec}`);
            semanticsData = {};
        }

        // Load connections data
        const connectionsResponse = await fetch(`data/${codec}/connections.json`);
        if (connectionsResponse.ok) {
            connectionsData = await connectionsResponse.json();
        } else {
            console.warn(`Connections data not found for ${codec}`);
            connectionsData = {};
        }

        hideLoading();
    } catch (error) {
        console.error('Error loading codec data:', error);
        showError('Failed to load codec data. Make sure to run the processing script first.');
    }
}

/**
 * Populate syntax list sidebar
 */
function populateSyntaxList() {
    const listContainer = document.getElementById('syntaxList');

    if (Object.keys(syntaxData).length === 0) {
        listContainer.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-exclamation-circle"></i>
                <p>No syntax data available. Run the processing script first.</p>
            </div>
        `;
        return;
    }

    listContainer.innerHTML = '';

    // Sort structures by section number
    const structures = Object.entries(syntaxData).sort((a, b) => {
        return a[1].section.localeCompare(b[1].section);
    });

    structures.forEach(([name, structure]) => {
        const item = document.createElement('div');
        item.className = 'syntax-item';
        item.innerHTML = `
            <span class="syntax-item-section">${structure.section}</span>
            <span class="syntax-item-name">${name}</span>
        `;

        item.addEventListener('click', () => {
            selectSyntaxStructure(name);
        });

        listContainer.appendChild(item);
    });
}

/**
 * Filter syntax list based on search query
 */
function filterSyntaxList(query) {
    const items = document.querySelectorAll('.syntax-item');
    const lowerQuery = query.toLowerCase();

    items.forEach(item => {
        const name = item.querySelector('.syntax-item-name').textContent.toLowerCase();
        if (name.includes(lowerQuery)) {
            item.style.display = 'flex';
        } else {
            item.style.display = 'none';
        }
    });
}

/**
 * Select and display a syntax structure
 */
function selectSyntaxStructure(name) {
    currentStructure = name;
    const structure = syntaxData[name];

    // Update active state in sidebar
    document.querySelectorAll('.syntax-item').forEach(item => {
        item.classList.remove('active');
        if (item.querySelector('.syntax-item-name').textContent === name) {
            item.classList.add('active');
        }
    });

    // Display syntax structure
    displaySyntaxStructure(structure);
}

/**
 * Display syntax structure in main panel with C++ style indentation
 */
function displaySyntaxStructure(structure) {
    document.getElementById('syntaxTitle').textContent = structure.name;
    document.getElementById('syntaxSection').textContent = `Section ${structure.section}`;

    const contentContainer = document.getElementById('syntaxContent');
    contentContainer.innerHTML = '';

    // Add descriptor if available
    if (structure.descriptor) {
        const descriptor = document.createElement('p');
        descriptor.style.marginBottom = '1.5rem';
        descriptor.style.color = '#6c757d';
        descriptor.textContent = structure.descriptor;
        contentContainer.appendChild(descriptor);
    }

    // Create syntax code block with C++ style indentation
    const codeBlock = document.createElement('div');
    codeBlock.className = 'syntax-code-block';

    // Add function signature
    const signature = document.createElement('div');
    signature.className = 'syntax-line';
    signature.innerHTML = `<span class="syntax-function">${structure.name}( ) {</span>`;
    codeBlock.appendChild(signature);

    // Track indentation level and single-statement tracking
    let indentLevel = 1; // Start at 1 because we're inside the function
    let singleStatementDepth = []; // Stack to track single-statement control blocks

    // Process each syntax line
    structure.parameters.forEach((param, index) => {
        const line = document.createElement('div');
        line.className = 'syntax-line';

        const lineType = param.condition || 'other';
        let syntaxText = param.name;
        const descriptor = param.type;

        // Check for braces in the text itself
        const hasOpeningBrace = syntaxText.trim().endsWith('{');
        const hasClosingBrace = syntaxText.trim().startsWith('}');
        const isCloseBraceOnly = lineType === 'brace_close';

        // Check if we need to unindent from a single-statement block
        const isControlStatement = lineType === 'if_statement' || lineType === 'else_if_statement' ||
                                   lineType === 'else_statement' || lineType === 'for_loop' ||
                                   lineType === 'while_loop' || lineType === 'do_while';

        // Unindent if previous line was a single-statement control and this is not its body
        if (singleStatementDepth.length > 0 && !isControlStatement && !hasClosingBrace) {
            const lastDepth = singleStatementDepth[singleStatementDepth.length - 1];
            if (lastDepth === indentLevel - 1) {
                indentLevel--;
                singleStatementDepth.pop();
            }
        }

        // Adjust indent for closing braces
        if (hasClosingBrace || isCloseBraceOnly) {
            indentLevel = Math.max(0, indentLevel - 1);
            // Clear single-statement tracking when we hit a brace
            singleStatementDepth = singleStatementDepth.filter(d => d < indentLevel);
        }

        // Calculate indentation (4 spaces per level)
        const indent = '    '.repeat(indentLevel);

        // Build line content based on type
        let lineHTML = '';

        if (isCloseBraceOnly) {
            lineHTML = `<span class="syntax-brace">}</span>`;
        } else if (hasClosingBrace && syntaxText.includes('else')) {
            // "} else" or "} else if(...)"
            const parts = syntaxText.split('else');
            if (parts[1] && parts[1].trim().startsWith('if')) {
                const condition = parts[1].replace(/^if\s*\(\s*/, '').replace(/\s*\).*$/, '');
                lineHTML = `<span class="syntax-brace">}</span> <span class="syntax-keyword">else if</span><span class="syntax-paren">(</span> ${highlightCondition(condition)} <span class="syntax-paren">)</span>`;
                if (syntaxText.trim().endsWith('{')) {
                    lineHTML += ` <span class="syntax-brace">{</span>`;
                }
            } else {
                lineHTML = `<span class="syntax-brace">}</span> <span class="syntax-keyword">else</span>`;
                if (syntaxText.trim().endsWith('{')) {
                    lineHTML += ` <span class="syntax-brace">{</span>`;
                }
            }
        } else if (lineType === 'if_statement' || lineType === 'else_if_statement') {
            let condition = syntaxText;
            const keyword = lineType === 'if_statement' ? 'if' : 'else if';
            condition = condition.replace(/^(if|else if)\s*\(/, '').replace(/\)\s*\{?\s*$/, '');
            lineHTML = `<span class="syntax-keyword">${keyword}</span><span class="syntax-paren">(</span> ${highlightCondition(condition)} <span class="syntax-paren">)</span>`;
            if (hasOpeningBrace) {
                lineHTML += ` <span class="syntax-brace">{</span>`;
            }
        } else if (lineType === 'else_statement') {
            lineHTML = `<span class="syntax-keyword">else</span>`;
            if (hasOpeningBrace) {
                lineHTML += ` <span class="syntax-brace">{</span>`;
            }
        } else if (lineType === 'for_loop') {
            let forContent = syntaxText.replace(/^for\s*\(/, '').replace(/\)\s*\{?\s*$/, '');
            lineHTML = `<span class="syntax-keyword">for</span><span class="syntax-paren">(</span> ${highlightCondition(forContent)} <span class="syntax-paren">)</span>`;
            if (hasOpeningBrace) {
                lineHTML += ` <span class="syntax-brace">{</span>`;
            }
        } else if (lineType === 'while_loop') {
            let condition = syntaxText.replace(/^while\s*\(/, '').replace(/\)\s*\{?\s*$/, '');
            lineHTML = `<span class="syntax-keyword">while</span><span class="syntax-paren">(</span> ${highlightCondition(condition)} <span class="syntax-paren">)</span>`;
            if (hasOpeningBrace) {
                lineHTML += ` <span class="syntax-brace">{</span>`;
            }
        } else if (lineType === 'do_while') {
            lineHTML = `<span class="syntax-keyword">do</span>`;
            if (hasOpeningBrace) {
                lineHTML += ` <span class="syntax-brace">{</span>`;
            }
        } else if (lineType === 'brace_open') {
            lineHTML = `<span class="syntax-brace">{</span>`;
        } else if (lineType === 'function_call') {
            // Updated regex to handle spaces before parentheses (e.g., "slice_header( )")
            const funcMatch = syntaxText.match(/^([a-zA-Z_][a-zA-Z0-9_]*)\s*\(\s*(.*?)\s*\)\s*$/);
            if (funcMatch) {
                const funcName = funcMatch[1];
                const args = funcMatch[2].trim();
                lineHTML = `<span class="syntax-function-call clickable-function" data-function="${funcName}" onclick="navigateToSyntaxStructure('${funcName}')" title="Click to view ${funcName} syntax">${funcName}</span><span class="syntax-paren">(</span>${args ? ' ' + highlightCondition(args) + ' ' : ' '}<span class="syntax-paren">)</span>`;
            } else {
                lineHTML = `<span class="syntax-function-call">${escapeHtml(syntaxText)}</span>`;
            }
        } else if (lineType === 'parameter') {
            const paramName = syntaxText;
            lineHTML = `<span class="syntax-param-name" data-param="${paramName}">${escapeHtml(paramName)}</span>`;
            if (descriptor) {
                const padding = Math.max(1, 50 - paramName.length - indent.length);
                lineHTML += ' '.repeat(padding) + `<span class="syntax-descriptor">${escapeHtml(descriptor)}</span>`;
            }
        } else {
            lineHTML = `<span class="syntax-other">${escapeHtml(syntaxText)}</span>`;
            if (descriptor) {
                lineHTML += ` <span class="syntax-descriptor">${escapeHtml(descriptor)}</span>`;
            }
        }

        line.innerHTML = `<span class="syntax-indent">${indent}</span>${lineHTML}`;
        codeBlock.appendChild(line);

        // Adjust indent for NEXT line
        if (hasOpeningBrace || lineType === 'brace_open') {
            // Opening brace - increase indent
            indentLevel++;
        } else if (isControlStatement && !hasOpeningBrace) {
            // Control statement without brace - indent next line only
            const nextParam = structure.parameters[index + 1];
            if (nextParam && nextParam.condition !== 'brace_open' && !nextParam.name.trim().startsWith('}')) {
                singleStatementDepth.push(indentLevel);
                indentLevel++;
            }
        }
    });

    // Add closing brace for function
    const closingBrace = document.createElement('div');
    closingBrace.className = 'syntax-line';
    closingBrace.innerHTML = `<span class="syntax-brace">}</span>`;
    codeBlock.appendChild(closingBrace);

    contentContainer.appendChild(codeBlock);

    // Add click handlers to parameter names
    contentContainer.querySelectorAll('.syntax-param-name, .syntax-function-call').forEach(elem => {
        elem.style.cursor = 'pointer';
        elem.addEventListener('click', (e) => {
            const paramName = e.target.dataset.param;
            if (paramName) {
                selectParameter(paramName);
            }
        });
    });
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Highlight parameter names in conditions
 */
function highlightCondition(text) {
    // Highlight parameter names (basic pattern matching)
    return text.replace(/\b([a-z_][a-z0-9_]*)\b/gi, '<span class="syntax-param-ref">$1</span>');
}

/**
 * Select and display parameter details
 * Connections are now shown inline in the semantics modal
 */
function selectParameter(paramName) {
    currentParameter = paramName;

    // Display semantics with current syntax structure context
    console.log('[selectParameter] Parameter:', paramName, 'Syntax Context:', currentStructure);
    displaySemantics(paramName, true, currentStructure);
}

/**
 * Display parameter semantics
 * @param {string} paramName - The parameter name to display semantics for
 * @param {boolean} pushToHistory - Whether to push current param to history (default true)
 * @param {string} syntaxContext - The syntax structure name this parameter belongs to (optional)
 */
function displaySemantics(paramName, pushToHistory = true, syntaxContext = null) {
    // IMPORTANT: Clear any previous AI analysis when switching parameters
    const aiContainer = document.getElementById('aiAnalysisContainer');
    if (aiContainer) {
        aiContainer.style.display = 'none';
        const aiContent = document.getElementById('aiAnalysisContent');
        if (aiContent) {
            aiContent.innerHTML = '';
        }
    }

    // Store the syntax context for AI analysis
    // If no context provided, preserve the current one (for related parameter navigation)
    console.log('[displaySemantics] Param:', paramName, 'New Context:', syntaxContext, 'Current Context Before:', currentSemanticsContext);
    if (syntaxContext !== null) {
        currentSemanticsContext = syntaxContext;
    }
    console.log('[displaySemantics] Current Context After:', currentSemanticsContext);
    // If currentSemanticsContext is still null, keep it null (no context available)

    // Get current parameter from modal title if we're pushing to history
    if (pushToHistory) {
        const currentParam = document.getElementById('semanticsModalTitle')?.textContent;
        if (currentParam && currentParam !== 'Semantics' && currentParam !== paramName) {
            // Only push if modal is already showing a parameter
            const modal = document.getElementById('semanticsModal');
            if (modal && modal.classList.contains('active')) {
                semanticsHistory.push(currentParam);
            }
        }
    }

    // Try exact match first
    let info = semanticsData[paramName];
    let matchType = 'exact';
    let displayName = paramName;

    // If not found, try to find a similar parameter
    if (!info) {
        // Remove array indices like [i], [ NumBytes++ ], etc.
        const baseName = paramName.replace(/\s*\[.*?\]\s*/g, '').trim();
        info = semanticsData[baseName];
        if (info) {
            matchType = 'base';
            displayName = baseName;
        }
    }

    // Try removing comments
    if (!info) {
        const noComments = paramName.replace(/\/\*.*?\*\//g, '').trim();
        info = semanticsData[noComments];
        if (info) {
            matchType = 'no-comment';
            displayName = noComments;
        }
    }

    // Try removing common prefixes (e.g., pps_conf_win_left_offset -> conf_win_left_offset)
    if (!info) {
        const prefixes = ['sps_', 'pps_', 'vps_', 'aps_', 'ph_', 'sh_', 'dci_', 'opi_'];
        for (const prefix of prefixes) {
            if (paramName.startsWith(prefix)) {
                const withoutPrefix = paramName.substring(prefix.length);
                info = semanticsData[withoutPrefix];
                if (info) {
                    matchType = 'inherited';
                    displayName = withoutPrefix;
                    break;
                }
            }
        }
    }

    // Try searching in related parameters only (removed "mentioned in definition" check as it's too broad)
    if (!info) {
        // Search for parameters where this param is in related_parameters array
        for (const [key, value] of Object.entries(semanticsData)) {
            // Check if in related parameters
            if (value.related_parameters && value.related_parameters.includes(paramName)) {
                info = value;
                matchType = 'related';
                displayName = key + ' (related to ' + paramName + ')';
                break;
            }
        }
    }

    // Try finding suffix match (e.g., search for parameters ending with the same suffix)
    if (!info) {
        const parts = paramName.split('_');
        if (parts.length > 2) {
            // Try last 2-3 words
            const suffix2 = parts.slice(-2).join('_');
            const suffix3 = parts.slice(-3).join('_');

            for (const key in semanticsData) {
                if (key.endsWith(suffix3) || key.endsWith(suffix2)) {
                    info = semanticsData[key];
                    matchType = 'suffix';
                    displayName = key;
                    break;
                }
            }
        }
    }

    // Show popup modal
    const modal = document.getElementById('semanticsModal');
    const modalTitle = document.getElementById('semanticsModalTitle');
    const modalContent = document.getElementById('semanticsModalContent');

    if (!info) {
        modalTitle.textContent = 'Parameter Information';
        modalContent.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-info-circle"></i>
                <p><strong>No semantic information available</strong></p>
                <p style="margin-top: 1rem; font-size: 0.9rem; color: #6c757d; line-height: 1.6;">
                    The parameter <code style="background: #f8f9fa; padding: 0.2rem 0.5rem; border-radius: 3px;">${escapeHtml(paramName)}</code>
                    may be defined elsewhere or inherited from a parent structure.
                </p>
                <p style="margin-top: 0.5rem; font-size: 0.85rem; color: #999;">
                    <i class="fas fa-lightbulb"></i> Try clicking on other parameters to view their semantics.
                </p>
            </div>
        `;
        modal.classList.add('active');
        return;
    }

    modalTitle.textContent = matchType === 'related' ? paramName : displayName;

    // Add syntax context indicator to modal header if available
    const modalHeader = modalTitle.parentElement;
    let contextIndicator = modalHeader.querySelector('.syntax-context-indicator');
    if (currentSemanticsContext) {
        if (!contextIndicator) {
            contextIndicator = document.createElement('div');
            contextIndicator.className = 'syntax-context-indicator';
            modalHeader.appendChild(contextIndicator);
        }
        contextIndicator.textContent = `in ${currentSemanticsContext}`;
        contextIndicator.style.display = 'block';
    } else if (contextIndicator) {
        contextIndicator.style.display = 'none';
    }

    let html = `
        <div class="semantic-content">`;

    // Add note if found through related match
    if (matchType === 'related') {
        html += `
            <div style="background: #d1ecf1; border-left: 4px solid #17a2b8; padding: 0.75rem 1rem; margin-bottom: 1rem; border-radius: 4px;">
                <small style="color: #0c5460;"><i class="fas fa-link"></i> <strong>Note:</strong>
                <code>${paramName}</code> is related to <code>${displayName.split(' (')[0]}</code></small>
            </div>
        `;
    } else if (matchType === 'inherited') {
        html += `
            <div style="background: #d4edda; border-left: 4px solid #28a745; padding: 0.75rem 1rem; margin-bottom: 1rem; border-radius: 4px;">
                <small style="color: #155724;"><i class="fas fa-share"></i> <strong>Note:</strong>
                This parameter inherits from <code>${displayName}</code></small>
            </div>
        `;
    }

    html += `
            <div class="semantic-header">
                <div class="semantic-param-name">${matchType === 'mentioned' || matchType === 'related' ? displayName.split(' (')[0] : displayName}</div>
                <div class="semantic-section-ref">Section ${info.section}</div>
            </div>

            <div class="semantic-definition">
                ${info.definition}
            </div>
    `;

    // Add constraints if available
    if (info.constraints && Object.keys(info.constraints).length > 0) {
        html += `
            <div class="semantic-constraints">
                <h4><i class="fas fa-ruler"></i> Constraints</h4>
        `;

        if (info.constraints.range) {
            html += `
                <div class="constraint-item">
                    <i class="fas fa-arrows-alt-h"></i>
                    <div>
                        <strong>Range:</strong> ${info.constraints.range}
                    </div>
                </div>
            `;
        }

        if (info.constraints.values) {
            html += `
                <div class="constraint-item">
                    <i class="fas fa-list"></i>
                    <div>
                        <strong>Values:</strong>
                        <ul style="margin-top: 0.5rem; margin-left: 1.5rem;">
            `;
            for (const [value, desc] of Object.entries(info.constraints.values)) {
                html += `<li>${value}: ${desc}</li>`;
            }
            html += `
                        </ul>
                    </div>
                </div>
            `;
        }

        html += `</div>`;
    }

    // Add related parameters if available
    if (info.related_parameters && info.related_parameters.length > 0) {
        html += `
            <div class="semantic-constraints">
                <h4><i class="fas fa-link"></i> Related Parameters</h4>
        `;
        info.related_parameters.forEach(relParam => {
            html += `
                <div class="constraint-item">
                    <i class="fas fa-chevron-right"></i>
                    <div>
                        <span class="param-name" onclick="displaySemantics('${relParam}', true);" style="cursor: pointer; color: #667eea;">
                            ${relParam}
                        </span>
                    </div>
                </div>
            `;
        });
        html += `</div>`;
    }

    html += `</div>`;

    modalContent.innerHTML = html;

    // Add connections visualization below semantics (async)
    addConnectionsToModal(paramName);

    // Update back button visibility
    const backBtn = document.getElementById('semanticsBackBtn');
    if (backBtn) {
        backBtn.style.display = semanticsHistory.length > 0 ? 'block' : 'none';
    }

    modal.classList.add('active');
}

/**
 * Add connections visualization to semantics modal
 */
async function addConnectionsToModal(paramName) {
    const modalContent = document.getElementById('semanticsModalContent');

    // Load connections data from the connection-graph.js module
    await loadConnectionsData();

    if (!connectionsData || !connectionsData[paramName]) {
        // No connections available
        return;
    }

    const connections = connectionsData[paramName];

    // Build connection tree structure
    const upstreamConnections = [];
    const downstreamConnections = [];

    // Upstream: Dependencies (what this parameter depends on)
    if (connections.dependencies && connections.dependencies.length > 0) {
        connections.dependencies.forEach(dep => {
            upstreamConnections.push({
                name: dep.parameter,
                type: 'dependency',
                context: dep.context || 'Depends on',
                strength: dep.strength || 0.8
            });
        });
    }

    // Downstream: References (what depends on/references this parameter)
    if (connections.references && connections.references.length > 0) {
        connections.references.forEach(ref => {
            downstreamConnections.push({
                name: ref.parameter,
                type: 'reference',
                context: ref.context || 'Referenced by',
                strength: ref.strength || 0.8
            });
        });
    }

    // Related concepts (shown separately, not in tree)
    const relatedConnections = connections.related_concepts || [];

    // Create tree HTML
    const connectionsHTML = `
        <div class="semantic-connections">
            <div class="connections-header-inline">
                <h4><i class="fas fa-sitemap"></i> Parameter Connections</h4>
                <div class="connection-legend">
                    <span class="legend-item upstream"><i class="fas fa-arrow-up"></i> Upstream (Dependencies)</span>
                    <span class="legend-item downstream"><i class="fas fa-arrow-down"></i> Downstream (References)</span>
                </div>
            </div>
            <div id="connectionTreeContainer" class="connection-tree-container">
                ${buildConnectionTree(paramName, upstreamConnections, downstreamConnections, relatedConnections)}
            </div>
        </div>
    `;

    // Append to existing content
    modalContent.innerHTML += connectionsHTML;
}

/**
 * Build HTML for connection tree
 */
function buildConnectionTree(rootParam, upstream, downstream, related) {
    let html = '<div class="connection-tree">';

    // Upstream connections (Dependencies)
    if (upstream.length > 0) {
        html += '<div class="tree-section upstream-section">';
        html += '<div class="section-label"><i class="fas fa-level-up-alt"></i> Upstream Dependencies</div>';
        html += '<div class="tree-nodes">';
        upstream.forEach(conn => {
            html += `
                <div class="tree-node upstream-node clickable"
                     onclick="navigateToParameter('${conn.name}')"
                     title="${conn.context}">
                    <i class="fas fa-arrow-right"></i>
                    <span class="node-name">${conn.name}</span>
                    <span class="node-context">${conn.context}</span>
                </div>
            `;
        });
        html += '</div>';
        html += '</div>';

        // Connection line
        html += '<div class="tree-connector upstream-connector"></div>';
    }

    // Root parameter (current)
    html += `
        <div class="tree-section root-section">
            <div class="tree-node root-node">
                <i class="fas fa-circle"></i>
                <span class="node-name">${rootParam}</span>
                <span class="node-badge">Current Parameter</span>
            </div>
        </div>
    `;

    // Downstream connections (References)
    if (downstream.length > 0) {
        // Connection line
        html += '<div class="tree-connector downstream-connector"></div>';

        html += '<div class="tree-section downstream-section">';
        html += '<div class="section-label"><i class="fas fa-level-down-alt"></i> Downstream References</div>';
        html += '<div class="tree-nodes">';
        downstream.forEach(conn => {
            html += `
                <div class="tree-node downstream-node clickable"
                     onclick="navigateToParameter('${conn.name}')"
                     title="${conn.context}">
                    <i class="fas fa-arrow-right"></i>
                    <span class="node-name">${conn.name}</span>
                    <span class="node-context">${conn.context}</span>
                </div>
            `;
        });
        html += '</div>';
        html += '</div>';
    }

    // Related concepts (if any)
    if (related.length > 0) {
        html += '<div class="tree-section related-section">';
        html += '<div class="section-label"><i class="fas fa-link"></i> Related Concepts</div>';
        html += '<div class="tree-nodes related-nodes">';
        related.forEach(conn => {
            html += `
                <div class="tree-node related-node clickable"
                     onclick="navigateToParameter('${conn.parameter}')"
                     title="${conn.context || 'Related concept'}">
                    <i class="fas fa-arrow-right"></i>
                    <span class="node-name">${conn.parameter}</span>
                    <span class="node-context">${conn.context || 'Related'}</span>
                </div>
            `;
        });
        html += '</div>';
        html += '</div>';
    }

    // Show message if no connections
    if (upstream.length === 0 && downstream.length === 0 && related.length === 0) {
        html += '<div class="empty-state"><p>No connections found for this parameter</p></div>';
    }

    html += '</div>';
    return html;
}

/**
 * Navigate to a parameter from connection tree
 */
function navigateToParameter(paramName) {
    console.log('[navigateToParameter] Navigating to:', paramName, 'Context:', currentSemanticsContext);
    // Display semantics with history tracking
    displaySemantics(paramName, true);
}

/**
 * Close semantics popup modal
 */
function closeSemanticsModal() {
    const modal = document.getElementById('semanticsModal');
    modal.classList.remove('active');
    // Clear history and context when closing modal
    semanticsHistory = [];
    currentSemanticsContext = null;
}

/**
 * Go back to previous parameter in semantics history
 */
function goBackSemantics() {
    if (semanticsHistory.length > 0) {
        const previousParam = semanticsHistory.pop();
        // Display without pushing to history (false parameter)
        displaySemantics(previousParam, false);
    }
}

/**
 * Logout and perform hard refresh
 * Clears all session storage, local storage, cookies, and forces cache reload
 */
function logout() {
    // Clear all session storage
    sessionStorage.clear();

    // Clear all local storage
    localStorage.clear();

    // Clear all cookies
    document.cookie.split(";").forEach(function(c) {
        document.cookie = c.replace(/^ +/, "").replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/");
    });

    // Force a hard refresh by reloading with cache bypass
    // This clears browser cache for this page
    window.location.href = window.location.href.split('?')[0] + '?t=' + new Date().getTime();
}

// Add click-outside-to-close for semantics modal
document.getElementById('semanticsModal')?.addEventListener('click', (e) => {
    if (e.target.id === 'semanticsModal') {
        closeSemanticsModal();
    }
});

/**
 * Navigate to a syntax structure by function name
 */
function navigateToSyntaxStructure(funcName) {
    // Close semantics modal if open
    closeSemanticsModal();

    // Try to find matching syntax structure
    // First try exact match
    let matchedStructure = null;
    let matchedKey = null;

    // Iterate over object values
    for (const [key, structure] of Object.entries(syntaxData)) {
        // Try exact match
        if (structure.name === funcName || key === funcName) {
            matchedStructure = structure;
            matchedKey = key;
            break;
        }

        // Try with parentheses
        if (structure.name === funcName + '()' || key === funcName + '()') {
            matchedStructure = structure;
            matchedKey = key;
            break;
        }

        // Try converting underscores to spaces or vice versa
        const funcWithSpaces = funcName.replace(/_/g, ' ');
        const funcWithUnderscores = funcName.replace(/ /g, '_');

        if (structure.name === funcWithSpaces || structure.name === funcWithUnderscores ||
            key === funcWithSpaces || key === funcWithUnderscores) {
            matchedStructure = structure;
            matchedKey = key;
            break;
        }

        // Try case-insensitive match
        if (structure.name && structure.name.toLowerCase() === funcName.toLowerCase()) {
            matchedStructure = structure;
            matchedKey = key;
            break;
        }
    }

    if (matchedStructure && matchedKey) {
        // Display the syntax structure using the key
        selectSyntaxStructure(matchedKey);

        // Highlight in sidebar and scroll to it
        const syntaxItems = document.querySelectorAll('.syntax-item');
        syntaxItems.forEach(item => {
            if (item.textContent.trim() === matchedStructure.name || item.textContent.trim() === matchedKey) {
                item.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        });
    } else {
        // If not found, show a message
        console.warn(`Syntax structure "${funcName}" not found`);
    }
}

/**
 * displayConnections function is now in connection-graph.js
 */

/**
 * Switch between tabs
 */
function switchTab(tabName) {
    // Update button states
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.tab === tabName) {
            btn.classList.add('active');
        }
    });

    // Update content visibility
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });

    if (tabName === 'semantics') {
        document.getElementById('semanticsTab').classList.add('active');
    } else if (tabName === 'connections') {
        document.getElementById('connectionsTab').classList.add('active');
    }
}

/**
 * Show connection graph in modal
 */
function showConnectionGraph(paramName) {
    const modal = document.getElementById('graphModal');
    modal.classList.add('active');

    // Render D3 graph
    renderConnectionGraph(paramName);
}

/**
 * Close graph modal
 */
function closeGraphModal() {
    const modal = document.getElementById('graphModal');
    modal.classList.remove('active');
}

/**
 * Render connection graph using D3.js
 */
function renderConnectionGraph(paramName) {
    const container = document.getElementById('connectionGraph');
    container.innerHTML = '';

    const connections = connectionsData[paramName];
    if (!connections) {
        container.innerHTML = '<p>No connection data available.</p>';
        return;
    }

    // Build nodes and links for D3
    const nodes = [{ id: paramName, group: 0, main: true }];
    const links = [];

    // Add referenced nodes
    if (connections.references) {
        connections.references.forEach(ref => {
            if (!nodes.find(n => n.id === ref.parameter)) {
                nodes.push({ id: ref.parameter, group: 1 });
            }
            links.push({
                source: paramName,
                target: ref.parameter,
                value: ref.strength,
                type: 'reference'
            });
        });
    }

    // Add dependent nodes
    if (connections.dependencies) {
        connections.dependencies.forEach(dep => {
            if (!nodes.find(n => n.id === dep.parameter)) {
                nodes.push({ id: dep.parameter, group: 2 });
            }
            links.push({
                source: dep.parameter,
                target: paramName,
                value: dep.strength,
                type: 'dependency'
            });
        });
    }

    // Add related nodes
    if (connections.related_concepts) {
        connections.related_concepts.forEach(rel => {
            if (!nodes.find(n => n.id === rel.parameter)) {
                nodes.push({ id: rel.parameter, group: 3 });
            }
            links.push({
                source: paramName,
                target: rel.parameter,
                value: rel.strength,
                type: 'related',
                dashed: true
            });
        });
    }

    // D3 force simulation
    const width = container.offsetWidth;
    const height = 500;

    const svg = d3.select(container)
        .append('svg')
        .attr('width', width)
        .attr('height', height);

    const simulation = d3.forceSimulation(nodes)
        .force('link', d3.forceLink(links).id(d => d.id).distance(100))
        .force('charge', d3.forceManyBody().strength(-300))
        .force('center', d3.forceCenter(width / 2, height / 2));

    // Draw links
    const link = svg.append('g')
        .selectAll('line')
        .data(links)
        .enter().append('line')
        .attr('stroke', d => d.type === 'reference' ? '#667eea' : d.type === 'dependency' ? '#e83e8c' : '#999')
        .attr('stroke-width', d => Math.sqrt(d.value) * 2)
        .attr('stroke-dasharray', d => d.dashed ? '5,5' : '0');

    // Draw nodes
    const node = svg.append('g')
        .selectAll('circle')
        .data(nodes)
        .enter().append('circle')
        .attr('r', d => d.main ? 12 : 8)
        .attr('fill', d => {
            if (d.main) return '#667eea';
            if (d.group === 1) return '#4c9aff';
            if (d.group === 2) return '#e83e8c';
            return '#6c757d';
        })
        .call(d3.drag()
            .on('start', dragstarted)
            .on('drag', dragged)
            .on('end', dragended));

    // Add labels
    const label = svg.append('g')
        .selectAll('text')
        .data(nodes)
        .enter().append('text')
        .text(d => d.id)
        .attr('font-size', d => d.main ? 12 : 10)
        .attr('font-weight', d => d.main ? 'bold' : 'normal')
        .attr('dx', 15)
        .attr('dy', 4)
        .style('pointer-events', 'none');

    simulation.on('tick', () => {
        link
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);

        node
            .attr('cx', d => d.x)
            .attr('cy', d => d.y);

        label
            .attr('x', d => d.x)
            .attr('y', d => d.y);
    });

    function dragstarted(event, d) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }

    function dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }

    function dragended(event, d) {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }
}

/**
 * Utility functions
 */
function showLoading() {
    document.getElementById('syntaxList').innerHTML = '<div class="loading"><i class="fas fa-spinner fa-spin"></i> Loading...</div>';
}

function hideLoading() {
    // Loading will be replaced by populated list
}

function clearDisplay() {
    document.getElementById('syntaxContent').innerHTML = `
        <div class="welcome-message">
            <i class="fas fa-hand-pointer"></i>
            <p>Click on a syntax structure from the left panel to view its details</p>
        </div>
    `;

    document.getElementById('semanticsTab').innerHTML = `
        <div class="empty-state">
            <i class="fas fa-info-circle"></i>
            <p>Click on a parameter to view its semantics</p>
        </div>
    `;

    document.getElementById('connectionsTab').innerHTML = `
        <div class="empty-state">
            <i class="fas fa-info-circle"></i>
            <p>Click on a parameter to view its connections</p>
        </div>
    `;
}

function showError(message) {
    document.getElementById('syntaxList').innerHTML = `
        <div class="empty-state">
            <i class="fas fa-exclamation-triangle"></i>
            <p>${message}</p>
        </div>
    `;
}

/**
 * AI Analysis functions
 */
let currentAiParameter = null;

async function getApiKey() {
    // Check if API key is stored in sessionStorage
    let apiKey = sessionStorage.getItem('claudeApiKey');

    if (!apiKey) {
        // Try to fetch from local config file first (for local development)
        try {
            const configResponse = await fetch('config.json');
            if (configResponse.ok) {
                const config = await configResponse.json();
                apiKey = config.ANTHROPIC_API_KEY;
                if (apiKey && apiKey.startsWith('sk-ant-')) {
                    sessionStorage.setItem('claudeApiKey', apiKey);
                    console.log('Using API key from config.json');
                    return apiKey;
                }
            }
        } catch (e) {
            // Config file doesn't exist (GitHub Pages deployment) - continue to prompt
            console.log('No config.json found, prompting for API key');
        }

        // Prompt user for API key (for GitHub Pages deployment)
        apiKey = prompt('Please enter your Claude API key (starts with sk-ant-...):\n\nYour key will be stored for this session only and never sent to any server except Anthropic\'s API.');

        if (apiKey && apiKey.startsWith('sk-ant-')) {
            sessionStorage.setItem('claudeApiKey', apiKey);
        } else {
            return null;
        }
    }

    return apiKey;
}

// AI Analysis Cache Functions
function getAiCacheKey(paramName, syntaxContext = '') {
    // Include syntax context to make cache specific to each syntax structure
    const contextKey = syntaxContext ? `_${syntaxContext}` : '';
    return `ai_analysis_${currentCodec}${contextKey}_${paramName}`;
}

function loadCachedAnalysis(paramName, syntaxContext = '') {
    const cacheKey = getAiCacheKey(paramName, syntaxContext);
    const cached = localStorage.getItem(cacheKey);
    if (cached) {
        try {
            return JSON.parse(cached);
        } catch (e) {
            console.error('Error parsing cached analysis:', e);
            return null;
        }
    }
    return null;
}

function saveCachedAnalysis(paramName, syntaxContext, explanation) {
    const cacheKey = getAiCacheKey(paramName, syntaxContext);
    const cacheData = {
        explanation: explanation,
        timestamp: new Date().toISOString(),
        codec: currentCodec,
        syntaxContext: syntaxContext
    };
    console.log('[saveCachedAnalysis] Saving cache with key:', cacheKey, 'Context:', syntaxContext);
    try {
        localStorage.setItem(cacheKey, JSON.stringify(cacheData));
    } catch (e) {
        console.error('Error saving to cache:', e);
    }
}

async function aiExplainParameter(forceRefresh = false) {
    const paramName = document.getElementById('semanticsModalTitle').textContent;

    if (!paramName || paramName === 'Semantics') {
        alert('Please select a parameter first');
        return;
    }

    currentAiParameter = paramName;

    // Show AI analysis container
    const aiContainer = document.getElementById('aiAnalysisContainer');
    const aiContent = document.getElementById('aiAnalysisContent');

    aiContainer.style.display = 'block';

    // Show loading state early to give user feedback
    aiContent.innerHTML = '<div class="ai-analysis-loading"><i class="fas fa-robot fa-spin"></i><p>Analyzing parameter...</p></div>';

    // Get parameter semantics and syntax context
    const semantics = semanticsData[paramName] || {};
    const definition = semantics.definition || 'No definition available';
    const constraints = semantics.constraints || [];
    const relatedParams = semantics.related_parameters || [];

    // Use the current semantics context (which syntax structure the user is viewing)
    const syntaxContext = currentSemanticsContext || '';
    console.log('[aiExplainParameter] Param:', paramName, 'Syntax Context:', syntaxContext, 'Force Refresh:', forceRefresh);

    // Check cache first (unless force refresh) - now syntax-specific
    if (!forceRefresh) {
        const cached = loadCachedAnalysis(paramName, syntaxContext);
        console.log('[aiExplainParameter] Cache lookup:', cached ? 'HIT' : 'MISS', 'Cache Key:', getAiCacheKey(paramName, syntaxContext));
        if (cached) {
            console.log('[aiExplainParameter] Using cached analysis from context:', cached.syntaxContext);
            displayAiAnalysis(cached.explanation, cached.timestamp, true, cached.syntaxContext);
            return;
        }
    }

    // Scroll to AI analysis
    aiContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

    try {

        // Build prompt for Claude
        const prompt = `You are an expert in H.266/VVC video codec specification. Please provide a clear, easy-to-understand explanation of the following parameter for someone learning about VVC.

Parameter: ${paramName}
${syntaxContext ? `Context: This parameter appears in the "${syntaxContext}" syntax structure.` : ''}

Specification Definition: ${definition}

Constraints: ${constraints.length > 0 ? constraints.join(', ') : 'None specified'}

Related Parameters: ${relatedParams.length > 0 ? relatedParams.join(', ') : 'None specified'}

Please explain:
1. What this parameter does in simple terms
2. ${syntaxContext ? `How it's specifically used in the ${syntaxContext} context` : 'When and why it\'s used in video encoding/decoding'}
3. Its practical impact on video quality or bitstream
4. How it relates to other VVC features (if applicable)

Keep the explanation concise (3-5 paragraphs) and accessible.`;

        // Call Claude API via local proxy server (same port as web server)
        const response = await fetch('/api/claude', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                model: 'claude-sonnet-4-5-20250929',
                max_tokens: 1024,
                messages: [{
                    role: 'user',
                    content: prompt
                }]
            })
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || `API error: ${response.status}`);
        }

        const data = await response.json();
        const explanation = data.content[0].text;

        // Save to cache with syntax context
        saveCachedAnalysis(paramName, syntaxContext, explanation);

        // Display the AI analysis
        displayAiAnalysis(explanation, new Date().toISOString(), false, syntaxContext);

    } catch (error) {
        console.error('AI analysis error:', error);
        aiContent.innerHTML = `
            <div class="ai-analysis-error">
                <strong>Error:</strong> ${error.message}
                <br><br>
                <small>Make sure the proxy server is running: python server/proxy.py</small>
            </div>
        `;
    }
}

function displayAiAnalysis(explanation, timestamp, isFromCache, syntaxContext = '') {
    const aiContent = document.getElementById('aiAnalysisContent');

    // Convert markdown-style formatting to HTML
    let html = explanation
        .replace(/\n\n/g, '</p><p>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`(.*?)`/g, '<code>$1</code>');

    // Wrap in paragraph tags if not already
    if (!html.startsWith('<p>')) {
        html = '<p>' + html + '</p>';
    }

    // Handle numbered lists
    html = html.replace(/(\d+)\.\s+/g, '<br>$1. ');

    // Add cache status and re-run button
    const cacheDate = new Date(timestamp);
    const formattedDate = cacheDate.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });

    const cacheStatus = isFromCache
        ? `<span class="cache-badge cache-hit"><i class="fas fa-check-circle"></i> Loaded from cache</span>`
        : `<span class="cache-badge cache-new"><i class="fas fa-sparkles"></i> Freshly generated</span>`;

    const contextBadge = syntaxContext
        ? `<span class="syntax-context-badge"><i class="fas fa-code"></i> ${syntaxContext}</span>`
        : '';

    const rerunButton = `
        <button class="btn-rerun-analysis" onclick="aiExplainParameter(true)" title="Re-run AI analysis">
            <i class="fas fa-sync-alt"></i> Re-run Analysis
        </button>
    `;

    aiContent.innerHTML = `
        <div class="ai-analysis-header">
            ${cacheStatus}
            ${contextBadge}
            <span class="analysis-timestamp">${formattedDate}</span>
            ${rerunButton}
        </div>
        <div class="ai-analysis-text">
            ${html}
        </div>
    `;
}

function closeAiAnalysis() {
    const aiContainer = document.getElementById('aiAnalysisContainer');
    aiContainer.style.display = 'none';
    currentAiParameter = null;
}
