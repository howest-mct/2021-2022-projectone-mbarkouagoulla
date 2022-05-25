from .Database import Database


class DataRepository:
    @staticmethod
    def json_or_formdata(request):
        if request.content_type == 'application/json':
            gegevens = request.get_json()
        else:
            gegevens = request.form.to_dict()
        return gegevens

    @staticmethod
    def read_status_lampen():
        sql = "SELECT * from lampen"
        return Database.get_rows(sql)

    @staticmethod
    def read_status_lamp_by_id(id):
        sql = "SELECT * from lampen WHERE id = %s"
        params = [id]
        return Database.get_one_row(sql, params)

    @staticmethod
    def update_status_lamp(id, status):
        sql = "UPDATE lampen SET status = %s WHERE id = %s"
        params = [status, id]
        return Database.execute_sql(sql, params)

    @staticmethod
    def update_status_alle_lampen(status):
        sql = "UPDATE lampen SET status = %s"
        params = [status]
        return Database.execute_sql(sql, params)
    
    #####################
    @staticmethod
    def read_gebruikers():
        sql = "SELECT * from gebruikers"
        return Database.get_rows(sql)
    
    @staticmethod
    def read_gebruikers_by_id(id):
        sql = "SELECT Voornaam from gebruikers WHERE gebruikerID = %s"
        params = [id]
        return Database.get_one_row(sql, params)
    
    @staticmethod
    def read_rfid_alle_gebruikers():
        sql = "SELECT `RFID-code` from gebruikers"
        return Database.get_rows(sql)

    @staticmethod
    def read_gebruikers_by_rfid(rfid):
        sql = "SELECT Voornaam from gebruikers WHERE `RFID-code` = %s"
        params = [rfid]
        return Database.get_one_row(sql, params)

    @staticmethod
    def read_rfid_gebruiker(gebruikersnaam):
        sql = "SELECT `RFID-code` from gebruikers Where Naam = %s"
        params = [gebruikersnaam]
        return Database.get_one_row(sql,params)
        
    @staticmethod
    def update_rfid_gebruiker(naam, code):
        sql = "UPDATE gebruikers SET `RFID-code` = %s WHERE Naam = %s"
        params = [code, naam]
        return Database.execute_sql(sql, params)
    

    
