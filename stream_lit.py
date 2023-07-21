import streamlit as st
from pathlib import Path
import os
from main import get_all_digitalized_data

# Title
st.title("Doc Digitalization")


st.header('Restricted File Extensions',)
uploaded_files = st.file_uploader('Upload your files',
 accept_multiple_files=True, type=['pdf'])

for file in uploaded_files:
    save_folder = 'pdfs'
    save_path = Path(save_folder, file.name)
    with open(save_path, mode='wb') as w:
        w.write(file.getvalue())
    path = os.path.join(save_folder,file.name)
    destination_path  = f"{file.name[:-4]}.json"
    df, order_des_details = get_all_digitalized_data(path,destination_path)
    st.header("File Name: {}".format(file.name))
    st.subheader("Order Details")
    st.success("Success")
    st.json(order_des_details)
    st.dataframe(df)
    os.remove(path)
    os.remove(destination_path)
    
    