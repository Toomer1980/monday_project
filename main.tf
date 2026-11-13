terraform {
  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.0"
    }
  }
}

# You will provide your API token when running the script
variable "do_token" {}

provider "digitalocean" {
  token = var.do_token
}

# Upload the zero-password SSH key we generated earlier
resource "digitalocean_ssh_key" "monday_auth" {
  name       = "monday_cloud_key"
  public_key = file("~/.ssh/monday_cloud_key.pub")
}

# Spin up the Swarm Node
resource "digitalocean_droplet" "monday_swarm_commander" {
  image  = "ubuntu-22-04-x64"
  name   = "sovereign-core-alpha"
  region = "nyc3" # New York 3 Datacenter
  size   = "s-2vcpu-4gb" # 2 CPUs, 4GB RAM (Ideal for Docker + Tor)
  ssh_keys = [digitalocean_ssh_key.monday_auth.fingerprint]

  # This injects the bootstrap script directly into the server's brain on boot
  user_data = <<-EOF
              #!/bin/bash
              echo "[*] Initializing SovereignCore Cloud Environment..."
              apt-get update && apt-get upgrade -y
              apt-get install -y docker.io docker-compose git ufw curl python3-venv

              echo "[*] Securing network perimeter..."
              ufw default deny incoming
              ufw default allow outgoing
              ufw allow 22/tcp
              ufw allow 80/tcp
              ufw allow 443/tcp
              ufw --force enable

              echo "[*] Constructing framework directories..."
              mkdir -p /opt/SovereignCore/{logs,data,models,entropy_streams}
              
              # Set permissions for predictive data processing
              chmod 755 /opt/SovereignCore/models
              chmod 755 /opt/SovereignCore/entropy_streams
              EOF
}

# Output the IP address so we can connect Bruno immediately
output "swarm_public_ip" {
  value = digitalocean_droplet.monday_swarm_commander.ipv4_address
}