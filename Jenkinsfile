/* 0.00.00.01 */
pipeline {
    agent {
        docker {
            label 'docker-slave'
            image 'activemauney/docker-env:latest'
            args '-u root -v /var/run/docker.sock:/var/run/docker.sock -v "$HOME":/home'
        }
    }
    stages {
        stage('Build') {
            steps {
                sh "cd ./docker_script; echo show_hostname; hostname; /bin/bash ./build_and_publish_jenkins.sh ${env.BUILD_ID}"
            }
        }
        stage('Test') {
            steps {
                sh "cd ./docker_script; /bin/bash ./inifuc_jenkins.sh pull ${env.BUILD_ID}"
            }
        }
    }
}
