参考: 
- **https://docs.nvidia.com/cuda/index.html**
- **https://developer.nvidia.com/video-encode-decode-gpu-support-matrix#Encoder**
- **https://gist.github.com/Brainiarc7/4f831867f8e55d35cbcb527e15f9f116**

安装CUDA
===

## 安装前准备

### 禁用开源显卡驱动
```shell
cat /etc/modprobe.d/blacklist-nouveau.conf
blacklist nouveau
options nouveau modeset=0

# 重新生成内核
sudo update-initramfs -u

# 重启
sudo init 6
```

### 验证显卡
```shell
lspci | grep -i nvidia

01:00.0 VGA compatible controller: NVIDIA Corporation Device 1c03 (rev a1)
01:00.1 Audio device: NVIDIA Corporation Device 10f1 (rev a1)
```

### 查看lunix系统信息
```shell
uname -m && cat /etc/*release

x86_64
DISTRIB_ID=Ubuntu
DISTRIB_RELEASE=16.04
DISTRIB_CODENAME=xenial
DISTRIB_DESCRIPTION="Ubuntu 16.04.5 LTS"
NAME="Ubuntu"
VERSION="16.04.5 LTS (Xenial Xerus)"
ID=ubuntu
ID_LIKE=debian
PRETTY_NAME="Ubuntu 16.04.5 LTS"
VERSION_ID="16.04"
HOME_URL="http://www.ubuntu.com/"
SUPPORT_URL="http://help.ubuntu.com/"
BUG_REPORT_URL="http://bugs.launchpad.net/ubuntu/"
VERSION_CODENAME=xenial
UBUNTU_CODENAME=xenial
```

### 安装相关包
```shell
sudo apt-get install gcc g++ linux-headers-$(uname -r) dkms build-essential -y
```

## 下载并安装CUDA

### 下载
```shell
# 软件包
wget --no-check-certificate https://developer.nvidia.com/compute/cuda/9.2/Prod2/local_installers/cuda-repo-ubuntu1604-9-2-local_9.2.148-1_amd64
```

### 安装(实际为配置本地源)
```shell
sudo dpkg -i cuda-repo-ubuntu1604-9-2-local_9.2.148-1_amd64
```

### 信任安装源证书
```
sudo apt-key add /var/cuda-repo-9-2-local/7fa2af80.pub
```

### 安装软件

*实际上是建立一个本地源*

```shell
sudo apt-get update
sudo apt-get install cuda
```

## 添加环境变量
```shell
export PATH=/usr/local/cuda-9.2/bin${PATH:+:${PATH}}
export LD_LIBRARY_PATH=/usr/local/cuda-9.2/lib64${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}
```

## 验证安装

**验证前要重启服务器**

### 查看驱动信息
```shell
sudo ldconfig
cat /proc/driver/nvidia/version

NVRM version: NVIDIA UNIX x86_64 Kernel Module  396.37  Tue Jun 12 13:47:27 PDT 2018
GCC version:  gcc version 5.4.0 20160609 (Ubuntu 5.4.0-6ubuntu1~16.04.10)
```
### 使用官方实例进行编译
```shell
# 下载官方试例(环境变量配置正确的情况下,可以这样使用)
cuda-install-samples-9.2.sh  ~

# 进入示例代码目录
cd ~/NVIDIA_CUDA-9.2_Samples/

# 编译示例代码
make -j8

# 运行示例程序
cd bin/x86_64/linux/release/
./deviceQuery

./deviceQuery Starting...

 CUDA Device Query (Runtime API) version (CUDART static linking)

Detected 1 CUDA Capable device(s)

Device 0: "GeForce GTX 1060 6GB"
  CUDA Driver Version / Runtime Version          9.2 / 9.2
  CUDA Capability Major/Minor version number:    6.1
  Total amount of global memory:                 6077 MBytes (6372196352 bytes)
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

deviceQuery, CUDA Driver = CUDART, CUDA Driver Version = 9.2, CUDA Runtime Version = 9.2, NumDevs = 1
Result = PASS
```

**输出为*PASS*即表示安装完成**


