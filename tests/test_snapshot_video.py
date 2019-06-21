import constval
from h264video import H264Video
from aioffmpeg_cmd_opts import H264EncoderArgs, FfmpegCmdModel

import pytest
import os
import random

@pytest.mark.asyncio
async def test_snapshot_video_aio():
    """
    测试视频缩放
    :return:
    """
    print('')
    assert all((os.path.isfile(constval.VIDEO),
                os.path.isfile(constval.FFMPEG_BIN),
                os.path.isfile(constval.FFPROBE_BIN)))
    h264_obj = H264Video(constval.VIDEO, constval.OUTPUT_DIR, constval.FFMPEG_BIN, constval.FFPROBE_BIN, True)
    home_dir = os.getenv('HOME')
    start_time = random.random() * 100
    target_height = random.randint(120, 480)
    print(f'out put jpg start time:{start_time:f},jpg height:{target_height:d}')
    print('current work dir', os.path.abspath(os.getcwd()))
    jpgpath, stderr = await h264_obj.cmd_do_aio(f'{home_dir:s}', 'jpg', FfmpegCmdModel.snapshot_video,
                                                start_time=start_time,
                                                target_height=target_height)

    assert jpgpath is not None and stderr == ''
    print('jpg path:', jpgpath)
    # 下面测试视频批量截图
    slice_begin = random.randint(0, 120)
    slice_end = random.randint(slice_begin, 240)
    slice_count = random.randint(1, 20)
    print(f'begin: {slice_begin:d}, end: {slice_end:d}, count: {slice_count:d}')
    print(h264_obj[slice_begin:slice_end:-slice_count])


def test_snapshot_video():
    """
    测试视频缩放
    :return:
    """
    print('')
    assert all((os.path.isfile(constval.VIDEO),
                os.path.isfile(constval.FFMPEG_BIN),
                os.path.isfile(constval.FFPROBE_BIN)))
    h264_obj = H264Video(constval.VIDEO, constval.OUTPUT_DIR, constval.FFMPEG_BIN, constval.FFPROBE_BIN, False)
    assert not hasattr(h264_obj, 'cmd_do_aio')
    home_dir = os.getenv('HOME')
    start_time = random.random() * 100
    target_height = random.randint(120, 480)
    print(f'out put jpg start time:{start_time:f},jpg height:{target_height:d}')
    print('current work dir', os.path.abspath(os.getcwd()))
    jpgpath, stderr = h264_obj.cmd_do(f'{home_dir:s}', 'jpg', FfmpegCmdModel.snapshot_video,
                                      start_time=start_time,
                                      target_height=target_height)

    assert jpgpath is not None and stderr == ''
    print('jpg path:', jpgpath)
    # 下面测试视频批量截图
    slice_begin = random.randint(0, 120)
    slice_end = random.randint(slice_begin, 240)
    slice_count = random.randint(1, 20)
    print(f'begin: {slice_begin:d}, end: {slice_end:d}, count: {slice_count:d}')
    print(h264_obj[slice_begin:slice_end:-slice_count])
