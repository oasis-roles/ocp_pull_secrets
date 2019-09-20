library('oasis-pipeline')

oasisMultistreamMoleculePipeline {
  upstream_git_url = 'https://github.com/oasis-roles/ocp_pull_secrets.git'
  molecule_role_name = 'ocp_pull_secrets'
  molecule_scenarios = ['default']
  properties = [pipelineTriggers([cron('H H * * *')])]
}
