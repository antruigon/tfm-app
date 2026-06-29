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
  - name: kaniko-mcp
    image: gcr.io/kaniko-project/executor:v1.23.2-debug
    command: ['sleep']
    args: ['99d']
    tty: true
  - name: kaniko-chatbot
    image: gcr.io/kaniko-project/executor:v1.23.2-debug
    command: ['sleep']
    args: ['99d']
    tty: true
  - name: git
    image: alpine/git:2.45.2
    command: ['cat']
    tty: true
"""
    }
  }
  environment {
    AWS_REGION = 'eu-north-1'
    AWS_ACCOUNT = '565083285597'
    IMAGE_TAG = "${env.GIT_COMMIT.take(7)}"
    CHARTS_REPO = 'https://github.com/antruigon/tfm-charts.git'
    CHARTS_BRANCH = 'master'
  }
  stages {
    stage('Checkout') {
      steps { checkout scm }
    }

    stage('Detect changes') {
      steps {
        script {
          def changes = sh(
            script: '''
              set +e
              git diff --name-only HEAD~1 HEAD 2>/dev/null
              if [ $? -ne 0 ]; then
                git show --name-only --pretty=format: HEAD
              fi
            ''',
            returnStdout: true
          ).trim()

          env.BUILD_MCP = (
            changes.contains('mcp-server/') ||
            changes.contains('Jenkinsfile')
          ) ? 'true' : 'false'

          env.BUILD_CHATBOT = (
            changes.contains('ia-chatbot/') ||
            changes.contains('Jenkinsfile')
          ) ? 'true' : 'false'

          if (env.BUILD_MCP == 'false' && env.BUILD_CHATBOT == 'false') {
            env.BUILD_MCP = 'true'
            env.BUILD_CHATBOT = 'true'
          }

          echo "BUILD_MCP=${env.BUILD_MCP} BUILD_CHATBOT=${env.BUILD_CHATBOT} IMAGE_TAG=${env.IMAGE_TAG}"
        }
      }
    }

    stage('CI: Test') {
      parallel {
        stage('mcp-server') {
          when { expression { env.BUILD_MCP == 'true' } }
          steps {
            container('python') {
              dir('mcp-server') {
                sh 'pip install -q -r requirements.txt && pytest -q'
              }
            }
          }
        }
        stage('ia-chatbot') {
          when { expression { env.BUILD_CHATBOT == 'true' } }
          steps {
            container('python') {
              dir('ia-chatbot') {
                sh 'pip install -q -r requirements.txt && pytest -q'
              }
            }
          }
        }
      }
    }

    stage('Push MCP') {
      when { expression { env.BUILD_MCP == 'true' } }
      steps {
        container('kaniko-mcp') {
          dir('mcp-server') {
            withAWS(region: "${AWS_REGION}", credentials: 'aws-ecr') {
              sh """
                /kaniko/executor \\
                  --context=. \\
                  --dockerfile=Dockerfile \\
                  --destination=${AWS_ACCOUNT}.dkr.ecr.${AWS_REGION}.amazonaws.com/mcp-server:${IMAGE_TAG}
              """
            }
          }
        }
      }
    }

    stage('Push Chatbot') {
      when { expression { env.BUILD_CHATBOT == 'true' } }
      steps {
        container('kaniko-chatbot') {
          dir('ia-chatbot') {
            withAWS(region: "${AWS_REGION}", credentials: 'aws-ecr') {
              sh """
                /kaniko/executor \\
                  --context=. \\
                  --dockerfile=Dockerfile \\
                  --destination=${AWS_ACCOUNT}.dkr.ecr.${AWS_REGION}.amazonaws.com/ia-chatbot:${IMAGE_TAG}
              """
            }
          }
        }
      }
    }

    stage('CD: Update GitOps') {
      when {
        expression { env.BUILD_MCP == 'true' || env.BUILD_CHATBOT == 'true' }
      }
      steps {
        container('git') {
          withCredentials([usernamePassword(
            credentialsId: 'github-tfm-charts',
            usernameVariable: 'GIT_USER',
            passwordVariable: 'GIT_TOKEN'
          )]) {
            sh """
              set -e
              apk add --no-cache sed >/dev/null

              git clone --branch "${CHARTS_BRANCH}" \\
                "https://\${GIT_USER}:\${GIT_TOKEN}@github.com/antruigon/tfm-charts.git" \\
                charts-repo
              cd charts-repo
              git config user.email "jenkins@tfm.local"
              git config user.name "Jenkins TFM"

              if [ "\$BUILD_MCP" = "true" ]; then
                sed -i "s/^  tag: .*/  tag: ${IMAGE_TAG}/" charts/mcp-server/values-dev.yaml
              fi
              if [ "\$BUILD_CHATBOT" = "true" ]; then
                sed -i "s/^  tag: .*/  tag: ${IMAGE_TAG}/" charts/ia-chatbot/values-dev.yaml
              fi

              git add charts/mcp-server/values-dev.yaml charts/ia-chatbot/values-dev.yaml
              git diff --staged --quiet && echo "Sin cambios en charts" && exit 0

              git commit -m "ci: image tag ${IMAGE_TAG} (tfm-app@${GIT_COMMIT})"
              git push origin "${CHARTS_BRANCH}"
            """
          }
        }
      }
    }
  }

  post {
    success {
      echo "Pipeline OK — imagen(es) :${IMAGE_TAG} en ECR; Argo CD sincronizará tfm-charts"
    }
  }
}
