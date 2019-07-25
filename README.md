模块安装
===

*尝试添加QSV很痛苦*

进入代码目录执行
```bash
python setup.py sdist
python setup.py install
```

**如果需要测试本类,请安装pytest,pytest-aysncio**

应用举例
===

## 初始化
```python
from aioffmpeg.h264video import H264Video
from aioffmpeg.cmd_opts import H264EncoderArgs, FfmpegCmdModel

h264_obj = H264Video(video_file, output_dir, ffmpeg_bin, 
                     ffprobe_bin, aio=True, auto_clear=False)
```
如果初始化使用 aio=True,则可以使用异步函数<br>
如果初始化使用 auto_clear=True,则对象析构时会自动删除视频源文件

## 缩放视频
```python
# 异步
scaled_obj, stderr = await h264_obj.cmd_do_aio(f'{home_dir:}', 'mp4', FfmpegCmdModel.scale_video,
                                               target_width=random.randint(700, 1000),
                                               target_height=random.randint(300, 1000),
                                               target_videobitrate=random.randint(100, 400),
                                               encode_lib=H264EncoderArgs.codec_v_libx264)
# 非异步
scaled_obj, stderr = h264_obj.cmd_do(f'{home_dir:}', 'mp4', FfmpegCmdModel.scale_video,
                                     target_width=random.randint(700, 1000),
                                     target_height=random.randint(300, 1000),
                                     target_videobitrate=random.randint(100, 400),
                                     encode_lib=H264EncoderArgs.codec_v_libx264)
```
成功返回一个新的 H264Video实例,和一个空字符串<br>
失败返回 None, stderr

## 旋转视频(左旋,右旋)
```python
# 异步
scaled_obj, stderr = await h264_obj.cmd_do_aio(f'{home_dir:}', 'mp4', FfmpegCmdModel.rotate_video,
                                               rotate_direct=rotate_direct,
                                               target_videobitrate=random.randint(100, 400),
                                               encode_lib=H264EncoderArgs.codec_v_libx264)
# 非异步
scaled_obj, stderr = h264_obj.cmd_do(f'{home_dir:}', 'mp4', FfmpegCmdModel.rotate_video,
                                     rotate_direct=rotate_direct,
                                     target_videobitrate=random.randint(100, 400),
                                     encode_lib=H264EncoderArgs.codec_v_libx264)                                                   
```
成功返回一个新的 H264Video实例,和一个空字符串<br>
失败返回 None, stderr

## 视频hls切片
```python
# 异步
m3u8path, stderr = await h264_obj.cmd_do_aio(f'{home_dir:s}', 'm3u8', FfmpegCmdModel.hls_video,
                                             target_videobitrate=video_bitrate,
                                             encode_lib=H264EncoderArgs.codec_v_libx264,
                                             ts_time=ts_time,
                                             ts_prefix='test-ts')
# 非异步
m3u8path, stderr = h264_obj.cmd_do(f'{home_dir:s}', 'm3u8', FfmpegCmdModel.hls_video,
                                   target_videobitrate=video_bitrate,
                                   encode_lib=H264EncoderArgs.codec_v_libx264,
                                   ts_time=ts_time,
                                   ts_prefix='test-ts')
```
成功返回一个新的 m3u8文件的路径,和一个空字符串<br>
失败返回 None, stderr

## 视频裁剪
```python
# 异步
cuted_video, stderr = await h264_obj.cmd_do_aio(f'{home_dir:s}', 'mp4', FfmpegCmdModel.cut_video,
                                                start_time=start_time,
                                                last_time=last_time,
                                                encode_lib=H264EncoderArgs.codec_v_libx264,
                                                target_videobitrate=500)
# 非异步                                              
cuted_video, stderr = h264_obj.cmd_do(f'{home_dir:s}', 'mp4', FfmpegCmdModel.cut_video,
                                      start_time=start_time,
                                      last_time=last_time,
                                      encode_lib=H264EncoderArgs.codec_v_libx264,
                                      target_videobitrate=500)
# 仅支持非异步,从0秒到20,均匀截取10个1秒的视频
new_obj_list = h264_obj[0:20:10]
# 仅支持非异步,截取一个从1面开始的一个1秒的视频
new_obj = h246_obj[2]                                
```
成功返回一个新的 H264Video实例,和一个空字符串<br>
失败返回 None, stderr
slice返回一个 H264Video实例列表

