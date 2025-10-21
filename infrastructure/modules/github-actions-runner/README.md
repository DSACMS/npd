# GitHub Action Runner

## Manual Work After Deploy

1. Get GitHub self-hosted runner script from GitHub
2. Install on instance
3. cp to /opt/actions-runner
4. give ec2-user ownership of /opt/actions-runner

```bash
sudo chown -R ec2-user:ec2-user /opt/github-runner
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

6. enable service `systemctl start github-runner.service`
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
10. Confirm GH Runner is available on GH