安装QSV支持
===

## 安装依赖

### Install baseline dependencies first (inclusive of OpenCL headers+)

```shell
sudo apt-get -y install autoconf automake build-essential libass-dev libtool pkg-config \
texinfo zlib1g-dev libva-dev cmake mercurial libdrm-dev libvorbis-dev libogg-dev git \
libx11-dev libperl-dev libpciaccess-dev libpciaccess0 xorg-dev intel-gpu-tools \
opencl-headers libwayland-dev xutils-dev ocl-icd-* libssl-dev
```

*Then add the Oibaf PPA, needed to install the latest development headers for libva:*

```shell
sudo add-apt-repository ppa:oibaf/graphics-drivers
sudo apt-get update && sudo apt-get -y upgrade && sudo apt-get -y dist-upgrade
```

*Configure git:*

> This will be needed by some projects below, such as when building opencl-clang. Use your credentials, as you see fit:

```shelll
git config --global user.name "FirstName LastName"
git config --global user.email "your@email.com"
```

*To address linker problems down the line with Ubuntu 18.04LTS:*

> maybe already be fixed

```shell
sudo ln -s /usr/lib/x86_64-linux-gnu/libGLX_mesa.so.0 /usr/lib/x86_64-linux-gnu/libGLX_mesa.so
```

*make some dir*

```shell
mkdir ~/extapp/vaapi
```

## install libdrm

```shell
cd ~/extapp/vaapi && \
git clone https://anongit.freedesktop.org/git/mesa/drm.git libdrm && \
cd libdrm && \
./autogen.sh --prefix=/usr --enable-udev && \
time make -j$(nproc) VERBOSE=1 && \
sudo make -j$(nproc) install && \
sudo ldconfig -vvvv
```

## install libva

```shell
cd ~/extapp/vaapi && \
git clone https://github.com/01org/libva && \
cd libva && \
./autogen.sh --prefix=/usr --libdir=/usr/lib/x86_64-linux-gnu && \
time make -j$(nproc) VERBOSE=1 && \
sudo make -j$(nproc) install && \
sudo ldconfig -vvvv
```

## install gmmlib
```shell
mkdir -p ~/extapp/vaapi/workspace && \
cd ~/extapp/vaapi/workspace && \
git clone https://github.com/intel/gmmlib && \
mkdir -p build && \
cd build && \
cmake -DCMAKE_BUILD_TYPE= Release ../gmmlib && \
make -j$(nproc) && \
sudo make -j$(nproc) install
```

## install intel media driver
```shell
cd ~/extapp/vaapi/workspace && \
git clone https://github.com/intel/media-driver && \
cd media-driver && \
git submodule init && \
git pull && \
mkdir -p ~/extapp/vaapi/workspace/build_media && \
cd ~/extapp/vaapi/workspace/build_media && \
cmake ../media-driver \
-DMEDIA_VERSION="2.0.0" \
-DBS_DIR_GMMLIB=$PWD/../gmmlib/Source/GmmLib/ \
-DBS_DIR_COMMON=$PWD/../gmmlib/Source/Common/ \
-DBS_DIR_INC=$PWD/../gmmlib/Source/inc/ \
-DBS_DIR_MEDIA=$PWD/../media-driver \
-DCMAKE_INSTALL_PREFIX=/usr \
-DCMAKE_INSTALL_LIBDIR=/usr/lib/x86_64-linux-gnu \
-DINSTALL_DRIVER_SYSCONF=OFF \
-DLIBVA_DRIVERS_PATH=/usr/lib/x86_64-linux-gnu/dri && \
time make -j$(nproc) VERBOSE=1 && \
sudo make -j$(nproc) install VERBOSE=1 && \
sudo usermod -a -G video $USER
```

*Now, export environment variables as shown below:*
```
LIBVA_DRIVERS_PATH=/usr/lib/x86_64-linux-gnu/dri
LIBVA_DRIVER_NAME=iHD
```
*Put that in /etc/environment.*

