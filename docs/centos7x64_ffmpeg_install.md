参考: 
- **https://docs.nvidia.com/cuda/index.html**
- **https://developer.nvidia.com/video-encode-decode-gpu-support-matrix#Encoder**


部署硬转软件
===

## 禁用开源显卡驱动
```shell
# 检查模块
lsmod | grep nouveau

vi /etc/modprobe.d/blacklist-nouveau.conf
blacklist nouveau
options nouveau modeset=0

# 重新生成内核
dracut --force

# 重启服务器,重新加载内核
init 6

# 检查模块
lsmod | grep nouveau
```

## 基础信息核对

### 安装基础软件包
```shell
yum install -y pciutils epel-release wget
```

### 验证显卡
```shell
lspci | grep -i nvidia

01:00.0 VGA compatible controller: NVIDIA Corporation GP106 [GeForce GTX 1060 6GB] (rev a1)
01:00.1 Audio device: NVIDIA Corporation GP106 High Definition Audio Controller (rev a1)
```

### 查看lunix系统信息
```shell
uname -m && cat /etc/*release

x86_64
CentOS Linux release 7.5.1804 (Core)
NAME="CentOS Linux"
VERSION="7 (Core)"
ID="centos"
ID_LIKE="rhel fedora"
VERSION_ID="7"
PRETTY_NAME="CentOS Linux 7 (Core)"
ANSI_COLOR="0;31"
CPE_NAME="cpe:/o:centos:centos:7"
HOME_URL="https://www.centos.org/"
BUG_REPORT_URL="https://bugs.centos.org/"

CENTOS_MANTISBT_PROJECT="CentOS-7"
CENTOS_MANTISBT_PROJECT_VERSION="7"
REDHAT_SUPPORT_PRODUCT="centos"
REDHAT_SUPPORT_PRODUCT_VERSION="7"

CentOS Linux release 7.5.1804 (Core)
CentOS Linux release 7.5.1804 (Core)
```

### 安装基础依赖包
```shell
yum install -y kernel-devel-$(uname -r) kernel-headers-$(uname -r) dkms
```

## 安装CUDA
```shell
# 下载安装源
wget --no-check-certificate https://developer.download.nvidia.com/compute/cuda/repos/rhel7/x86_64/cuda-repo-rhel7-10.0.130-1.x86_64.rpm

# 安装安装源
rpm -i cuda-repo-rhel7-10.0.130-1.x86_64.rpm
yum clean all
# 安装
yum install cuda -y
# 添加环境变量
export PATH=/usr/local/cuda/bin${PATH:+:${PATH}}
export LD_LIBRARY_PATH=/usr/local/cuda/lib64${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}
```

## 验证CUDA

**验证前要重启服务器**

### 查看驱动信息
```shell
ldconfig
cat /proc/driver/nvidia/version

NVRM version: NVIDIA UNIX x86_64 Kernel Module  410.48  Thu Sep  6 06:36:33 CDT 2018
GCC version:  gcc 版本 4.8.5 20150623 (Red Hat 4.8.5-28) (GCC)
```
### 使用官方实例进行编译
```shell
# 下载官方试例(环境变量配置正确的情况下,可以这样使用)
cuda-install-samples-10.0.sh  ~

# 进入示例代码目录
cd ~/NVIDIA_CUDA-10.0_Samples/

# 编译示例代码
make -j8

# 运行示例程序
cd bin/x86_64/linux/release/
./deviceQuery

./deviceQuery Starting...

 CUDA Device Query (Runtime API) version (CUDART static linking)

Detected 1 CUDA Capable device(s)

Device 0: "GeForce GTX 1060 6GB"
  CUDA Driver Version / Runtime Version          10.0 / 10.0
  CUDA Capability Major/Minor version number:    6.1
  Total amount of global memory:                 6078 MBytes (6373179392 bytes)
  (10) Multiprocessors, (128) CUDA Cores/MP:     1280 CUDA Cores
  GPU Max Clock rate:                            1785 MHz (1.78 GHz)
  Memory Clock rate:                             4004 Mhz
  Memory Bus Width:                              192-bit
  L2 Cache Size:                                 1572864 bytes
  Maximum Texture Dimension Size (x,y,z)         1D=(131072), 2D=(131072, 65536), 3D=(16384, 16384, 16384)
  Maximum Layered 1D Texture Size, (num) layers  1D=(32768), 2048 layers
  Maximum Layered 2D Texture Size, (num) layers  2D=(32768, 32768), 2048 layers
  Total amount of constant memory:               65536 bytes
  Total amount of shared memory per block:       49152 bytes
  Total number of registers available per block: 65536
  Warp size:                                     32
  Maximum number of threads per multiprocessor:  2048
  Maximum number of threads per block:           1024
  Max dimension size of a thread block (x,y,z): (1024, 1024, 64)
  Max dimension size of a grid size    (x,y,z): (2147483647, 65535, 65535)
  Maximum memory pitch:                          2147483647 bytes
  Texture alignment:                             512 bytes
  Concurrent copy and kernel execution:          Yes with 2 copy engine(s)
  Run time limit on kernels:                     No
  Integrated GPU sharing Host Memory:            No
  Support host page-locked memory mapping:       Yes
  Alignment requirement for Surfaces:            Yes
  Device has ECC support:                        Disabled
  Device supports Unified Addressing (UVA):      Yes
  Device supports Compute Preemption:            Yes
  Supports Cooperative Kernel Launch:            Yes
  Supports MultiDevice Co-op Kernel Launch:      Yes
  Device PCI Domain ID / Bus ID / location ID:   0 / 1 / 0
  Compute Mode:
     < Default (multiple host threads can use ::cudaSetDevice() with device simultaneously) >

deviceQuery, CUDA Driver = CUDART, CUDA Driver Version = 10.0, CUDA Runtime Version = 10.0, NumDevs = 1
Result = PASS
```

