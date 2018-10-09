from ubuntu:18.04

# Run apt to install OS packages
RUN apt update
RUN apt install -y tree vim curl python3 python3-pip git

# Python 3 package install example
RUN pip3 install ipython matplotlib numpy pandas scikit-learn scipy six

# create directory for "work".
RUN mkdir /work

# clone the rich context repo into /rich-context-contest
RUN git clone https://github.com/NYU-Chicago-data-facility/rich-context-contest.git /rich-context-contest

LABEL maintainer="jonathan.morgan@nyu.edu"