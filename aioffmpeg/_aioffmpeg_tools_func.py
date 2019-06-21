#!/usr/bin/env python
# -*- coding: utf-8 -*
from aioffmpeg_tools_func import *
from aioffmpeg_cmd_opts import *

import os
import time
from functools import wraps
import random
import json
import aiofiles


# 创建输出文件和2-pass ffmpeg encoder log prefix
def _mk_outputfile_and_ffmpeg2passprefix(cls_obj, output_dir: str,
                                         file_extensions: str) -> tuple:
    """
    生成output_file 和 ffmpeg 2pass log prefix
    出错返回 None, None
    :param output_dir: 目标输出目录
    :param output_dir_default: 默认输出目录
    :param origin_file_path: 源文件路径
    :param file_extensions: 文件扩展名
    :return: output_file, prefix
    """
    # 如果传入的 output_dir 为 None 或者为 空字符串, 则使用初始化类时使用的 output_dir
    if not output_dir:
        output_dir = cls_obj.output_dir
    origin_file_path = os.path.abspath(cls_obj.videofile_path)
    output_dir = os.path.abspath(output_dir)
    if not os.path.isdir(output_dir):
        return None, None
    # 目标文件路径
    ori_file_name = '.'.join(os.path.split(origin_file_path)[1].split('.')[:-1])
    output_file = output_dir + '/' + ori_file_name + str(time.time()) + '.' + file_extensions
    # 2步编码的日志文件前缀
    prefix = cls_obj.prefix_2pass + str(time.time())
    return output_file, prefix


# ffmpeg命令执行装饰器
def _ffmpeg_do_cmd(self, is_aio: bool = True):
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
            async def wrapper(output_dir, file_extensions, cmd_model, *args, **kwargs):
                output_file, prefix = _mk_outputfile_and_ffmpeg2passprefix(self, output_dir, file_extensions)
                if not all((output_file, prefix)):
                    return None, 'create output file error'
                auto_clear = kwargs.pop('auto_clear') if 'auto_clear' in kwargs else False
                _cmd1, _cmd2 = await fn(self, output_file, prefix, cmd_model, *args, **kwargs)
                if _cmd1 is None:
                    return None, 'command create error'
                status, _, stderr = await run_cmd(_cmd1)
                # debug
                # print(status)
                # end debug
                # 由于一些命令要使用 prefix 开头的文件做临时文件,所以不能直接删除
                if status != 0:
                    if _cmd2 is not None:
                        status, _, stderr = await run_cmd(_cmd2)
                        if status != 0:
                            return None, stderr
                    else:
                        return None, stderr
                if file_extensions == 'mp4':
                    ret_obj = self.__class__(output_file, self.output_dir, self._ffmpeg,
                                             self._ffprobe, is_aio, auto_clear)
                    return ret_obj, ''
                else:
                    return output_file, ''
        else:
            @wraps(fn)
            def wrapper(output_dir, file_extensions, cmd_model, *args, **kwargs):
                output_file, prefix = _mk_outputfile_and_ffmpeg2passprefix(self, output_dir, file_extensions)
                if not all((output_file, prefix)):
                    return None, 'create output file error'
                auto_clear = kwargs.pop('auto_clear') if 'auto_clear' in kwargs else False
                _cmd1, _cmd2 = fn(self, output_file, prefix, cmd_model, *args, **kwargs)
                if _cmd1 is None:
                    return None, 'command create error'
                status, _, stderr = simple_run_cmd(_cmd1)
                # debug
                # print(status)
                # end debug
                # 由于一些命令要使用 prefix 开头的文件做临时文件,所以不能直接删除
                if status != 0:
                    if _cmd2 is not None:
                        status, _, stderr = simple_run_cmd(_cmd2)
                        if status != 0:
                            return None, stderr
                    else:
                        return None, stderr
                if file_extensions == 'mp4':
                    ret_obj = self.__class__(output_file, self.output_dir, self._ffmpeg,
                                             self._ffprobe, is_aio, auto_clear)
                    return ret_obj, ''
                else:
                    return output_file, ''
        return wrapper
    return decorate


