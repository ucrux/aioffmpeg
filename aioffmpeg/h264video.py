#!/usr/bin/env python
# -*- coding: utf-8 -*-

from aioffmpeg.cmd_opts import *
from aioffmpeg._tools_func import _ffmpeg_do_cmd, _create_command, _create_command_aio
from aioffmpeg.tools_func import *

import os
import json
import time
import numbers
import random
from collections import namedtuple


class H264Video:
    """
    Basically, .h264 needs even dimensions so this filter will:
     1.Divide the original height and width by 2
     2.Round it up to the nearest pixel
     3.Multiply it by 2 again, thus making it an even number
     4.Add black padding pixels up to this number
    对ffmpeg linux 命令行工具的一个异步封装
    需要 ffmpeg 有 libx264 或 h264_nvenc 外部编码库支持
    主要功能有:
    1 视频按比例缩放填充视频
    2 旋转视频
    3 视频截图
    4 截取视频片段
    5 拼接视频
    6 HLS切片
    7 添加水印
      - 静态图片水印
      - 随机位置图片水印
    8 去除水印
      - 仅支持固定时间点,固定位置,固定大小水印
    以下是各种视频处理函数锁使用的参数
    ### 将视频做h264编码,并按要求缩放填充,且保持原视频比例
        FfmpegCmdModel.scale_video
        视频的音频部分将统一使用 acc编码 64kbit码率
        转码后的视频为 '原视频名字.timestamp.mp4'
        如果target_videobitrate超过原视频的bit_rate,将采用原视频的bit_rate
        :param output_file: 视频输出文件
        ;param prefix: two-pass log 前缀
        :param target_width: 转码后视频宽度,0使用原视频宽度
        :param target_height: 转码后视频高度,0使用原视频高度
        :param target_videobitrate: 转码后视频码率, 0使用原视频码率
        :param target_audiobitrate: 编码后音频的码率, 默认64
        :param v_frame: 转码后视频的帧率,默认24帧
        :param endcode_lib: h264编码使用的外部库
        :param preset_type: 编码速度参数
        :param crf_num: Constant Rate Factor 值
        :param profile_type: 编码配置文件
        :param level: 编码级别
    ### 对视频进行坐旋转或者右旋转,默认左旋转
        FfmpegCmdModel.rotate_video
        并按照给定的码率对视频进行编码,如果目标码率为0则使用源视频的码率
        如果target_videobitrate超过原视频的bit_rate,将采用原视频的bit_rate
        :param output_file: 视频输出目录,调用者要确保该目录存在且有写入权限
        ;param prefix: two-pass log 前缀
        :param rotate_direct: 视频旋转的方向,支持左旋或者右旋90度
        :param target_viderbitrate: 转码后视频码率, 0使用原视频码率
        :param target_audiobitrate: 编码后音频的码率, 默认64
        :param v_frame: 转码后视频的帧率,默认24帧
        :param endcode_lib: h264编码使用的外部库
        :param preset_type: 编码速度参数
        :param crf_num: Constant Rate Factor 值
        :param profile_type: 编码配置文件
        :param level: 编码级别
    ### 视频hls切片
        FfmpegCmdModel.hls_video
        如果target_videobitrate超过原视频的bit_rate,将采用原视频的bit_rate
        如果target_height超过原片高度,将采用原片高度
        :param output_file: 视频输出目录,调用者要确保该目录存在且有写入权限
        ;param prefix: two-pass log 前缀
        :param encode_lib: h264编码使用的外部库
        :param target_height: 转码后视频高度,0使用原视频高度
        :param v_frame: 转码后视频的帧率,默认24帧
        :param preset_type: 编码速度参数
        :param crf_num: Constant Rate Factor 值
        :param profile_type: 编码配置文件
        :param level: 编码级别
        :param target_videobitrate: 转码后视频码率, 0使用原视频码率
        :param target_audiobitrate: 编码后音频的码率, 默认64
        :param ts_time: ts切片时间
        :param ts_prefix: ts切片文件前缀, 默认 ts
    ### 视频截图
        FfmpegCmdModel.snapshot_video
        :param output_file: 图片输出文件,调用者需要确认有可写入权限
        :param _: 占位符
        :param start_time: 截图开始时间 seconds 12.231
        :param target_height: 图片高度,0使用原视频高度,默认使用360高度
    ### 裁剪视频
        FfmpegCmdModel.cut_video
        如果target_videobitrate超过原视频的bit_rate,将采用原视频的bit_rate
        如果target_height超过原片高度,将采用原片高度
        :param output_file: 视频输出文件,调用者要确保该目录存在且有写入权限
        ;param prefix: two-pass log 前缀
        :param start_time: 视频截取开始时间 seconds 12.231
        :param last_time: 视频截取持续时间 seconds 12.231
        :param encode_lib: h264编码使用的外部库
        :param target_height: 转码后视频高度,0使用原视频高度
        :param v_frame: 转码后视频的帧率,默认24帧
        :param preset_type: 编码速度参数
        :param crf_num: Constant Rate Factor 值
        :param profile_type: 编码配置文件
        :param level: 编码级别
        :param target_videobitrate: 转码后视频码率, 0使用原视频码率
        :param target_audiobitrate: 编码后音频的码率, 默认64
    ### 视频拼接
        FfmpegCmdModel.concat_video
        :param output_file: 视频输出文件,调用者要确保该目录存在且有写入权限
        ;param prefix: two-pass log 前缀
        :param input_obj: 输入文件文件2, self.videofile_path + input_obj.videofile_path
        :param encode_lib: h264编码使用的外部库
        :param v_frame: 转码后视频的帧率,默认24帧
        :param preset_type: 编码速度参数
        :param crf_num: Constant Rate Factor 值
        :param profile_type: 编码配置文件
        :param level: 编码级别
        :param target_videobitrate: 转码后视频码率, 0使用原视频码率
    ### 视频水印
        FfmpegCmdModel.logo_video_fix FfmpegCmdModel.logo_video_move
        :param output_file: 视频输出文件,调用者要确保该目录存在且有写入权限
        :param prefix: two-pass log file prefix
        :param water_mark_type: 水印类型, 0:固定位置图片水印, 1:移动位置图片水印
        :param input_img: 输入水印图片
        :param ratio_img_height: 水印图片的高度和原始视频高度的比值, 必须小于1
        :param img_position_x: 水印位置 x
        :param img_position_y: 水印位置 y
        :param encode_lib: h264编码使用的外部库
        :param v_frame: 转码后视频的帧率,默认24帧
        :param preset_type: 编码速度参数
        :param crf_num: Constant Rate Factor 值
        :param profile_type: 编码配置文件
        :param level: 编码级别
        :param target_videobitrate: 转码后视频码率, 0使用原视频码率
        :param target_audiobitrate: 编码后音频的码率, 默认64
    ### 删除视频水印
        FfmpegCmdModel.del_log
        :param output_file: 视频输出文件,调用者要确保该目录存在且有写入权限
        :param prefix:  two-pass log file prefix
        :param delog_tuple: 元祖里面的元素都是 delog_args 类型的具名元祖
        :param encode_lib: h264编码使用的外部库
        :param v_frame: 转码后视频的帧率,默认24帧
        :param preset_type: 编码速度参数
        :param crf_num: Constant Rate Factor 值
        :param profile_type: 编码配置文件
        :param level: 编码级别
        :param target_videobitrate: 转码后视频码率, 0使用原视频码率
        :param target_audiobitrate: 编码后音频的码率, 默认64
    ### 视频转gif
        FfmpegCmdModel.create_gif
        :param output_file: gif输出文件,调用者要确保该目录存在且有写入权限
        ;param prefix: gif 调色板文件
        :param start_time: 视频截取开始时间 seconds 12.231
        :param last_time: 视频截取持续时间 seconds 12.231
        :param target_height: gif高度
        :param v_frame: gif帧率
    """
    @property
    def aio(self):
        return bool(self._aio) if hasattr(self, '_aio') else False

    @property
    def auto_clear(self):
        return bool(self._auto_clear) if hasattr(self, '_auto_clear') else False

    @property
    def libx264(self):
        return self._libx264 if hasattr(self, '_libx264') else False

    @property
    def h264_nvenc(self):
        return self._h264_nvenc if hasattr(self, '_h264_nvenc') else False
    
    @property
    def prefix_2pass(self):
        return self._prefix_2pass if hasattr(self, '_prefix_2pass') else ('/tmp/dummy.' + str(time.time()))

    @property
    def output_dir(self):
        return self._output_dir

    @property
    def video_codecname(self):
        return self._video_codecname

    @property
    def video_profile(self):
        return self._video_profile

    @property
    def video_width(self):
        return self._video_width

    @property
    def video_height(self):
        return self._video_height

    @property
    def rotate(self):
        return self._rotate

    @property
    def video_pixfmt(self):
        return self._video_pixfmt

    @property
    def video_avgframerate(self):
        return self._video_avgframerate

    @property
    def video_bitrate(self):
        return self._video_bitrate

    @property
    def audio_codecname(self):
        return self._audio_codecname

    @property
    def audio_profile(self):
        return self._audio_profile

    @property
    def audio_samplefmt(self):
        return self._audio_samplefmt

    @property
    def audio_samplerate(self):
        return self._audio_samplerate

    @property
    def audio_channels(self):
        return self._audio_channels

    @property
    def audio_bitrate(self):
        return self._audio_bitrate

    @property
    def videofile_path(self):
        return self._video_file if hasattr(self, '_video_file') else '/tmp/None'

    @property
    def videofile_duration(self):
        return self._videofile_duration

    @property
    def videofile_size(self):
        return self._videofile_size

    @property
    def videofile_formatname(self):
        return self._videofile_formatname

    @staticmethod
    def create_delog_args(pos_x: int, pos_y: int, width: int,
                          height: int, begin_time: int, end_time: int) -> 'namedtuple':
        """
        构建去除水印选项的具名元祖
        :param pos_x: 水印位置的X坐标
        :param pos_y: 水印位置的y坐标
        :param width: 水印宽度
        :param height: 水印高度
        :param begin_time: 去除水印的开始时间
        :param end_time: 去除水印的结束时间
        :return: 返回构建去除水印选项的具名元祖
        """
        delog_args_str = 'pos_x pos_y width height begin_time end_time'
        delog_args = namedtuple('delog_args', delog_args_str)
        args = delog_args(pos_x,pos_y,width,height,begin_time,end_time)
        return args
    
    @staticmethod
    def download_m3u8(ffmpeg_bin: str, m3u8_url: str, output_file: str, *,
                      encode_lib: 'H264EncoderArgs' = H264EncoderArgs.codec_v_libx264, 
                      preset_type: 'H264EncoderArgs' = H264EncoderArgs.preset_veryslow,
                      crf_num: 'H264EncoderArgs' = H264EncoderArgs.crf_28,
                      profile_type: 'H264EncoderArgs' = H264EncoderArgs.profile_high,
                      level: 'H264EncoderArgs' = H264EncoderArgs.level_4_2) -> tuple:
        """
        将m3u8文件转化为mp4
        :param ffmpeg_bin: ffmpeg 二进制文件路径
        :param m3u8_url: m3u8文件路径
        :param output_file: 视频输出文件
        :param encode_lib: h264编码使用的外部库
        :param preset_type: 编码速度参数
        :param crf_num: Constant Rate Factor 值
        :param profile_type: 编码配置文件
        :param level: 编码级别
        return 成功返回(True, ''),失败返回(False, stderr)
        """
        cmd = FfmpegCmdModel.download_m3u8.format(
                ffmpeg_bin=ffmpeg_bin, m3u8_url=m3u8_url, encode_lib=encode_lib,
                preset_type=preset_type, crf_num=crf_num, profile_type=profile_type,
                level=level, output_file=output_file)
        status, _, stderr = simple_run_cmd(cmd)
        if status != 0:
            return False, stderr
        return True, ''

    @staticmethod
    async def download_m3u8_aio(ffmpeg_bin: str, m3u8_url: str, output_file: str, *,
                                encode_lib: 'H264EncoderArgs' = H264EncoderArgs.codec_v_libx264, 
                                preset_type: 'H264EncoderArgs' = H264EncoderArgs.preset_veryslow,
                                crf_num: 'H264EncoderArgs' = H264EncoderArgs.crf_28,
                                profile_type: 'H264EncoderArgs' = H264EncoderArgs.profile_high,
                                level: 'H264EncoderArgs' = H264EncoderArgs.level_4_2) -> tuple:
        """
        将m3u8文件转化为mp4
        :param ffmpeg_bin: ffmpeg 二进制文件路径
        :param m3u8_url: m3u8文件路径
        :param output_file: 视频输出文件
        :param encode_lib: h264编码使用的外部库
        :param preset_type: 编码速度参数
        :param crf_num: Constant Rate Factor 值
        :param profile_type: 编码配置文件
        :param level: 编码级别
        return 成功返回(True, ''),失败返回(False, stderr)
        """
        cmd = FfmpegCmdModel.download_m3u8.format(
                ffmpeg_bin=ffmpeg_bin, m3u8_url=m3u8_url, encode_lib=encode_lib,
                preset_type=preset_type, crf_num=crf_num, profile_type=profile_type,
                level=level, output_file=output_file)
        status, _, stderr = await run_cmd(cmd)
        if status != 0:
            return False, stderr 
        return True, ''

    def __init__(self, video_file: str, output_dir: str = '/tmp',
                 ffmpeg_bin: str = '/opt/ffmpeg/bin/ffmpeg',
                 ffprobe_bin: str = "/opt/ffmpeg/bin/ffprobe", aio=True, auto_clear=False):
        """
        初始化ffmpeg类,初始化的时候会判断各个文件是否存在,并且会获取视频文件的属性
        :param video_file: 视频文件
        :param output_dir: 默认输出文件.调用这需确保权限正确
        :param ffmpeg_bin: ffmpeg 可执行文件
        :param ffprobe_bin: ffprobe 可执行文件
        :param aio: 是否异步
        :param auto_clear: 是否自动清理源文件
        注意,本类仅支持linux
        """
        # 获取各个文件的绝对路径
        video_file = os.path.abspath(video_file)
        ffmpeg_bin = os.path.abspath(ffmpeg_bin)
        ffprobe_bin = os.path.abspath(ffprobe_bin)
        output_dir = os.path.abspath(output_dir)
        # 判断各个文件是否存在
        if not all([os.path.isfile(f) for f in (video_file, ffmpeg_bin, ffprobe_bin)]):
            raise FileNotFoundError(f'{video_file:s} {ffmpeg_bin:s} {ffprobe_bin:s} maybe not exists')
        if not os.path.isdir(output_dir):
            raise FileNotFoundError(f'{output_dir:s} is not exists')
        # 初始化 ffmpeg 和 ffprobe 二进制文件
        self._ffmpeg = ffmpeg_bin
        self._ffprobe = ffprobe_bin
        self._video_file = video_file
        self._output_dir = output_dir
        self._aio = aio
        self._auto_clear = auto_clear
        # 接下来判断ffmpeg二进制文件是否有 libx264 和 h264_nvenc 外部编码库的支持
        _command = FfmpegCmdModel.check_h264.format(ffmpeg_bin=self._ffmpeg)
        status, stdout, stderr = simple_run_cmd(_command)
        # debug
        # print(status, stdout, stderr)
        # end debug
        if status != 0:
            raise ChildProcessError(stderr)
        # 检查ffmpeg二进制文件h264外部编码库
        if 'libx264' in stdout:
            self._libx264 = True
        if 'h264_nvenc' in stdout:
            self._h264_nvenc = True
        if not any([self.libx264, self.h264_nvenc]):
            raise EnvironmentError(f'{self._ffmpeg:s} do not have extend encode lib: libx264 or h264_nvenc')
        # 准备获取视频文件的属性
        _command = FfmpegCmdModel.get_video_probe.format(
            ffprobe_bin=self._ffprobe,
            input_file=self._video_file
        )
        status, stdout, stderr = simple_run_cmd(_command)
        if status != 0:
            raise ChildProcessError(stderr)
        # debug
        # print(stdout)
        # end debug
        videofile_probe = json.loads(stdout)
        # 接下来判断视频是否有视频和音频,不是同时具备音频和视频,就直接报格式错误,并将视频属性保存
        # debug
        # print(videofile_probe)
        # end debug
        try:
            # 判断视频流和音频流都存在
            assert videofile_probe['streams'][0]['codec_type'] == 'video'
            assert videofile_probe['streams'][1]['codec_type'] == 'audio'
            # 视频流属性
            self._video_codecname = videofile_probe['streams'][0]['codec_name']
            self._video_profile = videofile_probe['streams'][0]['profile']
            self._video_width = int(float(videofile_probe['streams'][0]['width']))
            self._video_height = int(float(videofile_probe['streams'][0]['height']))
            # 视频旋转属性
            try:
                self._rotate = videofile_probe['streams'][0]['tags']['rotate']
            except (KeyError,IndexError):
                self._rotate = 0
            self._video_pixfmt = videofile_probe['streams'][0]['pix_fmt']
            self._video_avgframerate = int(float(videofile_probe['streams'][0]['avg_frame_rate'].split('/')[0])/
                                           float(videofile_probe['streams'][0]['avg_frame_rate'].split('/')[1]))
            try:
                self._video_bitrate = int(float(videofile_probe['streams'][0]['bit_rate']))
            except KeyError:
                self._video_bitrate = int(float(videofile_probe['format']['bit_rate']))
            # 音频流属性
            self._audio_codecname = videofile_probe['streams'][1]['codec_name']
            try:
                self._audio_profile = videofile_probe['streams'][1]['profile']
            except KeyError:
                self._audio_profile = 'unknown'
            self._audio_samplefmt = videofile_probe['streams'][1]['sample_fmt']
            self._audio_samplerate = int(float(videofile_probe['streams'][1]['sample_rate']))
            self._audio_channels = int(float(videofile_probe['streams'][1]['channels']))
            self._audio_bitrate = int(float(videofile_probe['streams'][1]['bit_rate']))
            # 视频文件属性
            self._videofile_duration = float(videofile_probe['format']['duration'])
            self._videofile_size = float(videofile_probe['format']['size'])
            self._videofile_formatname = videofile_probe['format']['format_name']
            assert float(self.videofile_duration) > 0
        except (AssertionError, IndexError, KeyError, TypeError):
            # raise
            raise TypeError(f'{self._video_file:s} format error, json -> \n {stdout:s}')
        self._prefix_2pass = '/tmp/ffmpeg2pass.' + str(time.time()) + str(random.random())
        # 各种视频处理函数,通过命令模版去对视频进行不同的处理
        if self.aio:
            self.cmd_do_aio = _ffmpeg_do_cmd(self, is_aio=True)(_create_command_aio)
        # 无论如何都会生成菲aio版本的命令
        self.cmd_do = _ffmpeg_do_cmd(self, is_aio=False)(_create_command)
        # 改变工作目录到 output_dir
        # os.chdir(output_dir)

    def __len__(self) -> int:
        return int(self.videofile_duration)

    def __add__(self, other: 'H264Video object') -> 'H264Video object':
        """
        两个ffmpeg对象相加, 即拼接视频
        输出视频的 宽度 高度 由被加数觉决定, 码率由用户设置和两个视频的原本码率决定,取最小值
        :param other: 另外一个H264Video对象
        :return: 一个新的H264Video
        """
        cls = type(self)
        assert isinstance(other, cls)
        encode_lib = H264EncoderArgs.codec_v_h264_nvenc if self.h264_nvenc else H264EncoderArgs.codec_v_libx264
        output, _ = self.cmd_do(None, 'mp4', FfmpegCmdModel.concat_video, input_obj=other, encode_lib=encode_lib)
        # 有的时候会找不到 codec_v_h264_nvenc 设备
        if output is None and encode_lib == H264EncoderArgs.codec_v_h264_nvenc:
            encode_lib = H264EncoderArgs.codec_v_libx264
            output, _ = self.cmd_do(None, 'mp4', FfmpegCmdModel.concat_video, input_obj=other, encode_lib=encode_lib)
        return output

    def __getitem__(self, item):
        """
        支持分片操作,如果step是负数,则为截图操作,如 step = -7 则截7张图,返回一个[imgpath1,imgpath2,...]
        图片默认保存在/tmp目录下
        如果step是正数,则原视频剪辑成step个1s长度的视频 [ffmpeg_obj1,ffmpeg_obj2,...]
        :param item: 可以是slice或者index
        :return:list() or str or ffmpeg_obj
        """
        cls = type(self)
        if isinstance(item, slice):
            start = 0 if item.start is None else item.start
            start, stop, step = slice(start, item.stop, item.step).indices(len(self))
            stop = stop if stop >= 0 else len(self)-1
            # debug
            # print(start, stop, step)
            # end debug
            # 如果step是负数,则是截图任务
            if step < 0:
                pic_count = abs(step)
                # 截图任务是在 start 和 stop 之间均匀截图
                delta_time = (stop+1 - start) / pic_count
                startime = start
                result = [self.cmd_do(None, 'jpg', FfmpegCmdModel.snapshot_video,
                                      start_time=startime + delta_time * count, target_height=240)
                          for count in range(pic_count)]
                return [pic_path[0] for pic_path in result if pic_path[0] is not None]
            else:
                # step > 0, 是要剪辑视频, 将视频剪辑成1s片段,step为片段个数
                delta_time = (stop + 1 - start) / step
                startime = start
                result = [self.cmd_do(None, 'mp4', FfmpegCmdModel.cut_video, start_time=startime + delta_time * count,
                                      encode_lib=H264EncoderArgs.codec_v_libx264)
                          for count in range(step)]
                return [ffmpeg_obj[0] for ffmpeg_obj in result if ffmpeg_obj[0] is not None]
        elif isinstance(item, numbers.Integral):
            # 以item为开始时间,截取时长为一秒的视频
            result, _ = self.cmd_do(None, 'mp4', FfmpegCmdModel.cut_video, start_time=item,
                                    encode_lib=H264EncoderArgs.codec_v_libx264)
            return result
        else:
            msg = '{cls.__name__} indices must be integral'
            raise TypeError(msg.format(cls=cls))

    def __repr__(self):
        return f'<{self.videofile_path:s}, libx264:{self.libx264!r}, h264_nvenc:{self.h264_nvenc!r}>'

    def __del__(self):
        """
        改函数不会删除 self.videofile_path
        所以调用者要管理好 videofile 原文件
        本类提供save_video的方法,将原视频保存到目标目录
        :return:
        """
        # 删除原始视频,如果需要的话
        if self.auto_clear:
            _commad = f"rm -rf '{self.videofile_path:s}'"
            simple_run_cmd(_commad)
        _command = f"rm -rf '{self.prefix_2pass:s}'*"
        # debug
        # print(_command)
        # end debug
        simple_run_cmd(_command)
