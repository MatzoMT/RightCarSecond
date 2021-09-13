import mysql.connector
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Recognized as popular carmakers by autotrader.com
car_makers = [
    "ACURA",
    "ALFA ROMEO",
    "AMC",
    "ASTON MARTIN",
    "AUDI",
    "BENTLEY",
    "BMW",
    "BUGATTI",
    "BUICK",
    "CADILLAC",
    "CHEVROLET",
    "CHRYSLER",
    "DAEWOO",
    "DATSUN",
    "DELOREAN",
    "DODGE",
    "EAGLE",
    "FERRARI",
    "FIAT",
    "FISKER",
    "FORD",
    "FREIGHTLINER",
    "GENESIS",
    "GEO",
    "GMC",
    "HONDA",
    "HYUNDAI",
    "INFINITI",
    "ISUZU",
    "JAGUAR",
    "JEEP",
    "KARMA",
    "KIA",
    "LAMBORGHINI",
    "LAND ROVER",
    "LEXUS",
    "LINCOLN",
    "LOTUS",
    "MASERATI",
    "MAYBACH",
    "MAZDA",
    "MCLAREN",
    "MERCEDES BENZ",
    "MERCEDES-BENZ",
    "MERCURY",
    "MINI",
    "MITSUBISHI",
    "NISSAN",
    "OLDSMOBILE",
    "PLYMOUTH",
    "POLESTAR",
    "PONTIAC",
    "PORSCHE",
    "ROLLS ROYCE",
    "ROLLS-ROYCE",
    "RAM",
    "SAAB",
    "SATURN",
    "SCION",
    "SMART",
    "SRT",
    "SUBARU",
    "SUZUKI",
    "TESLA",
    "TOYOTA",
    "VOLKSWAGEN",
    "VOLVO",
    "YUGO"
]

def parse_years():
    # Establishes connection with databae located on computer
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="password",
        database="car_project"
    )


    
    url = "https://webapi.nhtsa.gov/api/Recalls/vehicle?format=json"
    source_code = requests.get(url)
    plain_text = source_code.text
    # Converts JSON information into Python dictionary
    site_json = json.loads(plain_text)

    error_count = 0
    error_string=""

    # for loop parses each year given in results URL above except for placeholder 9999
    for year in site_json["Results"]:
        if year["ModelYear"] != "9999":
            # Following URL returns list of automakers registered for the selected year
            url_year = "https://webapi.nhtsa.gov/api/Complaints/vehicle/modelyear/" + year["ModelYear"] + "?format=json"
            source_code_year = requests.get(url_year)
            plain_text_year = source_code_year.text
            year_site_json = json.loads(plain_text_year)
            
            # for loop that takes the parsed year and automaker to search for its models for that year
            for make in year_site_json["Results"]:
                if make["Make"] not in car_makers:
                    continue
                try:
                    url_make = "https://webapi.nhtsa.gov/api/Complaints/vehicle/modelyear/" + year["ModelYear"] + "/make/" + make["Make"] + "?format=json"
                    source_code_make = requests.get(url_make)
                    plain_text_make = source_code_make.text
                    make_site_json = json.loads(plain_text_make)
                except:
                    error_count = error_count + 1
                    error_string = error_string + " " + year["ModelYear"] + " " + make["Make"] + "\n"
                    print("ERROR")

                # for loop that inserts each model into database
                for model in make_site_json["Results"]:
                    try:
                        url_model = "https://webapi.nhtsa.gov/api/Complaints/vehicle/modelyear/" + year["ModelYear"] + "/make/" + make["Make"] + "/model/" + model["Model"] + "?format=json"
                        source_code_model = requests.get(url_model)
                        plain_text_model = source_code_model.text
                        model_site_json = json.loads(plain_text_model)

                      #  print(year["ModelYear"] + " " + make["Make"] + " " + model["Model"] + " " + str(model_site_json["Count"]))
                        mycursor = mydb.cursor()
                        value = [year["ModelYear"],make["Make"],model["Model"],str(model_site_json["Count"])]
                        print(value)
                        #mycursor.execute('INSERT INTO car_information (Year, Make, Model, Complaints) VALUES (%s,%s,%s,%s)',value)
                        mycursor.execute('INSERT INTO car_info (Year, Make, Model, Complaints) VALUES (%s,%s,%s,%s)',value)
                        mydb.commit()
                    except Exception as e:
                        print(e)
                        error_count = error_count + 1
                        error_string = error_string + " " + year["ModelYear"] + " " + make["Make"] + "\n"
                #print(year["ModelYear"] + make["Make"])

    print("Number of errors: " + str(error_count))
    print("Error models: " + error_string)
                
# Writes sales of available models into database
def write_sales_into_database():
    # Establishes connection with database located on computer
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="password",
        database="car_project"
    )

    current_year = datetime.now().year

    while current_year > 1990:
        for car_maker in car_makers:
            url_make = "https://webapi.nhtsa.gov/api/Complaints/vehicle/modelyear/" + str(current_year) + "/make/" + car_maker + "?format=json"
            source_code_make = requests.get(url_make)
            plain_text_make = source_code_make.text
            make_site_json = json.loads(plain_text_make)       
            for model in make_site_json["Results"]: 

                print(model)
                sales_link = "https://carsalesbase.com/us-" + car_maker + "-" + model["Model"] + "/"
                html_text = requests.get(sales_link).text
                soup = BeautifulSoup(html_text, 'html.parser')
                try:
                    table = soup.find_all('table')[1]
                    tds = table.find_all('td')
                    counter = 0
                    td_counter = 0
                    for td in tds:
                        counter = counter + 1
                        # if statement reassigns year only if it is the first iteration
                        if td_counter % 2 == 1:
                            year = td.find_next('td').text.replace('.', '')
                        td_counter = td_counter + 1
                        if td_counter >= 2:
                            if counter % 2 == 1:
                                sale = td.find_next('td').text.replace('.', '') 
                                # reflects common U.S. convention of selling model with one additional model year
                                model_year = int(year) + 1
                                print(str(model_year) + " " + car_maker + " " + model["Model"] + ": " + sale) 
                        #print(td.find_next('td').find_next('td'))
                except:
                    print("Error: ")

        current_year = current_year - 1

    return current_year

def get_all_complaints(make, model, dict):
    # Establishes connection with databae located on computer
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="password",
        database="car_project"
    )
    # cursor set to buffered so that all results are fetched
    mycursor = mydb.cursor(buffered=True)
    #value = [year["ModelYear"],make["Make"],model["Model"],str(model_site_json["Count"])]
    #mycursor.execute("select Make, Model, Complaints from car_project.car_information where Make='HYUNDAI' and MODEL='SONATA'")
    query = "SELECT Year, Complaints FROM car_project.car_information WHERE Make='{}' AND Model='{}' ORDER BY Year DESC".format(make.upper(),model.upper())
    print(query)
    mycursor.execute(query)

    rows = mycursor.fetchall()
    for row in rows:
        counter = 0
        year = 0
        for col in row:
            if counter == 0:
                year = col
                counter = counter + 1
                continue
            #print("cmd%s," % col)
            dict[int(year)] = int(col)
            counter = 0

    #mydb.commit()
            


#parseYears()

"""
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="password",
  database="car_project"
)

mycursor = mydb.cursor()

sql = "INSERT INTO car_information (Year, Make, Model) VALUES (%s, %s, %s)"
val = ("2015","Volkswagen", "Passat")
mycursor.execute(sql, val)

mydb.commit()

print(mycursor.rowcount, "record inserted.")
"""