def _dealwith_delog(cls_obj, delog_args: 'namedtuple') -> str:
    """
    处理去除水印参数,如果参数有明显越界,返回''空字符串
    :param delog_args: 去除水印参数的具名元祖,由create_delog_args产生
    :return: 返回去除水印选项的字符串
    """
    if delog_args.pos_x > cls_obj.video_width or delog_args.pos_y > cls_obj.video_height or \
        delog_args.width + delog_args.pos_x > cls_obj.video_width or \
        delog_args.height + delog_args.pos_y > cls_obj.video_height or delog_args.end_time < delog_args.begin_time:
        return None
    opts = FfmpegOptsModel.del_log.format(
        X=delog_args.pos_x,
        Y=delog_args.pos_y,
        width=delog_args.width,
        height=delog_args.height,
        begin_time=delog_args.begin_time,
        end_time=delog_args.end_time
    )
    return opts


def _cmd_tools_base_info(cls_obj, args_dict, prefix, encode_lib, preset_type, crf_num, profile_type, level,
                         input_img, output_file, target_width, target_height,
                         v_frame, target_videobitrate, target_audiobitrate, start_time, last_time,
                         rotate_direct, ts_time, fix_ts_time, ts_prefix, delog_tuple):
    """
    命令创建工具函数,仅供内部使用,错误检查较少
    创建基础信息参数字典,机不需要复杂处理的参数
    失败返回空值
    """
    args_dict['ffmpeg_bin'] = cls_obj._ffmpeg
    args_dict['prefix'] = prefix
    # 编码参数
    args_dict['encode_lib'] = encode_lib
    args_dict['preset_type'] = preset_type if encode_lib == H264EncoderArgs.codec_v_libx264 \
        else H264EncoderArgs.preset_slow
    args_dict['crf_num'] = crf_num
    args_dict['profile_type'] = profile_type
    args_dict['level'] = level
    # 文件绝对路径
    args_dict['input_file'] = os.path.abspath(cls_obj.videofile_path)
    args_dict['input_img'] = os.path.abspath(input_img) if input_img else None
    args_dict['output_file'] = os.path.abspath(output_file)
    # 输出目录绝对路径
    args_dict['output_dir'] = os.path.split(output_file)[0]
    # 处理目标视频宽高
    target_width = cls_obj.video_width if not target_width else target_width
    target_height = cls_obj.video_height if not target_height else target_height
    target_width = int(int(target_width / 2) * 2)
    target_height = int(int(target_height / 2) * 2)
    # 处理目标视频帧率,不超过原始视频帧率
    v_frame = v_frame if v_frame < cls_obj.video_avgframerate else cls_obj.video_avgframerate
    # 处理目标视频码率,不超过原始视频码率
    target_videobitrate = int(cls_obj.video_bitrate / 1000) if not target_videobitrate \
        else (target_videobitrate if target_videobitrate < (cls_obj.video_bitrate / 1000)
              else int(cls_obj.video_bitrate / 1000))
    # 视频截图和裁剪
    # 时间大于1天的都安一天以内执行
    # 起始时间超过一天或者超过视频长度,直接截断
    #start_time = (start_time % 86400) % int(cls_obj.videofile_duration)
    # 持续时间超过一天,直接截断
    #last_time = (last_time % 86400)
    # 起始时间加上持续时间不能超过视频长度,超过则持续到视频结束
    last_time = last_time if start_time + last_time <= cls_obj.videofile_duration \
        else cls_obj.videofile_duration - start_time
    # 判断参数的合法性
    if any([i <= 0 for i in (target_width, target_height, v_frame, target_videobitrate,
                             target_audiobitrate, last_time)]) \
            or start_time < 0 or start_time >= cls_obj.videofile_duration:
        return None
    args_dict['target_width'] = target_width
    args_dict['target_height'] = target_height
    args_dict['frame'] = v_frame
    args_dict['video_rate'] = target_videobitrate
    args_dict['audio_rate'] = target_audiobitrate
    #str_start_time = '0' + str(datetime.timedelta(seconds=start_time)) if start_time < 36000 \
    #    else str(datetime.timedelta(seconds=start_time))
    #str_last_time = '0' + str(datetime.timedelta(seconds=last_time)) if last_time < 36000 \
    #    else str(datetime.timedelta(seconds=last_time))
    args_dict['start_time'] = start_time
    args_dict['last_time'] = last_time
    # 旋转视频
    args_dict['rotate_direct'] = rotate_direct
    # hls
    args_dict['ts_time'] = ts_time
    args_dict['fix_ts_time'] = fix_ts_time
    args_dict['ts_prefix'] = ts_prefix
    # 删除水印参数
    delog_opts = ''
    if delog_tuple is not None:
        delog_opts = ','.join([_dealwith_delog(cls_obj, args)
                               for args in delog_tuple if _dealwith_delog(cls_obj, args)])
        if delog_opts != '':
            delog_opts = ',' + delog_opts
    args_dict['opts_del_log'] = delog_opts
    return args_dict


