from aioffmpeg.h264video import H264Video
from aioffmpeg.cmd_opts import H264EncoderArgs, FfmpegCmdModel
from aioffmpeg.tools_func import *
import argparse
import os
import uuid

"""
命令行都是单线程执行
所以仅使用H264Video非异步的功能
ffmpeg 和 ffprobe 程序必须要在PATH中, 且不能使用 alias
"""
def _init_tools(input_file:str = None, output:str = None) -> tuple:
    """
    使用在main中的工具函数
    :param: input_file: 如果不为None,则计算绝对路径,且初始化成H264Video实例
    :param: output: 如果不为None,则计算绝对路径
    return  H264Video obj(None or Not None), abspath output(None or not None)
    """
    status, stdout, _ = simple_run_cmd(r'which ffmpeg')
    if status != 0:
        print(r'can not find ffmpeg bin in $PATH')
        exit(-1)
    ffmpeg_bin = stdout.replace('\n', '')
    status, stdout, stderr = simple_run_cmd(r'which ffprobe')
    if status != 0:
        print(r'can not find ffprobe bin in $PATH')
        exit(-1)
    ffprobe_bin = stdout.replace('\n', '')
    if input_file is not None:
        input_file = os.path.abspath(input_file)
        try: 
            h264_obj = H264Video(input_file, r'/tmp', ffmpeg_bin, ffprobe_bin, aio=False)
        except (Exception,FileNotFoundError):
            print(f'initial H264Video failed with {ffmpeg_bin} {ffprobe_bin} {input_file}')
            exit(-1)
    else:
        h264_obj = None
    if output is not None:
        output = os.path.abspath(output)
    return h264_obj, output


# h264_转码工作流基础函数
def _h264_workflow_base(input_obj: 'H246Video', cmd_model: 'FfmpegCmdModel', file_extension, 
                        dest_dir: str = None, needel = True, output_file = None, **kwargs) -> None:
    """
    :param input_obj: 输入的H264Video实例
    :param cmd_model: 编码使用的命令
    :param dest_dir: 输出目录
    :param file_extension: 文件扩展名
    :param needel: 是否需要删除input_obj
    :param output_file: 不为空则将输出文件移动之output_file
    :param kwargs: 转码使用的参数
    :return: None
    """
    if not isinstance(input_obj, H264Video):
        print(f'{input_obj} is not a instance of H264Video')
        exit(-1)
    if dest_dir:
        dest_dir = os.path.abspath(dest_dir)
    else:
        dest_dir = r'/tmp'
    status, _, _ = simple_run_cmd(f'mkdir -p {dest_dir}')
    if status != 0:
        print(f'can not make dir {dest_dir}')
        exit(-1)
    output, err = input_obj.cmd_do(dest_dir, file_extension, cmd_model, **kwargs)
    if output is None:
        print(err)
        exit(-1)
    if isinstance(output, H264Video):
        output._auto_clear = True
    if needel:
        del input_obj
    if output_file:
        if isinstance(output, H264Video):
            status, _, stderr = simple_run_cmd(f'mv -f {output.videofile_path} {output_file}')
        else:
            status, _, stderr = simple_run_cmd(f'mv -f {output} {output_file}')
        if status != 0:
            print(f'{stderr}')
            exit(-1)
    return output


