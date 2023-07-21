from table_data import extracted_slip_data
from segmentation import company_detail_box1, extract_details_from_Other_Details_right,\
    get_left_invoice_shipping_details, get_tax_untaxted_amount_data,get_order_des_details

from table_read_from_pdf import get_order_data
import json
import pandas as pd


def get_all_digitalized_data(pdf_path,destination_dir_json = "order_details.json"):
    extracted_slip_data(pdf_path,destination_dir_json)
    data = json.load(open(destination_dir_json))
    all_order_details_json = []
    all_df = pd.DataFrame()
    for i in range(len(data)):
        box1 = company_detail_box1(data[i])
        left_box2 = get_left_invoice_shipping_details(data[i])
        right_box2 = extract_details_from_Other_Details_right(data[i])
        address_data = {"Company_Address":box1, "Ship_Address1": left_box2, "Ship_Address2": right_box2}
        tax_untax_amount = get_tax_untaxted_amount_data(data[i])
        order_Des_details = get_order_des_details(data[i])
        total_order_count = len(data[i]["Orders"])
        all_data_injson = {**address_data,**order_Des_details,**tax_untax_amount}
        order_table_in_df,order_list_dicts = get_order_data(pdf_path,all_data_injson,i,total_order_count)
        all_data_injson = {**all_data_injson,**order_list_dicts}
        all_order_details_json.append(all_data_injson)
        all_df = pd.concat([all_df, order_table_in_df])
        
    return all_df, all_order_details_json
