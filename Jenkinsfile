node () {
    stage('setup') {
        sh '''
            python3 -m venv ve
            . ve/bin/activate
            pip install -r test_requirements.txt
        '''
    }

    stage('linting') {
        sh '''
            . ve/bin/activate
            flake8 ./src || error=true
            pylint ./src || error=true

            if [ $error ]
            then
                exit 1
            fi
        '''
    }

    stage('security') {
        sh '''
            . ve/bin/activate
            bandit -r src/
            LC_ALL=en_GB.UTF-8 safety check
        '''
    }

    stage('unit tests') {
        echo "You should run unit tests here"
    }
    
    stage('integration tests') {
        echo "You should run integration tests here"
    }

    stage('e2e tests') {
        echo "You should run end to end tests here"
    }
}
