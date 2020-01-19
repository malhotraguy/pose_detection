import json
import math
import os
import pprint
from time import sleep

import matplotlib.pyplot as plt
import requests
from dotenv import load_dotenv

from constants import INPUT_IMAGE_FOLDER

load_dotenv(verbose=True)
API_KEY = os.environ.get("API_KEY")
LOGIN_URL = "https://api.wrnch.ai/v1/login"
JOBS_URL = "https://api.wrnch.ai/v1/jobs"


def get_job_response(get_job_url, fetch_try=1, wait_for=0.50):
    sleep(wait_for)
    resp_get_job = requests.get(
        get_job_url, headers={"Authorization": f"Bearer {JWT_TOKEN}"}
    )
    # print('Status code:', resp_get_job.status_code)
    # print('\nResponse:')
    pprint.pprint(resp_get_job.text)
    fetch_try = fetch_try + 1
    if resp_get_job.status_code != 200:
        print(f"{fetch_try} wait for fetching the result")
        return get_job_response(get_job_url, fetch_try=fetch_try, wait_for=0.10)
    cloud_pose_estimation = json.loads(resp_get_job.text)
    return cloud_pose_estimation


def get_joint_coordinates(body_joints_coordinates, body_joint_position):
    coordinates = [
        body_joints_coordinates[2 * body_joint_position],
        body_joints_coordinates[2 * body_joint_position + 1],
    ]
    # Converting the sign of y coordinate as positive y coordinate from wrnch means y coordinate going down
    return coordinates


def get_distance(coordinates_1, coordinates_2):
    distance = math.sqrt(
        (coordinates_2[0] - coordinates_1[0]) ** 2
        + (coordinates_2[1] - coordinates_1[1]) ** 2
    )
    return distance


def plot_lines(right_wrist_co, left_wrist_co, right_shoulder_co, left_shoulder_co):
    plt.plot(
        [right_wrist_co[0], left_wrist_co[0]],
        [right_wrist_co[1], left_wrist_co[1]],
        "r-",
    )
    # plt.annotate('local max', xy=(1, 0), xytext=(1, 0.5),
    #              arrowprops=dict(facecolor='black', shrink=0.05),
    #              )
    plt.plot(
        [right_shoulder_co[0], left_shoulder_co[0]],
        [right_shoulder_co[1], left_shoulder_co[1]],
        "b-",
    )
    plt.axis([-1, 1, -1, 1])

    plt.show()


resp_auth = requests.post(LOGIN_URL, data={"api_key": API_KEY})
# # print(resp_auth.text)
# the jwt token is valid for an hour
JWT_TOKEN = json.loads(resp_auth.text)["access_token"]


def get_wrnch_data(local_image_path=None, image_byte_stream=None):
    # Open the file as a byte stream
    # Send a post request with authentification and the file
    if local_image_path:
        if os.path.isfile(local_image_path):
            with open(local_image_path, "rb") as f:
                resp_sub_job = requests.post(
                    JOBS_URL,
                    headers={"Authorization": f"Bearer {JWT_TOKEN}"},
                    files={"media": f},
                    data={"work_type": "json"},
                )
        else:
            raise Exception(f"Path={local_image_path} doesnot exist")
    elif image_byte_stream:
        resp_sub_job = requests.post(
            JOBS_URL,
            headers={"Authorization": f"Bearer {JWT_TOKEN}"},
            files={"media": image_byte_stream},
            data={"work_type": "json"},
        )
    else:
        raise Exception("No Input Image Data!!")

    job_id = json.loads(resp_sub_job.text)["job_id"]
    # print('Status code:', resp_sub_job.status_code)
    # print('Response:', resp_sub_job.text)
    # The status code should be 202 and return a job_id.

    job_fetcher_url = JOBS_URL + "/" + job_id
    # print(job_fetcher_url)
    pose_estimation = get_job_response(get_job_url=job_fetcher_url)
    # print(f"pose_estimation Keys={pose_estimation.keys()}")
    man_pose = pose_estimation["frames"][0]["persons"][0]

    # There are 25 joints and the joints json hold 50 values (25 pairs of coordinates).
    # Joint 0 coordinates, (x,y) = (man_pose['pose2d']['joints'][0],man_pose['pose2d']['joints'][1])
    # Joint n coordinates, (x,y) = (man_pose['pose2d']['joints'][2n],man_pose['pose2d']['joints'][2n+1])
    man_pose_joints = man_pose["pose2d"]["joints"]
    # print(len(man_pose_joints))

    left_wrist = get_joint_coordinates(man_pose_joints, 15)
    # print(f"left_wrist={left_wrist}")

    right_wrist = get_joint_coordinates(man_pose_joints, 10)
    # print(f"right_wrist={right_wrist}")

    left_shoulder = get_joint_coordinates(man_pose_joints, 13)
    # print(f"left_shoulder={left_shoulder}")

    right_shoulder = get_joint_coordinates(man_pose_joints, 12)
    # print(f"right_shoulder={right_shoulder}")

    wrist_distance = get_distance(right_wrist, left_shoulder)
    # print(f"wrist_distance={wrist_distance}")

    shoulder_distance = get_distance(right_shoulder, left_shoulder)
    # print(f"shoulder_distance={shoulder_distance}")

    length_resize_factor = wrist_distance / shoulder_distance
    # print(f"length_resize_factor={length_resize_factor}")

    left_wrist_increase_factor = (
        (left_wrist[0] - left_shoulder[0]) / (left_shoulder[0] - right_shoulder[0])
    ) + 1
    # print(f"left_wrist_increase_factor={left_wrist_increase_factor}")

    left_wrist_displacement = left_wrist[0] - left_shoulder[0]
    # print(f"left_wrist_displacement={left_wrist_displacement}")

    right_wrist_increase_factor = (
        (right_shoulder[0] - right_wrist[0]) / (left_shoulder[0] - right_shoulder[0])
    ) + 1
    # print(f"right_wrist_increase_factor={right_wrist_increase_factor}")

    right_wrist_displacement = right_shoulder[0] - right_wrist[0]
    # print(f"right_wrist_displacement={right_wrist_displacement}")

    rotation_angle_radians = math.atan2(
        (left_wrist[1] - right_wrist[1]), (left_wrist[1] - right_wrist[1])
    )
    # print(f"rotation_angle_radians={rotation_angle_radians}")

    rotation_angle_degrees = math.degrees(rotation_angle_radians)
    # print(f"rotation_angle_degrees={rotation_angle_degrees}")

    # plot_lines(right_wrist_co=right_wrist, left_wrist_co=left_wrist, right_shoulder_co=right_shoulder,
    #            left_shoulder_co=left_shoulder)

    return (
        wrist_distance,
        shoulder_distance,
        left_wrist_displacement,
        right_wrist_displacement,
        rotation_angle_degrees,
    )


if __name__ == "__main__":
    IMAGE_NAME = "WhatsApp Image 2020-01-19 at 1.56.26 AM (4).jpeg"
    IMAGE_FILE_PATH = f"{INPUT_IMAGE_FOLDER}/{IMAGE_NAME}"
    (
        wrist_dist,
        shoulder_dist,
        left_wrist_displ,
        right_wrist_displ,
        rotation_degrees,
    ) = get_wrnch_data(local_image_path=IMAGE_FILE_PATH)
    print(right_wrist_displ)
    print(left_wrist_displ)