## 视频截图
```python
# 异步
jpgpath, stderr = await h264_obj.cmd_do_aio(f'{home_dir:s}', 'jpg', FfmpegCmdModel.snapshot_video,
                                                start_time=start_time,
                                                target_height=target_height)
# 非异步
jpgpath, stderr = h264_obj.cmd_do(f'{home_dir:s}', 'jpg', FfmpegCmdModel.snapshot_video,
                                  start_time=start_time,
                                  target_height=target_height)
# 仅支持非异步,从0秒到20,均匀截取10张图,默认高度240,返回图片路径列表
jpgpath_list = h264_obj[0:20:-10]
```
成功返回一个 jpg 文件的路径,和一个空字符串<br>
失败返回 None, stderr

## 视频拼接
```python
# 异步
concat_video, stderr = await h264_obj.cmd_do_aio(f'{home_dir:s}', 'mp4', FfmpegCmdModel.concat_video,
                                                 input_obj=h264_obj1,
                                                 encode_lib=H264EncoderArgs.codec_v_libx264)
# 非异步                                            
concat_video, stderr = h264_obj.cmd_do(f'{home_dir:s}', 'mp4', FfmpegCmdModel.concat_video,
                                       input_obj=h264_obj1,
                                       encode_lib=H264EncoderArgs.codec_v_libx264)
# 仅限非异步
h264_obj_new = h264_obj + h264_obj1
```
成功返回一个新的 H264Video实例,和一个空字符串<br>
失败返回 None, stderr

## 视频水印
```python
# 异步
## 固定水印
fix_video_logo, stderr = await h264_obj.cmd_do_aio(f'{home_dir:s}', 'mp4', FfmpegCmdModel.logo_video_fix,
                                                   input_img=constval.LOGO,
                                                   ratio_img_height=ratio_img_height,
                                                   img_position_x=img_position_x,
                                                   img_position_y=img_position_y,
                                                   encode_lib=H264EncoderArgs.codec_v_libx264)
## 移动水印
move_video_logo, stderr = await h264_obj.cmd_do_aio(f'{home_dir:s}', 'mp4', FfmpegCmdModel.logo_video_move,
                                                    input_img=constval.LOGO,
                                                    ratio_img_height=ratio_img_height,
                                                    encode_lib=H264EncoderArgs.codec_v_libx264)
# 非异步
## 固定水印
fix_video_logo, stderr = h264_obj.cmd_do(f'{home_dir:s}', 'mp4', FfmpegCmdModel.logo_video_fix,
                                         input_img=constval.LOGO,
                                         ratio_img_height=ratio_img_height,
                                         img_position_x=img_position_x,
                                         img_position_y=img_position_y,
                                         encode_lib=H264EncoderArgs.codec_v_libx264)
## 移动水印
move_video_logo, stderr = h264_obj.cmd_do(f'{home_dir:s}', 'mp4', FfmpegCmdModel.logo_video_move,
                                          input_img=constval.LOGO,
                                          ratio_img_height=ratio_img_height,
                                          encode_lib=H264EncoderArgs.codec_v_libx264)
```
成功返回一个新的 H264Video实例,和一个空字符串<br>
失败返回 None, stderr