## install cmrt
```shell
cd ~/extapp/vaapi && \
git clone https://github.com/01org/cmrt && \
cd cmrt && \
./autogen.sh --prefix=/usr --libdir=/usr/lib/x86_64-linux-gnu && \
time make -j$(nproc) VERBOSE=1 && \
sudo make -j$(nproc) install
```

## install intel-hybrid-driver
```shell
cd ~/extapp/vaapi && \
git clone https://github.com/01org/intel-hybrid-driver && \
cd intel-hybrid-driver && \
./autogen.sh --prefix=/usr --libdir=/usr/lib/x86_64-linux-gnu && \
time make -j$(nproc) VERBOSE=1 && \
sudo make -j$(nproc) install
```

## install intel-vaapi-driver
```shell
cd ~/extapp/vaapi && \
git clone https://github.com/01org/intel-vaapi-driver && \
cd intel-vaapi-driver && \
./autogen.sh --prefix=/usr --libdir=/usr/lib/x86_64-linux-gnu --enable-hybrid-codec && \
time make -j$(nproc) VERBOSE=1 && \
sudo make -j$(nproc) install
```

## install libva-utils
```shell
cd ~/extapp/vaapi && \
git clone https://github.com/intel/libva-utils && \
cd libva-utils && \
./autogen.sh --prefix=/usr --libdir=/usr/lib/x86_64-linux-gnu && \
time make -j$(nproc) VERBOSE=1 && \
sudo make -j$(nproc) install
```

**reboot: sudo systemctl reboot**

## install Intel Neo OpenCL runtime
```shell
sudo add-apt-repository ppa:intel-opencl/intel-opencl
sudo apt-get update
sudo apt install intel-*
```

## Install the dependencies for the OpenCL back-end
```shell
sudo apt-get install ccache flex bison cmake g++ git patch zlib1g-dev \
autoconf xutils-dev libtool pkg-config libpciaccess-dev libz-dev clinfo
```

> Use clinfo and confirm that the ICD is detected.


## install Intel MSDK
```shell
cd ~/extapp/vaapi && \
git clone https://github.com/Intel-Media-SDK/MediaSDK msdk && \
cd msdk && \
git submodule init && \
git pull && \
mkdir -p ~/extapp/vaapi/build_msdk && \
cd ~/extapp/vaapi/build_msdk && \
cmake -DCMAKE_BUILD_TYPE=Release -DENABLE_WAYLAND=ON \
-DENABLE_X11_DRI3=ON -DENABLE_OPENCL=ON  ../msdk && \
time make -j$(nproc) VERBOSE=1 && \
sudo make install -j$(nproc) VERBOSE=1
```

**Create a library config file for the iMSDK:**

```shell
sudo vi /etc/ld.so.conf.d/imsdk.conf

#Content:

/opt/intel/mediasdk/lib
/opt/intel/mediasdk/plugins

sudo ldconfig -vvvv
```

**reboot: sudo systemctl reboot**


使ffmpeg支持CUDA下的cuvid vnenc NPP QSV
===

## 安装依赖

```shell
sudo apt-get update
sudo apt-get -y install autoconf automake build-essential libass-dev libfreetype6-dev \
  libtheora-dev libtool libvorbis-dev pkg-config texinfo zlib1g-dev unzip cmake mercurial
```

## 关闭图形界面
```shell
sudo systemctl set-default multi-user.target
```

## 创建编译用的目录
```shell
mkdir ${HOME}/ffmpeg/{ffmpeg_source,ffmpeg_build,bin} -pv
```

- ffmpeg_sources: 存放源码
- ffmpeg_build: 存放目标文件
- bin: 存放二进制文件

## 安装nasm
```shell
cd ${HOME}/extapp/ffmpeg/ffmpeg_source && \
wget https://www.nasm.us/pub/nasm/releasebuilds/2.14.02/nasm-2.14.02.tar.gz && \
tar xf nasm-2.14.02.tar.gz && \
cd nasm-2.14.02 && \
./autogen.sh && \
./configure --prefix="${HOME}/extapp/ffmpeg/ffmpeg_build" --bindir="${HOME}/extapp/ffmpeg/bin" && \
make -j8 && \
make install
```

