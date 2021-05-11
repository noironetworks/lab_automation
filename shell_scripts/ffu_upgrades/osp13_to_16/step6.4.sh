############################################################################
# 6.4 Preparing container images
############################################################################
# 1. Log in to your undercloud host as the stack user.
# 2. Generate the default container image preparation file:
openstack tripleo container image prepare default \
  --local-push-destination \
  --output-env-file templates/containers-prepare-parameter.yaml
# 3. Modify the containers-prepare-parameter.yaml to suit your requirements.

