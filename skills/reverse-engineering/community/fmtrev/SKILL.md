---
name: file-format-reverse-engineering
description: 文件格式与私有容器逆向。识别未知 magic 头、推断 TLV/chunk-based 结构、还原自家序列化格式。serialization 速识（protobuf / FlatBuffers / Cap'n Proto / MessagePack / BSON / CBOR / Avro / Thrift / Bincode / Postcard）；现成解析框架（Kaitai Struct / ImHex pattern / 010 Editor / Construct / Hachoir）；多媒体容器（MP4 box / Matroska EBML / Ogg）+ 数据库 / 备份 / 压缩 / 镜像。
---

# 文件格式 / 容器逆向

## 适用场景

- 拿到一份不认识的 .bin / .dat / .pak / .res / .sav / .vlt，要回答："里面是什么？怎么解？有没有 metadata、版本、校验？"
- 私有 / 自家序列化格式还原：游戏存档、备份格式、电商交易包、IoT 配置文件、广告 SDK 上报包。
- 通用 serialization 速识：protobuf / Flat / Cap'n Proto / MessagePack / CBOR / Thrift 等。
- 多媒体 / 数据库 / 备份 / 压缩 / 镜像容器结构解析。
- 用 Kaitai / ImHex pattern 给自家格式写一份机读规范。

## 不适用

- 网络协议 / 流式 → `protrev`。
- 完整文档 / 宏样本 → `docrev`。
- 二进制脚本字节码 → `scriptrev`。
- 加壳 / 加密容器（壳内的 PE） → `packrev`。

## 起手三秒

```bash
sample=unknown.bin
file "$sample"                                              # libmagic 第一判断
trid "$sample"                                              # 概率性
exiftool "$sample" | head -20
xxd "$sample" | head -8
strings -a "$sample" | head -30
strings -el "$sample" | head -30                            # UTF-16LE
ls -la "$sample"                                            # 大小是否对齐 (512/4096/65536)
```

熵分布看是否压缩 / 加密：

```bash
binwalk -E "$sample"                                        # 熵曲线 (gnuplot)
ent "$sample"
# 一般熵:
#   < 5    纯文本 / 重复
#   5-7    普通数据 + 二进制
#   7-7.5  压缩 / 编码
#   > 7.5  加密 / 高压缩
```

## 常见 magic 头大全（再速识一遍）

| Magic | 类型 |
| --- | --- |
| `7F 45 4C 46` (`\x7FELF`) | ELF |
| `4D 5A` (`MZ`) | PE / DOS |
| `CA FE BA BE` | Mach-O fat / Java class |
| `CE FA ED FE` / `CF FA ED FE` | Mach-O 32 / 64 LE |
| `D0 CF 11 E0 A1 B1 1A E1` | OLE2 (doc / xls / msi) |
| `50 4B 03 04` | ZIP / OOXML / JAR / APK / NUPKG |
| `52 61 72 21 1A 07` | RAR |
| `37 7A BC AF 27 1C` | 7z |
| `1F 8B 08` | gzip |
| `42 5A 68` | bzip2 |
| `28 B5 2F FD` | zstd |
| `FD 37 7A 58 5A 00` | xz |
| `04 22 4D 18` | LZ4 frame |
| `5D 00 00 80` | LZMA |
| `89 50 4E 47 0D 0A 1A 0A` | PNG |
| `FF D8 FF` | JPEG |
| `47 49 46 38` | GIF |
| `52 49 46 46 .. .. .. .. 57 45 42 50` | WebP (RIFF) |
| `42 4D` | BMP |
| `49 49 2A 00` / `4D 4D 00 2A` | TIFF LE / BE |
| `44 44 53 20` (`DDS `) | DDS texture |
| `4B 54 58 20 31 31` (`KTX 11`) | KTX 1 |
| `FF FB` / `FF F3` / `49 44 33` (`ID3`) | MP3 |
| `66 4C 61 43` (`fLaC`) | FLAC |
| `4F 67 67 53` (`OggS`) | Ogg |
| `52 49 46 46 .. .. .. .. 57 41 56 45` | WAV (RIFF) |
| `00 00 00 .. 66 74 79 70` (`ftyp`) | MP4 / MOV / 3GP / HEIF |
| `1A 45 DF A3` | Matroska (MKV / WebM) (EBML) |
| `25 50 44 46` (`%PDF`) | PDF |
| `7B 5C 72 74 66 31` (`{\rtf1`) | RTF |
| `53 51 4C 69 74 65 20 66 6F 72 6D 61 74 20 33` | SQLite 3 |
| `EF BB BF` | UTF-8 BOM (text) |
| `FF FE` / `FE FF` | UTF-16 BOM |
| `00 00 00 14 66 74 79 70 71 74` (`ftypqt  `) | QuickTime |
| `08 (00\|01)` + tag | protobuf (varint first byte) |
| `DA FF` / `D9 FF` | CBOR |
| `28 B5 2F FD` + 4 byte | zstd skippable frame |
| `45 53 54 4D` (`ESTM`) | Steam Cloud sync |
| `27 05 19 56` | U-Boot uImage |
| `73 71 73 68` (`hsqs`) | SquashFS LE |
| `28 CD 3D 45` | CramFS |
| `55 42 49 23` (`UBI#`) | UBI |
| `19 85` | JFFS2 |
| `ANDROID!` | Android Boot Image |
| `45 4D 55 33` (`EMU3`) | Emulator save? 自家定 |
| `42 4F 4F 4B` (`BOOK`) | 自家书籍格式 |
| `0A 18 00 00` 之类 | 起头一个 varint 长度，多见于 protobuf-like |

