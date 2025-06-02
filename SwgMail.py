import re

class SwgMail:
    @staticmethod
    def parse_survey_droid(email_data):
        if isinstance(email_data, str):
            planet = re.findall(r'Planet\:\s+[^\s]+\s([^\n]+)', email_data)[0]
            parts = re.split(r'Resources located\.\.\.[^\n]+[\n]+', email_data)
            data = parts[1].strip()
            lines = re.split(r'[\n]+', data)
            resources, group, resource_type = [[], None, None]
            for line in lines:
                if line.startswith("\t\t\t"):
                    resources, group, resource_type = SwgMail.survey_droid_reduce_set_resource_stats(line, [resources, group, resource_type])
                elif line.startswith("\t\t"):
                    resources, group, resource_type = SwgMail.survey_droid_reduce_init_resource(line, [resources, group, resource_type])
                elif line.startswith("\t"):
                    resources, group, resource_type = SwgMail.survey_droid_reduce_type(line, [resources, group, resource_type])
                else:
                    resources, group, resource_type = SwgMail.survey_droid_reduce_group(line, [resources, group, resource_type])
            resources = list(map(lambda resource: {**resource, 'planet': planet}, resources))
            return resources
        else:
            raise ValueError("email_data must be a string")

    @staticmethod
    def survey_droid_reduce_group(line, acc):
        resources, _, _ = acc
        return resources, line, None

    @staticmethod
    def survey_droid_reduce_type(line, acc):
        resources, group, _ = acc
        return resources, group, SwgMail.remove_tabs(line)

    @staticmethod
    def survey_droid_reduce_init_resource(line, acc):
        resources, group, resource_type = acc
        resource_name = re.sub(r'(.*\s([^\\]+).*)', r'\2', line)
        resource = {'name': resource_name, 'group': group, 'type': resource_type, 'stats': {}}
        return [resource] + resources, group, resource_type

    @staticmethod
    def survey_droid_reduce_set_resource_stats(line, acc):
        resources, group, resource_type = acc
        resource, others = resources[0], resources[1:]
        stat, value = re.split(r':\s*', SwgMail.remove_tabs(line))
        updated_stats = {**resource['stats'], stat: value}
        updated_resource = {**resource, 'stats': updated_stats}
        return [[updated_resource] + others, group, resource_type]

    @staticmethod
    def remove_tabs(str):
        return str.replace("\t", "")
