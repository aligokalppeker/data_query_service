from datetime import datetime
import requests

# Data has too many rows, so we may limit the rows to limit for migration
# Give import limit as -1, not to limit the rows to be imported
import_limit: int = 50000


def import_houses(apps, schema_editor):
    HouseItem = apps.get_model("server_app_api", "HouseItem")
    file_url = "http://prod.publicdata.landregistry.gov.uk.s3-website-eu-west-1.amazonaws.com/pp-complete.csv"
    req = requests.get(file_url, stream=True)
    record_count = 0
    print("Importing at most count:", import_limit)
    for chunk in req.iter_lines():
        # writing one chunk at a time to test_txt_f file
        if chunk:
            data: str = chunk.decode("utf-8")
            fields: [str] = data.replace("\"", "").split(",")
            print("Importing row", record_count)
            HouseItem(house_uuid=fields[0].replace("{", "").replace("}", ""),
                      primary_addressable_object_name=fields[3],
                      secondary_addressable_object_name=fields[3],
                      sell_price=int(fields[1]),
                      sell_date=datetime.strptime(fields[2], "%Y-%m-%d %H:%M"),
                      address_street=fields[9],
                      address_locality=fields[10],
                      address_town=fields[11],
                      address_county=fields[12],
                      address_city=fields[13],
                      house_type=fields[4],
                      ).save()

            record_count = record_count + 1
            if import_limit != -1 and record_count > import_limit:
                break
