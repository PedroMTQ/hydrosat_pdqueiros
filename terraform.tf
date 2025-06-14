
variable "dagster_version" {
  type        = string
  # check with  `helm search repo dagster/dagster --versions | head -n 2`
  default = "1.10.20"
}

variable "namespace" {
  type        = string
  default = "hydrosat-pdqueiros"
}


resource "kubernetes_namespace" "dagster_k8_terraform_namespace" {
  metadata {
    name = var.namespace
  }
}


terraform {
  required_providers {
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.9"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "2.37.1"
    }
  }
}

provider "kubernetes" {
  config_path = "~/.kube/config"
  config_context = "minikube"
}

provider "helm" {
  kubernetes {
    config_path = "~/.kube/config"
    config_context = "minikube"
  }
}



resource "helm_release" "dagster" {
  name       = "dagster"
  repository = "https://dagster-io.github.io/helm"
  chart      = "dagster"
  namespace  = var.namespace
  version    = var.dagster_version
  depends_on = [kubernetes_namespace.dagster_k8_terraform_namespace]
  values = [file("${path.module}/values.yaml")]
}



