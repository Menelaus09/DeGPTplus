"""
Flask Web应用 - DeGPT可视化界面
"""
import os
import sys
import json
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
from chat import llm_configured, load_config
from util import Log

# 尝试导入二角色模型
try:
    from role_v2 import DualRoleModel, dual_role_optimize
    DUAL_ROLE_AVAILABLE = True
except ImportError:
    DUAL_ROLE_AVAILABLE = False
    print("警告: 二角色模型未找到，将使用三角色模型")

app = Flask(__name__)
if CORS_AVAILABLE:
    CORS(app)

logger = Log().get(__file__)

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
        use_dual_role = data.get('use_dual_role', False)  # 是否使用二角色模式
        
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
        
        logger.info(f'开始优化，类型: {opt_type}, 模式: {"二角色" if use_dual_role else "三角色"}')
        
        # 使用二角色模式（如果可用且请求）
        if use_dual_role and DUAL_ROLE_AVAILABLE and opt_type == 'all':
            try:
                result = dual_role_optimize(code)
                
                response_data = {
                    'status': 'success',
                    'original_code': result.get('decompiler_output', code),
                    'optimized_code': result.get('output', code),
                    'workflow': result.get('workflow', 'DONE'),
                    'optimizations': {},
                    'analysis': result.get('analysis', ''),
                    'optimizations_needed': result.get('optimizations_needed', [])
                }
                
                if 'optimization_response' in result:
                    response_data['optimization_response'] = result.get('optimization_response', '')
                
                # 调试信息
                logger.info(f'二角色优化完成 - 原始代码长度: {len(code)}, 优化后长度: {len(result.get("output", code))}')
                logger.info(f'优化后代码是否改变: {result.get("output", code) != code}')
                
                return jsonify(response_data)
            except Exception as e:
                logger.warning(f'二角色模式失败，回退到三角色模式: {e}')
                # 回退到三角色模式
        
        if opt_type == 'all':
            # 使用RoleModel进行完整优化
            model = RoleModel(decompile_code=code)
            result = model.work()
            
            # 格式化结果
            response_data = {
                'status': 'success',
                'original_code': result.get('decompiler_output', code),
                'optimized_code': result.get('output', code),
                'workflow': result.get('workflow', 'DONE'),
                'optimizations': {}
            }
            
            # 提取优化详情
            if 'optimization' in result:
                for opt_name, opt_data in result['optimization'].items():
                    response_data['optimizations'][opt_name] = {
                        'input': opt_data.get('input', ''),
                        'output': opt_data.get('output', ''),
                        'status': opt_data.get('status', 'UNKNOWN'),
                        'advisor_response': opt_data.get('advisor_response', '')
                    }
            
            # 提取方向信息
            if 'original_directions_src' in result:
                response_data['directions'] = result.get('original_directions_src', '')
            if 'sorted_directions' in result:
                response_data['sorted_directions'] = result.get('sorted_directions', [])
                
        else:
            # 单种优化
            dtype = opt_str2dtype(opt_type)
            result = single_opt(code, dtype)
            
            response_data = {
                'status': 'success',
                'original_code': result.get('decompiler_output', code),
                'optimized_code': result.get('output', code),
                'workflow': 'DONE',
                'optimizations': {
                    opt_type.upper(): {
                        'input': code,
                        'output': result.get('output', code),
                        'status': 'SUCC',
                        'advisor_response': ''
                    }
                }
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
    app.run(debug=True, host='0.0.0.0', port=5000)

