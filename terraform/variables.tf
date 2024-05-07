variable "credentials_path" {
  description = "The path to your Google Cloud service account JSON key file."
  type        = string
}

variable "project_id" {
  description = "The project ID to deploy to."
  type        = string
}

variable "region" {
  description = "The region to deploy to."
  type        = string
  default     = "us-central1-a"
}