**输出为*PASS*即表示安装完成**



## 使ffmpeg支持CUDA下的cuvid vnenc和NPP

### 准备工作
```shell
# 安装依赖
yum install -y autoconf automake bzip2 cmake freetype-devel gcc gcc-c++ git libtool make mercurial pkgconfig zlib-devel libass-devel bzip2-devel
```

**以上步骤每一台硬转机都需要,"使ffmpeg支持CUDA下的cuvid vnenc和NPP"此步骤其他硬转机可以拷贝二进制文件**

```shell
# 创建编译所需目录
mkdir -pv /opt/ffmpeg/{ffmpeg_sources,ffmpeg_build,bin}


# 编译安装其他依赖包
# Tip: If you do not require certain encoders you may skip the relevant section 
# and then remove the appropriate ./configure option in FFmpeg. 
# For example, if libvorbis is not needed, then skip that section 
# and then remove --enable-libvorbis from the Install FFmpeg section. 

## nasm
cd /opt/ffmpeg/ffmpeg_sources && \
curl -O -L http://www.nasm.us/pub/nasm/releasebuilds/2.13.03/nasm-2.13.03.tar.bz2 && \
tar xjvf nasm-2.13.03.tar.bz2 && \
cd nasm-2.13.03 && \
./autogen.sh && \
./configure --prefix="/opt/ffmpeg/ffmpeg_build" --bindir="/opt/ffmpeg/bin" && \
make -j8 && \
make install

## yasm
cd /opt/ffmpeg/ffmpeg_sources && \
curl -O -L http://www.tortall.net/projects/yasm/releases/yasm-1.3.0.tar.gz && \
tar xzvf yasm-1.3.0.tar.gz && \
cd yasm-1.3.0 && \
PKG_CONFIG_PATH="/opt/ffmpeg/ffmpeg_build/lib/pkgconfig:$PKG_CONFIG_PATH" \
PATH="/opt/ffmpeg/bin:$PATH" \
./configure --prefix="/opt/ffmpeg/ffmpeg_build" --bindir="/opt/ffmpeg/bin" && \
PKG_CONFIG_PATH="/opt/ffmpeg/ffmpeg_build/lib/pkgconfig:$PKG_CONFIG_PATH" \
PATH="/opt/ffmpeg/bin:$PATH" \
make -j8 && \
make install


## libx264
cd /opt/ffmpeg/ffmpeg_sources && \
git clone --depth 1 http://git.videolan.org/git/x264 && \
cd x264 && \
PKG_CONFIG_PATH="/opt/ffmpeg/ffmpeg_build/lib/pkgconfig:$PKG_CONFIG_PATH" \
PATH="/opt/ffmpeg/bin:$PATH" \
./configure --prefix="/opt/ffmpeg/ffmpeg_build" \
--bindir="/opt/ffmpeg/bin" --enable-static && \
PKG_CONFIG_PATH="/opt/ffmpeg/ffmpeg_build/lib/pkgconfig:$PKG_CONFIG_PATH" \
PATH="/opt/ffmpeg/bin:$PATH" \
make -j8 && \
make install


## libx265
cd /opt/ffmpeg/ffmpeg_sources && \
hg clone https://bitbucket.org/multicoreware/x265 && \
cd /opt/ffmpeg/ffmpeg_sources/x265/build/linux && \
PKG_CONFIG_PATH="/opt/ffmpeg/ffmpeg_build/lib/pkgconfig:$PKG_CONFIG_PATH" \
PATH="/opt/ffmpeg/bin:$PATH" \
cmake -G "Unix Makefiles" \
-DCMAKE_INSTALL_PREFIX="/opt/ffmpeg/ffmpeg_build" \
-DENABLE_SHARED:bool=off ../../source && \
PKG_CONFIG_PATH="/opt/ffmpeg/ffmpeg_build/lib/pkgconfig:$PKG_CONFIG_PATH" \
PATH="/opt/ffmpeg/bin:$PATH" \
make -j8 && \
make install


## libfdk_aac
cd /opt/ffmpeg/ffmpeg_sources && \
git clone --depth 1 https://github.com/mstorsjo/fdk-aac && \
cd fdk-aac && \
PKG_CONFIG_PATH="/opt/ffmpeg/ffmpeg_build/lib/pkgconfig:$PKG_CONFIG_PATH" \
PATH="/opt/ffmpeg/bin:$PATH" \
autoreconf -fiv && \
PKG_CONFIG_PATH="/opt/ffmpeg/ffmpeg_build/lib/pkgconfig:$PKG_CONFIG_PATH" \
PATH="/opt/ffmpeg/bin:$PATH" \
./configure \
--prefix="/opt/ffmpeg/ffmpeg_build" \
--bindir="/opt/ffmpeg/bin" \
--disable-shared && \
PKG_CONFIG_PATH="/opt/ffmpeg/ffmpeg_build/lib/pkgconfig:$PKG_CONFIG_PATH" \
PATH="/opt/ffmpeg/bin:$PATH" \
make -j8 && \
make install


## libmp3lame
cd /opt/ffmpeg/ffmpeg_sources && \
curl -O -L http://downloads.sourceforge.net/project/lame/lame/3.100/lame-3.100.tar.gz && \
tar xzvf lame-3.100.tar.gz && \
cd lame-3.100 && \
PKG_CONFIG_PATH="/opt/ffmpeg/ffmpeg_build/lib/pkgconfig:$PKG_CONFIG_PATH" \
PATH="/opt/ffmpeg/bin:$PATH" \
./configure \
--prefix="/opt/ffmpeg/ffmpeg_build" \
--bindir="/opt/ffmpeg/bin" \
--disable-shared --enable-nasm && \
PKG_CONFIG_PATH="/opt/ffmpeg/ffmpeg_build/lib/pkgconfig:$PKG_CONFIG_PATH" \
PATH="/opt/ffmpeg/bin:$PATH" \
make -j8 && \
make install



## libopus
cd /opt/ffmpeg/ffmpeg_sources && \
curl -O -L https://archive.mozilla.org/pub/opus/opus-1.2.1.tar.gz && \
tar xzvf opus-1.2.1.tar.gz && \
cd opus-1.2.1 && \
PKG_CONFIG_PATH="/opt/ffmpeg/ffmpeg_build/lib/pkgconfig:$PKG_CONFIG_PATH" \
PATH="/opt/ffmpeg/bin:$PATH" \
./configure \
--prefix="/opt/ffmpeg/ffmpeg_build" \
--bindir="/opt/ffmpeg/bin" \
--disable-shared && \
PKG_CONFIG_PATH="/opt/ffmpeg/ffmpeg_build/lib/pkgconfig:$PKG_CONFIG_PATH" \
PATH="/opt/ffmpeg/bin:$PATH" \
make -j8 && \
make install


## libogg
cd /opt/ffmpeg/ffmpeg_sources && \
curl -O -L http://downloads.xiph.org/releases/ogg/libogg-1.3.3.tar.gz && \
tar xzvf libogg-1.3.3.tar.gz && \
cd libogg-1.3.3 && \
PKG_CONFIG_PATH="/opt/ffmpeg/ffmpeg_build/lib/pkgconfig:$PKG_CONFIG_PATH" \
PATH="/opt/ffmpeg/bin:$PATH" \
./configure \
--prefix="/opt/ffmpeg/ffmpeg_build" \
--bindir="/opt/ffmpeg/bin" \
--disable-shared && \
PKG_CONFIG_PATH="/opt/ffmpeg/ffmpeg_build/lib/pkgconfig:$PKG_CONFIG_PATH" \
PATH="/opt/ffmpeg/bin:$PATH" \
make -j8 && \
make install


## libvorbis
cd /opt/ffmpeg/ffmpeg_sources && \
curl -O -L http://downloads.xiph.org/releases/vorbis/libvorbis-1.3.5.tar.gz && \
tar xzvf libvorbis-1.3.5.tar.gz && \
cd libvorbis-1.3.5 && \
PKG_CONFIG_PATH="/opt/ffmpeg/ffmpeg_build/lib/pkgconfig:$PKG_CONFIG_PATH" \
PATH="/opt/ffmpeg/bin:$PATH" \
./configure \
--prefix="/opt/ffmpeg/ffmpeg_build" \
--with-ogg="/opt/ffmpeg/ffmpeg_build" \
--bindir="/opt/ffmpeg/bin" \
--disable-shared && \
PKG_CONFIG_PATH="/opt/ffmpeg/ffmpeg_build/lib/pkgconfig:$PKG_CONFIG_PATH" \
PATH="/opt/ffmpeg/bin:$PATH" \
make -j8 && \
make install


## libvpx
cd /opt/ffmpeg/ffmpeg_sources && \
git clone --depth 1 https://chromium.googlesource.com/webm/libvpx.git && \
cd libvpx && \
PKG_CONFIG_PATH="/opt/ffmpeg/ffmpeg_build/lib/pkgconfig:$PKG_CONFIG_PATH" \
PATH="/opt/ffmpeg/bin:$PATH" \
./configure \
--prefix="/opt/ffmpeg/ffmpeg_build" \
--disable-examples \
--disable-unit-tests \
--enable-vp9-highbitdepth \
--as=yasm && \
PKG_CONFIG_PATH="/opt/ffmpeg/ffmpeg_build/lib/pkgconfig:$PKG_CONFIG_PATH" \
PATH="/opt/ffmpeg/bin:$PATH" \
make -j8 && \
make install



## nvidia SDK
cd /opt/ffmpeg/ffmpeg_sources/ && \
git clone https://git.videolan.org/git/ffmpeg/nv-codec-headers.git && \
cd nv-codec-headers && \
make && \
make install
```

