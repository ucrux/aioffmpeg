import constval
from h264video import H264Video
from aioffmpeg_cmd_opts import H264EncoderArgs, FfmpegCmdModel

import pytest
import os
import random

@pytest.mark.asyncio
async def test_logo_video_aio():
    """
    测试视频缩放
    :return:
    """
    print('')
    h264_obj = H264Video(constval.VIDEO, constval.OUTPUT_DIR, constval.FFMPEG_BIN, constval.FFPROBE_BIN, True)
    print('current work dir', os.path.abspath(os.getcwd()))
    home_dir = os.path.abspath(os.getenv('HOME'))
    ratio_img_height = random.random()
    img_position_x = random.randint(0, 1000)
    img_position_y = random.randint(0, 2000)
    print(f'ratio_img_height:{ratio_img_height:f}, '
          f'img_position_x={img_position_x:d}, img_position_y={img_position_y:d}')
    # 固定水印
    fix_video_logo, stderr = await h264_obj.cmd_do_aio(f'{home_dir:s}', 'mp4', FfmpegCmdModel.logo_video_fix,
                                                       input_img=constval.LOGO,
                                                       ratio_img_height=ratio_img_height,
                                                       img_position_x=img_position_x,
                                                       img_position_y=img_position_y,
                                                       encode_lib=constval.CODEC)
    assert fix_video_logo is not None and stderr == ''
    print('H264Video object info:', fix_video_logo)
    print(f'out put video width:{fix_video_logo.video_width:d},video height:{fix_video_logo.video_height:d},'
          f'video bit rate:{fix_video_logo.video_bitrate:d}')
    # 移动水印
    fix_video_move, stderr = await h264_obj.cmd_do_aio(f'{home_dir:s}', 'mp4', FfmpegCmdModel.logo_video_move,
                                                       input_img=constval.LOGO,
                                                       ratio_img_height=ratio_img_height,
                                                       img_position_x=img_position_x,
                                                       img_position_y=img_position_y,
                                                       encode_lib=constval.CODEC)
    assert fix_video_move is not None and stderr == ''
    print('H264Video object info:', fix_video_move)
    print(f'out put video width:{fix_video_move.video_width:d},video height:{fix_video_move.video_height:d},'
          f'video bit rate:{fix_video_move.video_bitrate:d}')


def test_logo_video():
    """
    测试视频缩放
    :return:
    """
    print('')
    h264_obj = H264Video(constval.VIDEO, constval.OUTPUT_DIR, constval.FFMPEG_BIN, constval.FFPROBE_BIN, True)
    print('current work dir', os.path.abspath(os.getcwd()))
    home_dir = os.path.abspath(os.getenv('HOME'))
    ratio_img_height = random.random()
    img_position_x = random.randint(0, 1000)
    img_position_y = random.randint(0, 2000)
    print(f'ratio_img_height:{ratio_img_height:f}, '
          f'img_position_x={img_position_x:d}, img_position_y={img_position_y:d}')
    # 固定水印
    fix_video_logo, stderr = h264_obj.cmd_do(f'{home_dir:s}', 'mp4', FfmpegCmdModel.logo_video_fix,
                                             input_img=constval.LOGO,
                                             ratio_img_height=ratio_img_height,
                                             img_position_x=img_position_x,
                                             img_position_y=img_position_y,
                                             encode_lib=constval.CODEC)
    assert fix_video_logo is not None and stderr == ''
    print('H264Video object info:', fix_video_logo)
    print(f'out put video width:{fix_video_logo.video_width:d},video height:{fix_video_logo.video_height:d},'
          f'video bit rate:{fix_video_logo.video_bitrate:d}')
    # 移动水印
    fix_video_move, stderr = h264_obj.cmd_do(f'{home_dir:s}', 'mp4', FfmpegCmdModel.logo_video_move,
                                             input_img=constval.LOGO,
                                             ratio_img_height=ratio_img_height,
                                             img_position_x=img_position_x,
                                             img_position_y=img_position_y,
                                             encode_lib=constval.CODEC)
    assert fix_video_move is not None and stderr == ''
    print('H264Video object info:', fix_video_move)
    print(f'out put video width:{fix_video_move.video_width:d},video height:{fix_video_move.video_height:d},'
          f'video bit rate:{fix_video_move.video_bitrate:d}')
