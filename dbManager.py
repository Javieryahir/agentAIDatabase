import psycopg2


DB_HOST = "INSERT YOUR CREDENTIALS"  
DB_PORT = "INSERT YOUR CREDENTIALS"  
DB_USER = "INSERT YOOUR CREDNTIALS" 
DB_PASSWORD = "INSERT YOUR CREDENTIALS" 
DB_NAME = "INSERT YOUR CREDENDTIALS" 


def connect_to_db():
    try:
        connection = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            dbname=DB_NAME
        )
        return connection
    except Exception as e:
        return {
            "status" : "error",
            "details" : "Error al conectarse a la base de datos"
        }  

'''
def create_table():
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        
        create_table_query =
        CREATE TABLE IF NOT EXISTS cases (
            id SERIAL PRIMARY KEY,         -- Identificador Unico
            title VARCHAR(255) NOT NULL,   -- TItulo del caso
            status VARCHAR(50) NOT NULL,   -- Estado del caso (ej., "Abierto", "Cerrado")
            description TEXT,              -- DescripciOn del caso
            attorney VARCHAR(100),         -- Nombre del abogado asignado
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Fecha de creación
        );
      
        try:
            cursor.execute(create_table_query) 
            conn.commit()  
            
        except Exception as e:
       
        finally:
            cursor.close()  
            conn.close()    
'''

def create_case(title, status, description, attorney):
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        create_case_query = '''
        INSERT INTO cases (title, status, description, attorney)
        VALUES (%s, %s, %s, %s);
        '''
        try:
            cursor.execute(create_case_query, (title, status, description, attorney))
            conn.commit()  
        except Exception as e:
            return {
                "status" : "error",
                "details" : "Error al crear un registro"
            } 
        finally:
            cursor.close()
            conn.close()
            return {
                "status" : "success",
                "details" : "Registro Creado Exitosamente"
            } 
    else:
        return conn  



def read_all_cases():
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        read_all_query = 'SELECT * FROM cases;'
        try:
            cursor.execute(read_all_query)
            rows = cursor.fetchall()
        except Exception as e:
            return {
                "status" : "error",
                "details" : "Error al Leer todos los registros"
            } 
        finally:
            cursor.close()
            conn.close()
            
            return {
                "status" : "success",
                "details" : f"{rows}"
            } 
    else:
        return conn


def update_case(case_id, title=None, status=None, description=None, attorney=None):
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()

        
        update_query = 'UPDATE cases SET '
        params = []

        if title:
            update_query += 'title = %s, '
            params.append(title)
        if status:
            update_query += 'status = %s, '
            params.append(status)
        if description:
            update_query += 'description = %s, '
            params.append(description)
        if attorney:
            update_query += 'attorney = %s, '
            params.append(attorney)

        
        update_query = update_query.rstrip(', ') 
        update_query += ' WHERE id = %s;'
        params.append(case_id)

        try:
            cursor.execute(update_query, tuple(params))
            conn.commit()  # Confirmar los cambios
        except Exception as e:
            return {
                "status" : "error",
                "description": f"Error al querer actualizar registro con id {case_id}"
            }
        finally:
            cursor.close()
            conn.close()
            return {
                "status" : "success",
                "description": f"Registro actualizado exitosamente con id {case_id}"
            }
    else:
        return conn


def delete_case(case_id):
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        delete_case_query = 'DELETE FROM cases WHERE id = %s;'
        try:
            cursor.execute(delete_case_query, (case_id,))
            conn.commit()  
            
        except Exception as e:
            return {
                "status" : "error",
                "description": f"Error al querer Borrar registro con id {case_id}"
            }
        finally:
            cursor.close()
            conn.close()
            return {
                "status" : "success",
                "description": f"Registro borrado exitosamente con id {case_id}"
            }
    else:
        return conn







