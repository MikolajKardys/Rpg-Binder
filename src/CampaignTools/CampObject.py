import csv


class CampObject:
    OBJ_PATH = None

    def __init__(self, campaign):
        self.campaign = campaign
        self.id = None

    def __eq__(self, other):
        return self.id == other.id

    def __repr__(self):
        return str(self.id)

    def save_obj(self):
        campaign = self.campaign

        all_obj = self.load_obj(campaign)
        if all_obj:
            self.id = [int(obj.id) for obj in all_obj].pop() + 1
        else:
            self.id = 1

        file_path = campaign.campaign_dir_path + self.OBJ_PATH

        obj_dict = self.__dict__.copy()
        obj_dict.pop('campaign')

        writer = csv.DictWriter(open(file_path, "a", newline=''), obj_dict.keys())

        writer.writerow(obj_dict)
        return True

    def remove_obj(self):
        campaign = self.campaign

        rest = self.check_obj(self.load_obj(campaign), f"id!={self.id}")

        file_path = campaign.campaign_dir_path + self.OBJ_PATH

        curr_dict = self.__dict__.copy()
        curr_dict.pop('campaign')

        writer = csv.DictWriter(open(file_path, "w", newline=''), curr_dict.keys())
        writer.writeheader()
        for obj in rest:
            obj_dict = obj.__dict__.copy()
            obj_dict.pop('campaign')
            writer.writerow(obj_dict)

    def save_state(self):
        if self.id is None:
            self.save_obj()
        else:
            campaign = self.campaign

            all_obj = self.check_obj(self.load_obj(campaign))

            file_path = campaign.campaign_dir_path + self.OBJ_PATH

            curr_dict = self.__dict__.copy()
            curr_dict.pop('campaign')

            writer = csv.DictWriter(open(file_path, "w", newline=''), curr_dict.keys())
            writer.writeheader()
            for obj in all_obj:
                if obj.id != self.id:
                    obj_dict = obj.__dict__.copy()
                    obj_dict.pop('campaign')
                    writer.writerow(obj_dict)
                else:
                    writer.writerow(curr_dict)

    def obj_from_dict(self, row):
        self.__dict__.update(row)

    @classmethod
    def get_matching(cls, obj_tab, str_criteria):
        obj_tab = cls.check_obj(obj_tab, f"name~{str_criteria}")
        return obj_tab

    @classmethod
    def get(cls, campaign, *criteria):  # returns 1 object with given parameters
        obj_tab = cls.check_obj(cls.load_obj(campaign), *criteria)
        if len(obj_tab) == 0:
            return None
        return obj_tab[0]

    @classmethod
    def load_obj(cls, campaign):  # loads all items saved in campaign
        file_path = campaign.campaign_dir_path + cls.OBJ_PATH
        reader = csv.DictReader(open(file_path))
        obj_tab = []
        for row in reader:
            obj = cls(campaign)
            obj.obj_from_dict(row)
            obj_tab.append(obj)
        return obj_tab

    @staticmethod
    def check_obj(check_tab, *criteria):  # checks table with given criteria; "{field}={value}"; AND, not OR
        result_tab = []
        for obj in check_tab:
            meets_cr = True
            for cr in criteria:
                if cr.__contains__("!="):
                    field, value = cr.split("!=")
                    test = not str(obj.__dict__.get(field)).lower().__eq__(str(value.lower()))
                elif cr.__contains__("="):
                    field, value = cr.split("=")
                    test = str(obj.__dict__.get(field)).lower().__eq__(str(value.lower()))
                else:
                    field, value = cr.split("~")
                    test = str(obj.__dict__.get(field)).lower().__contains__(str(value.lower()))
                meets_cr = meets_cr and test
            if meets_cr:
                result_tab.append(obj)

        return result_tab
