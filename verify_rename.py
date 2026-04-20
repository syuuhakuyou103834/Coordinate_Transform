"""
验证文件重命名的简单脚本
"""

def verify_files():
    """验证文件是否存在"""
    import os

    print("=" * 60)
    print("验证文件重命名")
    print("=" * 60)

    files_to_check = [
        ("core_cross_section.py", "核心功能模块"),
        ("ui_cross_section.py", "UI界面模块"),
        ("main.py", "主程序入口"),
        ("test_app.py", "测试脚本")
    ]

    all_exist = True
    for filename, description in files_to_check:
        if os.path.exists(filename):
            print(f"[OK] {filename:30s} - {description}")
        else:
            print(f"[FAIL] {filename:30s} - File not found")
            all_exist = False

    # Check if old files are deleted
    old_files = ["core.py", "ui.py"]
    print("\nCheck if old files are deleted:")
    for filename in old_files:
        if not os.path.exists(filename):
            print(f"[OK] {filename:30s} - Deleted")
        else:
            print(f"[FAIL] {filename:30s} - Still exists (should be deleted)")
            all_exist = False

    # Verify import statements
    print("\nVerify import statements:")
    try:
        with open("main.py", "r", encoding="utf-8") as f:
            content = f.read()
            if "from core_cross_section import MapDataProcessor" in content:
                print("[OK] main.py core_cross_section import is correct")
            else:
                print("[FAIL] main.py core_cross_section import is incorrect")
                all_exist = False

            if "from ui_cross_section import MapDataUI" in content:
                print("[OK] main.py ui_cross_section import is correct")
            else:
                print("[FAIL] main.py ui_cross_section import is incorrect")
                all_exist = False
    except Exception as e:
        print(f"[FAIL] Failed to read main.py: {e}")
        all_exist = False

    try:
        with open("test_app.py", "r", encoding="utf-8") as f:
            content = f.read()
            if "import core_cross_section" in content:
                print("[OK] test_app.py core_cross_section import is correct")
            else:
                print("[FAIL] test_app.py core_cross_section import is incorrect")
                all_exist = False

            if "import ui_cross_section" in content:
                print("[OK] test_app.py ui_cross_section import is correct")
            else:
                print("[FAIL] test_app.py ui_cross_section import is incorrect")
                all_exist = False
    except Exception as e:
        print(f"[FAIL] Failed to read test_app.py: {e}")
        all_exist = False

    print("\n" + "=" * 60)
    if all_exist:
        print("[SUCCESS] All verifications passed! File renaming successful!")
    else:
        print("[FAIL] Some verifications failed, please check errors above")
    print("=" * 60)

    return all_exist

if __name__ == "__main__":
    verify_files()
