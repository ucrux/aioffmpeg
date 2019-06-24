import constval
from aioffmpeg.h264video import H264Video
from aioffmpeg.cmd_opts import H264EncoderArgs, FfmpegCmdModel

import pytest
import os
import random

@pytest.mark.asyncio
async def test_create_gif_aio():
    """
    测试视频缩放
    :return:
    """
    print('')
    h264_obj = H264Video(constval.VIDEO, constval.OUTPUT_DIR, constval.FFMPEG_BIN, constval.FFPROBE_BIN, True)
    start_time = random.random() * 100
    last_time = random.randint(int(start_time)+1, int(start_time)+50)
    target_height = random.randint(100, 720)
    print('current work dir', os.path.abspath(os.getcwd()))
    print(f'start_time: {start_time:f}, last_time: {last_time:d}, target_height: {target_height:d}, '
          f'video len: {h264_obj.videofile_duration:f}')
    print(start_time, last_time)
    home_dir = os.path.abspath(os.getenv('HOME'))
    gifpath, stderr = await h264_obj.cmd_do_aio(f'{home_dir:s}', 'gif', FfmpegCmdModel.create_gif,
                                                start_time=start_time,
                                                last_time=last_time,
                                                v_frame=5,
                                                target_height=target_height)

    assert gifpath is not None and stderr == ''
    print('jpg path:', gifpath)


def test_create_gif():
    """
    测试视频缩放
    :return:
    """
    print('')
    h264_obj = H264Video(constval.VIDEO, constval.OUTPUT_DIR, constval.FFMPEG_BIN, constval.FFPROBE_BIN, True)
    start_time = random.random() * 100
    last_time = random.randint(int(start_time)+1, int(start_time)+50)
    target_height = random.randint(100, 720)
    print('current work dir', os.path.abspath(os.getcwd()))
    print(f'start_time: {start_time:f}, last_time: {last_time:d}, target_height: {target_height:d}, '
          f'video len: {h264_obj.videofile_duration:f}')
    print(start_time, last_time)
    home_dir = os.path.abspath(os.getenv('HOME'))
    gifpath, stderr = h264_obj.cmd_do(f'{home_dir:s}', 'gif', FfmpegCmdModel.create_gif,
                                      start_time=start_time,
                                      last_time=last_time,
                                      v_frame=5,
                                      target_height=target_height)

    assert gifpath is not None and stderr == ''
    print('jpg path:', gifpath)
