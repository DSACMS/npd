#!/usr/bin/env bash
sudo -u ec2-user -i << EOF
set -euo pipefail

whoami

echo "==> Creating GitHub Actions runner directory"
sudo mkdir -p "${ RUNNER_DIR }"
sudo chown ec2-user:ec2-user "${ RUNNER_DIR }"

echo "==> Downloading GitHub runner ${ RUNNER_VERSION }"
curl -L -o "${ RUNNER_DIR }/actions-runner-linux-x64-${ RUNNER_VERSION }.tar.gz" \
  "https://github.com/actions/runner/releases/download/v${ RUNNER_VERSION }/actions-runner-linux-x64-${ RUNNER_VERSION }.tar.gz"

echo "==> Extracting runner"
cd "${ RUNNER_DIR }"
tar xzf "actions-runner-linux-x64-${ RUNNER_VERSION }.tar.gz"

echo "==> Configuring runner"
./config.sh --url "${ GITHUB_URL }" --token "${ TOKEN }" --unattended --labels experimental

echo "==> Creating systemd service"
sudo tee /etc/systemd/system/github-runner.service > /dev/null <<'EOT'
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
EOT

echo "==> Enabling GitHub runner service"
sudo systemctl enable --now github-runner.service

echo "==> Installing Docker"
sudo yum update -y
sudo yum install docker -y
sudo service docker start
sudo usermod -a -G docker ec2-user
sudo systemctl enable docker

echo "==> Installing Git"
sudo yum install git -y
EOF

echo "==> Adding nightly docker prune cron job"
( crontab -l 2>/dev/null; echo "00 00 * * * /usr/bin/docker system prune -af" ) | crontab -

echo "==> Bootstrap complete."