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

patientList = patientForm.selectbox("????????????????????????", retrivePatients(st.session_state.DoctorName))


CheckPatient = patientForm.form_submit_button("???????????????????????????????????????")

CallPatient = patientForm.form_submit_button("????????????????????????")

UncallPatient = patientForm.form_submit_button("????????????????????????????????????")

Complete = patientForm.form_submit_button("????????????????????????????????????")

if CheckPatient:
    QueueNumber = callQueue(patientList)
    st.text("???????????????????????????????????????\nQueue ID: {}\n????????????: {}\n??????????????????????????????: {}\n?????????????????????????????????????????????: {}\n????????????????????????: {}\n???????????????: {}".format(QueueNumber["Queue ID"], QueueNumber["Username"], QueueNumber["Doctor Name"], QueueNumber["Time"], QueueNumber["Appointed"], QueueNumber["Status"]))

if CallPatient:
    updateData(patientList, "Pending1")
    st.success("?????????????????????????????? ????????????????????????????????????????????? 10 ????????????")
            
if UncallPatient:
    updateData(patientList, "Waiting")
    st.success("??????????????????????????????????????????")

if Complete:
    updateData(patientList, "Complete")
    st.success("????????????????????????????????????")


if "Approved" not in st.session_state:
    st.session_state.Approved = False

st.title("????????????????????????????????????????????????????????????????????????")

adminForm = st.form("adminInitialForm", clear_on_submit=True)
username = adminForm.text_input("??????????????????????????????????????????????????????????????????????????????")
password = adminForm.text_input("????????????????????????")
loginButton = adminForm.form_submit_button("????????????????????????")

if loginButton:
    if username == "Admin" and password == "adminpass":
        st.session_state.Approved = True
        st.success("????????????????????????????????????????????????????????????")
    else:
        st.error("????????????????????????????????????????????????????????????????????????????????????????????????")

clientForm = st.form("clientDeleteForm", clear_on_submit=True)
clientName = clientForm.selectbox("?????????????????????????????????????????????????????????????????????", retriveClient())
clientSubmit = clientForm.form_submit_button("??????????????????????????????????????????")

if clientSubmit:
    if st.session_state.Approved:
        deleteClient(clientName)
        st.success("????????????????????????????????????")
    else:
        st.error("??????????????????????????????????????????????????????????????????")

if st.button("?????????????????????????????????????????????????????????"):
    if st.session_state.Approved:
        deleteClient("All")
        st.success("????????????????????????????????????")
    else:
        st.error("??????????????????????????????????????????????????????????????????")

queueForm = st.form("queueDeleteForm", clear_on_submit=True)
queueName = queueForm.selectbox("???????????????????????????????????????????????????", retriveData("ID"))
queueSubmit = queueForm.form_submit_button("???????????????")

if queueSubmit:
    if st.session_state.Approved:
        deleteData(queueName)
        st.success("????????????????????????????????????")
    else:
        st.error("??????????????????????????????????????????????????????????????????")

if st.button("????????????????????????"):
    if st.session_state.Approved:
        deleteData("All")
        st.success("????????????????????????????????????")
    else:
        st.error("??????????????????????????????????????????????????????????????????")


doctorInsertForm = st.empty()
doctorForm = doctorInsertForm.form(key="DoctorOnly", clear_on_submit=False)

Docusername = doctorForm.text_input("??????????????????????????????????????????")

registerButton = doctorForm.form_submit_button("??????????????????????????????")

if registerButton:
    output = register(Docusername)
    if output:
        st.success("??????????????????????????????????????????????????????????????????")
    else:
        st.error("??????????????????????????????????????????????????????")

doctorForm = st.form("doctorDeleteForm", clear_on_submit=True)
doctorName = doctorForm.selectbox("???????????????????????????????????????????????????????????????", retriveDoctor("client"))
doctorSubmit = doctorForm.form_submit_button("????????????????????????????????????")

if doctorSubmit:
    if st.session_state.Approved:
        deleteDoctor(doctorName)
        st.success("????????????????????????????????????")
    else:
        st.error("??????????????????????????????????????????????????????????????????")

if st.button("???????????????????????????????????????????????????"):
    if st.session_state.Approved:
        deleteDoctor("All")
        st.success("????????????????????????????????????")
    else:
        st.error("??????????????????????????????????????????????????????????????????")

settingForm = st.form("SettingsForm", clear_on_submit=False)
dailyLimit = settingForm.text_input("????????????????????????????????????????????????????????????????????????????????????")
walkInLimit = settingForm.text_input("????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????")
settingSubmit = settingForm.form_submit_button("??????????????????????????????????????????")

if settingSubmit:
    if st.session_state.Approved:
        settingChanges(dailyLimit, walkInLimit)
        st.success("????????????????????????????????????")
    else:
        st.error("??????????????????????????????????????????????????????????????????")