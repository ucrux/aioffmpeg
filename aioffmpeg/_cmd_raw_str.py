"""
此文件保存 aioffmpeg 使用的一些命令
供 aioffmpeg 类引用

aioffmpeg 需要支持 h264_nvenc 和 libx264 两个 encoder
但是在实际使用中,发现 使用 libx264 encoder 会让视频文件莫名其妙变大
"""
# 查看ffmpeg是否有外部编码库 h264_nvenc libx264
CMD_CHECK_H264 = r"'{ffmpeg_bin:s}' -hide_banner -encoders |grep -v libx264rgb| grep -E 'libx264|h264_nvenc'"

# 获取视频属性,在stdout中输出视频信息的属性
CMD_GET_VIDEO_PROBE = r"'{ffprobe_bin:s}' -v quiet -print_format json -show_format -show_streams '{input_file:s}'"


# 修改视频元数据
OPTS_MATEDATA = r"-metadata:s:v '{mate_k:s}'='{mate_v:s}' "
CMD_CH_VIDEO_METADATA = r"'{ffmpeg_bin:s}' -hide_banner -y -i '{input_file:s}' " \
                        r"{metadata_str:s} " \
                        r"-c copy '{output_file:s}'"

# 视频
"""
命令输出如下:
{
    "streams": [
        {
            "index": 0,
            "codec_name": "h264",
            "codec_long_name": "H.264 / AVC / MPEG-4 AVC / MPEG-4 part 10",
            "profile": "High",
            "codec_type": "video",
            "codec_time_base": "1/60",
            "codec_tag_string": "avc1",
            "codec_tag": "0x31637661",
            "width": 1920,
            "height": 1080,
            "coded_width": 1920,
            "coded_height": 1088,
            "has_b_frames": 2,
            "sample_aspect_ratio": "1:1",
            "display_aspect_ratio": "16:9",
            "pix_fmt": "yuv420p",
            "level": 40,
            "color_range": "tv",
            "color_space": "bt709",
            "color_transfer": "bt709",
            "chroma_location": "left",
            "refs": 1,
            "is_avc": "true",
            "nal_length_size": "4",
            "r_frame_rate": "30/1",
            "avg_frame_rate": "30/1",
            "time_base": "1/15360",
            "start_pts": 0,
            "start_time": "0.000000",
            "duration_ts": 185344,
            "duration": "12.066667",
            "bit_rate": "3891167",
            "bits_per_raw_sample": "8",
            "nb_frames": "362",
            "disposition": {
                "default": 1,
                "dub": 0,
                "original": 0,
                "comment": 0,
                "lyrics": 0,
                "karaoke": 0,
                "forced": 0,
                "hearing_impaired": 0,
                "visual_impaired": 0,
                "clean_effects": 0,
                "attached_pic": 0,
                "timed_thumbnails": 0
            },
            "tags": {
                "language": "und",
                "handler_name": "VideoHandler"
            }
        },
        {
            "index": 1,
            "codec_name": "aac",
            "codec_long_name": "AAC (Advanced Audio Coding)",
            "profile": "LC",
            "codec_type": "audio",
            "codec_time_base": "1/44100",
            "codec_tag_string": "mp4a",
            "codec_tag": "0x6134706d",
            "sample_fmt": "fltp",
            "sample_rate": "44100",
            "channels": 2,
            "channel_layout": "stereo",
            "bits_per_sample": 0,
            "r_frame_rate": "0/0",
            "avg_frame_rate": "0/0",
            "time_base": "1/44100",
            "start_pts": 0,
            "start_time": "0.000000",
            "duration_ts": 532463,
            "duration": "12.073991",
            "bit_rate": "101232",
            "max_bit_rate": "128000",
            "nb_frames": "521",
            "disposition": {
                "default": 1,
                "dub": 0,
                "original": 0,
                "comment": 0,
                "lyrics": 0,
                "karaoke": 0,
                "forced": 0,
                "hearing_impaired": 0,
                "visual_impaired": 0,
                "clean_effects": 0,
                "attached_pic": 0,
                "timed_thumbnails": 0
            },
            "tags": {
                "language": "und",
                "handler_name": "SoundHandler"
            }
        }
    ],
    "format": {
        "filename": "1@MIMK-059@006@001.mp4",
        "nb_streams": 2,
        "nb_programs": 0,
        "format_name": "mov,mp4,m4a,3gp,3g2,mj2",
        "format_long_name": "QuickTime / MOV",
        "start_time": "0.000000",
        "duration": "12.098000",
        "size": "6036532",
        "bit_rate": "3991755",
        "probe_score": 100,
        "tags": {
            "major_brand": "isom",
            "minor_version": "512",
            "compatible_brands": "isomiso2avc1mp41",
            "encoder": "Lavf57.84.100"
        }
    }
}
"""

