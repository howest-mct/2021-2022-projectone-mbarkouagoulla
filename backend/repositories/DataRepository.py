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
        sql = "SELECT Naam,Voornaam,`RFID-code` from Gebruikers"
        return Database.get_rows(sql)

    @staticmethod
    def read_gebruikers_by_id(id):
        sql = "SELECT Voornaam from Gebruikers WHERE gebruikerID = %s"
        params = [id]
        return Database.get_one_row(sql, params)

    @staticmethod
    def read_rfid_alle_gebruikers():
        sql = "SELECT `RFID-code` from Gebruikers"
        return Database.get_rows(sql)

    @staticmethod
    def read_gebruikers_by_rfid(rfid):
        sql = "SELECT Voornaam from Gebruikers WHERE `RFID-code` = %s"
        params = [rfid]
        return Database.get_one_row(sql, params)
    
    @staticmethod
    def read_gebruikerID_by_rfid(rfid):
        sql = "SELECT GebruikerID from Gebruikers WHERE `RFID-code` = %s"
        params = [rfid]
        return Database.get_one_row(sql, params)


    @staticmethod
    def read_rfid_gebruiker(gebruikersnaam):
        sql = "SELECT `RFID-code` from Gebruikers Where Naam = %s"
        params = [gebruikersnaam]
        return Database.get_one_row(sql, params)

    @staticmethod
    def update_rfid_gebruiker(naam, code):
        sql = "UPDATE Gebruikers SET `RFID-code` = %s WHERE Naam = %s"
        params = [code, naam]
        return Database.execute_sql(sql, params)

    @staticmethod
    def read_history_action():
        sql = "SELECT h.datum , g.voornaam , a.ActieBeschrijving from HistoriekActies h join Gebruikers g on h.FK_GebruikerID = g.GebruikerID join Acties a on a.ActieID = h.FK_ActieID"
        return Database.get_rows(sql)

    @staticmethod
    def add_history_action(actie,datum,gebruiker):
        sql = "INSERT into HistoriekActies (FK_ActieID,Datum,FK_GebruikerID) VALUES (%s,%s,%s)"
        params = [actie,datum,gebruiker]
        return Database.execute_sql(sql,params)

    @staticmethod
    def add_history_sensors(sensor,datum,waarde):
        sql = "INSERT into HistoriekSensors (FK_SensorID, Datum, Waarde) VALUES (%s, %s, %s)"
        params= [sensor,datum,waarde]
        return Database.execute_sql(sql,params)