## 安装yasm

*如果系统中的yasm版本号大于1.2.0,可以直接通过系统源安装*

### 查看系统源中yasm版本
```shell
apt-cache show yasm

# 大于1.2,自己使用系统源安装
# sudo apt-get install yasm

# 或者编译安装
cd ${HOME}/extapp/ffmpeg/ffmpeg_source && \
wget http://www.tortall.net/projects/yasm/releases/yasm-1.3.0.tar.gz && \
tar xzvf yasm-1.3.0.tar.gz && \
cd yasm-1.3.0 && \
PKG_CONFIG_PATH="${HOME}/extapp/ffmpeg/ffmpeg_build/lib/pkgconfig:$PKG_CONFIG_PATH" \
PATH="${HOME}/extapp/ffmpeg/bin:$PATH" \
./configure --prefix="${HOME}/extapp/ffmpeg/ffmpeg_build" --bindir="${HOME}/extapp/ffmpeg/bin" && \
PKG_CONFIG_PATH="${HOME}/extapp/ffmpeg/ffmpeg_build/lib/pkgconfig:$PKG_CONFIG_PATH" \
PATH="${HOME}/extapp/ffmpeg/bin:$PATH" \
make -j8 && \
make install
```


**以下安装的所有依赖包都是可选的,需要在FFmpeg编译是添加相应的启用选项,所以可以根据自己需要来安装**

## 安装libx264

*需要libx264-dev的版本号大于118*

```shell
#sudo apt-get install libx264-dev

# 或者编译安装：
cd ${HOME}/extapp/ffmpeg/ffmpeg_source && \
git clone --depth 1 http://git.videolan.org/git/x264 && \
cd x264 && \
PKG_CONFIG_PATH="${HOME}/extapp/ffmpeg/ffmpeg_build/lib/pkgconfig:$PKG_CONFIG_PATH" \
PATH="${HOME}/extapp/ffmpeg/bin:$PATH" \
./configure --prefix="${HOME}/extapp/ffmpeg/ffmpeg_build" \
--bindir="${HOME}/extapp/ffmpeg/bin" --enable-static && \
PKG_CONFIG_PATH="${HOME}/extapp/ffmpeg/ffmpeg_build/lib/pkgconfig:$PKG_CONFIG_PATH" \
PATH="${HOME}/extapp/ffmpeg/bin:$PATH" \
make -j8 && \
make install
```

## 安装libx265

*需要其版本号大于68*

**我在编织的时候直接去掉了x265的支持,所以这一步可以不安装**

```shell
# 直接安装的没用,请编译安装
#sudo apt-get install libx265-dev

# 或者编译安装
cd ${HOME}/extapp/ffmpeg/ffmpeg_source && \
hg clone https://bitbucket.org/multicoreware/x265 && \
cd ${HOME}/extapp/ffmpeg/ffmpeg_source/x265/build/linux && \
PKG_CONFIG_PATH="${HOME}/extapp/ffmpeg/ffmpeg_build/lib/pkgconfig:$PKG_CONFIG_PATH" \
PATH="${HOME}/extapp/ffmpeg/bin:$PATH" \
cmake -G "Unix Makefiles" \
-DCMAKE_INSTALL_PREFIX="${HOME}/extapp/ffmpeg/ffmpeg_build" \
-DENABLE_SHARED:bool=off ../../source && \
PKG_CONFIG_PATH="${HOME}/extapp/ffmpeg/ffmpeg_build/lib/pkgconfig:$PKG_CONFIG_PATH" \
PATH="${HOME}/extapp/ffmpeg/bin:$PATH" \
make -j8 && \
make install
```


## 安装libfdk-aac

