---
name: reverse-engineering-lab-infrastructure
description: 逆向安全实验室基础设施。VM 编排（Proxmox / ESXi / VirtualBox / Hyper-V / QEMU/KVM）；现成镜像（FLARE-VM / REMnux / SIFT / CommandoVM / Tsurugi）；网络隔离（host-only / NAT / sinkhole INetSim/FakeNet-NG）；快照策略；IaC（Vagrant / Packer / Terraform / Ansible / Nix）；安全 / 隔离（Firejail / bubblewrap / Qubes）；团队工具（MISP / TheHive / Cortex / Velociraptor）。
---

# 逆向 / 安全实验室基础设施

## 适用场景

- 搭建团队级 / 个人逆向工作环境：从干净基线 → 工具栈 → 网络隔离 → 快照 → 证据导出。
- 让分析师无需重复劳动，开 VM 就直接有 IDA / Ghidra / Frida / Wireshark / volatility 全套。
- 受控网络环境：让恶意样本以为联网，实际走 sinkhole。
- IaC：实验室全部可重建（disaster recovery）。
- 团队协作：MISP / TheHive / Velociraptor 三件套支持事件共享。

## 不适用

- 单个样本分析方法 → 各专项技能。
- 自动化分析流水线 → `revauto`。
- 报告交付规范 → `rev-report`。

## VM 平台选型

| 平台 | 适合 | 优势 |
| --- | --- | --- |
| **VMware Workstation Pro / Fusion** | 个人桌面 | snapshot 快、对 Windows 优化 |
| **VMware ESXi / vSphere** | 团队私有云 | 企业级，但收费 |
| **Proxmox VE** | 团队 + 自托管 | 开源，整合 KVM + LXC + Web UI |
| **VirtualBox** | 入门 / 跨平台 | 完全免费 |
| **Hyper-V** | Windows 主机 | 与 Windows / WSL2 / Sandbox / Defender Sandbox 集成 |
| **QEMU/KVM (libvirt)** | Linux 主机 + 大规模 | 性能最好 + IaC 友好 |
| **Parallels Desktop** | macOS 上跑 Win/Linux | M 芯片 ARM Windows 兼容性最好 |
| **UTM** | macOS Apple Silicon | 免费的 Parallels 替代 |
| **Xen** | 极端隔离 / DRAKVUF | agentless 监控 |
| **Qubes OS** | 最严隔离工作站 | 每个应用一个 VM |
| **WSL2** | Windows 桌面 + Linux tools | 不适合恶意样本（共享内核） |

## 现成镜像（最快上手）

```text
Windows 分析:
  FLARE-VM (Mandiant)         脚本套件，往 Windows 10/11 干净系统装 200+ 工具
  https://github.com/mandiant/flare-vm
  CommandoVM (FireEye → Mandiant) — 红队向, 已弃, 用 FLARE-VM

Linux 分析 / DFIR:
  REMnux                       现成 .ova，专做恶意 Linux 样本
  https://remnux.org
  SIFT Workstation (SANS)      现成 .ova，DFIR 专用
  https://www.sans.org/tools/sift-workstation/
  Tsurugi Linux                现成镜像，DFIR + OSINT
  https://tsurugi-linux.org
  Kali Linux                   通用 pentest，含部分 RE 工具
  ParrotOS Security            类似 Kali

取证专项:
  CAINE                        意大利 DFIR distro
  DEFT Linux                   类 SIFT

Mac 分析:
  Mac 无现成 distro，自家组装:
    brew install hopper / cutter / radare2 / ghidra / lldb / Frida
    Xcode + Additional Tools (含 PacketLogger / Configurator)
```

## FLARE-VM 一键装

```powershell
# 干净 Windows 10/11 VM 内 (admin PowerShell)
Set-ExecutionPolicy Unrestricted -Force
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
(New-Object net.webclient).DownloadFile(
    'https://raw.githubusercontent.com/mandiant/flare-vm/main/install.ps1',
    'install.ps1')

# 看脚本内容确认安全后跑
.\install.ps1

# 装完含:
#   静态: IDA Free / Ghidra / Cutter / x64dbg / dnSpyEx / dotPeek / PE-bear / Detect It Easy
#   动态: ProcMon / API Monitor / TCPView / Wireshark / Burp Suite
#   恶意: pestudio / floss / capa / yara / oledump / oletools / box-js
#   脚本: Python / pip / Frida / Cuckoo agent / Sysmon + SwiftOnSecurity config
#   工具: Sysinternals 全套 / Autoruns / ProcExp / 7-Zip / Notepad++ / VSCode
#   网络: FakeNet-NG / INetSim 客户端

# 后续更新工具
choco upgrade all -y                                          # FLARE-VM 用 chocolatey 管包
```

