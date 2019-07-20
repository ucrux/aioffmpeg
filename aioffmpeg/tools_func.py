import subprocess
import asyncio


def simple_run_cmd(cmd, timeout: int = 7200) -> 'status,stdout,stderr':
    """
    普通的执行shell命令
    :param cmd: 需要执行的shell命令
    :param timeout: 命令执行超时时间
    :return:
    """
    # debug
    # print(cmd)
    # end debug
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        stdout, stderr = proc.communicate(timeout=timeout)
        try:
            stdout = stdout.decode('utf8')
            stderr = stderr.decode('utf8')
        except UnicodeDecodeError:
            stdout = 'UnicodeDecodeError'
            stderr = 'UnicodeDecodeError'
    except TimeoutError:
        proc.terminate()
        status = -1
        stderr = f'execute {cmd:s} timeout'
    else:
        status = proc.returncode
        if status != 0:
            stderr = f'execute {cmd:s} return {proc.returncode:d} and stderr -> {stderr:s}'
    return status, stdout, stderr


async def run_cmd(cmd: str) -> 'status,stdout,stderr':
    """
    执行shell命令
    :param cmd: 需要执行的shell命令
    :return: status,stdout,stderr
    """
    # debug
    # print(cmd)
    # end debug
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)
    # 不知道这里需不需要使用 try: pass; except: pass; 在官方文档上没有找到关于这个的 exception
    stdout, stderr = await proc.communicate()
    try:
        stdout = stdout.decode('utf8')
        stderr = stderr.decode('utf8')
    except UnicodeDecodeError:
        stdout = 'UnicodeDecodeError'
        stderr = 'UnicodeDecodeError'
    if proc.returncode != 0:
        stderr = f'execute {cmd:s} return {proc.returncode:d} and stderr -> {stderr:s}'
    return proc.returncode, stdout, stderr
