"""
测试 cinspector 是否能正常工作
"""
import os
import sys

# 添加路径
DIR = os.path.dirname(os.path.abspath(__file__))
CINSPECTOR_DIR = os.path.join(os.path.dirname(DIR), 'cinspector', 'cinspector')
sys.path.insert(0, os.path.join(os.path.dirname(DIR), 'cinspector'))

print(f"测试 cinspector 模块...")
print(f"Cinspector 目录: {CINSPECTOR_DIR}")

# 检查 .so 文件
so_file = os.path.join(CINSPECTOR_DIR, 'cinspector-tree-sitter.so')
print(f"\n1. 检查 .so 文件:")
print(f"   路径: {so_file}")
print(f"   存在: {os.path.exists(so_file)}")
if os.path.exists(so_file):
    print(f"   大小: {os.path.getsize(so_file)} bytes")

# 尝试导入
print(f"\n2. 尝试导入 cinspector...")
try:
    from cinspector.interfaces import CCode
    print("   ✓ 成功导入 CCode")
except Exception as e:
    print(f"   ✗ 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 测试解析
print(f"\n3. 测试代码解析...")
try:
    test_code = "int main() { return 0; }"
    cc = CCode(test_code)
    print("   ✓ 成功解析代码")
    
    # 获取函数定义
    funcs = cc.get_by_type_name('function_definition')
    print(f"   ✓ 找到 {len(funcs)} 个函数定义")
except Exception as e:
    print(f"   ✗ 解析失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print(f"\n✓ 所有测试通过！cinspector 工作正常。")





