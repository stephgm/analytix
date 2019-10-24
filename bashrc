# .bashrc

# Source global definitions
if [ -f /etc/bashrc ]; then
	. /etc/bashrc
fi

# User specific aliases and functions
shopt -s extglob
export PS1="$(tty)\n\w\n[\u@\h \W]\$ "
export PS1="\e[2;94m[\d \t]\e[0m\n\[\e[7;49;37m\]\w\[\e[0m\n\u@\h \W]\$ "
#export PREFIX="/storage/data/anaconda2-5.1.0"
export PREFIX="/storage/data/local"
#export PREFIX="/storage/data/anaconda3-5.1.0"
#export PATH="${PREFIX}/bin:/usr/local/bin:/usr/bin:/bin:/usr/local/sbin:/usr/sbin:/sbin"
#export LD_LIBRARY_PATH="${PREFIX}/lib:${PREFIX}/lib64:/lib64:/usr/lib64:/usr/local/lib64:/lib:/usr/lib:/usr/local/lib"
#export PATH="/usr/local/bin:/usr/bin:/bin:/usr/local/sbin:/usr/sbin:/sbin:${PREFIX}/bin"
export PATH="${PREFIX}/bin:/usr/local/bin:/usr/bin:/bin:/usr/local/sbin:/usr/sbin:/sbin"
export LD_LIBRARY_PATH="/lib64:/usr/lib64:/usr/local/lib64:/lib:/usr/lib:/usr/local/lib:${PREFIX}/lib:${PREFIX}/lib64"
export GEOS_DIR="${PREFIX}"
export PYTHONHTTPSVERIFY=0
alias lt="ls -ltr"
alias ll="ls -lh"
alias pipi="pip install --trusted-host pypi.python.org --trusted-host pypi.org --trusted-host files.pythonhosted.org"
alias pipv="pip --trusted-host pypi.python.org --trusted-host pypi.org --trusted-host files.pythonhosted.org"
alias dev="cd ~/src/analytix"
