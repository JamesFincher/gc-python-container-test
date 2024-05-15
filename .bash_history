netstat
fuser
netstat
ps
help ps
ps --help
ps --list
ps -list
kill -9 $(lsof -i TCP:8000 | grep LISTEN | awk '{print $2}')
apt-get install lsof
sudo apt-get install lsof
kill -9 $(lsof -i TCP:8000 | grep LISTEN | awk '{print $2}')