# 图片
"""
{
    "streams": [
        {
            "index": 0,
            "codec_name": "png",
            "codec_long_name": "PNG (Portable Network Graphics) image",
            "codec_type": "video",
            "codec_time_base": "0/1",
            "codec_tag_string": "[0][0][0][0]",
            "codec_tag": "0x0000",
            "width": 135,
            "height": 240,
            "coded_width": 135,
            "coded_height": 240,
            "has_b_frames": 0,
            "sample_aspect_ratio": "1:1",
            "display_aspect_ratio": "9:16",
            "pix_fmt": "rgb24",
            "level": -99,
            "color_range": "pc",
            "refs": 1,
            "r_frame_rate": "25/1",
            "avg_frame_rate": "0/0",
            "time_base": "1/25",
            "disposition": {
                "default": 0,
                "dub": 0,
                "original": 0,
                "comment": 0,
                "lyrics": 0,
                "karaoke": 0,
                "forced": 0,
                "hearing_impaired": 0,
                "visual_impaired": 0,
                "clean_effects": 0,
                "attached_pic": 0,
                "timed_thumbnails": 0
            }
        }
    ],
    "format": {
        "filename": "cherryheadlalalala1559748161.1761171559748548.4088461.png",
        "nb_streams": 1,
        "nb_programs": 0,
        "format_name": "png_pipe",
        "format_long_name": "piped png sequence",
        "size": "68042",
        "probe_score": 99
    }
}
"""

# 视频缩放命令,如果原视频比例与被缩放的比例不匹配,则使用黑边填充,并做初步转码(转成mp4格式)
# 音频只使用 aac 编码
# 缩放后的大小调用者给出, pad_optons由调用者判断给出
# 左右填充的参数
OPTS_PAD_LR = r",pad={target_width:d}:{target_height:d}:({target_width:d}-iw)/2:0:black"
# 上下填充的参数
OPTS_PAD_UD = r",pad={target_width:d}:{target_height:d}:0:({target_height:d}-ih)/2:black"
# ASS字幕参数
OPTS_ASS = r",ass='{ass_file:s}'"
# 缩放填充添加ASS字幕命令
CMD_SCALE_VIDEO_CODECS = r"'{ffmpeg_bin:s}' -hide_banner -y -i '{input_file:s}' -threads 0 " \
                         r"-c:v {encode_lib:s} -pass 1 -an -f mp4 -movflags +faststart -passlogfile {prefix:s} " \
                         r'-vf "format=yuv420p,scale={target_width:d}:{target_height:d}{pad_options:s}{ass_options:s}" ' \
                         r"-r {frame:d}  -preset {preset_type:s} -crf {crf_num:d} -profile:v {profile_type:s} " \
                         r"-level {level:s} -g {frame:d} -b:v {video_rate:d}k /dev/null && " \
                         r"'{ffmpeg_bin:s}' -hide_banner -y -i '{input_file:s}' -threads 0 " \
                         r"-c:v {encode_lib:s}  -c:a aac -b:a {audio_rate:d}k -pass 2 " \
                         r"-f mp4 -movflags +faststart -passlogfile {prefix:s} " \
                         r'-vf "format=yuv420p,scale={target_width:d}:{target_height:d}{pad_options:s}{ass_options:s}" ' \
                         r"-r {frame:d} -preset {preset_type:s} -crf {crf_num:d} -profile:v {profile_type:s} " \
                         r"-level {level:s} -g {frame:d} -b:v {video_rate:d}k '{output_file:s}'"
