"""
构建 cinspector-tree-sitter.so 文件
在Windows上运行此脚本来生成解析器库
"""
import os
import sys
import subprocess
from pathlib import Path

def build_parser():
    """构建 tree-sitter C 解析器"""
    # 获取当前脚本所在目录
    script_dir = Path(__file__).parent
    cinspector_dir = script_dir / 'cinspector'
    
    # 切换到 cinspector 目录
    os.chdir(cinspector_dir)
    
    print(f"当前工作目录: {os.getcwd()}")
    print("开始构建 cinspector-tree-sitter.so...")
    
    # 检查是否已存在 tree-sitter-c 目录
    tree_sitter_c_dir = Path('tree-sitter-c')
    if not tree_sitter_c_dir.exists():
        print("正在克隆 tree-sitter-c...")
        try:
            subprocess.check_call([
                'git', 'clone', '-b', 'v0.20.2',
                'https://github.com/tree-sitter/tree-sitter-c.git'
            ])
        except subprocess.CalledProcessError as e:
            print(f"错误: 无法克隆 tree-sitter-c: {e}")
            print("请确保已安装 git 并且可以访问 GitHub")
            return False
    else:
        print("tree-sitter-c 目录已存在，跳过克隆")
    
    # 构建库
    print("正在构建解析器库...")
    try:
        from tree_sitter import Language
        
        # 在Windows上，tree-sitter会生成 .pyd 或 .dll 文件
        # 但代码期望 .so 文件，所以我们需要处理这个问题
        output_file = 'cinspector-tree-sitter.so'
        
        Language.build_library(
            output_file,
            ['tree-sitter-c']
        )
        
        # 检查生成的文件
        if os.path.exists(output_file):
            print(f"[成功] 成功构建: {output_file}")
            return True
        else:
            # 在Windows上可能生成了 .pyd 或 .dll 文件
            pyd_file = output_file.replace('.so', '.pyd')
            dll_file = output_file.replace('.so', '.dll')
            
            if os.path.exists(pyd_file):
                print(f"[信息] 发现 {pyd_file}，重命名为 {output_file}")
                os.rename(pyd_file, output_file)
                return True
            elif os.path.exists(dll_file):
                print(f"[信息] 发现 {dll_file}，重命名为 {output_file}")
                os.rename(dll_file, output_file)
                return True
            else:
                # 检查是否有其他扩展名的文件
                base_name = output_file.replace('.so', '')
                for ext in ['.pyd', '.dll', '.so']:
                    test_file = base_name + ext
                    if os.path.exists(test_file):
                        print(f"[信息] 发现 {test_file}，复制为 {output_file}")
                        import shutil
                        shutil.copy2(test_file, output_file)
                        return True
                
                print("[错误] 未找到生成的库文件")
                print(f"[调试] 当前目录: {os.getcwd()}")
                print(f"[调试] 查找的文件: {output_file}")
                return False
                
    except ImportError:
        print("错误: 未安装 tree-sitter 包")
        print("请运行: pip install tree-sitter==0.20.4")
        return False
    except Exception as e:
        print(f"错误: 构建失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = build_parser()
    if success:
        print("\n构建完成！")
    else:
        print("\n构建失败，请检查错误信息")
        sys.exit(1)

