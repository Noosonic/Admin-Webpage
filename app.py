import streamlit as st
from datetime import date
import firebase_admin
from firebase_admin import credentials, firestore

fileName = str(date.today())
fileName = fileName + ".csv"

if not firebase_admin._apps:
    cred = credentials.Certificate("certificate.json")
    app = firebase_admin.initialize_app(cred)

store = firestore.client()

collection_name = fileName

doctorFileName = "DoctorList.csv"
clientFileName = "ClientList.csv"
settingFileName = "Setting.csv"

def settingChanges(DailyLimit, WalkInLimit):
    store.collection(settingFileName).document("Settings").update({"DailyLimit":int(DailyLimit)})
    store.collection(settingFileName).document("Settings").update({"WalkInLimit":int(WalkInLimit)})

def deleteData(type):
    docs = store.collection(collection_name).get()
    if type == "All":
        for doc in docs:
            key = doc.id
            store.collection(collection_name).document(key).delete()
    else:
        for doc in docs:
            if doc.id == type:
                store.collection(collection_name).document(doc.id).delete()
                break

def deleteDoctor(type):
    docs = store.collection(doctorFileName).get()
    if type == "All":
        for doc in docs:
            key = doc.id
            store.collection(doctorFileName).document(key).delete()
    else:
        for doc in docs:
            if doc.id == type:
                store.collection(doctorFileName).document(doc.id).delete()
                break

def deleteClient(type):
    docs = store.collection(clientFileName).get()
    if type == "All":
        for doc in docs:
            key = doc.id
            store.collection(clientFileName).document(key).delete()
    else:
        for doc in docs:
            if doc.id == type:
                store.collection(clientFileName).document(doc.id).delete()
                break

def uploadData(data, naming):
    store.collection(collection_name).document(naming).set(data)

def retriveData(type):
    data = []

    docs = store.collection(collection_name).get()
    for doc in docs:
        data.append(doc.to_dict())

    if type == "ID":
        IDs = []
        for each in data:
            IDs.append(each["Queue ID"])
        return IDs
    elif type == "All":
        return data
    else:
        for each in data:
            if (type == each["Queue ID"]):
                return each["Status"]

def updateData(QueueID, newStatus):
    docs = store.collection(collection_name).get()
    for doc in docs:
        key = doc.id
        temp = doc.to_dict()
        if QueueID == temp["Queue ID"]:
            store.collection(collection_name).document(key).update({"Status":newStatus})
            break

def uploadDoctor(doctor, naming):
    store.collection(doctorFileName).document(naming).set(doctor)

def retriveDoctor(caller):
    data = []

    docs = store.collection(doctorFileName).get()
    for doc in docs:
        data.append(doc.to_dict())

    if caller == "client":
        doctorNames = []
        for each in data:
            doctorNames.append(each["Doctor Name"])
        return doctorNames
    elif caller == "doctor":
        doctorInfo = []
        for each in data:
            doctorInfo.append([each["Doctor Name"], each["Password"]])
        return doctorInfo

def retrivePatients(doctor):
    data = retriveData("All")
    subData = []
    for each in data:
        subData.append(each["Queue ID"])
    return subData

def uploadClient(doctor, naming):
    store.collection(clientFileName).document(naming).set(doctor)

def retriveClient():
    data = []

    docs = store.collection(clientFileName).get()
    for doc in docs:
        data.append(doc.to_dict())

    naming = []
    for each in data:
        naming.append(each["Client Name"])
    return naming

# ---------------------------------------------------------------------------------

def callQueue(queueNumber):
    data = retriveData("All")
    for each in data:
        if queueNumber == each["Queue ID"]:
            return each

def register(name):
    # readFile = open("DoctorList.csv", "r")
    # reader = csv.reader(readFile)
    reader = retriveDoctor("client")
    for row in reader:
        if row == name:
            return False
    # readFile.close()

    uploadDoctor({"Doctor Name": name}, name)
    return True

# ---------------------------------------------------------------------------------

if "DoctorName" not in st.session_state:
    st.session_state.DoctorName = "Unknown"

def initiatGlobalVariables():
    global loginButton
    global patientList
    global CheckPatient
    global CallPatient
    global UncallPatient
    global Complete

initiatGlobalVariables()

patientCallForm = st.empty()
patientForm = patientCallForm.form("PatientCall", clear_on_submit=False)

patientList = patientForm.selectbox("เลือกคิว", retrivePatients(st.session_state.DoctorName))


CheckPatient = patientForm.form_submit_button("ตรวจสอบข้อมูล")

CallPatient = patientForm.form_submit_button("เรียกคิว")

UncallPatient = patientForm.form_submit_button("หยุดเรียกคิว")

Complete = patientForm.form_submit_button("เสร็จสิ้นคิว")