# 视频旋转命令,支持视频的左旋和右旋
CMD_ROTATE_VIDEO = r"'{ffmpeg_bin:s}' -hide_banner -y -i '{input_file:s}' -threads 0 " \
                   r"-c:v {encode_lib:s} -pass 1 -an -f mp4 -movflags +faststart -passlogfile {prefix:s} " \
                   r"-vf 'format=yuv420p,transpose={rotate_direct:d}' -g {frame:d} " \
                   r"-r {frame:d} -preset {preset_type:s} -crf {crf_num:d} -profile:v {profile_type:s} " \
                   r"-level {level:s} -b:v {video_rate:d}k /dev/null && " \
                   r"'{ffmpeg_bin:s}' -hide_banner -y -i '{input_file:s}' -threads 0 " \
                   r"-c:v {encode_lib:s} -c:a aac -b:a {audio_rate:d}k -pass 2 -f mp4 " \
                   r"-movflags +faststart -passlogfile {prefix:s} " \
                   r"-vf 'format=yuv420p,transpose={rotate_direct:d}' -g {frame:d} " \
                   r"-r {frame:d} -preset {preset_type:s} -crf {crf_num:d} -profile:v {profile_type:s} " \
                   r"-level {level:s} -b:v {video_rate:d}k '{output_file:s}'"
# HLS 切片参数
OPTS_HLS_ENC_KEY_URL = r'-hls_enc_key_url'
# HLS 切片命令
CMD_HLS_VIDEO = r"'{ffmpeg_bin:s}' -hide_banner -y -i '{input_file:s}' -threads 0 " \
                r"-c:v {encode_lib:s} -pass 1 -an -f hls -movflags +faststart -passlogfile {prefix:s} " \
                r"-vf 'format=yuv420p,scale=-2:{target_height:d}' -g {frame:d} " \
                r"-r {frame:d} -preset {preset_type:s} -crf {crf_num:d} -profile:v {profile_type:s} " \
                r"-level {level:s} -b:v {video_rate:d}k " \
                r"-hls_init_time {ts_time:d} -hls_time {ts_time:d} -hls_list_size 0 -hls_enc {enc:d} " \
                r"-hls_enc_key {enc_key:s} -hls_enc_iv {enc_iv:s} {hls_enc_key_url} " \
                r"-hls_flags independent_segments{fix_ts_time}+" \
                r"second_level_segment_size+second_level_segment_index+second_level_segment_duration " \
                r"-strftime 1 " \
                r'-hls_segment_filename "{prefix:s}-%%013t-%%08s-%%010d.ts" ' \
                r"/dev/null && " \
                r"'{ffmpeg_bin:s}' -hide_banner -y -i '{input_file:s}' -threads 0 " \
                r"-c:v {encode_lib:s} -c:a aac -b:a {audio_rate:d}k -pass 2 " \
                r"-f hls -movflags +faststart -passlogfile {prefix:s} " \
                r"-vf 'format=yuv420p,scale=-2:{target_height:d}' -g {frame:d} " \
                r"-r {frame:d} -preset {preset_type:s} -crf {crf_num:d} -profile:v {profile_type:s} " \
                r"-level {level:s} -b:v {video_rate:d}k " \
                r"-hls_init_time {ts_time:d} -hls_time {ts_time:d} -hls_list_size 0 -hls_enc {enc:d} " \
                r"-hls_enc_key {enc_key:s} -hls_enc_iv {enc_iv:s} {hls_enc_key_url} " \
                r"-hls_flags independent_segments{fix_ts_time}+" \
                r"second_level_segment_size+second_level_segment_index+second_level_segment_duration " \
                r"-strftime 1 " \
                r'-hls_segment_filename "{output_dir}/{ts_prefix:s}-%%013t-%%08s-%%010d.ts" ' \
                r"'{output_file:s}'"