```shell
#sudo apt-get install libfdk-aac-dev 

# 或者编译安装
cd ${HOME}/extapp/ffmpeg/ffmpeg_source && \
git clone --depth 1 https://github.com/mstorsjo/fdk-aac && \
cd fdk-aac && \
PKG_CONFIG_PATH="${HOME}/extapp/ffmpeg/ffmpeg_build/lib/pkgconfig:$PKG_CONFIG_PATH" \
PATH="${HOME}/extapp/ffmpeg/bin:$PATH" \
autoreconf -fiv && \
PKG_CONFIG_PATH="${HOME}/extapp/ffmpeg/ffmpeg_build/lib/pkgconfig:$PKG_CONFIG_PATH" \
PATH="${HOME}/extapp/ffmpeg/bin:$PATH" \
./configure \
--prefix="${HOME}/extapp/ffmpeg/ffmpeg_build" \
--bindir="${HOME}/extapp/ffmpeg/bin" \
--disable-shared && \
PKG_CONFIG_PATH="${HOME}/extapp/ffmpeg/ffmpeg_build/lib/pkgconfig:$PKG_CONFIG_PATH" \
PATH="${HOME}/extapp/ffmpeg/bin:$PATH" \
make -j8 && \
make install
```

## 安装libmp3lam

*版本号大于3.98.3*

```shell
#sudo apt-get install libmp3lame-dev

# 或者编译安装
cd ${HOME}/extapp/ffmpeg/ffmpeg_source && \
wget http://downloads.sourceforge.net/project/lame/lame/3.100/lame-3.100.tar.gz && \
tar xzvf lame-3.100.tar.gz && \
cd lame-3.100 && \
PKG_CONFIG_PATH="${HOME}/extapp/ffmpeg/ffmpeg_build/lib/pkgconfig:$PKG_CONFIG_PATH" \
PATH="${HOME}/extapp/ffmpeg/bin:$PATH" \
./configure \
--prefix="${HOME}/extapp/ffmpeg/ffmpeg_build" \
--bindir="${HOME}/extapp/ffmpeg/bin" \
--disable-shared --enable-nasm && \
PKG_CONFIG_PATH="${HOME}/extapp/ffmpeg/ffmpeg_build/lib/pkgconfig:$PKG_CONFIG_PATH" \
PATH="${HOME}/extapp/ffmpeg/bin:$PATH" \
make -j8 && \
make install
```

## 安装libopus

*版本号大于1.1*

```shell
#sudo apt-get install libopus-dev

# 或者编译安装
cd ${HOME}/extapp/ffmpeg/ffmpeg_source && \
wget https://archive.mozilla.org/pub/opus/opus-1.3.1.tar.gz && \
tar xzvf opus-1.3.1.tar.gz && \
cd opus-1.3.1 && \
PKG_CONFIG_PATH="${HOME}/extapp/ffmpeg/ffmpeg_build/lib/pkgconfig:$PKG_CONFIG_PATH" \
PATH="${HOME}/extapp/ffmpeg/bin:$PATH" \
./configure \
--prefix="${HOME}/extapp/ffmpeg/ffmpeg_build" \
--bindir="${HOME}/extapp/ffmpeg/bin" \
--disable-shared && \
PKG_CONFIG_PATH="${HOME}/extapp/ffmpeg/ffmpeg_build/lib/pkgconfig:$PKG_CONFIG_PATH" \
PATH="${HOME}/extapp/ffmpeg/bin:$PATH" \
make -j8 && \
make install
```

## 安装libogg
```shell
cd ${HOME}/extapp/ffmpeg/ffmpeg_source && \
wget http://downloads.xiph.org/releases/ogg/libogg-1.3.3.tar.gz && \
tar xzvf libogg-1.3.3.tar.gz && \
cd libogg-1.3.3 && \
PKG_CONFIG_PATH="${HOME}/extapp/ffmpeg/ffmpeg_build/lib/pkgconfig:$PKG_CONFIG_PATH" \
PATH="${HOME}/extapp/ffmpeg/bin:$PATH" \
./configure \
--prefix="${HOME}/extapp/ffmpeg/ffmpeg_build" \
--bindir="${HOME}/extapp/ffmpeg/bin" \
--disable-shared && \
PKG_CONFIG_PATH="${HOME}/extapp/ffmpeg/ffmpeg_build/lib/pkgconfig:$PKG_CONFIG_PATH" \
PATH="${HOME}/extapp/ffmpeg/bin:$PATH" \
make -j8 && \
make install
```

