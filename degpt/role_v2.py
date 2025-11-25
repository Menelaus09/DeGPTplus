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
from mssc import check_with_mssc
from role import Referee, Advisor, Operator, DType

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
    
    def optimize(self, code: str, opt_types: List[str] = None,
                mssc_stats: Optional[Dict[str, int]] = None) -> Tuple[str, str]:
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
                # 如有 MSSC 统计对象，则在采纳前进行语义校验
                if optimized_code and optimized_code != current_code:
                    if mssc_stats is not None:
                        accepted = check_with_mssc(current_code, optimized_code, mssc_stats)
                        if accepted:
                            current_code = optimized_code
                            all_responses.append(f"[{opt_type}]: MSSC accepted, change applied. {response[:80]}...")
                        else:
                            all_responses.append(f"[{opt_type}]: MSSC rejected, change discarded.")
                    else:
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
    
    def __init__(self, *, decompile_code: Optional[str] = None, src_code: Optional[str] = None,
                 mssc_stats: Optional[Dict[str, int]] = None):
        """
        Args:
            decompile_code: 反编译输出的代码
            src_code: 源代码（用于评估，可选）
        """
        self.code = decompile_code
        self.src_code = src_code
        self.analyzer = Analyzer()
        self.optimizer = Optimizer()
        # 可选 MSSC 统计对象，由上层统一创建和汇总
        self.mssc_stats: Optional[Dict[str, int]] = mssc_stats
    
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
            optimized_code, optimization_response = self.optimizer.optimize(
                self.code,
                optimizations,
                mssc_stats=self.mssc_stats,
            )
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
    """使用二角色模型优化代码（兼容旧接口，不启用 MSSC 统计）"""
    model = DualRoleModel(decompile_code=decompile_code, mssc_stats=None)
    return model.work()


class Transformer:
    """
    方案 B 中的 Transformer：根据 Referee 的 directions 一次性完成必要的转化。
    """

    def __init__(self):
        self.llm = QueryChatGPT()
        self.llm.insert_system_prompt(
            'You are an expert C code transformer. Based on given directions, '
            'perform minimal necessary changes to the code while preserving semantics. '
            'Return only the final C code.'
        )
        # Transformer 优先使用 Qwen-Plus（或配置中指定的模型）
        try:
            # 如果未来单独为 Qwen 配置段，可以在此处调整
            self.model = load_config('LLM', 'model')
        except Exception:
            self.model = None

    def _build_prompt(self, code: str, directions_str: str, strengthen: bool = False) -> str:
        prompt = get_prompt('transform_b')
        if not prompt:
            base = (
                "You are given C code and high-level optimization directions.\n"
                "Directions: {directions}\n"
                "Directions may include: SIMPLIFY, ADD_COMMENT, RENAME_VAR.\n"
                "Apply only the necessary changes implied by the directions, keep control flow and semantics intact,\n"
                "and return ONLY the final C code (you may use a ```c code block). Code:\n\n{code}"
            )
        else:
            base = prompt['content']

        if strengthen:
            # 强化约束：在存在 directions 时，必须做出肉眼可见的改动
            base += (
                "\n\nIMPORTANT:\n"
                "- Directions are NOT empty, so you MUST apply at least one visible change implied by them.\n"
                "- Do NOT return code that is identical to the input (beyond trivial whitespace).\n"
            )

        return base.format(code=code, directions=directions_str)

    @staticmethod
    def _normalized(code: str) -> str:
        # 去掉空白用于粗略判断“是否有实质改动”
        return ''.join(code.split())

    def transform(self, code: str, directions: List[DType]) -> Tuple[str, str]:
        dir_names = [d.value if isinstance(d, DType) else str(d) for d in directions]
        directions_str = ', '.join(dir_names) if dir_names else 'NONE'

        # 第一次尝试
        prompt_content = self._build_prompt(code, directions_str, strengthen=False)
        response = self.llm.query(prompt_content, model=self.model) if self.model else self.llm.query(prompt_content)
        optimized_code = self._extract_code(response, code)

        # 如果 Referee 认为需要优化（directions 非空），但代码实质上没有变化，则进行一次强化重试
        if directions and self._normalized(optimized_code) == self._normalized(code):
            strong_prompt = self._build_prompt(code, directions_str, strengthen=True)
            response_strong = self.llm.query(strong_prompt, model=self.model) if self.model else self.llm.query(strong_prompt)
            optimized_code_strong = self._extract_code(response_strong, code)

            # 只要第二次输出与原始不同，就采用强化版本
            if self._normalized(optimized_code_strong) != self._normalized(code):
                return optimized_code_strong, response_strong
            # 否则退回第一次结果，并由上层通过额外字段标记“无改动”
            return optimized_code, response_strong

        return optimized_code, response

    def _extract_code(self, response: str, original_code: str) -> str:
        # 与 Optimizer._extract_code 保持一致的提取逻辑
        code_block_pattern = r'```(?:c|C)?\s*\n(.*?)\n```'
        match = re.search(code_block_pattern, response, re.DOTALL)
        if match:
            return match.group(1).strip()

        if is_code_in_response(original_code, response):
            try:
                cc = CCode(response)
                funcs = cc.get_by_type_name('function_definition')
                if funcs:
                    return funcs[0].src
            except Exception:
                pass

        return response_filter(response)