def _cmd_tools_scale_video(cls_obj, args_dict, target_width, target_height):
    """
    命令创建工具函数,仅供内部使用,错误检查较少
    创建视频缩放命令时的特殊处理
    失败返回空值
    """
    # 判断视频的宽高比
    # 计算目标视频宽高比,保留3位小数
    target_whratio = round(float(target_width) / float(target_height), 4)
    # 计算原视频宽高比,保留3位小数
    origin_whratio = round(float(cls_obj.video_width) / float(cls_obj.video_height), 4)
    # 缩放视频
    # 根据宽高比生成不同的命令
    if target_whratio == origin_whratio:
        # 缩放长宽比相同
        pad_options = ''
    elif target_whratio > origin_whratio:
        # 缩放后视频的宽度比原视频宽,需要在缩放后的视频两边填充黑边
        pad_options = FfmpegOptsModel.pad_left_right.format(
            target_width=target_width,
            target_height=target_height,
        )
        target_width = int(round(target_height * origin_whratio, 0))
        target_width = int(int(target_width / 2) * 2)
    else:
        # 缩放后视频的高度比原视频高,需要在缩放后的视频上下填充黑边
        pad_options = FfmpegOptsModel.pad_up_down.format(
            target_width=target_width,
            target_height=target_height,
        )
        target_height = int(round(target_width / origin_whratio, 0))
        target_height = int(int(target_height / 2) * 2)
    # 判断参数的合法性
    if any([i <= 0 for i in (target_width, target_height)]):
        # 参数不合法直接返回 两个空命令
        return None
    args_dict['target_width'] = target_width
    args_dict['target_height'] = target_height
    args_dict['pad_options'] = pad_options
    return args_dict


def _cmd_tools_concate_vide(cls_obj, args_dict, input_obj, target_videobitrate, v_frame):
    """
    命令创建工具函数,仅供内部使用,错误检查较少
    创建视频拼接命令时的特殊处理
    失败返回空值
    """
    cls = type(cls_obj)
    # 判断输入的对象是否和 cls_obj 是同一类对象, 且 input_obj 不是 cls_obj
    if input_obj is cls_obj or not isinstance(input_obj, cls):
        return None
    target_videobitrate = min(target_videobitrate, int(input_obj.video_bitrate / 1000))
    v_frame = min(v_frame, int(input_obj.video_avgframerate))
    if any([i <= 0 for i in (target_videobitrate, v_frame)]):
        return None
    args_dict['video_rate'] = target_videobitrate
    args_dict['frame'] = v_frame
    return args_dict


