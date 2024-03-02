```
docker run -d --name erknet-db -e MYSQL_DATABASE=erknet -e MYSQL_USER=admin -e MYSQL_PASSWORD=erknet -e MYSQL_ROOT_PASSWORD=erknet-data -v erknet-data:/var/lib/mysql -p 3306:3306 mariadb:11.3
```

Open a command prompt and navigate to the directory 
```bash
cd path\to\your\project\backend
```

Create a virtual environment 
```bash
python -m venv venv
```

Activate the virtual environment:
```bash
venv\Scripts\activate
```

Installs all the packages listed in the requirements.txt file.
```bash
pip install -r requirements.txt
```

Populate the database
```bash
python model.py
```

Running The App
```bash
python main.py
```

```bash
cd path\to\your\project\frontend
```

Install the npm package
```bash
npm install
```

Install the expo package
```bash
npm install expo
```

run react native application
```bash
npx expo run
```