import cv2
import pytesseract
import json
from pdf2image import convert_from_path
import os
from webcolors import name_to_rgb
from dotenv import load_dotenv
load_dotenv()
pytesseract_path = os.getenv("PYTESSERACT_PATH")
pytesseract.pytesseract.tesseract_cmd = pytesseract_path

def decorate_function(func):
    print(func,"this function is running")
    return func

def create_rectangle(img,xy1 = (0,0),xy2 =  (2200,1800), color_name = "black"):
    color = name_to_rgb(color_name)
    img = cv2.rectangle(img, xy1,xy2, color=color, thickness=2)
    return img

@decorate_function
def convert_pdf_to_image(pdf_path):
    images = convert_from_path(pdf_path,
                               poppler_path = os.getenv("POPPLER_PATH") )
    return images


@decorate_function
def get_address_and_order_segmentation(full_image_path):
    image = cv2.imread(full_image_path)
    company_and_shipping_details = image[125:643,]
    order_details = image[630:1800,:]
    # cv2.imwrite(f"imgs\order_details.jpg", order_details)
    
    return company_and_shipping_details, order_details

def mark_region(real_image,area_range = 8800 ):
    global image 
    im = real_image

    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (9,9), 0)
    thresh = cv2.adaptiveThreshold(blur,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,11,30)

    # Dilate to combine adjacent text contours
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9,9))
    dilate = cv2.dilate(thresh, kernel, iterations=4)

    # Find contours, highlight text areas, and extract ROIs
    cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    line_items_coordinates = []
    lines_coor_area = []
    count = 1

    for c in cnts:
        area = cv2.contourArea(c)
        x,y,w,h = cv2.boundingRect(c)
        if y >= 0 and x <= 1000:
            if area>area_range:
                image = cv2.rectangle(im, (x,y), (2200, y+h), color=(0,255,0), thickness=2)
                # cv2.putText(image, f"area: {area}, count: {count}", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36,255,12), 2)
                line_items_coordinates.append([(x,y), (2200, y+h)])
                lines_coor_area.append([(x,y), (2200, y+h),(area)])
                count+=1
        if y >= 2400 and x<= 2000:
            image = cv2.rectangle(im, (x,y), (2200, y+h), color=(255,0,255), thickness=2)
            line_items_coordinates.append([(x,y), (2200, y+h)])
            lines_coor_area.append([(x,y), (2200, y+h),(area)])
    
    return image, line_items_coordinates,lines_coor_area

def remove_overlapped_boxes(image):
    indices = []
    # real_img = cv2.imread(image_path)
    img,lines,line_area = mark_region(image)

    for i in range(len(lines)):
        x1,y1 = lines[i][0]
        x2,y2 = lines[i][1]
        for j in range(len(lines)):
                tx1,ty1 = lines[j][0]
                tx2,ty2 = lines[j][1]
                if i==j:
                    continue
                else:
                    if (y1<=ty1) and (y2>=ty2) and (x1<=tx1) and (x2>=tx2):
                        indices.append(j)
         
    for ind in indices:
        lines.pop(ind)
        
    return lines


@decorate_function   
def get_company_shipment_details(cropped_company_shipped_details_img):
    json_data = {}
    address_image = cropped_company_shipped_details_img
    company_address = address_image[:200,]
    
    shipping_and_other_address = address_image[201:,]
    
    other_add = shipping_and_other_address[:,:900]
    invoice_shipping_address = shipping_and_other_address[:,900:]
    
    json_data["company_details"] = str(pytesseract.image_to_string(company_address,config='--psm 6'))
    other_add_res = str(pytesseract.image_to_string(other_add,config='--psm 6'))
    if (len(other_add_res.split('\n')))>2:
        json_data["invoice_shipping_address"] = other_add_res
    else:
        json_data["invoice_shipping_address"]  = ""
    json_data["other_address_details"] = str(pytesseract.image_to_string(invoice_shipping_address,config='--psm 6'))
    return json_data

@decorate_function
def get_order_details1(order_img,i):
    order_detail_dict1 = {}
    image = order_img
    start_ind = 0
    end_ind = 0
    untaxed_data = ""
    taxed_data = ""
    total_data = ""
    data = str(pytesseract.image_to_string(order_img,config='--psm 6')).split('\n')
    while ("" in data):
        data.remove("")
    for i in range(len(data)):
        if data[i].startswith("Order") or (data[i].startswith("Quotation")) or (data[i].startswith("Your Reference")):
            
            if ("Date" not in data[i]):
                order_detail_dict1["Order_Id_detail"] = data[i]
                
            else:
                order_detail_dict1["Order_desc_detail"] = data[i:i+2]
        
        elif data[i].startswith("Description"):
            order_detail_dict1["order_detail_column"] = data[i]
            if not start_ind:
                start_ind = i+1
        
        elif data[i].startswith("Untaxed") or data[i].startswith("Tax") or data[i].startswith("Total"):
            if not end_ind:
                end_ind = i
            if data[i].startswith("Untaxed"):
                untaxed_data = data[i]
            
            elif data[i].startswith("Tax"):
                taxed_data = data[i]
                
            elif data[i].startswith("Total"):
                total_data = data[i]
    data_list = data[start_ind:end_ind]

    all_orders = []
    for dt in data_list:
        numeric_data = []
        
        for i in dt.split():  
            
            try:
                i = float(i)
                numeric_data.append(i)
            except:
                pass

        if len(numeric_data):
            all_orders.append(dt)
        
    order_detail_dict1[f"Orders"] = all_orders
    order_detail_dict1["Untaxed_data"] = untaxed_data
    order_detail_dict1["Tax_data"] = taxed_data
    order_detail_dict1["Total_data"] = total_data
 
    return order_detail_dict1

    
@decorate_function  
def extracted_slip_data(pdf_path,json_filename):
    imgs_main_dir = "imgs"
    images = convert_pdf_to_image(pdf_path)
    all_image_data = []
    
    for i in range(len(images)):

    # Save pages as images in the pdf
        images[i].save(imgs_main_dir+'\page' + str(i) + '.jpg', 'JPEG')
        img = imgs_main_dir+'\page' + str(i) + '.jpg'
        address_Details_img,order_details_img = get_address_and_order_segmentation(img)
        company_data = get_company_shipment_details(address_Details_img)
        order_details = get_order_details1(order_details_img,i)
        full_extracted_data = {**company_data, **order_details}
        all_image_data.append(full_extracted_data)
        os.remove(img)

        with open(json_filename, "w") as json_file:
            json.dump(all_image_data, json_file,indent=2)
    


