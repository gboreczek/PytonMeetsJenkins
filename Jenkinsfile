pipeline {
    agent any 
    stages { 
		stage('Pull changes'){
			steps{
				sh '''					
					cd ~/PytonMeetsJenkins
					git pull
				'''
			}
		}
        stage('Build') { 
            steps {
                sh '''   
					cd ~/PytonMeetsJenkins
                    sudo docker build -t localhost:5000/python-meets-jenkins:passy_z_pliku .
				'''
            }
        }
        stage('Smoke/connection test') { 
            steps {
                sh '''
					sudo docker run -t --rm -v ~/PytonMeetsJenkins:/usr/src/app localhost:5000/python-meets-jenkins > stdout.log
					cat stdout.log
				'''				
            }
        }        
    }
}
