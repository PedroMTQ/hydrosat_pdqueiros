
variable "namespace" {
  type        = string
}

variable "dagster_pvc" {
  type        = string
  default = "dagster-pvc"
}


variable "dagster_version" {
  type        = string
  default = "~1.10"
}


variable "rabbitmq_username" {
  type        = string
  sensitive   = true
}

variable "rabbitmq_password" {
  type        = string
  sensitive   = true
}

# for cluster communication
variable "rabbitmq_volume_size" {
  type        = string
  default = "4Gi"
  }


variable "postgres_username" {
  type        = string
  sensitive   = true
}

variable "postgres_password" {
  type        = string
  sensitive   = true
}


variable "postgres_database" {
  type        = string
  sensitive   = true
  }


variable "postgres_volume_size" {
  type        = string
  default     = "8Gi"
  }


# variable "dagster_pull_policy" {
#   type        = string
#   sensitive   = true
#   # TODO in prod change to Always
#   default = "IfNotPresent"
#   }


