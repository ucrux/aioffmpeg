import constval
from aioffmpeg.h264video import H264Video
from aioffmpeg.cmd_opts import H264EncoderArgs, FfmpegCmdModel

import pytest
import os
import random


@pytest.mark.asyncio
async def test_delog_video_aio():
    """
    测试视频缩放
    :return:
    """
    print('')
    h264_obj = H264Video(constval.VIDEO, constval.OUTPUT_DIR, aio=True)
    print('current work dir', os.path.abspath(os.getcwd()))
    home_dir = os.path.abspath(os.getenv('HOME'))
    delog_args = tuple([
                        H264Video.create_delog_args(random.randint(0, 600),
                                                    random.randint(0, 1000),
                                                    random.randint(0, 300),
                                                    random.randint(0, 300),
                                                    random.randint(0, 100),
                                                    random.randint(100, 200))
        for i in range(10)])
    delog_obj, stderr = await h264_obj.cmd_do_aio(f'{home_dir:}', 'mp4', FfmpegCmdModel.del_log,
                                                  delog_tuple=delog_args,
                                                  encode_lib=constval.CODEC)
    assert delog_obj is not None and stderr == ''
    print('H264Video object info:', delog_obj)
    print(f'out put video width:{delog_obj.video_width:d},video height:{delog_obj.video_height:d},'
          f'video bit rate:{delog_obj.video_bitrate:d}')


def test_delog_video():
    """
    测试视频缩放
    :return:
    """
    print('')
    h264_obj = H264Video(constval.VIDEO, constval.OUTPUT_DIR, aio=True)
    print('current work dir', os.path.abspath(os.getcwd()))
    home_dir = os.path.abspath(os.getenv('HOME'))
    delog_args = tuple([
                        H264Video.create_delog_args(random.randint(0, 600),
                                                    random.randint(0, 1000),
                                                    random.randint(0, 300),
                                                    random.randint(0, 300),
                                                    random.randint(0, 100),
                                                    random.randint(100, 200))
        for i in range(10)])
    delog_obj, stderr = h264_obj.cmd_do(f'{home_dir:}', 'mp4', FfmpegCmdModel.del_log,
                                        delog_tuple=delog_args,
                                        encode_lib=constval.CODEC)
    assert delog_obj is not None and stderr == ''
    print('H264Video object info:', delog_obj)
    print(f'out put video width:{delog_obj.video_width:d},video height:{delog_obj.video_height:d},'
          f'video bit rate:{delog_obj.video_bitrate:d}')
