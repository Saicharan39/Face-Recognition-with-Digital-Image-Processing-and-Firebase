import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{'databaseURL':"https://face-detection-for-attendance-default-rtdb.firebaseio.com/"})


ref=db.reference("students")


data={
    
    "12345":
        {
            "name" :"Rajnikanth",
            "major": "cinema",
            "starting year": 2003,
            "total attendance":10,
            "standing":"Good",
            "year":4,
            "last attendance time":" 2022-12-11 00:54:34"
            
                },
        
        
        "23456":
        {
            "name" :"kcr",
            "major": "politics",
            "starting year": 2000,
            "total attendance":10,
            "standing":"Excellent",
            "year":3,
            "last attendance time":" 2020-12-11 10:54:34"
            
                },
        "34567":
        {
            "name" :"Elon Musk",
            "major": "Engineer",
            "starting year": 1996,
            "total attendance":6,
            "standing":"Satisfactory",
            "year":2,
            "last attendance time":" 2013-12-11 00:14:34"
            
                }
}


for key,value in data.items():
    ref.child(key).set(value)