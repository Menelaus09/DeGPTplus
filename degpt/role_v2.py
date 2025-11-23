"""
二角色机制 - 使用更强大的AI模型
角色1: Analyzer - 分析代码，确定优化方向
角色2: Optimizer - 直接进行优化，确保语义正确
"""
import os
import re
import sys
import json
import traceback
from typing import Optional, Dict, List, Tuple
from cinspector.interfaces import CCode
from cinspector.nodes import Util

DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(DIR, '.'))
from util import Log, is_code_in_response, response_filter
from chat import QueryChatGPT, llm_configured, load_config

logger = Log().get(__file__)

PROMPT_PATH = os.path.join(DIR, 'prompt_v2.json')  # 新的prompt文件


def get_prompt(name: str, prompt_path: str = PROMPT_PATH) -> Optional[Dict[str, str]]:
    """获取prompt"""
    if not os.path.exists(prompt_path):
        logger.warning(f"Prompt file not found: {prompt_path}, using default prompts")
        return None
    
    with open(prompt_path, 'r', encoding='utf-8') as f:
        prompts = json.load(f)
    
    for _p in prompts:
        if _p['name'] == name:
            return _p['prompt']
    return None


class Analyzer:
    """
    分析器：分析代码，确定需要哪些优化
    替代原来的Referee角色
    """
    
    def __init__(self):
        self.llm = QueryChatGPT()
        self.llm.insert_system_prompt(
            'You are an expert code analyzer. Analyze C code and determine what optimizations are needed.'
        )
    
    def analyze(self, code: str) -> Tuple[str, List[str]]:
        """
        分析代码，返回优化建议
        
        Args:
            code: 待分析的代码
        Returns:
            (分析结果文本, 优化类型列表)
        """
        prompt = get_prompt('analyze')
        if not prompt:
            # 使用默认prompt
            prompt_content = (
                "Analyze the following C code and determine what optimizations are needed. "
                "Consider: code simplification, adding comments, variable renaming. "
                "Respond with a JSON object containing 'needs_simplify', 'needs_comment', 'needs_rename' (all boolean) "
                "and 'analysis' (brief explanation).\n\n{code}"
            )
        else:
            prompt_content = prompt['content']
        
        try:
            response = self.llm.query(prompt_content.format(code=code))
            
            # 解析响应
            optimizations = self._parse_analysis(response)
            return response, optimizations
        except Exception as e:
            logger.error(f"Analyzer failed: {e}")
            # 默认返回所有优化
            return "Analysis failed, applying all optimizations", ['simplify', 'comment', 'rename']
    
    def _parse_analysis(self, response: str) -> List[str]:
        """解析分析结果"""
        optimizations = []
        
        # 尝试解析JSON
        try:
            # 先尝试直接解析整个响应
            try:
                data = json.loads(response.strip())
            except:
                # 如果失败，尝试提取JSON部分（支持多行JSON）
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                else:
                    raise ValueError("No JSON found in response")
            
            # 解析JSON数据
            if isinstance(data, dict):
                if data.get('needs_simplify', False):
                    optimizations.append('simplify')
                if data.get('needs_comment', False):
                    optimizations.append('comment')
                if data.get('needs_rename', False):
                    optimizations.append('rename')
        except Exception as e:
            logger.debug(f"JSON parsing failed: {e}, using keyword matching")
            pass
        
        # 如果JSON解析失败，使用关键词匹配
        if not optimizations:
            response_lower = response.lower()
            if 'simplif' in response_lower or 'redundant' in response_lower:
                optimizations.append('simplify')
            if 'comment' in response_lower or 'explain' in response_lower:
                optimizations.append('comment')
            if 'rename' in response_lower or 'variable' in response_lower:
                optimizations.append('rename')
        
        # 如果还是没有，默认全部
        if not optimizations:
            optimizations = ['simplify', 'comment', 'rename']
        
        return optimizations


