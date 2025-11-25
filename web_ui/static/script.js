// 检查配置状态
async function checkConfig() {
    try {
        const response = await fetch('/api/check_config');
        const data = await response.json();
        
        const indicator = document.getElementById('statusIndicator');
        const statusText = document.getElementById('statusText');
        
        if (data.configured) {
            indicator.className = 'status-indicator ready';
            statusText.textContent = `配置正常 - 模型: ${data.model}`;
        } else {
            indicator.className = 'status-indicator error';
            statusText.textContent = data.message || '配置未完成';
        }
    } catch (error) {
        const indicator = document.getElementById('statusIndicator');
        const statusText = document.getElementById('statusText');
        indicator.className = 'status-indicator error';
        statusText.textContent = '无法连接到服务器';
        console.error('检查配置失败:', error);
    }
}

// 优化代码
async function optimizeCode() {
    const codeInput = document.getElementById('codeInput');
    const code = codeInput.value.trim();
    
    if (!code) {
        showError('请输入代码');
        return;
    }
    
    const optType = document.querySelector('input[name="optType"]:checked').value;
    const useDualRole = false;  // 已移除旧版二角色复选框，保留此变量用于向后兼容
    const workflowModeInput = document.querySelector('input[name="workflowMode"]:checked');
    const workflowMode = workflowModeInput ? workflowModeInput.value : null;
    const optimizeBtn = document.getElementById('optimizeBtn');
    const btnText = document.getElementById('btnText');
    const btnLoader = document.getElementById('btnLoader');
    
    // 禁用按钮并显示加载状态
    optimizeBtn.disabled = true;
    btnText.textContent = '优化中...';
    btnLoader.style.display = 'inline-block';
    
    // 隐藏错误和结果
    hideError();
    hideResult();
    const runStats = document.getElementById('runStats');
    if (runStats) {
        runStats.style.display = 'none';
        runStats.textContent = '';
    }
    
    // 设置超时提示（仅作为信息提示，不中断请求）
    let timeoutWarning = null;
    const showTimeoutWarning = () => {
        if (!timeoutWarning) {
            timeoutWarning = setTimeout(() => {
                // 显示信息提示（不是错误）
                const errorSection = document.getElementById('errorSection');
                const errorMessage = document.getElementById('errorMessage');
                errorMessage.innerHTML = '<div style="color: var(--warning-color);">⏳ 请求处理时间较长，请耐心等待...<br>如果长时间无响应，可能是网络问题。</div>';
                errorSection.style.display = 'block';
                errorSection.style.background = 'rgba(245, 158, 11, 0.1)';
                errorSection.style.borderColor = 'var(--warning-color)';
            }, 30000); // 30秒后显示提示
        }
    };
    showTimeoutWarning();
    
    try {
        const response = await fetch('/api/optimize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                code: code,
                opt_type: optType,
                use_dual_role: useDualRole,
                workflow_mode: workflowMode
            })
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            showResult(data);
        } else {
            showError(data.message || '优化失败', data.error_type);
        }
    } catch (error) {
        let errorMsg = '网络错误: ' + error.message;
        if (error.message.includes('timeout') || error.name === 'TimeoutError') {
            errorMsg = '请求超时，请检查网络连接后重试';
        }
        showError(errorMsg, 'timeout');
        console.error('优化失败:', error);
    } finally {
        // 清除超时提示
        if (timeoutWarning) {
            clearTimeout(timeoutWarning);
            timeoutWarning = null;
        }
        // 恢复错误区域样式（如果被超时提示修改过）
        const errorSection = document.getElementById('errorSection');
        if (errorSection) {
            errorSection.style.background = 'rgba(239, 68, 68, 0.1)';
            errorSection.style.borderColor = 'var(--error-color)';
        }
        // 恢复按钮状态
        optimizeBtn.disabled = false;
        btnText.textContent = '开始优化';
        btnLoader.style.display = 'none';
    }
}

