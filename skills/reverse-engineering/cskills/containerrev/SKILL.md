---
name: container-artifact-reverse-engineering
description: 容器镜像与运行时制品逆向。OCI / Docker / containerd / podman / CRI-O 镜像格式、layer 解析、SBOM 提取、distroless / chainguard 识别、buildah / kaniko 产物、Kubernetes Pod / ConfigMap / Secret 取证、namespace / cgroup / capabilities / seccomp / AppArmor 隔离面、容器逃逸面识别（CVE-2019-5736 等）。配合 fwrev / cloudrev / linuxrev 用。
---

# 容器制品逆向

## 适用场景

- 拿到一个 Docker / OCI 镜像，要回答："里面装了什么？哪一层是恶意 / 后门 / 异常的？挖矿、反弹 shell 在哪？SBOM 是什么？基于哪个基础镜像？"
- 镜像供应链审计：第三方公司送来的镜像准备生产部署前，做静态扫描 + 取证。
- 镜像内某二进制做 binrev，但要先把镜像、层、配置剥开。
- Kubernetes 集群取证：从节点拷出来的 container snapshot / pod tar / containerd 数据目录还原。

## 不适用

- 镜像内单个 ELF/PE 函数级深挖 → `binrev`。
- 镜像内 Linux 运行生态（systemd / sysctl / 内核接口） → `linuxrev`。
- 云端 Agent / 边缘组件 → `cloudrev`。

## OCI 镜像格式速查

```text
镜像 = 一个 tarball，结构（OCI Image Format Spec）：
  manifest.json                # 顶级清单（多镜像 / 多平台）
  index.json                   # OCI 入口
  blobs/
    sha256/
      <digest>                 # 每个 blob：可能是 config / layer / manifest
  oci-layout                   # 标记: {"imageLayoutVersion":"1.0.0"}

每个镜像 = manifest + config + N 个 layer
  manifest:
    "config": { "digest": "sha256:..." },     # 指向 image config
    "layers": [
      { "digest": "sha256:...", "mediaType": "application/vnd.oci.image.layer.v1.tar+gzip" },
      ...                                       # 按 build 顺序
    ]
  config:
    "architecture", "os", "config" (entrypoint/cmd/env/user/exposed_ports/volumes),
    "rootfs": { "diff_ids": [...] },           # 解压后每层 sha256
    "history": [{ "created", "created_by", ... }]   # build 命令历史

每层 = tarball, 解压后是 rootfs 的 overlay diff
最终 rootfs = layer1 + layer2 + ... overlay 累加，删除用 .wh.<file> whiteout 标记
```

## 拆包工具链

```bash
# 从 registry / Docker daemon 拉
docker pull alpine:3.20
docker save alpine:3.20 -o alpine.tar
docker image inspect alpine:3.20

# 不依赖 docker daemon
skopeo copy docker://alpine:3.20 oci-archive:/tmp/alpine.oci
skopeo inspect docker://alpine:3.20
skopeo list-tags docker://docker.io/library/alpine

crane manifest alpine:3.20
crane config alpine:3.20
crane export alpine:3.20 - | tar -tv | head    # 把所有 layer 合并解出
crane pull alpine:3.20 alpine.tar --format=oci
crane append -f myfile.tar -b alpine:3.20 -t myrepo:tag    # 追加层

# 解开 docker save 出的 tarball
mkdir -p img && tar -xf alpine.tar -C img
cat img/manifest.json | jq
ls img/blobs/sha256/                            # 各层

# 用 dive 交互查看每一层增删
dive alpine:3.20

# 单层解开
mkdir -p layer && tar -xzf img/blobs/sha256/<layer-digest> -C layer

# 把整个镜像扁平化成 rootfs（合并所有层 + 处理 whiteout）
docker create --name tmp alpine:3.20
docker export tmp -o rootfs.tar
docker rm tmp
mkdir rootfs && tar -xf rootfs.tar -C rootfs

# undocker（独立工具）
undocker alpine.tar -i 0 -o rootfs.tar
```

## 镜像扫描 / SBOM / 漏洞

```bash
# trivy: 漏洞 + secret + license + IaC 一站式
trivy image alpine:3.20
trivy image --format json --output report.json alpine:3.20
trivy image --severity CRITICAL,HIGH alpine:3.20
trivy image --scanners vuln,secret,config,license alpine:3.20

# grype: Anchore 出品的漏洞扫描
grype alpine:3.20
grype alpine:3.20 -o json

# syft: SBOM 生成（CycloneDX / SPDX）
syft alpine:3.20 -o cyclonedx-json > sbom.json
syft alpine:3.20 -o spdx-json
syft packages dir:./rootfs                       # 直接扫目录

# clair: 老牌但仍在用
clairctl analyze alpine:3.20

# docker scout（Docker 自家）
docker scout cves alpine:3.20
docker scout recommendations alpine:3.20

# diffoscope: 对比两版镜像
diffoscope alpine:3.19 alpine:3.20

# Anchore engine：完整服务化扫描，含 policy gate
anchore-cli image add alpine:3.20
anchore-cli image vuln alpine:3.20 all
```

