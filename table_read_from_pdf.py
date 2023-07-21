import camelot
import os
import pandas as pd
import numpy as np
pdf_path = "pdfs\Quotation _ Order.pdf"


def get_order_data(pdf_path,order_data,i=0,total_order_count = 1):
    tables = camelot.read_pdf(pdf_path, flavor='stream',pages="all")
    df = tables[i].df.to_dict()
    df = pd.DataFrame(df)
    
    df.replace("",np.nan,inplace=True)
    try:
        df.dropna(thresh = df.shape[1]-2,axis=0,inplace=True)
    except:
        df.dropna(thresh = 5,axis=0,inplace=True)
    
    order_df = df.reset_index(drop=True)
    start_ind = order_df[order_df[0]=="Description"].index[0]
    order_df = order_df.loc[start_ind:].reset_index(drop=True)
    order_df.dropna(axis = 1,inplace=True,how = "all")
    order_df.columns = order_df.loc[0]
    order_df.drop(0,inplace=True)
    order_df.dropna(axis=0,inplace=True,thresh= 3)        
    splitting_cols = [col for col in order_df.columns if "\n" in col]
    column_names = [col.split('\n') for col in splitting_cols]
    new_df = order_df
    if splitting_cols:
        for j in range(len(splitting_cols)):
            new_df[column_names[j]] = order_df[splitting_cols[j]].str.split(pat='\n', expand=True)
            new_df.drop(splitting_cols[j],inplace=True,axis=1)
    
    if new_df.shape[0]==total_order_count:
        new_order_df = new_df
    else:
        new_order_df = new_df.loc[:total_order_count]
    order_list_dict = {}
    all_orderlist = []
    for ind in new_order_df.index:
        row = new_order_df.loc[ind].to_dict()
        all_orderlist.append(row)
    order_list_dict["order_lines"] = all_orderlist
    new_order_df["Order_ID"] = order_data["Order_ID"]
    
    final_order_detail = new_order_df[["Order_ID","Description","Quantity","Unit Price","Taxes","Tax excl.","Tax incl."]]
    return final_order_detail, order_list_dict

# path = f"pdfs\Quotation _ Order.pdf"
# print(get_order_data(path))

# for i in range(40):
#     path = f"pdfs\sp_pdfs\document-page{i}.pdf"
#     print(get_order_data(path))

