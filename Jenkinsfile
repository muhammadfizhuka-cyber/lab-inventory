// Asumsi: Jenkins jalan langsung di Windows (agent pakai `bat`), Docker Desktop & Python ada di PATH.
// Kalau Jenkins berjalan di Linux/container, ganti `bat` -> `sh` dan sesuaikan path.
pipeline {
    agent any

    options { timestamps() }
    triggers { githubPush() }

    environment {
        COMPOSE_PROJECT_NAME = 'lab-inventory'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                bat 'git log -1 --oneline'
            }
        }

        stage('Syntax Check') {
            steps {
                bat 'python -m py_compile backend\\app.py'
                bat 'docker compose config -q'
            }
        }

        stage('Build Image') {
            steps {
                bat 'docker compose build'
            }
        }

        stage('Automated Deployment') {
            steps {
                bat 'docker compose up -d --remove-orphans'
            }
        }

        stage('Health Check') {
            steps {
                bat 'powershell -NoProfile -ExecutionPolicy Bypass -File healthcheck.ps1'
            }
        }
    }

    post {
        success { echo 'Deploy sukses. UI: http://localhost:8081' }
        failure { bat 'docker compose logs --tail=50' }
    }
}
