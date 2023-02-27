import re


TO_SNAKE_CASE = [
    (re.compile('(.)([A-Z][a-z]+)'), r'\1_\2'),
    (re.compile('__([A-Z])'), r'_\1'),
    (re.compile('([a-z0-9])([A-Z])'), r'\1_\2'),
]

UTC_DATETIME_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:.\d{9})?(?:Z|[+-]\d{2}:\d{2})?$")
UTC_DATE_RE = re.compile("^\d{4}-\d{2}-\d{2}$")


def to_snake_case(name):
    for pattern, repl in TO_SNAKE_CASE:
        name = pattern.sub(repl, name)
    return name.lower()


class PydanticField:
    def __init__(self, name, type_name):
        self.name = name
        self.type_name = type_name

    def __str__(self):
        name, alias = self.create_alias(self.name)
        if alias:
            return f'    {name}: {self.type_name} = Field(alias="{alias}")\n'
        return f"    {name}: {self.type_name}\n"

    @staticmethod
    def create_alias(name):
        snake = to_snake_case(name)
        if snake != name:
            return snake, name
        return name, None

    @classmethod
    def parse(cls, name, val):
        if isinstance(val, dict):
            models = PydanticModel.parse(name.capitalize(), val)
            return cls(name, models[0].name), models
        if isinstance(val, list):
            return cls.parse_list_field(name, val)
        if isinstance(val, str):
            if UTC_DATETIME_RE.match(val):
                return cls(name, "datetime"), []
            if UTC_DATE_RE.match(val):
                return cls(name, "date"), []

        return cls(name, type(val).__name__), []

    @classmethod
    def parse_list_field(cls, name, val):
        if val:
            field, nested_models = cls.parse(name, val[0])
            return field.as_list_field(), nested_models
        return cls(name, "List[any]"), []

    def as_list_field(self):
        return self.__class__(self.name, f"List[{self.type_name}]")


class PydanticModel:
    def __init__(self, name, fields):
        self.name = name
        self.fields = fields

    @classmethod
    def parse(cls, name, obj):
        fields = []
        models = []
        for key, val in obj.items():
            field, nested_models = PydanticField.parse(key, val)
            fields.append(field)
            models.extend(nested_models)
        return [cls(name, fields), *models]

    def __str__(self):
        return f"class {self.name}(BaseModel):\n" + "".join(map(str, self.fields))


def generate_model(name, o):
    for model in reversed(PydanticModel.parse(name, o)):
        print(model)
        print()
