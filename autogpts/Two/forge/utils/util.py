import os


def write_to_file(file_path, data):
    try:
        # 使用绝对路径
        abs_file_path = os.path.abspath(file_path)

        # 检查写入权限
        if not os.access(abs_file_path, os.W_OK):
            raise PermissionError(f"文件不可写入：{abs_file_path}")

        # 打开文件并写入数据
        with open(abs_file_path, 'w') as f:
            f.write(data)
            print(f"数据已成功写入 {abs_file_path}")

    except PermissionError as pe:
        print(f"写入文件时出错: 权限不足 - {pe}")
    except Exception as e:
        print(f"写入文件时出错: {e}")