## TLV / Chunk 结构识别

```text
万变不离三宗:

A) 固定头 + body
   [magic(4)][version(2)][flags(2)][length(4)][body...]
   body 可能再细分

B) TLV (Type-Length-Value) 链
   [type(1-4)][length(1-4)][value(len)]
   [type][length][value] ...
   优点: 易扩展
   常见: ASN.1 DER, Bluetooth GATT, IEEE 802.11 IE, Apple TLV (NWAccount, AirDrop)

C) Chunk (RIFF / PNG / IFF) 风格
   每个 chunk 有 4 字节 type ID + 4 字节长度 + payload + 可选 CRC
   PNG: <length><type 4字符><data><crc>  (length 不含 type/crc)
   IFF/RIFF: FOURCC + size + payload
   常见: PNG, RIFF (WAV/AVI/WebP), AIFF, JPEG (SOI/markers), Matroska (EBML)

D) 块头 + 数据表 (PE/ELF/Mach-O 风格)
   多张表 (offset, size, attr)，主表是文件头里的 directory

E) Tagged Stream (Protobuf / CBOR / MessagePack)
   交错的 tag + 类型 + 值
```

## 多个样本对比定位字段

```bash
# 拿到 N 份同类型样本（如不同时间的 .sav）
ls samples/
# 比较所有样本对齐的字节差异
for f in samples/*.bin; do
    xxd "$f" | head -64 > "$f.hex"
done
diff samples/sample1.bin.hex samples/sample2.bin.hex | head -100
# 通常前几十字节是头部，里面的"固定字段"在所有样本里都一样
# "变化字段"是用户数据 / 时间戳 / 计数器

# 自动找变化位置
python3 - <<'PY'
import sys
from glob import glob
files = sorted(glob('samples/*.bin'))
data = [open(f,'rb').read() for f in files]
n = min(len(d) for d in data)
for i in range(n):
    bytes_at_i = set(d[i] for d in data)
    if len(bytes_at_i) > 1:
        print(f"{i:#06x}: VARIES ({len(bytes_at_i)} values, e.g. {sorted(list(bytes_at_i))[:4]})")
    elif i < 64:
        print(f"{i:#06x}: const {data[0][i]:#04x}")
PY

# 找长度字段：通常长度字段值 = 后续段落字节数 ± 头长
# 写脚本枚举每个 4 字节 dword, 看是否 = 后续偏移到 EOF
python3 - <<'PY'
import struct
data = open('sample.bin','rb').read()
for i in range(0, min(256, len(data)-4)):
    le = struct.unpack('<I', data[i:i+4])[0]
    be = struct.unpack('>I', data[i:i+4])[0]
    for v, ed in ((le,'LE'),(be,'BE')):
        # 候选: 文件剩余 = v / v+i+4 / v 等
        if v == len(data) - i - 4 or v == len(data) or v == len(data) - i:
            print(f"{i:#06x} {ed} {v} = matches file length pattern")
PY
```

## Kaitai Struct（写规范的最佳方法）

