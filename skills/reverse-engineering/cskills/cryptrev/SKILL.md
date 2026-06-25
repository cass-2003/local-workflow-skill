---
name: cryptographic-reverse-engineering
description: 加密算法识别与实现审计逆向。识别样本里使用的算法（AES/DES/RC4/ChaCha/SM4/RSA/EC/HMAC/...）、模式（ECB/CBC/GCM/CTR）、库（OpenSSL/libsodium/CryptoJS/CommonCrypto/JCE）、自实现魔改密码、key 生命周期与典型误用。配合 binrev/scriptrev/webrev 用。
---

# 加密算法识别与实现审计逆向

## 适用场景

- 二进制 / JS / dex / .NET IL 里看到一段疑似加密代码，要回答："这是什么算法？什么模式？key 怎么来的？iv/nonce 怎么来的？输出格式？"
- 接口签名 / token / 配置文件 / DRM / license 校验里嵌入加密，要还原成 Python/Node 等价实现以便 fuzz 或解析。
- 审计自家或第三方代码：检查 key 硬编码、IV 重用、ECB、不带 MAC、time-leaky 比较、随机数源。
- 发现自实现 / 魔改算法（改 S-box / 改轮常量 / 改置换），要识别基础形态并差异化。

## 不适用

- 算法本身已知，问的是"绕过 license/DRM/支付"——不在本技能范围。
- 协议字段位级 → `protrev`。
- 加壳和 packer 内置解密 → `packrev`（packer 解密后的 payload 才回 cryptrev）。

## 算法快速识别（按指纹）

### 对称分组

| 算法 | 特征 |
| --- | --- |
| AES (Rijndael) | S-box `63 7c 77 7b f2 6b 6f c5 30 01 67 2b fe d7 ab 76 ...`；逆 S-box `52 09 6a d5 30 36 a5 38 bf 40 a3 9e 81 f3 d7 fb`；轮常量 `01 02 04 08 10 20 40 80 1b 36`；T-table 4×1024 字节；块 16，key 16/24/32 |
| DES / 3DES | S1..S8 表（`14 04 13 01 02 0f ...`）；初始置换 IP / 逆置换；块 8，key 8 |
| Blowfish | P-array 18 个 32-bit + 4×256 S-box，源自 π 小数；块 8，key 1..56 |
| Twofish | MDS 矩阵、Q0/Q1 排列、白化轮 | 
| RC4 | 256 字节 S 数组 + i,j 双指针 + KSA / PRGA；流密码无块边界 |
| ChaCha20 / Salsa20 | 常量 `expand 32-byte k` / `expa nd 32 -byt e k`；4×4 状态、20 轮、64-byte block；常配 Poly1305 |
| SM4（中国国密） | S-box `d6 90 e9 fe cc e1 3d b7 16 b6 14 c2 28 fb 2c ...`；轮常量 ck `00070e15 1c232a31 ...`；块 16，key 16 |
| TEA / XTEA / XXTEA | `magic = 0x9e3779b9`（黄金分割衍生）；64-bit 块；32 轮 |
| Camellia | sigma 常量 `a09e667f3bcc908b ...`、SP 表 |
| ARIA | 类 Rijndael S-box，但不是同一组 |

### 流密码 / KDF

| 算法 | 特征 |
| --- | --- |
| HMAC | `ipad=0x36 (×64)` / `opad=0x5c (×64)`；两次 hash 嵌套 |
| HKDF | extract = HMAC(salt, IKM)；expand 用 HMAC 链 |
| PBKDF2 | HMAC + 计数 i 大端拼接 + 大量迭代 |
| scrypt | N/r/p 参数；ROMix；BlockMix；Salsa20/8 内核 |
| bcrypt | `$2a$ / $2b$ / $2y$` 前缀；EksBlowfish；72 字节 password 限 |
| argon2 | id/i/d 变种；Blake2b 内核；时间/内存/并发参数 |

### 哈希

| 算法 | 输出 / 内核 |
| --- | --- |
| MD5 | 16 bytes；`a=0x67452301 b=0xefcdab89 c=0x98badcfe d=0x10325476` |
| SHA-1 | 20 bytes；初始 `H0=67452301 H1=efcdab89 H2=98badcfe H3=10325476 H4=c3d2e1f0` |
| SHA-256 | 32 bytes；K 常量 64 个 `428a2f98 71374491 ...`；H 初值 `6a09e667 bb67ae85 ...` |
| SHA-512 | 64 bytes；80 轮；64-bit 字 |
| SHA-3 / Keccak | round constants + ρ 常量；状态 5×5×64 |
| Blake2b/2s | 类 ChaCha 的 G 函数；自带 keyed hash 模式 |
| SM3 | 国密；T 常量 `7380166f`/`7a879d8a`；与 SHA-256 接近但 P0/P1 置换不同 |

