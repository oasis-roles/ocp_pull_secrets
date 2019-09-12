[![Build Status](https://travis-ci.com/oasis-roles/ocp_pull_secrets.svg?branch=master)](https://travis-ci.com/oasis-roles/ocp_pull_secrets)

ocp_pull_secrets
================

Get pull secrets to be used by OpenShift Container Platform (OCP) 4.x
to pull images from registries that require authentication. This is done with
your offline access token found at https://cloud.redhat.com/openshift/token
(login required), and according to the documentation found in the OCP
[install guides](https://cloud.redhat.com/openshift/install).

**Note**: As this role demonstrates, the offline access token can be used to
grant anyone the ability to authenticate to APIs, such as `api.openshift.com`,
as the owner of the offline access token. **Protect this token as you would
protect any other sensitive authentication information.** All
authentication-related tasks in this role are set to *not* log by default, but
this can be altered if needed; see the Optional Role Variables below.

The resulting pull secrets are stored in an ansible fact for use in later
plays, either in an OCP 4.x installation role or tasks. Note that because
this role leaves it up to the calling user when and where (i.e. on which
host) to generate the output fact, and makes no attempt at idempotence.
If writing the ansible fact out to a file, the `to_json` filter must be
used. By default, the output ansible fact is `ocp_pull_secrets`, but this
can be customized if needed.

Example playbooks are provided below which demonstrates the proper use of
the `to_json` filter, various ways to load the access token, and ways to
invoke this role in an idempotent way based on output facts or files.

Requirements
------------

Ansible 2.7 or higher

Red Hat Enterprise Linux 7 or equivalent

Valid Red Hat Subscriptions

Role Variables
--------------

### Required

* `ocp_pull_secrets_offline_token` - Offline access token acquired from
  https://cloud.redhat.com/openshift/token (login required), or an offline access token provided
  by the authentication service providing the `ocp_pull_secrets_token_url` if the
  default `sso.redhat.com` and `api.openshift.com` default services are not used.

### Optional

* `ocp_pull_secrets_out_var` - Name of the fact in which to store the gathered pull secrets JSON.
  Default `ocp_pull_secrets`.
* `ocp_pull_secrets_additional_auths` - Dictionary of additional authorizations to inject into the
  gathered pull secrets, see usage example below. Default `{}` (empty dict).
* `ocp_pull_secrets_no_log` - If true, prevent logging secrets to ansible output.
  Default `true`.
* `ocp_pull_secrets_token_url` - OpenID token endpoint used to convert the offline access token into
  an authorization bearer token for use with the api endpoint URL.
  Default `https://sso.redhat.com/auth/realms/redhat-external/protocol/openid-connect/token`.
* `ocp_pull_secrets_api_url` - API endpoint providing pull secrets for use by OCP.
  Default `https://api.openshift.com/api/accounts_mgmt/v1/access_token`.

Example Playbooks
-----------------

### Load access token from a file, write the pull secrets to a file

The basic workflow of generating the pull secrets file, expected to be run on a
single host, such as an OCP installation bootstrap/bastion host.

```yaml
- name: Load offline access token from file and write pull secrets to another file
  hosts: ocp_pull_secrets_host
  vars:
    ocp_pull_secrets_offline_token: "{{ lookup('file', '/path/to/token.file') }}"
  roles:
    - role: oasis_roles.ocp_pull_secrets
  tasks:
    - name: Write pull secrets out to a secret place
      copy:
        # the to_json filter is required
        # if outputting for use in the OCP installer, do not indent the output
        # json, use the to_nice_json filter, or otherwise reformat it
        content: "{{ ocp_pull_secrets | to_json }}"
        dest: "/path/to/pull_secrets.json"
        # "become" and/or set file modes appropriately to keep the secrets safe
```

### Load access token from environment, inject additional auths

Assuming that the environment variable `OCP_OFFLINE_ACCESS_TOKEN_ENVVAR` contains the
entire offline access token string, and there are additional authorizations to inject:

```yaml
- name: Load offline access token from the environment to get pull secrets to custom fact
  hosts: ocp_pull_secrets_host
  vars:
    ocp_pull_secrets_offline_token: "{{ lookup('env' 'OCP_OFFLINE_ACCESS_TOKEN_ENVVAR') }}"
    ocp_pull_secrets_additional_auths:
        host1.example.com:
            email: user1@example.com
            auth: base64_encoded_auth_token
        host2.example.com:
            email: user2@example.com
            auth: base64_encoded_auth_token
  roles:
    - role: oasis_roles.ocp_pull_secrets
```

Note that the `additional_auths` structure, where the top-level key is the registry hostname
to which to authenticate, and the value for that key is itself a dictionary containing the
authentication information for that registry hostname, such as an `email` and related `auth`
token.

### Conditionally skip output fact generation if fact already set

This is one way to run this role idempotently, but the 'when' clause
could be anything.

```yaml
- name: Skip getting the pull secrets based on output fact
  hosts: ocp_pull_secrets_host
  vars:
    ocp_pull_secrets_offline_token: 'your token here'
  roles:
    - name: oasis_roles.ocp_pull_secrets
      # 'ocp_pull_secrets' is the default output fact name
      when: ocp_pull_secrets is undefined
```

Another option that would be stateful across Ansible Playbook runs
would be writing the pull secrets fact to a file, and then only
invoking the role when the output file does not exist:

```yaml
- name: Skip getting the pull secrets based on output file
  hosts: all
  gather_facts: false
  vars:
    ocp_pull_secrets_no_log: false
  pre_tasks:
    - name: Stat output file
      stat:
        path: pull_secrets_output.json
      register: pull_secrets_file
  roles:
    - name: oasis_roles.ocp_pull_secrets
      when: not pull_secrets_file.stat.exists
```

Dependencies
------------

None

License
-------

GPLv3

Author Information
------------------

Sean Myers <sean.myers@redhat.com>
