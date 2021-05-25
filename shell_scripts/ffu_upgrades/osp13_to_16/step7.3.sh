############################################################################
# 7.3 Validating the pre-upgrade requirements
############################################################################
# 1. Source the stackrc file.
# 2. Run the openstack tripleo validator run command with the --group pre-upgrade option and include the /usr/libexec/platform-python python runtime environment:
openstack tripleo validator run --group pre-upgrade --python-interpreter /usr/libexec/platform-python
# 3. Review the results of the validation report. To view detailed output from a specific validation, run the openstack tripleo validator show run command against the UUID of the specific validation from the report:
openstack tripleo validator show run -full  <UUID>
# A FAILED validation does not prevent you from deploying or running Red Hat OpenStack Platform. However, a FAILED validation can indicate a potential issue with a production environment.