```yaml
# my_format.ksy
meta:
  id: my_format
  endian: le
  file-extension: bin
seq:
  - id: magic
    contents: [0x4D, 0x59, 0x46, 0x4D]                       # "MYFM"
  - id: version
    type: u2
  - id: flags
    type: u2
  - id: chunk_count
    type: u4
  - id: chunks
    type: chunk
    repeat: expr
    repeat-expr: chunk_count
types:
  chunk:
    seq:
      - id: tag
        type: u4
      - id: len
        type: u4
      - id: data
        size: len
        type:
          switch-on: tag
          cases:
            0x01: string_chunk
            0x02: int_array
            _: bytes_chunk
  string_chunk:
    seq:
      - id: text
        type: strz
        encoding: UTF-8
  int_array:
    seq:
      - id: values
        type: u4
        repeat: eos
  bytes_chunk:
    seq:
      - id: raw
        size-eos: true
```

```bash
# 用 Kaitai 工具
pip install kaitaistruct
kaitai-struct-compiler -t python my_format.ksy
# 生成 my_format.py，可直接 import 解析

# Web IDE: https://ide.kaitai.io
# 上传 .ksy + .bin → 树形浏览 + hex 高亮

# Compile 到其他语言
kaitai-struct-compiler -t cpp_stl my_format.ksy
kaitai-struct-compiler -t java my_format.ksy
kaitai-struct-compiler -t rust my_format.ksy

# 现成 .ksy 库
git clone https://github.com/kaitai-io/kaitai_struct_formats
# 含 300+ 格式：dos_mz, elf, mach_o, png, mp3, mp4, pdf, sqlite3 ...
```

## ImHex pattern language

```text
ImHex (https://imhex.werwolv.net): 现代 hex editor + pattern
.hexpat 是它的格式描述语言（类 C 类型）

例子:
#pragma endian little
struct Header {
    char magic[4];
    u16 version;
    u16 flags;
    u32 chunk_count;
};

enum ChunkType : u32 {
    String = 0x01,
    IntArray = 0x02,
};

struct Chunk {
    ChunkType tag;
    u32 len;
    if (tag == ChunkType::String)
        char text[len];
    else if (tag == ChunkType::IntArray)
        u32 values[len / 4];
    else
        u8 data[len];
};

struct File {
    Header hdr;
    Chunk chunks[hdr.chunk_count];
};

File file @ 0;
```

ImHex 自带一堆插件：CRC / 哈希 / Diff / Bookmark / Magic / Lua scripting / Disassembler / Math eval / Yara。

## 010 Editor binary template

```c
// my_format.bt
LittleEndian();

struct Header {
    char magic[4];
    uint16 version;
    uint16 flags;
    uint32 chunk_count;
};

struct Chunk {
    uint32 tag;
    uint32 len;
    if (tag == 1) {
        char text[len] <bgcolor=cLtGreen>;
    } else if (tag == 2) {
        uint32 values[len/4] <bgcolor=cLtBlue>;
    } else {
        uchar data[len] <bgcolor=cLtRed>;
    }
};

Header hdr;
local int i;
for (i = 0; i < hdr.chunk_count; i++) {
    Chunk chunk;
}
```

010 Editor 模板库 https://www.sweetscape.com/010editor/repository/templates/  已有 300+ 格式。

## Serialization 速识

### protobuf

```text
特征:
  - 没有 magic 头
  - 字节序列里出现"<8|low3bit type>"的 pattern
    type bits:
      0   varint        (int32/int64/uint32/uint64/sint*/bool/enum)
      1   64-bit fixed
      2   length-delim  (string/bytes/embedded msg/packed)
      5   32-bit fixed
  - 字段号 = (first_byte >> 3); 1 byte tag = 字段号 < 16

识别命令:
protoc --decode_raw < captured.bin
# 输出:
#   1: 12345
#   2: "hello"
#   3 {
#     1: "nested"
#   }

# 知道 .proto 后精确解
protoc -I. --decode=mypkg.MyMsg my.proto < captured.bin

# 反推 .proto schema
blackboxprotobuf decode captured.bin
pbtk import captured.bin                                    # protobuf toolkit
protobuf-inspector captured.bin                             # 字段类型推测

# 从二进制中提 .proto 描述
# 1) C++ binary: 查找 FileDescriptorProto 字符串
strings binary | grep '\.proto$'
strings -el binary | grep '\.proto$'

# 2) Go binary: 用 GoReSym + grep proto.Marshal
goresym -t binary | grep -i proto

# 3) Java: 反编译后看 .proto 类
```

### FlatBuffers

