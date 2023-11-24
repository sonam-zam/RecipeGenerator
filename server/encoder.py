import json
import six

from server.data.models.recipe import Recipe


class JSONEncoder(json.JSONEncoder):
    include_nulls = False

    def default(self, o):
        if isinstance(o, Recipe):
            dikt = {}
            for attr, _ in six.iteritems(o.swagger_types):
                value = getattr(o, attr)
                if value is None and not self.include_nulls:
                    continue
                attr = o.attribute_map[attr]
                dikt[attr] = value
            return dikt
        return json.JSONEncoder.default(self, o)