## REMnux 一键起

```bash
# 下 .ova → VirtualBox / VMware 导入
# 或在已有 Ubuntu 上转换
wget https://REMnux.org/remnux-cli
chmod +x remnux-cli
sudo mv remnux-cli /usr/local/bin/remnux
sudo remnux install                                          # 转 Ubuntu → REMnux

# REMnux 含 700+ 工具，按类别有 alias
remnux info                                                  # 概览
remnux upgrade
remnux update-tool capa
remnux list-tools                                            # 全部
remnux info volatility3
remnux info oletools
```

## QEMU/KVM + libvirt（Linux 主机最优方案）

```bash
# 装
sudo apt install qemu-system-x86 qemu-utils libvirt-daemon-system virt-manager virtinst

# 加自己到 libvirt 组
sudo usermod -aG libvirt,kvm $USER

# 启动 daemon
sudo systemctl enable --now libvirtd

# GUI: virt-manager
virt-manager

# CLI: virsh
virsh list --all
virsh start win10-vm
virsh shutdown win10-vm
virsh snapshot-create-as win10-vm clean-base
virsh snapshot-list win10-vm
virsh snapshot-revert win10-vm clean-base

# 创建 VM (CLI)
virt-install \
    --name win10-vm \
    --memory 8192 --vcpus 4 \
    --disk path=/var/lib/libvirt/images/win10.qcow2,size=80 \
    --cdrom /isos/Win10.iso \
    --os-variant win10 \
    --network network=isolated \
    --graphics spice

# 网络配置（隔离 + sinkhole）
sudo virsh net-define isolated.xml
sudo virsh net-start isolated
sudo virsh net-autostart isolated
```

```xml
<!-- isolated.xml: host-only 网络 -->
<network>
  <name>isolated</name>
  <bridge name='virbr-iso' stp='on' delay='0'/>
  <ip address='10.99.99.1' netmask='255.255.255.0'>
    <dhcp>
      <range start='10.99.99.10' end='10.99.99.99'/>
    </dhcp>
  </ip>
  <!-- 没有 <forward> = 完全隔离, 不能访问外网 -->
</network>
```

## Proxmox VE（团队场景）

```bash
# 装在物理服务器上 (Debian 12 base)
wget https://download.proxmox.com/iso/proxmox-ve_8.x.iso
# U 盘启动 → 完整 hypervisor

# Web UI: https://<host>:8006
# CLI: pveam / qm / pct

# 创建 VM
qm create 100 \
    --name win10-analyst \
    --memory 8192 --cores 4 \
    --net0 virtio,bridge=vmbr1 \
    --scsi0 local-lvm:80 \
    --cdrom local:iso/Win10.iso \
    --ostype win10

qm start 100
qm snapshot 100 clean-base
qm rollback 100 clean-base

# 模板化（每个分析师拿快照克隆）
qm clone 100 200 --name win10-flare-template --full
qm template 200                                              # 标记为模板

# 克隆给具体分析师
qm clone 200 201 --name analyst-alice
qm clone 200 202 --name analyst-bob

# 网络: 自家 sinkhole VM
# vmbr0 (外网) → admin VM
# vmbr1 (隔离) → 恶意分析 VM
# 在隔离网中跑 INetSim/FakeNet-NG VM, 把所有 DNS/HTTP/SMTP/IRC 答给假数据
```

## 网络隔离 + Sinkhole

```bash
# INetSim (经典恶意软件 sinkhole)
sudo apt install inetsim
sudo vim /etc/inetsim/inetsim.conf
# 启用服务:
#   dns
#   http
#   https
#   smtp
#   smtps
#   pop3
#   ftp
#   irc
#   ntp
sudo inetsim                                                 # 启动
# log 位置: /var/log/inetsim/

# FakeNet-NG (Mandiant, Python + 灵活)
pip install fakenet-ng
sudo fakenet                                                 # 一键 hijack 所有出口流量
# 配置 fakenet.ini 自定义假响应

# DNS sinkhole
# Pi-hole / Unbound + zone file
echo '*.example.com.    IN    A    10.99.99.50' >> /etc/unbound/local-data.conf

# 配合 mitmproxy 抓 TLS
mitmproxy --mode transparent --listen-port 8080 --ssl-insecure
# iptables / pf 把 80/443 重定向到 mitmproxy

# WireGuard 隔离 + 跳板
# 实验室出口走自己 VPN, 防止厂房默认 SOCKS 泄漏
sudo wg-quick up vpn
ip route show
```