### 编译安装ffmpeg
```shell
cd /opt/ffmpeg/ffmpeg_sources && \
curl -O -L https://ffmpeg.org/releases/ffmpeg-snapshot.tar.bz2 && \
tar xjvf ffmpeg-snapshot.tar.bz2 && \
cd ffmpeg && \
PKG_CONFIG_PATH="/opt/ffmpeg/ffmpeg_build/lib/pkgconfig:/usr/local/lib/pkgconfig:$PKG_CONFIG_PATH" \
PATH="/opt/ffmpeg/bin:$PATH" \
./configure \
  --prefix="/opt/ffmpeg/ffmpeg_build" \
  --pkg-config-flags="--static" \
  --extra-cflags="-I/opt/ffmpeg/ffmpeg_build/include" \
  --extra-ldflags="-L/opt/ffmpeg/ffmpeg_build/lib" \
  --extra-cflags="-I/usr/local/cuda/include" \
  --extra-ldflags="-L/usr/local/cuda/lib64" \
  --extra-libs=-lpthread \
  --extra-libs=-lm \
  --bindir="/opt/ffmpeg/bin" \
  --enable-gpl \
  --enable-libass \
  --enable-libfdk_aac \
  --enable-libfreetype \
  --enable-libmp3lame \
  --enable-libopus \
  --enable-libvorbis \
  --enable-libvpx \
  --enable-libx264 \
  --enable-libx265 \
  --enable-nonfree \
  --disable-shared \
  --enable-nvenc \
  --enable-cuda \
  --enable-cuvid \
  --enable-libnpp && \
PKG_CONFIG_PATH="/opt/ffmpeg/ffmpeg_build/lib/pkgconfig:$PKG_CONFIG_PATH" \
PATH="/opt/ffmpeg/bin:$PATH" \
make -j8 && \
PKG_CONFIG_PATH="/opt/ffmpeg/ffmpeg_build/lib/pkgconfig:$PKG_CONFIG_PATH" \
PATH="/opt/ffmpeg/bin:$PATH" \
make install && \
hash -r
```

### 验证ffmpeg安装
#### 查看编码
```shell
/opt/ffmpeg/bin/ffmpeg -encoders 2>/dev/null | grep nvenc

 V..... h264_nvenc           NVIDIA NVENC H.264 encoder (codec h264)
 V..... nvenc                NVIDIA NVENC H.264 encoder (codec h264)
 V..... nvenc_h264           NVIDIA NVENC H.264 encoder (codec h264)
 V..... nvenc_hevc           NVIDIA NVENC hevc encoder (codec hevc)
 V..... hevc_nvenc           NVIDIA NVENC hevc encoder (codec hevc)
```

#### 转码测试
##### CPU
```shell
/opt/ffmpeg/bin/ffmpeg -i 012518_637.mp4 output.mp4

frame=109793 fps=174 q=-1.0 Lsize=  753684kB time=01:00:59.73 bitrate=1687.1kbits/s speed=5.79x
```

##### GPU
```shell
/opt/ffmpeg/bin/ffmpeg -i 012518_637.mp4 -c:v h264_nvenc -preset default output_2.mp4

frame=109793 fps=1081 q=17.0 Lsize=  948846kB time=01:00:59.73 bitrate=2123.9kbits/s speed=  36x
```