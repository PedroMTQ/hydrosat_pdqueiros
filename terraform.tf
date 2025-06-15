
variable "dagster_version" {
  type        = string

}

variable "namespace" {
  type        = string
}


resource "kubernetes_namespace" "hydrosat_pdqueiros_namespace" {
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

# if you are not using minikube you need to change these 2
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
  depends_on = [kubernetes_namespace.hydrosat_pdqueiros_namespace]
  values = [file("${path.module}/dagster-chart.yaml")]
}



