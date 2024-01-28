import json
import csv
import subprocess
import yaml
import datetime
import os


def main():
    secrets = read_config_file()
    refresh_token = get_access_token(
        secrets["client_id"],
        secrets["client_secret"],
        secrets["code"],
    )
    activities_json = all_strava_activities(
        refresh_token,
        after=date_to_timestamp("2024/01/01"),
    )
    parsed = parse_json_to_dict(activities_json, lambda obj: obj["type"] == "Run")
    write_runs_to_csv(parsed)


def read_json_file(file_path):
    with open(file_path, "r") as file:
        data = json.load(file)
    return data


def parse_json_to_dict(json_data, filter_func):
    dict = []
    for obj in json_data:
        if filter_func(obj):
            dict.append(
                {
                    "name": obj.get("name", None),
                    "distance": obj.get("distance", None) / 1000,  # km
                    "moving_time": obj.get("moving_time", None) / 60,  # min
                    "elapsed_time": obj.get("elapsed_time", None) / 60,  # min
                    "start_date": obj.get("start_date_local", None)[:10],  # Y-m-d
                    "average_heartrate": obj.get("average_heartrate", None),
                    "max_heartrate": obj.get("max_heartrate", None),
                    "elevation": obj.get("total_elevation_gain", None),  # m
                }
            )
    return dict


def write_runs_to_csv(json_data, output="strava.csv"):
    with open(output, "w", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "start_date",
                "distance",
                "moving_time",
                "elapsed_time",
                "pace",
                "elevation",
                "average_heartrate",
                "max_heartrate",
                "name",
            ],
            delimiter=";",
        )
        writer.writeheader()
        writer.writerows(json_data)


def strava_activities_page(access_token, after=0, page=1, per_page=200):
    curl_command = f'curl -X GET "https://www.strava.com/api/v3/athlete/activities?per_page={per_page}&page={page}&after={after}" -H "Authorization: Bearer {access_token}"'
    print(curl_command)
    result = subprocess.run(curl_command, shell=True, capture_output=True, text=True)
    return json.loads(result.stdout)


def all_strava_activities(access_token, after=0):
    json_data = []
    page = 1
    while True:
        new_json_data = strava_activities_page(access_token, page=page, after=after)
        print(new_json_data, len(new_json_data), not new_json_data)
        if not new_json_data:
            break
        json_data += new_json_data
        page = page + 1
    return json_data


def date_to_timestamp(date):
    return datetime.datetime.strptime(date, "%Y/%m/%d").timestamp()


def get_access_token(client_id, client_secret, code, output="access_token.yaml"):
    data = read_yaml_file(output)
    if data and "access_token" in data:
        return data["access_token"]

    curl_command = f'curl -X POST "https://www.strava.com/oauth/token" -F client_id={client_id} -F client_secret={client_secret} -F code={code} -F grant_type=authorization_code'
    print(curl_command)
    result = subprocess.run(curl_command, shell=True, capture_output=True, text=True)
    data = json.loads(result.stdout)

    if "errors" in data:
        raise Exception("Error while getting access token", data)

    with open(output, "w") as file:
        yaml.dump(data, file)

    return data["access_token"]


def read_yaml_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            data = yaml.safe_load(file)
        return data
    else:
        return None


def read_config_file(file_path="secrets.yaml"):
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            data = yaml.safe_load(file)

            if "code" not in data or not data["code"] or data["code"] == "TODO":
                raise Exception(
                    "client_id not found in config file",
                    f"http://www.strava.com/oauth/authorize?client_id={data['client_id']}&response_type=code&redirect_uri=http://localhost/exchange_token&approval_prompt=force&scope=activity:read_all",
                )

        return data
    else:
        raise Exception("Config file not found")


if __name__ == "__main__":
    main()
