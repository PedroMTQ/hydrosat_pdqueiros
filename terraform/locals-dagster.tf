# contains configuration parameters per service
# docs: https://github.com/dagster-io/dagster/blob/master/helm/dagster/values.yaml
# locals {
#   dagster_values = {
#     celeryK8s = {
#       enabled = true
#       worker = {
#         replicas = 2
#       }
#       brokerUrl     = "pyamqp://${var.rabbitmq_username}:${var.rabbitmq_password}@rabbitmq.${var.namespace}.svc.cluster.local:5672//"
#       resultBackend = "db+postgresql://${var.postgres_username}:${var.postgres_password}@postgresql.${var.namespace}.svc.cluster.local:5432/${var.postgres_database}"
#     }
#     postgresql = {
#       enabled = true
#       auth = {
#         username = var.postgres_username
#         password = var.postgres_password
#         database = var.postgres_database
#       }
#       persistence = {
#          enabled = true
#         #  existingClaim = var.dagster_pvc
#        }

#     }
#     rabbitmq = {
#       enabled = true
#       rabbitmq = {
#         username = var.rabbitmq_username
#         password = var.rabbitmq_password
#       }
#       persistence = {
#          enabled = true
#         #  existingClaim = var.dagster_pvc
#        }
#     }
#   }
# }