# HLS 切片命令 另外一种
CMD_HLS_VIDEO_OTHER = r"'{ffmpeg_bin:s}' -hide_banner -y -i '{input_file:s}' -threads 0 " \
                      r"-c:v {encode_lib:s} -pass 1 -an -f hls -movflags +faststart -passlogfile {prefix:s} " \
                      r"-vf 'format=yuv420p,scale=-2:{target_height:d}' -g {frame:d} " \
                      r"-r {frame:d} -preset {preset_type:s} -crf {crf_num:d} -profile:v {profile_type:s} " \
                      r"-level {level:s} -b:v {video_rate:d}k " \
                      r"-hls_init_time {ts_time:d} -hls_time {ts_time:d} -hls_list_size 0 -hls_enc {enc:d} " \
                      r"-hls_enc_key {enc_key:s} -hls_enc_iv {enc_iv:s} {hls_enc_key_url} " \
                      r"-use_localtime 1 -hls_flags " \
                      r"second_level_segment_size+second_level_segment_index+second_level_segment_duration{fix_ts_time} " \
                      r"-strftime 1 " \
                      r'-hls_segment_filename "{prefix:s}-%%013t-%%08s-%%010d.ts" ' \
                      r"{prefix:s}.m3u8 && " \
                      r"'{ffmpeg_bin:s}' -hide_banner -y -i '{input_file:s}' -threads 0 " \
                      r"-c:v {encode_lib:s} -c:a aac -b:a {audio_rate:d}k -pass 2 " \
                      r"-f hls -movflags +faststart -passlogfile {prefix:s} " \
                      r"-vf 'format=yuv420p,scale=-2:{target_height:d}' -g {frame:d} " \
                      r"-r {frame:d} -preset {preset_type:s} -crf {crf_num:d} -profile:v {profile_type:s} " \
                      r"-level {level:s} -b:v {video_rate:d}k " \
                      r"-hls_init_time {ts_time:d} -hls_time {ts_time:d} -hls_list_size 0 -hls_enc {enc:d} " \
                      r"-hls_enc_key {enc_key:s} -hls_enc_iv {enc_iv:s} {hls_enc_key_url} " \
                      r"-use_localtime 1 -hls_flags " \
                      r"second_level_segment_size+second_level_segment_index+second_level_segment_duration{fix_ts_time} " \
                      r"-strftime 1 " \
                      r'-hls_segment_filename "{output_dir}/{ts_prefix:s}-%%013t-%%08s-%%010d.ts" ' \
                      r"'{output_file:s}'"
# 截图命令,截取以帧做为图片
CMD_SNAPSHOT = r"'{ffmpeg_bin:s}' -ss {start_time:f} -i '{input_file:s}' -passlogfile {prefix:s} -threads 0 " \
               r"-vf 'scale=-2:{target_height:d}' -y -f image2 " \
               r"-vframes 1 '{output_file:s}'"

# 视频裁剪命令
CMD_CUT_VIDEO = r"'{ffmpeg_bin:s}' -hide_banner -y -ss {start_time:f} -t '{last_time:f}' " \
                r"-i '{input_file:s}' -threads 0 " \
                r"-c:v {encode_lib:s} -pass 1 -an -f mp4 -movflags +faststart -passlogfile {prefix:s} " \
                r"-vf 'format=yuv420p,scale=-2:{target_height:d}' -g {frame:d} " \
                r"-r {frame:d} -preset {preset_type:s} -crf {crf_num:d} -profile:v {profile_type:s} " \
                r"-level {level:s} -b:v {video_rate:d}k " \
                r"/dev/null && " \
                r"'{ffmpeg_bin:s}' -hide_banner -y -ss {start_time:f} -t '{last_time:f}' " \
                r"-i '{input_file:s}' -threads 0 " \
                r"-c:v {encode_lib:s} -c:a aac -b:a {audio_rate:d}k -pass 2 " \
                r"-f mp4 -movflags +faststart -passlogfile {prefix:s} " \
                r"-vf 'format=yuv420p,scale=-2:{target_height:d}' -g {frame:d} " \
                r"-r {frame:d} -preset {preset_type:s} -crf {crf_num:d} -profile:v {profile_type:s} " \
                r"-level {level:s} -b:v {video_rate:d}k " \
                r"'{output_file:s}'"

