from setuptools import setup
from setuptools import find_packages
setup(name='aioffmpeg',
      version='0.1.25',
      description='a ffmpeg wrapped lib for asyncio',
      long_description='',
      author='ucrux',
      author_email='ucrux@none.com',
      url='https://github.com/ucrux/aioffmpeg.git',
      license='MIT',
      #install_requires=['aiofiles>=0.4.0'],
      python_requires='>= 3.7',
      classifiers=[
            # 发展时期,常见的如下
            #   3 - Alpha
            #   4 - Beta
            #   5 - Production/Stable
            'Development Status :: 3 - Alpha',
            # 开发的目标用户
            'Intended Audience :: Developers',
            'Operating System :: POSIX',
            # 目标 Python 版本
            'Programming Language :: Python :: 3.7',
            'Topic :: Software Development :: Bug Tracking',
      ],
      packages=find_packages(exclude=["*test*"]),
      entry_points={
        'console_scripts': [
            'aioffpmeg = aioffmpeg.cmdline_tool:main',
        ]     
      }
      #package_dir = {'':'aioffmpeg'},
      #py_modules=['h264video', '_aioffmpeg_cmd_raw_str', '_aioffmpeg_tools_func', 'aioffmpeg_cmd_opts', 'aioffmpeg_tools_func']
      )
