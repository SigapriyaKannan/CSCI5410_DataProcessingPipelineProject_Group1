
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }

  required_version = ">= 1.2.0"
}

provider "google" {
  project = var.project_id
  region  = var.region
}

variable "project_id" {
  description = "kube-assignment-428815"
  type        = string
}

variable "region" {
  description = "us-central1"
  type        = string
  default     = "us-central1"
}

variable "image" {
  description = "gcr.io/kube-assignment-428815/serverless/next-frontend"
  type        = string
}

resource "null_resource" "delete_cloud_run" {
  provisioner "local-exec" {
    command = "gcloud run services delete quickdataprocessor --region=${var.region} --project=${var.project_id} --quiet"
  }

  triggers = {
    always_run = "${timestamp()}"
  }
}

resource "google_cloud_run_service" "app" {
  depends_on = [null_resource.delete_cloud_run]
  name     = "quickdataprocessor"
  location = var.region

  template {
    spec {
      containers {
        image = var.image
        ports {
          container_port = 80
        }
      }
    }
  }

  autogenerate_revision_name = true
}

# Allow unauthenticated requests
resource "google_cloud_run_service_iam_member" "unauthenticated_access" {
  location = google_cloud_run_service.app.location
  service  = google_cloud_run_service.app.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

output "cloud_run_url" {
  value = google_cloud_run_service.app.status[0].url
}