class TwoRoleModeB:
    """
    二角色方案 B：Referee + Transformer
    """

    def __init__(self, *, decompile_code: Optional[str] = None, src_code: Optional[str] = None,
                 mssc_stats: Optional[Dict[str, int]] = None):
        self.code = decompile_code
        self.src_code = src_code
        self.referee = Referee()
        self.transformer = Transformer()
        self.mssc_stats: Optional[Dict[str, int]] = mssc_stats

    def work(self) -> Dict:
        result: Dict = {
            'source_code': self.src_code,
            'decompiler_output': self.code,
            'workflow': 'TWO_ROLE_B',
        }
        if not self.code:
            result['workflow'] = 'ERROR'
            result['error'] = 'No code provided'
            return result

        try:
            analysis_text, directions = self.referee.get_direction(self.code)
            result['analysis'] = analysis_text
            direction_values = [d.value if isinstance(d, DType) else str(d) for d in directions]
            result['directions'] = direction_values

            candidate_code, raw_resp = self.transformer.transform(self.code, directions)
            result['llm_raw_response'] = raw_resp

            # 软门禁：始终展示 Transformer 生成的 candidate_code，
            # MSSC 仅用于标记语义风险，不再强制回退到原始代码。
            if self.mssc_stats is not None:
                accepted = check_with_mssc(self.code, candidate_code, self.mssc_stats)
            else:
                accepted = None

            result['optimized_code'] = candidate_code
            if accepted is True:
                result['mssc_status'] = 'ACCEPTED'
            elif accepted is False:
                result['mssc_status'] = 'REJECTED'
            else:
                result['mssc_status'] = 'UNKNOWN'

            # 如果在 directions 非空的情况下，candidate 与 original 完全一致，标记为无改动
            if directions and Transformer._normalized(candidate_code) == Transformer._normalized(self.code):
                result['transformer_status'] = 'TRANSFORMER_NO_CHANGE'

            # 构建 optimizations 字典，根据 directions 创建条目
            optimizations: Dict[str, Dict] = {}
            direction_map = {
                'SIMPLIFY': 'SIMPLIFY',
                'ADD_COMMENT': 'ADD_COMMENT',
                'RENAME_VAR': 'RENAME_VAR',
            }
            
            # 尝试从响应中提取重命名变量的映射（如果存在）
            rename_map = None
            if 'RENAME_VAR' in [d.value if isinstance(d, DType) else str(d) for d in directions]:
                # 尝试从响应中提取 JSON 格式的变量映射
                # 查找 JSON 对象模式
                json_pattern = r'\{[^{}]*"[^"]*"\s*:\s*"[^"]*"[^{}]*\}'
                json_matches = re.findall(json_pattern, raw_resp)
                for match in json_matches:
                    try:
                        parsed = json.loads(match)
                        if isinstance(parsed, dict) and len(parsed) > 0:
                            rename_map = json.dumps(parsed, ensure_ascii=False)
                            break
                    except:
                        continue
            
            # 根据 directions 创建优化条目
            for direction in directions:
                direction_key = direction.value if isinstance(direction, DType) else str(direction)
                if direction_key in direction_map:
                    opt_key = direction_map[direction_key]
                    status = 'SUCC' if accepted is not False else 'FAIL|OPERATOR'
                    
                    # 对于重命名变量，使用提取的变量映射，不设置 output（只显示变量映射）
                    if opt_key == 'RENAME_VAR':
                        if rename_map:
                            optimizations[opt_key] = {
                                'input': self.code,
                                'output': '',  # 重命名变量不显示代码，只显示变量映射
                                'status': status,
                                'advisor_response': rename_map,
                            }
                        else:
                            # 如果没有找到变量映射，仍然不显示代码
                            optimizations[opt_key] = {
                                'input': self.code,
                                'output': '',
                                'status': status,
                                'advisor_response': raw_resp,
                            }
                    else:
                        # 对于其他优化类型，显示最终代码
                        optimizations[opt_key] = {
                            'input': self.code,
                            'output': candidate_code,
                            'status': status,
                            'advisor_response': raw_resp,
                        }
            
            # 如果没有 directions，但代码有变化，创建一个综合条目
            if not optimizations and candidate_code != self.code:
                optimizations['ALL'] = {
                    'input': self.code,
                    'output': candidate_code,
                    'status': 'SUCC' if accepted is not False else 'FAIL|OPERATOR',
                    'advisor_response': raw_resp,
                }
            
            result['optimizations'] = optimizations
            result['output'] = result['optimized_code']
        except Exception as e:
            logger.error(f'[TwoRoleModeB] Error: {e}')
            logger.error(traceback.format_exc())
            result['workflow'] = 'ERROR'
            result['error'] = str(e)
            result['output'] = self.code

        return result


