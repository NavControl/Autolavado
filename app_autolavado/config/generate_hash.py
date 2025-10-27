import bcrypt

# Contraseña que deseas hashear
password = "12345678".encode('utf-8')  # Convertir a bytes

# Generar hash
hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
print(hashed_password.decode('utf-8'))  # Imprimir como string para guardar
