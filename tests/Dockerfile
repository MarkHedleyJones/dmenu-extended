FROM python:3-slim

# Setup the user account
RUN addgroup --gid 1000 user \
  && adduser --disabled-password --gecos '' --gid 1000 --uid 1000 user
USER user
WORKDIR /home/user
ENV PATH=/home/user/.local/bin:$PATH

# Copy the package into the image
COPY --chown=user requirements.txt /home/user/dmenu-extended/requirements.txt

# Upgrade pip and install required packages for build
RUN python -m pip install --upgrade pip \
  && pip install --upgrade --no-cache-dir -r dmenu-extended/requirements.txt

# Copy the package into the image
COPY --chown=user . /home/user/dmenu-extended

# Install dmenu-extended into the image
RUN cd /home/user/dmenu-extended \
  && python3 -m build --wheel \
  && pip3 install dist/dmenu_extended-*-py3-none-any.whl --upgrade

# We can't run the real dmenu here because it requires a tty
# For measuring performance we can just create a fake dmenu
# This just exits, which lets us measure the time it takes to open the menu
USER root
# RUN echo "#!/usr/bin/env sh\nexit 0" > /usr/bin/dmenu \
#   && chmod +x /usr/bin/dmenu
RUN echo "#!/usr/bin/env bash\n\
counter=0\n\
while read -r line; do let \"counter++\"; done\n\
echo \"Items: \$((\${counter} - 1))\" > /tmp/dmenu.log\n\
exit 0\n" > /usr/bin/dmenu && chmod +x /usr/bin/dmenu

USER user
