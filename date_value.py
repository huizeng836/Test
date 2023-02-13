import pandas as pd
import datetime
import holidays



def convert_date(input_date):
    dt = input_date.strip()
    ans = datetime.date(int(dt[6:]), int(dt[3:5]), int(dt[:2]))
    return ans

def get_nz_holidays():
    current_year = datetime.date.today().year
    
    next_year = current_year + 1
    nz_holiday = holidays.NewZealand(years = range(current_year, next_year), prov = 'AUK')
    return list(nz_holiday.keys())

def get_date_profile(input_date):
    
    input_date = datetime.datetime.strptime(input_date, "%Y-%m-%d").strftime("%d/%m/%Y")
    
    convert_input_date = convert_date(input_date)
    dow = convert_input_date.strftime("%A")
    holiday = False
    ss = False
    if convert_input_date.month == 12:
        ss = True
    so_data = pd.read_excel('data/SO.xlsx')
    df = pd.DataFrame(so_data, columns = ['SO', 'UO'])
    
    school_open = True
    uni_open = True
    print(df['UO'].values)
    
    if input_date in df['SO'].values or holiday == True or (dow == 'Saturday' or dow == 'Sunday'):
        school_open = False

    if input_date in df['UO'].values or holiday == True or (dow == 'Saturday' or dow == 'Sunday'):
        uni_open = False

    
    print(f'DoW: {dow}, Public Holiday: {holiday}, School Open: {school_open}, Uni open: {uni_open}, Shopping: {ss}')




if __name__ == '__main__':
    get_date_profile("2023-02-13")
    
    #convert date from dd/mm/yyyy to date format
    # date = input("Date: ")
    # date = datetime.datetime.strptime(date, "%Y-%m-%d").strftime("%#d/%m/%Y")
    # dates = convert_date(date)

    # #check date is a nz public holiday or not
    # nz_holiday = holidays.NewZealand(years = range(2015, 2025), prov = 'AKL')
    # print(nz_holiday)
    # holiday = dates in nz_holiday

    # #day of the week
    # dow = dates.strftime("%A")

    # #shopping season
    # if dates.month != 12:
    #     ss = False
    # else:
    #     ss = True

    
    # so_data = pd.read_excel('SO.xlsx')
    # df = pd.DataFrame(so_data, columns = ['SO', 'UO'])

    # #School open
    # if date in df['SO'].values or holiday == True or (dow == 'Saturday' or dow == 'Sunday'):
    #     school_open = False
    # else:
    #     school_open = True

    # #Uni open
    # if date in df['UO'].values or holiday == True or (dow == 'Saturday' or dow == 'Sunday'):
    #     uni_open = False
    # else:
    #     uni_open = True
    
    # print(f'DoW: {dow}, Public Holiday: {holiday}, School Open: {school_open}, Uni open: {uni_open}, Shopping: {ss}')