def main():
    parser = argparse.ArgumentParser(description='aioffmpeg command line tools')
    parser.add_argument(r'--function', r'-f', required=True, choices='msctndagh', default=None,
                        help=r"this tool's functions, m: concat ts from m3u8 file, s: scale video, "
                             r"c: cut video, t: concat video, n: take a snapshot from video, "
                             r"d: delete video logo, a: add logo to video, "
                             r"g: make a gif from video, h: make hls ts from video")
    parser.add_argument(r'--input', r'-i', required=True, default=None, 
                        action=r'append', nargs=r'+', 
                        help=r'input m3u8 file(local or url), or input video')
    parser.add_argument(r'--output', r'-o', required=True, default=None, help=r'output file(jpg,gif,mp4,m3u8)')
    parser.add_argument(r'--width', r'-w', default=0, help=r"video width, default using source video's width")
    parser.add_argument(r'--height', r'-e', default=0, help=r"video(image) height, default using source video's height,image only has height")
    parser.add_argument(r'--videorate', r'-r', default=0, help=r"video rate, default using source video's video rate")
    parser.add_argument(r'--codeclib', r'-l', choices='gc', default='c', help=r'video codec lib, g: gpu codec, c: cpu codec')
    parser.add_argument(r'--startime', r'-s', default=0, help=r'cut video, make gif or take snapshot begin time')
    parser.add_argument(r'--lastime', r'-t', default=1, help=r'cut vider or make gif last time')
    parser.add_argument(r'--positionx', r'-x', default=None, help=r'delete logo or add logo position x')
    parser.add_argument(r'--positiony', r'-y', default=None, help=r'delete logo or add logo position y')
    parser.add_argument(r'--dwidth', r'-dw',default=1, help=r'delete logo width')
    parser.add_argument(r'--dheight', r'-dh',default=1, help=r'delete logo height')
    parser.add_argument(r'--ratio', r'-rh', default=0.11, help=r'add loge ratio of video height')
    parser.add_argument(r'--giframe', r'-gf', default=5, help=r'gif frame')
    parser.add_argument(r'--tstime', r'-ts', default=10, help=r'ts fragment time')
    args = parser.parse_args()
    # print(args.input)
    try:
        width = int(args.width)
        height = int(args.height)
        videorate = int(args.videorate)
        startime = float(args.startime)
        lastime = float(args.lastime)
        position_x = int(args.positionx) if args.positionx else None
        position_y = int(args.positiony) if args.positiony else None
        dwidth = int(args.dwidth)
        dheight = int(args.dheight)
        ratio = float(args.ratio)
        giframe = int(args.giframe)
        tstime = int(args.tstime)
        assert lastime >= 1
        assert startime >= 0
        assert ratio > 0 and ratio < 1
        if position_x and position_y:
            assert position_x >= 0 and position_y >= 0
        assert dwidth > 0 and dheight > 0
        assert giframe > 0
        assert tstime > 0
    except ValueError:
        print(r'--width, --height, --videorate should be integral')
        print(r'--startime and --lastime must be a number')
        print(r'--positionx and --positiony must be a integral')
        print(r'--dwidth and --dheight must be a integral')
        print(r'--giframe must be a integral')
        print(r'--tstime must be a integral')
        exit(-1)
    except AssertionError:
        print('start time must >= 0, lastime must >= 1')
        print('position_x must >= 0, img_position_y must >= 0')
        print('dwidth must > 0, dheight must > 0')
        print('ratio must > 0, and must < 1')
        print('gif frame must > 0')
        print('ts fragment time must > 0')
        exit(-1)
    encode_lib = H264EncoderArgs.codec_v_h264_nvenc if args.codeclib == 'g' else H264EncoderArgs.codec_v_libx264
    kwargs = dict()
    kwargs['target_width'] = width
    kwargs['target_height'] = height
    kwargs['target_videobitrate'] = videorate
    kwargs['start_time'] = startime
    kwargs['last_time'] = lastime
    kwargs['encode_lib'] = encode_lib
    kwargs['ratio_img_height'] = ratio
    kwargs['ts_time'] = tstime
    kwargs['ts_prefix'] = str(uuid.uuid1())
    try:
        if args.function == r'm':
            status, stdout, _ = simple_run_cmd(r'which ffmpeg')
            if status != 0:
                print(r'can not find ffmpeg bin in $PATH')
                exit(-1)
            ffmpeg_bin = stdout.replace('\n', '')
            status, stdout, stderr = simple_run_cmd(r'which ffprobe')
            if status != 0:
                print(r'can not find ffprobe bin in $PATH')
                exit(-1)
            ffprobe_bin = stdout.replace('\n', '')
            # 合并TS文件
            _, output = _init_tools(None, args.output)
            print(r'begin concat ts ...')
            result, stderr = H264Video.download_m3u8(ffmpeg_bin, args.input, output)
            if result:
                print(f'concat done, output: {output}')
            else:
                print(f'concat error: {stderr}')
                exit(-1)
        elif args.function == r's':
            # 缩放视频
            h264_obj, output_file = _init_tools(args.input[0][0], args.output)
            print(f'scale video {args.input[0][0]} ...')
            _h264_workflow_base(h264_obj, FfmpegCmdModel.scale_video, 
                                'mp4', output_file=output_file, **kwargs)
            print(f'scale video done, output: {output_file}')
        elif args.function == r'c':
            # 裁减视频
            h264_obj, output_file = _init_tools(args.input[0][0], args.output)
            print(f'cut video {args.input[0][0]} ...')
            _h264_workflow_base(h264_obj, FfmpegCmdModel.cut_video, 'mp4', 
                                output_file=output_file, **kwargs)
            print(f'cut video done, output: {output_file}')
        elif args.function == r't':
            # 拼接视频
            try:
                assert len(args.input) >= 2
            except AssertionError:
                print(f'input file must more than 2')
                exit(-1)
            h264_obj, output_file = _init_tools(args.input[0][0], args.output)
            h264_obj1, _ = _init_tools(args.input[1][0], args.output)
            print(f'concat video {args.input[0][0]} {args.input[1][0]} ...')
            h264out_obj1 = h264_obj + h264_obj1
            status, _, stderr = simple_run_cmd(f'mv -f {h264out_obj1.videofile_path} {output_file}')
            if status != 0:
                print(f'{stderr}')
                exit(-1)
            print(f'concat video done, output: {output_file}')
        elif args.function == r'n':
            startime = int(startime)
            h264_obj, output_file = _init_tools(args.input[0][0], args.output)
            print(f'take snanshot from video {args.input[0][0]} ...')
            _h264_workflow_base(h264_obj, FfmpegCmdModel.snapshot_video, 'jpg', 
                                output_file=output_file, **kwargs)
            print(f'snapshot done, output: {output_file}')
        elif args.function == r'd':
            position_x = 0 if not position_x else position_x
            position_y = 0 if not position_y else position_y
            h264_obj, output_file = _init_tools(args.input[0][0], args.output)
            delog_args = tuple([H264Video.create_delog_args(position_x, position_y, dwidth, dheight,
                                                            int(startime), int(startime + lastime))])
            kwargs['delog_tuple'] = delog_args
            print(f'delete logo from video {args.input[0][0]} ...')
            _h264_workflow_base(h264_obj, FfmpegCmdModel.del_log, 'mp4', 
                                output_file=output_file, **kwargs)
            print(f'delete logo done, output: {output_file}')
        elif args.function == r'a':
            # 添加水印
            try:
                assert len(args.input) >= 2
            except AssertionError:
                print(f'input file must more than 2')
                exit(-1)
            h264_obj, output_file = _init_tools(args.input[0][0], args.output)
            kwargs['input_img'] = os.path.abspath(args.input[1][0])
            print(f'add logo to video {args.input[0][0]} ...')
            if position_x is not None and position_y is not None:
                kwargs['img_position_x'] = position_x
                kwargs['img_position_y'] = position_y
                _h264_workflow_base(h264_obj, FfmpegCmdModel.logo_video_fix, 'mp4', 
                                    output_file=output_file, **kwargs)
            else:
                _h264_workflow_base(h264_obj, FfmpegCmdModel.logo_video_move, 'mp4', 
                                    output_file=output_file, **kwargs)
            print(f'add logo done, output: {output_file}')
        elif args.function == r'g':
            # 生成gif
            h264_obj, output_file = _init_tools(args.input[0][0], args.output)
            kwargs['v_frame'] = giframe
            print(f'make gif from video {args.input[0][0]} ...')
            _h264_workflow_base(h264_obj, FfmpegCmdModel.create_gif, 'gif', 
                                output_file=output_file, **kwargs)
            print(f'make gif done, output: {output_file}')
        elif args.function == r'h':
            # ts切片
            h264_obj, output_file = _init_tools(args.input[0][0], args.output)
            if not os.path.isdir(output_file):
                print(f'{output_file} must be a dir')
                exit(-1)
            print(f'make ts from video {args.input[0][0]} ...')
            m3u8_out = _h264_workflow_base(h264_obj, FfmpegCmdModel.hls_video, 'm3u8', 
                                           dest_dir=output_file, **kwargs)
            print(f'make ts done, output : {m3u8_out}')
    except KeyboardInterrupt:
        simple_run_cmd(f'rm -rf {args.output}')
        print(r'use interrupt proccess')
        exit(1)
    exit(0)

