from models import db, User, Feedback
from app import app

db.drop_all()
db.create_all()

u1 = User(first_name = "Harrison", last_name = "Ndubuisi", email = "example@gmail.com", username = "harri1", password = User.register("harrison1"))
u2 = User(first_name = "Chinonso", last_name = "Biglegend", email = "example@yahoo.com", username = "harri2", password = User.register("harrison2"))
u3 = User(first_name = "Valentine", last_name = "Ezigbo", email = "example@hotmail.com", username = "harri3", password = User.register("harrison3"))

db.session.add_all([u1, u2, u3])
db.session.commit()

f1 = Feedback(title = "Good job", content = "It has been an amezing struggle", username = "harri1")
f2 = Feedback(title = "Joy", content = "Hopefully, we will get there with joy", username = "harri2")
f3 = Feedback(title = "Happy", content = "It feels good to see your progress", username = "harri3")
f4 = Feedback(title = "Strong", content = "We are all alone in this together", username = "harri1")

db.session.add_all([f1, f2, f3, f4])
db.session.commit()