# 视频拼接命令
# 有gpu转码的时候首选CMD_CONCAT_VIDEO命令,如果CMD_CONCAT_VIDEO失败则使用CMD_CONCAT_VIDEO_SAFE
# 没有gpu转码的时候选用CMD_CONCAT_VIDEO_SAFE
# CMD_CONCAT_VIDEO 能保证音轨同步, CMD_CONCAT_VIDEO_SAFE 拼接速度快
CMD_CONCAT_VIDEO = r"'{ffmpeg_bin:s}' -hide_banner -y -i '{input_file1:s}' -i '{input_file2:s}' " \
                   r"-threads 0 -c:v {encode_lib:s} -pass 1 -an -f mp4 -movflags +faststart -passlogfile {prefix:s} " \
                   r"-filter_complex '[0:0] [0:1] [1:0] [1:1] concat=n=2:v=1:a=1 [v] [a]' -map '[v]' -map '[a]' " \
                   r" -g {frame:d} -r {frame:d} -preset {preset_type:s} -crf {crf_num:d} -profile:v {profile_type:s} " \
                   r"-level {level:s} -b:v {video_rate:d}k /dev/null && " \
                   r"'{ffmpeg_bin:s}' -hide_banner -y -i '{input_file1:s}' -i '{input_file2:s}' " \
                   r"-threads 0 -c:v {encode_lib:s} -c:a aac -b:a {audio_rate:d}k -pass 2 -f mp4 " \
                   r"-movflags +faststart -passlogfile {prefix:s} " \
                   r"-filter_complex '[0:0] [0:1] [1:0] [1:1] concat=n=2:v=1:a=1 [v] [a]' -map '[v]' -map '[a]' " \
                   r"-g {frame:d} -r {frame:d} -preset {preset_type:s} -crf {crf_num:d} -profile:v {profile_type:s} " \
                   r"-level {level:s} -b:v {video_rate:d}k '{output_file:s}'"

CMD_CONCAT_VIDEO_SAFE = r"'{ffmpeg_bin:s}' -f concat -safe 0 -i '{concat_file:s}' -c copy '{output_file:s}'"
# 水印命令
# 固定水印
CMD_LOGO_FIX = r"'{ffmpeg_bin:s}' -hide_banner -y -i '{input_file:s}' -i '{input_img:s}' " \
               r"-threads 0 -c:v {encode_lib:s} -pass 1 -an -f mp4 -movflags +faststart -passlogfile {prefix:s} " \
               r'-filter_complex "[1:v]scale=-2:{img_height:d}[ovrl],[0:v][ovrl]overlay={X:d}:{Y:d}" ' \
               r"-g {frame:d} -r {frame:d} -preset {preset_type:s} -crf {crf_num:d} -profile:v {profile_type:s} " \
               r"-level {level:s} -b:v {video_rate:d}k /dev/null && " \
               r"'{ffmpeg_bin:s}' -hide_banner -y -i '{input_file:s}' -i '{input_img:s}' " \
               r"-threads 0 -c:v {encode_lib:s} -c:a aac -b:a {audio_rate:d}k -pass 2 -f mp4 " \
               r"-movflags +faststart -passlogfile {prefix:s} " \
               r'-filter_complex "[1:v]scale=-2:{img_height:d}[ovrl],[0:v][ovrl]overlay={X:d}:{Y:d}" ' \
               r"-g {frame:d} -r {frame:d} -preset {preset_type:s} -crf {crf_num:d} -profile:v {profile_type:s} " \
               r"-level {level:s} -b:v {video_rate:d}k '{output_file:s}'"
