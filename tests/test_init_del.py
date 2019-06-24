import constval
from aioffmpeg.h264video import H264Video

import pytest
import os




def test_init_del():
    """
    测试初始化
    验证 视频文件 在资源释放是是否会被删除
    :param tmpdir: 临时目录, 由 pytest 管理
    :return:
    """
    assert all((os.path.isfile(constval.VIDEO),
                os.path.isfile(constval.FFMPEG_BIN),
                os.path.isfile(constval.FFPROBE_BIN),
                os.path.isfile(constval.VIDEO_DUMMY),
                os.path.isfile(constval.FFMPEG_BIN_DUMMY),
                os.path.isfile(constval.FFPROBE_BIN_DUMMY)))
    h264video_obj = H264Video(constval.VIDEO, constval.OUTPUT_DIR, constval.FFMPEG_BIN, constval.FFPROBE_BIN, True)
    assert any((h264video_obj.libx264, h264video_obj.h264_nvenc))
    attr_list = ['libx264', 'h264_nvenc', 'output_dir', 'video_codecname', 'video_profile', 'video_width',
                 'video_height', 'video_pixfmt', 'video_avgframerate', 'video_bitrate', 'audio_codecname',
                 'audio_profile', 'audio_samplefmt', 'audio_samplerate', 'audio_channels', 'audio_bitrate',
                 'videofile_path', 'videofile_duration', 'videofile_size', 'videofile_formatname']
    assert all([hasattr(h264video_obj, attr) for attr in attr_list])
    del h264video_obj
    # 下面进行初始化异常测试
    # 视频文件异常
    with pytest.raises(ChildProcessError):
        H264Video(constval.VIDEO_DUMMY, constval.OUTPUT_DIR, constval.FFMPEG_BIN, constval.FFPROBE_BIN)
    # FFMPEG_BIN 异常
    with pytest.raises(ChildProcessError):
        H264Video(constval.VIDEO_DUMMY, constval.OUTPUT_DIR, constval.FFMPEG_BIN, constval.FFPROBE_BIN)
    # FFPROBE_BIN 异常
    with pytest.raises(ChildProcessError):
        H264Video(constval.VIDEO, constval.OUTPUT_DIR, constval.FFMPEG_BIN, constval.FFPROBE_BIN_DUMMY)
    with pytest.raises(FileNotFoundError):
        H264Video(constval.VIDEO_NOT_EXIST, constval.OUTPUT_DIR, constval.FFMPEG_BIN_NOT_EXIST,
                  constval.FFPROBE_BIN_NOT_EXIST)
    with pytest.raises(FileNotFoundError):
        H264Video(constval.VIDEO, constval.OUTPUT_DIR_NOT_EXIST, constval.FFMPEG_BIN, constval.FFPROBE_BIN)
