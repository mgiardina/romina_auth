from utilities.config import engine
from utilities.auth import (
    User,
    PasswordChange,
    add_user,
    change_user,
    del_user,
    show_users,
    user_exists
)

# este script corre la configuracion inicial de las tablas de la base de datos

def create_user_table(model,engine):
    model.metadata.create_all(engine)

def create_password_change_table(model,engine):
    model.metadata.create_all(engine)


create_user_table(User,engine)
create_password_change_table(PasswordChange,engine)


first = 'test'
last = 'test'
email = 'test@test.com'
password = 'test'
add_user(first,last,password,email,engine)


show_users(engine)

print(user_exists(email,engine))


