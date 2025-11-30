import requests
import json
import time
import pandas as pd
from mortgage import amortization_schedule
from fetch import generate_rental_estimate

API_KEY = "8de5a7ba9cmsh2858fb246877cc3p10d9e6jsnfe5932cb3231"
HOST = "realty-mole-property-api.p.rapidapi.com"
US_HOST = "us-real-estate.p.rapidapi.com"
US_RE_HOST = "us-real-estate-listings.p.rapidapi.com"
property_data = []
rental_data = []
research_params = {
  "location" : 'San Francisco, CA',
  "down_payment": 20.0,
  "interest_rate": 5.0, 
  "property_tax" : 1.2,
  "expense_ratio" : 0
}

def send_request(endpoint, params):
    url = f"https://{HOST}/{endpoint}"
    headers = {
        "content-type": "application/octet-stream",
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": HOST,
    }
    response = requests.get(url, headers=headers, params=params)
    return response

def get_rental_market_data(zipCode):
    endpoint = f"zipCodes/{zipCode}"
    params = {}
    response = send_request(endpoint, params)
    #print (response.json())
    return response.json()
  
def get_property_records(address):
    endpoint = "properties"
    params = {"address": address}
    return send_request(endpoint, params)

def get_property_sale_price(address):
    endpoint = "salePrice"
    params = {"address": address}
    return send_request(endpoint, params)

def get_property_rental_price(address):
    endpoint = "rentalPrice"
    params = {"address": address}
    return send_request(endpoint, params)

def get_property_listings(zipcode):
    endpoint = "saleListings"
    params = {"zipCode":zipcode, "propertyType":"Single Family", "limit":"10"}
    response = send_request(endpoint, params)
    data = json.loads(response.content.decode('utf-8'))
    return data['data']['home_search']['results']

def get_property_for_sale_by_location(location):
    endpoint = "for-sale"
    params = {"location":location,"offset":"0","limit":"50", "property_type":"single_family"}
    url = f"https://{US_RE_HOST}/{endpoint}"
    headers = {
      "content-type": "application/octet-stream",
    	"X-RapidAPI-Key": API_KEY,
    	"X-RapidAPI-Host": US_RE_HOST
    }
    response = requests.get(url, headers=headers, params=params)
  
    print (response)
    return json.loads(response.content.decode('utf-8'))

def get_property_for_sale(zipcode):
    endpoint = "v2/for-sale-by-zipcode"
    params = {"zipcode":zipcode,"offset":"0","limit":"42", "property_type":"single_family"}
    url = f"https://{US_HOST}/{endpoint}"
    headers = {
      "content-type": "application/octet-stream",
    	"X-RapidAPI-Key": API_KEY,
    	"X-RapidAPI-Host": US_HOST
    }
    response = requests.get(url, headers=headers, params=params)
    return json.loads(response.content.decode('utf-8'))

def calc_rent_adjustment(bedrooms, baths, sqft, delta_rent):
    if(int(bedrooms) == 1):
      delta_sqft = delta_rent*0.8/700
      rent_adj = (sqft - 700) * delta_sqft
      rent_adj += (baths - 1) * (delta_rent * 0.2)
    elif(int(bedrooms) == 2): 
      delta_sqft = delta_rent*0.8/700
      rent_adj = (sqft - 1400) * delta_sqft
      rent_adj += (baths - 2) * (delta_rent * 0.2)
    elif(int(bedrooms) == 3): 
      delta_sqft = delta_rent*0.8/600
      rent_adj = (sqft - 2000) * delta_sqft
      rent_adj += (baths - 2) * (delta_rent * 0.2)
    elif(int(bedrooms) == 4): 
      delta_sqft = delta_rent*0.7/500
      rent_adj = (sqft - 2500) * delta_sqft
      rent_adj += (baths - 2) * (delta_rent * 0.3)
    elif(int(bedrooms) > 4): 
      delta_sqft = delta_rent*0.5/900
      rent_adj = (sqft - 3400) * delta_sqft
      rent_adj += (baths - 4) * (delta_rent * 0.25)
      rent_adj += (bedrooms - 5) * (delta_rent * 0.25)
    #print (f"Adjusted rent: {rent_adj} {delta_rent} {bedrooms} {baths} {sqft}")  
    return round(rent_adj, 2)
  
