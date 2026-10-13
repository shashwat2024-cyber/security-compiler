const $ = (id) => document.getElementById(id);

const sourceEditor = $("sourceCode");
const analyzeButton = $("analyzeButton");
const sampleButton = $("sampleButton");
const results = $("results");
const errorPanel = $("errorPanel");

let latestData = null;

const sampleCode = `void main() {
    char buffer[8];
    input = read_input();
    copy = input;
    strcpy(buffer, copy);
}`;

function element(tag, text = "", className = "") {
    const node = document.createElement(tag);
    node.textContent = text;

    if (className) {
        node.className = className;
    }

    return node;
}

function updateCharacterCount() {
    $("charCount").textContent =
        `${sourceEditor.value.length} characters`;
}

function showError(message) {
    errorPanel.textContent = message;
    errorPanel.classList.remove("hidden");
    results.classList.add("hidden");
}

function hideError() {
    errorPanel.textContent = "";
    errorPanel.classList.add("hidden");
}

function showTab(name) {
    document.querySelectorAll(".tab").forEach((button) => {
        const active = button.dataset.tab === name;

        button.classList.toggle("active", active);
        button.setAttribute("aria-selected", String(active));
    });

    document.querySelectorAll(".tab-content").forEach((panel) => {
        panel.classList.toggle("hidden", panel.id !== `tab-${name}`);
    });
}

document.querySelectorAll(".tab").forEach((button) => {
    button.addEventListener("click", () => showTab(button.dataset.tab));
});

function renderReport(report) {
    const summary = report.summary || {};

    $("totalFindings").textContent = summary.total_findings ?? 0;
    $("highFindings").textContent = summary.high ?? 0;
    $("mediumFindings").textContent = summary.medium ?? 0;
    $("lowFindings").textContent = summary.low ?? 0;

    $("reportMessage").textContent =
        "Analysis completed. Review the findings and pipeline results.";

    renderFindings();
}

function renderFindings() {
    const list = $("findingsList");
    list.replaceChildren();

    if (!latestData) return;

    const filter = $("severityFilter").value;
    const query = $("findingSearch").value.trim().toLowerCase();

    const findings = (latestData.findings || []).filter((finding) => {
        const searchable = [
            finding.rule_id,
            finding.severity,
            finding.function,
            finding.sink,
            finding.description,
            finding.message,
            finding.recommendation,
            finding.destination_buffer,
            finding.buffer_size,
            ...(finding.tainted_variables || [])
        ].join(" ").toLowerCase();

        const matchesSeverity =
            filter === "ALL" || finding.severity === filter;

        return matchesSeverity && searchable.includes(query);
    });

    if (findings.length === 0) {
        list.append(
            element("p", "No findings match these filters.", "empty-result")
        );
        return;
    }

    findings.forEach((finding) => {
        const card = element("article", "", "finding");

        card.append(
            element(
                "span",
                finding.severity || "UNKNOWN",
                `severity severity-${String(finding.severity || "").toLowerCase()}`
            )
        );

        card.append(
            element("h4", `${finding.rule_id || "Rule"}: ${finding.sink || "Finding"}`)
        );

        card.append(element("p", `Function: ${finding.function || "Unknown"}`));
        card.append(element("p", `Source line: ${finding.line ?? "Unknown"}`));

        const variables = finding.tainted_variables || [];
        card.append(
            element(
                "p",
                `Tainted variables: ${variables.join(", ") || "None listed"}`
            )
        );

        card.append(element("p", finding.message || ""));
        card.append(element("p", finding.description || ""));

        // Show buffer information when supplied by the analyzer.
        if (finding.destination_buffer != null) {
            card.append(
                element(
                    "p",
                    `Destination buffer: ${finding.destination_buffer}`,
                    "finding-detail"
                )
            );
        }

        if (finding.buffer_size != null) {
            card.append(
                element(
                    "p",
                    `Buffer capacity: ${finding.buffer_size} bytes`,
                    "finding-detail"
                )
            );
        }

        card.append(
            element(
                "p",
                `Recommendation: ${finding.recommendation || "Review this call."}`
            )
        );

        const jump = element("button", "Show source line", "secondary");

        jump.addEventListener("click", () => {
            const lines = sourceEditor.value.split("\n");
            const lineIndex = Math.max(
                0,
                Number(finding.line || 1) - 1
            );

            const start = lines
                .slice(0, lineIndex)
                .join("\n").length + (lineIndex ? 1 : 0);

            const end = start + (lines[lineIndex] || "").length;

            sourceEditor.focus();
            sourceEditor.setSelectionRange(start, end);
        });

        card.append(jump);
        list.append(card);
    });
}