def _cmd_tools_log_video(cls_obj, args_dict, img_position_x, img_position_y,
                         ratio_img_height, input_img_width, input_img_height):
    """
    命令创建工具函数,仅供内部使用,错误检查较少
    创建视频命令时的特殊处理
    失败返回空值
    """
    if 0.0 < ratio_img_height < 1.0 and input_img_width > 0 and input_img_height > 0:
        # 有正常的图片参数
        # 求出图片的目标高度
        target_img_height = cls_obj.video_height * ratio_img_height
        target_img_width = target_img_height * (input_img_width / input_img_height)
        # 水印基础信息,固定水印用
        args_dict['X'] = int(img_position_x if img_position_x + target_img_width <= cls_obj.video_width else
                             (cls_obj.video_width - target_img_width))
        args_dict['Y'] = int(img_position_y if img_position_y + target_img_height <= cls_obj.video_height
            else (cls_obj.video_height - target_img_height))
        # debug
        # print('X:', args_dict['X'])
        # print('Y:', args_dict['Y'])
        # print(f'input_img_height: {input_img_height:f}, input_img_width:{input_img_width:f}')
        # print(f'target_img_height: {target_img_height:f}, target_img_width: {target_img_width:f}, '
        #       f'cls_obj.video_height: {cls_obj.video_height:f}, cls_obj.video_width: {cls_obj.video_width:f}')
        # end debug
        # 水印比率正常
        # 移动水印
        ST = random.randint(30, 60)  # 水印暂停的时间间隔
        # 图片初始位置 X
        LX_low = 30 if target_img_width + 30 <= cls_obj.video_width else 0
        LX_low = int(LX_low)
        LX_high = 100 if target_img_width + 100 <= cls_obj.video_width else \
            ((cls_obj.video_width - target_img_width) / 4)
        LX_high = int(LX_high)
        # debug
        # print(f'LX_low:{LX_low:d}, LX_high:{LX_high:d}')
        # end debug
        if LX_low > LX_high:
            LX_low = int(LX_high / 8)
        # debug
        # print(f'LX_low:{LX_low:d}, LX_high:{LX_high:d}')
        # end debug
        # 图片初始位置 Y
        LY_low = 30 if target_img_height + 30 <= cls_obj.video_height else 0
        LY_low = int(LY_low)
        LY_high = 50 if target_img_height + 50 <= cls_obj.video_height else \
            ((cls_obj.video_height - target_img_height) / 4)
        LY_high = int(LY_high)
        # debug
        # print(f'LY_low:{LY_low:d}, LY_high:{LY_high:d}')
        # end debug
        if LY_low > LY_high:
            LY_low = int(LY_high / 8)
        # debug
        # print(f'LY_low:{LY_low:d}, LY_high:{LY_high:d}')
        # end debug
        # 图片底部位置 X
        mid_width = cls_obj.video_width / 2
        MX_low = (mid_width - 100) if target_img_width + mid_width - 100 <= cls_obj.video_width \
                                      and mid_width - 100 >= 0 \
            else ((mid_width - target_img_width / 2) if mid_width + target_img_width / 2 < cls_obj.video_width else 0)
        MX_low = int(MX_low)
        MX_high = (mid_width + 100) if target_img_width + mid_width + 100 <= cls_obj.video_width \
            else (mid_width if mid_width + target_img_width <= cls_obj.video_width else \
                      ((cls_obj.video_width - target_img_width) / 2))
        MX_high = int(MX_high)
        # debug
        # print(f'MX_low:{MX_low:d}, MX_high:{MX_high:d}')
        # end debug
        if MX_low > MX_high:
            MX_low = int(MX_high / 4)
        # debug
        # print(f'MX_low:{MX_low:d}, MX_high:{MX_high:d}')
        # end debug
        # 图片底部位置 Y
        MY_low = (cls_obj.video_height - 200) if target_img_height <= 200 and \
                                               cls_obj.video_height - 200 >= 0 else \
            ((cls_obj.video_height - target_img_height) / 4)
        MY_low = int(MY_low)
        MY_high = (cls_obj.video_height - 80) if target_img_height <= 80 and \
                                               cls_obj.video_height - 80 >= 0 else \
            (cls_obj.video_height - target_img_height)
        MY_high = int(MY_high)
        # debug
        # print(f'MY_low:{MY_low:d}, MX_high:{MY_high:d}')
        # end debug
        if MY_low > MY_high:
            MX_low = int(MY_high / 4)
        # debug
        # print(f'MY_low:{MY_low:d}, MX_high:{MY_high:d}')
        # end debug
        # 图片右边位置 X
        RX_low = (cls_obj.video_width - target_img_width - 100) if cls_obj.video_width >= target_img_width + 100 else \
            ((cls_obj.video_width - target_img_width) / 2)
        RX_low = int(RX_low)
        RX_high = (cls_obj.video_width - target_img_width - 20) if cls_obj.video_width >= target_img_width + 20 else \
            (cls_obj.video_width - target_img_width)
        RX_high = int(RX_high)
        # debug
        # print(f'RX_low:{RX_low:d}, RX_high:{RX_high:d}')
        # end debug
        if RX_low > RX_high:
            RX_low = int(RX_high / 2)
        # debug
        # print(f'RX_low:{RX_low:d}, RX_high:{RX_high:d}')
        # end debug
        args_dict['img_height'] = int(target_img_height) if int(target_img_height) > 0 else 1
        args_dict['ST'] = ST            # 水印暂停的时间间隔
        args_dict['TT'] = ST * 3 + 6    # 一个循环的总时间
        args_dict['LX'] = random.randint(LX_low, LX_high)  # X轴随机开始的位置
        args_dict['LY'] = random.randint(LY_low, LY_high)  # Y轴随机开始的位置
        args_dict['MX'] = random.randint(MX_low, MX_high)  # X轴底部的位置
        args_dict['MY'] = random.randint(MY_low, MY_high)  # Y轴底部的位置
        args_dict['RX'] = random.randint(RX_low, RX_high)  # X轴右侧位置
        return args_dict
    else:
        return None


