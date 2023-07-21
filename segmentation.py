import re 

def company_detail_box1(data):
  company_box1_details = {}
  company_dls = data['company_details'].split('\n')
  while("" in company_dls ):
    company_dls.remove("")
  company_country = company_dls[-1]
  cp_name = company_dls[0].split('(')[0]
  company_address = ' '.join(company_dls[1:-1])
  state_zip = company_dls[-2].split()
  state_name = ' '.join(state_zip[:-1])
  zip_code = state_zip[-1]
  company_box1_details["Company_Name"] = cp_name
  company_box1_details["State"] = state_name
  company_box1_details["Country"] = company_country
  company_box1_details["ZipCode"] = zip_code
  company_box1_details["Company_Address"] = company_address
  return company_box1_details

def extract_details_from_Other_Details_right(data):
  company_name = ""
  customer_name = ""
  other_address_dict = {}
  other_add = data['other_address_details']
  splited_data = other_add.split('\n')
  while("" in splited_data):
    splited_data.remove("")
  your_company_and_name = splited_data[0].split(",")
  tax_id_data = [i for i in splited_data if "Tax ID" in i ]
  tax_id = tax_id_data[0].split(':')[-1] if len(tax_id_data) else ""
  if len(your_company_and_name)==2:
    company_name,customer_name = your_company_and_name
  else:
    customer_name = your_company_and_name[0]

  company_add = ' '.join(splited_data[1:-2]) if tax_id else ' '.join(splited_data[1:-1])
  country = splited_data[-2] if tax_id  else splited_data[-1]
  zip_code = splited_data[-3] if tax_id else splited_data[-2]
  other_address_dict["Company_Name"] = company_name
  other_address_dict["Customer_Name"] = customer_name
  other_address_dict["Full Company Address"] = company_add
  other_address_dict["Tax ID"] = tax_id
  other_address_dict["Country_Name"] = country
  other_address_dict["ZipCode"] = company_add.split()[-1]
  return other_address_dict

def get_left_invoice_shipping_details(data):
    shiiping_details = {}
    
    if data["invoice_shipping_address"]:
        invoice_data = data["invoice_shipping_address"].replace("&","").split('\n')
        phone_number = ""
        if invoice_data:
            while("" in invoice_data):
                invoice_data.remove("")
            phone_number = invoice_data[-1]
            company_and_name = invoice_data[1].split(',')
            if len(company_and_name)==2:
                company_name,name = company_and_name
            else:
                name = company_and_name[0]
            country = invoice_data[-2]
            state_zip = invoice_data[-3].split()
            state = ' '.join(state_zip[:-1])
            zip_code = state_zip[-1]
            shiiping_details["Name"] = name
            shiiping_details["Company"] = company_name
            shiiping_details["State"] = state
            shiiping_details["ZipCode"] = zip_code
            shiiping_details["Country"] = country
            shiiping_details["Phone"] = phone_number
        
    return shiiping_details
    

def gettax_data(tax_data):
    tax_amount = ""
    tax_percentage = ""
    txt_data_text = tax_data
    if txt_data_text:
        tp,ta = txt_data_text.split("Tax")[-1].split("%")
        if "on" in ta:
            tax_amount = re.split(r"\d+",ta,maxsplit=2)[-1][2:]
        else:
            tax_amount = ta
        tax_percentage = tp
    return tax_amount, tax_percentage

def get_tax_untaxted_amount_data(json_data):
    
    tax_amount,tax_percentage = gettax_data(json_data["Tax_data"])
    tax_percentage = float(tax_percentage) if tax_percentage else 0
    total_amount = json_data["Total_data"].split("Total")[-1]
    untaxed_amount = json_data["Untaxed_data"].split("Amount")[-1]
    res =  {"Tax_percentage(%)":tax_percentage, "Tax_amount":tax_amount, "Total_amount":total_amount, "untaxed_amount":untaxed_amount}
    return res
    

def get_order_des_details(data):
    order_id = data["Order_Id_detail"].split()[-1]
    oder_des_detail = data["Order_desc_detail"]
    keys = [i for i in oder_des_detail[0].split(":") if i!=""]
    val_data = data["Order_desc_detail"][1].split()
    values = val_data[:-2]
    values.append(' '.join(val_data[-2:]))
    res = {keys[i]: values[i] for i in range(len(keys))}
    order_des_details = {**{"Order_ID":order_id}, **res}
    
    return order_des_details
        
        