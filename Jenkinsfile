def linting_pipeline() {
	return [
		stage('linting') {
			sh "tox -e linting"
		},
		stage('security') {
			sh "tox -e security"
		}
	]
}

def tests_pipeline(def interpreter, def cov_option, def all) {
	return {	
		node() {
			stage('unit tests') {
				sh "tox -e ${interpreter}-${cov_option} -- -m unit"
			}
			
			if(all) {
				stage('integration tests') {
					sh "tox -e ${interpreter}-${cov_option} -- -m integration"
				}
				stage('e2e tests') {
					sh "tox -e ${interpreter}-${cov_option} -- -m e2e"
				}
			}
		}
	}
}

interpreters = ["pypy3", "py36"]

def quick_build(def cov_option) {
	checkout scm

	def stages = linting_pipeline()

	def tests_branches = [:]
	for (interpreter in interpreters) {
		tests_branches[interpreter] = tests_pipeline(interpreter, "nocov", false)
	}
	stages.push(
		stage('tests') {
			parallel(tests_branches)
		}
	)

	return stages
}

def full_build() {
	checkout scm

	def stages = linting_pipeline()

	def tests_branches = [:]
	for (interpreter in interpreters) {
		tests_branches[interpreter] = tests_pipeline(interpreter, "nocov", false)
	}
	stages.push(
		stage('tests') {
			parallel(tests_branches)
		}
	)
	stages.push(
		stage('coverage report') {
			sh "tox -e coverage-report"
		}
	)

	return stages
}

properties([
	pipelineTriggers([
		cron('H */3 * * *'),
		pollSCM('H/5 * * * *')
	]),
	buildDiscarder(logRotator(daysToKeepStr: '30'))
])

branch = env.BRANCH_NAME

@NonCPS
def isTimerTriggered() {
	def timerTrigger = currentBuild.rawBuild.getCause(hudson.triggers.TimerTrigger$TimerTriggerCause)
	return !!timerTrigger
}

node() {
	def isTimerTriggered = isTimerTriggered()

	switch(branch) {
		case 'master':
			if (!isTimerTriggered) {
				full_build()

				stage('build package') {
					sh "tox -e wheel"
				}

				deleteDir()
			}
			break

		case 'develop':
			if (isTimerTriggered) {
				full_build()
				deleteDir()
			}
			break
		default:
			if (!isTimerTriggered) {
				quick_build("nocov")
				deleteDir()
			}
	}
}
