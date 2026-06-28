pipeline {
  agent {
    kubernetes {
      yaml """
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: python
    image: python:3.12-slim
    command: ['cat']
    tty: true
  - name: kaniko
    image: gcr.io/kaniko-project/executor:v1.23.2-debug
    command: ['sleep']
    args: ['99d']
    tty: true
"""
    }
  }
  environment {
    AWS_REGION = 'eu-north-1'
    ECR_REPO   = '565083285597.dkr.ecr.eu-north-1.amazonaws.com/mcp-server'
    IMAGE_TAG  = "${env.GIT_COMMIT.take(7)}"
  }
  stages {
    stage('Checkout') {
      steps { checkout scm }
    }
    stage('Test') {
      steps {
        container('python') {
          dir('mcp-server') {
            sh 'pip install -q -r requirements.txt && pytest -q'
          }
        }
      }
    }
    stage('Build & Push ECR') {
      steps {
        container('kaniko') {
          dir('mcp-server') {
            withAWS(region: "${AWS_REGION}", credentials: 'aws-ecr') {
              sh """
                /kaniko/executor \\
                  --context=. \\
                  --dockerfile=Dockerfile \\
                  --destination=${ECR_REPO}:${IMAGE_TAG} \\
                  --destination=${ECR_REPO}:latest
              """
            }
          }
        }
      }
    }
  }
}
