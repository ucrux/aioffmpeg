#!/usr/bin/env python
# -*- coding: utf-8 -*-

from aioffmpeg._cmd_raw_str import *

# h264编码参数选项
class H264EncoderArgs():
    """
    h.264 编码的一些参数
    ; -profile:v
    ; -level
    ; -preset
    ; -crf
    ; -c:v
    ; -r
    如果ffmpeg编译时加了external的libx264,那就这么写:
    aioffmpeg -i input.mp4 -c:v libx264 -x264-params "profile=high:level=3.0" output.mp4
    aioffmpeg -i input -c:v libx264 -profile:v main -preset:v fast -level 3.1 -x264opts crf=18
    """

    """
    c:v 参数,h.264 video使用编码库
    """
    codec_v_libx264 = 'libx264'
    codec_v_h264_nvenc = 'h264_nvenc'

    """
    profile 参数 H.264 Baseline profile,Extended profile和Main profile都是针对8位样本数据,4:2:0格式(YUV)的视频序列
    在相同配置情况下,High profile(HP)可以比Main profile(MP)降低10%的码率
    根据应用领域的不同,Baseline profile多应用于实时通信领域,Main profile多应用于流媒体领域,High profile则多应用于广电和存储领域
    """
    profile_baseline = 'baseline'  # 基本画质.支持I/P帧,只支持无交错(Progressive)和CAVLC
    profile_extended = 'extended'  # 进阶画质.支持I/P/B/SP/SI帧,只支持无交错(Progressive)和CAVLC
    profile_main = 'main'          # 主流画质.提供I/P/B帧,支持无交错(Progressive)和交错(Interlaced),也支持CAVLC和CABAC
    profile_high = 'high'          # 高级画质.在main Profile的基础上增加了8x8内部预测,自定义量化,无损视频编码和更多的YUV格式
    profile_high10 = 'high10'
    profile_high422 = 'high422'
    profile_high444 = 'high444'
    """
    level 参数定义可以使用的最大帧率,码率和分辨率
              level        max          max          max bitrate          max bitrate      high resolution
              number    macroblocks    frame      for profile baseline    for profile        @frame rate
                         per secs      size        extended main high         high
    """
    level_1 = '1'      #   1485         99             64 kbit/s           80 kbit/s         128x96@30.9
                       #                                                                     176x144@15.0
    level_1b = '1b'    #   1485         99            128 kbit/s           160 kbit/s        128x96@30.9
                       #                                                                     176x144@15.0
    level_1_1 = '1.1'  #   3000        396            192 kbit/s           240 kbit/s        176x144@30.3
                       #                                                                     320x240@10.0
                       #                                                                     352x288@7.5
    level_1_2 = '1.2'  #   6000        396            384 kbit/s           480 kbit/s        320x240@20.0
                       #                                                                     352x288@15.2
    level_1_3 = '1.3'  #   11880       396            768 kbit/s           960 kbit/s        320x240@36.0
                       #                                                                     352x288@30.0
    level_2 = '2'      #   11880       396            2 Mbit/s             2.5 Mbit/s        320x240@36.0
                       #                                                                     352x288@30.0
    level_2_1 = '2.1'  #   19880       792            4 Mbit/s             5 Mbit/s          352x480@30.0
                       #                                                                     352x576@25.0
    level_2_2 = '2.2'  #   20250       1620           4 Mbit/s             5 Mbit/s          352x480@30.7
                       #                                                                     352x576@25.6
                       #                                                                     720x480@15.0
                       #                                                                     720x576@12.5
    level_3 = '3'      #   40500       1620           10 Mbit/s            12.5 Mbit/s       352x480@61.4
                       #                                                                     352x576@51.1
                       #                                                                     720x480@30.0
                       #                                                                     720x576@25.0
    level_3_1 = '3.1'  #   108000      3600           14 Mbit/s            17.5 Mbit/s       720x480@80.0
                       #                                                                     720x576@66.7
                       #                                                                     1280x720@30.0
    level_3_2 = '3.2'  #   216000      5120           20 Mbit/s            25 Mbit/s         1280x720@60.0
                       #                                                                     1280x1024@42.2
    level_4 = '4'      #   245760      8192           20 Mbit/s            25 Mbit/s         1280x720@68.3
                       #                                                                     1920x1088@30.1
                       #                                                                     2048x1024@30.0
    level_4_1 = '4.1'  #   245760      8192           50 Mbit/s            50 Mbit/s         1280x720@68.3
                       #                                                                     1920x1088@30.1
                       #                                                                     2048x1024@30.00
    level_4_2 = '4.2'  #   522240      8704           50 Mbit/s            50 Mbit/s         1280x1088@64.0
                       #                                                                     2048x1088@60.0
    level_5 = '5'      #   589824      22080          135 Mbit/s           168.75 Mbit/s     1920x1088@72.3
                       #                                                                     2048x1024@72.0
                       #                                                                     2048x1088@67.8
                       #                                                                     2560x1920@30.7
                       #                                                                     3680x1536@26.7
    level_5_1 = '5.1'  #   983040      36864          240 Mbit/s           300 Mbit/s        1920x1088@120.5
                       #                                                                     4096x2048@30.0
                       #                                                                     4096x2304@26.7
    """
    preset 参数
    调整编码速度,越慢编码质量越高
    ultrafast,superfast,veryfast,faster,fast,medium,slow,slower,veryslow and placebo
    """
    preset_ultrafast = 'ultrafast'
    preset_superfast = 'superfast'
    preset_veryfast = 'veryfast'
    preset_faster = 'faster'
    preset_fast = 'fast'
    preset_medium = 'medium'
    preset_slow = 'slow'
    preset_slower = 'slower'
    preset_veryslow = 'veryslow'
    # preset_placebo = 'placebo'
    """
    crf 参数
    CRF(Constant Rate Factor)
    范围 0-51: 
      - 0是编码毫无丢失信息
      - 23 is 默认
      - 51 是最差的情况
    相对合理的区间是18-28. 
    值越大,压缩效率越高,但也意味着信息丢失越严重,输出图像质量越差
    crf每+6，比特率减半
    crf每-6，比特率翻倍
    """
    crf_0 = 0
    crf_18 = 18
    crf_23 = 23
    crf_28 = 28
    crf_51 = 51
    """
    视频帧率
    """
    # gif用
    v_frame_5 = 5
    v_frame_8 = 8
    v_frame_15 = 15
    # 视频用
    v_frame_30 = 30
    v_frame_24 = 24
    """
    视频旋转方向参数
    """
    v_left_rotate = 2
    v_right_rotate = 1
    """
    是否固定ts切片的时长
    """
    no_fix_ts_time = ''
    fix_ts_time = '+split_by_time'
    """
    音频码率
    """
    audio_rate_64 = 64
    audio_rate_128 = 128
    """
    图片水印模版
    """
    # 固定图片水印位置
    water_mark_fix = 0
    water_mark_move = 1


class FfmpegCmdModel:
    check_h264 = CMD_CHECK_H264
    get_video_probe = CMD_GET_VIDEO_PROBE
    ch_video_metadata = CMD_CH_VIDEO_METADATA
    scale_video = CMD_SCALE_VIDEO_CODECS
    rotate_video = CMD_ROTATE_VIDEO
    hls_video = CMD_HLS_VIDEO
    hls_video_other = CMD_HLS_VIDEO_OTHER
    snapshot_video = CMD_SNAPSHOT
    cut_video = CMD_CUT_VIDEO
    concat_video = CMD_CONCAT_VIDEO
    concat_video_safe = CMD_CONCAT_VIDEO_SAFE
    logo_video_fix = CMD_LOGO_FIX
    logo_video_move = CMD_LOGO_MOVE
    del_log = CMD_DEL_LOGO
    create_gif = CMD_GIF_VIDEO


class FfmpegOptsModel:
    matedata = OPTS_MATEDATA
    pad_left_right = OPTS_PAD_LR
    pad_up_down = OPTS_PAD_UD
    del_log = OPTS_DEL_LOGO
    ass = OPTS_ASS

