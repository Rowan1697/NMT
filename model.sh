virtualenv -p python3.7 env
source env/bin/activate

pip install -r requirements.txt

pip install gdown
mkdir model
cd model
gdown https://drive.google.com/uc?id=1okPd4ifQQuWrEH5hiz6ikX8G8EBoGVOk
gdown https://drive.google.com/uc?id=1_djURBJCIToETfTXCRrX2N5gN1qRukHe
gdown https://drive.google.com/uc?id=15wjG2d09DAw8P7kU09oM4UfRplkpRKYU
gdown https://drive.google.com/uc?id=1TFbXFSUhGTb9aopgssM6Hn86Cyoh-38K

cd ..
cd nematus
python setup.py install
