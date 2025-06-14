

resource "kubernetes_namespace" "dagster_k8_terraform_namespace" {
  metadata {
    name = var.namespace
  }
}

# resource "kubernetes_persistent_volume_claim" "dagster_pvc" {
#   metadata {
#     name      = var.dagster_pvc
#     namespace = var.namespace
#   }
#   spec {
#     access_modes = ["ReadWriteOnce"]

#     resources {
#       requests = {
#         storage = "10Gi"
#       }
#     }
#   }
# }


resource "helm_release" "dagster" {
  name       = "dagster"
  repository = "https://dagster-io.github.io/helm"
  chart      = "dagster"
  namespace  = var.namespace
  version    = var.dagster_version
  depends_on = [kubernetes_namespace.dagster_k8_terraform_namespace]#, kubernetes_persistent_volume_claim.dagster_home_pvc]
  values = [
    yamlencode({
      env = {
        DAGSTER_HOME = "/opt/dagster_home"
      }
      persistence = {
        enabled = true
    }
      # dagsterHome = {
      #   volume = {
      #     persistentVolumeClaim = {
      #       claimName = kubernetes_persistent_volume_claim.dagster_home_pvc.metadata[0].name
      #     }
      #   }
      #   }
      userDeployments = {
        enabled         = true
        deployments = [
        {
          name = "service_1"
          #"localhost:5000/dagster_service:latest"
          image = {
            repository= "localhost:5000/dagster_service"
            tag= "latest"
            pullPolicy= "Never" # or Always/IfNotPresent
          }
          command = ["dagster", "api", "grpc", "-f", "./src/dagster_k8s_terraform_dev/jobs/service.py"]
          env = {
            SERVICE_NAME = "service_1"
            DAGSTER_HOME = "/opt/dagster_home"
          }
        }
      ]
      }

      # serviceAccount = {
      #   create = true
      #   name   = "dagster-runner"
      # }

      runLauncher = {
        type = "K8sRunLauncher"
      }

    })
  ]
}



