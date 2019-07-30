import constval
from aioffmpeg.h264video import H264Video
from aioffmpeg.cmd_opts import H264EncoderArgs, FfmpegCmdModel

import pytest
import os
import random

@pytest.mark.asyncio
async def test_hls_video_qsv_aio():
    """
    测试视频缩放
    :return:
    """
    print('')
    h264_obj = H264Video(constval.VIDEO, constval.OUTPUT_DIR, aio=True)
    home_dir = os.getenv('HOME')
    video_bitrate = random.randint(100, 400)
    ts_time = random.randint(5,15)
    print('current work dir', os.path.abspath(os.getcwd()))
    m3u8path, stderr = await h264_obj.cmd_do_aio(f'{home_dir:s}', 'm3u8', FfmpegCmdModel.hls_video_qsv,
                                                 target_videobitrate=video_bitrate,
                                                 target_height=random.randint(100,300),
                                                 ts_time=ts_time,
                                                 ts_prefix='test-ts-aio')

    assert m3u8path is not None and stderr == ''
    print('m3u8 path:', m3u8path)
    print(f'out put video bit rate:{video_bitrate:d},ts seg time:{ts_time:d}')


def test_hls_video():
    """
    测试视频缩放
    :return:
    """
    print('')
    h264_obj = H264Video(constval.VIDEO, constval.OUTPUT_DIR, aio=False)
    home_dir = os.getenv('HOME')
    assert not hasattr(h264_obj, 'cmd_do_aio')
    video_bitrate = random.randint(100, 400)
    ts_time = random.randint(5,15)
    print('current work dir', os.path.abspath(os.getcwd()))
    m3u8path, stderr = h264_obj.cmd_do(f'{home_dir:s}', 'm3u8', FfmpegCmdModel.hls_video_qsv,
                                       target_videobitrate=video_bitrate,
                                       target_height=random.randint(100,300),
                                       ts_time=ts_time,
                                       ts_prefix='test-ts')

    assert m3u8path is not None and stderr == ''
    print('m3u8 path:', m3u8path)
    print(f'out put video bit rate:{video_bitrate:d},ts seg time:{ts_time:d}')