function renderTokens(tokens) {
    const body = $("tokenRows");
    body.replaceChildren();

    const query = $("tokenSearch").value.trim().toLowerCase();

    const filtered = (tokens || []).filter((token) =>
        `${token.type} ${token.value} ${token.line}`
            .toLowerCase()
            .includes(query)
    );

    filtered.forEach((token, index) => {
        const row = element("tr");

        [
            index + 1,
            token.type,
            String(token.value),
            token.line
        ].forEach((value) => {
            row.append(element("td", value));
        });

        body.append(row);
    });

    $("tokenCount").textContent =
        `${filtered.length} of ${(tokens || []).length} tokens`;
}

function renderTreeValue(parent, value, label = "") {
    if (value === null || value === undefined) {
        const row = element("div", "", "tree-leaf");
        if (label) row.append(element("span", label, "tree-key"));
        row.append(element("span", String(value), "tree-value"));
        parent.append(row);
        return;
    }

    if (Array.isArray(value)) {
        const details = element("details", "", "tree-node");
        details.open = parent.childElementCount === 0;
        details.append(element("summary", `${label || "Items"} (${value.length})`));
        value.forEach((item, index) => renderTreeValue(details, item, `[${index}]`));
        parent.append(details);
        return;
    }

    if (typeof value === "object") {
        if (value.type) {
            const details = element("details", "", "tree-node");
            details.open = parent.childElementCount === 0;
            const title = [label, value.type, value.name].filter(Boolean).join(": ");
            details.append(element("summary", title));

            Object.entries(value).forEach(([key, child]) => {
                if (key === "type") return;
                if (child === null || typeof child !== "object") {
                    const row = element("div", "", "tree-leaf");
                    row.append(element("span", key, "tree-key"));
                    row.append(element("span", String(child), "tree-value"));
                    details.append(row);
                } else {
                    renderTreeValue(details, child, key);
                }
            });

            parent.append(details);
            return;
        }

        const entries = Object.entries(value);
        if (entries.length === 2 && "field" in value && "value" in value) {
            renderTreeValue(parent, value.value, value.field || label);
            return;
        }

        const details = element("details", "", "tree-node");
        details.open = parent.childElementCount === 0;
        details.append(element("summary", label || "Details"));
        entries.forEach(([key, child]) => renderTreeValue(details, child, key));
        parent.append(details);
        return;
    }

    const row = element("div", "", "tree-leaf");
    if (label) row.append(element("span", label, "tree-key"));
    row.append(element("span", String(value), "tree-value"));
    parent.append(row);
}

function renderAST(ast) {
    const root = $("astTree");
    root.replaceChildren();

    if (!ast) {
        root.append(element("p", "No AST data available."));
        return;
    }

    renderTreeValue(root, ast, ast.type || "Program");
}

function renderIR(ir) {
    const root = $("irView");
    root.replaceChildren();

    (ir?.functions || []).forEach((fn) => {
        const section = element("section", "", "ir-function");

        section.append(
            element("h4", `${fn.return_type} ${fn.name}()`)
        );

        if (!(fn.instructions || []).length) {
            section.append(element("p", "No IR instructions."));
        }

        (fn.instructions || []).forEach((instruction, index) => {
            const row = element("div", "", "ir-instruction");

            row.append(element("span", String(index + 1), "ir-number"));
            row.append(element("code", instruction.operation));
            row.append(
                element("code", JSON.stringify(instruction.arguments))
            );
            row.append(element("span", `Line ${instruction.line}`, "muted"));

            section.append(row);
        });

        root.append(section);
    });

    if (!root.childElementCount) {
        root.append(element("p", "No intermediate representation available."));
    }
}

