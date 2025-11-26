"""
Flask Web应用 - DeGPT可视化界面
"""
import os
import sys
import json
import time
import traceback
from flask import Flask, render_template, request, jsonify

# 尝试导入flask_cors，如果未安装则跳过
try:
    from flask_cors import CORS
    CORS_AVAILABLE = True
except ImportError:
    CORS_AVAILABLE = False
    print("警告: flask_cors未安装，CORS功能将被禁用")

# 添加degpt目录到路径
DIR = os.path.dirname(os.path.abspath(__file__))
DEGPT_DIR = os.path.join(os.path.dirname(DIR), 'degpt')
sys.path.insert(0, DEGPT_DIR)

from role import RoleModel, single_opt, opt_str2dtype, DType
from chat import llm_configured, load_config, test_llm_connection
from util import Log

# 尝试导入二角色及增强工作流
try:
    from role_v2 import (
        DualRoleModel,
        dual_role_optimize,
        TwoRoleModeB,
        one_shot_optimize,
    )
    DUAL_ROLE_AVAILABLE = True
except ImportError:
    DUAL_ROLE_AVAILABLE = False
    print("警告: 二角色模型未找到，将使用三角色模型")

app = Flask(__name__)
if CORS_AVAILABLE:
    CORS(app)

logger = Log().get(__file__)


def _build_mssc_stats(stats: dict) -> dict:
    total = int(stats.get('total_checks', 0) or 0)
    rejected = int(stats.get('rejected', 0) or 0)
    if total > 0:
        reject_rate = rejected / total
    else:
        reject_rate = None
    return {
        'total_checks': total,
        'rejected': rejected,
        'reject_rate': reject_rate,
    }


def run_optimization(code: str, opt_type: str, workflow_mode: str, use_dual_role: bool) -> dict:
    """
    统一的后端调度入口：
    - 根据 workflow_mode / use_dual_role / opt_type 选择具体工作流
    - 统一收集 MSSC 统计与耗时
    - 返回标准化结构（不含 status 字段）
    """
    mssc_stats: dict = {}
    start_time = time.time()

    result: dict
    effective_workflow = None

    # 显式指定 workflow_mode 时优先
    if workflow_mode in ('three_role', 'two_role_a', 'two_role_b', 'one_shot'):
        if workflow_mode == 'three_role':
            model = RoleModel(decompile_code=code, mssc_stats=mssc_stats)
            raw = model.work()
            effective_workflow = 'THREE_ROLE'

            result = {
                'original_code': raw.get('decompiler_output', code),
                'optimized_code': raw.get('output', code),
                'workflow': effective_workflow,
                'optimizations': {},
            }
            if 'optimization' in raw:
                for opt_name, opt_data in raw['optimization'].items():
                    result['optimizations'][opt_name] = {
                        'input': opt_data.get('input', ''),
                        'output': opt_data.get('output', ''),
                        'status': opt_data.get('status', 'UNKNOWN'),
                        'advisor_response': opt_data.get('advisor_response', ''),
                    }
            if 'original_directions_src' in raw:
                result['directions'] = raw.get('original_directions_src', '')
            if 'sorted_directions' in raw:
                result['sorted_directions'] = raw.get('sorted_directions', [])

        elif workflow_mode == 'two_role_a':
            # 使用旧版二角色模式（DualRoleModel）
            model = DualRoleModel(decompile_code=code, mssc_stats=mssc_stats)
            raw = model.work()
            effective_workflow = 'TWO_ROLE_A'
            result = {
                'original_code': raw.get('decompiler_output', code),
                'optimized_code': raw.get('output', code),
                'workflow': effective_workflow,
                'analysis': raw.get('analysis', ''),
                'optimizations_needed': raw.get('optimizations_needed', []),
                'optimizations': raw.get('optimizations', {}),
                'mssc_status': raw.get('mssc_status', ''),
            }
            if 'optimization_response' in raw:
                result['optimization_response'] = raw.get('optimization_response', '')

        elif workflow_mode == 'two_role_b':
            model = TwoRoleModeB(decompile_code=code, mssc_stats=mssc_stats)
            raw = model.work()
            effective_workflow = 'TWO_ROLE_B'
            result = {
                'original_code': raw.get('decompiler_output', code),
                'optimized_code': raw.get('output', code),
                'workflow': effective_workflow,
                'analysis': raw.get('analysis', ''),
                'directions': raw.get('directions', []),
                'mssc_status': raw.get('mssc_status', ''),
                'optimizations': raw.get('optimizations', {}),
            }

        else:  # one_shot
            raw = one_shot_optimize(code, mssc_stats=mssc_stats)
            effective_workflow = 'ONE_SHOT'
            result = {
                'original_code': raw.get('original_code', code),
                'optimized_code': raw.get('optimized_code', code),
                'workflow': effective_workflow,
                'llm_raw_response': raw.get('llm_raw_response', ''),
                'mssc_status': raw.get('mssc_status', ''),
                'optimizations': raw.get('optimizations', {}),
            }

    else:
        # 未显式指定 workflow_mode：兼容旧逻辑
        # 注意：use_dual_role 选项已从前端移除，此逻辑保留用于向后兼容
        if use_dual_role and DUAL_ROLE_AVAILABLE and opt_type == 'all':
            model = DualRoleModel(decompile_code=code, mssc_stats=mssc_stats)
            raw = model.work()
            effective_workflow = 'DUAL_ROLE'
            result = {
                'original_code': raw.get('decompiler_output', code),
                'optimized_code': raw.get('output', code),
                'workflow': effective_workflow,
                'analysis': raw.get('analysis', ''),
                'optimizations_needed': raw.get('optimizations_needed', []),
            }
            if 'optimization_response' in raw:
                result['optimization_response'] = raw.get('optimization_response', '')
        elif opt_type == 'all':
            # 三角色完整优化
            model = RoleModel(decompile_code=code, mssc_stats=mssc_stats)
            raw = model.work()
            effective_workflow = 'THREE_ROLE'
            result = {
                'original_code': raw.get('decompiler_output', code),
                'optimized_code': raw.get('output', code),
                'workflow': effective_workflow,
                'optimizations': {},
            }
            if 'optimization' in raw:
                for opt_name, opt_data in raw['optimization'].items():
                    result['optimizations'][opt_name] = {
                        'input': opt_data.get('input', ''),
                        'output': opt_data.get('output', ''),
                        'status': opt_data.get('status', 'UNKNOWN'),
                        'advisor_response': opt_data.get('advisor_response', ''),
                    }
            if 'original_directions_src' in raw:
                result['directions'] = raw.get('original_directions_src', '')
            if 'sorted_directions' in raw:
                result['sorted_directions'] = raw.get('sorted_directions', [])
        else:
            # 单种优化：仍使用原三角色 single_opt，暂不强制 MSSC
            dtype = opt_str2dtype(opt_type)
            raw = single_opt(code, dtype)
            effective_workflow = 'SINGLE_OPT'
            result = {
                'original_code': raw.get('decompiler_output', code),
                'optimized_code': raw.get('output', code),
                'workflow': effective_workflow,
                'optimizations': {
                    opt_type.upper(): {
                        'input': code,
                        'output': raw.get('output', code),
                        'status': 'SUCC',
                        'advisor_response': '',
                    }
                },
            }

    elapsed_ms = int((time.time() - start_time) * 1000)
    result['elapsed_ms'] = elapsed_ms
    result['mssc'] = _build_mssc_stats(mssc_stats)

    if effective_workflow and 'workflow' not in result:
        result['workflow'] = effective_workflow

    return result

