# GitHub Action Runner

## Manual Work After Deploy

1. Get GitHub self-hosted runner script from GitHub
2. Install on instance
3. cp to /opt/actions-runner
4. give ec2-user ownership of /opt/actions-runner

```bash
sudo chown -R ec2-user:ec2-user /opt/actions-runner
```

5. Create a github action service using this template:

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

6. Enable and start service `sudo systemctl enable --now github-runner.service`
7. Configure Docker

```bash
sudo yum update -y
sudo yum install docker -y
sudo service docker start
sudo usermod -a -G docker ec2-user
sudo systemctl start docker
sudo systemctl enable docker
```

8. Install Git

```bash
sudo yum install git -y
```

9. Restart the instance
10. Confirm GH Runner is still available on GH
11. Check service status on EC2 instance

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