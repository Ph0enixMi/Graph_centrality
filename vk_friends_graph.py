import requests, json


class VkGraph:
    def __init__(
            self,
            api_key,
            profiles_id=[182826238, 170609622, 273594586, 332501512, 197466399, 351652267],
            api_version=5.199,
            write_json=True,
            limit=1000
    ):
        self.api_key = api_key
        self.profiles_id = profiles_id
        self.api_version = api_version
        self.write_json = write_json
        self.limit = limit
        self._friends_data = {}

        self._get_data()
        self._clean_nodes()
        if self.write_json:
            self._write_json(self._friends_data)


    def _get_data(self):
        for profile_id in self.profiles_id:
            friends = self._fetch_friends(profile_id)
            if friends is not None:
                self._friends_data[profile_id] = friends
                for friend_id in friends:
                    if friend_id not in self._friends_data:
                        self._friends_data[friend_id] = self._fetch_friends(friend_id)


    def _fetch_friends(self, user_id):
        url = f"https://api.vk.com/method/friends.get?access_token={self.api_key}&user_id={user_id}&v={self.api_version}&count={self.limit}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json().get('response', {}).get('items', [])
        except requests.RequestException:
            return []


    def _clean_nodes(self):
        values = list(self._friends_data.values())
        flat_values = [item for sublist in values for item in sublist]

        elements_to_keep = {element for element in flat_values if flat_values.count(element) > 1}

        cleaned_data = {}
        for key, value in self._friends_data.items():
            cleaned_value = [element for element in value if element in elements_to_keep or element in self.profiles_id]
            if len(cleaned_value) > 1:
                cleaned_data[key] = cleaned_value

        self._friends_data = cleaned_data


    @staticmethod
    def _write_json(data):
        with open("friends.json", "w", encoding="UTF-8") as file_out:
            json.dump(data, file_out, ensure_ascii=False, indent=2)
