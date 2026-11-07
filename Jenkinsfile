pipeline {
    agent any

    environment {
        PYTHONUNBUFFERED = '1'
        REGISTRY_NAME = 'python-crud-api'
        CONTAINER_NAME = 'production-api-container'
        DOCKER_NETWORK = 'jenkins-net'
        PORT_MAPPING = '5000:5000'
        VOLUME_NAME = 'production-api-data'
    }

    stages {
        stage('1. Checkout Code') {
            steps {
                echo 'Checking out source code from GitHub'
                checkout scm
                sh 'git rev-parse HEAD && git rev-parse --short HEAD'
            }
        }

        stage('2. Code Syntax Verification') {
            steps {
                sh 'python3 -m py_compile app.py test_app.py'
            }
        }

        stage('3. Automated API Tests') {
            steps {
                sh 'python3 -m unittest -v test_app.py'
            }
        }

        stage('4. Build Docker Image') {
            steps {
                sh '''
                    COMMIT_SHA=$(git rev-parse --short HEAD)
                    echo "Building image for BUILD_NUMBER=${BUILD_NUMBER}, COMMIT_SHA=${COMMIT_SHA}"
                    docker build -t ${REGISTRY_NAME}:${BUILD_NUMBER} .
                    docker tag ${REGISTRY_NAME}:${BUILD_NUMBER} ${REGISTRY_NAME}:${COMMIT_SHA}
                    docker tag ${REGISTRY_NAME}:${BUILD_NUMBER} ${REGISTRY_NAME}:latest
                    docker images ${REGISTRY_NAME}
                '''
            }
        }

        stage('5. Automated Deployment') {
            steps {
                sh '''
                    docker network inspect ${DOCKER_NETWORK} >/dev/null 2>&1 || docker network create ${DOCKER_NETWORK}
                    docker stop ${CONTAINER_NAME} || true
                    docker rm ${CONTAINER_NAME} || true
                    docker volume create ${VOLUME_NAME}
                    docker run -d \
                        --name ${CONTAINER_NAME} \
                        --network ${DOCKER_NETWORK} \
                        -p ${PORT_MAPPING} \
                        -v ${VOLUME_NAME}:/var/lib/backend_data \
                        ${REGISTRY_NAME}:latest
                    docker ps --filter "name=${CONTAINER_NAME}"
                '''
            }
        }

        stage('6. Health Check') {
            steps {
                sh '''
                    sleep 3
                    curl -fsS http://${CONTAINER_NAME}:5000/health || curl -fsS http://localhost:5000/health
                    echo ""
                    docker logs --tail 20 ${CONTAINER_NAME}
                '''
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully.'
        }
        failure {
            echo 'Pipeline failed. Inspect Console Output.'
        }
    }
}

