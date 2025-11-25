# GitHub Action Runner

## Manual Work After Deploy


1. Create `/opt/actions-runner` directory

```commandline
sudo mkdir /opt/actions-runner
```

2. Change owner of `/opt/actions-runner` to ec2-user:

```commandline
sudo chown ec2-user:ec2-user /opt/actions-runner
```

3. Download the GitHub Actions agent to `/opt/actions-runner`:

```commandline
curl -o /opt/actions-runner/actions-runner-linux-x64-2.329.0.tar.gz -L https://github.com/actions/runner/releases/download/v2.329.0/actions-runner-linux-x64-2.329.0.tar.gz
```

4. Move into the GitHub Actions directory

```commandline
cd /opt/actions-runner
```

5. Extract the GitHub Actions runner archive:

```commandline
tar xzf /opt/actions-runner/actions-runner-linux-x64-2.329.0.tar.gz
```

6. Configure the GitHub Actions runner with the repository and secret token:

```commandline
./config.sh --url https://github.com/CMS-Enterprise/NPD --token <secret>
```

Follow the prompts. The defaults are typically fine but you should specify that the builder is meant for `dev`, `prod`, etc.

7. Start the GitHub Actions runner manually:

```commandline
./run.sh
```

8. Create a github action service using this template:

```bash
sudo tee /etc/systemd/system/github-runner.service > /dev/null <<'EOF'
[Unit]
Description=GitHub Actions Runner
After=network-online.target
Wants=network-online.target

[Service]
User=ec2-user
WorkingDirectory=/opt/actions-runner
ExecStart=/opt/actions-runner/run.sh
Restart=always
RestartSec=5s
KillMode=process
Environment=PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

[Install]
WantedBy=multi-user.target
EOF
```

9. Enable and start service

```commandline
sudo systemctl enable --now github-runner.service
```

10. Configure Docker

The build server uses Docker internally, but Docker doesn't come by default with this image. We need to install it separately.

```bash
sudo yum update -y
sudo yum install docker -y
sudo service docker start
sudo usermod -a -G docker ec2-user
sudo systemctl start docker
sudo systemctl enable docker
```

11. Install Git

GitHub Actions also uses Git to fetch resources.

```bash
sudo yum install git -y
```

12. Update the size of the root partition so GitHub Actions can use the full disk: 

Resize partition `nvme0n1p3` to fill remaining disk

```bash
sudo parted /dev/nvme0n1
(parted) print
(parted) resizepart 3 100%
(parted) quit
sudo partprobe /dev/nvme0n1
```

Resize the physical volume:

```
sudo pvresize /dev/nvme0n1p3
sudo pvs
sudo vgs
```

`nvme0n1p3` should show more free space.

Grow the root logical volume by half the remaining space:

```bash
sudo lvextend -l +50%FREE /dev/VolGroup00/rootVol
sudo xfs_growfs /
```

Grow the logical volume backing /var (where Docker stores build artifacts)  by the remaining space

```bash
sudo lvextend -l +100%FREE /dev/VolGroup00/rootVol
sudo xfs_growfs /var
```

Confirm that the output of `lsblk` shows that `VolGroup00-rootVol` and `VolGroup00-varVol` have reasonable amounts of storage.

```commandline
[ec2-user@ip-10-152-23-22 ~]$ lsblk
NAME                     MAJ:MIN RM   SIZE RO TYPE MOUNTPOINTS
nvme0n1                  259:0    0   250G  0 disk
├─nvme0n1p1              259:1    0   512M  0 part /boot/efi
├─nvme0n1p2              259:2    0     1G  0 part /boot
└─nvme0n1p3              259:3    0 248.5G  0 part
  ├─VolGroup00-rootVol   253:0    0   229G  0 lvm  /
  ├─VolGroup00-homeVol   253:1    0     3G  0 lvm  /home
  ├─VolGroup00-tmpVol    253:2    0     2G  0 lvm  /tmp
  ├─VolGroup00-varVol    253:3    0     5G  0 lvm  /var
  ├─VolGroup00-logVol    253:4    0     4G  0 lvm  /var/log
  ├─VolGroup00-auditVol  253:5    0     4G  0 lvm  /var/log/audit
  └─VolGroup00-vartmpVol 253:6    0   1.5G  0 lvm  /var/tmp
```

12. Restart the instance

```commandline
sudo reboot
```

13. In GitHub, confirm that a runner matching the IP address of the instance is live 
14. Confirm that the github-runner.service is loaded and active in systemd 

```commandline
sh-5.2$ sudo systemctl status github-runner.service
● github-runner.service - GitHub Actions Runner
     Loaded: loaded (/etc/systemd/system/github-runner.service; enabled; preset: disabled)
     Active: active (running) since Tue 2025-10-28 15:34:31 EDT; 9min ago
   Main PID: 2543 (run.sh)
      Tasks: 14 (limit: 18894)
     Memory: 115.7M
        CPU: 3.879s
     CGroup: /system.slice/github-runner.service
             ├─2543 /bin/bash /opt/actions-runner/run.sh
             ├─2593 /bin/bash /opt/actions-runner/run-helper.sh
             └─2598 /opt/actions-runner/bin/Runner.Listener run

Oct 28 15:36:41 ip-10-204-107-24.ec2.internal run.sh[2598]: Current runner version: '2.329.0'
Oct 28 15:36:41 ip-10-204-107-24.ec2.internal run.sh[2598]: 2025-10-28 19:36:41Z: Listening for Jobs
```

15. Confirm that github-runner.service is configured and connecting to GitHub.

```
journalctl -u github-runner.service -f
[ec2-user@ip-10-152-23-22 bin]$ journalctl -u github-runner.service -f
Nov 25 12:10:52 ip-10-152-23-22.ec2.internal run.sh[2594]: √ Connected to GitHub
Nov 25 12:10:52 ip-10-152-23-22.ec2.internal run.sh[2594]: A session for this runner already exists.
Nov 25 12:11:23 ip-10-152-23-22.ec2.internal run.sh[2594]: √ Connected to GitHub
Nov 25 12:11:23 ip-10-152-23-22.ec2.internal run.sh[2594]: A session for this runner already exists.
Nov 25 12:11:54 ip-10-152-23-22.ec2.internal run.sh[2594]: √ Connected to GitHub
Nov 25 12:11:55 ip-10-152-23-22.ec2.internal run.sh[2594]: A session for this runner already exists.
Nov 25 12:12:25 ip-10-152-23-22.ec2.internal run.sh[2594]: √ Connected to GitHub
Nov 25 12:12:26 ip-10-152-23-22.ec2.internal run.sh[2594]: 2025-11-25 17:12:26Z: Runner reconnected.
Nov 25 12:12:26 ip-10-152-23-22.ec2.internal run.sh[2594]: Current runner version: '2.329.0'
Nov 25 12:12:26 ip-10-152-23-22.ec2.internal run.sh[2594]: 2025-11-25 17:12:26Z: Listening for Jobs
```