def derive_rental_estimate(address, bedrooms, baths, sqft):
  rent_estimate = 0
  idx = 0
  static_idx = 0
  delta_rent = 0
  print (rental_data)
  minbeds = rental_data[0]['bedrooms']
  maxbeds = rental_data[-1]['bedrooms']
  for i in rental_data:
    idx += 1
    if(int(i['bedrooms']) == int(bedrooms)):
      break
  idx -= 1
  
  if(int(bedrooms) <= minbeds):
    delta_rent = rental_data[1]['averageRent'] - rental_data[0]['averageRent']
  elif(int(bedrooms) >= maxbeds):
    delta_rent = rental_data[idx]['averageRent'] - rental_data[idx-1]['averageRent']
  else:
    delta_rent1 = rental_data[idx]['averageRent'] - rental_data[idx-1]['averageRent']
    delta_rent2 = rental_data[idx+1]['averageRent'] - rental_data[idx]['averageRent']
    delta_rent = (delta_rent1 + delta_rent2)/2
  rent_estimate = rental_data[idx]['averageRent']
  rent_estimate += round(calc_rent_adjustment(int(bedrooms), int(baths), int(sqft), float(delta_rent)), 2) 
  #print (f"{address} {idx} {delta_rent} {rent_estimate}")
  return rent_estimate 
  
