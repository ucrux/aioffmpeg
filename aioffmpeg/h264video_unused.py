from aioffmpeg_h264_encoder_args import *
from aioffmpeg_tools_func import *
from _aioffmpeg_tools_func import *

import os
import asyncio
import json
import time
import subprocess
from functools import wraps
import datetime
import numbers
import random
import aiofiles
from collections import namedtuple

class H264Video():
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
    """
    def _ffmpeg_opt(is_aio: bool = True):
        """
        ffmpeg命令行操作装饰器
        此装饰器返回一个异步函数
        使用此装饰器会为函数产生2个新的参数output_dir,file_extensions
        被装饰的函数实际上只是产生一个shell命令
        :return: 以 obj 开头的函数,返回一个新的ffmpeg实例,使用缩放填充后的视频做初始化,和标准错误
                如果出错则返回 None, 和错误信息 'ffmpeg_object, stderr'
                以 str 开头的函数, 返回一个字符串和标准错误
        """
        def decorate(fn):
            if is_aio:
                @wraps(fn)
                async def wrapper(self, output_dir, file_extensions, *args, **kwargs):
                    # 如果传入的 output_dir 为 None 或者为 空字符串, 则使用初始化类时使用的 output_dir
                    if not output_dir:
                        output_dir = self._output_dir
                    output_dir = os.path.abspath(output_dir)
                    if not os.path.isdir(output_dir):
                        return None, f'{output_dir:s} not exists'
                    # 目标文件路径
                    ori_file_name = '.'.join(os.path.split(self._video_file)[1].split('.')[:-1])
                    output_file = output_dir + '/' + ori_file_name + str(time.time()) + '.' + file_extensions
                    # 2步编码的日志文件前缀
                    prefix = 'ffmpeg2pass.' + str(time.time())
                    _command = fn(self, output_file, prefix, *args, **kwargs)
                    if _command is None:
                        return None, 'command create error'
                    status, stdout, stderr = await self._run_cmd(_command)
                    # 删除2步编码的日志文件
                    _, _, _ = await self._run_cmd(f'rm -rf {prefix:s}*')
                    # debug
                    # print(status)
                    # end debug
                    if status != 0:
                        return None, stderr
                    if fn.__name__.startswith('obj_'):
                        return self.__class__(output_file, self.output_dir, self._ffmpeg, self._ffprobe), ''
                    elif fn.__name__.startswith('str_'):
                        return output_file, ''
            else:
                @wraps(fn)
                def wrapper(self, output_dir, file_extensions, *args, **kwargs):
                    # 如果传入的 output_dir 为 None 或者为 空字符串, 则使用初始化类时使用的 output_dir
                    if not output_dir:
                        output_dir = self._output_dir
                    output_dir = os.path.abspath(output_dir)
                    if not os.path.isdir(output_dir):
                        return None, f'{output_dir:s} not exists'
                    # 目标文件路径
                    ori_file_name = '.'.join(os.path.split(self._video_file)[1].split('.')[:-1])
                    output_file = output_dir + '/' + ori_file_name + str(time.time()) + '.' + file_extensions
                    # 2步编码的日志文件前缀
                    prefix = 'ffmpeg2pass.' + str(time.time())
                    _command = fn(self, output_file, prefix, *args, **kwargs)
                    if _command is None:
                        return None, 'command create error'
                    status, stdout, stderr = self._simple_run_cmd(_command)
                    # 删除2步编码的日志文件
                    _, _, _ = self._simple_run_cmd(f'rm -rf {prefix:s}*')
                    # debug
                    # print(status)
                    # end debug
                    if status != 0:
                        return None, stderr
                    if fn.__name__.startswith('obj_'):
                        return self.__class__(output_file, self.output_dir, self._ffmpeg, self._ffprobe), ''
                    elif fn.__name__.startswith('str_'):
                        return output_file, ''
            return wrapper
        return decorate

    @property
    def libx264(self):
        return self._libx264 if hasattr(self, '_libx264') else False

    @property
    def h264_nvenc(self):
        return self._h264_nvenc if hasattr(self, '_h264_nvenc') else False

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
    def _simple_run_cmd(cmd, timeout: int = 7200) -> 'status,stdout,stderr':
        """
        普通的执行shell命令
        :param cmd:
        :param timeout:
        :return:
        """
        # debug
        # print(cmd)
        # end debug
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            stdout, stderr = proc.communicate(timeout=timeout)
            stdout = stdout.decode('utf8')
            stderr = stderr.decode('utf8')
        except TimeoutError:
            proc.terminate()
            status = -1
            stderr = f'execute {cmd:s} timeout'
        else:
            status = proc.returncode
            if status != 0:
                stderr = f'execute {cmd:s} return {proc.returncode:d} and stderr -> {stderr:s}'
        return status, stdout, stderr

    @staticmethod
    async def _run_cmd(cmd: str) -> 'status,stdout,stderr':
        """
        执行shell命令
        :param cmd: 需要执行的shell命令
        :return: status,stdout,stderr
        """
        # debug
        # print(cmd)
        # end debug
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)
        # 不知道这里需不需要使用 try: pass; except: pass; 在官方文档上没有找到关于这个的 exception
        stdout, stderr = await proc.communicate()
        stdout = stdout.decode('utf8')
        stderr = stderr.decode('utf8')
        if proc.returncode != 0:
            stderr = f'execute {cmd:s} return {proc.returncode:d} and stderr -> {stderr:s}'
        return proc.returncode, stdout, stderr

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

    def __init__(self, video_file:str, output_dir:str = '/tmp',
                 ffmpeg_bin:str = '/opt/ffmpeg/bin/ffmpeg',
                 ffprobe_bin:str = "/opt/ffmpeg/bin/ffprobe"):
        """
        初始化ffmpeg类,初始化的时候会判断各个文件是否存在,并且会获取视频文件的属性
        :param video_file: 视频文件
        :param ffmpeg_bin: ffmpeg 可执行文件
        :param ffprobe_bin: ffprobe 可执行文件
        注意,本类仅支持linux
        """
        # 获取各个文件的绝对路径
        video_file = os.path.abspath(video_file)
        ffmpeg_bin = os.path.abspath(ffmpeg_bin)
        ffprobe_bin = os.path.abspath(ffprobe_bin)
        # 判断各个文件是否存在
        if not all([os.path.isfile(f) for f in (video_file, ffmpeg_bin, ffprobe_bin)]):
            raise FileExistsError(f'{video_file:s} {ffmpeg_bin:s} {ffprobe_bin:s} maybe not exists')
        # 初始化 ffmpeg 和 ffprobe 二进制文件
        self._ffmpeg = ffmpeg_bin
        self._ffprobe = ffprobe_bin
        self._video_file = video_file
        self._output_dir = output_dir
        # 接下来判断ffmpeg二进制文件是否有 libx264 和 h264_nvenc 外部编码库的支持
        _command = aioffmpeg_cmd.CMD_CHECK_H264.format(ffmpeg_bin=self._ffmpeg)
        status, stdout, stderr = self._simple_run_cmd(_command)
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
        _command = aioffmpeg_cmd.CMD_GET_VIDEO_PROBE.format(
            ffprobe_bin=self._ffprobe,
            input_file=self._video_file
        )
        status, stdout, stderr = self._simple_run_cmd(_command)
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
        # 改变工作目录到 /tmp
        os.chdir('/tmp')

    def _dealwith_delog(self, delog_args: 'namedtuple') -> str:
        """
        处理去除水印参数,如果参数有明显越界,返回''空字符串
        :param delog_args: 去除水印参数的具名元祖,由create_delog_args产生
        :return: 返回去除水印选项的字符串
        """
        if delog_args.pos_x > self.video_width or delog_args.pos_y > self.video_height or \
            delog_args.width + delog_args.pos_x > self.video_width or \
            delog_args.height + delog_args.pos_y > self.video_height or \
            delog_args.end_time < delog_args.begin_time:
            return None
        opts = aioffmpeg_cmd.OPTS_DEL_LOGO.format(
            X = delog_args.pos_x,
            Y = delog_args.pos_y,
            width = delog_args.width,
            height = delog_args.height,
            begin_time = delog_args.begin_time,
            end_time = delog_args.end_time
        )
        return opts

    @_ffmpeg_opt()
    def obj_video_scale(self, output_file: str,
                        prefix: str,
                        target_width: int = 0,
                        target_height: int = 0,
                        target_videobitrate: int = 0,
                        target_audiobitrate: int = H264EncoderArgs.audio_rate_64,
                        v_frame: int = H264EncoderArgs.v_frame_24,
                        encode_lib = H264EncoderArgs.codec_v_h264_nvenc,
                        preset_type = H264EncoderArgs.preset_veryslow,
                        crf_num = H264EncoderArgs.crf_23,
                        profile_type = H264EncoderArgs.profile_high,
                        level = H264EncoderArgs.level_4_2) -> str:
        """
        产生ffmpeg编码命令
        将视频做h264编码,并按要求缩放填充,且保持原视频比例
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
        :return: 返回一个新的ffmpeg实例,使用缩放填充后的视频做初始化.和标准错误
        """
        target_width = self.video_width if not target_width else target_width
        target_height = self.video_height if not target_height else target_height
        target_width = int(int(target_width / 2) * 2)
        target_height = int(int(target_height / 2) * 2)
        v_frame = v_frame if v_frame < self.video_avgframerate else self.video_avgframerate
        target_videobitrate = int(self.video_bitrate / 1000) if not target_videobitrate \
            else (target_videobitrate if target_videobitrate < (self.video_bitrate / 1000)
                  else int(self.video_bitrate / 1000) )
        assert all([i > 0 for i in (target_width, target_height, v_frame, target_videobitrate, target_audiobitrate)])
        # 判断视频的宽高比
        # 计算目标视频宽高比,保留3位小数
        target_whratio = round(float(target_width)/float(target_height), 4)
        # 计算原视频宽高比,保留3位小数
        origin_whratio = round(float(self.video_width)/float(self.video_height), 4)
        # 根据宽高比生成不同的命令
        if target_whratio == origin_whratio:
            # 缩放长宽比相同
            pad_options = ''
        elif target_whratio > origin_whratio:
            # 缩放后视频的宽度比原视频宽,需要在缩放后的视频两边填充黑边
            pad_options = aioffmpeg_cmd.OPTS_PAD_LR.format(
                target_width=target_width,
                target_height=target_height,
            )
            target_width = int(round(target_height * origin_whratio, 0))
            target_width = int(int(target_width / 2) * 2)
        else:
            # 缩放后视频的高度比原视频高,需要在缩放后的视频上下填充黑边
            pad_options = aioffmpeg_cmd.OPTS_PAD_UD.format(
                target_width=target_width,
                target_height=target_height,
            )
            target_height = int(round(target_width / origin_whratio, 0))
            target_height = int(int(target_height / 2) * 2)
        _command = aioffmpeg_cmd.CMD_SCALE_VIDEO_CODECS.format(
            ffmpeg_bin=self._ffmpeg,
            input_file=self._video_file,
            encode_lib=encode_lib,
            prefix=prefix,
            target_width=target_width,
            target_height=target_height,
            pad_options=pad_options,
            frame=v_frame,
            preset_type=preset_type,
            crf_num=crf_num,
            profile_type=profile_type,
            level=level,
            video_rate=target_videobitrate,
            audio_rate = target_audiobitrate,
            output_file=output_file
        )
        return _command

    @_ffmpeg_opt()
    def obj_video_rotate(self, output_file: str,
                         prefix: str,
                         rotate_direct: int = H264EncoderArgs.v_left_rotate,
                         target_videobitrate: int = 0,
                         target_audiobitrate: int = H264EncoderArgs.audio_rate_64,
                         v_frame: int = H264EncoderArgs.v_frame_24,
                         encode_lib = H264EncoderArgs.codec_v_h264_nvenc,
                         preset_type = H264EncoderArgs.preset_veryslow,
                         crf_num = H264EncoderArgs.crf_23,
                         profile_type = H264EncoderArgs.profile_high,
                         level = H264EncoderArgs.level_4_2) -> str:
        """
        对视频进行坐旋转或者右旋转,默认左旋转
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
        :return: 返回视频旋转命令
        """
        v_frame = v_frame if v_frame < self.video_avgframerate else self.video_avgframerate
        target_videobitrate = int(self.video_bitrate / 1000) if not target_videobitrate \
            else (target_videobitrate if target_videobitrate < (self.video_bitrate / 1000)
                  else int(self.video_bitrate / 1000))
        assert all([i > 0 for i in (v_frame, target_videobitrate, target_audiobitrate)])
        _command = aioffmpeg_cmd.CMD_ROTATE_VIDEO.format(
            ffmpeg_bin=self._ffmpeg,
            input_file=self._video_file,
            encode_lib=encode_lib,
            prefix=prefix,
            rotate_direct=rotate_direct,
            frame=v_frame,
            preset_type=preset_type,
            crf_num=crf_num,
            profile_type=profile_type,
            level=level,
            video_rate=target_videobitrate,
            audio_rate=target_audiobitrate,
            output_file=output_file
        )
        return _command

    @_ffmpeg_opt()
    def str_video_hls(self, output_file: str,
                      prefix: str,
                      encode_lib = H264EncoderArgs.codec_v_h264_nvenc,
                      target_height: int = 0,
                      v_frame: int = H264EncoderArgs.v_frame_24,
                      preset_type=H264EncoderArgs.preset_veryslow,
                      crf_num=H264EncoderArgs.crf_23,
                      profile_type=H264EncoderArgs.profile_high,
                      level=H264EncoderArgs.level_4_2,
                      target_videobitrate: int = 0,
                      target_audiobitrate: int = H264EncoderArgs.audio_rate_64,
                      ts_time: int = 10,
                      fix_ts_time = H264EncoderArgs.no_fix_ts_time,
                      ts_prefix: str = 'ts') -> str:
        """
        产生切片命令
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
        :return: 返回影片切片命令
        """
        target_height = self.video_height if not target_height else (
            target_height if target_height < self.video_height else self.video_height)
        v_frame = v_frame if v_frame < self.video_avgframerate else self.video_avgframerate
        target_videobitrate = int(self.video_bitrate / 1000) if not target_videobitrate \
            else (target_videobitrate if target_videobitrate < (self.video_bitrate / 1000)
                  else int(self.video_bitrate / 1000))
        assert all([i > 0 for i in (target_height, v_frame, target_videobitrate, ts_time, target_audiobitrate)])
        output_dir = os.path.split(output_file)[0]
        # _command = f"mkdir -p '{output_dir}/m3u8-dir'"
        # status, _, _ = self._simple_run_cmd(_command)
        # assert status == 0
        _command = aioffmpeg_cmd.CMD_HLS_VIDEO.format(
            ffmpeg_bin=self._ffmpeg,
            input_file=self._video_file,
            encode_lib=encode_lib,
            prefix=prefix,
            target_height=target_height,
            frame=v_frame,
            preset_type=preset_type,
            crf_num=crf_num,
            profile_type=profile_type,
            level=level,
            video_rate=target_videobitrate,
            audio_rate=target_audiobitrate,
            ts_time=ts_time,
            fix_ts_time=fix_ts_time,
            ts_prefix=ts_prefix,
            output_dir=output_dir,
            output_file=output_file
        )
        return _command

    @_ffmpeg_opt()
    def str_video_snapshot(self, output_file: str,
                           _: str,
                           start_time: float = 0,
                           target_height: int = 240) -> str:
        """
        生成视频截图命令
        :param output_file: 图片输出文件,调用者需要确认有可写入权限
        :param _: 占位符
        :param start_time: 截图开始时间 seconds 12.231
        :param target_height: 图片高度,0使用原视频高度,默认使用360高度
        :return: 视频截图命令
        """
        target_height = self.video_height if not target_height else (
            target_height if target_height < self.video_height else self.video_height)
        assert target_height > 0
        assert start_time >= 0
        start_time = (start_time % 86400) % self.videofile_duration
        str_start_time = '0' + str(datetime.timedelta(seconds=start_time)) if start_time < 36000 \
            else str(datetime.timedelta(seconds=start_time))
        _commad = aioffmpeg_cmd.CMD_SNAPSHOT.format(
            ffmpeg_bin=self._ffmpeg,
            start_time=str_start_time,
            input_file=self._video_file,
            target_height=target_height,
            output_file=output_file,
        )
        return _commad

    @_ffmpeg_opt()
    def obj_video_cut(self, output_file: str,
                      prefix: str,
                      start_time: float = 0,
                      last_time: float = 1,
                      encode_lib=H264EncoderArgs.codec_v_h264_nvenc,
                      target_height: int = 0,
                      v_frame: int = H264EncoderArgs.v_frame_24,
                      preset_type=H264EncoderArgs.preset_veryslow,
                      crf_num=H264EncoderArgs.crf_23,
                      profile_type=H264EncoderArgs.profile_high,
                      level=H264EncoderArgs.level_4_2,
                      target_videobitrate: int = 0,
                      target_audiobitrate: int = H264EncoderArgs.audio_rate_64,
                      ):
        """
        产生裁剪视频的命令
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
        :return: 返回视频截取命令
        """
        target_height = self.video_height if not target_height else (
            target_height if target_height < self.video_height else self.video_height)
        target_videobitrate = int(self.video_bitrate / 1000) if not target_videobitrate \
            else (target_videobitrate if target_videobitrate < (self.video_bitrate / 1000)
                  else int(self.video_bitrate / 1000))
        v_frame = v_frame if v_frame < self.video_avgframerate else self.video_avgframerate
        assert  all([i > 0 for i in (target_height, target_videobitrate, last_time, v_frame, target_audiobitrate)])
        assert start_time >= 0
        # 时间大于1天的都安一天以内执行
        start_time = (start_time % 86400) % self.videofile_duration
        last_time = (last_time % 86400)
        last_time = last_time if start_time + last_time <= self.videofile_duration \
            else self.videofile_duration - start_time - 1
        str_start_time = '0' + str(datetime.timedelta(seconds=start_time)) if start_time < 36000 \
            else str(datetime.timedelta(seconds=start_time))
        str_last_time = '0' + str(datetime.timedelta(seconds=last_time)) if last_time < 36000 \
            else str(datetime.timedelta(seconds=last_time))
        # debug
        # print(start_time, last_time, self.videofile_duration)
        # end debug
        # debug
        # print(output_file)
        # end debug
        _command = aioffmpeg_cmd.CMD_CUT_VIDEO.format(
            ffmpeg_bin=self._ffmpeg,
            start_time=str_start_time,
            last_time=str_last_time,
            input_file=self._video_file,
            encode_lib=encode_lib,
            prefix=prefix,
            target_height=target_height,
            frame=v_frame,
            preset_type=preset_type,
            crf_num=crf_num,
            profile_type=profile_type,
            level=level,
            video_rate=target_videobitrate,
            audio_rate=target_audiobitrate,
            output_file=output_file
        )
        return _command

    async def obj_video_concat(self, output_dir: str, file_extensions: str,
                               input_obj: 'H264Video obj',
                               encode_lib=H264EncoderArgs.codec_v_h264_nvenc,
                               v_frame: int = H264EncoderArgs.v_frame_24,
                               preset_type=H264EncoderArgs.preset_veryslow,
                               crf_num=H264EncoderArgs.crf_23,
                               profile_type=H264EncoderArgs.profile_high,
                               level=H264EncoderArgs.level_4_2,
                               target_videobitrate: int = 0,
                               target_audiobitrate: int = H264EncoderArgs.audio_rate_64,
                               ) -> 'H264Video obj':
        """
        执行视频拼接任务
        :param output_dir: 输出文件的位置,调用者要确保该目录存在且有写入权限
        :param input_obj: 输入文件文件2, self.videofile_path + input_obj.videofile_path
        :param encode_lib: h264编码使用的外部库
        :param v_frame: 转码后视频的帧率,默认24帧
        :param preset_type: 编码速度参数
        :param crf_num: Constant Rate Factor 值
        :param profile_type: 编码配置文件
        :param level: 编码级别
        :param target_videobitrate: 转码后视频码率, 0使用原视频码率
        :return: 返回一个新的 ffpmeg 对象
        """
        cls = type(self)
        if not isinstance(input_obj, cls):
            return None, f'{input_obj!r} is not a object of H264Video'
        if not output_dir:
            output_dir = self._output_dir
        output_dir = os.path.abspath(output_dir)
        if not os.path.isdir(output_dir):
            return None, f'{output_dir:s} not exists'
        # 目标文件路径
        ori_file_name = '.'.join(os.path.split(self._video_file)[1].split('.')[:-1])
        output_file = output_dir + '/' + ori_file_name + str(time.time()) + '.' + file_extensions
        target_videobitrate = int(self.video_bitrate / 1000) if not target_videobitrate \
            else (target_videobitrate if target_videobitrate < (self.video_bitrate / 1000)
                  else int(self.video_bitrate / 1000))
        target_videobitrate = min(target_videobitrate, int(input_obj.video_bitrate / 1000))
        v_frame = v_frame if v_frame < self.video_avgframerate else self.video_avgframerate
        v_frame = min(v_frame, int(input_obj.video_avgframerate))
        assert target_videobitrate > 0 and v_frame > 0 and target_audiobitrate > 0
        # 将视频格式统一
        input_obj1, stderr = await self.obj_video_scale(None, 'mp4', encode_lib=encode_lib,
                                                target_videobitrate=target_videobitrate,
                                                        v_frame=v_frame)
        input_obj2, stderr = await input_obj.obj_video_scale(None, 'mp4', target_width=self.video_width,
                                                     target_height=self.video_height,
                                                     target_videobitrate=target_videobitrate,
                                                     encode_lib=encode_lib,
                                                             v_frame=v_frame)
        if not all([input_obj1, input_obj2]):
            return None, f'scale {input_obj1.videofile_path:s} or {input_obj2.videofile_path:s} failed'
        # 如果支持GPU转码且指明使用GPU转码
        if self.h264_nvenc and encode_lib == H264EncoderArgs.codec_v_h264_nvenc:
            # tow-pass log prefix
            prefix = 'ffmpeg2pass.' + str(time.time())
            _command = aioffmpeg_cmd.CMD_CONCAT_VIDEO.format(
                ffmpeg_bin=self._ffmpeg,
                input_file1=input_obj1.videofile_path,
                input_file2=input_obj2.videofile_path,
                encode_lib=encode_lib,
                prefix=prefix,
                frame=v_frame,
                preset_type=preset_type,
                crf_num=crf_num,
                profile_type=profile_type,
                level=level,
                video_rate=target_videobitrate,
                audio_rate=target_audiobitrate,
                output_file=output_file
            )
            status, stdout, stderr = await self._run_cmd(_command)
            # delete two-pass log
            _, _, _ = await self._run_cmd(f'rm -rf {prefix:s}*')
            # debug
            # print(status)
            # end debug
            if status == 0:
                return cls(output_file, self.output_dir, self._ffmpeg, self._ffprobe), ''
        # GPU转码失败,或者不使用GPU转码
        tmp_concat_file = '/tmp/' + str(time.time()) + str(random.random()) + '.txt'
        concat_str = f"file '{input_obj1.videofile_path:s}'\nfile '{input_obj2.videofile_path:s}'\n"
        try:
            async with aiofiles.open(tmp_concat_file, mode='w') as f:
                await f.write(concat_str)
        except (PermissionError,IOError):
            return None, f'create concat tmp file {tmp_concat_file:s} failed'
        _command = aioffmpeg_cmd.CMD_CONCAT_VIDEO_SAFE.format(
            ffmpeg_bin=self._ffmpeg,
            concat_file=tmp_concat_file,
            output_file=output_file
        )
        status, stdout, stderr = await self._run_cmd(_command)
        # debug
        # print(status)
        # end debug
        # 清理临时文件
        _, _, _ = await self._run_cmd(f"rm -rf '{tmp_concat_file:s}'")
        if status != 0:
            return None, stderr
        new_obj = cls(output_file, self.output_dir, self._ffmpeg, self._ffprobe)
        # return await new_obj.obj_video_scale(None, 'mp4',
        #                                      target_videobitrate=target_videobitrate,
        #                                      encode_lib=encode_lib)
        return new_obj, ''

    @_ffmpeg_opt()
    def obj_video_water_mark(self, output_file: str,
                             prefix: str,
                             *,
                             water_mark_type: 'H264EncoderArgs',
                             input_img: str,
                             ratio_img_height: float,
                             img_position_x: float,
                             img_position_y: float,
                             encode_lib=H264EncoderArgs.codec_v_h264_nvenc,
                             v_frame: int = H264EncoderArgs.v_frame_24,
                             preset_type=H264EncoderArgs.preset_veryslow,
                             crf_num=H264EncoderArgs.crf_23,
                             profile_type=H264EncoderArgs.profile_high,
                             level=H264EncoderArgs.level_4_2,
                             target_videobitrate: int = 0,
                             target_audiobitrate: int = H264EncoderArgs.audio_rate_64,
                             ) -> str:
        """
        生成打水印的命令
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
        :return: 添加水印的命令
        """
        target_videobitrate = int(self.video_bitrate / 1000) if not target_videobitrate \
            else (target_videobitrate if target_videobitrate < (self.video_bitrate / 1000)
                  else int(self.video_bitrate / 1000))
        v_frame = v_frame if v_frame < self.video_avgframerate else self.video_avgframerate
        assert all([i > 0 for i in (v_frame, target_videobitrate, target_audiobitrate, img_position_x, img_position_y)])
        assert 0 < ratio_img_height < 1
        # 检查图片是否存在
        assert os.path.isfile(input_img)
        # 获取图片尺寸
        _command = aioffmpeg_cmd.CMD_GET_VIDEO_PROBE.format(
            ffprobe_bin=self._ffprobe,
            input_file=input_img
        )
        status, stdout, stderr = self._simple_run_cmd(_command)
        if status != 0:
            return None
        # json 的异常 直接往外抛
        img_probe = json.loads(stdout)
        img_height = img_probe['streams'][0]['height']
        img_width = img_probe['streams'][0]['width']
        # 求出图片的目标高度
        target_img_height = self.video_height * ratio_img_height
        target_img_width = target_img_height * (img_width / img_height)
        # debug
        # print(img_width,img_height,target_img_width,target_img_height)
        # end debug
        assert all([int(i) > 0 for i in (target_img_height, target_img_width)])
        # 目标图片大小 小于视频大小
        assert target_img_height < self.video_height
        assert target_img_width < self.video_width
        _command = None
        if water_mark_type == H264EncoderArgs.water_mark_fix:
            # 固定位置水印命令
            # 判断x的位置是否可以容下水印图片
            img_position_x = img_position_x if (target_img_width + img_position_x) < self.video_width else (
                self.video_width - target_img_width + 1
            )
            img_position_y = img_position_y if (target_img_height + img_position_y) < self.video_height else (
                self.video_height - target_img_height + 1
            )
            _command = aioffmpeg_cmd.CMD_WATER_MARK_FIX.format(
                ffmpeg_bin=self._ffmpeg,
                input_video=self.videofile_path,
                input_img=input_img,
                encode_lib=encode_lib,
                prefix=prefix,
                img_height=int(target_img_height),
                X=img_position_x,
                Y=img_position_y,
                frame=v_frame,
                preset_type=preset_type,
                crf_num=crf_num,
                profile_type=profile_type,
                level=level,
                video_rate=target_videobitrate,
                audio_rate=target_audiobitrate,
                output_file=output_file
            )
        elif water_mark_type == H264EncoderArgs.water_mark_move:
            # 移动水印
            ST = random.randint(30, 60)  # 水印暂停的时间间隔
            # 图片初始位置 X
            LX_low = 30 if target_img_width + 30 <= self.video_width else 0
            LX_low = int(LX_low)
            LX_high = 100 if target_img_width + 100 <= self.video_width else (self.video_width - target_img_width) / 4
            LX_high = int(LX_high)
            # 图片初始位置 Y
            LY_low = 30 if target_img_height + 30 <= self.video_height else 0
            LY_low = int(LY_low)
            LY_high = 50 if target_img_height + 50 <= self.video_height else (self.video_height - target_img_height) / 4
            LY_high = int(LY_high)
            # 图片底部位置 X
            mid_width = self.video_width / 2
            MX_low = mid_width - 100 if target_img_width + mid_width - 100 <= self.video_width \
                                        and mid_width - 100 >= 0 \
                else (mid_width - target_img_width / 2 if mid_width + target_img_width / 2 < self.video_width else 0)
            MX_low = int(MX_low)
            MX_high = mid_width + 100 if target_img_width + mid_width + 100 <= self.video_width \
                else (mid_width if mid_width + target_img_width <= self.video_width else \
                          (self.video_width - target_img_width) / 2)
            MX_high = int(MX_high)
            # 图片底部位置 Y
            MY_low = self.video_height - 200 if target_img_height  <= 200 and \
                self.video_height - 200 >= 0 else (self.video_height - target_img_height) / 4
            MY_low = int(MY_low)
            MY_high = self.video_height - 80 if target_img_height <= 80 and \
                self.video_height - 80 >= 0 else self.video_height - target_img_height
            MY_high = int(MY_high)
            # 图片右边位置 X
            RX_low = self.video_width - target_img_width - 100 if self.video_width >= target_img_width + 100 else \
                (self.video_width - target_img_width) / 2
            RX_low = int(RX_low)
            RX_high = self.video_width - target_img_width - 20 if  self.video_width >= target_img_width + 20 else \
                self.video_width - target_img_width
            RX_high = int(RX_high)
            _command = aioffmpeg_cmd.CMD_WATER_MARK_MOVE.format(
                ffmpeg_bin=self._ffmpeg,
                input_video=self.videofile_path,
                input_img=input_img,
                encode_lib=encode_lib,
                prefix=prefix,
                img_height=int(target_img_height),
                ST=ST,          # 水印暂停的时间间隔
                TT=ST * 3 + 6,  # 一个循环的总时间
                LX=random.randint(LX_low, LX_high),     # X轴随机开始的位置
                LY=random.randint(LY_low, LY_high),     # Y轴随机开始的位置
                MX=random.randint(MX_low, MX_high),     # X轴底部的位置
                MY=random.randint(MY_low, MY_high),     # Y轴底部的位置
                RX=random.randint(RX_low, RX_high),     # X轴右侧位置
                frame=v_frame,
                preset_type=preset_type,
                crf_num=crf_num,
                profile_type=profile_type,
                level=level,
                video_rate=target_videobitrate,
                audio_rate=target_audiobitrate,
                output_file=output_file
            )
        return _command

    @_ffmpeg_opt()
    def obj_video_delog(self, output_file: str,
                        prefix: str,
                        *,
                        delog_tuple: tuple,
                        encode_lib=H264EncoderArgs.codec_v_h264_nvenc,
                        v_frame: int = H264EncoderArgs.v_frame_24,
                        preset_type=H264EncoderArgs.preset_veryslow,
                        crf_num=H264EncoderArgs.crf_23,
                        profile_type=H264EncoderArgs.profile_high,
                        level=H264EncoderArgs.level_4_2,
                        target_videobitrate: int = 0,
                        target_audiobitrate: int = H264EncoderArgs.audio_rate_64,
                        ) -> str:
        """
        返回删除水印的命令
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
        :return:
        """
        v_frame = v_frame if v_frame < self.video_avgframerate else self.video_avgframerate
        target_videobitrate = int(self.video_bitrate / 1000) if not target_videobitrate \
            else (target_videobitrate if target_videobitrate < (self.video_bitrate / 1000)
                  else int(self.video_bitrate / 1000))
        assert all([i > 0 for i in (v_frame, target_videobitrate, target_audiobitrate)])
        delog_opts = ','.join([self._dealwith_delog(args) for args in delog_tuple if self._dealwith_delog(args)])
        if delog_opts != '':
            delog_opts = ',' + delog_opts
        _command = aioffmpeg_cmd.CMD_DEL_WATER_MARK.format(
            ffmpeg_bin=self._ffmpeg,
            input_file=self.videofile_path,
            encode_lib=encode_lib,
            prefix=prefix,
            opts_del_log=delog_opts,
            frame=v_frame,
            preset_type=preset_type,
            crf_num=crf_num,
            profile_type=profile_type,
            level=level,
            video_rate=target_videobitrate,
            audio_rate=target_audiobitrate,
            output_file=output_file
        )
        return _command

    async def save_video(self, output_dir: str) -> 'bool, err_msg':
        """
        将原视频保存到目标目录
        调用者要保证目标目录存在,且具有写入权限
        :param output_dir: 目标目录
        :return: 成功返回 True 失败返回 False
        """
        output_dir = os.path.abspath(output_dir)
        if not os.path.isdir(output_dir):
            return False, f'{output_dir:s} not exists'
        _command = f"cp -f '{self.videofile_path:s}' '{output_dir:s}'"
        status, stdout, stderr = await self._run_cmd(_command)
        return (True, stderr) if status == 0 else (False, stderr)

    def __len__(self):
        return int(self.videofile_duration)

    async def __add__(self, other: 'H264Video object') -> 'H264Video object':
        """
        两个ffmpeg对象相加, 即拼接视频
        输出视频的 宽度 高度 由被加数觉决定, 码率由用户设置和两个视频的原本码率决定,取最小值
        :param other: 另外一个ffpmeg对象
        :return:
        """
        cls = type(self)
        assert isinstance(other, cls)
        encode_lib = H264EncoderArgs.codec_v_h264_nvenc if self.h264_nvenc else H264EncoderArgs.codec_v_libx264
        output, _ = await self.obj_video_concat(None, 'mp4', other, encode_lib=encode_lib)
        return output

    async def __getitem__(self, item):
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
                result = [await self.str_video_snapshot(None, 'png', start_time=startime + delta_time * count)
                        for count in range(pic_count)]
                return [ pic_path[0] for pic_path in result if pic_path[0] is not None]
            else:
                # step > 0, 是要剪辑视频, 将视频剪辑成1s片段,step为片段个数
                delta_time = (stop + 1 - start) / step
                startime = start
                result = [await self.obj_video_cut(None, 'mp4', start_time=startime + delta_time * count,
                                                   encode_lib=H264EncoderArgs.codec_v_libx264)
                          for count in range(step)]
                return [ffmpeg_obj[0] for ffmpeg_obj in result if ffmpeg_obj[0] is not None]
        elif isinstance(item, numbers.Integral):
            # 以item为开始时间,截取时长为一秒的视频
            result, _ = await self.obj_video_cut(None, 'mp4', start_time=item,
                                                 encode_lib=H264EncoderArgs.codec_v_libx264)
            return result
        else:
            msg = '{cls.__name__} indices must be integral'
            raise TypeError(msg.format(cls=cls))

    def __repr__(self):
        return f'<{self.videofile_path:s}, libx264:{self.libx264!r}, h264_nvenc:{self.h264_nvenc!r}>'

    def __del__(self):
        """
        改函数会删除 self.videofile_path
        所以调用者要保存好 videofile 原文件的副本
        本类提供save_video的方法,将原视频保存到目标目录
        :return:
        """
        _commad = f"rm -rf '{self.videofile_path:s}'"
        _, _, _ = self._simple_run_cmd(_commad)