```text
特征:
  - 头部 4 字节: root offset (向后跳到 root vtable)
  - 后面是 vtable + 数据，零拷贝
  - 通常 schema(.fbs) 在源码里能找到

工具:
flatc --binary --schema schema.fbs sample.bin
flatc --json --schema schema.fbs sample.bin -- > sample.json
flatc --strict-json schema.fbs sample.bin

# 反推 schema
# 难，FlatBuffers 没保留字段名
# 看 vtable 大小 + 字段对齐
```

### Cap'n Proto

```text
特征:
  - 类似 protobuf 但零拷贝 + segment
  - 头: 4 字节 segment_count - 1 + 每个 segment 长度

capnp decode schema.capnp Type < sample.bin
capnp eval schema.capnp 'Type.new(...)'
```

### MessagePack

```text
特征:
  - 第一字节标 type:
      0x00-0x7f  正整数 (小)
      0xa0-0xbf  fixstr (<=31 字符)
      0xc0  nil  0xc2 false  0xc3 true
      0xc4-0xc6  bin8/16/32
      0xca-0xcb  float32/64
      0xcc-0xcf  uint8/16/32/64
      0xd0-0xd3  int8/16/32/64
      0xd9-0xdb  str8/16/32
      0xdc-0xdd  array16/32
      0xde-0xdf  map16/32

msgpack-cli unpack sample.bin
python3 -c "import msgpack; print(msgpack.unpackb(open('sample.bin','rb').read()))"
```

### CBOR

```text
RFC 8949, 类 JSON 二进制
头字节: high 3 bit = major type, low 5 bit = info

工具:
cbor2json sample.cbor                                       # python cbor2 包
cbor-diag sample.cbor                                       # 转人类可读 (CBOR diagnostic notation)
python3 -c "import cbor2; print(cbor2.loads(open('sample.cbor','rb').read()))"
```

### BSON

```text
MongoDB 用，第一个 int32 是文档长度
工具:
python3 -c "import bson; print(bson.decode_all(open('sample.bson','rb').read()))"
bsondump --pretty sample.bson
```

### Avro

```text
.avro = sync 帧 + schema (含在文件头) + 数据块
工具:
avro-tools tojson sample.avro
avro-tools getschema sample.avro
```

### Thrift

```text
二进制 / 紧凑 / JSON 三种格式
工具:
thrift -gen py schema.thrift
# 然后 import 生成的代码解码
```

### Bincode / Postcard (Rust)

```text
Bincode: serde 默认 binary，每个 int 用本机 endian + 长度
Postcard: 嵌入式优化的紧凑 varint
没有 schema 自描述，必须有源码定义
```

### Java serialization (.ser)

```text
头: AC ED 00 05
工具: ysoserial / serialdumper / Java 自己反序列化
```

### Python pickle

```text
头: 80 + version byte (e.g. 80 04 for v4)
危险: pickle 反序列化 = 任意代码执行
分析: pickletools.dis(open('x.pkl','rb').read())
```

## 多媒体容器结构

```bash
# MP4 / MOV / HEIF (Box / Atom)
mp4dump sample.mp4                                          # Bento4
mp4info sample.mp4
ffprobe -show_streams -show_format sample.mp4
exiftool sample.mp4
# 顶层 box: ftyp moov mdat free
# moov 包含: trak (track) + mvhd (header)

# Matroska / WebM (EBML)
mkvinfo sample.mkv
mkvextract tracks sample.mkv 0:audio.opus 1:video.vp9
ffprobe sample.mkv

# Ogg
ogginfo sample.ogg
oggdec sample.ogg

# RIFF (WAV / AVI / WebP)
ffprobe sample.wav
# 顶层: RIFF [size] WAVE [chunks: fmt, data, ...]

# AIFF
file sample.aiff
# FORM [size] AIFF [chunks]

# FLAC
metaflac --list sample.flac

# JPEG
exiftool sample.jpg
jpginfo sample.jpg
# Markers: FF D8 (SOI), FF E0 (APP0), FF DB (DQT), FF C0 (SOF), FF DA (SOS), FF D9 (EOI)

# PNG
pngcheck -v sample.png
pngtest sample.png
# Chunks: IHDR PLTE IDAT IEND + 可选 tEXt iTXt zTXt sRGB pHYs gAMA cHRM iCCP
```

## 数据库 / 备份 / 镜像容器

