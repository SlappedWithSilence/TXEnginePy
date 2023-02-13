import requests


class Viewer:
    """
    A basic class that visualizes the TXEngine API
    """

    def __init__(self):
        self.ip = 'http://' + input("Enter the IP for the TXEngine server: ")

    def display(self, value: dict):
        """
        Primitively print GET results
        """

        if value["frame_type"] == "Room":
            print(value["components"]["content"])

            for idx, opt in enumerate(value["components"]["options"]):
                print(f"[{idx}] {opt}")

        else:
            print(value["components"]["content"])

        input_type = value["input_type"][0]
        input_range = value["input_range"]

        if input_type == "int":
            print(f"Enter a number between ({input_range['min']} and {input_range['max']}):")

        elif input_type == "none":
            print(f"Press any key:")

        elif input_type == "str":
            print("Enter a string: ")

        elif input_type == "affirmative":
            print("Enter y, n, yes, or no:")


if __name__ == "__main__":

    viewer = Viewer()

    while True:
        results = requests.get(viewer.ip, verify=False)
        viewer.display(results.json())
        user_input = input()

        r = requests.put(viewer.ip, params={"user_input": user_input}, verify=False)
