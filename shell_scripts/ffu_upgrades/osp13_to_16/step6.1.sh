############################################################################
# 6.1 Locking the environment to a Red Hat Enterprise Linux release
############################################################################
# 1. Log in to the undercloud as the stack user.
# 2. Lock the undercloud to a specific verison with the subscription-manager release command:
sudo subscription-manager release --set=8.2