function renderCFG(cfgs) {
    const root = $("cfgView");
    root.replaceChildren();

    (cfgs || []).forEach((cfg) => {
        root.append(element("h4", `Function: ${cfg.function_name}`));

        (cfg.blocks || []).forEach((block) => {
            const card = element("div", "", "graph-node");

            card.append(element("strong", `Block ${block.block_id}`));

            (block.instructions || []).forEach((instruction) => {
                card.append(
                    element(
                        "code",
                        `${instruction.operation} ${JSON.stringify(instruction.arguments)} (line ${instruction.line})`
                    )
                );
            });

            card.append(
                element(
                    "p",
                    `Successors: ${(block.successors || []).join(", ") || "None"}`
                )
            );

            root.append(card);

            if ((block.successors || []).length) {
                root.append(element("div", "↓", "graph-arrow"));
            }
        });
    });

    if (!root.childElementCount) {
        root.append(element("p", "No CFG data available."));
    }
}

function renderCallGraph(graph) {
    const root = $("callGraphView");
    root.replaceChildren();

    const entries = Object.entries(graph || {});

    if (!entries.length) {
        root.append(element("p", "No function call data available."));
        return;
    }

    entries.forEach(([caller, callees]) => {
        const row = element("div", "", "call-row");

        row.append(element("strong", caller));
        row.append(element("span", "→"));
        row.append(element("span", (callees || []).join(", ") || "(no calls)"));

        root.append(row);
    });
}

function renderPipeline(pipeline) {
    renderTokens(pipeline.tokens || []);
    renderAST(pipeline.ast);
    renderIR(pipeline.ir);
    renderCFG(pipeline.cfg);
    renderCallGraph(pipeline.call_graph);
}

sourceEditor.addEventListener("input", updateCharacterCount);

$("severityFilter").addEventListener("change", renderFindings);
$("findingSearch").addEventListener("input", renderFindings);

$("tokenSearch").addEventListener("input", () => {
    renderTokens(latestData?.pipeline?.tokens || []);
});

sampleButton.addEventListener("click", () => {
    sourceEditor.value = sampleCode;
    updateCharacterCount();
    hideError();
});

$("exportButton").addEventListener("click", () => {
    if (!latestData) return;

    const blob = new Blob(
        [JSON.stringify(latestData, null, 2)],
        { type: "application/json" }
    );

    const url = URL.createObjectURL(blob);
    const link = element("a");

    link.href = url;
    link.download = "security-compiler-report.json";

    document.body.append(link);
    link.click();
    link.remove();

    setTimeout(() => URL.revokeObjectURL(url), 1000);
});

analyzeButton.addEventListener("click", async () => {
    hideError();
    analyzeButton.disabled = true;
    analyzeButton.textContent = "Analyzing...";

    try {
        const response = await fetch("/analyze", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                source_code: sourceEditor.value
            })
        });

        const data = await response.json();

        if (!response.ok) {
            showError(data.error || "Analysis failed.");
            return;
        }

        if (
            !data.pipeline ||
            !data.summary ||
            !Array.isArray(data.findings)
        ) {
            showError("The server response is missing required analysis data.");
            return;
        }

        latestData = data;

        renderReport(data);
        renderPipeline(data.pipeline);

        showTab("security");
        results.classList.remove("hidden");
    } catch (error) {
        showError(
            "Could not connect to the analyzer. Make sure the Flask server is running."
        );
    } finally {
        analyzeButton.disabled = false;
        analyzeButton.textContent = "Analyze program";
    }
});

updateCharacterCount();
