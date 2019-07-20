import constval
from aioffmpeg.h264video import H264Video
from aioffmpeg.cmd_opts import H264EncoderArgs, FfmpegCmdModel

import pytest
import os
import random


@pytest.mark.asyncio
async def test_dl_m3u8_aio():
    """
    测试下载m3u8
    :return:
    """
    print('')
    result, stderr = await H264Video.download_m3u8_aio(constval.FFMPEG_BIN, 
                            r'/home/ucrux/5b9668b0-a960-11e9-92fd-000c29ac26a7.m3u8',
                            r'/tmp/out0.mp4')
    assert not result and stderr != ''
    print(stderr)
    result, stderr = await H264Video.download_m3u8_aio(constval.FFMPEG_BIN, 
                            r'http://cdn2.pangzitv.com/upload/20180528/5deac534a230bf7ce707d2e913886b3e/5deac534a230bf7ce707d2e913886b3e.m3u8', 
                            r'/tmp/out1.mp4')
    assert result and stderr == ''