if CheckPatient:
    QueueNumber = callQueue(patientList)
    st.text("ข้อมูลผู้ป่วย\nQueue ID: {}\nชื่อ: {}\nมาหาคุณหมอ: {}\nเข้าแถวเมื่อตอน: {}\nได้นัดมา: {}\nสถานะ: {}".format(QueueNumber["Queue ID"], QueueNumber["Username"], QueueNumber["Doctor Name"], QueueNumber["Time"], QueueNumber["Appointed"], QueueNumber["Status"]))

if CallPatient:
    updateData(patientList, "Pending1")
    st.success("กำลังเรียก ขอให้รอเป็นเวลา 10 นาที")
            
if UncallPatient:
    updateData(patientList, "Waiting")
    st.success("กำลังหยุดเรียก")

if Complete:
    updateData(patientList, "Complete")
    st.success("เสร็จสิ้นคิว")


if "Approved" not in st.session_state:
    st.session_state.Approved = False

st.title("เจ้าหน้าที่จัดคิวผู้ป่วย")

adminForm = st.form("adminInitialForm", clear_on_submit=True)
username = adminForm.text_input("ชื่อบัญชีเจ้าหน้าที่จัดคิว")
password = adminForm.text_input("รหัสผ่าน")
loginButton = adminForm.form_submit_button("เข้าระบบ")

if loginButton:
    if username == "Admin" and password == "adminpass":
        st.session_state.Approved = True
        st.success("เข้าระบบเสร็จสมบูรณ์")
    else:
        st.error("ไม่มีบัญชีชื่อนี้หร์อรหัสผ่านผิด")

clientForm = st.form("clientDeleteForm", clear_on_submit=True)
clientName = clientForm.selectbox("ชื่อบัญชีผู้ป่วยที่จะลบ", retriveClient())
clientSubmit = clientForm.form_submit_button("ลบบัญชีผู้ป่วย")

if clientSubmit:
    if st.session_state.Approved:
        deleteClient(clientName)
        st.success("เสร็จสมบูรณ์")
    else:
        st.error("คุณไม่มีสิทธิแก้ข้อมูล")

if st.button("ลบบัญชีผู้ป่วยทุกคน"):
    if st.session_state.Approved:
        deleteClient("All")
        st.success("เสร็จสมบูรณ์")
    else:
        st.error("คุณไม่มีสิทธิแก้ข้อมูล")

queueForm = st.form("queueDeleteForm", clear_on_submit=True)
queueName = queueForm.selectbox("คิวที่ต้องการจะลบ", retriveData("ID"))
queueSubmit = queueForm.form_submit_button("ลบคิว")

if queueSubmit:
    if st.session_state.Approved:
        deleteData(queueName)
        st.success("เสร็จสมบูรณ์")
    else:
        st.error("คุณไม่มีสิทธิแก้ข้อมูล")

if st.button("ลบทุกคิว"):
    if st.session_state.Approved:
        deleteData("All")
        st.success("เสร็จสมบูรณ์")
    else:
        st.error("คุณไม่มีสิทธิแก้ข้อมูล")


doctorInsertForm = st.empty()
doctorForm = doctorInsertForm.form(key="DoctorOnly", clear_on_submit=False)

Docusername = doctorForm.text_input("ชื่อบัญชีแพทย์")

registerButton = doctorForm.form_submit_button("สร้างบัญชี")

if registerButton:
    output = register(Docusername)
    if output:
        st.success("สร้างบัญชีเสร็จสมบูรณ์")
    else:
        st.error("มีแพทย์ชื่อนี้แล้ว")

doctorForm = st.form("doctorDeleteForm", clear_on_submit=True)
doctorName = doctorForm.selectbox("ชื่อบัญชีแพทย์ที่จะลบ", retriveDoctor("client"))
doctorSubmit = doctorForm.form_submit_button("ลบบัญชีแพทย์")

if doctorSubmit:
    if st.session_state.Approved:
        deleteDoctor(doctorName)
        st.success("เสร็จสมบูรณ์")
    else:
        st.error("คุณไม่มีสิทธิแก้ข้อมูล")

if st.button("ลบบัญชีแพทย์ทุกคน"):
    if st.session_state.Approved:
        deleteDoctor("All")
        st.success("เสร็จสมบูรณ์")
    else:
        st.error("คุณไม่มีสิทธิแก้ข้อมูล")

settingForm = st.form("SettingsForm", clear_on_submit=False)
dailyLimit = settingForm.text_input("จำนวนผู้ป่วยสูงสุดที่รับตรวจ")
walkInLimit = settingForm.text_input("จำนวนผู้ป่วยที่ไม่ได้นัดสูงสุดที่รับตรวจ")
settingSubmit = settingForm.form_submit_button("เปลี่ยนค่าระบบ")

if settingSubmit:
    if st.session_state.Approved:
        settingChanges(dailyLimit, walkInLimit)
        st.success("เสร็จสมบูรณ์")
    else:
        st.error("คุณไม่มีสิทธิแก้ข้อมูล")