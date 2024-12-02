
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
  description = "gcr.io/kube-assignment-428815/serverless/next-frontend:latest"
  type        = string
}

# Cloud Run Service
resource "google_cloud_run_service" "app" {
  name     = "quickdataprocessor"
  location = var.region

  template {
    spec {
      containers {
        image = var.image
        
        # Environment variables
        env {
          name  = "NEXT_PUBLIC_AUTH_API"
          value = "https://jzi33rv5fg.execute-api.us-east-1.amazonaws.com/Dev"
        }
        env {
          name  = "NEXT_PUBLIC_LOG_API"
          value = "https://us-central1-k8s-assignment-csci5409.cloudfunctions.net"
        }
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
