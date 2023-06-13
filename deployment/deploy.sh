echo "Updating the system"
sudo apt-get update
echo "Installing libraries"
sudo pip3 install pycryptodome
echo "Preparing directories"
mkdir /opt/hip-vpls/
cd ..
echo "Copying the files"
rsync -rv  hiplib  switchd.py  switchfabric.py /opt/hip-vpls/
echo "Copying the service file"
cd startup
cp hip-vpls.service /etc/systemd/system/
sudo systemctl enable hip-vpls
sudo systemctl start hip-vpls

