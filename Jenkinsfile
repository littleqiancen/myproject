pipeline {
  agent any

  environment {
    REGISTRY = 'ghcr.io'
    OWNER = 'littleqiancen'
    BACKEND_IMAGE = "${REGISTRY}/${OWNER}/myproject-backend"
    FRONTEND_IMAGE = "${REGISTRY}/${OWNER}/myproject-frontend"
    DEPLOY_DIR = '/opt/casegen'
    COMPOSE_FILE = 'docker-compose.prod.yml'
  }

  options {
    timestamps()
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Compute Tag') {
      steps {
        script {
          env.IMAGE_TAG = sh(script: "git rev-parse --short=8 HEAD", returnStdout: true).trim()
        }
      }
    }

    stage('Login GHCR') {
      steps {
        withCredentials([usernamePassword(credentialsId: 'ghcr', usernameVariable: 'GHCR_USER', passwordVariable: 'GHCR_TOKEN')]) {
          sh '''
            set -e
            echo "$GHCR_TOKEN" | docker login ghcr.io -u "$GHCR_USER" --password-stdin
          '''
        }
      }
    }

    stage('Build Images') {
      steps {
        sh '''
          set -e
          docker build -t "${BACKEND_IMAGE}:${IMAGE_TAG}" -t "${BACKEND_IMAGE}:latest" ./backend
          docker build -t "${FRONTEND_IMAGE}:${IMAGE_TAG}" -t "${FRONTEND_IMAGE}:latest" ./frontend
        '''
      }
    }

    stage('Push Images') {
      steps {
        sh '''
          set -e
          docker push "${BACKEND_IMAGE}:${IMAGE_TAG}"
          docker push "${BACKEND_IMAGE}:latest"
          docker push "${FRONTEND_IMAGE}:${IMAGE_TAG}"
          docker push "${FRONTEND_IMAGE}:latest"
        '''
      }
    }

    stage('Deploy') {
      steps {
        sh '''
          set -e
          mkdir -p "${DEPLOY_DIR}"
          cp -f "${COMPOSE_FILE}" "${DEPLOY_DIR}/${COMPOSE_FILE}"
          mkdir -p "${DEPLOY_DIR}/data/uploads" "${DEPLOY_DIR}/data/data"
          if [ ! -f "${DEPLOY_DIR}/data/settings.json" ]; then
            echo "{}" > "${DEPLOY_DIR}/data/settings.json"
          fi
          if [ ! -f "${DEPLOY_DIR}/.env" ]; then
            echo "BACKEND_PORT=8000" > "${DEPLOY_DIR}/.env"
            echo "FRONTEND_PORT=80" >> "${DEPLOY_DIR}/.env"
            echo "DATABASE_PATH=/app/data/casegen.db" >> "${DEPLOY_DIR}/.env"
            echo "CHROMADB_PATH=/app/data/chromadb_data" >> "${DEPLOY_DIR}/.env"
          fi
          cd "${DEPLOY_DIR}"
          export BACKEND_IMAGE="${BACKEND_IMAGE}"
          export FRONTEND_IMAGE="${FRONTEND_IMAGE}"
          export IMAGE_TAG="${IMAGE_TAG}"
          docker compose -f "${COMPOSE_FILE}" pull
          docker compose -f "${COMPOSE_FILE}" up -d
        '''
      }
    }
  }

  post {
    always {
      sh '''
        docker logout ghcr.io || true
      '''
    }
  }
}
