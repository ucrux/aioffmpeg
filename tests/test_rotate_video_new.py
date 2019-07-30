import constval
from aioffmpeg.h264video import H264Video
from aioffmpeg.cmd_opts import H264EncoderArgs, FfmpegCmdModel

import pytest
import os
import random


@pytest.mark.asyncio
async def test_rotate_video_aio():
    """
    测试视频缩放
    :return:
    """
    print('')
    h264_obj = H264Video(constval.VIDEO, constval.OUTPUT_DIR, aio=True)
    print('current work dir', os.path.abspath(os.getcwd()))
    home_dir = os.path.abspath(os.getenv('HOME'))
    rotate_direct = H264EncoderArgs.v_left_rotate if random.randint(0, 1) == 0 else H264EncoderArgs.v_right_rotate
    print(f'rotate_drect: {rotate_direct:d}')
    scaled_obj, stderr = await h264_obj.cmd_do_aio(f'{home_dir:}', 'mp4', FfmpegCmdModel.rotate_video,
                                                   rotate_direct=rotate_direct,
                                                   target_videobitrate=random.randint(100, 400),
                                                   hwaccel=H264EncoderArgs.hwaccel_cuda,
                                                   decoder=H264EncoderArgs.decoder_h264_cuvid
                                                   encode_lib=H264EncoderArgs.codec_v_h264_nvenc)
    assert scaled_obj is not None and stderr == ''
    print('H264Video object info:', scaled_obj)
    print(f'out put video width:{scaled_obj.video_width:d},video height:{scaled_obj.video_height:d},'
          f'video bit rate:{scaled_obj.video_bitrate:d}')


def test_rotate_video():
    """
    测试视频缩放
    :return:
    """
    print('')
    h264_obj = H264Video(constval.VIDEO, constval.OUTPUT_DIR, aio=False)
    assert not hasattr(h264_obj, 'cmd_do_aio')
    print('current work dir', os.path.abspath(os.getcwd()))
    home_dir = os.path.abspath(os.getenv('HOME'))
    rotate_direct = H264EncoderArgs.v_left_rotate if random.randint(0, 1) == 0 else H264EncoderArgs.v_right_rotate
    print(f'rotate_drect: {rotate_direct:d}')
    scaled_obj, stderr = h264_obj.cmd_do(f'{home_dir:}', 'mp4', FfmpegCmdModel.rotate_video,
                                         rotate_direct=rotate_direct,
                                         target_videobitrate=random.randint(100, 400),
                                         hwaccel=H264EncoderArgs.hwaccel_cuda,
                                         decoder=H264EncoderArgs.decoder_h264_cuvid
                                         encode_lib=H264EncoderArgs.codec_v_libx264)
    assert scaled_obj is not None and stderr == ''
    print('H264Video object info:', scaled_obj)
    print(f'out put video width:{scaled_obj.video_width:d},video height:{scaled_obj.video_height:d},'
          f'video bit rate:{scaled_obj.video_bitrate:d}')