class Optimizer:
    """
    优化器：直接进行代码优化，确保语义正确
    合并了原来Advisor和Operator的功能
    """
    
    def __init__(self):
        self.llm = QueryChatGPT()
        self.llm.insert_system_prompt(
            'You are an expert C code optimizer. Optimize code while preserving exact semantics. '
            'Return only the optimized code without explanations.'
        )
    
    def optimize(self, code: str, opt_types: List[str] = None) -> Tuple[str, str]:
        """
        优化代码
        
        Args:
            code: 待优化的代码
            opt_types: 优化类型列表，如果为None则进行全部优化
        Returns:
            (优化后的代码, 响应文本)
        """
        if opt_types is None:
            opt_types = ['simplify', 'comment', 'rename']
        
        current_code = code
        all_responses = []
        
        # 按顺序进行优化
        for opt_type in opt_types:
            try:
                optimized_code, response = self._apply_optimization(current_code, opt_type)
                if optimized_code and optimized_code != current_code:
                    current_code = optimized_code
                    all_responses.append(f"[{opt_type}]: {response[:100]}...")
                else:
                    all_responses.append(f"[{opt_type}]: No changes applied")
            except Exception as e:
                logger.warning(f"Optimization {opt_type} failed: {e}")
                all_responses.append(f"[{opt_type}]: Failed - {str(e)}")
        
        return current_code, "\n".join(all_responses)
    
    def _apply_optimization(self, code: str, opt_type: str) -> Tuple[str, str]:
        """应用单个优化"""
        prompt = get_prompt(f'optimize_{opt_type}')
        
        if not prompt:
            # 使用默认prompt
            if opt_type == 'simplify':
                prompt_content = (
                    "Simplify the following C code by removing redundant variables and unnecessary code. "
                    "Preserve exact semantics. Return only the optimized code:\n\n{code}"
                )
            elif opt_type == 'comment':
                prompt_content = (
                    "Add helpful comments to the following C code explaining the purpose and logic. "
                    "Return the code with comments:\n\n{code}"
                )
            elif opt_type == 'rename':
                prompt_content = (
                    "Rename variables in the following C code to have more meaningful names. "
                    "Preserve exact semantics. Return only the optimized code:\n\n{code}"
                )
            else:
                return code, f"Unknown optimization type: {opt_type}"
        else:
            prompt_content = prompt['content']
        
        try:
            response = self.llm.query(prompt_content.format(code=code))
            
            # 提取代码
            optimized_code = self._extract_code(response, code)
            
            return optimized_code, response
        except Exception as e:
            logger.error(f"Optimization {opt_type} failed: {e}")
            return code, f"Error: {str(e)}"
    
    def _extract_code(self, response: str, original_code: str) -> str:
        """从响应中提取代码"""
        # 尝试提取代码块
        code_block_pattern = r'```(?:c|C)?\s*\n(.*?)\n```'
        match = re.search(code_block_pattern, response, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        # 如果没有代码块，检查是否包含原始代码
        if is_code_in_response(original_code, response):
            try:
                # 尝试提取函数定义
                cc = CCode(response)
                funcs = cc.get_by_type_name('function_definition')
                if funcs:
                    return funcs[0].src
            except:
                pass
        
        # 如果都失败，返回过滤后的响应
        return response_filter(response)


class DualRoleModel:
    """
    二角色模型：Analyzer + Optimizer
    """
    
    def __init__(self, *, decompile_code: Optional[str] = None, src_code: Optional[str] = None):
        """
        Args:
            decompile_code: 反编译输出的代码
            src_code: 源代码（用于评估，可选）
        """
        self.code = decompile_code
        self.src_code = src_code
        self.analyzer = Analyzer()
        self.optimizer = Optimizer()
    
    def work(self) -> Dict:
        """
        执行优化工作流
        
        Returns:
            包含优化结果的字典
        """
        result = {
            'source_code': self.src_code,
            'decompiler_output': self.code,
            'workflow': 'INIT'
        }
        
        if not self.code:
            result['workflow'] = 'ERROR'
            result['error'] = 'No code provided'
            return result
        
        try:
            # 步骤1: 分析
            logger.info('[DualRoleModel] Starting analysis...')
            analysis_text, optimizations = self.analyzer.analyze(self.code)
            result['analysis'] = analysis_text
            result['optimizations_needed'] = optimizations
            result['workflow'] = 'ANALYZED'
            
            logger.info(f'[DualRoleModel] Optimizations needed: {optimizations}')
            
            # 步骤2: 优化
            logger.info('[DualRoleModel] Starting optimization...')
            optimized_code, optimization_response = self.optimizer.optimize(self.code, optimizations)
            result['optimized_code'] = optimized_code
            result['optimization_response'] = optimization_response
            result['workflow'] = 'DONE'
            result['output'] = optimized_code
            
            logger.info('[DualRoleModel] Optimization completed')
            
        except Exception as e:
            logger.error(f'[DualRoleModel] Error: {e}')
            logger.error(traceback.format_exc())
            result['workflow'] = 'ERROR'
            result['error'] = str(e)
            result['output'] = self.code  # 返回原始代码
        
        return result


def dual_role_optimize(decompile_code: str) -> Dict:
    """使用二角色模型优化代码"""
    model = DualRoleModel(decompile_code=decompile_code)
    return model.work()

