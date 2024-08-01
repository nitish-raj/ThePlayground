FROM gitpod/workspace-full:latest

# Install postgres and other tools
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    pandoc \
    pandoc-citeproc \
    curl \
    gdebi-core \
    dirmngr \
    gnupg \
    apt-transport-https \
    ca-certificates \
    software-properties-common \
    git

# Install Quarto
# ENV QUARTO_VERSION="1.4.550"
# RUN mkdir -p /opt/quarto/${QUARTO_VERSION} && \
#     curl -o quarto.tar.gz -L "https://github.com/quarto-dev/quarto-cli/releases/download/v${QUARTO_VERSION}/quarto-${QUARTO_VERSION}-linux-amd64.tar.gz" && \
#     tar -zxvf quarto.tar.gz -C "/opt/quarto/${QUARTO_VERSION}" && \
#     rm ./quarto.tar.gz && \
#     ln -s /opt/quarto/${QUARTO_VERSION}/quarto-${QUARTO_VERSION}/bin/quarto /usr/local/bin/quarto

# Install R and required packages
# RUN wget -qO- https://cloud.r-project.org/bin/linux/ubuntu/marutter_pubkey.asc | sudo tee -a /etc/apt/trusted.gpg.d/cran_ubuntu_key.asc && \
#     add-apt-repository "deb https://cloud.r-project.org/bin/linux/ubuntu $(lsb_release -cs)-cran40/" && \
#     apt install -y --no-install-recommends r-base && \
#     add-apt-repository -y ppa:c2d4u.team/c2d4u4.0+ && \
#     R -e "install.packages(c('renv','knitr','rmarkdown'), repos = c(CRAN = 'https://cloud.r-project.org'))"

# Install Google Cloud SDK
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg add - && \
    apt-get update -y && apt-get install -y google-cloud-sdk

# Switch back to gitpod user
USER gitpod

# Set up Git configuration
RUN git config --global core.autocrlf input && \
    git config --global user.email "22993803+nitish-raj@users.noreply.github.com" && \
    git config --global user.name "Nitish"

WORKDIR /workspace/
# RUN quarto install chromium --no-prompt
# RUN quarto install tinytex --no-prompt
RUN python3 -m pip install jupyter

# Ensure Git is initialized in the workspace
RUN git init

# You can uncomment these lines if you want to use renv
# COPY renv.lock renv.lock
# ENV RENV_PATHS_LIBRARY renv/library
# RUN R -e "renv::restore()"
# RUN R -e "renv::repair()"