## 基础镜像与编译特征识别

```bash
# 看 history（最快）
docker history --no-trunc alpine:3.20
crane config alpine:3.20 | jq '.history'

# 典型基础镜像签名
ls rootfs/etc/os-release
cat rootfs/etc/os-release           # NAME="Alpine Linux" / Debian / Ubuntu / CentOS / RHEL / Wolfi
cat rootfs/etc/alpine-release       # Alpine 版本
cat rootfs/etc/debian_version
ls rootfs/lib/                       # libc 类型: musl-libc-x.y / libc-2.x.so / glibc

# Distroless 识别
ls rootfs/                           # 只有 /etc /var /usr/bin/<binary> 几乎没 shell
ls rootfs/bin/sh /bin/bash 2>/dev/null   # distroless 里没有
file rootfs/etc/passwd               # 经典 distroless 就 nobody/root 几个

# Wolfi (Chainguard) 识别
ls rootfs/etc/wolfi-release
cat rootfs/etc/apk/repositories       # 含 wolfi-base
ls rootfs/var/lib/db/sbom/            # Chainguard 默认带 SBOM 文件

# Scratch 镜像（什么都没有）
ls rootfs/                            # 只有用户的 binary

# Buildpacks / paketo
ls rootfs/cnb/                        # Cloud Native Buildpacks 标志
cat rootfs/layers/config/metadata.toml
```

## 异常 / 后门检测面

```bash
# 1) 寻找异常的 ENTRYPOINT / CMD
docker image inspect alpine:3.20 | jq '.[0].Config.Entrypoint, .[0].Config.Cmd'
crane config img:tag | jq '.config.Entrypoint, .config.Cmd'

# 2) 检查所有可执行文件
find rootfs -type f -executable -not -path '*/proc/*' | head -50
find rootfs -type f -executable -not -path '*/proc/*' -exec file {} \; | grep -i ELF

# 3) 寻找异常文件
find rootfs -name "*.sh" | xargs grep -lE 'curl|wget|nc -|bash -i|/dev/tcp' 2>/dev/null
find rootfs -name 'authorized_keys' -o -name 'id_rsa' 2>/dev/null
find rootfs -path '*/.ssh/*'
find rootfs -newer alpine.tar 2>/dev/null         # 比基础镜像新的文件
find rootfs -size +50M                             # 异常大文件

# 4) 检查 cron / systemd / init
find rootfs/etc/cron* rootfs/var/spool/cron rootfs/etc/systemd 2>/dev/null
cat rootfs/etc/crontab 2>/dev/null

# 5) 检查 setuid / setgid
find rootfs -type f \( -perm -4000 -o -perm -2000 \) -exec ls -la {} \; 2>/dev/null

# 6) 反弹 shell / 挖矿常见特征
grep -RE 'xmrig|monero|stratum\+tcp|bash -i|nc -e|dev/tcp/' rootfs/ 2>/dev/null | head -20
strings rootfs/usr/bin/* 2>/dev/null | grep -iE 'xmrig|stratum|cryptonight|donate' | head

# 7) 时间戳异常（Reproducible Builds 视角）
find rootfs -newer rootfs/etc/os-release -ls 2>/dev/null | head
ls -la --full-time rootfs/usr/bin/ | head

# 8) 用 capa 扫所有 ELF
for bin in $(find rootfs -type f -executable); do
    if file "$bin" | grep -q ELF; then
        capa "$bin" --json 2>/dev/null
    fi
done | jq -s 'map(select(.matches | length > 0))'
```

## 容器逃逸面识别（看，不打）

```text
1) 高权限挂载
   - hostPath / privileged 容器
   - 挂载 /proc /sys /var/run/docker.sock 进容器
   - 挂载宿主 /

2) 特权 capabilities
   - CAP_SYS_ADMIN / CAP_NET_ADMIN / CAP_SYS_PTRACE
   - 能 mount / 能改 cgroup / 能 ptrace 宿主进程

3) 默认能力组（看 cap.h）：
   常驻: CAP_AUDIT_WRITE, CAP_CHOWN, CAP_DAC_OVERRIDE, CAP_FOWNER, CAP_FSETID,
        CAP_KILL, CAP_MKNOD, CAP_NET_BIND_SERVICE, CAP_NET_RAW, CAP_SETFCAP,
        CAP_SETGID, CAP_SETPCAP, CAP_SETUID, CAP_SYS_CHROOT
   危险: CAP_SYS_ADMIN, CAP_SYS_MODULE, CAP_SYS_RAWIO, CAP_SYS_PTRACE,
        CAP_NET_ADMIN, CAP_DAC_READ_SEARCH, CAP_AUDIT_CONTROL, CAP_BPF

4) 已知 CVE 类（识别用，不展开）
   - CVE-2019-5736  (runc 写 /proc/self/exe)
   - CVE-2022-0185  (kernel filesystem context UAF)
   - CVE-2022-0492  (cgroup release_agent)
   - CVE-2022-23222 (kernel BPF verifier 类型混淆)
   - CVE-2024-21626 (runc 文件描述符泄露 → leaky vessels)

5) 查看运行时
   ps -ef | grep -E 'containerd|runc|crun|kata'
   crictl info / crictl ps                  # CRI-O / containerd 都有
   ctr -n k8s.io containers list             # containerd
   nerdctl ps                                 # containerd 客户端
   podman ps / podman inspect

6) 看挂载视图
   cat /proc/self/mountinfo
   findmnt
   mount | head
```