// 显示结果
function showResult(data) {
    const resultSection = document.getElementById('resultSection');
    const resultTitle = document.getElementById('resultTitle');
    const originalCode = document.getElementById('originalCode');
    const optimizedCode = document.getElementById('optimizedCode');
    const optimizationDetails = document.getElementById('optimizationDetails');
    const detailsContent = document.getElementById('detailsContent');
    const runStats = document.getElementById('runStats');
    
    // 设置标题中的工作流模式
    if (resultTitle) {
        const modeName = getWorkflowName(data.workflow);
        if (modeName) {
            resultTitle.textContent = `优化结果（模式：${modeName}）`;
        } else {
            resultTitle.textContent = '优化结果';
        }
    }

    // 设置代码
    originalCode.textContent = data.original_code || '';
    optimizedCode.textContent = data.optimized_code || '';
    
    // 高亮代码
    hljs.highlightElement(originalCode);
    hljs.highlightElement(optimizedCode);
    
    // 显示优化详情
    let detailsHTML = '';
    
    // 优先显示 optimizations（优化步骤详情）
    if (data.optimizations && Object.keys(data.optimizations).length > 0) {
        // 按照固定顺序显示：SIMPLIFY, ADD_COMMENT, RENAME_VAR
        const order = ['SIMPLIFY', 'ADD_COMMENT', 'RENAME_VAR'];
        const displayed = new Set();
        
        for (const optName of order) {
            if (data.optimizations[optName]) {
                const optData = data.optimizations[optName];
                const statusClass = optData.status.startsWith('SUCC') ? 'succ' : 'fail';
                
                // 对于重命名变量，只显示变量映射JSON，不显示代码
                let contentHTML = '';
                if (optName === 'RENAME_VAR') {
                    // 重命名变量：只显示变量映射JSON，不显示代码
                    if (optData.advisor_response) {
                        try {
                            // 尝试解析 JSON
                            const renameMap = JSON.parse(optData.advisor_response);
                            if (typeof renameMap === 'object' && renameMap !== null) {
                                // 只显示变量映射JSON，不显示代码
                                contentHTML = `<pre style="background: var(--code-bg); padding: 10px; border-radius: 4px; margin: 10px 0; font-size: 0.9rem; overflow-x: auto;">${escapeHtml(JSON.stringify(renameMap, null, 2))}</pre>`;
                            } else {
                                contentHTML = `<p style="color: var(--text-secondary); margin: 10px 0; font-size: 0.9rem;">变量重命名信息不可用</p>`;
                            }
                        } catch (e) {
                            // 不是 JSON，不显示代码块内容
                            if (optData.advisor_response.includes('```')) {
                                contentHTML = `<p style="color: var(--text-secondary); margin: 10px 0; font-size: 0.9rem;">变量重命名信息不可用</p>`;
                            } else {
                                // 尝试直接显示（可能是纯文本的变量映射说明）
                                contentHTML = `<p style="color: var(--text-secondary); margin: 10px 0; font-size: 0.9rem;">${escapeHtml(optData.advisor_response)}</p>`;
                            }
                        }
                    } else {
                        contentHTML = `<p style="color: var(--text-secondary); margin: 10px 0; font-size: 0.9rem;">变量重命名信息不可用</p>`;
                    }
                } else if (optData.output && optData.output.trim()) {
                    // 对于其他优化类型（简化代码、添加注释），显示优化后的代码
                    contentHTML = `<pre style="background: var(--code-bg); padding: 10px; border-radius: 4px; margin: 10px 0; font-size: 0.9rem; overflow-x: auto;"><code class="language-c">${escapeHtml(optData.output)}</code></pre>`;
                } else if (optData.advisor_response) {
                    // 如果没有 output，显示建议响应
                    contentHTML = `<p style="color: var(--text-secondary); margin: 10px 0; font-size: 0.9rem;">${escapeHtml(optData.advisor_response)}</p>`;
                }
                
                detailsHTML += `
                    <div class="optimization-item">
                        <h4>
                            ${getOptName(optName)}
                            <span class="status-badge ${statusClass}">${optData.status}</span>
                        </h4>
                        ${contentHTML}
                    </div>
                `;
                displayed.add(optName);
            }
        }
        
        // 显示其他未在固定顺序中的优化项
        for (const [optName, optData] of Object.entries(data.optimizations)) {
            if (!displayed.has(optName)) {
                const statusClass = optData.status.startsWith('SUCC') ? 'succ' : 'fail';
                let contentHTML = '';
                if (optData.output) {
                    contentHTML = `<pre style="background: var(--code-bg); padding: 10px; border-radius: 4px; margin: 10px 0; font-size: 0.9rem; overflow-x: auto;"><code class="language-c">${escapeHtml(optData.output)}</code></pre>`;
                } else if (optData.advisor_response) {
                    contentHTML = `<p style="color: var(--text-secondary); margin: 10px 0; font-size: 0.9rem;">${escapeHtml(optData.advisor_response)}</p>`;
                }
                detailsHTML += `
                    <div class="optimization-item">
                        <h4>
                            ${getOptName(optName)}
                            <span class="status-badge ${statusClass}">${optData.status}</span>
                        </h4>
                        ${contentHTML}
                    </div>
                `;
            }
        }
    }
    
    // 如果没有 optimizations，但有 analysis，显示分析信息（兼容旧版）
    if (!detailsHTML && (data.analysis || data.optimizations_needed)) {
        if (data.analysis) {
            detailsHTML += `<div class="optimization-item">
                <h4>代码分析</h4>
                <p style="color: var(--text-secondary); margin: 10px 0;">${escapeHtml(data.analysis)}</p>
            </div>`;
        }
        if (data.optimizations_needed && data.optimizations_needed.length > 0) {
            const optNames = {
                'simplify': '简化代码',
                'comment': '添加注释',
                'rename': '重命名变量'
            };
            const optList = data.optimizations_needed.map(opt => optNames[opt] || opt).join('、');
            detailsHTML += `<div class="optimization-item">
                <h4>建议的优化</h4>
                <p style="color: var(--text-secondary); margin: 10px 0;">${optList}</p>
            </div>`;
        }
    }
    
    if (detailsHTML) {
        detailsContent.innerHTML = detailsHTML;
        optimizationDetails.style.display = 'block';
        
        // 高亮代码块
        if (typeof hljs !== 'undefined') {
            detailsContent.querySelectorAll('code.language-c').forEach(block => {
                hljs.highlightElement(block);
            });
        }
    } else {
        optimizationDetails.style.display = 'none';
    }

    // 显示运行指标
    if (runStats) {
        let html = '';
        if (data.mssc) {
            const total = data.mssc.total_checks ?? 0;
            const rejected = data.mssc.rejected ?? 0;
            let rateText = '—';
            if (data.mssc.reject_rate !== null && data.mssc.reject_rate !== undefined) {
                rateText = (data.mssc.reject_rate * 100).toFixed(1) + '%';
            }
            html += `MSSC 检查次数：${total}，拒绝次数：${rejected}，拒绝率：${rateText}`;
        }
        if (typeof data.elapsed_ms === 'number') {
            const seconds = (data.elapsed_ms / 1000).toFixed(1);
            if (html) html += ' ｜ ';
            html += `本次优化耗时：${seconds} 秒`;
        }
        if (html) {
            runStats.innerHTML = html;
            runStats.style.display = 'block';
        } else {
            runStats.style.display = 'none';
            runStats.textContent = '';
        }
    }
    
    resultSection.style.display = 'block';
    resultSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// 获取优化类型中文名
function getOptName(optName) {
    const names = {
        'SIMPLIFY': '简化代码',
        'ADD_COMMENT': '添加注释',
        'RENAME_VAR': '重命名变量'
    };
    return names[optName] || optName;
}

// 获取工作流模式中文名
function getWorkflowName(workflow) {
    if (!workflow) return '';
    const map = {
        'THREE_ROLE': '三角色',
        'DUAL_ROLE': '旧版二角色',
        'TWO_ROLE_A': '二角色 A（Analyzer + Optimizer）',
        'TWO_ROLE_B': '二角色 B（Referee + Transformer）',
        'ONE_SHOT': 'One-shot',
        'SINGLE_OPT': '单步优化'
    };
    return map[workflow] || workflow;
}

// 显示分析信息（二角色模式）
function showAnalysis(data) {
    const optimizationDetails = document.getElementById('optimizationDetails');
    const detailsContent = document.getElementById('detailsContent');
    
    if (data.analysis || data.optimizations_needed) {
        let analysisHTML = '';
        
        if (data.analysis) {
            analysisHTML += `<div class="optimization-item">
                <h4>代码分析</h4>
                <p style="color: var(--text-secondary); margin: 10px 0;">${escapeHtml(data.analysis)}</p>
            </div>`;
        }
        
        if (data.optimizations_needed && data.optimizations_needed.length > 0) {
            const optNames = {
                'simplify': '简化代码',
                'comment': '添加注释',
                'rename': '重命名变量'
            };
            const optList = data.optimizations_needed.map(opt => optNames[opt] || opt).join('、');
            analysisHTML += `<div class="optimization-item">
                <h4>建议的优化</h4>
                <p style="color: var(--text-secondary); margin: 10px 0;">${optList}</p>
            </div>`;
        }
        
        if (data.optimization_response) {
            analysisHTML += `<div class="optimization-item">
                <h4>优化过程</h4>
                <pre style="color: var(--text-secondary); margin: 10px 0; white-space: pre-wrap; font-size: 0.9rem;">${escapeHtml(data.optimization_response)}</pre>
            </div>`;
        }
        
        detailsContent.innerHTML = analysisHTML;
        optimizationDetails.style.display = 'block';
    }
}

// 显示错误
function showError(message, errorType = 'other') {
    const errorSection = document.getElementById('errorSection');
    const errorMessage = document.getElementById('errorMessage');
    
    // 处理多行错误信息
    const formattedMessage = message.replace(/\n/g, '<br>');
    
    // 如果是超时错误，添加重试按钮
    let errorHTML = `<div>${formattedMessage}</div>`;
    if (errorType === 'timeout') {
        errorHTML += '<div style="margin-top: 15px;"><button class="btn btn-secondary" onclick="optimizeCode()">重试</button></div>';
    }
    
    errorMessage.innerHTML = errorHTML;
    errorSection.style.display = 'block';
    errorSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// 隐藏错误
function hideError() {
    document.getElementById('errorSection').style.display = 'none';
}

// 隐藏结果
function hideResult() {
    document.getElementById('resultSection').style.display = 'none';
}

// 清空代码
function clearCode() {
    document.getElementById('codeInput').value = '';
    hideResult();
    hideError();
}

// 加载示例代码
function loadExample() {
    const exampleCode = `int fibonacci(int n) {
    int uVar1;
    int iVar2;
    int iVar3;
    
    if (n < 2) {
        return n;
    }
    
    iVar2 = fibonacci(n - 1);
    iVar3 = fibonacci(n - 2);
    uVar1 = iVar2 + iVar3;
    
    return uVar1;
}`;
    
    document.getElementById('codeInput').value = exampleCode;
    hideResult();
    hideError();
}

// 复制结果
async function copyResult() {
    const optimizedCode = document.getElementById('optimizedCode').textContent;
    try {
        await navigator.clipboard.writeText(optimizedCode);
        // 简单的提示
        const btn = event.target;
        const originalText = btn.textContent;
        btn.textContent = '已复制!';
        setTimeout(() => {
            btn.textContent = originalText;
        }, 2000);
    } catch (error) {
        showError('复制失败: ' + error.message);
    }
}

// HTML转义
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// 页面加载时检查配置
document.addEventListener('DOMContentLoaded', function() {
    checkConfig();
    
    // 代码输入框支持Tab键
    const codeInput = document.getElementById('codeInput');
    codeInput.addEventListener('keydown', function(e) {
        if (e.key === 'Tab') {
            e.preventDefault();
            const start = this.selectionStart;
            const end = this.selectionEnd;
            this.value = this.value.substring(0, start) + '    ' + this.value.substring(end);
            this.selectionStart = this.selectionEnd = start + 4;
        }
    });
    
    // Enter + Ctrl 快捷键优化
    codeInput.addEventListener('keydown', function(e) {
        if (e.ctrlKey && e.key === 'Enter') {
            e.preventDefault();
            optimizeCode();
        }
    });
});