## 安装libvorbis

```shell
cd ${HOME}/extapp/ffmpeg/ffmpeg_source && \
wget http://downloads.xiph.org/releases/vorbis/libvorbis-1.3.6.tar.gz && \
tar xzvf libvorbis-1.3.6.tar.gz && \
cd libvorbis-1.3.6 && \
PKG_CONFIG_PATH="${HOME}/extapp/ffmpeg/ffmpeg_build/lib/pkgconfig:$PKG_CONFIG_PATH" \
PATH="${HOME}/extapp/ffmpeg/bin:$PATH" \
./configure \
--prefix="${HOME}/extapp/ffmpeg/ffmpeg_build" \
--with-ogg="${HOME}/extapp/ffmpeg/ffmpeg_build" \
--bindir="${HOME}/extapp/ffmpeg/bin" \
--disable-shared && \
PKG_CONFIG_PATH="${HOME}/extapp/ffmpeg/ffmpeg_build/lib/pkgconfig:$PKG_CONFIG_PATH" \
PATH="${HOME}/extapp/ffmpeg/bin:$PATH" \
make -j8 && \
make install
```


## 安装libvpx

*版本号大于0.9.7*

```shell
#sudo apt-get install libvpx-dev

# 或者编译安装
cd ${HOME}/extapp/ffmpeg/ffmpeg_source && \
git clone --depth 1 https://chromium.googlesource.com/webm/libvpx.git && \
cd libvpx && \
PKG_CONFIG_PATH="${HOME}/extapp/ffmpeg/ffmpeg_build/lib/pkgconfig:$PKG_CONFIG_PATH" \
PATH="${HOME}/extapp/ffmpeg/bin:$PATH" \
./configure \
--prefix="${HOME}/extapp/ffmpeg/ffmpeg_build" \
--disable-examples \
--disable-unit-tests \
--enable-vp9-highbitdepth \
--as=yasm && \
PKG_CONFIG_PATH="${HOME}/extapp/ffmpeg/ffmpeg_build/lib/pkgconfig:$PKG_CONFIG_PATH" \
PATH="${HOME}/extapp/ffmpeg/bin:$PATH" \
make -j8 && \
make install
```

## 配置NVENC并下载ffmpeg

### 安装NVENC的依赖

```shell
#sudo apt-get -y install glew-utils libglew-dbg libglew-dev libglew1.13 \
#libglewmx-dev libglewmx-dbg freeglut3 freeglut3-dev freeglut3-dbg libghc-glut-dev \
#libghc-glut-doc libghc-glut-prof libalut-dev libxmu-dev libxmu-headers libxmu6 \
#libxmu6-dbg libxmuu-dev libxmuu1 libxmuu1-dbg
```

### 下载ffmpeg
```shell
# git获取代码
#cd /data/ffmpeg/ffmpeg_sources
#git clone https://github.com/FFmpeg/FFmpeg ffmpeg -b master
```

### 安装NVIDIA SDK
```
cd ${HOME}/extapp/ffmpeg/ffmpeg_source && \
git clone https://git.videolan.org/git/ffmpeg/nv-codec-headers.git && \
cd nv-codec-headers && \
make && \
sudo make install
```