## 快照策略（必须）

```text
逐层快照, 层级清晰:

1) clean-base
   - 装完系统 + 全部更新 + 关防火墙 / 自动更新 / 自动登录
   - 不装任何工具
   - "原始系统" 快照, 永远保留

2) tools-base
   - 在 clean-base 之上装 FLARE-VM / REMnux / 自家工具栈
   - 装完后快照
   - 用于团队复制 / 升级工具时回滚

3) per-engagement (每次分析任务):
   3.1) pre-sample
        从 tools-base 克隆, 设网络隔离, 准备样本目录
        快照: "engagement-X-clean"
   3.2) post-static
        做完静态分析后快照
        快照: "engagement-X-static-done"
   3.3) post-dynamic
        跑完动态后快照 (保留运行状态)
        快照: "engagement-X-dynamic-done"
   3.4) evidence-export
        证据导出完毕 + VM 状态归档后
        销毁 VM

回滚命令 (libvirt):
virsh snapshot-list vm-name
virsh snapshot-revert vm-name clean-base
virsh snapshot-delete vm-name engagement-x-clean
```

## IaC：完全 reproducible 实验室

```bash
# Packer: 用脚本自动从 .iso 装出基线镜像
# packer-win10-flare.json
{
  "builders": [{
    "type": "virtualbox-iso",
    "iso_url": "Win10.iso",
    "iso_checksum": "sha256:...",
    "vm_name": "win10-flare-base",
    "memory": 8192,
    "cpus": 4,
    "guest_os_type": "Windows10_64",
    "ssh_username": "analyst",
    "ssh_password": "analyst",
    "boot_command": [...],
    "shutdown_command": "shutdown /s /t 0",
    "headless": true
  }],
  "provisioners": [
    {
      "type": "powershell",
      "scripts": ["scripts/install-flare.ps1"]
    }
  ]
}
packer build packer-win10-flare.json
```

```bash
# Vagrant: 用现成 box 起 VM
# Vagrantfile
Vagrant.configure("2") do |config|
  config.vm.box = "remnux/v7"
  config.vm.network "private_network", ip: "10.99.99.20"
  config.vm.provider "virtualbox" do |v|
    v.memory = 8192
    v.cpus = 4
  end
end
vagrant up
vagrant ssh
vagrant snapshot save clean-base
vagrant snapshot restore clean-base
```

```bash
# Terraform + libvirt provider
terraform init
cat <<EOF > main.tf
terraform {
  required_providers {
    libvirt = { source = "dmacvicar/libvirt" }
  }
}
resource "libvirt_volume" "win10" {
  name = "win10-vm.qcow2"
  source = "/isos/win10-base.qcow2"
  format = "qcow2"
}
resource "libvirt_domain" "win10_analyst" {
  name = "analyst-${var.alias}"
  memory = "8192"
  vcpu = 4
  disk { volume_id = libvirt_volume.win10.id }
  network_interface { network_name = "isolated" }
}
EOF
terraform apply
```

```bash
# Ansible: 配置已有 VM
# inventory.ini
[analyst_vms]
10.99.99.10 ansible_user=analyst

# playbook.yml
- hosts: analyst_vms
  tasks:
    - name: Install FLARE-VM tools
      win_chocolatey: name={{ item }} state=present
      with_items: [idafree, ghidra, x64dbg, dnspy, processhacker, sysinternals]
    - name: Disable Defender
      win_shell: Set-MpPreference -DisableRealtimeMonitoring $true
ansible-playbook -i inventory.ini playbook.yml
```

```nix
# Nix Flake: 完全声明式工具栈 (Linux/macOS)
# flake.nix
{
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-23.11";
  outputs = { self, nixpkgs }: {
    devShells.x86_64-linux.default = nixpkgs.legacyPackages.x86_64-linux.mkShell {
      buildInputs = with nixpkgs.legacyPackages.x86_64-linux; [
        ghidra cutter radare2 binwalk yara capa
        wireshark mitmproxy volatility3
        python3.withPackages (p: [ p.pefile p.lief p.frida-tools ])
      ];
    };
  };
}
nix develop                                                   # 进入完整环境
```

## 单机隔离：Firejail / bubblewrap / Sandbox-Exec

