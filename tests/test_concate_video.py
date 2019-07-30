import constval
from aioffmpeg.h264video import H264Video
from aioffmpeg.cmd_opts import H264EncoderArgs, FfmpegCmdModel

import pytest
import os
import random

@pytest.mark.asyncio
async def test_concat_video_aio():
    """
    测试视频缩放
    :return:
    """
    print('')
    h264_obj = H264Video(constval.VIDEO, constval.OUTPUT_DIR, aio=True)
    h264_obj1 = H264Video(constval.VIDEO1, constval.OUTPUT_DIR, aio=True)
    print('current work dir', os.path.abspath(os.getcwd()))
    home_dir = os.path.abspath(os.getenv('HOME'))
    concat_video, stderr = await h264_obj.cmd_do_aio(f'{home_dir:s}', 'mp4', FfmpegCmdModel.concat_video,
                                                     input_obj=h264_obj1,
                                                     encode_lib=constval.CODEC)
    # print(stderr)
    assert concat_video is not None and stderr == ''
    print('H264Video object info:', concat_video)
    print(f'out put video width:{concat_video.video_width:d},video height:{concat_video.video_height:d},'
          f'video bit rate:{concat_video.video_bitrate:d}')
    add_test1 = h264_obj + h264_obj1
    add_test2 = h264_obj1 + h264_obj
    print('add_test1 H264Video object info:', add_test1)
    print(f'add_test1 out put video width:{add_test1.video_width:d},video height:{add_test1.video_height:d},'
          f'video bit rate:{add_test1.video_bitrate:d}')
    print('add_test2 H264Video object info:', add_test2)
    print(f'add_test2 out put video width:{add_test2.video_width:d},video height:{add_test2.video_height:d},'
          f'video bit rate:{add_test2.video_bitrate:d}')


def test_concat_video():
    """
    测试视频缩放
    :return:
    """
    print('')
    h264_obj = H264Video(constval.VIDEO, constval.OUTPUT_DIR, aio=True)
    h264_obj1 = H264Video(constval.VIDEO1, constval.OUTPUT_DIR, aio=True)
    print('current work dir', os.path.abspath(os.getcwd()))
    home_dir = os.path.abspath(os.getenv('HOME'))
    concat_video, stderr = h264_obj.cmd_do(f'{home_dir:s}', 'mp4', FfmpegCmdModel.concat_video,
                                           input_obj=h264_obj1,
                                           encode_lib=constval.CODEC)
    # print(stderr)
    assert concat_video is not None and stderr == ''
    print('H264Video object info:', concat_video)
    print(f'out put video width:{concat_video.video_width:d},video height:{concat_video.video_height:d},'
          f'video bit rate:{concat_video.video_bitrate:d}')
    add_test1 = h264_obj + h264_obj1
    add_test2 = h264_obj1 + h264_obj
    print('add_test1 H264Video object info:', add_test1)
    print(f'add_test1 out put video width:{add_test1.video_width:d},video height:{add_test1.video_height:d},'
          f'video bit rate:{add_test1.video_bitrate:d}')
    print('add_test2 H264Video object info:', add_test2)
    print(f'add_test2 out put video width:{add_test2.video_width:d},video height:{add_test2.video_height:d},'
          f'video bit rate:{add_test2.video_bitrate:d}')