### 安装ffmpeg
```shell
cd ${HOME}/extapp/ffmpeg/ffmpeg_source && \
wget https://ffmpeg.org/releases/ffmpeg-snapshot.tar.bz2 && \
tar xjvf ffmpeg-snapshot.tar.bz2 && \
cd ffmpeg && \
PKG_CONFIG_PATH="${HOME}/extapp/ffmpeg/ffmpeg_build/lib/pkgconfig:/opt/intel/mediasdk/lib/pkgconfig:/usr/local/lib/pkgconfig:$PKG_CONFIG_PATH" \
PATH="${HOME}/extapp/ffmpeg/bin:$PATH" \
./configure \
  --prefix="${HOME}/extapp/ffmpeg/ffmpeg_build" \
  --pkg-config-flags="--static" \
  --extra-cflags="-I${HOME}/extapp/ffmpeg/ffmpeg_build/include" \
  --extra-ldflags="-L${HOME}/extapp/ffmpeg/ffmpeg_build/lib" \
  --extra-cflags="-I/usr/local/cuda/include" \
  --extra-ldflags="-L/usr/local/cuda/lib64" \
  --extra-cflags="-I/opt/intel/mediasdk/include" \
  --extra-ldflags="-L/opt/intel/mediasdk/lib" \
  --extra-ldflags="-L/opt/intel/mediasdk/plugins" \
  --extra-libs="-lpthread -lm -lz -ldl" \
  --bindir="${HOME}/extapp/ffmpeg/bin" \
  --enable-libmfx \
  --enable-vaapi \
  --enable-opencl \
  --enable-libdrm \
  --enable-runtime-cpudetect \
  --enable-openssl \
  --enable-pic \
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
  --disable-debug \
  --disable-shared \
  --enable-nvenc \
  --enable-cuda \
  --enable-cuvid \
  --enable-libnpp && \
PKG_CONFIG_PATH="${HOME}/extapp/ffmpeg/ffmpeg_build/lib/pkgconfig:/usr/local/lib/pkgconfig:$PKG_CONFIG_PATH" \
PATH="${HOME}/extapp/ffmpeg/bin:$PATH" \
make -j8 && \
PKG_CONFIG_PATH="${HOME}/extapp/ffmpeg/ffmpeg_build/lib/pkgconfig:/usr/local/lib/pkgconfig:$PKG_CONFIG_PATH" \
PATH="${HOME}/extapp/ffmpeg/bin:$PATH" \
make install && \
hash -r
```

**这几个QSV要使用的**
```
  --enable-libmfx \
  --enable-vaapi \
  --enable-opencl \
  --enable-libdrm \
```

### 验证

#### 查看编码
```shell
/data/ffmpeg/bin/ffmpeg -encoders 2>/dev/null | grep nvenc

 V..... h264_nvenc           NVIDIA NVENC H.264 encoder (codec h264)
 V..... nvenc                NVIDIA NVENC H.264 encoder (codec h264)
 V..... nvenc_h264           NVIDIA NVENC H.264 encoder (codec h264)
 V..... nvenc_hevc           NVIDIA NVENC hevc encoder (codec hevc)
 V..... hevc_nvenc           NVIDIA NVENC hevc encoder (codec hevc)


ffmpeg  -hide_banner -encoders | grep vaapi

 V..... h264_vaapi           H.264/AVC (VAAPI) (codec h264)
 V..... hevc_vaapi           H.265/HEVC (VAAPI) (codec hevc)
 V..... mjpeg_vaapi          MJPEG (VAAPI) (codec mjpeg)
 V..... mpeg2_vaapi          MPEG-2 (VAAPI) (codec mpeg2video)
 V..... vp8_vaapi            VP8 (VAAPI) (codec vp8)
 V..... vp9_vaapi            VP9 (VAAPI) (codec vp9)

ffmpeg  -hide_banner -encoders | grep qsv

 V..... h264_qsv             H.264 / AVC / MPEG-4 AVC / MPEG-4 part 10 (Intel Quick Sync Video acceleration) (codec h264)
 V..... hevc_qsv             HEVC (Intel Quick Sync Video acceleration) (codec hevc)
 V..... mjpeg_qsv            MJPEG (Intel Quick Sync Video acceleration) (codec mjpeg)
 V..... mpeg2_qsv            MPEG-2 video (Intel Quick Sync Video acceleration) (codec mpeg2video)

```

#### 转码测试

##### CPU
```shell
/data/ffmpeg/bin/ffmpeg -i 012518_637.mp4 output.mp4

frame=28525 fps=195 q=29.0 size=  181504kB time=00:15:51.18 bitrate=1563.2kbits/s speed=6.51x
```

##### GPU
```shell
/data/ffmpeg/bin/ffmpeg -i 012518_637.mp4 -c:v h264_nvenc -preset default output_2.mp4

frame= 9236 fps=1026 q=19.0 size=   77824kB time=00:05:08.22 bitrate=2068.4kbits/s speed=34.2x
```
