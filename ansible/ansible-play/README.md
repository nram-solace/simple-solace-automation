# Ansible playbook for Solace Automation

## About

This folder has sample Ansible playbook, inventory, roles and other required files to provision Solace Message VPN Objects with Ansible.

- **Inventory file**: SEMP URL and authentication are read from inventory file
- **roles**: SEMP templates are defined in roles/xxx/main.yml. REST posts are done from here as well.
- **vars**: Actual values for the SEMP templates are read in from vars/xxx.yml

### Note

- This implementation has no depedency on Python and SEMP requestes are triggerred (POST) directly from Ansible roles file.

- This implementation is NOT modular doesn't use tasks. All operations are called from the playbook directly.

## Env

- Solace S/W Broker 10.0

## Status

- Queue Creation + Queue subscription: OK
- DMR Cluster creation : OK
- Client Username + Profiles : Not-tested
- VPN Creation : Not tested