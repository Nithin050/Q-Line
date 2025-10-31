# 1. Configure the Google Cloud provider
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "5.0.0"
    }
  }
}

provider "google" {
  project = "qwiklabs-gcp-03-535c303cdbb1"
  region  = "us-east1"
  zone    = "us-east1-c"
}

# 2. Create a simple VPC network (manual subnet creation allowed)
resource "google_compute_network" "vpc_network" {
  name                    = "q-line-network"
  auto_create_subnetworks = false
}

# 3. Create a subnetwork
resource "google_compute_subnetwork" "vpc_subnetwork" {
  name          = "q-line-subnet"
  ip_cidr_range = "10.0.1.0/24"
  region        = "us-east1"
  network       = google_compute_network.vpc_network.id
}

# 4. Firewall rule to allow HTTP (Port 80)
resource "google_compute_firewall" "allow_http" {
  name    = "q-line-firewall-http"
  network = google_compute_network.vpc_network.name

  allow {
    protocol = "tcp"
    ports    = ["80"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["http-server"]

  depends_on = [google_compute_network.vpc_network]
}

# 5. Firewall rule to allow SSH (Port 22)
resource "google_compute_firewall" "allow_ssh" {
  name    = "q-line-firewall-ssh"
  network = google_compute_network.vpc_network.name

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["ssh-server"]

  depends_on = [google_compute_network.vpc_network]
}

# 6. Create the Virtual Machine
resource "google_compute_instance" "vm_instance" {
  name         = "q-line-vm"
  machine_type = "e2-micro"
  zone         = "us-east1-c"

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
    }
  }

  network_interface {
    network    = google_compute_network.vpc_network.id
    subnetwork = google_compute_subnetwork.vpc_subnetwork.id

    access_config {
      # Assign a public IP
    }
  }

  tags = ["http-server", "ssh-server"]

  metadata_startup_script = <<-EOF
    #!/bin/bash
    apt-get update
    apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release

    # Add Docker's official GPG key
    curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

    # Set up the stable repository
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian \
      $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

    # Install Docker Engine
    apt-get update
    apt-get install -y docker-ce docker-ce-cli containerd.io
  EOF

  depends_on = [
    google_compute_network.vpc_network,
    google_compute_subnetwork.vpc_subnetwork,
    google_compute_firewall.allow_http,
    google_compute_firewall.allow_ssh
  ]
}

# 7. Output the VM's Public IP address
output "vm_public_ip" {
  description = "The public IP address of the VM"
  value       = google_compute_instance.vm_instance.network_interface[0].access_config[0].nat_ip
}
