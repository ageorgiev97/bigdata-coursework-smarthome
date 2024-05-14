<p align="center">
    <img src="https://cdn-icons-png.flaticon.com/256/10751/10751558.png" alt="Logo" >
    <h2 align="center">SmartHome Analytics: visualise and analyze your home!</h2>
    <p align="center">Coursework for BigData course at TU-Varna</p>
</p>


### How to setup:

The input sensor data must be placed in the `landing/` folder, adjacent to the `work.py` script.

When ran, it will pre-process the input json data, copy it to the hadoop filesystem, do some conversions and then 
upload them to the local mysql database.
It will automatically create all needed tables and databases. The script assumes 
that the user and password is default: user: `root`, password: `root`.
They can be changed in `work.py`. In the future will add it with an argument.

The script can be run automatically, by adding the following entry to `crontab -e`:
`0 0 * * * <path-to-work.py>`
This will run the job once every day at midnight, which is the recommended interval.
It can also be directly invoked from the command line at any time.

For the dashboard we again assume that the mysql user and password are `root`. Can be changed in `dashboard/app.py`.
Before running `dashboard/app.py` we must run `pip install -r requirements.txt` in the repository working dir.

After running it we can check the dashboard at http://127.0.0.1:8050/


Tested with:

| Tool     | Version | 
| -------- |---------| 
| Python   | 3.8.9   | 
| Hadoop   | 3.3.0   | 
| Hive     | 3.1.2   | 
| Sqoop    | 1.4.7   | 
| MySql    | 8.0.25  | 