```bash
# SQLite
sqlite3 sample.db '.schema'
sqlite3 sample.db '.tables'
sqlite3 sample.db 'SELECT * FROM ... LIMIT 10'

# 受损 SQLite 修复
sqlite3 broken.db .recover > recovery.sql

# WAL/SHM 文件
# *.db-wal, *.db-shm（运行中的事务）
# 取证时这俩是必须的

# Realm (Mongo Realm / 老 io.realm)
# 二进制 KV 数据库，工具 realm-studio

# LevelDB / RocksDB
# 多文件目录，含 .log .ldb .sst MANIFEST CURRENT
leveldbutil idump LOG

# MySQL .ibd
mysqlfrm                                                    # 还原 .frm 表结构 (老版)
innochecksum sample.ibd
undrop-for-innodb                                           # 表数据恢复

# Tar / Cpio / Pax
tar -tvf sample.tar
cpio -tv < sample.cpio

# 7z / RAR / ZIP
7z l sample.7z
unzip -l sample.zip
unrar l sample.rar

# Disk image:
file sample.img
fdisk -l sample.img
losetup -fP sample.img
mount /dev/loop0p1 mnt/

# QEMU
qemu-img info sample.qcow2
qemu-img convert -f qcow2 -O raw sample.qcow2 sample.raw

# VMware
qemu-img info sample.vmdk
```

## 字节扫描小脚本

```python
# 自动猜数据类型
import struct
data = open('sample.bin','rb').read()
print(f"size: {len(data)}")

# 看是否对齐到 16/256/4096/65536
for align in (16, 256, 4096, 65536):
    if len(data) % align == 0:
        print(f"aligned to {align}")

# 找重复 magic 头（chunk 风格）
from collections import Counter
quads = Counter()
for i in range(0, len(data) - 4, 1):
    q = data[i:i+4]
    if all(0x20 <= b < 0x7f for b in q):                    # 可读 ASCII
        quads[q] += 1
print("possible chunk magics (sorted):")
for q, n in quads.most_common(20):
    print(f"  {q!r:30s} {n}")

# 找看起来像长度的字段（len == 后续到 EOF）
for i in range(0, min(len(data)-4, 4096)):
    le = struct.unpack('<I', data[i:i+4])[0]
    be = struct.unpack('>I', data[i:i+4])[0]
    rest = len(data) - i - 4
    for v, ed in ((le,'LE'),(be,'BE')):
        if 4 <= v <= rest and (v == rest or v + 4 == rest or v == rest - 4):
            print(f"{i:#06x} {ed} {v} ~~ EOF after current")
```

## 实战入口

- **Wikipedia 文件格式 / Forensic Wiki**：基本格式速查。
- **Just Solve the File Format Problem (fileformats.fandom.com)**：堪称最全。
- **Kaitai Struct format gallery**：300+ 格式现成 .ksy。
- **010 Editor template repository**：同上但 .bt 格式。
- **ImHex pattern repository**。
- **Construct library**：Python 现成解析器集合。
- **GameRes / XeNTaX forum / ReverseCraft**：游戏 / 自家格式社区。
- **CTF reversing 题**：经常出现自家文件格式。
- **Flare-On 题集 / DEFCON CTF 题集**：含格式逆向题。
- **Wireshark dissector tutorial**：网络格式与文件格式相通。

## 自检（拿到未知文件 30 分钟内回答）

1. 文件大小 + 对齐特征 + 前 64 字节 hex？
2. 是否有可读 magic 头 / FOURCC？
3. 结构是固定头 / TLV / chunk / table-of-contents？
4. 字段：版本 / flags / 长度 / 时间戳 / hash？
5. 是序列化（protobuf / msgpack / cbor）还是自家二进制？
6. 多个样本对比，哪些位置变化、哪些固定？
7. 是否压缩（高熵）/ 加密（更高熵 + 无 magic）？
8. 能否写出 .ksy / .hexpat / .bt 形式的解析器？

## 相邻技能

- `protrev` — 网络流上的相同格式（如 protobuf）。
- `docrev` — Office / PDF / RTF 文档容器。
- `binrev` — 文件解析器本身（二进制）的函数级。
- `scriptrev` — 字节码容器（.pyc / .luac / .class）。
- `fwrev` — 固件容器（uImage / SquashFS / UBI）。
- `cryptrev` — 加密 / 校验段算法识别。
- `vmrev` — 自家 VM 字节码作为文件格式。
- `iotrev` — IoT 端到端的私有格式（OTA / NVRAM / config）。
- `gamerev` — 游戏资源 / 存档自家格式。
- `revauto` — 批量分析自家格式的脚本化。