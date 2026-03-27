pipeline {
    agent any

    tools {
        'org.jenkinsci.plugins.docker.commons.tools.DockerTool' 'docker-cli'
    }

    environment {
        DOCKER_HOST = 'tcp://host.docker.internal:2375'
    }

    stages {
        stage('Run task') {
            steps {
                withCredentials([
                    string(
                        credentialsId: 'alts-postgres-host',
                        variable: 'POSTGRES_HOST'
                    ),
                    string(
                        credentialsId: 'alts-postgres-port',
                        variable: 'POSTGRES_PORT'
                    ),
                    usernamePassword(
                        credentialsId: 'alts-postgres-login',
                        usernameVariable: 'POSTGRES_USERNAME',
                        passwordVariable: 'POSTGRES_PASSWORD'
                    ),
                    string(
                        credentialsId: 'alts-postgres-database',
                        variable: 'POSTGRES_DATABASE'
                    ),
                    string(
                        credentialsId: 'alts-git-private-repo-url',
                        variable: 'GIT_PRIVATE_REPO_URL'
                    )
                ]) {
                    sh '''
                        docker run \
                        --rm \
                        -e LOG_LEVEL=20 \
                        -e POSTGRES_HOST=$POSTGRES_HOST \
                        -e POSTGRES_PORT=$POSTGRES_PORT \
                        -e POSTGRES_USERNAME=$POSTGRES_USERNAME \
                        -e POSTGRES_PASSWORD=$POSTGRES_PASSWORD \
                        -e POSTGRES_DATABASE=$POSTGRES_DATABASE \
                        -e GIT_PRIVATE_REPO_URL=$GIT_PRIVATE_REPO_URL \
                        alts-metric
                    '''
                }
            }
        }
    }
}
