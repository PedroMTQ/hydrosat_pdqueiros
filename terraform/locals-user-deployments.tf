locals {
  user_deployments = [
    {
      name    = "service_1"
      image   = "localhost:5000/dagster_service:latest"
      command = "dagster api grpc -f src/dagster_k8s/services/service_1/jobs/service.py"
      env = {
        SERVICE_NAME = "service_1"
        DAGSTER_HOME = "/opt/dagster_home"
      }
      # autoscaling = {
      #   enabled                      = true
      #   minReplicas                  = 1
      #   maxReplicas                  = 3
      #   targetCPUUtilizationPercentage = 60
      # }
    }
  ]
}