## Kubernetes Pod / Cluster 取证

```bash
# Pod 描述与配置
kubectl get pod <name> -o yaml > pod.yaml
kubectl get cm,secret -A -o yaml                  # 全部 ConfigMap / Secret
kubectl describe pod <name>

# 节点上 containerd / docker 数据目录
ls /var/lib/containerd/io.containerd.content.v1.content/blobs/sha256/
ls /var/lib/docker/overlay2/
ls /var/lib/kubelet/pods/<podUID>/

# Pod 网络命名空间
ls -la /proc/$(crictl inspect <id> | jq -r .info.pid)/ns/

# RBAC + ServiceAccount token
cat /var/run/secrets/kubernetes.io/serviceaccount/token
cat /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
cat /var/run/secrets/kubernetes.io/serviceaccount/namespace
# 所有 Pod 默认拿到自家 SA token，能调 API server

# kubectl-trace / kubectl-debug：在 Pod 里跑 bpftrace / 调试容器
kubectl debug node/<node> -it --image=ubuntu
kubectl debug pod/<pod> -it --image=alpine --target=<container>
kubectl-trace run node/<node> -e 'tracepoint:syscalls:sys_enter_openat { printf("%s\n", str(args->filename)); }'

# 镜像源审计（哪些 registry 被许可）
cat /etc/containers/registries.conf
cat /etc/containerd/config.toml
```

## 镜像签名 / 验证

```text
内容寻址 (Content Addressable)：
  digest = sha256(manifest 的 JSON)
  manifest 内嵌 layer + config 各自 sha256
  改任一字节 → digest 变 → 验证就失败

签名方案：
1) Docker Content Trust (DCT) / Notary v1: TUF, 已老
2) Sigstore / cosign: 现代标准
   cosign sign --key cosign.key example.com/img:tag
   cosign verify --key cosign.pub example.com/img:tag
   cosign verify-attestation
3) Notary v2 / OCI artifact-spec referrer
4) Red Hat Simple Signing (基于 GPG)

验证命令:
crane manifest --platform=linux/amd64 image:tag | sha256sum
cosign verify image:tag --certificate-identity-regexp '...' --certificate-oidc-issuer-regexp '...'
```

## 实战入口

- **Container Security (Liz Rice, O'Reilly)** — 系统化教材。
- **kube-hunter / kube-bench / kubesec** — 集群审计工具，看它们检查啥就知道攻击面在哪。
- **trivy-action / Snyk Container Hub / Aqua / Sysdig blog** — 大量真实事件分析。
- **HackTricks Cloud / Kubernetes Goat** — 靶场。
- **Falco / Tracee / Tetragon** — 运行时检测，看规则学攻击模式。
- **CTF: PicoCTF Container / DEFCON Cloud Village**。

## 自检（拿到镜像 30 分钟内回答）

1. 镜像 digest？manifest 类型（OCI / Docker v2 / V2.2）？多平台？
2. 基础镜像（alpine / debian / ubuntu / distroless / wolfi / scratch）？版本？
3. 几层？最大一层多少字节？是否有"巨厚一层"提示一次性把恶意码塞进来？
4. ENTRYPOINT / CMD / USER（是否 root 跑）？暴露端口？挂载卷？
5. SBOM 出来后高危 CVE 数？是否含明显未补的漏洞？
6. 是否有签名（cosign / DCT）？签名身份是否可信？
7. 异常文件 / 异常 cron / 异常 setuid / 反弹 shell / 挖矿字符串扫一遍是否清白？

## 相邻技能

- `binrev` — 镜像内 ELF 函数级深挖。
- `linuxrev` — 容器内 Linux 运行生态、systemd、syscall 边界。
- `cloudrev` — 云端配套 Agent / Sidecar。
- `fwrev` — 嵌入式 / IoT 容器化趋势（Balena / k3s on edge）。
- `cryptrev` — cosign / DCT 签名机制与 root key。
- `sdkrev` — 云 SDK 嵌入到镜像里的二进制。
- `protrev` — 镜像传输协议（OCI distribution spec / registry push/pull）。
- `iotrev` — IoT 边缘容器（Balena / KubeEdge）。
- `mrev` — Android 容器（不同语义但镜像类似 OCI 格式）。