async def _create_command_aio(cls_obj, output_file: str, prefix: str,
                              cmd_model: 'ffmpeg_cmd_model',
                              *,
                              # 输入
                              input_obj: 'H264Video obj' = None,  # 拼接视频是传入的另外的H264Video实例
                              input_img: str = None,
                              # 音视频基础参数
                              target_width: int = 0,
                              target_height: int = 0,
                              target_videobitrate: int = 0,
                              target_audiobitrate: 'H264EncoderArgs' = H264EncoderArgs.audio_rate_128,
                              v_frame: 'H264EncoderArgs' = H264EncoderArgs.v_frame_24,
                              # 编码相关
                              encode_lib: 'H264EncoderArgs' = H264EncoderArgs.codec_v_h264_nvenc,
                              preset_type: 'H264EncoderArgs' = H264EncoderArgs.preset_veryslow,
                              crf_num: 'H264EncoderArgs' = H264EncoderArgs.crf_23,
                              profile_type: 'H264EncoderArgs' = H264EncoderArgs.profile_high,
                              level: 'H264EncoderArgs' = H264EncoderArgs.level_4_2,
                              # 旋转视频方向参
                              rotate_direct: 'H264EncoderArgs' = H264EncoderArgs.v_left_rotate,
                              # hls相关
                              ts_time: int = 10,
                              fix_ts_time: 'H264EncoderArgs' = H264EncoderArgs.no_fix_ts_time,
                              ts_prefix: str = 'ts',
                              # 截图,裁剪视频相关
                              start_time: float = 0,
                              last_time: float = 1,
                              # 添加图片水印相关
                              ratio_img_height: float = 0.0,
                              img_position_x: float = 0.0,
                              img_position_y: float = 0.0,
                              # 删除图片水印相关
                              delog_tuple: tuple = None) -> str:
    """
    :param cls_obj: ffmpeg 相关对象
    :param output_file: 视频输出文件
    :param prefix: two-pass log 前缀
    # 输入文件
    :param input_obj: 拼接视频时使另外一个输入实例
    :param input_img: 水印图片
    # 音视频基础参数
    :param target_width: 输出视频目标宽度
    :param target_height: 输出视频目标高度
    :param target_videobitrate: 输出视频目标码率
    :param target_audiobitrate: 输出音频目标码率
    :param v_frame: 输出视频目标帧率
    # 编码相关
    :param encode_lib: h264编码使用的外部库
    :param preset_type: 编码速度参数
    :param crf_num: Constant Rate Factor 值
    :param profile_type: 编码配置文件
    :param level: 编码级别
    # 旋转视频方向参数
    :param rotate_direct: 视频旋转方向
    # hls相关
    :param ts_time: ts切片时长
    :param fix_ts_time: 是否固定切片时长
    :param ts_prefix: ts 切片前缀名
    # 截图,裁剪视频相关
    :param start_time: 截图或裁剪视频起始时间
    :param last_time: 裁剪视频持续时间
    # 水印相关
    :param ratio_img_height: 图片水印高度和源视频高度只比
    :param img_position_x: 固定图片水印x轴位置
    :param img_position_y: 固定图片水印y轴位置
    # 删除图片水印相关
    delog_tuple: 删除水印是的参数元祖
    """
    args_dict = dict()
    cmd2 = None
    args_dict['input_file1'] = None
    args_dict['input_file2'] = None
    args_dict = _cmd_tools_base_info(cls_obj, args_dict, prefix, encode_lib, preset_type, crf_num, profile_type, level,
                                     input_img, output_file, target_width, target_height,
                                     v_frame, target_videobitrate, target_audiobitrate, start_time, last_time,
                                     rotate_direct, ts_time, fix_ts_time, ts_prefix, delog_tuple)
    if args_dict is None:
        return None, None
    # 视频缩放的特殊处理
    if cmd_model == FfmpegCmdModel.scale_video:
        args_dict = _cmd_tools_scale_video(cls_obj, args_dict, args_dict['target_width'], args_dict['target_height'])
        if args_dict is None:
            return None, None
    # hls 视频的特殊处理
    if cmd_model == FfmpegCmdModel.hls_video:
        cmd2 = FfmpegCmdModel.hls_video_other.format(**args_dict)
    # 拼接视频的特殊处理
    if cmd_model == FfmpegCmdModel.concat_video:
        if input_obj is None or not hasattr(input_obj, 'aio'):
            return None, None
        if not all([i for i in (cls_obj.aio, input_obj.aio)]):
            return None, None
        args_dict = _cmd_tools_concate_vide(cls_obj, args_dict, input_obj,  args_dict['video_rate'], args_dict['frame'])
        if args_dict is None:
            return None, None
        # 将两个视频的格式统一
        input_obj1, _ = await cls_obj.cmd_do_aio(None, 'mp4', FfmpegCmdModel.scale_video,
                                                 auto_clear=True,
                                                 encode_lib=args_dict['encode_lib'],
                                                 target_videobitrate=args_dict['video_rate'],
                                                 v_frame=args_dict['frame'])
        input_obj2, _ = await input_obj.cmd_do_aio(None, 'mp4', FfmpegCmdModel.scale_video,
                                                   auto_clear=True,
                                                   target_width=cls_obj.video_width,
                                                   target_height=cls_obj.video_height,
                                                   encode_lib=args_dict['encode_lib'],
                                                   target_videobitrate=args_dict['video_rate'],
                                                   v_frame=args_dict['frame'])
        if not all([input_obj1, input_obj2]):
            return None, None
        args_dict['input_file1'] = input_obj1.videofile_path
        args_dict['input_file2'] = input_obj2.videofile_path
        concat_file = prefix + str(time.time()) + str(random.random()) + '.txt'
        try:
            concat_str = f"file '{args_dict['input_file1']:s}'\nfile '{args_dict['input_file2']:s}'\n"
            async with aiofiles.open(concat_file, mode='w') as f:
                await f.write(concat_str)
        except (PermissionError, IOError, ValueError):
            concat_file = None
        # 如果是视频拼接,第二种拼接方式命令生成
        if concat_file is not None:
            try:
                cmd2 = FfmpegCmdModel.concat_video_safe.format(
                            ffmpeg_bin=cls_obj._ffmpeg,
                            concat_file=concat_file,
                            output_file=output_file)
            except ValueError:
                cmd2 = None
    # 需要处理水印
    if cmd_model == FfmpegCmdModel.logo_video_fix or cmd_model == FfmpegCmdModel.logo_video_move:
        if input_img is None:
            return None, None
        _command = FfmpegCmdModel.get_video_probe.format(
            ffprobe_bin=cls_obj._ffprobe,
            input_file=input_img
        )
        status, stdout, _ = await run_cmd(_command)
        if status != 0:
            return None, None
        # json 的异常 直接往外抛
        try:
            img_probe = json.loads(stdout)
            input_img_width = img_probe['streams'][0]['width']
            input_img_height = img_probe['streams'][0]['height']
        except (KeyError, IndexError, TypeError, ValueError):
            return None, None
        args_dict = _cmd_tools_log_video(cls_obj, args_dict, img_position_x, img_position_y,
                                         ratio_img_height, input_img_width, input_img_height)
        if args_dict is None:
            return None, None
    # debug
    # print(args_dict)
    # end debug
    try:
        cmd1 = cmd_model.format(**args_dict)
    except ValueError:
        # 格式化字符串错误
        return None, None
    return cmd1, cmd2