# 移动水印
CMD_LOGO_MOVE = r"'{ffmpeg_bin:s}' -hide_banner -y -i '{input_file:s}' -i '{input_img:s}' " \
                r"-i '{input_img:s}' -i '{input_img:s}' -i '{input_img:s}' -i '{input_img:s}' -i '{input_img:s}' "\
                r"-threads 0 -c:v {encode_lib:s} -pass 1 -an -f mp4 -movflags +faststart -passlogfile {prefix:s} " \
                r'-filter_complex "[1]scale=-2:{img_height:d}[img1];'\
                r"[0][img1]overlay=x='if(between(mod(t,{TT:d}),0,{ST:d}),{LX:d},NAN)':y={LY:d}[ovrl1]," \
                r"[2]scale=-2:{img_height:d}[img2];"\
                r"[ovrl1][img2]overlay=x='if(between(mod(t,{TT:d}),{ST:d},{ST:d}+2)," \
                r"{LX:d}+(({MX:d}-{LX:d})/2)*(mod(t,{TT:d})-{ST:d}),NAN)':" \
                r"y='{LY:d}+(({MY:d}-{LY:d})/2)*(mod(t,{TT:d})-{ST:d})'[ovrl2]," \
                r"[3]scale=-2:{img_height:d}[img3];"\
                r"[ovrl2][img3]overlay=x='if(between(mod(t,{TT:d}),{ST:d}+2,{ST:d}*2+2),{MX:d},NAN)':"\
                r"y={MY:d}[ovrl3],[4]scale=-2:{img_height:d}[img4];"\
                r"[ovrl3][img4]overlay=x='if(between(mod(t,{TT:d}),{ST:d}*2+2,{ST:d}*2+4)," \
                r"{MX:d}+(({RX:d}-{MX:d})/2)*(mod(t,{TT:d})-(({ST:d}*2)+2)),NAN)':" \
                r"y='{MY:d}-(({MY:d}-{LY:d})/2)*(mod(t,{TT:d})-(({ST:d}*2)+2))'[ovrl4]," \
                r"[5]scale=-2:{img_height:d}[img5];"\
                r"[ovrl4][img5]overlay=x='if(between(mod(t,{TT:d}),{ST:d}*2+4,{ST:d}*3+4),{RX:d},NAN)':"\
                r"y={LY:d}[ovrl5],[6]scale=-2:{img_height:d}[img6];"\
                r"[ovrl5][img6]overlay=x='if(between(mod(t,{TT:d}),{ST:d}*3+4,{ST:d}*3+6)," \
                r"{RX:d}-(({RX:d}-{LX:d})/2)*(mod(t,{TT:d})-(({ST:d}*3)+4)),NAN)':" \
                r'y={LY:d}" -g {frame:d} -r {frame:d} -preset {preset_type:s} -crf {crf_num:d} ' \
                r"-profile:v {profile_type:s} -level {level:s} -b:v {video_rate:d}k /dev/null && " \
                r"'{ffmpeg_bin:s}' -hide_banner -y -i '{input_file:s}' -i '{input_img:s}' " \
                r"-i '{input_img:s}' -i '{input_img:s}' -i '{input_img:s}' -i '{input_img:s}' -i '{input_img:s}' "\
                r"-threads 0 -c:v {encode_lib:s} -c:a aac -b:a {audio_rate:d}k -pass 2 -f mp4 "\
                r'-movflags +faststart -passlogfile {prefix:s} -filter_complex "[1]scale=-2:{img_height:d}[img1];'\
                r"[0][img1]overlay=x='if(between(mod(t,{TT:d}),0,{ST:d}),{LX:d},NAN)':y={LY:d}[ovrl1]," \
                r"[2]scale=-2:{img_height:d}[img2];"\
                r"[ovrl1][img2]overlay=x='if(between(mod(t,{TT:d}),{ST:d},{ST:d}+2)," \
                r"{LX:d}+(({MX:d}-{LX:d})/2)*(mod(t,{TT:d})-{ST:d}),NAN)':" \
                r"y='{LY:d}+(({MY:d}-{LY:d})/2)*(mod(t,{TT:d})-{ST:d})'[ovrl2]," \
                r"[3]scale=-2:{img_height:d}[img3];"\
                r"[ovrl2][img3]overlay=x='if(between(mod(t,{TT:d}),{ST:d}+2,{ST:d}*2+2),{MX:d},NAN)':"\
                r"y={MY:d}[ovrl3],[4]scale=-2:{img_height:d}[img4];"\
                r"[ovrl3][img4]overlay=x='if(between(mod(t,{TT:d}),{ST:d}*2+2,{ST:d}*2+4)," \
                r"{MX:d}+(({RX:d}-{MX:d})/2)*(mod(t,{TT:d})-(({ST:d}*2)+2)),NAN)':" \
                r"y='{MY:d}-(({MY:d}-{LY:d})/2)*(mod(t,{TT:d})-(({ST:d}*2)+2))'[ovrl4]," \
                r"[5]scale=-2:{img_height:d}[img5];"\
                r"[ovrl4][img5]overlay=x='if(between(mod(t,{TT:d}),{ST:d}*2+4,{ST:d}*3+4),{RX:d},NAN)':"\
                r"y={LY:d}[ovrl5],[6]scale=-2:{img_height:d}[img6];"\
                r"[ovrl5][img6]overlay=x='if(between(mod(t,{TT:d}),{ST:d}*3+4,{ST:d}*3+6)," \
                r"{RX:d}-(({RX:d}-{LX:d})/2)*(mod(t,{TT:d})-(({ST:d}*3)+4)),NAN)':" \
                r'y={LY:d}" -g {frame:d} -r {frame:d} -preset {preset_type:s} -crf {crf_num:d} ' \
                r"-profile:v {profile_type:s} -level {level:s} -b:v {video_rate:d}k '{output_file:s}'"