def one_shot_optimize(code: str, mssc_stats: Optional[Dict[str, int]] = None) -> Dict:
    """
    方案 C：One-shot 模式，一次性完成简化 / 注释 / 重命名。
    """
    llm = QueryChatGPT()
    llm.insert_system_prompt(
        'You are an expert C programmer. Improve the given decompiled C code by simplifying structure, '
        'adding helpful comments, and renaming variables to meaningful names. '
        'Keep the control flow and semantics unchanged. Return ONLY the final C code.'
    )

    prompt = get_prompt('one_shot')
    if not prompt:
        prompt_content = (
            "Improve the following C code in one shot:\n"
            "- Simplify redundant variables and code\n"
            "- Add helpful comments explaining logic\n"
            "- Rename variables to meaningful names\n"
            "Keep semantics and control flow unchanged. Return ONLY the final C code "
            "(you may use a ```c code block).\n\n{code}"
        )
    else:
        prompt_content = prompt['content']

    response = llm.query(prompt_content.format(code=code))

    # 复用与 Transformer 相同的提取逻辑
    extractor = Transformer()
    candidate_code = extractor._extract_code(response, code)

    result: Dict = {
        'original_code': code,
        'workflow': 'ONE_SHOT',
        'llm_raw_response': response,
    }

    if mssc_stats is not None:
        accepted = check_with_mssc(code, candidate_code, mssc_stats)
    else:
        accepted = True

    if accepted:
        result['optimized_code'] = candidate_code
        result['mssc_status'] = 'ACCEPTED'
    else:
        result['optimized_code'] = code
        result['mssc_status'] = 'REJECTED'

    # 构建 optimizations 字典，根据提示内容创建三个优化条目
    # One-shot 模式一次性完成所有优化，所以每个条目的 input 都是原始代码，output 都是最终代码
    optimizations: Dict[str, Dict] = {}
    status = 'SUCC' if accepted else 'FAIL|OPERATOR'
    final_code = candidate_code if accepted else code
    
    # 尝试从响应中提取重命名变量的映射（如果存在）
    rename_map = None
    # 查找 JSON 对象模式
    json_pattern = r'\{[^{}]*"[^"]*"\s*:\s*"[^"]*"[^{}]*\}'
    json_matches = re.findall(json_pattern, response)
    for match in json_matches:
        try:
            parsed = json.loads(match)
            if isinstance(parsed, dict) and len(parsed) > 0:
                rename_map = json.dumps(parsed, ensure_ascii=False)
                break
        except:
            continue
    
    # 根据提示内容，one-shot 模式会执行简化、注释、重命名三种优化
    optimizations['SIMPLIFY'] = {
        'input': code,
        'output': final_code,
        'status': status,
        'advisor_response': response,
    }
    optimizations['ADD_COMMENT'] = {
        'input': code,
        'output': final_code,
        'status': status,
        'advisor_response': response,
    }
    # 对于重命名变量，不设置 output（只显示变量映射），如果找到变量映射则使用，否则使用完整响应但不显示代码
    optimizations['RENAME_VAR'] = {
        'input': code,
        'output': '',  # 重命名变量不显示代码，只显示变量映射
        'status': status,
        'advisor_response': rename_map if rename_map else response,
    }
    
    result['optimizations'] = optimizations

    return result

