#=================================Renad Jqaim==================================================
#====================the following script to show sg that open from anywhere===========================
import boto3
from tkinter import Tk, Label, Button, Listbox, Scrollbar, StringVar, Toplevel, END, filedialog

def fetch_security_groups(profile_name):
    session = boto3.Session(profile_name=profile_name)
    ec2 = session.client('ec2')
    
    security_groups = ec2.describe_security_groups()['SecurityGroups']
    sg_data = []

    for sg in security_groups:
        for permission in sg.get('IpPermissions', []):
            for ip_range in permission.get('IpRanges', []):
                if ip_range.get('CidrIp') == '0.0.0.0/0':
                    sg_data.append({
                        'GroupName': sg.get('GroupName', 'N/A'),
                        'GroupId': sg.get('GroupId', 'N/A'),
                        'Description': sg.get('Description', 'N/A')
                    })
                    break

    return sg_data

def list_security_groups():
    profile = profile_var.get()
    try:
        sg_data = fetch_security_groups(profile)
        listbox.delete(0, END)  
        for sg in sg_data:
            listbox.insert(END, f"Name: {sg['GroupName']} | ID: {sg['GroupId']} | Desc: {sg['Description']}")
    except Exception as e:
        listbox.insert(END, f"Error fetching security groups: {str(e)}")

def export_to_csv():
    profile = profile_var.get()
    sg_data = fetch_security_groups(profile)
    if not sg_data:
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
    )
    if file_path:
        with open(file_path, 'w') as f:
            f.write("GroupName,GroupId,Description\n")
            for sg in sg_data:
                f.write(f"{sg['GroupName']},{sg['GroupId']},{sg['Description']}\n")

def show_profiles():
    profiles = boto3.Session().available_profiles
    for profile in profiles:
        profile_listbox.insert(END, profile)

def select_profile(event):
    selected_profile = profile_listbox.get(profile_listbox.curselection())
    profile_var.set(selected_profile)

# Tkinter GUI
root = Tk()
root.title("LTM Security Group Viewer")
root.geometry("600x400")

profile_var = StringVar()
profile_var.set("default")

Label(root, text="LTM Security Group Viewer", font=("Arial", 16)).pack(pady=10)
Label(root, text="Select AWS Profile:").pack()

profile_listbox = Listbox(root, height=5, selectmode="single")
profile_listbox.pack(pady=5)

Button(root, text="Fetch Security Groups", command=list_security_groups).pack(pady=5)
Button(root, text="Export to CSV", command=export_to_csv).pack(pady=5)

listbox = Listbox(root, height=10, width=80)
listbox.pack(pady=10)

scrollbar = Scrollbar(root, orient="vertical", command=listbox.yview)
scrollbar.pack(side="right", fill="y")
listbox.config(yscrollcommand=scrollbar.set)

profile_listbox.bind("<<ListboxSelect>>", select_profile)

show_profiles()  

root.mainloop()