# 去除水印
# 去除水印选项
OPTS_DEL_LOGO = r"delogo=x={X:d}:y={Y:d}:w={width:d}:h={height:d}:enable='between(t,{begin_time:d},{end_time:d})'"
# 去除水印命令
CMD_DEL_LOGO = r"'{ffmpeg_bin:s}' -hide_banner -y -i '{input_file:s}' -threads 0 " \
               r"-c:v {encode_lib:s} -pass 1 -an -f mp4 -movflags +faststart -passlogfile {prefix:s} " \
               r'-vf "format=yuv420p{opts_del_log:s}" ' \
               r"-r {frame:d}  -preset {preset_type:s} -crf {crf_num:d} -profile:v {profile_type:s} " \
               r"-level {level:s} -g {frame:d} -b:v {video_rate:d}k /dev/null && " \
               r"'{ffmpeg_bin:s}' -hide_banner -y -i '{input_file:s}' -threads 0 " \
               r"-c:v {encode_lib:s}  -c:a aac -b:a {audio_rate:d}k -pass 2 " \
               r"-f mp4 -movflags +faststart -passlogfile {prefix:s} " \
               r'-vf "format=yuv420p{opts_del_log:s}" ' \
               r"-r {frame:d} -preset {preset_type:s} -crf {crf_num:d} -profile:v {profile_type:s} " \
               r"-level {level:s} -g {frame:d} -b:v {video_rate:d}k '{output_file:s}'"
# 生成GIF
CMD_GIF_VIDEO = r"'{ffmpeg_bin:s}' -hide_banner -y -ss {start_time:f} -t '{last_time:f}' " \
                r"-i '{input_file:s}' -threads 0 -an -r {frame:d} " \
                r"-vf 'fps={frame:d},scale=-2:{target_height:d}:flags=lanczos,palettegen' '{prefix:s}.png' && " \
                r"'{ffmpeg_bin:s}' -hide_banner -y -ss {start_time:f} -t '{last_time:f}' " \
                r"-i '{input_file:s}' -i '{prefix:s}.png' -threads 0 -an -f gif -r {frame:d} " \
                r"-lavfi 'fps={frame:d},scale=-2:{target_height:d}:flags=lanczos[x];[x][1:v]paletteuse' " \
                r"'{output_file:s}'"

# 下载m3u8,合成mp4文件,使用源视频的帧率和码率
CMD_M3U8_DOWNLOAD = r"'{ffmpeg_bin:s}' -hide_banner -allowed_extensions ALL -y " \
                    r"-protocol_whitelist 'file,http,crypto,tcp' -i '{m3u8_url:s}' -threads 0 " \
                    r"-c:v {encode_lib:s} -c:a aac -f mp4 -movflags +faststart " \
                    r'-vf "format=yuv420p" -preset {preset_type:s} -crf {crf_num:d} ' \
                    r"-profile:v {profile_type:s} -level {level:s} '{output_file:s}'"
