import subprocess
import threading
import time


def run_powershell_command_realtime(command):
    """
    实时执行PowerShell命令并显示输出
    """
    try:
        # 使用Popen启动进程，实时获取输出
        process = subprocess.Popen(
            ["powershell", "-Command", command],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,  # 行缓冲
            universal_newlines=True
        )

        # 创建线程来读取标准输出
        def read_stdout():
            for line in iter(process.stdout.readline, ''):
                print(line, end='', flush=True)
            process.stdout.close()

        # 创建线程来读取标准错误
        def read_stderr():
            for line in iter(process.stderr.readline, ''):
                print(f"错误: {line}", end='', flush=True)
            process.stderr.close()

        # 启动输出读取线程
        stdout_thread = threading.Thread(target=read_stdout)
        stderr_thread = threading.Thread(target=read_stderr)
        stdout_thread.daemon = True
        stderr_thread.daemon = True
        stdout_thread.start()
        stderr_thread.start()

        # 等待进程完成
        while process.poll() is None:
            time.sleep(0.1)

        # 等待输出线程完成
        stdout_thread.join(timeout=1)
        stderr_thread.join(timeout=1)

        return {
            "success": process.returncode == 0,
            "returncode": process.returncode
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"执行命令时发生错误: {str(e)}"
        }


def main():
    print("PowerShell命令执行器（实时输出）")
    print("输入'quit'或'exit'退出程序")
    print("-" * 40)

    while True:
        # 获取用户输入
        command = input("\n请输入PowerShell命令: ").strip()

        # 检查退出条件
        if command.lower() in ['quit', 'exit']:
            print("程序退出，再见！")
            break

        if not command:
            print("命令不能为空，请重新输入。")
            continue

        # 执行命令
        print(f"\n执行命令: {command}")
        print("输出结果:")
        print("-" * 30)

        start_time = time.time()

        # 执行命令并实时显示输出
        result = run_powershell_command_realtime(command)

        end_time = time.time()
        execution_time = end_time - start_time

        print("-" * 30)

        # 显示执行结果
        if result.get("success"):
            print(f"命令执行成功（耗时: {execution_time:.2f}秒）")
        else:
            print(f"命令执行失败（耗时: {execution_time:.2f}秒）")
            if "error" in result:
                print(f"错误信息: {result['error']}")
            print(f"退出代码: {result.get('returncode', 'N/A')}")

        print("-" * 40)


if __name__ == "__main__":
    main()