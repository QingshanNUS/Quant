readme:

This is the tutorial for setting up bloomberg python api without C# environment. 
The method is to use visual studio build tools to connect C# api with python.

need:
blpapi_cpp             #Bloomberg Open API C/C++ version 3.9+
blpapi-3.9.0           #Bloomberg Open API Python version 3.9+
Visual studio 2017 + Python development workload + native development tools option
Visual studio 2017 build tools

install using the commands below:
C:\Program Files (x86)\Microsoft Visual C++ Build Tools>set BLPAPI_ROOT=c:\blpapi_cpp
C:\Program Files (x86)\Microsoft Visual C++ Build Tools>cd c:\blpapi-3.9.0
c:\blpapi-3.9.0>python setup.py install


if fatal error LNK1158:cannot run'rc.exe':

add environment variables: C:\Program Files (x86)\Windows Kits\8.0\bin\x86

copy these files:
rc.exe
rcdll.dll

from:
C:\Program Files (x86)\Windows Kits\8.0\bin\x86

to:
C:\Program Files (x86)\Microsoft Visual Studio 11.0\VC\bin


Qingshan
May 30 2018