## 去除水印
```python
# 构造参数
delog_args = tuple([    # delog_args_str = 'pos_x pos_y width height begin_time end_time'
                        H264Video.create_delog_args(random.randint(0, 600),  
                                                    random.randint(0, 1000),
                                                    random.randint(0, 300),
                                                    random.randint(0, 300),
                                                    random.randint(0, 100),
                                                    random.randint(100, 200))
                    for i in range(10)])

# 异步
delog_obj, stderr = await h264_obj.cmd_do_aio(f'{home_dir:}', 'mp4', FfmpegCmdModel.del_log,
                                              delog_tuple=delog_args,
                                              encode_lib=H264EncoderArgs.codec_v_libx264)
# 非异步
delog_obj, stderr = h264_obj.cmd_do(f'{home_dir:}', 'mp4', FfmpegCmdModel.del_log,
                                    delog_tuple=delog_args,
                                    encode_lib=H264EncoderArgs.codec_v_libx264)
```
成功返回一个新的 H264Video实例,和一个空字符串<br>
失败返回 None, stderr

## 生成gif
```python
# 异步
gifpath, stderr = await h264_obj.cmd_do_aio(f'{home_dir:s}', 'gif', FfmpegCmdModel.create_gif,
                                            start_time=start_time,
                                            last_time=last_time,
                                            v_frame=5,
                                            target_height=target_height)
# 非异步
gifpath, stderr = h264_obj.cmd_do(f'{home_dir:s}', 'gif', FfmpegCmdModel.create_gif,
                                  start_time=start_time,
                                  last_time=last_time,
                                  v_frame=5,
                                  target_height=target_height)
```
成功返回一个 gif文件的路径,和一个空字符串<br>
失败返回 None, stderr

命令行工具
===

```
$ aioffpmeg -h
usage: aioffpmeg [-h] --function {m,s,c,t,n,d,a,g,h} --input INPUT [INPUT ...]
                 --output OUTPUT [--width WIDTH] [--height HEIGHT]
                 [--videorate VIDEORATE] [--codeclib {g,c}]
                 [--startime STARTIME] [--lastime LASTIME]
                 [--positionx POSITIONX] [--positiony POSITIONY]
                 [--dwidth DWIDTH] [--dheight DHEIGHT] [--ratio RATIO]
                 [--giframe GIFRAME] [--tstime TSTIME]

aioffmpeg command line tools

optional arguments:
  -h, --help            show this help message and exit
  --function {m,s,c,t,n,d,a,g,h}, -f {m,s,c,t,n,d,a,g,h}
                        this tool's functions, m: concat ts from m3u8 file, s:
                        scale video, c: cut video, t: concat video, n: take a
                        snapshot from video, d: delete video logo, a: add logo
                        to video, g: make a gif from video, h: make hls ts
                        from video
  --input INPUT [INPUT ...], -i INPUT [INPUT ...]
                        input m3u8 file(local or url), or input video
  --output OUTPUT, -o OUTPUT
                        output file(jpg,gif,mp4,m3u8)
  --width WIDTH, -w WIDTH
                        video width, default using source video's width
  --height HEIGHT, -e HEIGHT
                        video(image) height, default using source video's
                        height,image only has height
  --videorate VIDEORATE, -r VIDEORATE
                        video rate, default using source video's video rate
  --codeclib {g,c}, -l {g,c}
                        video codec lib, g: gpu codec, c: cpu codec
  --startime STARTIME, -s STARTIME
                        cut video, make gif or take snapshot begin time
  --lastime LASTIME, -t LASTIME
                        cut vider or make gif last time
  --positionx POSITIONX, -x POSITIONX
                        delete logo or add logo position x
  --positiony POSITIONY, -y POSITIONY
                        delete logo or add logo position y
  --dwidth DWIDTH, -dw DWIDTH
                        delete logo width
  --dheight DHEIGHT, -dh DHEIGHT
                        delete logo height
  --ratio RATIO, -rh RATIO
                        add loge ratio of video height
  --giframe GIFRAME, -gf GIFRAME
                        gif frame
  --tstime TSTIME, -ts TSTIME
                        ts fragment time

```

其他文档
===
- [centos7安装ffmpeg](./docs/centos7x64_ffmpeg_install.md)
- [ubuntu安装ffmpeg](./docs/ubuntu18.04x64_ffmpeg_install.md)
