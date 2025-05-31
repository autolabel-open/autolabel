import os
import tarfile
import subprocess
from datetime import datetime

def find_newest_tar_gz(path):
    """ 在给定目录中找到最新的.tar.gz文件 """
    newest_file = None
    newest_time = datetime.min
    for file in os.listdir(path):
        if file.endswith('.tar.gz'):
            file_path = os.path.join(path, file)
            file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            if file_time > newest_time:
                newest_time = file_time
                newest_file = file_path
    return newest_file

def extract_and_count_lines(tar_path, extract_dir):
    """ 解压tar.gz文件并计算解压后所有文件的行数 """
    if not tar_path:
        return
    # 解压tar.gz到指定目录
    # with tarfile.open(tar_path, 'r:gz') as tar:
    # tar.extractall(path=extract_dir)
    subprocess.run(['du', '-l', tar_path])
    return

    subprocess.run(['tar', 'xzvf', tar_path, '-C', extract_dir])
    
    sysdig_total = 0
    tshark_total = 0
    applog_total = 0

    malicious_count_applog = 0
    malicious_count_tshark = 0
    malicious_count_sysdig = 0

    # 遍历解压后的文件，并计算行数
    for root, dirs, files in os.walk(extract_dir):
        for file in files:
            file_path = os.path.join(root, file)
            # 使用wc -l命令计算文件行数
            result = subprocess.run(['wc', '-l', file_path], stdout=subprocess.PIPE, text=True)
            lines = int(result.stdout.split()[0])
            if '/sysdig/' in file_path:
                sysdig_total += lines
                count_result = subprocess.run(['grep', '-o', '"malicious": true', file_path], stdout=subprocess.PIPE).stdout.count(b'\n')
                malicious_count_sysdig += count_result
            elif '/tshark/' in file_path:
                tshark_total += lines
                count_result = subprocess.run(['grep', '-o', '"malicious": true', file_path], stdout=subprocess.PIPE).stdout.count(b'\n')
                malicious_count_tshark += count_result
            elif '/applog/' in file_path:
                applog_total += lines
                count_result = subprocess.run(['grep', '-o', '\\*MALICIOUS\\*', file_path], stdout=subprocess.PIPE).stdout.count(b'\n')
                malicious_count_applog += count_result
            print(f"文件: {file_path}, 行数: {lines}, 攻击行数: {count_result}")

    print(f"路径: {tar_path}, Sysdig 总行数: {sysdig_total}, Tshark 总行数: {tshark_total}, Applog 总行数: {applog_total}")
    print(f"Applog 中 '*MALICIOUS*' 出现次数: {malicious_count_applog}")
    print(f"Tshark 中 '\"malicious\": true' 出现次数: {malicious_count_tshark}")
    print(f"Sysdig 中 '\"malicious\": true' 出现次数: {malicious_count_sysdig}")
    # print(f"路径: {tar_path}, 解压后总行数: {total_lines}")

def main():
    search_dir = '/home/pyh/autolabel-2024/results'  # 当前目录
    extract_dir = '/tmp/tar_temp'  # 解压目录

    # 遍历当前目录及子目录
    for root, dirs, files in os.walk(search_dir):
        tar_path = find_newest_tar_gz(root)
        if tar_path:
            # print(f"处理文件: {tar_path}")
            # 确保解压目录是空的
            if os.path.exists(extract_dir):
                subprocess.run(['rm', '-rf', extract_dir])
            os.makedirs(extract_dir, exist_ok=True)
            extract_and_count_lines(tar_path, extract_dir)

if __name__ == "__main__":
    main()
