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
    AWS_ACCOUNT = '565083285597'
    IMAGE_TAG  = "${env.GIT_COMMIT.take(7)}"
  }
  stages {
    stage('Checkout') {
      steps { checkout scm }
    }
    stage('Test & Build') {
      parallel {
        stage('mcp-server') {
          stages {
            stage('Test MCP') {
              steps {
                container('python') {
                  dir('mcp-server') {
                    sh 'pip install -q -r requirements.txt && pytest -q'
                  }
                }
              }
            }
            stage('Push MCP') {
              steps {
                container('kaniko') {
                  dir('mcp-server') {
                    withAWS(region: "${AWS_REGION}", credentials: 'aws-ecr') {
                      sh """
                        /kaniko/executor \\
                          --context=. \\
                          --dockerfile=Dockerfile \\
                          --destination=${AWS_ACCOUNT}.dkr.ecr.${AWS_REGION}.amazonaws.com/mcp-server:${IMAGE_TAG} \\
                          --destination=${AWS_ACCOUNT}.dkr.ecr.${AWS_REGION}.amazonaws.com/mcp-server:latest
                      """
                    }
                  }
                }
              }
            }
          }
        }
        stage('ia-chatbot') {
          stages {
            stage('Test Chatbot') {
              steps {
                container('python') {
                  dir('ia-chatbot') {
                    sh 'pip install -q -r requirements.txt && pytest -q'
                  }
                }
              }
            }
            stage('Push Chatbot') {
              steps {
                container('kaniko') {
                  dir('ia-chatbot') {
                    withAWS(region: "${AWS_REGION}", credentials: 'aws-ecr') {
                      sh """
                        /kaniko/executor \\
                          --context=. \\
                          --dockerfile=Dockerfile \\
                          --destination=${AWS_ACCOUNT}.dkr.ecr.${AWS_REGION}.amazonaws.com/ia-chatbot:${IMAGE_TAG} \\
                          --destination=${AWS_ACCOUNT}.dkr.ecr.${AWS_REGION}.amazonaws.com/ia-chatbot:latest
                      """
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