### 公钥

| 算法 | 特征 |
| --- | --- |
| RSA | 大整数 + 模幂；常见 e=65537；OAEP / PKCS1v15 / PSS 填充指纹 |
| DH | 大素数 p + 生成元 g；模幂 |
| ECDSA / ECDH | 曲线参数：P-256 / secp256k1 / Curve25519 / SM2；常量 a/b/p/n/Gx/Gy |
| Ed25519 | Curve25519 + SHA-512；公私钥都是 32 字节 |
| SM2 | 国密曲线；签名带 ZA(用户标识哈希) |

### 编码 / 校验（不是加密但常被认成加密）

| 名 | 字符集 / 特征 |
| --- | --- |
| Base64 / Base64URL | `A-Za-z0-9+/=` 或 `A-Za-z0-9-_` |
| Base32 | `A-Z2-7=` |
| Base58 (Bitcoin) | 无 0OIl |
| URL encode | `%XX` |
| hex | 0-9a-f |
| CRC32 | poly `0xEDB88320`（reverse 0x04C11DB7） |
| Adler-32 | mod 65521 |
| XOR | 单字节循环 / 多字节 key 重复 / 流式加滚 |

## 核心工具

| 名 | 作用 |
| --- | --- |
| **findcrypt-yara** | IDA 插件，扫描所有已知常量表（S-box/IV/Magic）→ 在反编译中标注 |
| **kerckhoffs** | radare2 / Ghidra 算法识别脚本 |
| **CryptoIdent / FindCrypt2 / CryptoSearcher** | 老牌 IDA 插件 |
| **capa-rules: data-manipulation/encryption/** | capa 规则集，函数级算法识别 |
| **YARA crypto.yar / crypto_signatures.yar** | 二进制扫描，多算法常量库 |
| **CyberChef** | 浏览器解码瑞士军刀，调试自实现链最快 |
| **dcode.fr / boxentriq.com** | 在线密码工具 |
| **OpenSSL / libsodium 源码** | 对照参考实现 |
| **ssdeep / tlsh** | 模糊哈希，对比相似实现 |

## 工作流

### 1. 静态扫一遍常量

```bash
# 二进制
yara -s rules/crypto_signatures.yar orig.bin
yara -s rules/findcrypt.yar orig.bin
capa orig.bin -t 'data-manipulation/encryption' -t 'data-manipulation/hashing'
floss orig.bin > strings.de.txt   # 解码混淆字符串再 grep magic

# 通用 grep（命中 → 转 hex 再 grep 二进制）
grep -ao 'expand 32-byte k' orig.bin   # ChaCha20
grep -aoE 'OpenSSL [0-9.]+|BoringSSL|libsodium|wolfSSL|CryptoJS|BouncyCastle'
xxd orig.bin | grep -E '637c777b f26b6fc5 |52096ad5 30360a5 '   # AES sbox / inv-sbox

# Python 找常量表
python3 -c '
import struct, sys
data = open(sys.argv[1],"rb").read()
sbox = bytes([0x63,0x7c,0x77,0x7b,0xf2,0x6b,0x6f,0xc5,0x30,0x01,0x67,0x2b,0xfe,0xd7,0xab,0x76])
print("AES sbox at", hex(data.find(sbox)) if sbox in data else "no")
' orig.bin
```

### 2. 反编译看模式

OpenSSL EVP 调用链是最常见的：

```c
EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
EVP_EncryptInit_ex(ctx, EVP_aes_256_gcm(), NULL, key, iv);    // 这里就锁定了算法+模式
EVP_EncryptUpdate(ctx, out, &outl, in, inl);
EVP_EncryptFinal_ex(ctx, out+outl, &outl2);
EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_GET_TAG, 16, tag);
```

Windows BCryptXxx：

```c
BCryptOpenAlgorithmProvider(&hAlg, BCRYPT_AES_ALGORITHM, NULL, 0);
BCryptSetProperty(hAlg, BCRYPT_CHAINING_MODE, (PBYTE)BCRYPT_CHAIN_MODE_GCM, ...);
BCryptGenerateSymmetricKey(hAlg, &hKey, NULL, 0, key, keyLen, 0);
BCryptEncrypt(hKey, in, inLen, &authInfo, iv, ivLen, out, outLen, &cb, 0);
```

JNI / Android（看 java.crypto / bouncycastle）：

```java
Cipher c = Cipher.getInstance("AES/GCM/NoPadding");           // 字符串就是答案
SecretKeySpec k = new SecretKeySpec(keyBytes, "AES");
GCMParameterSpec p = new GCMParameterSpec(128, iv);
c.init(Cipher.ENCRYPT_MODE, k, p);
byte[] ct = c.doFinal(plain);
```

JS（Web / Node）：

```js
crypto.subtle.encrypt({name:'AES-GCM', iv}, key, data)        // WebCrypto
CryptoJS.AES.encrypt(plain, CryptoJS.enc.Hex.parse(keyHex), {mode:CryptoJS.mode.CBC, iv:CryptoJS.enc.Hex.parse(ivHex), padding:CryptoJS.pad.Pkcs7})
require('crypto').createCipheriv('aes-256-cbc', key, iv)      // Node
```

iOS / CommonCrypto：

```c
CCCryptorCreate(kCCEncrypt, kCCAlgorithmAES, kCCOptionPKCS7Padding, key, kCCKeySizeAES256, iv, &cryptor);
CCCryptorUpdate(cryptor, in, inLen, out, outLen, &moved);
```

### 3. 还原成参考实现

把抓到的 key/iv/算法/模式写一份 Python 等价：

```python
# AES-256-GCM 等价
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
key = bytes.fromhex("...")
iv  = bytes.fromhex("...")
ct  = bytes.fromhex("...")
tag = ct[-16:]
body = ct[:-16]
c = Cipher(algorithms.AES(key), modes.GCM(iv, tag)).decryptor()
print(c.update(body) + c.finalize())

# RC4 等价（自实现常用）
def rc4(key, data):
    S = list(range(256))
    j = 0
    for i in range(256):
        j = (j + S[i] + key[i % len(key)]) & 0xff
        S[i], S[j] = S[j], S[i]
    i = j = 0
    out = bytearray()
    for c in data:
        i = (i+1) & 0xff
        j = (j+S[i]) & 0xff
        S[i], S[j] = S[j], S[i]
        out.append(c ^ S[(S[i]+S[j]) & 0xff])
    return bytes(out)
```

### 4. 动态 hook 抓 key / iv / 明文

Frida 脚本（Android / iOS / Linux / macOS / Windows 通用）：

```js
// hook OpenSSL EVP_EncryptInit_ex 拿 key+iv+算法
const init = Module.findExportByName(null, 'EVP_EncryptInit_ex');
Interceptor.attach(init, {
  onEnter(args) {
    this.alg = args[1];
    this.key = args[3];
    this.iv  = args[4];
  },
  onLeave(retval) {
    const algName = new NativePointer(this.alg).readPointer();   // EVP_CIPHER 结构体
    console.log('[EVP_EncryptInit] cipher_ptr=', this.alg);
    console.log('  key=', this.key.isNull() ? null : Memory.readByteArray(this.key, 32));
    console.log('  iv =', this.iv.isNull() ? null : Memory.readByteArray(this.iv, 16));
  }
});

// hook Java AES（Android）
Java.perform(() => {
  const Cipher = Java.use('javax.crypto.Cipher');
  Cipher.init.overload('int','java.security.Key','java.security.spec.AlgorithmParameterSpec').implementation = function(m,k,s){
    console.log('Cipher.init mode='+m+' algo='+this.getAlgorithm()+' key='+k.getEncoded());
    return this.init(m,k,s);
  };
  Cipher.doFinal.overload('[B').implementation = function(input){
    const out = this.doFinal(input);
    console.log('doFinal in=',input.length,'out=',out.length);
    return out;
  };
});
```

iOS CommonCrypto：

```js
const cc = Module.findExportByName('libcommonCrypto.dylib', 'CCCryptorCreate');
Interceptor.attach(cc, {
  onEnter(args){
    this.op = args[0].toInt32();
    this.alg= args[1].toInt32();
    this.opt= args[2].toInt32();
    this.key= args[3];
    this.kl = args[4].toInt32();
  },
  onLeave(){
    console.log('CCCryptorCreate', this.op, this.alg, 'keyLen='+this.kl, 'key=', Memory.readByteArray(this.key, this.kl));
  }
});
```

Windows BCryptEncrypt：直接拿 BCryptGenerateSymmetricKey 截 key，再 hook BCryptEncrypt 拿明文 + iv。

### 5. 自实现魔改的辨识

**改 S-box**：把 256 字节常量 dump 出来，与标准 AES S-box 比对：相同长度但 hash 不同 → 大概率换表。注意 S-box 满足 `S(0)+S(255) ≠ 0xff` 时一定是非标准。

**改轮常量**：AES Rcon 是 `01 02 04 08 10 20 40 80 1b 36`，魔改常用左移基数变化。

**改 IV 长度**：标准 AES-GCM IV=12B 最优，AES-CBC IV=16B；看到怪长度先怀疑魔改。

**改顺序**：把 SubBytes/ShiftRows/MixColumns/AddRoundKey 调换 → 等价构造无意义但能挡死照搬解密。

**白盒 AES**：T-table 形式，4×1024 字节，但每个 T 表都被随机仿射变换包裹 → 看到上千 KB "S-box 表" → 白盒。

## 误用模式（审计要找的就是这些）

| 类别 | 模式 | 风险 |
| --- | --- | --- |
| ECB | `EVP_aes_256_ecb` / `Cipher.getInstance("AES")` 默认 ECB | 同明文同密文，结构泄露 |
| 静态 IV | iv 是常量、是 key 一部分、是版本号 | CBC 失语义安全；CTR/GCM 直接灾难 |
| Nonce 重用 | GCM/CTR 同 key 同 nonce 加两次 | 密钥流复用 → XOR 暴露明文 |
| 无 MAC | AES-CBC 后不带 HMAC / 仅 CRC | padding oracle、bit-flipping |
| Bleichenbacher | RSA PKCS1v15 解密区分错误 | RSA 解密 oracle |
| Padding oracle | 服务端区分 "padding 错" 与 "MAC 错" | CBC 完全可解 |
| 弱 KDF | sha1(password) / md5(password+salt) / 单轮 | 离线爆破 |
| 弱随机数 | rand() / time() 作 seed / Math.random() 作 IV | 全场景灾难 |
| 比较时序泄露 | strcmp / memcmp / String.equals 比对 MAC | 时序差打 byte-by-byte |
| 硬编码 key | 二进制里固定 32 字节 / 32 字符 hex / base64 | 拿包即拿钥 |
| 派生 key 不分用途 | 同 master key 拿来同时做加密 + 签名 | cross-protocol |

## 实战入口

- **CryptoHack** — 系统化训练所有典型误用 + 经典攻击。
- **CryptoPals** — 8 套实战题，从 base64 到 RSA Bleichenbacher 完整覆盖。
- **picoCTF / NahamCon Crypto** — 入门赛题。
- **MalwareBazaar** + 选择 ransomware 家族 — 自己抓 key 还原解密。
- **Flare-On 历年密码题** — 与逆向结合。
- **github.com/RoganDawes/HMAC-Defeated / cryptohack/Writeups** — 公开 writeup。

## 自检（拿到一段加密代码 30 分钟内回答）

1. 算法：基础 / 常见 / 自实现魔改？常量是什么？
2. 模式：ECB/CBC/GCM/CTR/CFB/OFB？是否 AEAD？
3. Key：哪来的？硬编码 / 派生 / 协商？长度？
4. IV/nonce：哪来的？是否随机？是否重用？
5. 是否带认证（MAC/AEAD tag）？认证范围对不对？
6. 输出格式：先 IV 再 ct 再 tag？base64？长度怎么算？
7. 能不能写一份 Python 等价跑出同一密文？

## 相邻技能

- `binrev` — 拿到加密函数后的反编译细节。
- `scriptrev` — JS / Java / .NET / Python pyc 里的密码学实现。
- `webrev` — 浏览器内 WebCrypto / CryptoJS / WASM 加密。
- `mrev` — Android Cipher / iOS CommonCrypto 调用链 hook。
- `protrev` — 协议帧里加密载荷的字段位置。
- `packrev` — packer 自带解密（多用 RC4 / 自定义 XOR + LZ）。
- `vmrev` — 自实现 VM 把加密做成 opcode（高强度反爬常见）。
- `fwrev` — 固件签名 / Secure Boot / 镜像加密。