#!/usr/bin/env python3
"""
视频分析可视化工具启动脚本
"""

if __name__ == "__main__":
    try:
        from main_window import main
        main()
    except ImportError as e:
        print(f"导入错误: {e}")
        print("请确保已安装所有依赖包:")
        print("pip install -r requirements.txt")
    except Exception as e:
        print(f"程序启动失败: {e}")
        input("按回车键退出...") 