```bash
# Firejail: 用户态沙箱（Linux）
firejail --net=none --private --read-only=/usr ./suspect_binary
firejail --x11 --net=none --whitelist=/tmp/sandbox firefox
firejail --profile=/etc/firejail/firefox.profile firefox

# bubblewrap (Flatpak 底层)
bwrap --ro-bind / / \
      --tmpfs /tmp \
      --proc /proc \
      --dev /dev \
      --unshare-all \
      ./suspect_binary

# 自家沙箱 profile
cat > my-sandbox.profile <<EOF
include /etc/firejail/disable-common.inc
include /etc/firejail/disable-programs.inc
net none
private
private-tmp
private-dev
caps.drop all
seccomp
nonewprivs
noroot
EOF

# Windows Sandbox (Windows 10/11 Pro+)
# Settings → Apps → Optional features → Windows Sandbox
# 启动后是一次性 VM, 关闭即销毁
# 配置: .wsb 文件 (XML)
<Configuration>
  <vGPU>Disable</vGPU>
  <Networking>Disable</Networking>
  <MappedFolders>
    <MappedFolder>
      <HostFolder>C:\samples</HostFolder>
      <ReadOnly>true</ReadOnly>
    </MappedFolder>
  </MappedFolders>
</Configuration>

# macOS sandbox-exec (老)
sandbox-exec -f profile.sb ./suspect_binary
# Apple 不再维护，新方案: App Sandbox + Hardened Runtime + XPC
```

## Qubes OS（极端隔离）

```text
特点: 整个工作站每个 app 一个 VM
适合: 高敏分析师 / 处理高威胁样本

架构:
  dom0: 控制虚拟机, 极小, 不联网
  sys-net: 处理所有网络 (单独 VM)
  sys-firewall: 网络过滤
  sys-usb: 处理 USB 设备
  
工作 VM:
  personal: 日常 (邮件 / 文档)
  work: 工作敏感
  vault: 离线密码 / Keepass
  red: 红队工具
  blue: 蓝队分析
  disposable VMs: 一次性, 每次开一个新, 关闭销毁

启动 disposable VM:
qvm-run --dispvm=fedora-39-dvm xterm

文件传输:
qvm-copy file.txt              # 触发 GUI 选 destination VM, 不能被 source VM 阻止
qvm-open-in-vm work@gmail.com  # 在 work VM 打开附件

下载: qubes.com/intro
```

## 团队工具栈

| 角色 | 工具 | 备注 |
| --- | --- | --- |
| **事件管理** | TheHive | 现代化 SOAR-ish |
| **IOC 共享** | MISP | 标准化 STIX2 / 平台对接 |
| **自动化分析** | Cortex | 给 TheHive 提供 analyzer |
| **威胁情报平台** | OpenCTI | knowledge graph + STIX2 |
| **DFIR / 远程 hunt** | Velociraptor (Rapid7 fork) | agent-based, 速度快 |
| **EDR / 终端取证** | osquery + Fleet | 轻量替代 |
| **沙箱** | CAPE / Cuckoo3 / DRAKVUF | 见 `revauto` |
| **协作文档** | Confluence / GitLab Wiki | 报告与 SOP 沉淀 |
| **聊天 + 告警** | Slack / Mattermost / Teams | + webhook 集成 |

```bash
# TheHive + Cortex + MISP docker-compose
git clone https://github.com/TheHive-Project/Docker-Templates
cd Docker-Templates/docker
docker-compose up -d
# 默认账号 admin@thehive.local / secret
# Web: http://localhost:9000

# Velociraptor
velociraptor --config server.config.yaml frontend &
velociraptor --config client.config.yaml client &
# Web: https://localhost:8889
```

## 工具版本固定 / 离线包缓存

```bash
# 防止某天 GitHub down / 工具被删 → 自家缓存
mkdir -p /opt/tools-cache/{deb,rpm,pip,npm}

# Debian
apt-mirror                                                    # 同步本地源
# 或 squid-deb-proxy 做缓存代理

# RHEL
reposync --download_path=/opt/tools-cache/rpm

# Python
pip download -r requirements.txt -d /opt/tools-cache/pip
# 离线安装: pip install --no-index --find-links=/opt/tools-cache/pip -r requirements.txt

# Node
npm pack <pkg>                                                # 拿 .tgz
# verdaccio: 自家 npm 缓存代理

# Docker
docker save image:tag -o image.tar
docker load -i image.tar

# Artifactory / Nexus / Harbor: 企业级缓存

# IDA / Hex-Rays 等商业: license server + 内网镜像
```