@app.route('/')
def index():
    """主页面"""
    return render_template('index.html')

@app.route('/api/check_config', methods=['GET'])
def check_config():
    """检查LLM配置"""
    try:
        configured = llm_configured()
        if configured:
            model = load_config('LLM', 'model')
            return jsonify({
                'status': 'success',
                'configured': True,
                'model': model
            })
        else:
            return jsonify({
                'status': 'success',
                'configured': False,
                'message': '请先配置LLM API密钥'
            })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/optimize', methods=['POST'])
def optimize():
    """优化代码接口"""
    try:
        data = request.json
        code = data.get('code', '').strip()
        opt_type = data.get('opt_type', 'all')
        use_dual_role = data.get('use_dual_role', False)  # 是否使用二角色模式（旧逻辑）
        workflow_mode = data.get('workflow_mode', None) or None
        
        if not code:
            return jsonify({
                'status': 'error',
                'message': '代码不能为空'
            }), 400
        
        if not llm_configured():
            return jsonify({
                'status': 'error',
                'message': 'LLM未配置，请先配置API密钥'
            }), 400
        
        logger.info(f'开始优化，类型: {opt_type}, workflow_mode: {workflow_mode}, '
                    f'模式: {"二角色" if use_dual_role else "三角色"}')

        # 统一调度
        result = run_optimization(code, opt_type, workflow_mode, use_dual_role)

        response_data = {
            'status': 'success',
            **result,
        }

        logger.info('优化完成')
        return jsonify(response_data)
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f'优化失败: {error_msg}')
        logger.error(traceback.format_exc())
        
        # 识别超时错误并给出友好提示
        if 'timeout' in error_msg.lower() or 'timed out' in error_msg.lower():
            friendly_msg = (
                '请求超时，可能是以下原因：\n'
                '1. 网络连接不稳定\n'
                '2. API服务器响应较慢\n'
                '3. 代码过长导致处理时间过长\n\n'
                '建议：\n'
                '- 检查网络连接\n'
                '- 尝试使用较短的代码片段\n'
                '- 稍后重试'
            )
        elif 'connection' in error_msg.lower() or 'connect' in error_msg.lower():
            friendly_msg = (
                '网络连接失败，可能是以下原因：\n'
                '1. 网络连接中断\n'
                '2. API服务器不可达\n'
                '3. 防火墙或代理设置问题\n\n'
                '建议：\n'
                '- 检查网络连接\n'
                '- 检查API配置是否正确\n'
                '- 检查防火墙设置'
            )
        else:
            friendly_msg = f'优化失败: {error_msg}'
        
        return jsonify({
            'status': 'error',
            'message': friendly_msg,
            'error_type': 'timeout' if 'timeout' in error_msg.lower() else 'other'
        }), 500

@app.route('/api/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    # 在启动 Flask 之前先检测一次 LLM API 连接情况，并在控制台输出中文提示
    ok, msg = test_llm_connection()
    print("=" * 60)
    print("LLM API 连接检测结果：")
    if ok:
        print(f"[OK] {msg}")
    else:
        print("[ERROR] API 连接检测失败：")
        print(msg)
    print("=" * 60)

    app.run(debug=True, host='0.0.0.0', port=5000)

