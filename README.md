# Ghidra FIDB generator and importer script.

*Heavily inspired by: https://github.com/threatrack/ghidra-fid-generator*

## Why was this made:
I wanted to learn how to use functionIDs with Ghidra, and found the above repo for importing them in bulk. However it did not seem to work, so in an effort to learn, I rewrote it in python and fixed the issues that prevented it from running.

## Requirements:
Required commands on the system:
- ar
- tar
- 7z
- Ghidra (Tested with Ghidra 10.4)  
  
Required environment variables:
```bash
$ env | grep GHIDRA
GHIDRA_PROJ=/home/cottontail/ghidra_projects
GHIDRA_HOME=/opt/ghidra
```

## Source package file:
The source package file is a list of urls to library packages. The script uses the filename to setup pathing. The name should be `<distro>.<library>.txt`. Please see example file: `ubuntu.lib.txt`

This script downloads the library packages to the below folder structure:

```bash
$ tree src/
src/
└── ubuntu.libc
    ├── libc6-dev-amd64_2.23-0ubuntu11.3_i386.deb
    ├── libc6-dev-amd64_2.23-0ubuntu3_i386.deb
    ├── libc6-dev-amd64_2.27-3ubuntu1.5_i386.deb
    ├── libc6-dev-amd64_2.27-3ubuntu1.6_i386.deb
    ├── libc6-dev-amd64_2.27-3ubuntu1_i386.deb
    ├── libc6-dev-amd64_2.31-0ubuntu9.12_i386.deb
    ├── libc6-dev-amd64_2.31-0ubuntu9.7_i386.deb
    ├── libc6-dev-amd64_2.31-0ubuntu9_i386.deb
    ├── libc6-dev-amd64_2.35-0ubuntu3.4_i386.deb
    ├── libc6-dev-amd64_2.35-0ubuntu3_i386.deb
    ├── libc6-dev-amd64_2.37-0ubuntu2.1_i386.deb
    ├── libc6-dev-amd64_2.37-0ubuntu2_i386.deb
    ├── libc6-dev-amd64_2.38-1ubuntu6_i386.deb
    ├── libc6-dev-amd64_2.38-3ubuntu1_i386.deb
    ├── libc6-dev-arm64-cross_2.23-0ubuntu3cross1_all.deb
    ├── libc6-dev-arm64-cross_2.27-3ubuntu1cross1.1_all.deb
    ├── libc6-dev-arm64-cross_2.27-3ubuntu1cross1_all.deb
    ├── libc6-dev-arm64-cross_2.31-0ubuntu7cross1_all.deb
    ├── libc6-dev-arm64-cross_2.31-0ubuntu9.9cross1_all.deb
    ├── libc6-dev-arm64-cross_2.35-0ubuntu1cross3_all.deb
    ├── libc6-dev-arm64-cross_2.37-0ubuntu2cross1_all.deb
    ├── libc6-dev-arm64-cross_2.38-1ubuntu4cross1_all.deb
    ├── libc6-dev-arm64-cross_2.38-3ubuntu1cross1_all.deb
    ├── libc6-dev-armhf-cross_2.23-0ubuntu3cross1_all.deb
    ├── libc6-dev-armhf-cross_2.27-3ubuntu1cross1.1_all.deb
    ├── libc6-dev-armhf-cross_2.27-3ubuntu1cross1_all.deb
    ├── libc6-dev-armhf-cross_2.31-0ubuntu7cross1_all.deb
    ├── libc6-dev-armhf-cross_2.31-0ubuntu9.9cross1_all.deb
    ├── libc6-dev-armhf-cross_2.35-0ubuntu1cross3_all.deb
    ├── libc6-dev-armhf-cross_2.37-0ubuntu2cross1_all.deb
    ├── libc6-dev-armhf-cross_2.38-1ubuntu4cross1_all.deb
    ├── libc6-dev-armhf-cross_2.38-3ubuntu1cross1_all.deb
    ├── libc6-dev-i386_2.23-0ubuntu11.3_amd64.deb
    ├── libc6-dev-i386_2.23-0ubuntu3_amd64.deb
    ├── libc6-dev-i386_2.27-3ubuntu1.5_amd64.deb
    ├── libc6-dev-i386_2.27-3ubuntu1.6_amd64.deb
    ├── libc6-dev-i386_2.27-3ubuntu1_amd64.deb
    ├── libc6-dev-i386_2.31-0ubuntu9.12_amd64.deb
    ├── libc6-dev-i386_2.31-0ubuntu9.7_amd64.deb
    ├── libc6-dev-i386_2.31-0ubuntu9_amd64.deb
    ├── libc6-dev-i386_2.35-0ubuntu3.4_amd64.deb
    ├── libc6-dev-i386_2.35-0ubuntu3_amd64.deb
    ├── libc6-dev-i386_2.37-0ubuntu2.1_amd64.deb
    ├── libc6-dev-i386_2.37-0ubuntu2_amd64.deb
    ├── libc6-dev-i386_2.38-1ubuntu6_amd64.deb
    ├── libc6-dev-i386_2.38-3ubuntu1_amd64.deb
    ├── libc6-dev-powerpc-cross_2.23-0ubuntu3cross1_all.deb
    ├── libc6-dev-powerpc-cross_2.27-3ubuntu1cross1.1_all.deb
    ├── libc6-dev-powerpc-cross_2.27-3ubuntu1cross1_all.deb
    ├── libc6-dev-ppc64el-cross_2.23-0ubuntu3cross1_all.deb
    ├── libc6-dev-ppc64el-cross_2.27-3ubuntu1cross1.1_all.deb
    ├── libc6-dev-ppc64el-cross_2.27-3ubuntu1cross1_all.deb
    ├── libc6-dev-ppc64el-cross_2.31-0ubuntu7cross1_all.deb
    ├── libc6-dev-ppc64el-cross_2.31-0ubuntu9.9cross1_all.deb
    ├── libc6-dev-ppc64el-cross_2.35-0ubuntu1cross3_all.deb
    ├── libc6-dev-ppc64el-cross_2.37-0ubuntu2cross1_all.deb
    ├── libc6-dev-ppc64el-cross_2.38-1ubuntu4cross1_all.deb
    ├── libc6-dev-ppc64el-cross_2.38-3ubuntu1cross1_all.deb
    ├── libc6-dev-s390x-cross_2.31-0ubuntu7cross1_all.deb
    ├── libc6-dev-s390x-cross_2.31-0ubuntu9.9cross1_all.deb
    ├── libc6-dev-s390x-cross_2.35-0ubuntu1cross3_all.deb
    ├── libc6-dev-s390x-cross_2.37-0ubuntu2cross1_all.deb
    ├── libc6-dev-s390x-cross_2.38-1ubuntu4cross1_all.deb
    └── libc6-dev-s390x-cross_2.38-3ubuntu1cross1_all.deb
2 directories, 64 files
```
## Where are the object files:
The program uses temporary folders to extract the library packages and extracts `*.o` and `*.obj` files to the `lib/<distro>` folder.
```bash
$ tree lib
lib
└── ubuntu
    ├── libc6-dev
    │   ├── amd64_2.23
    │   │   ├── 0ubuntu11.3_i386
    │   │   │   ├── libanl
    │   │   │   │   ├── gai_cancel.o
    │   │   │   │   ├── gai_error.o
    │   │   │   │   ├── gai_misc.o
    │   │   │   │   ├── gai_notify.o
    │   │   │   │   ├── gai_suspend.o
    │   │   │   │   └── getaddrinfo_a.o
    │   │   │   ├── libBrokenLocale
    │   │   │   │   └── broken_cur_max.o
    │   │   │   ├── libc
    │   │   │   │   ├── a64l.o
    │   │   │   │   ├── abort.o
    │   │   │   │   ├── abs.o
    │   │   │   │   ├── accept4.o
    │   │   │   │   ├── accept.o
    │   │   │   │   ├── access.o
    │   │   │   │   ├── acct.o
    │   │   │   │   ├── addmul_1.o
    │   │   │   │   ├── add_n.o
    │   │   │   │   ├── adjtime.o
    │   │   │   │   ├── adjtimex.o
    │   │   │   │   ├── alarm.o
    │   │   │   │   ├── alias-lookup.o
    │   │   │   │   ├── alloca_cutoff.o
    │   │   │   │   ├── allocrtsig.o
    *** Output truncated ***
1031 directories, 173515 files
```

TODO:
- Finish README.md documentation.
- Remove Duplicates from .fidb files.
- Repack for distrubtion.
- Implement way to skip libraries that have already been imported.
- Cleanup main script output for 7z and final fidb creation.