## 凭据管理

```bash
# 实验室凭据集中存
# Vault (HashiCorp) - 最强, 但重
vault server -dev
vault kv put secret/lab/ida-license value="..."

# Bitwarden / Vaultwarden (轻量, 自托管)
docker run -d --name vaultwarden -v ./data:/data -p 8000:80 vaultwarden/server

# 1Password / LastPass / KeePass team
# pass (Unix passwordstore)
pass init <gpg-key>
pass insert lab/jira-token
pass lab/jira-token

# 不要在 Git 仓库里放凭据 - 用 git-secret / SOPS 加密
sops --encrypt --in-place secrets.yaml
```

## 实战参考拓扑

```text
                ┌──────────────────┐
                │  Internet         │
                └────────┬─────────┘
                         │
                ┌────────▼─────────┐
                │  Edge Firewall    │   (DMZ 出口)
                │  pfSense / OPNsense│
                └────────┬─────────┘
                         │
       ┌─────────────────┼─────────────────┐
       │                 │                 │
  ┌────▼────┐      ┌─────▼─────┐    ┌─────▼─────┐
  │ Admin   │      │ Tools     │    │ Sample    │
  │ VLAN    │      │ Servers   │    │ Lab VLAN  │
  │ (RDP/   │      │ (TheHive/ │    │ (隔离)    │
  │  SSH)   │      │  MISP/    │    │           │
  └─────────┘      │  Vault)   │    └─────┬─────┘
                   └───────────┘          │
                                  ┌───────▼─────────┐
                                  │  Sinkhole VM     │
                                  │  (INetSim+pihole│
                                  │  +mitmproxy)     │
                                  └─────────────────┘
                                          │
                                  ┌───────▼─────────┐
                                  │  Analyst VMs    │
                                  │  FLARE-VM /     │
                                  │  REMnux / SIFT  │
                                  └─────────────────┘

数据流:
- 样本通过 单向 transfer 进 Sample Lab VLAN
- 不与 Admin VLAN 互通
- 分析师从 Admin VLAN 通过专门 jump host SSH/RDP 进 Analyst VMs
- 报告导出经过 PGP 加密 → Tools Server (TheHive) 落地
```

## 实战入口

- **FLARE-VM / REMnux / SIFT 官方文档**：装好就是分析师。
- **The DFIR Report 实验室搭建指南**。
- **SANS FOR526 / FOR578 / FOR508**：实验室方法论。
- **Practical Malware Analysis 第 2 章 (Lab setup)**。
- **Mandiant lab post / SentinelLabs lab post**：企业级参考。
- **awesome-malware-analysis / awesome-pentest GitHub**：工具索引。
- **Qubes OS docs**：极端隔离参考。
- **HashiCorp Packer / Vagrant / Terraform docs**：IaC 入门。
- **Ansible for DevOps**：自动化配置参考书。
- **Velociraptor / TheHive / MISP / OpenCTI 官方文档**。

## 自检（搭实验室前 30 分钟回答）

1. 团队规模？同时几个分析师？要不要多租户隔离？
2. 硬件预算（笔记本上跑 VM vs 自建服务器 vs 云）？
3. VM 平台选型（KVM / ESXi / Proxmox / VirtualBox / Hyper-V）？
4. 用 FLARE-VM / REMnux 现成镜像还是完全自家组装？
5. 网络隔离策略（host-only / NAT / 完全断网 / sinkhole / 内网跳板）？
6. 快照策略（几层 / 多久清理）？
7. IaC 工具（Packer / Vagrant / Terraform / Ansible / Nix）？
8. 团队工具栈（TheHive / MISP / Velociraptor / 自家）？
9. 凭据 / 工具 license 管理方式？
10. 灾备 / 镜像缓存（内网 apt / pip / npm / Docker 镜像）？

## 相邻技能

- `revauto` — 实验室之上的自动化流水线。
- `rev-report` — 报告交付与证据归档规范。
- `malrev` — 实验室主要用户场景之一。
- `memrev` — Volatility / Velociraptor 跑在实验室。
- `fuzzrev` — 实验室 fuzz 集群。
- `containerrev` / `cloudrev` — 云上 / 容器化实验室部署。
- `mrev` — 移动分析需要的 Android / iOS 设备农场。
- `iotrev` / `hwrev` — 硬件 / 设备实验室（与本技能软件层互补）。
- `debugrev` — 调试器联机配置（kd-net / gdbserver）。
- `protrev` — 实验室内的网络抓包基础设施。