def get_rental_estimate(address, bedrooms, baths, sqft):
    url = "https://realty-mole-property-api.p.rapidapi.com/rentalPrice"
    querystring = {
        "address": address,
        "propertyType": "Single Family",
        "bedrooms": bedrooms,
        "bathrooms": baths,
        "squareFootage": sqft,
        "compCount": "5"
    }
    headers = {
        "X-RapidAPI-Key": "8de5a7ba9cmsh2858fb246877cc3p10d9e6jsnfe5932cb3231",
        "X-RapidAPI-Host": "realty-mole-property-api.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring)

    if "rent" in response.json():
        return float(response.json()["rent"])
    else:
        print (response.json())
        return 0.0
      
def get_address_line(address, city, state_code, postal_code):
    address_line = "{}, {}, {}, {}".format(address, city, state_code, postal_code)
    return address_line

def generate_rental_potentials(zipcode):
  decoded_rental_data = []
  #listings = get_property_for_sale(zipcode)
  #print (listings)
  #if(listings['status'] == 200): 
  #  results = listings['data']['home_search']['results']
  #else:
  listings = get_property_for_sale_by_location(zipcode)
  results = listings['listings']
    #print(listings['message'])
    #exit(listings['status'])
  rdata = get_rental_market_data(zipcode)
  #print (rdata['rentalData']['detailed'])
  for rental in rdata['rentalData']['detailed']:
    decoded_rent = {
        'bedrooms': rental['bedrooms'],
        'averageRent': rental['averageRent'],
        'minRent': rental['minRent'],
        'maxRent': rental['maxRent'],
        'totalRentals': rental['totalRentals']
    }
    rental_data.append(decoded_rent)
  #rental_data = decoded_rental_data
  #print (rental_data)
  return results

def collect_research_params():
    location = input("Enter Location (zipcode/city) for research: ")
    down_payment = input("Enter % of Down Payment: ")
    int_rate = input("Enter Current Mortgage Interest Rate: ")
    prop_tax = input("Enter Property Tax Rate for this Location: ")
    expenses = input("Enter Average Monthly Expenses (HoA, Insurance, Maintenance, etc.): ")
    incr_exp = input("Enter Yearly Rate of Increase in Expenses: ")
    incr_inc = input("Enter Yearly Rate of Increase in Rent Income: ")
    incr_val = input("Enter Yearly Rate of Increase in Property Value: ")
  
    exp_ratio = float(expenses)
    down_pmt = float(down_payment)
    irate = float(int_rate)
    property_tax = float(prop_tax) 
    
    research_params["location"] = location
    research_params["down_payment"] = down_pmt
    research_params["interest_rate"] = irate
    research_params["property_tax"] = property_tax
    research_params["expense_ratio"] = exp_ratio
    research_params["incr_exp"] = incr_exp
    research_params["incr_inc"] = incr_inc
    research_params["incr_val"] = incr_val
    
  
def collect_property_data():
  index = 0
  print(research_params)
  location = research_params['location']
  #location = input("Enter Location (zipcode/city) for research: ")
  results = generate_rental_potentials(location)
  down_payment = research_params['down_payment']
  int_rate = research_params['interest_rate']
  incr_exp = research_params['incr_exp']
  incr_inc = research_params['incr_inc']
  incr_val = research_params['incr_val']  
  
  for listing in results:
      address = listing['location']['address']['line']
      city = listing['location']['address']['city']
      state_code = listing['location']['address']['state_code']
      postal_code = listing['location']['address']['postal_code']
      if(postal_code == None): 
        postal_code = "00000"
      sqft = listing['description']['sqft']
      if(sqft == None):
        sqft = 0
      beds = listing['description']['beds']
      if(beds == None):
        beds = 0
      baths_full = listing['description']['baths_full']
      if(baths_full == None):
        baths_full = 0
      lot_sqft = listing['description']['lot_sqft']
      if(lot_sqft == None):
        lot_sqft = 0
      property_type = listing['description']['type']
      if(property_type == None):
        property_type = "Single Family"
      list_price = listing['list_price']
      if(list_price == None):
          list_price = 0
      address_line = get_address_line(address, city, state_code, postal_code)
      #print(f"List price: {list_price}, Down payment: {down_payment}, Interest rate: {int_rate}")
      loan_amount = list_price - (list_price*down_payment/100)
      invest_amount = list_price*down_payment/100
      loan_term = 30
      address_line = get_address_line(address, city, state_code, postal_code)
      #rental_estimate1 = get_rental_estimate(address_line, beds, baths_full, sqft)
      rental_estimate = derive_rental_estimate(address_line, beds, baths_full, sqft)
      #print(f"Address: {address_line} {rental_estimate1} {rental_estimate}")
      if(rental_estimate == None):
          rental_estimate = 0
      
      #Property Analysis
      amt_tab = amortization_schedule(int_rate, loan_amount, loan_term)
      prop_tax = research_params['property_tax']
      monthly_prop_tax = ((prop_tax/12)*list_price)/100
      monthly_exp = research_params['expense_ratio']
      amt_tab['total_exp'] = amt_tab['interest'] + monthly_exp + monthly_prop_tax
      amt_tab['total_inc'] = rental_estimate
      amt_tab['total_pnl'] = amt_tab['total_inc'] - amt_tab['total_exp'] 
      #print (f"List Price: {list_price} Loan Amount: {loan_amount} Invest Amount: {invest_amount} Rental Estimate: {rental_estimate}")
      
      #time.sleep(1)
      #print (".", end="")
      property_data.append({
          "index": index,
          "address": address,
          "address_line": address_line,
          "sqft": int(sqft),
          "beds": int(beds),
          "baths_full": int(baths_full),
          "lot_sqft": int(lot_sqft),
          "type": property_type,
          "list_price": round(float(list_price), 2),
          "rent_estimate": round(float(rental_estimate), 2),
          "amortization_schedule": amt_tab,
          "property_tax": prop_tax,
          "invest_amount": invest_amount,
          "monthly_exp": monthly_exp
      })
      yearly_data = analyze_property(index, incr_exp, incr_inc, incr_val)
      property_data[index]['yearly_stats'] = yearly_data
      index += 1
  print ("")

#def generate_rental_report(prop_data):
  

def analyze_property(prop_id, incr_exp, incr_inc, incr_val):
  #prop_data = property_data[int(prop_id)]
  yearly_exp = []
  yearly_inc = []
  yearly_val = []
  yearly_roi = []
  yearly_rroi = []
  yearly_iroi = []
  yearly_cf = []
  pdata = []
  yearly_texp = 0
  exp_mult = 1
  inc_mult = 1
  amt_tab = property_data[prop_id]['amortization_schedule']
  home_val = property_data[prop_id]['list_price']
  prop_tax = property_data[prop_id]['property_tax']
  monthly_exp = property_data[prop_id]['monthly_exp']
  invest_amount = property_data[prop_id]['invest_amount']   
  
  for index, row in amt_tab.iterrows():
    year = int(index/12)
    if(index%12 == 0):
      if (year!=0):
        exp_mult = float(exp_mult) + (float(incr_exp)/100)
        inc_mult = float(inc_mult) + (float(incr_inc)/100)
        yearly_val.append(yearly_val[year-1] * (1+float(incr_val)/100)) 
      else:
        exp_mult = 1
        inc_mult = 1
        yearly_val.append(home_val * (1+float(incr_val)/100))
      yearly_texp = 0
      yearly_exp.append(0)
      yearly_inc.append(0)
      yearly_cf.append(0)
      yearly_roi.append(yearly_val[year]-home_val)  
      yearly_iroi.append(round((yearly_roi[year]*100/invest_amount)/(year+1), 2))
    monthly_prop_tax = (prop_tax/12)*(yearly_val[year-1]/100)
    yearly_exp[year] = monthly_exp*exp_mult + monthly_prop_tax + row['interest'] + yearly_exp[year]
    yearly_inc[year] = row['total_inc']*inc_mult + yearly_inc[year]
    yearly_texp += row['principal']   
    yearly_cf[year] = yearly_inc[year] - (yearly_exp[year] + yearly_texp)
    if(index%12 == 11):
      yearly_rroi.append(round((yearly_inc[year-1]-yearly_exp[year-1])*100/invest_amount, 2))
      #print(f"Year {year}: Expenses: {round(yearly_exp[year], 2)}, Income: {round(yearly_inc[year], 2)}, CF: {round(yearly_cf[year], 2)}, Value: {round(yearly_val[year], 2)}, ROI: {round(yearly_roi[year], 2)} rROI: {yearly_rroi[year]}% iROI: {yearly_iroi[year]}%")
      pdata.append ({
        "Year": year,
        "Expenses": round(yearly_exp[year], 2),
        "Income": round(yearly_inc[year], 2),
        "Cash Flow": round(yearly_cf[year], 2),
        "Rental ROI": yearly_rroi[year],
        "Property Value": round(yearly_val[year], 2),
        "Yearly ROI": round(yearly_roi[year], 2),
        "Investment ROI": yearly_iroi[year]
      })
    #total_exp = row['total_exp']
    #total_inc = row['total_inc']
    #print (f"{index}: {total_exp:.2f} {total_inc:.2f}")
  #print (property_data[int(prop_id)]['amortization_schedule'])
  #print (pdata)
  pdf = pd.DataFrame(pdata)
  #print (pdf)
  return pdf
    
def print_rental_potentials():
  print("Listing Details:")
  print("{:<5} {:<24} {:<8} {:<6} {:<6} {:<10} {:<10} {:<10} {:<10}".format("Idx", "Address", 
                                                        "SqFt", "# Beds", "# Baths", "Price", 
                                                        "Rent Est", "+RoI Year", "+CF Year" 
                                                        ))
  for property in property_data:
    index = property['index']      
    address = property['address']
    sqft = property['sqft']
    beds = property['beds']
    baths_full = property['baths_full']
    list_price = property['list_price']
    rental_estimate = property['rent_estimate']
    pdf = property['yearly_stats']
    idx = 0
    cf_year = 0
    for cash_flow in pdf['Cash Flow']:
      idx += 1
      if(float(cash_flow) > 0):
        cf_year = idx
        #print (f"Cash Flow = {cash_flow} {idx}")
        break
    if(cf_year == 0):
      cf_year = 30
    idx = 0
    roi_year = 0
    for roi in pdf['Rental ROI']:
      idx += 1
      if(float(roi) > 0):
        roi_year = idx
        #print (f"ROI = {roi} {idx}")
        break
    if(roi_year == 0):
      roi_year = 30
    #pdf[pdf['Rental ROI'] > 0].index[1]
    print("{:<5} {:<24} {:<8} {:<6} {:<6} ${:<10} ${:<10} {:<10} {:<10}".format(index, address, sqft, beds, baths_full, list_price, rental_estimate, roi_year, cf_year))
  

def get_rental_estimate(address, bedrooms, baths, sqft):
    url = "https://realty-mole-property-api.p.rapidapi.com/rentalPrice"

    querystring = {
        "address": address,
        "propertyType": "Single Family",
        "bedrooms": str(bedrooms),
        "bathrooms": str(baths),
        "squareFootage": str(sqft),
        "compCount": "5"
    }

    headers = {
        "X-RapidAPI-Key": "f8afd74a7dmsh8feb825ecf24206p1f7ef5jsnb0b19e15db3b",
        "X-RapidAPI-Host": "realty-mole-property-api.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    return response.json()["rent"]

def plot_expense_vs_income(index):
  print(index, " Plot function is not ready yet!")
  
def print_main_menu():
  print("")
  print("Main Menu:")
  print("1. Collect Rental Research Parameters")
  print("2. Collect Rental Potentials based on city")
  print("3. Analyze Property from Potential list")
  print("4. Generate Rental Estimate Model")
  print("5. Exit")
  option = input("Enter the operation you like to perform: ")
  return option

def print_report(index):
  print (f"Address    : {property_data[index]['address_line']}")
  print (f"Sq. Ft.    : {property_data[index]['sqft']}")
  print (f"Bedrooms   : {property_data[index]['beds']}")
  print (f"Bathrooms  : {property_data[index]['baths_full']}")
  print (f"Lot Size   : {property_data[index]['lot_sqft']}")
  print (f"Price      : ${property_data[index]['list_price']}")
  print (f"Rent Est   : ${property_data[index]['rent_estimate']}")
  print (f"Invest Amt : ${property_data[index]['invest_amount']}")
  print ()
  pdf = property_data[index]['yearly_stats']
  print(pdf)
  
def main_function():
  option = print_main_menu()
  while (option != '5'):
    if(option == '3'):
      index = input("Enter the index of the property to analyze: ")
      print_report(int(index))
    elif(option == '4'):  
      #index = input("Enter the index of the property to plot: ")
      #plot_expense_vs_income(int(index))
      generate_rental_estimate(property_data)
    elif(option == '2'):
      collect_property_data()
      print_rental_potentials()
    elif(option == '1'):
      collect_research_params()
      print (research_params)
    option = print_main_menu()
  
main_function()

input_loan = 500000
input_years = 30

scenario1 = amortization_schedule(4.00, input_loan, input_years)
#scenario2 = amortization_schedule(3.00, input_loan, input_years)
#scenario3 = amortization_schedule(2.00, input_loan, input_years)

print (scenario1)