def _create_command(cls_obj, output_file: str, prefix: str,
                    cmd_model: 'ffmpeg_cmd_model',
                    *,
                    # 输入
                    input_obj: 'H264Video obj' = None,  # 拼接视频是传入的另外的H264Video实例
                    input_img: str = None,
                    # 音视频基础参数
                    target_width: int = 0,
                    target_height: int = 0,
                    target_videobitrate: int = 0,
                    target_audiobitrate: 'H264EncoderArgs' = H264EncoderArgs.audio_rate_64,
                    v_frame: 'H264EncoderArgs' = H264EncoderArgs.v_frame_24,
                    # 编码相关
                    encode_lib: 'H264EncoderArgs' = H264EncoderArgs.codec_v_h264_nvenc,
                    preset_type: 'H264EncoderArgs' = H264EncoderArgs.preset_veryslow,
                    crf_num: 'H264EncoderArgs' = H264EncoderArgs.crf_23,
                    profile_type: 'H264EncoderArgs' = H264EncoderArgs.profile_high,
                    level: 'H264EncoderArgs' = H264EncoderArgs.level_4_2,
                    # 旋转视频方向参
                    rotate_direct: 'H264EncoderArgs' = H264EncoderArgs.v_left_rotate,
                    # hls相关
                    ts_time: int = 10,
                    fix_ts_time: 'H264EncoderArgs' = H264EncoderArgs.no_fix_ts_time,
                    ts_prefix: str = 'ts',
                    # 截图,裁剪视频相关
                    start_time: float = 0,
                    last_time: float = 1,
                    # 添加图片水印相关
                    ratio_img_height: float = 0.0,
                    img_position_x: float = 0.0,
                    img_position_y: float = 0.0,
                    # 删除图片水印相关
                    delog_tuple: tuple = None) -> str:
    """
    :param cls_obj: ffmpeg 相关对象
    :param output_file: 视频输出文件
    :param prefix: two-pass log 前缀
    # 输入文件
    :param input_obj: 拼接视频时使另外一个输入实例
    :param input_img: 水印图片
    # 音视频基础参数
    :param target_width: 输出视频目标宽度
    :param target_height: 输出视频目标高度
    :param target_videobitrate: 输出视频目标码率
    :param target_audiobitrate: 输出音频目标码率
    :param v_frame: 输出视频目标帧率
    # 编码相关
    :param encode_lib: h264编码使用的外部库
    :param preset_type: 编码速度参数
    :param crf_num: Constant Rate Factor 值
    :param profile_type: 编码配置文件
    :param level: 编码级别
    # 旋转视频方向参数
    :param rotate_direct: 视频旋转方向
    # hls相关
    :param ts_time: ts切片时长
    :param fix_ts_time: 是否固定切片时长
    :param ts_prefix: ts 切片前缀名
    # 截图,裁剪视频相关
    :param start_time: 截图或裁剪视频起始时间
    :param last_time: 裁剪视频持续时间
    # 水印相关
    :param ratio_img_height: 图片水印高度和源视频高度只比
    :param img_position_x: 固定图片水印x轴位置
    :param img_position_y: 固定图片水印y轴位置
    # 删除图片水印相关
    delog_tuple: 删除水印是的参数元祖
    """
    args_dict = dict()
    cmd2 = None
    args_dict['input_file1'] = None
    args_dict['input_file2'] = None
    args_dict = _cmd_tools_base_info(cls_obj, args_dict, prefix, encode_lib, preset_type, crf_num, profile_type, level,
                                     input_img, output_file, target_width, target_height,
                                     v_frame, target_videobitrate, target_audiobitrate, start_time, last_time,
                                     rotate_direct, ts_time, fix_ts_time, ts_prefix, delog_tuple)
    if args_dict is None:
        return None, None
    # 视频缩放的特殊处理
    if cmd_model == FfmpegCmdModel.scale_video:
        args_dict = _cmd_tools_scale_video(cls_obj, args_dict, args_dict['target_width'], args_dict['target_height'])
        if args_dict is None:
            return None, None
    # hls 视频的特殊处理
    if cmd_model == FfmpegCmdModel.hls_video:
        cmd2 = FfmpegCmdModel.hls_video_other.format(**args_dict)
    # 拼接视频的特殊处理
    if cmd_model == FfmpegCmdModel.concat_video:
        if input_obj is None:
            return None, None
        args_dict = _cmd_tools_concate_vide(cls_obj, args_dict, input_obj, args_dict['video_rate'], args_dict['frame'])
        if args_dict is None:
            return None, None
        # 将两个视频的格式统一
        input_obj1, _ = cls_obj.cmd_do(None, 'mp4', FfmpegCmdModel.scale_video,
                                       auto_clear=True,
                                       encode_lib=args_dict['encode_lib'],
                                       target_videobitrate=args_dict['video_rate'],
                                       v_frame=args_dict['frame'])
        input_obj2, _ = input_obj.cmd_do(None, 'mp4', FfmpegCmdModel.scale_video,
                                         auto_clear=True,
                                         target_width=cls_obj.video_width,
                                         target_height=cls_obj.video_height,
                                         encode_lib=args_dict['encode_lib'],
                                         target_videobitrate=args_dict['video_rate'],
                                         v_frame=args_dict['frame'])
        if not all([input_obj1, input_obj2]):
            return None, None
        args_dict['input_file1'] = input_obj1.videofile_path
        args_dict['input_file2'] = input_obj2.videofile_path
        concat_file = prefix + str(time.time()) + str(random.random()) + '.txt'
        try:
            concat_str = f"file '{args_dict['input_file1']:s}'\nfile '{args_dict['input_file2']:s}'\n"
            with open(concat_file, 'w') as f:
                f.write(concat_str)
        except (PermissionError, IOError, ValueError):
            concat_file = None
        # 如果是视频拼接,第二种拼接方式命令生成
        if concat_file is not None:
            try:
                cmd2 = FfmpegCmdModel.concat_video_safe.format(
                            ffmpeg_bin=cls_obj._ffmpeg,
                            concat_file=concat_file,
                            output_file=output_file)
            except ValueError:
                cmd2 = None
    # 需要处理水印
    if cmd_model == FfmpegCmdModel.logo_video_fix or cmd_model == FfmpegCmdModel.logo_video_move:
        if input_img is None:
            return None, None
        _command = FfmpegCmdModel.get_video_probe.format(
            ffprobe_bin=cls_obj._ffprobe,
            input_file=input_img
        )
        status, stdout, _ = simple_run_cmd(_command)
        if status != 0:
            return None, None
        # json 的异常 直接往外抛
        try:
            img_probe = json.loads(stdout)
            input_img_width = img_probe['streams'][0]['width']
            input_img_height = img_probe['streams'][0]['height']
        except (KeyError, IndexError, TypeError, ValueError):
            return None, None
        args_dict = _cmd_tools_log_video(cls_obj, args_dict, img_position_x, img_position_y,
                                         ratio_img_height, input_img_width, input_img_height)
        if args_dict is None:
            return None, None
    # debug
    # print(args_dict)
    # end debug
    try:
        cmd1 = cmd_model.format(**args_dict)
    except (ValueError, KeyError):
        # 格式化字符串错误
        return None, None
    return cmd1, cmd2
